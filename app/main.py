#!/usr/bin/env python3
"""
BGP Monitor - Sistema simplificado de monitoramento BGP
"""
import asyncio
import signal
import sys
import logging

from app.api.main import app
from app.scheduler import bgp_scheduler
from app.core.config import settings

# Configurar logging simples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configurar lifespan events do FastAPI
@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    logger.info(f"Starting BGP Monitor v2.1.1 - Target ASN: {settings.target_asn}")
    
    # Inicializar banco de dados e scheduler
    await bgp_scheduler.initialize()
    bgp_scheduler.start()
    
    logger.info("BGP Monitor started with historical data collection enabled")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de finalização"""
    logger.info("Shutting down BGP Monitor")
    bgp_scheduler.stop()
    await bgp_scheduler.cleanup()


def signal_handler(signum, frame):
    """Handler para sinais do sistema"""
    logger.info(f"Received signal: {signum}")
    bgp_scheduler.stop()
    sys.exit(0)


def main():
    """Função principal"""
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar aplicação
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()


# Exporta a aplicação FastAPI para uso no gunicorn/uvicorn
__all__ = ["app"]
