"""
BGP Monitor v2.1.1 - Sistema de Monitoramento BGP com PostgreSQL

Este módulo contém a aplicação principal do BGP Monitor v2.1.1,
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

Changelog v2.1.1:
- Correção de problemas de imports entre módulos
- Melhoria na documentação de instalação (INSTALLATION.md completo)
- Scripts de instalação automatizada aprimorados
- Testes de sistema completos implementados
- Ambiente virtual otimizado e validado
- Correção de dependências e migrations
- Sistema de validação de imports funcionando
- Serviço systemd configurado e testado
- Pacote final otimizado para distribuição
"""

__version__ = "2.1.1"
__author__ = "BGP Monitor Team"
__description__ = "Sistema de Monitoramento BGP com PostgreSQL"