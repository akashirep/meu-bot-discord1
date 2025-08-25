#!/usr/bin/env python3
"""
Keep Alive Service - Mantém o bot ativo no Replit
Servidor web simples que responde a requests para evitar que o Replit durma
"""

import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify
import logging

# Configuração de logging para Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

app = Flask(__name__)

# Referência para o gerenciador do bot
bot_manager = None

@app.route('/')
def home():
    """Página principal com status do bot"""
    return render_template('index.html')

@app.route('/status')
def status():
    """API endpoint com status detalhado do bot"""
    if bot_manager:
        status_data = bot_manager.get_status()
        status_data['timestamp'] = datetime.now().isoformat()
        return jsonify(status_data)
    else:
        return jsonify({
            'running': False,
            'uptime': '0:00:00',
            'restart_count': 0,
            'bot_ready': False,
            'guild_count': 0,
            'timestamp': datetime.now().isoformat(),
            'error': 'Bot manager not initialized'
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'FenixBot Keep Alive'
    })

@app.route('/ping')
def ping():
    """Endpoint simples para keep alive"""
    return 'pong'

def run_keep_alive(manager=None):
    """
    Executa o servidor Flask para keep alive
    Args:
        manager: Instância do BotManager para obter status
    """
    global bot_manager
    bot_manager = manager
    
    try:
        # Executa o servidor Flask
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logging.error(f"Erro no serviço keep-alive: {e}")

def start_monitoring():
    """Inicia thread de monitoramento do bot"""
    def monitor():
        while True:
            try:
                time.sleep(300)  # 5 minutos
                if bot_manager:
                    status = bot_manager.get_status()
                    logging.info(f"Monitor: Bot running={status['running']}, "
                               f"ready={status['bot_ready']}, "
                               f"guilds={status['guild_count']}")
            except Exception as e:
                logging.error(f"Erro no monitor: {e}")
    
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

if __name__ == "__main__":
    # Para teste individual
    run_keep_alive()
