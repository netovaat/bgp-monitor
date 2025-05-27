#!/usr/bin/env python3
"""
BGP Monitor - Sistema simplificado de monitoramento BGP
"""
import asyncio
import signal
import sys

from app.api.main import app
from app.scheduler import bgp_scheduler
from app.core.config import settings
import structlog

logger = structlog.get_logger()


# Configurar lifespan events do FastAPI
@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    logger.info("Starting BGP Monitor", version="1.0.0", target_asn=settings.target_asn)
    bgp_scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de finalização"""
    logger.info("Shutting down BGP Monitor")
    bgp_scheduler.stop()


def signal_handler(signum, frame):
    """Handler para sinais do sistema"""
    logger.info("Received signal", signal=signum)
    bgp_scheduler.stop()
    sys.exit(0)


def main():
    """Função principal"""
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar aplicação
    import uvicorn
    
    logger.info("Starting server", host=settings.host, port=settings.port)
    
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
