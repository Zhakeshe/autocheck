import asyncio
from pyrogram import Client
from pyrogram.raw.functions.payments import GetStarGifts, GetStarsStatus
from pyrogram.raw.types.payments import StarGiftsNotModified
from pyrogram.raw.types import InputPeerSelf
from aiogram import Bot

SESSION_NAME = "test"

BOT_TOKEN = "7817713558:AAGQUcTKqNmR3GAx-zfHt0aKh4Tneoa_sLQ"
CHAT_ID = 8073910583  # Хабарлама алатын чат немесе user id
CHECK_INTERVAL_SECONDS = 5

known_gift_ids = set()
last_gift_list_hash = 0

app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
bot = Bot(token=BOT_TOKEN)

async def get_current_star_balance():
    try:
        status = await app.invoke(GetStarsStatus(peer=InputPeerSelf()))
        return status.balance.amount
    except Exception:
        return 0

async def monitor_and_notify():
    global known_gift_ids, last_gift_list_hash
    initial_gifts_response = await app.invoke(GetStarGifts(hash=0))
    if hasattr(initial_gifts_response, 'gifts'):
        for gift in initial_gifts_response.gifts:
            known_gift_ids.add(gift.id)
        last_gift_list_hash = initial_gifts_response.hash

    while True:
        try:
            star_gifts_response = await app.invoke(
                GetStarGifts(hash=last_gift_list_hash)
            )

            if hasattr(star_gifts_response, 'gifts'):
                for gift_data in star_gifts_response.gifts:
                    if gift_data.id not in known_gift_ids:
                        known_gift_ids.add(gift_data.id)

                        # Фильтр: қара фон және ≤ 500 звезда
                        if getattr(gift_data, "background_colors", None) == ["#000000"] and gift_data.stars <= 500:
                            text = f"🎁 Жаңа подарка!\nID: {gift_data.id}\n⭐ {gift_data.stars}\n{getattr(gift_data, 'title', 'N/A')}"
                            await bot.send_message(CHAT_ID, text)

                last_gift_list_hash = star_gifts_response.hash

            elif isinstance(star_gifts_response, StarGiftsNotModified):
                pass

        except Exception as e:
            print(f"Қате: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

async def main():
    await app.start()
    try:
        await monitor_and_notify()
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
