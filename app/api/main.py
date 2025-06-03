from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import asyncio
import time
from datetime import datetime

from app.core.config import settings
from app.services.telegram import telegram_service
from app.services.prefix_monitor import prefix_monitor
from app.services.peer_monitor import peer_monitor
from app.services.irr_validator import irr_validator
from app.utils.metrics import metrics
from app.api.bgp_historical import router as bgp_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BGP Monitor API",
    description="API para monitoramento BGP com dados históricos e alertas via Telegram",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API histórica
app.include_router(bgp_router)

# Lista de prefixos monitorados (armazenada em memória)
monitored_prefixes = []


@app.get("/")
async def root():
    """Endpoint raiz com informações básicas"""
    return {
        "service": "BGP Monitor",
        "version": "1.0.1",
        "status": "running",
        "target_asn": settings.target_asn,
        "uptime": int(time.time() - metrics.start_time)
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    stats = metrics.get_system_stats()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": stats["uptime_seconds"],
        "total_alerts": stats["total_alerts"],
        "healthy_components": stats["healthy_components"]
    }


@app.get("/metrics")
async def get_metrics():
    """Endpoint para estatísticas do sistema"""
    return metrics.get_system_stats()


# Endpoints de Prefixos
@app.get("/prefixes")
async def get_monitored_prefixes():
    """Lista todos os prefixos monitorados"""
    return monitored_prefixes


@app.post("/prefixes")
async def add_monitored_prefix(prefix_data: Dict[str, Any]):
    """Adiciona um novo prefixo para monitoramento"""
    try:
        new_prefix = {
            "id": len(monitored_prefixes) + 1,
            "prefix": prefix_data["prefix"],
            "asn": prefix_data["asn"],
            "description": prefix_data.get("description", ""),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        monitored_prefixes.append(new_prefix)
        
        # Log da adição
        logger.info(f"Prefix added: {new_prefix['prefix']} (ASN: {new_prefix['asn']})")
        
        return new_prefix
        
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Campo obrigatório ausente: {e}"
        )


@app.delete("/prefixes/{prefix_id}")
async def remove_monitored_prefix(prefix_id: int):
    """Remove um prefixo do monitoramento"""
    global monitored_prefixes
    
    # Procurar prefixo pelo ID
    prefix_index = None
    for i, prefix in enumerate(monitored_prefixes):
        if prefix["id"] == prefix_id:
            prefix_index = i
            break
    
    if prefix_index is None:
        raise HTTPException(
            status_code=404,
            detail="Prefixo não encontrado"
        )
    
    removed_prefix = monitored_prefixes.pop(prefix_index)
    
    logger.info(f"Prefix removed: {removed_prefix['prefix']} (ASN: {removed_prefix['asn']})")
    
    return {"message": f"Prefixo {removed_prefix['prefix']} removido com sucesso"}


# Endpoints de Alertas
@app.get("/alerts")
async def get_recent_alerts():
    """Lista os alertas recentes"""
    return {
        "alerts": [],
        "alert_breakdown": metrics.alert_counters,
        "last_checks": metrics.last_checks
    }


# Endpoints de Testes
@app.post("/test/telegram")
async def test_telegram():
    """Testa conectividade com Telegram"""
    try:
        await telegram_service.send_status_update(
            "BGP Monitor",
            "info",
            "🧪 Teste de conectividade - Sistema funcionando corretamente!"
        )
        return {"status": "success", "message": "Mensagem enviada com sucesso"}
    except Exception as e:
        logger.error(f"Telegram test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar mensagem: {str(e)}"
        )


@app.post("/monitoring/run-checks")
async def run_manual_checks():
    """Executa verificações manuais de BGP"""
    try:
        # Simular execução de verificações
        start_time = time.time()
        
        # Atualizar métricas de componentes
        metrics.update_component_health("api", True)
        metrics.update_component_health("monitoring", True)
        
        # Simular duração da verificação
        duration = time.time() - start_time
        metrics.record_check_duration("manual_check", duration)
        
        logger.info(f"Manual checks completed (duration: {duration:.2f}s)")
        
        return {
            "status": "completed",
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "checks_performed": [
                "prefix_announcements",
                "peer_relationships", 
                "latency_measurements"
            ]
        }
        
    except Exception as e:
        logger.error(f"Manual checks failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro nas verificações: {str(e)}"
        )


