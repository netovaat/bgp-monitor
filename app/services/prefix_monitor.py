import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.services.ripe_api import ripe_api
from app.services.telegram import telegram_service
from app.core.config import settings
from app.utils.metrics import metrics

logger = logging.getLogger(__name__)


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
        logger.info(f"Added prefix to monitoring: {prefix}")
        
    def remove_monitored_prefix(self, prefix: str):
        """Remove um prefixo do monitoramento"""
        self.monitored_prefixes = [
            p for p in self.monitored_prefixes 
            if p["prefix"] != prefix
        ]
        logger.info(f"Removed prefix from monitoring: {prefix}")
        
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
                
            logger.info(f"Checking prefix announcements (count: {len(self.monitored_prefixes)})")
            
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
                        
                        logger.warning(f"Missing prefix detected: {prefix} (ASN: {self.target_asn})")
                else:
                    # Verifica se o prefixo estava ausente e agora foi restaurado
                    if self._had_recent_alert("prefix_missing", prefix):
                        # Calcula tempo de ausência
                        downtime_minutes = self._calculate_downtime("prefix_missing", prefix)
                        
                        recovery_data = {
                            "alert_type": "prefix_restored",
                            "severity": "info",
                            "title": f"Prefixo {prefix} restaurado",
                            "message": f"🟢 Prefixo {prefix} restaurado na tabela BGP.",
                            "details": {
                                "prefix": prefix,
                                "asn": self.target_asn,
                                "downtime_minutes": downtime_minutes,
                                "check_time": datetime.utcnow().isoformat()
                            }
                        }
                        
                        # Envia notificação de recuperação
                        await telegram_service.send_recovery_alert(recovery_data)
                        logger.info(f"Prefix recovery detected: {prefix} (ASN: {self.target_asn}), downtime: {downtime_minutes}min")
                    
                    # Prefixo está sendo anunciado - limpa alertas
                    self._clear_alert("prefix_missing", prefix)
                    logger.debug(f"Prefix announcement confirmed: {prefix}")
                    
        except Exception as e:
            logger.error(f"Error checking prefix announcements: {str(e)}")
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
    
    def _had_recent_alert(self, alert_type: str, identifier: str) -> bool:
        """Verifica se um alerta existia recentemente (para detecção de recuperação)"""
        key = f"{alert_type}:{identifier}"
        return key in self.last_alerts
    
    def _calculate_downtime(self, alert_type: str, identifier: str) -> int:
        """Calcula tempo de indisponibilidade em minutos desde o alerta original"""
        key = f"{alert_type}:{identifier}"
        last_alert = self.last_alerts.get(key)
        
        if last_alert:
            alert_time = datetime.fromisoformat(last_alert)
            current_time = datetime.utcnow()
            time_diff = current_time - alert_time
            return int(time_diff.total_seconds() / 60)
        
        return 0


# Instância global do monitor
prefix_monitor = PrefixMonitor()
