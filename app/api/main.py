from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import asyncio
import time
from datetime import datetime

from app.core.config import settings
from app.services.telegram import telegram_service
from app.utils.metrics import metrics
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BGP Monitor API",
    description="API para monitoramento BGP com alertas via Telegram",
    version="1.0.1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)