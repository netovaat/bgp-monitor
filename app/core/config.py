from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str
    telegram_chat_id: str
    
    # BGP Monitoring
    target_asn: int
    max_latency_ms: int = 250
    min_upstreams: int = 2
    irr_check_interval: int = 3600
    
    # RIPE API
    ripe_api_key: Optional[str] = None
    ripe_base_url: str = "https://stat.ripe.net/data"
    
    # Monitoring intervals (seconds)
    prefix_check_interval: int = 300  # 5 minutes
    aspath_check_interval: int = 300  # 5 minutes
    peer_check_interval: int = 600    # 10 minutes
    latency_check_interval: int = 900 # 15 minutes
    
    # Alerting
    alert_cooldown: int = 1800  # 30 minutes between same alerts
    
    # Application
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()
