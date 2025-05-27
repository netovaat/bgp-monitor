import time
from typing import Dict, Any
from datetime import datetime
import structlog

logger = structlog.get_logger()


class SimpleMetrics:
    """Sistema simples de métricas em memória"""
    
    def __init__(self):
        self.start_time = time.time()
        self.alert_counters = {}
        self.component_status = {}
        self.last_checks = {}
    
    def record_alert(self, alert_type: str, severity: str):
        """Registra um novo alerta"""
        key = f"{alert_type}.{severity}"
        current_count = self.alert_counters.get(key, 0) + 1
        self.alert_counters[key] = current_count
        
        logger.info("Alert recorded", alert_type=alert_type, severity=severity, count=current_count)
    
    def update_component_health(self, component: str, healthy: bool):
        """Atualiza status de saúde de um componente"""
        self.component_status[component] = healthy
        logger.debug("Component health updated", component=component, healthy=healthy)
    
    def record_check_duration(self, check_type: str, duration: float):
        """Registra duração de uma verificação"""
        self.last_checks[check_type] = {
            "duration": duration,
            "timestamp": time.time()
        }
        logger.debug("Check duration recorded", check_type=check_type, duration=duration)
    
    def record_api_request(self, endpoint: str, success: bool):
        """Registra requisição à API do RIPE"""
        logger.debug("API request recorded", endpoint=endpoint, success=success)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        uptime = int(time.time() - self.start_time)
        total_alerts = sum(self.alert_counters.values())
        healthy_components = sum(1 for status in self.component_status.values() if status)
        
        return {
            "uptime_seconds": uptime,
            "total_alerts": total_alerts,
            "healthy_components": healthy_components,
            "total_components": len(self.component_status),
            "last_checks": self.last_checks,
            "alert_breakdown": self.alert_counters
        }


# Instância global do coletor de métricas
metrics = SimpleMetrics()
