from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from src.services.container_service import ContainerService
from src.repositories.container_repository import get_container_repository
from src.mappers.container_mapper import get_container_mapper
from src.services.msc_service import get_msc_service
import re

class TelegramBotService:
    def __init__(self):
        self.container_service = ContainerService(get_container_repository(), get_container_mapper(), get_msc_service())

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[
            InlineKeyboardButton("Cadastrar Novo Container", callback_data='register_container'),
            InlineKeyboardButton("Visualizar Container", callback_data='view_container')
        ]]
        await update.message.reply_text(
            "Bem Vindo ao TrackWise! Escolha uma das opções abaixo:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "view_container":
            context.user_data["action"] = "viewing_container"
            await query.message.reply_text("Informe o número do container que deseja visualizar:")
        elif query.data == "register_container":
            context.user_data["action"] = "registering_container"
            await query.message.reply_text("Informe o número do container para cadastrar:")

    async def handle_container_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        action = context.user_data.get("action")
        number = update.message.text.strip()

        if action == "viewing_container":
            container_format = r"^[A-Za-z]{4}[0-9]{7}$"  # 4 letras seguidas de 7 números
            if not re.match(container_format, number):
                await update.message.reply_text("⚠️ O número do container não está no formato correto. Tente novamente.")
                return
            container_info = self.container_service.find_by_container_number(number)
            if not container_info:
                await update.message.reply_text(f"⚠️ Container {number} não encontrado. Tente novamente.")
                return
            await update.message.reply_text(container_info.to_telegram_chat(), parse_mode="Markdown")
        elif action == "registering_container":
            result = self.container_service.register_container(number)
            await update.message.reply_text(result)
        else:
            await update.message.reply_text("Por favor, escolha uma opção primeiro usando /start.")

        context.user_data["action"] = None

    def setup_handlers(self, app):
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_container_message))
