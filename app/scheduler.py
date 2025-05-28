import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.core.config import settings
from app.core.asn_config import asn_config_manager
from app.services.telegram import telegram_service
from app.services.prefix_monitor import prefix_monitor
from app.services.peer_monitor import peer_monitor
from app.services.irr_validator import irr_validator
from app.services.bgp_data_service import bgp_data_service
from app.services.anomaly_detector import anomaly_detector
from app.database.connection import init_database, close_database
from app.utils.metrics import metrics
import logging

logger = logging.getLogger(__name__)


class BGPScheduler:
    """Scheduler simples para tarefas de monitoramento BGP"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.loop = None
        self.monitored_asns = []  # Lista de ASNs para monitoramento histórico
        
    async def initialize(self):
        """Inicializa o banco de dados e configurações"""
        await init_database()
        
        # Carregar ASNs do gerenciador de configuração
        self.monitored_asns = asn_config_manager.get_enabled_asns()
        
        # Se não houver ASNs configurados, usar o TARGET_ASN das configurações como fallback
        if not self.monitored_asns and settings.target_asn and settings.target_asn != 0:
            # Adicionar automaticamente o ASN das configurações
            asn_config_manager.add_asn(
                asn=settings.target_asn,
                name=f"AS{settings.target_asn}",
                description="ASN configurado automaticamente das configurações",
                monitoring_enabled=True,
                alert_enabled=True
            )
            self.monitored_asns = [settings.target_asn]
        
        logger.info(f"Scheduler initialized with {len(self.monitored_asns)} ASNs for historical monitoring: {self.monitored_asns}")
        
    def start(self):
        """Inicia o scheduler"""
        if self.running:
            return
            
        self.running = True
        
        # Configurar agendamento original
        schedule.every(settings.prefix_check_interval).seconds.do(self._run_prefix_check)
        schedule.every(settings.peer_check_interval).seconds.do(self._run_peer_check)
        schedule.every(settings.latency_check_interval).seconds.do(self._run_latency_check)
        schedule.every(settings.irr_check_interval).seconds.do(self._run_irr_check)
        schedule.every().hour.do(self._run_health_check)
        schedule.every().day.at("08:00").do(self._send_daily_report)
        
        # Agendamento para coleta de dados históricos
        schedule.every(5).minutes.do(self._run_historical_collection)  # Coleta a cada 5 minutos
        schedule.every(30).minutes.do(self._run_anomaly_detection)     # Detecção de anomalias
        schedule.every().day.at("02:00").do(self._run_data_cleanup)    # Limpeza diária
        schedule.every().day.at("06:00").do(self._send_weekly_analysis) # Relatório semanal (domingo)
        
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
            logger.error(f"Prefix check failed: {str(e)}")
            metrics.update_component_health("prefix_monitor", False)
    
    async def _async_prefix_check(self):
        """Verificação assíncrona de prefixos"""
        try:
            alerts = await prefix_monitor.check_prefix_announcements()
            if alerts:
                logger.info(f"Prefix alerts generated (count: {len(alerts)})")
            metrics.update_component_health("prefix_monitor", True)
        except Exception as e:
            logger.error(f"Async prefix check failed: {str(e)}")
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
            logger.error(f"Peer check failed: {str(e)}")
            metrics.update_component_health("peer_monitor", False)
    
    async def _async_peer_check(self):
        """Verificação assíncrona de peers"""
        try:
            alerts = await peer_monitor.check_peer_relationships()
            if alerts:
                logger.info(f"Peer alerts generated (count: {len(alerts)})")
            metrics.update_component_health("peer_monitor", True)
        except Exception as e:
            logger.error(f"Async peer check failed: {str(e)}")
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
            logger.error(f"Latency check failed: {str(e)}")
    
    async def _async_latency_check(self):
        """Verificação assíncrona de latência"""
        try:
            alerts = await peer_monitor.measure_latency()
            if alerts:
                logger.info(f"Latency alerts generated (count: {len(alerts)})")
        except Exception as e:
            logger.error(f"Async latency check failed: {str(e)}")
    
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
            logger.error(f"IRR check failed: {str(e)}")
    
    async def _async_irr_check(self):
        """Verificação assíncrona de IRR"""
        try:
            monitored_prefixes = prefix_monitor.get_monitored_prefixes()
            alerts = await irr_validator.validate_all_monitored_prefixes(monitored_prefixes)
            if alerts:
                logger.info(f"IRR alerts generated (count: {len(alerts)})")
        except Exception as e:
            logger.error(f"Async IRR check failed: {str(e)}")
    
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
            logger.error(f"Health check failed: {str(e)}")
    
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
            logger.error(f"Async health check failed: {str(e)}")
    
    def _send_daily_report(self):
        """Envia relatório diário"""
        try:
            logger.info("Sending daily report")
            
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_daily_report(), self.loop
                ).result(timeout=120)
            
        except Exception as e:
            logger.error(f"Daily report failed: {str(e)}")
    
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
            logger.error(f"Failed to send daily report: {str(e)}")
    
    def _run_historical_collection(self):
        """Executa coleta de dados históricos para todos os ASNs monitorados"""
        try:
            if not self.loop:
                return
                
            logger.info("Starting historical data collection...")
            asyncio.run_coroutine_threadsafe(
                self._async_historical_collection(), self.loop
            ).result(timeout=300)  # 5 minutos timeout
            
        except Exception as e:
            logger.error(f"Historical collection failed: {str(e)}")
    
    async def _async_historical_collection(self):
        """Executa coleta de dados históricos assíncrona"""
        try:
            if not self.monitored_asns:
                logger.warning("No ASNs configured for historical monitoring")
                return
            
            # Coletar snapshots de todos os ASNs
            results = await bgp_data_service.collect_multiple_asns(
                self.monitored_asns, 
                batch_size=settings.api_batch_size
            )
            
            successful_collections = len([r for r in results if r])
            total_asns = len(self.monitored_asns)
            
            logger.info(f"Historical collection completed: {successful_collections}/{total_asns} ASNs")
            
            # Atualizar métricas
            metrics.increment_counter("historical_collections")
            metrics.set_gauge("asns_collected", successful_collections)
            
        except Exception as e:
            logger.error(f"Historical collection error: {e}")
            metrics.increment_counter("historical_collection_errors")
    
    def _run_anomaly_detection(self):
        """Executa detecção de anomalias para todos os ASNs monitorados"""
        try:
            if not self.loop:
                return
                
            logger.info("Starting anomaly detection...")
            asyncio.run_coroutine_threadsafe(
                self._async_anomaly_detection(), self.loop
            ).result(timeout=180)  # 3 minutos timeout
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
    
    async def _async_anomaly_detection(self):
        """Executa detecção de anomalias assíncrona"""
        try:
            if not self.monitored_asns:
                return
            
            # Executar detecção de anomalias
            anomaly_report = await anomaly_detector.monitor_multiple_asns(self.monitored_asns)
            
            total_anomalies = anomaly_report['summary']['total_anomalies']
            high_severity = anomaly_report['summary']['high_severity_count']
            unstable_asns = anomaly_report['summary']['unstable_asns']
            
            logger.info(
                f"Anomaly detection completed: {total_anomalies} anomalies detected "
                f"({high_severity} high severity, {unstable_asns} unstable ASNs)"
            )
            
            # Atualizar métricas
            metrics.increment_counter("anomaly_detections")
            metrics.set_gauge("current_anomalies", total_anomalies)
            metrics.set_gauge("high_severity_anomalies", high_severity)
            
            # Enviar alerta se houver muitas anomalias
            if high_severity > 2:
                await self._send_high_anomaly_alert(anomaly_report)
                
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            metrics.increment_counter("anomaly_detection_errors")
    
    def _run_data_cleanup(self):
        """Executa limpeza de dados antigos"""
        try:
            if not self.loop:
                return
                
            logger.info("Starting data cleanup...")
            asyncio.run_coroutine_threadsafe(
                self._async_data_cleanup(), self.loop
            ).result(timeout=600)  # 10 minutos timeout
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {str(e)}")
    
    async def _async_data_cleanup(self):
        """Executa limpeza de dados antigos assíncrona"""
        try:
            await bgp_data_service.cleanup_old_data(settings.data_retention_days)
            logger.info("Data cleanup completed successfully")
            metrics.increment_counter("data_cleanups")
            
        except Exception as e:
            logger.error(f"Data cleanup error: {e}")
            metrics.increment_counter("data_cleanup_errors")
    
    def _send_weekly_analysis(self):
        """Envia análise semanal (apenas aos domingos)"""
        if datetime.now().weekday() != 6:  # 6 = domingo
            return
            
        try:
            if not self.loop:
                return
                
            logger.info("Starting weekly analysis...")
            asyncio.run_coroutine_threadsafe(
                self._async_weekly_analysis(), self.loop
            ).result(timeout=300)
            
        except Exception as e:
            logger.error(f"Weekly analysis failed: {str(e)}")
    
    async def _async_weekly_analysis(self):
        """Executa análise semanal assíncrona"""
        try:
            if not self.monitored_asns:
                return
            
            weekly_reports = []
            
            for asn in self.monitored_asns:
                # Gerar estatísticas da semana
                stats = await bgp_data_service.get_asn_statistics(asn, days_back=7)
                
                # Detectar alterações da semana
                changes = await bgp_data_service.detect_prefix_changes(asn, hours_back=168)  # 7 dias
                
                # Verificar instabilidade
                instability = await anomaly_detector.detect_routing_instability(asn, window_hours=168)
                
                weekly_reports.append({
                    'asn': asn,
                    'stats': stats,
                    'changes': changes,
                    'instability': instability
                })
            
            # Enviar relatório consolidado
            await self._send_weekly_report(weekly_reports)
            
        except Exception as e:
            logger.error(f"Weekly analysis error: {e}")
    
    async def _send_high_anomaly_alert(self, anomaly_report: Dict[str, Any]):
        """Envia alerta quando há muitas anomalias detectadas"""
        high_severity = anomaly_report['summary']['high_severity_count']
        total_anomalies = anomaly_report['summary']['total_anomalies']
        
        message = f"""🚨 **ALERTA: Múltiplas Anomalias BGP Detectadas**

