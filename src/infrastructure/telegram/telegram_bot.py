from telegram.ext import ApplicationBuilder
from src.services.telegram_bot_service import TelegramBotService
import asyncio
from telegram.error import Conflict


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(self.token).build()
        self.handler = TelegramBotService()
        self.handler.setup_handlers(self.app)
        self._is_running = False

    async def start_in_background(self):
        if self._is_running:
            print("O bot já está em execução!")
            return

        try:
            await self.app.initialize()
            await self.app.start()
            
            # Configuração recomendada para polling
            await self.app.updater.start_polling(
                drop_pending_updates=True,  # Ignora updates pendentes ao iniciar
                timeout=10,  # Tempo de espera por updates
                poll_interval=0.5  # Intervalo entre requisições
            )
            
            self._is_running = True
            print("Bot do Telegram iniciado com sucesso!")
            
        except Conflict as e:
            print(f"Erro: Já existe uma instância do bot em execução. {e}")
            await self._shutdown()
            raise
        except Exception as e:
            print(f"Erro ao iniciar o bot: {e}")
            await self._shutdown()
            raise

    async def stop(self):
        if not self._is_running:
            return
            
        try:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            self._is_running = False
            print("Bot do Telegram parado com sucesso!")
        except Exception as e:
            print(f"Erro ao parar o bot: {e}")
            raise

    async def _shutdown(self):
        """Método auxiliar para desligamento seguro"""
        try:
            if hasattr(self, 'app') and self.app:
                await self.stop()
        except Exception as e:
            print(f"Erro durante o desligamento: {e}")

    async def __aenter__(self):
        await self.start_in_background()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()