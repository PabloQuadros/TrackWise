from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from src.services.container_service import ContainerService
from src.repositories.container_repository import get_container_repository
from src.mappers.container_mapper import get_container_mapper
from src.services.msc_service import get_msc_service
from src.services.search_scheduling_service import get_search_scheduling_service
import re

class TelegramBotService:
    def __init__(self):
        self.container_service = ContainerService(get_container_repository(), get_container_mapper(), get_msc_service(), get_search_scheduling_service())

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
        text = update.message.text.strip()

        if action == "viewing_container":
            container_format = r"^[A-Za-z]{4}[0-9]{7}$"  # 4 letras seguidas de 7 números
            if not re.match(container_format, text):
                await update.message.reply_text("⚠️ O número do container não está no formato correto. Tente novamente.")
                return
            container_info = self.container_service.find_by_container_number(text)
            if not container_info:
                await update.message.reply_text(f"⚠️ Container {text} não encontrado. Tente novamente.")
                return
            await update.message.reply_text(container_info.to_telegram_chat(), parse_mode="Markdown")
        elif action == "registering_container":
            if "container_number" not in context.user_data:
                container_format = r"^[A-Z]{4}[0-9]{7}$"
                if not re.match(container_format, text):
                    await update.message.reply_text("⚠️ O número do container não está no formato correto (ex: MSCU1234567).")
                    return
                context.user_data["container_number"] = text
                await update.message.reply_text("Agora informe o nome do armador (ex: MSC, MAERSK, etc.):")
                return

            if "shipping_company" not in context.user_data:
                context.user_data["shipping_company"] = text
                await update.message.reply_text("Se desejar, informe o número do booking. Caso não tenha, digite - (hífen):")
                return

            if "booking_number" not in context.user_data:
                context.user_data["booking_number"] = text if text != "-" else None

                # Criar objeto ContainerCreate
                from src.models.container_create import ContainerCreate
                try:
                    container_create = ContainerCreate(
                        number=context.user_data["container_number"],
                        shipping_company=context.user_data["shipping_company"],
                        booking_number=context.user_data["booking_number"]
                    )
                    result = self.container_service.register_container(container_create)
                    await update.message.reply_text(f"✅ Container cadastrado com sucesso!\n\n{result}")
                except Exception as e:
                    await update.message.reply_text(f"❌ Erro ao cadastrar o container: {str(e)}")

                # Limpar dados após finalizar o cadastro
                context.user_data.clear()
                return
        else:
            await update.message.reply_text("Por favor, escolha uma opção primeiro usando /start.")

        context.user_data["action"] = None

    def setup_handlers(self, app):
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_container_message))