⚠️ **Anomalias de Alta Severidade:** {high_severity}
📊 **Total de Anomalias:** {total_anomalies}
🕐 **Horário:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

🔍 **Ação Recomendada:**
• Investigar imediatamente as alterações de roteamento
• Verificar configurações BGP dos ASNs afetados
• Monitorar conectividade de rede

💡 **ASNs com Instabilidade:** {anomaly_report['summary']['unstable_asns']}

---
Esta mensagem é enviada automaticamente quando múltiplas anomalias de alta severidade são detectadas."""
        
        await telegram_service.send_message(message)
    
    async def _send_weekly_report(self, weekly_reports: List[Dict[str, Any]]):
        """Envia relatório semanal consolidado"""
        if not weekly_reports:
            return
        
        # Calcular estatísticas gerais
        total_changes = sum(len(report['changes']) for report in weekly_reports)
        unstable_count = sum(1 for report in weekly_reports 
                           if report['instability']['status'] in ['unstable', 'highly_unstable'])
        
        message = f"""📈 **Relatório Semanal BGP Monitor**

📅 **Período:** {(datetime.now() - timedelta(days=7)).strftime('%d/%m')} - {datetime.now().strftime('%d/%m/%Y')}
🎯 **ASNs Monitorados:** {len(weekly_reports)}

