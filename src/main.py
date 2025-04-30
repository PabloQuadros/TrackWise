from fastapi import FastAPI
from src.controllers.container_controller import router as container_router
from src.infrastructure.telegram.telegram_bot import TelegramBot
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from src.services.container_search_scheduling_service import get_container_search_scheduling_service
import asyncio
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

telegram_bot = TelegramBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
container_search_scheduling_service = get_container_search_scheduling_service()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_bot.start_in_background()
    print("Bot Telegram rodando...")
    
    asyncio.create_task(container_search_scheduling_service.start())
    print("Rotina de busca agendada iniciada...")

    yield

    await telegram_bot.app.stop()
    print("Bot Telegram finalizado.")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(container_router, prefix="/api/v1")



