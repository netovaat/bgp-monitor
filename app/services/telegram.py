import asyncio
import logging
from typing import Dict, Any, Optional
from telegram import Bot
from telegram.error import TelegramError

from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Serviço para envio de notificações via Telegram"""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self._bot = None
    
    @property
    def bot(self):
        """Lazy initialization do bot Telegram"""
        if self._bot is None and self.bot_token:
            self._bot = Bot(token=self.bot_token)
        return self._bot
        
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Envia um alerta via Telegram"""
        try:
            # Verificar se configuração está válida
            if not self.bot_token or not self.chat_id:
                logger.warning("Telegram bot token ou chat_id não configurados")
                return False
                
            if not self.bot:
                logger.error("Falha ao inicializar bot Telegram")
                return False
            
            message = self._format_alert_message(alert_data)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
            logger.info(f"Telegram alert sent - Type: {alert_data.get('alert_type')}, Severity: {alert_data.get('severity')}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram alert: {str(e)}")
            return False
    
    async def send_recovery_alert(self, recovery_data: Dict[str, Any]) -> bool:
        """Envia um alerta de recuperação via Telegram"""
        # Força severidade como 'info' para alarmes de recuperação
        recovery_data["severity"] = "info"
        return await self.send_alert(recovery_data)
    
    async def send_status_update(self, component: str, status: str, details: Optional[str] = None) -> bool:
        """Envia atualização de status do sistema"""
        try:
            emoji_map = {
                "healthy": "✅",
                "warning": "⚠️", 
                "error": "❌"
            }
            
            emoji = emoji_map.get(status, "ℹ️")
            message = f"{emoji} <b>BGP Monitor Status</b>\n\n"
            message += f"<b>Component:</b> {component}\n"
            message += f"<b>Status:</b> {status.upper()}\n"
            
            if details:
                message += f"<b>Details:</b> {details}\n"
                
            message += f"<b>Time:</b> {self._get_current_time()}"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send status update: {str(e)}")
            return False
    
    async def send_daily_report(self, report_data: Dict[str, Any]) -> bool:
        """Envia relatório diário de monitoramento"""
        try:
            message = self._format_daily_report(report_data)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("Daily report sent via Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send daily report: {str(e)}")
            return False
    
    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Formata mensagem de alerta para Telegram"""
        severity_emoji = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        alert_type_emoji = {
            "prefix_missing": "📡",
            "route_leak": "🔗", 
            "peer_loss": "🛑",
            "latency_high": "🌐",
            "irr_validation": "📋",
            "insufficient_upstreams": "📊",
            "sudden_increase": "📊",
            "sudden_decrease": "📊",
            "routing_instability": "🔄",
            # Alarmes de recuperação
            "peer_recovered": "🟢",
            "prefix_restored": "🟢", 
            "upstreams_normalized": "🟢",
            "latency_normalized": "🟢",
            "instability_resolved": "🟢",
            "anomaly_resolved": "🟢"
        }
        
        # Mensagens PT-BR
        alert_messages_pt_br = {
            "peer_loss": "🛑 Perda de {relationship} AS{peer_asn} detectada.",
            "prefix_missing": "📡 Prefixo crítico {prefix} não visível na tabela BGP.",
            "route_leak": "🔗 Possível vazamento detectado: prefixo {prefix} anunciado indevidamente.",
            "insufficient_upstreams": "📊 Número insuficiente de upstreams ativos ({active}/{minimum} mínimo).",
            "latency_high": "🌐 Latência elevada detectada para AS{peer_asn} ({latency}ms).",
            "irr_validation": "📋 Anúncio BGP não conforme com registro IRR detectado.",
            "sudden_increase": "📊 Aumento súbito de {percentage}% nos anúncios BGP detectado.",
            "sudden_decrease": "📊 Diminuição anômala de {percentage}% nos prefixos anunciados.",
            "routing_instability": "🔄 Instabilidade crítica: {changes} mudanças de rota em {timeframe} minutos.",
            # Mensagens de recuperação
            "peer_recovered": "🟢 {relationship} AS{peer_asn} recuperado com sucesso.",
            "prefix_restored": "🟢 Prefixo {prefix} restaurado na tabela BGP.",
            "upstreams_normalized": "🟢 Número de upstreams normalizado ({active}/{minimum} mínimo).",
            "latency_normalized": "🟢 Latência normalizada para AS{peer_asn} ({latency}ms).",
            "instability_resolved": "🟢 Instabilidade de roteamento resolvida.",
            "anomaly_resolved": "🟢 Anomalia estatística resolvida - valores normalizados."
        }
        
        alert_type_names_pt_br = {
            "peer_loss": "Perda de Peer BGP",
            "prefix_missing": "Prefixo Ausente",
            "route_leak": "Vazamento de Rota",
            "insufficient_upstreams": "Conectividade Upstream",
            "latency_high": "Performance de Rede",
            "irr_validation": "Validação IRR",
            "sudden_increase": "Anomalia Estatística",
            "sudden_decrease": "Anomalia Estatística", 
            "routing_instability": "Instabilidade de Roteamento",
            # Tipos de recuperação
            "peer_recovered": "Peer Recuperado",
            "prefix_restored": "Prefixo Restaurado",
            "upstreams_normalized": "Conectividade Normalizada",
            "latency_normalized": "Performance Normalizada",
            "instability_resolved": "Estabilidade Restaurada",
            "anomaly_resolved": "Anomalia Resolvida"
        }
        
        relationship_types_pt_br = {
            "upstream": "upstream",
            "peer": "peer", 
            "customer": "customer",
            "unknown": "relacionamento desconhecido"
        }
        
        severity = alert_data.get("severity", "info")
        alert_type = alert_data.get("alert_type", "unknown")
        details = alert_data.get("details", {})
        
        emoji = severity_emoji.get(severity, "ℹ️")
        type_emoji = alert_type_emoji.get(alert_type, "📊")
        
        # Usar mensagem PT-BR se disponível
        if alert_type in alert_messages_pt_br:
            message_template = alert_messages_pt_br[alert_type]
            # Formatação dinâmica da mensagem baseada nos detalhes
            try:
                if alert_type in ["peer_loss", "peer_recovered"]:
                    relationship = details.get('relationship_type', 'unknown')
                    relationship_pt = relationship_types_pt_br.get(relationship, relationship)
                    formatted_message = message_template.format(
                        relationship=relationship_pt.capitalize(),
                        peer_asn=details.get('peer_asn', 'unknown')
                    )
                elif alert_type in ["prefix_missing", "prefix_restored", "route_leak"]:
                    formatted_message = message_template.format(
                        prefix=details.get('prefix', 'unknown')
                    )
                elif alert_type in ["insufficient_upstreams", "upstreams_normalized"]:
                    formatted_message = message_template.format(
                        active=details.get('active_upstreams', 0),
                        minimum=details.get('minimum_required', 0)
                    )
                elif alert_type in ["latency_high", "latency_normalized"]:
                    formatted_message = message_template.format(
                        peer_asn=details.get('peer_asn', 'unknown'),
                        latency=details.get('latency_ms', 0)
                    )
                elif alert_type in ["sudden_increase", "sudden_decrease"]:
                    formatted_message = message_template.format(
                        percentage=details.get('change_percentage', 0)
                    )
                elif alert_type == "routing_instability":
                    formatted_message = message_template.format(
                        changes=details.get('route_changes', 0),
                        timeframe=details.get('timeframe_minutes', 5)
                    )
                else:
                    formatted_message = message_template
            except KeyError:
                formatted_message = alert_data.get('message', 'Mensagem não disponível')
        else:
            formatted_message = alert_data.get('message', 'No message')
        
        message = f"{emoji} <b>Monitor BGP - Alerta</b> {type_emoji}\n\n"
        message += f"<b>Severidade:</b> {severity.upper()}\n"
        
        type_name = alert_type_names_pt_br.get(alert_type, alert_type.replace('_', ' ').title())
        message += f"<b>Tipo:</b> {type_name}\n\n"
        message += f"<b>Mensagem:</b>\n{formatted_message}\n\n"
        
        # Adiciona detalhes específicos baseado no tipo de alerta
        if details:
            message += "<b>Detalhes:</b>\n"
            
            if alert_type == "prefix_missing":
                message += f"• Prefixo: <code>{details.get('prefix')}</code>\n"
                message += f"• ASN Origem: AS{details.get('asn')}\n"
                if details.get('last_seen'):
                    message += f"• Última Visibilidade: {details.get('last_seen')}\n"
                message += "• Impacto: Serviços indisponíveis\n"
                
            elif alert_type == "prefix_restored":
                message += f"• Prefixo: <code>{details.get('prefix')}</code>\n"
                message += f"• ASN Origem: AS{details.get('asn')}\n"
                downtime = details.get('downtime_minutes', 0)
                message += f"• Tempo de Ausência: {downtime} minutos\n"
                message += "• Status: Visibilidade global restaurada\n"
                message += "• Impacto: Serviços normalizados\n"
                
            elif alert_type == "route_leak":
                message += f"• Prefixo: <code>{details.get('prefix')}</code>\n"
                message += f"• ASN Origem Legítima: AS{details.get('origin_asn')}\n"
                unexpected_asns = details.get('unexpected_asns', [])
                if unexpected_asns:
                    asn_list = ', '.join([f'AS{asn}' for asn in unexpected_asns])
                    message += f"• ASNs Suspeitos: {asn_list}\n"
                message += "• Tipo: Route leak através de peer\n"
                message += "• Ação: Verificar filtros BGP\n"
                
            elif alert_type == "peer_loss":
                peer_asn = details.get('peer_asn')
                relationship = details.get('relationship_type', 'unknown')
                message += f"• Peer Perdido: AS{peer_asn}\n"
                message += f"• Tipo de Relacionamento: {relationship}\n"
                if relationship == "upstream":
                    message += "• Impacto: Alta disponibilidade comprometida\n"
                else:
                    message += "• Impacto: Redundância reduzida\n"
                    
            elif alert_type == "peer_recovered":
                peer_asn = details.get('peer_asn')
                relationship = details.get('relationship_type', 'unknown')
                downtime = details.get('downtime_minutes', 0)
                message += f"• Peer Recuperado: AS{peer_asn}\n"
                message += f"• Tipo de Relacionamento: {relationship}\n"
                message += f"• Tempo de Indisponibilidade: {downtime} minutos\n"
                message += "• Status: Conectividade restaurada\n"
                if relationship == "upstream":
                    message += "• Impacto: Alta disponibilidade normalizada\n"
                else:
                    message += "• Impacto: Redundância normalizada\n"
                    
            elif alert_type == "insufficient_upstreams":
                active = details.get('active_upstreams', 0)
                minimum = details.get('minimum_required', 0)
                lost_upstreams = details.get('lost_upstreams', [])
                message += f"• Upstreams Ativos: {active}\n"
                message += f"• Mínimo Configurado: {minimum}\n"
                if lost_upstreams:
                    lost_list = ', '.join([f'AS{asn}' for asn in lost_upstreams])
                    message += f"• Upstreams Perdidos: {lost_list}\n"
                message += "• Risco: Dependência excessiva de provedores\n"
                
            elif alert_type == "upstreams_normalized":
                active = details.get('active_upstreams', 0)
                minimum = details.get('minimum_required', 0)
                recovered_upstreams = details.get('recovered_upstreams', [])
                problem_duration = details.get('problem_duration_minutes', 0)
                message += f"• Upstreams Ativos: {active}\n"
                message += f"• Mínimo Configurado: {minimum}\n"
                if recovered_upstreams:
                    recovered_list = ', '.join([f'AS{asn}' for asn in recovered_upstreams])
                    message += f"• Upstreams Recuperados: {recovered_list}\n"
                message += "• Status: Redundância adequada restaurada\n"
                message += f"• Tempo de Problema: {problem_duration} minutos\n"
                
            elif alert_type == "latency_high":
                peer_asn = details.get('peer_asn')
                current_latency = details.get('latency_ms', 0)
                threshold = details.get('threshold_ms', 100)
                message += f"• Peer Afetado: AS{peer_asn}\n"
                message += f"• Latência Atual: {current_latency}ms\n"
                message += f"• Limite Configurado: {threshold}ms\n"
                message += "• Tendência: Aumentando nos últimos 10 minutos\n"
                message += "• Recomendação: Monitorar conectividade\n"
                
            elif alert_type == "latency_normalized":
                peer_asn = details.get('peer_asn')
                current_latency = details.get('latency_ms', 0)
                previous_latency = details.get('previous_latency_ms', 0)
                threshold = details.get('threshold_ms', 100)
                improvement = details.get('improvement_ms', 0)
                message += f"• Peer Afetado: AS{peer_asn}\n"
                message += f"• Latência Atual: {current_latency}ms\n"
                message += f"• Latência Anterior: {previous_latency}ms\n"
                message += f"• Limite Configurado: {threshold}ms\n"
                if improvement > 0:
                    improvement_pct = round((improvement / previous_latency) * 100) if previous_latency > 0 else 0
                    message += f"• Melhoria: -{improvement_pct}% ({improvement}ms de redução)\n"
                message += "• Status: Performance restaurada\n"
                
            elif alert_type in ["sudden_increase", "sudden_decrease"]:
                metric = details.get('metric', 'anúncios BGP')
                change_pct = details.get('change_percentage', 0)
                previous_value = details.get('previous_value', 0)
                current_value = details.get('current_value', 0)
                z_score = details.get('z_score', 0)
                timeframe = details.get('timeframe_minutes', 15)
                
                message += f"• Métrica: {metric}\n"
                if alert_type == "sudden_increase":
                    message += f"• Variação: +{change_pct}% (de {previous_value} para {current_value}/hora)\n"
                else:
                    message += f"• Variação: -{change_pct}% (de {previous_value} para {current_value} prefixos)\n"
                message += f"• Janela Temporal: Últimos {timeframe} minutos\n"
                message += f"• Desvio Padrão: {z_score}σ"
                if z_score > 5:
                    message += " (muito além do normal)\n"
                elif z_score > 3:
                    message += " (além do normal)\n"
                else:
                    message += "\n"
                    
                if alert_type == "sudden_increase" and change_pct > 300:
                    message += "• Possíveis Causas: Route leak, ataque, falha de filtro\n"
                else:
                    message += "• Possível Causa: Falha de configuração ou conectividade\n"
                    
            elif alert_type == "anomaly_resolved":
                metric = details.get('metric', 'anúncios BGP')
                current_value = details.get('current_value', 0)
                previous_value = details.get('previous_value', 0)
                reduction = details.get('reduction_value', 0)
                z_score = details.get('current_z_score', 0)
                duration = details.get('anomaly_duration_minutes', 0)
                
                message += f"• Métrica: {metric}\n"
                message += f"• Valor Atual: {current_value}/hora (normal)\n"
                message += f"• Valor Anterior: {previous_value}/hora (anômalo)\n"
                if reduction > 0:
                    reduction_pct = round((reduction / previous_value) * 100) if previous_value > 0 else 0
                    message += f"• Redução: -{reduction_pct}% ({reduction} anúncios/hora)\n"
                message += f"• Desvio Atual: {z_score}σ (dentro do normal)\n"
                message += f"• Duração da Anomalia: {duration} minutos\n"
                
            elif alert_type == "routing_instability":
                affected_prefixes = details.get('affected_prefixes', 0)
                route_changes = details.get('route_changes', 0)
                timeframe = details.get('timeframe_minutes', 5)
                involved_asns = details.get('involved_asns', [])
                
                message += f"• Prefixos Afetados: {affected_prefixes} prefixos únicos\n"
                message += f"• Mudanças de Rota: {route_changes} nos últimos {timeframe} minutos\n"
                message += f"• Limite Normal: <10 mudanças/{timeframe}min\n"
                if involved_asns:
                    asn_list = ', '.join([f'AS{asn}' for asn in involved_asns[:3]])
                    message += f"• ASNs Envolvidos: {asn_list}\n"
                if route_changes > 30:
                    message += "• Impacto: Degradação severa da convergência\n"
                else:
                    message += "• Recomendação: Monitoramento contínuo\n"
                    
            elif alert_type == "instability_resolved":
                current_changes = details.get('current_changes', 0)
                previous_changes = details.get('previous_changes', 0)
                timeframe = details.get('timeframe_minutes', 5)
                reduction_pct = details.get('reduction_percentage', 0)
                duration = details.get('problem_duration_minutes', 0)
                
                message += f"• Mudanças de Rota: {current_changes} nos últimos {timeframe} minutos\n"
                message += f"• Limite Normal: <10 mudanças/{timeframe}min\n"
                if reduction_pct > 0:
                    message += f"• Redução: -{reduction_pct}% (de {previous_changes} para {current_changes} mudanças)\n"
                message += f"• Duração do Problema: {duration} minutos\n"
                message += "• Status: Convergência normalizada\n"
                
            elif alert_type == "irr_validation":
                prefix = details.get('prefix')
                announcing_asn = details.get('announcing_asn')
                message += f"• Prefixo: <code>{prefix}</code>\n"
                message += f"• ASN Anunciante: AS{announcing_asn}\n"
                message += "• Status IRR: Não registrado/conflitante\n"
                message += "• Base IRR Consultada: RADB, RIPE\n"
                message += "• Ação Sugerida: Verificar autorização de anúncio\n"
                
        message += f"\n<b>Horário:</b> {self._get_current_time_brt()}"
        
        return message
    
    def _get_current_time_brt(self) -> str:
        """Retorna timestamp atual formatado em BRT"""
        from datetime import datetime, timezone, timedelta
        # UTC-3 para BRT
        brt = timezone(timedelta(hours=-3))
        now_brt = datetime.now(brt)
        return now_brt.strftime("%d/%m/%Y %H:%M:%S BRT")
    
    def _format_daily_report(self, report_data: Dict[str, Any]) -> str:
        """Formata relatório diário"""
        message = "📊 <b>BGP Monitor Daily Report</b>\n\n"
        
        # Estatísticas gerais
        stats = report_data.get("stats", {})
        message += "<b>📈 Statistics (Last 24h):</b>\n"
        message += f"• Total Alerts: {stats.get('total_alerts', 0)}\n"
        message += f"• Critical Alerts: {stats.get('critical_alerts', 0)}\n"
        message += f"• Monitored Prefixes: {stats.get('monitored_prefixes', 0)}\n"
        message += f"• Active Peers: {stats.get('active_peers', 0)}\n"
        message += f"• Avg Latency: {stats.get('avg_latency', 0)}ms\n\n"
        
        # Status dos componentes
        components = report_data.get("component_status", {})
        message += "<b>🔧 Component Status:</b>\n"
        for component, status in components.items():
            emoji = "✅" if status == "healthy" else "❌"
            message += f"• {component.replace('_', ' ').title()}: {emoji}\n"
        
        message += f"\n<b>Generated:</b> {self._get_current_time()}"
        
        return message
    
    def _get_current_time(self) -> str:
        """Retorna timestamp atual formatado"""
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    async def test_connection(self) -> bool:
        """Testa a conexão com o Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="🤖 BGP Monitor - Teste de conexão realizado com sucesso!"
            )
            return True
        except Exception as e:
            logger.error(f"Telegram connection test failed: {str(e)}")
            return False


# Instância global do serviço Telegram
telegram_service = TelegramService()
