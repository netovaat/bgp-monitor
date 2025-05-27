import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from app.services.ripe_api import ripe_api
from app.services.telegram import telegram_service
from app.core.config import settings
from app.utils.metrics import metrics

logger = structlog.get_logger()


class PrefixMonitor:
    """Monitor de prefixos BGP"""
    
    def __init__(self):
        self.target_asn = settings.target_asn
        # Lista de prefixos monitorados em memória
        self.monitored_prefixes = []
        self.last_alerts = {}  # Cache de alertas recentes
        
    def add_monitored_prefix(self, prefix: str, description: str = ""):
        """Adiciona um prefixo para monitoramento"""
        prefix_data = {
            "prefix": prefix,
            "asn": self.target_asn,
            "description": description,
            "added_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        self.monitored_prefixes.append(prefix_data)
        logger.info("Added prefix to monitoring", prefix=prefix)
        
    def remove_monitored_prefix(self, prefix: str):
        """Remove um prefixo do monitoramento"""
        self.monitored_prefixes = [
            p for p in self.monitored_prefixes 
            if p["prefix"] != prefix
        ]
        logger.info("Removed prefix from monitoring", prefix=prefix)
        
    def get_monitored_prefixes(self) -> List[Dict[str, Any]]:
        """Retorna lista de prefixos monitorados"""
        return self.monitored_prefixes.copy()
        
    async def check_prefix_announcements(self) -> List[Dict[str, Any]]:
        """Verifica se todos os prefixos monitorados estão sendo anunciados"""
        alerts = []
        
        try:
            if not self.monitored_prefixes:
                logger.info("No prefixes configured for monitoring")
                return alerts
                
            logger.info("Checking prefix announcements", count=len(self.monitored_prefixes))
            
            # Busca prefixos atualmente anunciados
            announced_prefixes = await ripe_api.get_announced_prefixes(self.target_asn)
            announced_set = {p.get("prefix") for p in announced_prefixes}
            
            for prefix_obj in self.monitored_prefixes:
                if not prefix_obj.get("is_active"):
                    continue
                    
                prefix = prefix_obj["prefix"]
                
                if prefix not in announced_set:
                    # Prefixo não está sendo anunciado - criar alerta
                    alert_data = {
                        "alert_type": "prefix_missing",
                        "severity": "critical",
                        "title": f"Prefixo {prefix} não encontrado nos anúncios globais",
                        "message": f"🚨 O prefixo {prefix} do AS{self.target_asn} não foi encontrado nos anúncios globais do BGP.",
                        "details": {
                            "prefix": prefix,
                            "asn": self.target_asn,
                            "last_seen": None,
                            "check_time": datetime.utcnow().isoformat()
                        }
                    }
                    
                    # Verifica se já existe um alerta similar recente
                    if not self._has_recent_alert("prefix_missing", prefix):
                        alerts.append(alert_data)
                        self._record_alert("prefix_missing", prefix)
                        
                        # Envia notificação Telegram
                        await telegram_service.send_alert(alert_data)
                        
                        # Atualiza métricas
                        metrics.increment_alert_counter("prefix_missing")
                        
                        logger.warning("Missing prefix detected", prefix=prefix, asn=self.target_asn)
                else:
                    # Prefixo está sendo anunciado - limpa alertas
                    self._clear_alert("prefix_missing", prefix)
                    logger.debug("Prefix announcement confirmed", prefix=prefix)
                    
        except Exception as e:
            logger.error("Error checking prefix announcements", error=str(e))
            metrics.update_component_health("prefix_monitor", False)
            raise
            
        # Atualiza saúde do componente
        metrics.update_component_health("prefix_monitor", True)
        metrics.record_check_time("prefix_check")
        
        return alerts
    
    def _has_recent_alert(self, alert_type: str, identifier: str) -> bool:
        """Verifica se já existe alerta recente para evitar spam"""
        key = f"{alert_type}:{identifier}"
        last_alert = self.last_alerts.get(key)
        
        if last_alert:
            # Considera recente se foi há menos de 1 hora
            time_diff = datetime.utcnow() - datetime.fromisoformat(last_alert)
            return time_diff < timedelta(hours=1)
            
        return False
    
    def _record_alert(self, alert_type: str, identifier: str):
        """Registra um alerta para controle de frequência"""
        key = f"{alert_type}:{identifier}"
        self.last_alerts[key] = datetime.utcnow().isoformat()
    
    def _clear_alert(self, alert_type: str, identifier: str):
        """Remove registro de alerta quando problema é resolvido"""
        key = f"{alert_type}:{identifier}"
        self.last_alerts.pop(key, None)


# Instância global do monitor
prefix_monitor = PrefixMonitor()
