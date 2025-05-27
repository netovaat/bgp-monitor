import os
from typing import Optional


class Settings:
    """Configurações da aplicação usando variáveis de ambiente"""
    
    def __init__(self):
        # Telegram
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        
        # BGP Monitoring
        self.target_asn = int(os.getenv("TARGET_ASN", "0"))
        self.max_latency_ms = int(os.getenv("MAX_LATENCY_MS", "250"))
        self.min_upstreams = int(os.getenv("MIN_UPSTREAMS", "2"))
        self.irr_check_interval = int(os.getenv("IRR_CHECK_INTERVAL", "3600"))
        
        # RIPE API
        self.ripe_api_key = os.getenv("RIPE_API_KEY")
        self.ripe_base_url = os.getenv("RIPE_BASE_URL", "https://stat.ripe.net/data")
        
        # Monitoring intervals (seconds)
        self.prefix_check_interval = int(os.getenv("PREFIX_CHECK_INTERVAL", "300"))
        self.peer_check_interval = int(os.getenv("PEER_CHECK_INTERVAL", "600"))
        
        # HTTP/API settings
        self.port = int(os.getenv("PORT", "8000"))
        self.host = os.getenv("HOST", "0.0.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        # Monitoring intervals adicionais
        self.aspath_check_interval = int(os.getenv("ASPATH_CHECK_INTERVAL", "300"))
        self.latency_check_interval = int(os.getenv("LATENCY_CHECK_INTERVAL", "900"))
        
        # Alerting
        self.alert_cooldown = int(os.getenv("ALERT_COOLDOWN", "1800"))


# Instância global das configurações
settings = Settings()