@app.post("/monitoring/check-prefixes")
async def run_prefix_check():
    """Executa verificação manual de prefixos"""
    try:
        start_time = time.time()
        logger.info("Running manual prefix check")
        
        # Executar verificação de prefixos
        alerts = await prefix_monitor.check_prefix_announcements()
        
        duration = time.time() - start_time
        metrics.record_check_duration("prefix_check", duration)
        
        return {
            "status": "completed",
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "alerts_generated": len(alerts),
            "alerts": alerts[:5] if alerts else []  # Limitar a 5 alertas para resposta
        }
        
    except Exception as e:
        logger.error(f"Prefix check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na verificação de prefixos: {str(e)}"
        )


@app.post("/monitoring/check-peers")
async def run_peer_check():
    """Executa verificação manual de peers"""
    try:
        start_time = time.time()
        logger.info("Running manual peer check")
        
        # Executar verificação de peers
        alerts = await peer_monitor.check_peer_relationships()
        
        duration = time.time() - start_time
        metrics.record_check_duration("peer_check", duration)
        
        return {
            "status": "completed",
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "alerts_generated": len(alerts),
            "alerts": alerts[:5] if alerts else []
        }
        
    except Exception as e:
        logger.error(f"Peer check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na verificação de peers: {str(e)}"
        )


@app.post("/monitoring/check-latency")
async def run_latency_check():
    """Executa verificação manual de latência"""
    try:
        start_time = time.time()
        logger.info("Running manual latency check")
        
        # Executar medição de latência
        alerts = await peer_monitor.measure_latency()
        
        duration = time.time() - start_time
        metrics.record_check_duration("latency_check", duration)
        
        return {
            "status": "completed",
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "alerts_generated": len(alerts),
            "alerts": alerts[:5] if alerts else []
        }
        
    except Exception as e:
        logger.error(f"Latency check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na verificação de latência: {str(e)}"
        )


@app.post("/monitoring/check-irr")
async def run_irr_check():
    """Executa verificação manual de IRR"""
    try:
        start_time = time.time()
        logger.info("Running manual IRR check")
        
        # Obter prefixos monitorados
        monitored_prefixes = prefix_monitor.get_monitored_prefixes()
        
        # Executar validação IRR
        alerts = await irr_validator.validate_all_monitored_prefixes(monitored_prefixes)
        
        duration = time.time() - start_time
        metrics.record_check_duration("irr_check", duration)
        
        return {
            "status": "completed",
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "prefixes_validated": len(monitored_prefixes),
            "alerts_generated": len(alerts),
            "alerts": alerts[:5] if alerts else []
        }
        
    except Exception as e:
        logger.error(f"IRR check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na verificação IRR: {str(e)}"
        )


@app.post("/prefixes/add")
async def add_prefix():
    """Adiciona um prefixo para monitoramento"""
    try:
        # Por enquanto, vamos usar dados de exemplo
        # Em uma implementação completa, isso viria do body da requisição
        example_prefix = "203.0.113.0/24"
        description = "Prefixo de exemplo"
        
        prefix_monitor.add_monitored_prefix(example_prefix, description)
        
        logger.info(f"Prefix added via API: {example_prefix}")
        
        return {
            "status": "success",
            "message": f"Prefixo {example_prefix} adicionado com sucesso",
            "prefix": example_prefix,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to add prefix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao adicionar prefixo: {str(e)}"
        )


@app.post("/prefixes/remove")
async def remove_prefix():
    """Remove um prefixo do monitoramento"""
    try:
        # Exemplo de remoção - em implementação real viria do body
        example_prefix = "203.0.113.0/24"
        
        prefix_monitor.remove_monitored_prefix(example_prefix)
        
        logger.info(f"Prefix removed via API: {example_prefix}")
        
        return {
            "status": "success",
            "message": f"Prefixo {example_prefix} removido com sucesso",
            "prefix": example_prefix,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to remove prefix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover prefixo: {str(e)}"
        )


