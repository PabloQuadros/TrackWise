from telegram.ext import ApplicationBuilder
from src.services.telegram_bot_service import TelegramBotService

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(self.token).build()
        self.handler = TelegramBotService()
        self.handler.setup_handlers(self.app)

    async def start_in_background(self):
        await self.app.initialize()
        await self.app.start()
        print("Bot do Telegram iniciado!")
        import asyncio
        asyncio.create_task(self.app.updater.start_polling())