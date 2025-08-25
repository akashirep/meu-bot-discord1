#!/usr/bin/env python3
"""
FenixBots - Sistema de Tickets Discord
Aplicação principal que executa o bot Discord e o serviço keep-alive
"""

import asyncio
import logging
import os
import sys
import threading
import time
from datetime import datetime

from bot_final import FenixBotFinal
from keep_alive import run_keep_alive

# Configuração de logging otimizada para deploy
is_deployed = os.getenv('REPLIT_DEPLOYMENT') == '1'

if is_deployed:
    # Em deploy: apenas console, sem arquivos de log
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
else:
    # Em desenvolvimento: logs em arquivo e console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/fenix_bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)

class BotManager:
    """Gerenciador principal do bot com auto-restart e monitoramento"""
    
    def __init__(self):
        self.bot = None
        self.running = False
        self.restart_count = 0
        self.start_time = datetime.now()
        
    async def start_bot(self):
        """Inicia o bot Discord com tratamento de erros"""
        try:
            logger.info("Iniciando FenixBot...")
            self.bot = FenixBotFinal()
            await self.bot.start()
        except Exception as e:
            logger.error(f"Erro ao iniciar o bot: {e}")
            raise
            
    async def run_with_restart(self):
        """Executa o bot com restart automático em caso de falha"""
        self.running = True
        
        while self.running:
            try:
                await self.start_bot()
            except Exception as e:
                self.restart_count += 1
                logger.error(f"Bot crashou (restart #{self.restart_count}): {e}")
                
                if self.restart_count > 10:
                    logger.critical("Muitos restarts consecutivos. Parando o bot.")
                    break
                    
                logger.info(f"Reiniciando em 30 segundos...")
                await asyncio.sleep(30)
                
                # Limpa o bot anterior
                if self.bot:
                    try:
                        await self.bot.close()
                    except:
                        pass
                    self.bot = None
            else:
                # Bot parou normalmente
                logger.info("Bot parou normalmente.")
                break
                
    def stop(self):
        """Para o bot graciosamente"""
        logger.info("Parando FenixBot...")
        self.running = False
        if self.bot:
            asyncio.create_task(self.bot.close())
            
    def get_status(self):
        """Retorna status atual do bot"""
        uptime = datetime.now() - self.start_time
        return {
            'running': self.running,
            'uptime': str(uptime).split('.')[0],  # Remove microsegundos
            'restart_count': self.restart_count,
            'bot_ready': self.bot.is_ready() if self.bot else False,
            'guild_count': len(self.bot.guilds) if self.bot and self.bot.is_ready() else 0
        }

# Instância global do gerenciador
bot_manager = BotManager()

def run_bot():
    """Executa o bot em uma thread separada"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_manager.run_with_restart())
    except Exception as e:
        logger.error(f"Erro crítico no bot: {e}")
    finally:
        logger.info("Thread do bot finalizada")

def main():
    """Função principal"""
    logger.info("=" * 50)
    logger.info("FenixBots - Sistema de Tickets Discord")
    logger.info("Iniciando aplicação...")
    logger.info("=" * 50)
    
    # Verifica se o token está configurado
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN não encontrado nas variáveis de ambiente!")
        logger.error("Configure o token do bot antes de continuar.")
        sys.exit(1)
    
    # Cria diretórios necessários (apenas em desenvolvimento)
    if not is_deployed:
        os.makedirs("logs", exist_ok=True)
        os.makedirs("transcripts", exist_ok=True)
    
    try:
        # Inicia o serviço keep-alive em thread separada
        logger.info("Iniciando serviço keep-alive...")
        keep_alive_thread = threading.Thread(target=run_keep_alive, args=(bot_manager,))
        keep_alive_thread.daemon = True
        keep_alive_thread.start()
        
        # Aguarda um pouco para o servidor web iniciar
        time.sleep(2)
        logger.info("Serviço keep-alive iniciado com sucesso")
        
        # Inicia o bot Discord em thread separada
        logger.info("Iniciando bot Discord...")
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        if is_deployed:
            logger.info("🚀 FenixBot DEPLOYED - Rodando 24/7 no servidor!")
            logger.info("✅ Bot online permanentemente - pode fechar o navegador!")
        else:
            logger.info("🔧 FenixBot em desenvolvimento")
            logger.info("Pressione Ctrl+C para parar")
        
        # Mantém o programa principal rodando
        try:
            while True:
                time.sleep(60)  # Verifica a cada minuto
                
                # Log de status periodico
                status = bot_manager.get_status()
                logger.info(f"Status: Running={status['running']}, "
                           f"Uptime={status['uptime']}, "
                           f"Restarts={status['restart_count']}, "
                           f"Guilds={status['guild_count']}")
                
        except KeyboardInterrupt:
            logger.info("Interrupção detectada. Parando...")
            
    except Exception as e:
        logger.error(f"Erro na aplicação principal: {e}")
    finally:
        # Cleanup
        logger.info("Finalizando aplicação...")
        bot_manager.stop()
        logger.info("Aplicação finalizada")

if __name__ == "__main__":
    main()