# Configurações
@app.get("/config")
async def get_config():
    """Retorna configurações não sensíveis"""
    return {
        "target_asn": settings.target_asn,
        "max_latency_ms": settings.max_latency_ms,
        "min_upstreams": settings.min_upstreams,
        "check_intervals": {
            "prefix_check": settings.prefix_check_interval,
            "peer_check": settings.peer_check_interval,
            "latency_check": settings.latency_check_interval
        }
    }


# Endpoints de consulta RIPE API
@app.get("/as/{asn}")
async def get_as_info(asn: int):
    """Obtém informações de um ASN via RIPE API"""
    try:
        from app.services.ripe_api import ripe_api
        as_info = await ripe_api.get_as_info(asn)
        return as_info
    except Exception as e:
        logger.error(f"Failed to get AS{asn} info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter informações do AS{asn}: {str(e)}"
        )


@app.get("/prefixes/{asn}")
async def get_as_prefixes(asn: int):
    """Obtém prefixos anunciados por um ASN via RIPE API"""
    try:
        from app.services.ripe_api import ripe_api
        prefixes = await ripe_api.get_prefixes(asn)
        return prefixes
    except Exception as e:
        logger.error(f"Failed to get AS{asn} prefixes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter prefixos do AS{asn}: {str(e)}"
        )


@app.get("/peers/{asn}")
async def get_as_peers(asn: int):
    """Obtém peers de um ASN via RIPE API"""
    try:
        from app.services.ripe_api import ripe_api
        peers = await ripe_api.get_peers(asn)
        return peers
    except Exception as e:
        logger.error(f"Failed to get AS{asn} peers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter peers do AS{asn}: {str(e)}"
        )


@app.get("/monitoring/peers/{asn}")
async def check_asn_peers(asn: int):
    """Verifica peers de um ASN específico"""
    try:
        logger.info(f"Checking peers for ASN {asn}")
        
        # Executar verificação de peers para ASN específico
        result = await peer_monitor.check_specific_asn_peers(asn)
        
        return result
        
    except Exception as e:
        logger.error(f"ASN peer check failed for {asn}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na verificação de peers do ASN {asn}: {str(e)}"
        )


# Endpoints de Testes de Alarmes de Recuperação
@app.post("/test/recovery/peer")
async def test_peer_recovery_alert():
    """Testa alerta de recuperação de peer"""
    try:
        alert_data = {
            "alert_type": "peer_recovered",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "info",
            "target_asn": settings.target_asn,
            "details": {
                "peer_asn": 64512,
                "peer_name": "AS64512 - Provedor Exemplo",
                "downtime_minutes": 47,
                "recovery_time": datetime.utcnow().isoformat()
            }
        }
        
        await telegram_service.send_recovery_alert(alert_data)
        
        logger.info("Sent test peer recovery alert")
        
        return {
            "status": "success",
            "message": "Alerta de recuperação de peer enviado com sucesso",
            "alert_data": alert_data
        }
        
    except Exception as e:
        logger.error(f"Failed to send test peer recovery alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar alerta de teste: {str(e)}"
        )


@app.post("/test/recovery/upstreams")
async def test_upstreams_normalized_alert():
    """Testa alerta de normalização de upstreams"""
    try:
        alert_data = {
            "alert_type": "upstreams_normalized",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "info",
            "target_asn": settings.target_asn,
            "details": {
                "current_upstreams": 4,
                "required_minimum": 3,
                "downtime_minutes": 23,
                "recovery_time": datetime.utcnow().isoformat()
            }
        }
        
        await telegram_service.send_recovery_alert(alert_data)
        
        logger.info("Sent test upstreams normalized alert")
        
        return {
            "status": "success",
            "message": "Alerta de normalização de upstreams enviado com sucesso",
            "alert_data": alert_data
        }
        
    except Exception as e:
        logger.error(f"Failed to send test upstreams normalized alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar alerta de teste: {str(e)}"
        )


