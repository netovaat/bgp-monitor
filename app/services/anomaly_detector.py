"""
Advanced BGP Anomaly Detection Service
Detecta alterações bruscas e anomalias nos dados BGP usando análise estatística
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func, desc, and_, or_
import statistics
import logging

from app.models.database import ASNSnapshot, BGPAlert
from app.database.connection import db_manager
from app.services.bgp_data_service import bgp_data_service
from app.services.telegram import telegram_service

logger = logging.getLogger(__name__)


class BGPAnomalyDetector:
    """Detector de anomalias avançado para dados BGP"""
    
    def __init__(self):
        self.alert_cooldown = {}  # Cache para evitar spam de alertas
    
    async def detect_sudden_changes(self, asn: int, sensitivity: str = "medium") -> List[Dict[str, Any]]:
        """
        Detecta mudanças bruscas nos prefixos usando análise estatística
        
        Args:
            asn: Número do ASN a analisar
            sensitivity: "low", "medium", "high" - sensibilidade da detecção
        """
        # Configurações de sensibilidade
        sensitivity_config = {
            "low": {"std_multiplier": 3.0, "min_change_percent": 20},
            "medium": {"std_multiplier": 2.5, "min_change_percent": 15},
            "high": {"std_multiplier": 2.0, "min_change_percent": 10}
        }
        
        config = sensitivity_config.get(sensitivity, sensitivity_config["medium"])
        
        # Buscar dados históricos (últimas 48 horas)
        cutoff_time = datetime.now() - timedelta(hours=48)
        
        from app.database.connection import db_manager
        async with db_manager.get_session() as session:
            query = select(ASNSnapshot).where(
                and_(
                    ASNSnapshot.asn == asn,
                    ASNSnapshot.timestamp >= cutoff_time
                )
            ).order_by(desc(ASNSnapshot.timestamp))
            
            result = await session.execute(query)
            snapshots = result.scalars().all()
            
            if len(snapshots) < 10:  # Precisa de dados suficientes
                return []
            
            anomalies = []
            prefix_counts = [s.prefix_count for s in snapshots]
            
            # Calcular baseline estatístico
            baseline_mean = statistics.mean(prefix_counts[10:])  # Excluir os 10 mais recentes
            baseline_std = statistics.stdev(prefix_counts[10:]) if len(prefix_counts[10:]) > 1 else 0
            
            # Analisar os snapshots mais recentes
            for i, snapshot in enumerate(snapshots[:10]):
                current_count = snapshot.prefix_count
                
                # Calcular desvio do baseline
                if baseline_std > 0:
                    z_score = abs(current_count - baseline_mean) / baseline_std
                else:
                    z_score = 0
                
                # Calcular mudança percentual em relação à média
                percent_change = abs(current_count - baseline_mean) / baseline_mean * 100 if baseline_mean > 0 else 0
                
                # Detectar anomalia
                is_anomaly = (
                    z_score > config["std_multiplier"] and 
                    percent_change > config["min_change_percent"]
                )
                
                if is_anomaly:
                    anomaly_type = "sudden_increase" if current_count > baseline_mean else "sudden_decrease"
                    
                    anomaly = {
                        "timestamp": snapshot.timestamp.isoformat(),
                        "asn": asn,
                        "type": anomaly_type,
                        "severity": self._calculate_severity(z_score, percent_change),
                        "current_prefixes": current_count,
                        "baseline_mean": round(baseline_mean, 2),
                        "z_score": round(z_score, 2),
                        "percent_change": round(percent_change, 2),
                        "description": f"Detected {anomaly_type} in AS{asn}: {current_count} prefixes ({percent_change:.1f}% change)"
                    }
                    
                    anomalies.append(anomaly)
            
            return anomalies
    
    async def detect_routing_instability(self, asn: int, window_hours: int = 6) -> Dict[str, Any]:
        """
        Detecta instabilidade de roteamento baseada na frequência de mudanças
        """
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        async with db_manager.get_session() as session:
            query = select(ASNSnapshot).where(
                and_(
                    ASNSnapshot.asn == asn,
                    ASNSnapshot.timestamp >= cutoff_time
                )
            ).order_by(ASNSnapshot.timestamp)
            
            result = await session.execute(query)
            snapshots = result.scalars().all()
            
            if len(snapshots) < 3:
                return {"instability_score": 0, "status": "insufficient_data"}
            
            # Contar mudanças consecutivas
            changes = 0
            total_change_magnitude = 0
            
            for i in range(1, len(snapshots)):
                current = snapshots[i]
                previous = snapshots[i-1]
                
                current_prefixes = set(current.announced_prefixes)
                previous_prefixes = set(previous.announced_prefixes)
                
                if current_prefixes != previous_prefixes:
                    changes += 1
                    # Calcular magnitude da mudança
                    added = len(current_prefixes - previous_prefixes)
                    removed = len(previous_prefixes - current_prefixes)
                    total_change_magnitude += added + removed
            
            # Calcular score de instabilidade
            change_frequency = changes / len(snapshots) * 100  # Porcentagem de snapshots com mudanças
            avg_change_magnitude = total_change_magnitude / changes if changes > 0 else 0
            
            # Score combinado (0-100, onde 100 é muito instável)
            instability_score = min(100, change_frequency * 2 + (avg_change_magnitude / 10))
            
            status = "stable"
            if instability_score > 70:
                status = "highly_unstable"
            elif instability_score > 40:
                status = "unstable"
            elif instability_score > 20:
                status = "moderately_stable"
            
            return {
                "asn": asn,
                "window_hours": window_hours,
                "instability_score": round(instability_score, 2),
                "status": status,
                "total_changes": changes,
                "change_frequency_percent": round(change_frequency, 2),
                "avg_change_magnitude": round(avg_change_magnitude, 2),
                "recommendation": self._get_instability_recommendation(status)
            }
    
    async def monitor_multiple_asns(self, asn_list: List[int]) -> Dict[str, Any]:
        """
        Monitora múltiplos ASNs e gera relatório consolidado de anomalias
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "asns_monitored": len(asn_list),
            "anomalies": [],
            "instability_reports": [],
            "summary": {
                "total_anomalies": 0,
                "high_severity_count": 0,
                "unstable_asns": 0
            }
        }
        
        # Processar ASNs em batches para não sobrecarregar
        for asn in asn_list:
            try:
                # Detectar anomalias
                anomalies = await self.detect_sudden_changes(asn, "medium")
                if anomalies:
                    results["anomalies"].extend(anomalies)
                    results["summary"]["total_anomalies"] += len(anomalies)
                    
                    # Contar severidade alta
                    high_severity = sum(1 for a in anomalies if a.get("severity") in ["high", "critical"])
                    results["summary"]["high_severity_count"] += high_severity
                
                # Verificar instabilidade
                instability = await self.detect_routing_instability(asn, 6)
                if instability.get("status") in ["unstable", "highly_unstable"]:
                    results["instability_reports"].append(instability)
                    if instability.get("status") == "highly_unstable":
                        results["summary"]["unstable_asns"] += 1
                
                # Delay pequeno entre processamentos
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error monitoring ASN {asn}: {e}")
        
        # Gerar alertas se necessário
        await self._generate_alerts_for_anomalies(results["anomalies"])
        
        return results
    
    async def _generate_alerts_for_anomalies(self, anomalies: List[Dict[str, Any]]):
        """Gera alertas para anomalias detectadas"""
        for anomaly in anomalies:
            if anomaly.get("severity") in ["high", "critical"]:
                await self._send_anomaly_alert(anomaly)
    
    async def _send_anomaly_alert(self, anomaly: Dict[str, Any]):
        """Envia alerta de anomalia via Telegram"""
        asn = anomaly["asn"]
        alert_key = f"anomaly_{asn}_{anomaly['type']}"
        
        # Rate limiting de alertas (não enviar o mesmo alerta por 1 hora)
        current_time = datetime.now()
        if alert_key in self.alert_cooldown:
            time_diff = (current_time - self.alert_cooldown[alert_key]).total_seconds()
            if time_diff < 3600:  # 1 hora
                return
        
        # Criar alerta no banco de dados
        async with db_manager.get_session() as session:
            alert = BGPAlert(
                asn=asn,
                alert_type=anomaly["type"],
                message=anomaly["description"],
                severity=anomaly["severity"],
                new_value={
                    "current_prefixes": anomaly["current_prefixes"],
                    "z_score": anomaly["z_score"],
                    "percent_change": anomaly["percent_change"]
                }
            )
            session.add(alert)
            await session.commit()
        
        # Enviar via Telegram
        emoji = "🚨" if anomaly["severity"] == "critical" else "⚠️"
        message = (
            f"{emoji} **BGP Anomaly Detected**\n\n"
            f"**ASN:** {asn}\n"
            f"**Type:** {anomaly['type'].replace('_', ' ').title()}\n"
            f"**Severity:** {anomaly['severity'].upper()}\n"
            f"**Current Prefixes:** {anomaly['current_prefixes']}\n"
            f"**Change:** {anomaly['percent_change']:.1f}%\n"
            f"**Z-Score:** {anomaly['z_score']:.2f}\n"
            f"**Time:** {anomaly['timestamp']}\n\n"
            f"🔍 This indicates a significant deviation from normal routing patterns."
        )
        
        await telegram_service.send_message(message)
        
        # Atualizar cache de cooldown
        self.alert_cooldown[alert_key] = current_time
    
    def _calculate_severity(self, z_score: float, percent_change: float) -> str:
        """Calcula a severidade baseada no z-score e mudança percentual"""
        if z_score > 4.0 or percent_change > 50:
            return "critical"
        elif z_score > 3.0 or percent_change > 30:
            return "high"
        elif z_score > 2.5 or percent_change > 20:
            return "medium"
        else:
            return "low"
    
    def _get_instability_recommendation(self, status: str) -> str:
        """Retorna recomendações baseadas no status de instabilidade"""
        recommendations = {
            "stable": "No action required. Routing appears stable.",
            "moderately_stable": "Monitor closely for patterns. Consider investigating if trend continues.",
            "unstable": "Investigate routing configuration. Check for BGP flapping or network issues.",
            "highly_unstable": "URGENT: Significant routing instability detected. Immediate investigation required."
        }
        return recommendations.get(status, "Unknown status")


# Instância global do detector
anomaly_detector = BGPAnomalyDetector()
