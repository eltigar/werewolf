import asyncio
from bot import bot, dp


async def main():
    # Delete webhook (in case it was previously set) and start polling
    from data import game_service
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