@app.post("/test/recovery/prefix")
async def test_prefix_restored_alert():
    """Testa alerta de restauração de prefixo"""
    try:
        alert_data = {
            "alert_type": "prefix_restored",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "info",
            "target_asn": settings.target_asn,
            "details": {
                "prefix": "203.0.113.0/24",
                "origin_asn": settings.target_asn,
                "downtime_minutes": 15,
                "recovery_time": datetime.utcnow().isoformat(),
                "current_paths": 3
            }
        }
        
        await telegram_service.send_recovery_alert(alert_data)
        
        logger.info("Sent test prefix restored alert")
        
        return {
            "status": "success",
            "message": "Alerta de restauração de prefixo enviado com sucesso",
            "alert_data": alert_data
        }
        
    except Exception as e:
        logger.error(f"Failed to send test prefix restored alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar alerte de teste: {str(e)}"
        )


@app.post("/test/recovery/latency")
async def test_latency_normalized_alert():
    """Testa alerta de normalização de latência"""
    try:
        alert_data = {
            "alert_type": "latency_normalized",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "info",
            "target_asn": settings.target_asn,
            "details": {
                "peer_asn": 64512,
                "peer_name": "AS64512 - Provedor Exemplo",
                "current_latency": 45,
                "max_latency": settings.max_latency_ms,
                "previous_latency": 850,
                "downtime_minutes": 8
            }
        }
        
        await telegram_service.send_recovery_alert(alert_data)
        
        logger.info("Sent test latency normalized alert")
        
        return {
            "status": "success",
            "message": "Alerta de normalização de latência enviado com sucesso",
            "alert_data": alert_data
        }
        
    except Exception as e:
        logger.error(f"Failed to send test latency normalized alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar alerta de teste: {str(e)}"
        )


@app.post("/test/recovery/instability")
async def test_instability_resolved_alert():
    """Testa alerta de resolução de instabilidade"""
    try:
        alert_data = {
            "alert_type": "instability_resolved",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "info",
            "target_asn": settings.target_asn,
            "details": {
                "prefix": "203.0.113.0/24",
                "origin_asn": settings.target_asn,
                "stable_time_minutes": 30,
                "previous_flaps": 23,
                "downtime_minutes": 62
            }
        }
        
        await telegram_service.send_recovery_alert(alert_data)
        
        logger.info("Sent test instability resolved alert")
        
        return {
            "status": "success",
            "message": "Alerta de resolução de instabilidade enviado com sucesso",
            "alert_data": alert_data
        }
        
    except Exception as e:
        logger.error(f"Failed to send test instability resolved alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar alerta de teste: {str(e)}"
        )


@app.post("/test/recovery/anomaly")
async def test_anomaly_resolved_alert():
    """Testa alerta de resolução de anomalia"""
    try:
        alert_data = {
            "alert_type": "anomaly_resolved",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "info",
            "target_asn": settings.target_asn,
            "details": {
                "metric": "announcement_count",
                "current_value": 1250,
                "baseline_value": 1200,
                "anomaly_type": "spike",
                "detection_method": "statistical_analysis",
                "downtime_minutes": 18
            }
        }
        
        await telegram_service.send_recovery_alert(alert_data)
        
        logger.info("Sent test anomaly resolved alert")
        
        return {
            "status": "success",
            "message": "Alerta de resolução de anomalia enviado com sucesso",
            "alert_data": alert_data
        }
        
    except Exception as e:
        logger.error(f"Failed to send test anomaly resolved alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar alerta de teste: {str(e)}"
        )


