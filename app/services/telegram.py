import asyncio
from typing import Dict, Any, Optional
from telegram import Bot
from telegram.error import TelegramError
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class TelegramService:
    """Serviço para envio de notificações via Telegram"""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.bot = Bot(token=self.bot_token)
        
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Envia um alerta via Telegram"""
        try:
            message = self._format_alert_message(alert_data)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
            logger.info("Telegram alert sent", 
                       alert_type=alert_data.get("alert_type"),
                       severity=alert_data.get("severity"))
            return True
            
        except TelegramError as e:
            logger.error("Failed to send Telegram alert", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error sending Telegram alert", error=str(e))
            return False
    
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
            logger.error("Failed to send status update", error=str(e))
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
            logger.error("Failed to send daily report", error=str(e))
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
            "irr_validation": "📋"
        }
        
        severity = alert_data.get("severity", "info")
        alert_type = alert_data.get("alert_type", "unknown")
        
        emoji = severity_emoji.get(severity, "ℹ️")
        type_emoji = alert_type_emoji.get(alert_type, "📊")
        
        message = f"{emoji} <b>BGP Monitor Alert</b> {type_emoji}\n\n"
        message += f"<b>Severity:</b> {severity.upper()}\n"
        message += f"<b>Type:</b> {alert_type.replace('_', ' ').title()}\n\n"
        message += f"<b>Message:</b>\n{alert_data.get('message', 'No message')}\n\n"
        
        # Adiciona detalhes específicos baseado no tipo de alerta
        details = alert_data.get("details", {})
        if details:
            message += "<b>Details:</b>\n"
            
            if alert_type == "prefix_missing":
                message += f"• Prefix: <code>{details.get('prefix')}</code>\n"
                message += f"• ASN: AS{details.get('asn')}\n"
                
            elif alert_type == "route_leak":
                message += f"• Prefix: <code>{details.get('prefix')}</code>\n"
                message += f"• Origin ASN: AS{details.get('origin_asn')}\n"
                message += f"• Unexpected ASNs: {', '.join([f'AS{asn}' for asn in details.get('unexpected_asns', [])])}\n"
                
            elif alert_type == "peer_loss":
                message += f"• Lost Peer: AS{details.get('peer_asn')}\n"
                message += f"• Relationship: {details.get('relationship_type', 'unknown')}\n"
                
            elif alert_type == "latency_high":
                message += f"• Target: <code>{details.get('target_prefix')}</code>\n"
                message += f"• Latency: {details.get('latency_ms')}ms\n"
                message += f"• Threshold: {settings.max_latency_ms}ms\n"
                
        message += f"\n<b>Time:</b> {self._get_current_time()}"
        
        return message
    
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
            logger.error("Telegram connection test failed", error=str(e))
            return False


# Instância global do serviço Telegram
telegram_service = TelegramService()
