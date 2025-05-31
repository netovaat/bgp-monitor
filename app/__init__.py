"""
BGP Monitor v2.2.0 - Sistema de Monitoramento BGP com PostgreSQL

Este módulo contém a aplicação principal do BGP Monitor v2.2.0,
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

Changelog v2.2.0:
- Script de instalação unificado e otimizado
- Documentação completamente revisada e atualizada
- Remoção de scripts obsoletos e redundantes
- Configurações padronizadas e validadas
- Sistema de empacotamento aprimorado
- Suporte completo a flags de configuração
- Melhorias na estrutura de arquivos
- Processo de instalação simplificado
"""

__version__ = "2.2.0"
__author__ = "netovaat"
__description__ = "Sistema de Monitoramento BGP com PostgreSQL"