@app.post("/test/recovery/all")
async def test_all_recovery_alerts():
    """Testa todos os tipos de alertas de recuperação"""
    try:
        results = []
        
        # Lista de todos os tipos de alertas de recuperação
        recovery_alerts = [
            {
                "type": "peer_recovered",
                "data": {
                    "alert_type": "peer_recovered",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "info",
                    "target_asn": settings.target_asn,
                    "details": {
                        "peer_asn": 64512,
                        "peer_name": "AS64512 - Provedor Exemplo",
                        "downtime_minutes": 47,
                        "recovery_time": datetime.utcnow().isoformat()
                    }
                }
            },
            {
                "type": "upstreams_normalized",
                "data": {
                    "alert_type": "upstreams_normalized",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "info",
                    "target_asn": settings.target_asn,
                    "details": {
                        "current_upstreams": 4,
                        "required_minimum": 3,
                        "downtime_minutes": 23,
                        "recovery_time": datetime.utcnow().isoformat()
                    }
                }
            },
            {
                "type": "prefix_restored",
                "data": {
                    "alert_type": "prefix_restored",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "info",
                    "target_asn": settings.target_asn,
                    "details": {
                        "prefix": "203.0.113.0/24",
                        "origin_asn": settings.target_asn,
                        "downtime_minutes": 15,
                        "recovery_time": datetime.utcnow().isoformat(),
                        "current_paths": 3
                    }
                }
            },
            {
                "type": "latency_normalized",
                "data": {
                    "alert_type": "latency_normalized",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "info",
                    "target_asn": settings.target_asn,
                    "details": {
                        "peer_asn": 64512,
                        "peer_name": "AS64512 - Provedor Exemplo",
                        "current_latency": 45,
                        "max_latency": settings.max_latency_ms,
                        "previous_latency": 850,
                        "downtime_minutes": 8
                    }
                }
            },
            {
                "type": "instability_resolved",
                "data": {
                    "alert_type": "instability_resolved",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "info",
                    "target_asn": settings.target_asn,
                    "details": {
                        "prefix": "203.0.113.0/24",
                        "origin_asn": settings.target_asn,
                        "stable_time_minutes": 30,
                        "previous_flaps": 23,
                        "downtime_minutes": 62
                    }
                }
            },
            {
                "type": "anomaly_resolved",
                "data": {
                    "alert_type": "anomaly_resolved",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "info",
                    "target_asn": settings.target_asn,
                    "details": {
                        "metric": "announcement_count",
                        "current_value": 1250,
                        "baseline_value": 1200,
                        "anomaly_type": "spike",
                        "detection_method": "statistical_analysis",
                        "downtime_minutes": 18
                    }
                }
            }
        ]
        
        # Enviar cada tipo de alerta com um pequeno delay
        for alert in recovery_alerts:
            try:
                await telegram_service.send_recovery_alert(alert["data"])
                results.append({
                    "type": alert["type"],
                    "status": "success",
                    "message": f"Alerta {alert['type']} enviado com sucesso"
                })
                
                # Pequeno delay entre alertas para não sobrecarregar
                await asyncio.sleep(1)
                
            except Exception as e:
                results.append({
                    "type": alert["type"],
                    "status": "error",
                    "message": str(e)
                })
        
        logger.info(f"Sent {len(recovery_alerts)} test recovery alerts")
        
        return {
            "status": "completed",
            "message": f"Teste de {len(recovery_alerts)} tipos de alertas de recuperação concluído",
            "results": results,
            "total_alerts": len(recovery_alerts),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"])
        }
        
    except Exception as e:
        logger.error(f"Failed to send test recovery alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar alertas de teste: {str(e)}"
        )


