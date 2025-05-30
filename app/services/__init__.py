"""
BGP Monitor v2.0 - Services Module

Módulo de serviços do BGP Monitor v2.0 contendo:
- Coleta de dados BGP via RIPE API
- Detecção de anomalias com machine learning
- Monitoramento de prefixos e peers
- Validação IRR
- Notificações via Telegram
- Rate limiting inteligente

Todos os serviços são assíncronos e otimizados para
monitoramento de até 50 ASNs simultaneamente.
"""

__version__ = "2.0.0"