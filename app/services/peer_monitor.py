import asyncio
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta
import logging

from app.services.ripe_api import ripe_api
from app.services.telegram import telegram_service
from app.core.config import settings
from app.utils.metrics import metrics

logger = logging.getLogger(__name__)


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
                logger.info(f"Initial peer discovery - peer_count: {len(current_peers)}")
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
                    
                    logger.warning(f"Peer loss detected - peer_asn: {lost_asn}, relationship: {relationship}")
            
            # Notificações para peers recuperados
            for new_asn in new_peers:
                # Verifica se este peer tinha um alerta ativo
                if self._had_recent_alert("peer_loss", str(new_asn)):
                    # Encontra informações do peer recuperado
                    peer_info = next((p for p in current_peers if p["asn"] == new_asn), {})
                    relationship = peer_info.get("relationship_type", "unknown")
                    
                    # Calcula tempo de indisponibilidade
                    downtime_minutes = self._calculate_downtime("peer_loss", str(new_asn))
                    
                    recovery_data = {
                        "alert_type": "peer_recovered",
                        "severity": "info",
                        "title": f"Peer AS{new_asn} recuperado",
                        "message": f"🟢 {relationship.capitalize()} AS{new_asn} recuperado com sucesso.",
                        "details": {
                            "peer_asn": new_asn,
                            "relationship_type": relationship,
                            "target_asn": self.target_asn,
                            "downtime_minutes": downtime_minutes,
                            "check_time": datetime.utcnow().isoformat()
                        }
                    }
                    
                    await telegram_service.send_recovery_alert(recovery_data)
                    self._clear_alert("peer_loss", str(new_asn))
                    logger.info(f"Peer recovery detected - peer_asn: {new_asn}, relationship: {relationship}, downtime: {downtime_minutes}min")
            
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
                # Verifica se havia problema de upstreams insuficientes e agora foi resolvido
                if self._had_recent_alert("insufficient_upstreams", "global"):
                    # Calcula tempo do problema
                    problem_duration = self._calculate_downtime("insufficient_upstreams", "global")
                    
                    recovery_data = {
                        "alert_type": "upstreams_normalized",
                        "severity": "info",
                        "title": f"Upstreams normalizados: {upstream_count}/{self.min_upstreams}",
                        "message": f"🟢 Número de upstreams normalizado ({upstream_count}/{self.min_upstreams} mínimo).",
                        "details": {
                            "active_upstreams": upstream_count,
                            "minimum_required": self.min_upstreams,
                            "target_asn": self.target_asn,
                            "problem_duration_minutes": problem_duration,
                            "check_time": datetime.utcnow().isoformat()
                        }
                    }
                    
                    await telegram_service.send_recovery_alert(recovery_data)
                    logger.info(f"Upstreams normalized - count: {upstream_count}, duration: {problem_duration}min")
                
                # Limpa alerta de upstreams insuficientes se resolvido
                self._clear_alert("insufficient_upstreams", "global")
                
        except Exception as e:
            logger.error(f"Error checking peer relationships: {str(e)}")
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
                # Simula latência variável (em produção seria ping/traceroute real)
                import random
                # Simula latência entre 30-120ms com variação
                base_latency = random.uniform(30, 120)
                simulated_latency = round(base_latency, 1)
                
                peer_asn = peer["asn"]
                peer_name = peer.get("name", f"AS{peer_asn}")
                
                if simulated_latency > settings.max_latency_ms:
                    # Latência alta - criar alerta
                    alert_data = {
                        "alert_type": "high_latency",
                        "severity": "warning",
                        "title": f"Latência alta para AS{peer_asn}: {simulated_latency}ms",
                        "message": f"⚠️ Latência para upstream AS{peer_asn} está em {simulated_latency}ms (limite: {settings.max_latency_ms}ms)",
                        "details": {
                            "peer_asn": peer_asn,
                            "peer_name": peer_name,
                            "latency_ms": simulated_latency,
                            "threshold_ms": settings.max_latency_ms,
                            "check_time": datetime.utcnow().isoformat(),
                            "target_asn": self.target_asn
                        }
                    }
                    
                    if not self._has_recent_alert("high_latency", str(peer_asn)):
                        alerts.append(alert_data)
                        self._record_alert("high_latency", str(peer_asn))
                        await telegram_service.send_alert(alert_data)
                        metrics.increment_alert_counter("high_latency")
                else:
                    # Latência normal - verificar se havia problema e agora foi resolvido
                    if self._had_recent_alert("high_latency", str(peer_asn)):
                        # Calcular tempo do problema de latência
                        downtime_minutes = self._calculate_downtime("high_latency", str(peer_asn))
                        
                        # Obter latência anterior do cache de alertas se disponível
                        previous_latency = self._get_previous_latency(str(peer_asn))
                        
                        recovery_data = {
                            "alert_type": "latency_normalized",
                            "severity": "info",
                            "title": f"Latência normalizada para AS{peer_asn}",
                            "message": f"🟢 Latência normalizada para AS{peer_asn} ({simulated_latency}ms).",
                            "details": {
                                "peer_asn": peer_asn,
                                "peer_name": peer_name,
                                "current_latency": simulated_latency,
                                "previous_latency": previous_latency,
                                "max_latency": settings.max_latency_ms,
                                "downtime_minutes": downtime_minutes,
                                "target_asn": self.target_asn,
                                "recovery_time": datetime.utcnow().isoformat()
                            }
                        }
                        
                        alerts.append(recovery_data)
                        await telegram_service.send_recovery_alert(recovery_data)
                        
                        # Limpar alerta da cache
                        self._clear_alert("high_latency", str(peer_asn))
                        
                        logger.info(f"Latency normalized for AS{peer_asn}: {simulated_latency}ms (was {previous_latency}ms, down for {downtime_minutes}min)")
                
                # Registra métrica de latência
                metrics.record_latency_measurement(peer_asn, simulated_latency)
                
        except Exception as e:
            logger.error(f"Error measuring latencies: {str(e)}")
            
        return alerts
    
    async def check_specific_asn_peers(self, asn: int) -> Dict[str, Any]:
        """Verifica peers de um ASN específico"""
        try:
            # Obtém vizinhos do ASN específico
            neighbours_data = await ripe_api.get_asn_neighbours(asn)
            current_peers = self._extract_peer_info(neighbours_data)
            
            # Analisar tipos de relacionamento
            relationships = {}
            for peer in current_peers:
                rel_type = peer.get("relationship_type", "unknown")
                relationships[rel_type] = relationships.get(rel_type, 0) + 1
            
            # Verificar se tem upstreams suficientes
            upstream_count = relationships.get("upstream", 0)
            has_sufficient_upstreams = upstream_count >= self.min_upstreams
            
            return {
                "asn": asn,
                "timestamp": datetime.utcnow().isoformat(),
                "total_peers": len(current_peers),
                "peer_breakdown": relationships,
                "has_sufficient_upstreams": has_sufficient_upstreams,
                "min_upstreams_required": self.min_upstreams,
                "peers": current_peers[:10],  # Limitando a 10 para não sobrecarregar
                "status": "healthy" if has_sufficient_upstreams else "warning"
            }
            
        except Exception as e:
            logger.error(f"Error checking peers for ASN {asn}: {str(e)}")
            return {
                "asn": asn,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    def _extract_peer_info(self, neighbours_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai informações de peers dos dados da API"""
        peers = []
        
        # A API RIPE retorna os dados diretamente, não aninhados em "data"
        neighbours = neighbours_data.get("neighbours", [])
        
        for neighbour in neighbours:
            peer_asn = neighbour.get("asn")
            if peer_asn:
                # Determina tipo de relacionamento baseado em heurísticas simples
                relationship_type = self._determine_relationship(neighbour)
                
                peer_info = {
                    "asn": peer_asn,
                    "relationship_type": relationship_type,
                    "type": neighbour.get("type", "unknown"),  # left/right do RIPE
                    "power": neighbour.get("power", 0),
                    "v4_peers": neighbour.get("v4_peers", 0),
                    "v6_peers": neighbour.get("v6_peers", 0),
                    "last_seen": datetime.utcnow().isoformat()
                }
                peers.append(peer_info)
                
        return peers
    
    def _determine_relationship(self, neighbour: Dict[str, Any]) -> str:
        """Determina tipo de relacionamento BGP baseado nos dados do RIPE"""
        asn = neighbour.get("asn")
        ripe_type = neighbour.get("type", "")
        power = neighbour.get("power", 0)
        
        # No RIPE: "left" = providers/upstreams, "right" = customers
        if ripe_type == "left":
            # Heurística adicional: ASNs menores e com mais poder geralmente são upstreams
            if asn and (asn < 20000 or power > 200):
                return "upstream"
            else:
                return "peer"
        elif ripe_type == "right":
            return "customer"
        else:
            # Fallback para heurística original
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
    
    def _get_previous_latency(self, peer_asn: str) -> float:
        """Obtém a latência anterior de um peer (simulado)"""
        # Em um sistema real, isso viria de métricas históricas
        # Para simulação, retorna uma latência alta plausível
        import random
        return round(random.uniform(200, 800), 1)


# Instância global do monitor
peer_monitor = PeerMonitor()