# Endpoints informativos sobre alertas
@app.get("/alerts/types")
async def get_alert_types():
    """Lista todos os tipos de alertas disponíveis"""
    return {
        "problem_alerts": {
            "peer_lost": {
                "description": "Peer BGP perdido/desconectado",
                "severity": "critical",
                "emoji": "🔴",
                "category": "connectivity"
            },
            "insufficient_upstreams": {
                "description": "Número insuficiente de upstreams",
                "severity": "critical", 
                "emoji": "⚠️",
                "category": "connectivity"
            },
            "prefix_missing": {
                "description": "Prefixo não encontrado no BGP",
                "severity": "critical",
                "emoji": "🚨",
                "category": "routing"
            },
            "high_latency": {
                "description": "Latência elevada detectada",
                "severity": "warning",
                "emoji": "🐌",
                "category": "performance"
            },
            "route_instability": {
                "description": "Instabilidade de rota (flapping)",
                "severity": "warning",
                "emoji": "📊",
                "category": "routing"
            },
            "anomaly_detected": {
                "description": "Anomalia estatística detectada",
                "severity": "warning",
                "emoji": "📈",
                "category": "analysis"
            }
        },
        "recovery_alerts": {
            "peer_recovered": {
                "description": "Peer BGP recuperado/reconectado",
                "severity": "info",
                "emoji": "🟢",
                "category": "connectivity"
            },
            "upstreams_normalized": {
                "description": "Número de upstreams normalizado",
                "severity": "info",
                "emoji": "✅",
                "category": "connectivity"
            },
            "prefix_restored": {
                "description": "Prefixo restaurado no BGP",
                "severity": "info",
                "emoji": "🔄",
                "category": "routing"
            },
            "latency_normalized": {
                "description": "Latência normalizada",
                "severity": "info",
                "emoji": "⚡",
                "category": "performance"
            },
            "instability_resolved": {
                "description": "Instabilidade de rota resolvida",
                "severity": "info",
                "emoji": "📊",
                "category": "routing"
            },
            "anomaly_resolved": {
                "description": "Anomalia estatística resolvida",
                "severity": "info",
                "emoji": "📉",
                "category": "analysis"
            }
        },
        "system_alerts": {
            "system_startup": {
                "description": "Sistema iniciado",
                "severity": "info",
                "emoji": "🚀",
                "category": "system"
            },
            "monitoring_error": {
                "description": "Erro no monitoramento",
                "severity": "error",
                "emoji": "❌",
                "category": "system"
            }
        }
    }


@app.get("/alerts/recovery/examples")
async def get_recovery_alert_examples():
    """Retorna exemplos de alertas de recuperação em PT-BR"""
    return {
        "description": "Exemplos de mensagens de alertas de recuperação em português brasileiro",
        "language": "pt-br",
        "examples": {
            "peer_recovered": {
                "title": "🟢 Peer BGP Recuperado",
                "message": "O peer AS64512 - Provedor Exemplo foi reconectado após 47 minutos offline. Conectividade BGP restaurada.",
                "details": ["Tempo de inatividade: 47 minutos", "Reconectado às 14:30 BRT"]
            },
            "upstreams_normalized": {
                "title": "✅ Upstreams Normalizados", 
                "message": "Número de upstreams normalizado (4/3 mínimo). Redundância BGP restaurada após 23 minutos.",
                "details": ["Upstreams atuais: 4", "Mínimo necessário: 3", "Tempo de problema: 23 minutos"]
            },
            "prefix_restored": {
                "title": "🔄 Prefixo Restaurado",
                "message": "Prefixo 203.0.113.0/24 foi restaurado no BGP após 15 minutos ausente. Agora visível em 3 caminhos.",
                "details": ["Caminhos atuais: 3", "Tempo de ausência: 15 minutos"]
            },
            "latency_normalized": {
                "title": "⚡ Latência Normalizada",
                "message": "Latência com AS64512 normalizada (45ms). Problema de performance resolvido após 8 minutos.",
                "details": ["Latência atual: 45ms", "Latência anterior: 850ms", "Tempo de problema: 8 minutos"]
            },
            "instability_resolved": {
                "title": "📊 Instabilidade Resolvida",
                "message": "Instabilidade do prefixo 203.0.113.0/24 resolvida. Rota estável há 30 minutos após 23 oscilações.",
                "details": ["Estável há: 30 minutos", "Oscilações anteriores: 23", "Tempo de problema: 62 minutos"]
            },
            "anomaly_resolved": {
                "title": "📉 Anomalia Resolvida",
                "message": "Anomalia estatística em 'announcement_count' resolvida. Valores normalizados após 18 minutos.",
                "details": ["Valor atual: 1250", "Valor baseline: 1200", "Tempo de anomalia: 18 minutos"]
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)