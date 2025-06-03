# 🎨 Guia de Customização de Alarmes do Telegram

## 🚀 **Como Customizar os Alarmes do BGP Monitor**

### **1. Alterando Emojis dos Alarmes**

Edite o arquivo `app/services/telegram.py`, na função `_format_alert_message()`:

```python
# ANTES (padrão)
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

# DEPOIS (customizado)
severity_emoji = {
    "critical": "💥",      # Mais dramático
    "warning": "🔔",       # Sino de alerta
    "info": "💡"           # Lâmpada para info
}

alert_type_emoji = {
    "prefix_missing": "🔍",     # Lupa para busca
    "route_leak": "⚡",         # Raio para vazamento
    "peer_loss": "💔",          # Coração partido
    "latency_high": "🐌",       # Caracol para lentidão
    "irr_validation": "📝"      # Papel para validação
}
```

### **2. Personalizando Mensagens por Tipo**

```python
def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
    # ... código existente ...
    
    # CUSTOMIZAÇÃO: Mensagens personalizadas por tipo
    alert_type = alert_data.get("alert_type", "unknown")
    
    if alert_type == "peer_loss":
        # Mensagem personalizada para perda de peer
        relationship = alert_data.get("details", {}).get("relationship_type", "unknown")
        peer_asn = alert_data.get("details", {}).get("peer_asn")
        
        if relationship == "upstream":
            custom_message = f"🔥 EMERGÊNCIA: Perdemos upstream AS{peer_asn}! Conectividade em risco!"
        elif relationship == "customer":
            custom_message = f"💰 RECEITA: Cliente AS{peer_asn} desconectou. Verificar impacto financeiro."
        else:
            custom_message = f"🔄 REDE: Peer AS{peer_asn} offline. Monitorando estabilidade."
            
        # Substituir mensagem padrão
        message = message.replace(alert_data.get('message', ''), custom_message)
    
    # ... resto do código ...
```

### **3. Adicionando Informações Extras**

```python
# Adicionar campos extras aos detalhes
if alert_type == "peer_loss":
    message += f"• Lost Peer: AS{details.get('peer_asn')}\n"
    message += f"• Relationship: {details.get('relationship_type', 'unknown')}\n"
    
    # NOVOS CAMPOS PERSONALIZADOS
    message += f"• 📍 Localização: {details.get('peer_country', 'Unknown')}\n"
    message += f"• ⏱️ Downtime: {details.get('downtime_duration', 'Unknown')}\n"
    message += f"• 📊 Impacto: {details.get('traffic_impact', 'Analyzing...')}\n"
    message += f"• 🎯 Ação: {details.get('recommended_action', 'Monitor')}\n"
    message += f"• 📞 Contato: {details.get('peer_contact', 'N/A')}\n"
```

### **4. Formatação HTML Avançada**

```python
def _format_advanced_alert(self, alert_data: Dict[str, Any]) -> str:
    """Formatação mais avançada com HTML"""
    
    message = f"""
<b>🚨 BGP MONITOR ALERT 🚨</b>

<b>📋 INFORMAÇÕES BÁSICAS:</b>
├─ <b>Severidade:</b> <code>{severity.upper()}</code>
├─ <b>Tipo:</b> <code>{alert_type.replace('_', ' ').title()}</code>
└─ <b>Horário:</b> <code>{timestamp}</code>

<b>🔍 DETALHES TÉCNICOS:</b>
├─ <b>ASN Afetado:</b> <code>AS{target_asn}</code>
├─ <b>Peer Perdido:</b> <code>AS{peer_asn}</code>
├─ <b>Tipo Relação:</b> <code>{relationship}</code>
└─ <b>Duração:</b> <code>{duration}</code>

<b>🎯 AÇÃO RECOMENDADA:</b>
<i>{recommended_action}</i>

<b>📞 CONTATOS:</b>
├─ <b>NOC:</b> <code>{noc_contact}</code>
└─ <b>Peer:</b> <code>{peer_contact}</code>
"""
    
    return message
```

### **5. Alertas por Severidade Diferenciados**

```python
def _get_severity_config(self, severity: str) -> dict:
    """Configuração específica por severidade"""
    
    configs = {
        "critical": {
            "emoji": "🚨",
            "prefix": "⚠️ CRÍTICO ⚠️",
            "color_tag": "🔴",
            "urgency": "IMEDIATO"
        },
        "warning": {
            "emoji": "⚠️",
            "prefix": "⚡ ATENÇÃO ⚡",
            "color_tag": "🟡",
            "urgency": "MODERADO"
        },
        "info": {
            "emoji": "ℹ️",
            "prefix": "📊 INFO 📊",
            "color_tag": "🟢",
            "urgency": "BAIXO"
        }
    }
    
    return configs.get(severity, configs["info"])
```