📊 **Resumo da Semana:**
• Total de alterações detectadas: {total_changes}
• ASNs com instabilidade: {unstable_count}

"""
        
        # Adicionar detalhes por ASN
        for report in weekly_reports:
            asn = report['asn']
            stats = report['stats']
            changes_count = len(report['changes'])
            stability_score = report['instability']['instability_score']
            
            if 'prefix_statistics' in stats:
                prefix_stats = stats['prefix_statistics']
                message += f"""
🔹 **AS{asn}:**
   • Prefixos atuais: {prefix_stats.get('current_count', 'N/A')}
   • Alterações na semana: {changes_count}
   • Score de estabilidade: {stability_score:.1f}/100
   • Status: {report['instability']['status']}
"""
        
        message += f"""
---
📝 **Observações:**
• Scores baixos de estabilidade indicam mudanças frequentes
• Monitore ASNs com instabilidade alta
• Relatório gerado automaticamente aos domingos

🕐 **Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"""
        
        await telegram_service.send_message(message)
    
    def add_asn_to_monitoring(self, asn: int):
        """Adiciona um ASN à lista de monitoramento histórico"""
        if asn not in self.monitored_asns:
            self.monitored_asns.append(asn)
            logger.info(f"Added AS{asn} to historical monitoring")
    
    def remove_asn_from_monitoring(self, asn: int):
        """Remove um ASN da lista de monitoramento histórico"""
        if asn in self.monitored_asns:
            self.monitored_asns.remove(asn)
            logger.info(f"Removed AS{asn} from historical monitoring")
    
    def get_monitored_asns(self) -> List[int]:
        """Retorna a lista de ASNs sendo monitorados"""
        return self.monitored_asns.copy()
    
    async def cleanup(self):
        """Limpeza final do scheduler"""
        try:
            await close_database()
            logger.info("Scheduler cleanup completed")
        except Exception as e:
            logger.error(f"Scheduler cleanup error: {e}")

# Instância global do scheduler
bgp_scheduler = BGPScheduler()
