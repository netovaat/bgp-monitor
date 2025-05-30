"""
BGP Scheduler Service - Gerenciamento de tarefas agendadas para coleta BGP
"""
import sys
import os

# Importar do módulo principal do scheduler na pasta app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from app.scheduler import BGPScheduler
    # Criar instância global do scheduler  
    bgp_scheduler = BGPScheduler()
except ImportError:
    # Fallback: importar do scheduler no diretório raiz app
    from scheduler import BGPScheduler
    bgp_scheduler = BGPScheduler()

# Export the same interface
__all__ = ['BGPScheduler', 'bgp_scheduler']
