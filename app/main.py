import asyncio

from app.bot_app import create_bot_and_dispatcher, init_app


async def main() -> None:
    await init_app()
    bot, dp = create_bot_and_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
