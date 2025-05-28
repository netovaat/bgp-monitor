import os
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()


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
        
        # Database settings
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", "5432"))
        self.db_name = os.getenv("DB_NAME", "bgp_monitor")
        self.db_user = os.getenv("DB_USER", "bgp_monitor")
        self.db_password = os.getenv("DB_PASSWORD", "bgp_monitor_password")
        
        # Data retention settings
        self.data_retention_days = int(os.getenv("DATA_RETENTION_DAYS", "365"))
        self.cleanup_interval_hours = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))
        
        # Rate limiting for API calls
        self.api_rate_limit_per_asn = int(os.getenv("API_RATE_LIMIT_PER_ASN", "30"))  # seconds
        self.api_batch_size = int(os.getenv("API_BATCH_SIZE", "5"))  # ASNs per batch


# Instância global das configurações
settings = Settings()
