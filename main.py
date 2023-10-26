import asyncio
from bot import bot, dp
from data_storage.data import data


async def main():
    # Delete webhook (in case it was previously set) and start polling
    import data_storage.data
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
