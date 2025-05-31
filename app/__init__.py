"""
BGP Monitor v1.0.0 - Sistema de Monitoramento BGP com PostgreSQL

Este módulo contém a aplicação principal do BGP Monitor v1.0.0,
incluindo APIs, serviços de coleta, detecção de anomalias e 
notificações via Telegram.

Arquitetura:
- FastAPI para APIs REST
- PostgreSQL para persistência
- Async/await para performance
- Scheduler para coletas automáticas
- Sistema de alertas inteligente

Desenvolvido para monitoramento de até 50 ASNs simultaneamente
com detecção de anomalias em tempo real.

Release Inicial v1.0.0:
- Sistema completo de monitoramento BGP multi-ASN
- Detecção de anomalias estatísticas com Z-score
- Armazenamento histórico em PostgreSQL
- Alertas via Telegram em português
- Rate limiting inteligente para API RIPE
- Scheduler automático a cada 15 minutos
- API REST completa com FastAPI
- Script de instalação automatizado
- Documentação completa e exemplos práticos
"""

__version__ = "1.0.0"
__author__ = "netovaat"
__description__ = "Sistema de Monitoramento BGP com PostgreSQL"