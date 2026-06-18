import requests
import re
import time
import random
import base64
from faker import Faker
from user_agent import generate_user_agent

x = Faker()
n = x.name()
r = requests.Session()
u = generate_user_agent()

def python():
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
    
e = python()

headers = {
    'authority': 't.cometlytrack.com',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://www.clickfunnels.com',
    'referer': 'https://www.clickfunnels.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
}

params = {
    'space_id': '3377699765000018',
}

json_data = {
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

response = r.post('https://t.cometlytrack.com/e/t', params=params, headers=headers, json=json_data)

headers = {
    'authority': 'api-order.payments.ai',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer pk_live_oSLT21YBfpfTp6TqUF5JCZX4vxMenFyjAAjUiso',
    'content-type': 'application/json',
    'origin': 'https://framepay.payments.ai',
    'reb-api-consumer': 'Rebilly/framepay@framepay.payments.ai_48f95c8',
    'referer': 'https://framepay.payments.ai/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': u,
}

json_data = {
    'method': 'payment-card',
    'billingAddress': {
        'firstName': n,
        'lastName': n,
        'emails': [
            {
                'label': 'Emails',
                'value': e,
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
        'pan': '6011007263391681',
        'cvv': '038',
        'expYear': '2030',
        'expMonth': '10',
    },
}

response = r.post(
    'https://api-order.payments.ai/organizations/79e29172-59dd-4f18-82d6-28758d4a89fa/tokens',
    headers=headers,
    json=json_data,
)

uwu = response.json()['id']

headers = {
    'authority': 'www.clickfunnels.com',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://www.clickfunnels.com',
    'referer': 'https://www.clickfunnels.com/scale-monthly-step-2',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': u,
    'x-cf2-post-type': 'submit',
}

json_data = {
    'billing_same_as_shipping': True,
    'product': True,
    'contact': {
        'email': e,
        'phone_number': '+33758839929',
        'first_name': n,
        'last_name': n,
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

response = r.post('https://www.clickfunnels.com/scale-monthly-step-2', cookies=r.cookies, headers=headers, json=json_data)

print(response.text)