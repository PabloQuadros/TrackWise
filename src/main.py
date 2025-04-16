from fastapi import FastAPI
from src.controllers.container_controller import router as container_router
from src.infrastructure.telegram.telegram_bot import TelegramBot
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

telegram_bot = TelegramBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_bot.start_in_background()
    print("Bot Telegram rodando...")
    
    yield

    await telegram_bot.app.stop()
    print("Bot Telegram finalizado.")

app = FastAPI(lifespan=lifespan)
app.include_router(container_router, prefix="/api/v1")