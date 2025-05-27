import asyncio
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta
import structlog

from app.services.ripe_api import ripe_api
from app.services.telegram import telegram_service
from app.core.config import settings
from app.utils.metrics import metrics

logger = structlog.get_logger()


class PeerMonitor:
    """Monitor de relacionamentos BGP e peers"""
    
    def __init__(self):
        self.target_asn = settings.target_asn
        self.min_upstreams = settings.min_upstreams
        self.known_peers = {}  # Cache de peers conhecidos
        self.last_alerts = {}  # Cache de alertas recentes
        
    async def check_peer_relationships(self) -> List[Dict[str, Any]]:
        """Monitora relacionamentos BGP e detecta perda de peers"""
        alerts = []
        
        try:
            # Obtém vizinhos atuais do ASN
            neighbours_data = await ripe_api.get_asn_neighbours(self.target_asn)
            current_peers = self._extract_peer_info(neighbours_data)
            current_peer_asns = {peer["asn"] for peer in current_peers}
            
            # Se é a primeira execução, apenas armazena os peers atuais
            if not self.known_peers:
                self.known_peers = {peer["asn"]: peer for peer in current_peers}
                logger.info("Initial peer discovery", peer_count=len(current_peers))
                return alerts
                
            # Detecta peers perdidos
            known_peer_asns = set(self.known_peers.keys())
            lost_peers = known_peer_asns - current_peer_asns
            new_peers = current_peer_asns - known_peer_asns
            
            # Alertas para peers perdidos
            for lost_asn in lost_peers:
                peer_info = self.known_peers.get(lost_asn, {})
                relationship = peer_info.get("relationship_type", "unknown")
                
                severity = "critical" if relationship == "upstream" else "warning"
                
                alert_data = {
                    "alert_type": "peer_loss",
                    "severity": severity,
                    "title": f"Perda de peer AS{lost_asn} detectada",
                    "message": f"🛑 Perda de {relationship} AS{lost_asn} detectada.",
                    "details": {
                        "peer_asn": lost_asn,
                        "relationship_type": relationship,
                        "target_asn": self.target_asn,
                        "check_time": datetime.utcnow().isoformat()
                    }
                }
                
                if not self._has_recent_alert("peer_loss", str(lost_asn)):
                    alerts.append(alert_data)
                    self._record_alert("peer_loss", str(lost_asn))
                    await telegram_service.send_alert(alert_data)
                    metrics.increment_alert_counter("peer_loss")
                    
                    logger.warning("Peer loss detected", peer_asn=lost_asn, relationship=relationship)
            
            # Log para novos peers (informativo)
            for new_asn in new_peers:
                logger.info("New peer discovered", peer_asn=new_asn)
            
            # Atualiza cache de peers conhecidos
            self.known_peers = {peer["asn"]: peer for peer in current_peers}
            
            # Verifica se temos upstreams suficientes
            upstream_count = len([
                p for p in current_peers 
                if p.get("relationship_type") == "upstream"
            ])
            
            if upstream_count < self.min_upstreams:
                alert_data = {
                    "alert_type": "insufficient_upstreams",
                    "severity": "critical",
                    "title": f"Upstreams insuficientes: {upstream_count}/{self.min_upstreams}",
                    "message": f"🚨 AS{self.target_asn} tem apenas {upstream_count} upstreams (mínimo: {self.min_upstreams})",
                    "details": {
                        "current_upstreams": upstream_count,
                        "required_upstreams": self.min_upstreams,
                        "target_asn": self.target_asn,
                        "check_time": datetime.utcnow().isoformat()
                    }
                }
                
                if not self._has_recent_alert("insufficient_upstreams", "global"):
                    alerts.append(alert_data)
                    self._record_alert("insufficient_upstreams", "global")
                    await telegram_service.send_alert(alert_data)
                    metrics.increment_alert_counter("insufficient_upstreams")
            else:
                # Limpa alerta de upstreams insuficientes se resolvido
                self._clear_alert("insufficient_upstreams", "global")
                
        except Exception as e:
            logger.error("Error checking peer relationships", error=str(e))
            metrics.update_component_health("peer_monitor", False)
            raise
            
        # Atualiza saúde do componente
        metrics.update_component_health("peer_monitor", True)
        metrics.record_check_time("peer_check")
        
        return alerts
    
    async def measure_latency(self) -> List[Dict[str, Any]]:
        """Mede latência para peers críticos (simulado)"""
        alerts = []
        
        try:
            # Implementação simplificada - em um cenário real seria conectar aos peers
            logger.info("Measuring peer latencies")
            
            # Simula medição de latência para upstreams
            upstream_peers = [
                p for p in self.known_peers.values() 
                if p.get("relationship_type") == "upstream"
            ]
            
            for peer in upstream_peers:
                # Simula latência (em produção seria ping/traceroute real)
                simulated_latency = 50.0  # ms
                
                if simulated_latency > settings.max_latency_ms:
                    alert_data = {
                        "alert_type": "high_latency",
                        "severity": "warning",
                        "title": f"Latência alta para AS{peer['asn']}: {simulated_latency}ms",
                        "message": f"⚠️ Latência para upstream AS{peer['asn']} está em {simulated_latency}ms (limite: {settings.max_latency_ms}ms)",
                        "details": {
                            "peer_asn": peer["asn"],
                            "latency_ms": simulated_latency,
                            "threshold_ms": settings.max_latency_ms,
                            "check_time": datetime.utcnow().isoformat()
                        }
                    }
                    
                    if not self._has_recent_alert("high_latency", str(peer["asn"])):
                        alerts.append(alert_data)
                        self._record_alert("high_latency", str(peer["asn"]))
                        await telegram_service.send_alert(alert_data)
                        metrics.increment_alert_counter("high_latency")
                
                # Registra métrica de latência
                metrics.record_latency_measurement(peer["asn"], simulated_latency)
                
        except Exception as e:
            logger.error("Error measuring latencies", error=str(e))
            
        return alerts
    
    def _extract_peer_info(self, neighbours_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai informações de peers dos dados da API"""
        peers = []
        
        data = neighbours_data.get("data", {})
        neighbours = data.get("neighbours", [])
        
        for neighbour in neighbours:
            peer_asn = neighbour.get("asn")
            if peer_asn:
                # Determina tipo de relacionamento baseado em heurísticas simples
                relationship_type = self._determine_relationship(neighbour)
                
                peer_info = {
                    "asn": peer_asn,
                    "relationship_type": relationship_type,
                    "description": neighbour.get("holder", ""),
                    "last_seen": datetime.utcnow().isoformat()
                }
                peers.append(peer_info)
                
        return peers
    
    def _determine_relationship(self, neighbour: Dict[str, Any]) -> str:
        """Determina tipo de relacionamento BGP (heurística simples)"""
        # Implementação básica - em produção seria mais sofisticada
        asn = neighbour.get("asn")
        
        # Heurística: ASNs menores geralmente são upstreams
        if asn and asn < 10000:
            return "upstream"
        elif asn and asn > 60000:
            return "customer"
        else:
            return "peer"
    
    def _has_recent_alert(self, alert_type: str, identifier: str) -> bool:
        """Verifica se já existe alerta recente para evitar spam"""
        key = f"{alert_type}:{identifier}"
        last_alert = self.last_alerts.get(key)
        
        if last_alert:
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
    
    def get_peer_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos peers atuais"""
        if not self.known_peers:
            return {"total": 0, "upstreams": 0, "peers": 0, "customers": 0}
            
        relationships = {}
        for peer in self.known_peers.values():
            rel_type = peer.get("relationship_type", "unknown")
            relationships[rel_type] = relationships.get(rel_type, 0) + 1
            
        return {
            "total": len(self.known_peers),
            "upstreams": relationships.get("upstream", 0),
            "peers": relationships.get("peer", 0), 
            "customers": relationships.get("customer", 0),
            "last_check": datetime.utcnow().isoformat()
        }


# Instância global do monitor
peer_monitor = PeerMonitor()
