from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

class TelegramBotService:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(self.token).build()
        self.setup_handlers()

    async def start_command(self, update, context):
        # Criando os botões
        keyboard = [
            [
                InlineKeyboardButton("Cadastrar Novo Container", callback_data='register_container'),
                InlineKeyboardButton("Visualizar Container", callback_data='view_container')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Enviando a mensagem com os botões
        await update.message.reply_text(
            "Bem Vindo ao TrackWise! Escolha uma das opções abaixo:",
            reply_markup=reply_markup
        )

    async def handle_container_message(self, update, context):
        container_number = update.message.text.strip()
        await update.message.reply_text(f"Container {container_number} cadastrado!")

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_container_message))

    async def start_in_background(self):
        await self.app.initialize()
        await self.app.start()
        print("Bot do Telegram iniciado!")
        # Essa linha mantém o bot ouvindo sem bloquear a FastAPI
        asyncio.create_task(self.app.updater.start_polling())
