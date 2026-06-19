import requests
import re

r = requests.Session()

headers = {
    'authority': 'awwatersheds.org',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryMxr4PdnqPmsBg69V',
    'origin': 'https://awwatersheds.org',
    'referer': 'https://awwatersheds.org/donate/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
}

files = {
    'give-honeypot': (None, ''),
    'give-form-id-prefix': (None, '4572-1'),
    'give-form-id': (None, '4572'),
    'give-form-title': (None, 'Donate Now'),
    'give-current-url': (None, 'https://awwatersheds.org/donate/'),
    'give-form-url': (None, 'https://awwatersheds.org/donate/'),
    'give-form-minimum': (None, '1'),
    'give-form-maximum': (None, '1000000'),
    'give-form-hash': (None, 'bfe3071ab0'),
    'give-price-id': (None, 'custom'),
    'give-recurring-logged-in-only': (None, ''),
    'give-logged-in-only': (None, '1'),
    'give_recurring_donation_details': (None, '{"is_recurring":false}'),
    'give-amount': (None, '1'),
    'payment-mode': (None, 'paypal-commerce'),
    'give_first': (None, 'Tommy'),
    'give_last': (None, 'Walid'),
    'give_email': (None, 'PythonXapi@gmal.com'),
    'give_comment': (None, ''),
    'give_lake_affiliation': (None, 'Lovell Lake'),
    'give_lake_affiliation_other': (None, ''),
    'card_exp_month': (None, ''),
    'card_exp_year': (None, ''),
    'give_action': (None, 'purchase'),
    'give-gateway': (None, 'paypal-commerce'),
    'action': (None, 'give_process_donation'),
    'give_ajax': (None, 'true'),
}

response = r.post('https://awwatersheds.org/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, files=files)

headers = {
    'authority': 'awwatersheds.org',
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryxFpnAqtRSqqlY03V',
    'origin': 'https://awwatersheds.org',
    'referer': 'https://awwatersheds.org/donate/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
}

params = {
    'action': 'give_paypal_commerce_create_order',
}

files = {
    'give-honeypot': (None, ''),
    'give-form-id-prefix': (None, '4572-1'),
    'give-form-id': (None, '4572'),
    'give-form-title': (None, 'Donate Now'),
    'give-current-url': (None, 'https://awwatersheds.org/donate/'),
    'give-form-url': (None, 'https://awwatersheds.org/donate/'),
    'give-form-minimum': (None, '1'),
    'give-form-maximum': (None, '1000000'),
    'give-form-hash': (None, 'bfe3071ab0'),
    'give-price-id': (None, 'custom'),
    'give-recurring-logged-in-only': (None, ''),
    'give-logged-in-only': (None, '1'),
    'give_recurring_donation_details': (None, '{"is_recurring":false}'),
    'give-amount': (None, '1'),
    'payment-mode': (None, 'paypal-commerce'),
    'give_first': (None, 'Tommy'),
    'give_last': (None, 'Walid'),
    'give_email': (None, 'PythonXapi@gmal.com'),
    'give_comment': (None, ''),
    'give_lake_affiliation': (None, 'Lovell Lake'),
    'give_lake_affiliation_other': (None, ''),
    'card_exp_month': (None, ''),
    'card_exp_year': (None, ''),
    'give-gateway': (None, 'paypal-commerce'),
}

response = r.post(
    'https://awwatersheds.org/wp-admin/admin-ajax.php',
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
    'paypal-client-context': '37E13958RD450504A',
    'referer': 'https://www.paypal.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    'x-app-name': 'smart-payment-buttons',
}

json_data = {
    'query': '\n        query GetCheckoutDetails($orderID: String!) {\n            checkoutSession(token: $orderID) {\n                cart {\n                    billingType\n                    productCode\n                    intent\n                    paymentId\n                    billingToken\n                    amounts {\n                        total {\n                            currencyValue\n                            currencyCode\n                            currencyFormatSymbolISOCurrency\n                        }\n                    }\n                    supplementary {\n                        initiationIntent\n                    }\n                    category\n                }\n                flags {\n                    isChangeShippingAddressAllowed\n                }\n                payees {\n                    merchantId\n                    email {\n                        stringValue\n                    }\n                }\n            }\n        }\n        ',
    'variables': {
        'orderID': '37E13958RD450504A',
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
    'paypal-client-context': '37E13958RD450504A',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    'x-app-name': 'standardcardfields',
    'x-country': 'US',
}

json_data = {
    'query': '\n        mutation payWithCard(\n            $token: String!\n            $card: CardInput\n            $paymentToken: String\n            $phoneNumber: String\n            $firstName: String\n            $lastName: String\n            $shippingAddress: AddressInput\n            $billingAddress: AddressInput\n            $email: String\n            $currencyConversionType: CheckoutCurrencyConversionType\n            $installmentTerm: Int\n            $identityDocument: IdentityDocumentInput\n            $feeReferenceId: String\n        ) {\n            approveGuestPaymentWithCreditCard(\n                token: $token\n                card: $card\n                paymentToken: $paymentToken\n                phoneNumber: $phoneNumber\n                firstName: $firstName\n                lastName: $lastName\n                email: $email\n                shippingAddress: $shippingAddress\n                billingAddress: $billingAddress\n                currencyConversionType: $currencyConversionType\n                installmentTerm: $installmentTerm\n                identityDocument: $identityDocument\n                feeReferenceId: $feeReferenceId\n            ) {\n                flags {\n                    is3DSecureRequired\n                }\n                cart {\n                    intent\n                    cartId\n                    buyer {\n                        userId\n                        auth {\n                            accessToken\n                        }\n                    }\n                    returnUrl {\n                        href\n                    }\n                }\n                paymentContingencies {\n                    threeDomainSecure {\n                        status\n                        method\n                        redirectUrl {\n                            href\n                        }\n                        parameter\n                    }\n                }\n            }\n        }\n        ',
    'variables': {
        'token': '37E13958RD450504A',
        'card': {
            'cardNumber': '4419206163338130',
            'expirationDate': '10/2028',
            'postalCode': '96400',
            'securityCode': '028',
        },
        'phoneNumber': '3154962318',
        'firstName': 'tomym',
        'lastName': 'welson',
        'billingAddress': {
            'givenName': 'tomym',
            'familyName': 'welson',
            'line1': 'Cali park 39 qve vii',
            'line2': None,
            'city': 'California',
            'state': 'CA',
            'postalCode': '96400',
            'country': 'US',
        },
        'shippingAddress': {
            'givenName': 'tomym',
            'familyName': 'welson',
            'line1': 'Cali park 39 qve vii',
            'line2': None,
            'city': 'California',
            'state': 'CA',
            'postalCode': '96400',
            'country': 'US',
        },
        'email': 'PythonXapi@gmal.com',
        'currencyConversionType': 'PAYPAL',
    },
    'operationName': 'payWithCard',
}

response = r.post('https://www.paypal.com/graphql?paywithcard', cookies=r.cookies, headers=headers, json=json_data)

print(response.text)