### **6. Templates por Horário**

```python
def _get_time_based_template(self) -> dict:
    """Templates diferentes por horário"""
    from datetime import datetime
    
    current_hour = datetime.now().hour
    
    if 22 <= current_hour or current_hour <= 6:
        # Noturno - mais discreto
        return {
            "urgency_emoji": "🌙",
            "prefix": "Alerta Noturno",
            "tone": "discreto"
        }
    elif 6 < current_hour <= 18:
        # Comercial - mais formal
        return {
            "urgency_emoji": "🏢",
            "prefix": "Alerta BGP",
            "tone": "formal"
        }
    else:
        # Fim de expediente - moderado
        return {
            "urgency_emoji": "🌅",
            "prefix": "Alerta de Rede",
            "tone": "moderado"
        }
```

## 🧪 **Testando Suas Customizações**

### **1. Usando o Script de Teste**
```bash
# Execute o script de teste que criamos
./test_telegram_alerts.sh
```

### **2. Teste Manual via Python**
```python
# Criar arquivo test_custom_alert.py
import asyncio
import sys
sys.path.append('/opt/bgp-monitor')

from app.services.telegram import telegram_service

async def test_custom_alert():
    alert_data = {
        "alert_type": "peer_loss",
        "severity": "critical",
        "message": "🔥 TESTE: Seu alerta customizado aqui!",
        "details": {
            "peer_asn": 65001,
            "relationship_type": "upstream",
            "peer_country": "Brasil",
            "downtime_duration": "5 minutos",
            "traffic_impact": "15% do tráfego",
            "recommended_action": "Contatar NOC imediatamente",
            "noc_contact": "+55 11 9999-9999",
            "peer_contact": "noc@provider.com"
        }
    }
    
    result = await telegram_service.send_alert(alert_data)
    print(f"Resultado: {'✅ Sucesso' if result else '❌ Falha'}")

# Executar teste
asyncio.run(test_custom_alert())
```

### **3. Teste de Status Customizado**
```python
# Teste de status com formatação custom
async def test_custom_status():
    await telegram_service.send_status_update(
        component="Sistema BGP Custom",
        status="healthy",
        details="🚀 Todos os sistemas operacionais! 100% uptime nas últimas 24h."
    )

asyncio.run(test_custom_status())
```

## 🎯 **Exemplos de Customizações Populares**

### **1. Estilo Corporate**
```python
severity_emoji = {
    "critical": "🔴",
    "warning": "🟡", 
    "info": "🟢"
}

# Mensagem formal
message = f"""
<b>BGP NETWORK MONITORING SYSTEM</b>

<b>Alert Classification:</b> {severity.upper()}
<b>Alert Type:</b> {alert_type.replace('_', ' ').title()}
<b>Timestamp:</b> {timestamp}

<b>Technical Details:</b>
{details_text}

<b>Recommended Action:</b>
Please contact Network Operations Center immediately.

<b>Reference ID:</b> BGP-{alert_id}
"""
```

### **2. Estilo Gaming/Tech**
```python
severity_emoji = {
    "critical": "💀",
    "warning": "⚡",
    "info": "🤖"
}

# Mensagem tech
message = f"""
<b>🎮 BGP MONITOR v2.0 🎮</b>

<b>[ ! ]</b> <code>ALERT TRIGGERED</code> <b>[ ! ]</b>

<b>╭─ SYSTEM STATUS</b>
<b>├─</b> Level: <code>{severity.upper()}</code>
<b>├─</b> Type: <code>{alert_type}</code>
<b>╰─</b> Time: <code>{timestamp}</code>

<b>╭─ NETWORK DATA</b>
<b>├─</b> {details_line_1}
<b>├─</b> {details_line_2}
<b>╰─</b> {details_line_3}

<code>>>> MONITORING ACTIVE <<<</code>
"""
```

### **3. Estilo Minimalista**
```python
severity_emoji = {
    "critical": "●",
    "warning": "●",
    "info": "●"
}

# Mensagem clean
message = f"""
<b>BGP Alert</b>

{severity.upper()} • {alert_type.replace('_', ' ')}
{main_message}

{timestamp}
"""
```

---

## 🔧 **Aplicando as Customizações**

1. **Backup do arquivo original:**
```bash
cp /opt/bgp-monitor/app/services/telegram.py /opt/bgp-monitor/app/services/telegram.py.backup
```

2. **Edite o arquivo:**
```bash
nano /opt/bgp-monitor/app/services/telegram.py
```

3. **Teste suas mudanças:**
```bash
./test_telegram_alerts.sh
```

4. **Reinicie o serviço:**
```bash
sudo systemctl restart bgp-monitor
```

---

**🎉 Agora você pode personalizar completamente os alertas do BGP Monitor!**
