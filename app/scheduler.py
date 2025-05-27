import asyncio
import schedule
import time
import threading
from datetime import datetime
from typing import Dict, Any

from app.core.config import settings
from app.services.telegram import telegram_service
from app.services.prefix_monitor import prefix_monitor
from app.services.peer_monitor import peer_monitor
from app.services.irr_validator import irr_validator
from app.utils.metrics import metrics
import structlog

logger = structlog.get_logger()


class BGPScheduler:
    """Scheduler simples para tarefas de monitoramento BGP"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.loop = None
        
    def start(self):
        """Inicia o scheduler"""
        if self.running:
            return
            
        self.running = True
        
        # Configurar agendamento
        schedule.every(settings.prefix_check_interval).seconds.do(self._run_prefix_check)
        schedule.every(settings.peer_check_interval).seconds.do(self._run_peer_check)
        schedule.every(settings.latency_check_interval).seconds.do(self._run_latency_check)
        schedule.every(settings.irr_check_interval).seconds.do(self._run_irr_check)
        schedule.every().hour.do(self._run_health_check)
        schedule.every().day.at("08:00").do(self._send_daily_report)
        
        # Iniciar thread do scheduler
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        
        logger.info("BGP Scheduler started")
    
    def stop(self):
        """Para o scheduler"""
        self.running = False
        schedule.clear()
        logger.info("BGP Scheduler stopped")
    
    def _scheduler_loop(self):
        """Loop principal do scheduler"""
        # Criar event loop para tarefas assíncronas
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
            
        self.loop.close()
    
    def _run_prefix_check(self):
        """Executa verificação de prefixos"""
        try:
            start_time = time.time()
            logger.info("Running prefix announcements check")
            
            # Executa verificação assíncrona
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_prefix_check(), self.loop
                ).result(timeout=300)  # 5 minutos timeout
            
            duration = time.time() - start_time
            metrics.record_check_duration("prefix_announcements", duration)
            
        except Exception as e:
            logger.error("Prefix check failed", error=str(e))
            metrics.update_component_health("prefix_monitor", False)
    
    async def _async_prefix_check(self):
        """Verificação assíncrona de prefixos"""
        try:
            alerts = await prefix_monitor.check_prefix_announcements()
            if alerts:
                logger.info("Prefix alerts generated", count=len(alerts))
            metrics.update_component_health("prefix_monitor", True)
        except Exception as e:
            logger.error("Async prefix check failed", error=str(e))
            metrics.update_component_health("prefix_monitor", False)
    
    def _run_peer_check(self):
        """Executa verificação de peers"""
        try:
            start_time = time.time()
            logger.info("Running peer relationships check")
            
            # Executa verificação assíncrona
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_peer_check(), self.loop
                ).result(timeout=300)
            
            duration = time.time() - start_time
            metrics.record_check_duration("peer_relationships", duration)
            
        except Exception as e:
            logger.error("Peer check failed", error=str(e))
            metrics.update_component_health("peer_monitor", False)
    
    async def _async_peer_check(self):
        """Verificação assíncrona de peers"""
        try:
            alerts = await peer_monitor.check_peer_relationships()
            if alerts:
                logger.info("Peer alerts generated", count=len(alerts))
            metrics.update_component_health("peer_monitor", True)
        except Exception as e:
            logger.error("Async peer check failed", error=str(e))
            metrics.update_component_health("peer_monitor", False)
    
    def _run_latency_check(self):
        """Executa verificação de latência"""
        try:
            start_time = time.time()
            logger.info("Running latency measurements")
            
            # Executa verificação assíncrona
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_latency_check(), self.loop
                ).result(timeout=180)
            
            duration = time.time() - start_time
            metrics.record_check_duration("latency_measurements", duration)
            
        except Exception as e:
            logger.error("Latency check failed", error=str(e))
    
    async def _async_latency_check(self):
        """Verificação assíncrona de latência"""
        try:
            alerts = await peer_monitor.measure_latency()
            if alerts:
                logger.info("Latency alerts generated", count=len(alerts))
        except Exception as e:
            logger.error("Async latency check failed", error=str(e))
    
    def _run_irr_check(self):
        """Executa verificação IRR"""
        try:
            start_time = time.time()
            logger.info("Running IRR validation check")
            
            # Executa verificação assíncrona
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_irr_check(), self.loop
                ).result(timeout=600)  # 10 minutos timeout
            
            duration = time.time() - start_time
            metrics.record_check_duration("irr_validation", duration)
            
        except Exception as e:
            logger.error("IRR check failed", error=str(e))
    
    async def _async_irr_check(self):
        """Verificação assíncrona de IRR"""
        try:
            monitored_prefixes = prefix_monitor.get_monitored_prefixes()
            alerts = await irr_validator.validate_all_monitored_prefixes(monitored_prefixes)
            if alerts:
                logger.info("IRR alerts generated", count=len(alerts))
        except Exception as e:
            logger.error("Async IRR check failed", error=str(e))
    
    def _run_health_check(self):
        """Executa verificação de saúde do sistema"""
        try:
            logger.info("Running system health check")
            
            # Executa verificação assíncrona
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_health_check(), self.loop
                ).result(timeout=60)
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
    
    async def _async_health_check(self):
        """Verificação assíncrona de saúde"""
        try:
            # Verifica conectividade com serviços externos
            from app.services.ripe_api import ripe_api
            
            # Teste básico da API RIPE
            try:
                await ripe_api.get_announced_prefixes(settings.target_asn)
                metrics.update_component_health("ripe_api", True)
            except Exception:
                metrics.update_component_health("ripe_api", False)
                
            # Teste do Telegram
            try:
                await telegram_service.send_status_update(
                    "BGP Monitor", 
                    "info", 
                    "Sistema de monitoramento funcionando normalmente"
                )
                metrics.update_component_health("telegram", True)
            except Exception:
                metrics.update_component_health("telegram", False)
                
            logger.info("Health check completed")
            
        except Exception as e:
            logger.error("Async health check failed", error=str(e))
    
    def _send_daily_report(self):
        """Envia relatório diário"""
        try:
            logger.info("Sending daily report")
            
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_daily_report(), self.loop
                ).result(timeout=120)
            
        except Exception as e:
            logger.error("Daily report failed", error=str(e))
    
    async def _async_daily_report(self):
        """Envia relatório diário assíncrono"""
        try:
            # Coleta estatísticas do sistema
            system_stats = metrics.get_system_stats()
            peer_summary = peer_monitor.get_peer_summary()
            irr_summary = irr_validator.get_validation_summary()
            
            # Monta mensagem do relatório
            report_message = f"""📊 **Relatório Diário BGP Monitor**
            
🎯 **ASN Monitorado:** AS{settings.target_asn}
⏱️ **Uptime:** {system_stats.get('uptime_seconds', 0)//3600}h
🚨 **Total de Alertas:** {system_stats.get('total_alerts', 0)}

👥 **Peers BGP:**
• Total: {peer_summary.get('total', 0)}
• Upstreams: {peer_summary.get('upstreams', 0)}
• Peers: {peer_summary.get('peers', 0)}
• Customers: {peer_summary.get('customers', 0)}

🔍 **Validações IRR:**
• Total validações: {irr_summary.get('total_validations', 0)}
• Prefixos válidos: {irr_summary.get('valid_prefixes', 0)}
• Prefixos inválidos: {irr_summary.get('invalid_prefixes', 0)}

✅ **Componentes Saudáveis:** {system_stats.get('healthy_components', 0)}

---
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"""
            
            await telegram_service.send_status_update(
                "BGP Monitor",
                "info",
                report_message
            )
            
            logger.info("Daily report sent successfully")
            
        except Exception as e:
            logger.error("Failed to send daily report", error=str(e))


# Instância global do scheduler
bgp_scheduler = BGPScheduler()
