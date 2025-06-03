# 🔧 Implementação de Alertas PT-BR - BGP Monitor

## 📋 **Guia de Implementação Técnica**

Este documento detalha como implementar e personalizar o sistema de alertas em português brasileiro do BGP Monitor v1.2.0.

---

## 🏗️ **Arquitetura do Sistema de Alertas**

### **Componentes Principais**

```
BGP Monitor v1.2.0
├── Detectores de Problemas
│   ├── PeerMonitor (peers/upstreams/latência)
│   ├── PrefixMonitor (prefixos ausentes)
│   └── AnomalyDetector (anomalias/instabilidade)
├── Sistema de Alertas
│   ├── TelegramService (formatação/envio)
│   ├── Templates PT-BR (mensagens)
│   └── API Endpoints (testes)
└── Detectores de Recuperação
    ├── Recovery Detection (automática)
    ├── Cache de Alertas (histórico)
    └── Notificações Positivas (PT-BR)
```

---

## 🔨 **Implementação Passo a Passo**

### **1. Configuração Base**

#### **A. Configurar Token do Telegram**
```bash
# Editar arquivo .env
cp .env.example .env
nano .env

# Adicionar configurações
TELEGRAM_BOT_TOKEN=seu_bot_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

#### **B. Configurar Limites de Alerta**
```bash
# Configurações de sensibilidade
BGP_LATENCY_THRESHOLD=100          # Limite de latência (ms)
BGP_MIN_UPSTREAMS=2                # Mínimo de upstreams
BGP_INSTABILITY_THRESHOLD=10       # Mudanças/5min para instabilidade
BGP_ANOMALY_CONFIDENCE=0.95        # Confiança para anomalias (95%)
```

### **2. Personalização de Mensagens**

#### **A. Modificar Templates no TelegramService**

**Arquivo:** `/app/services/telegram.py`

```python
# Adicionar novo tipo de alerta
ALERT_MESSAGES = {
    # Alertas existentes...
    "novo_tipo_alerta": {
        "emoji": "🆕",
        "title": "Novo Tipo de Alerta",
        "template": "🆕 {message}",
        "severity": "MÉDIO"
    }
}

# Adicionar template de recuperação
RECOVERY_MESSAGES = {
    # Recuperações existentes...
    "novo_tipo_recuperado": {
        "emoji": "✨",
        "title": "Novo Tipo Recuperado",
        "template": "✨ {message}",
        "severity": "INFORMATIVO"
    }
}
```

#### **B. Personalizar Detalhes por Tipo**

```python
def _format_details(self, alert_type: str, details: Dict) -> str:
    """Formatar detalhes específicos por tipo de alerta"""
    
    if alert_type == "novo_tipo_alerta":
        return f"""• Parâmetro 1: {details.get('param1', 'N/A')}
• Parâmetro 2: {details.get('param2', 'N/A')}
• Status: {details.get('status', 'Desconhecido')}"""
    
    # Casos existentes...
    return self._format_default_details(details)
```

### **3. Implementar Novo Monitor**

#### **A. Criar Novo Detector**

**Arquivo:** `/app/services/novo_monitor.py`

```python
import asyncio
from datetime import datetime
from typing import Dict, Any
from .telegram import TelegramService

class NovoMonitor:
    def __init__(self):
        self.telegram = TelegramService()
        self.alert_cache = {}
        
    async def check_novo_problema(self, asn: str) -> bool:
        """Detectar novo tipo de problema"""
        try:
            # Lógica de detecção aqui
            problema_detectado = await self._verificar_condicao(asn)
            
            if problema_detectado and asn not in self.alert_cache:
                # Enviar alerta
                await self.telegram.send_alert(
                    alert_type="novo_tipo_alerta",
                    message=f"Novo problema detectado em {asn}",
                    severity="MÉDIO",
                    details={
                        "asn": asn,
                        "param1": "valor1",
                        "param2": "valor2",
                        "detected_at": datetime.now().isoformat()
                    }
                )
                self.alert_cache[asn] = datetime.now()
                return True
                
        except Exception as e:
            print(f"Erro ao verificar {asn}: {e}")
        
        return False
    
    async def check_novo_recuperacao(self, asn: str) -> bool:
        """Detectar recuperação do problema"""
        try:
            if asn in self.alert_cache:
                problema_resolvido = await self._verificar_resolucao(asn)
                
                if problema_resolvido:
                    problema_inicio = self.alert_cache[asn]
                    duracao = datetime.now() - problema_inicio
                    
                    # Enviar alerta de recuperação
                    await self.telegram.send_recovery_alert(
                        alert_type="novo_tipo_recuperado",
                        message=f"Problema resolvido em {asn}",
                        details={
                            "asn": asn,
                            "downtime": self._format_duration(duracao),
                            "resolved_at": datetime.now().isoformat()
                        }
                    )
                    
                    # Remover do cache
                    del self.alert_cache[asn]
                    return True
                    
        except Exception as e:
            print(f"Erro ao verificar recuperação {asn}: {e}")
        
        return False
    
    async def _verificar_condicao(self, asn: str) -> bool:
        """Implementar lógica específica de detecção"""
        # Sua lógica aqui
        return False
    
    async def _verificar_resolucao(self, asn: str) -> bool:
        """Implementar lógica específica de recuperação"""
        # Sua lógica aqui
        return False
    
    def _format_duration(self, duration) -> str:
        """Formatar duração em português"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours} horas e {minutes} minutos"
        else:
            return f"{minutes} minutos"
```

#### **B. Integrar no Scheduler**

**Arquivo:** `/app/scheduler.py`

```python
from app.services.novo_monitor import NovoMonitor

class BGPScheduler:
    def __init__(self):
        # Monitores existentes...
        self.novo_monitor = NovoMonitor()
    
    async def run_monitoring_cycle(self):
        """Executar ciclo completo de monitoramento"""
        try:
            # Monitoramentos existentes...
            
            # Novo monitoramento
            for asn in self.monitored_asns:
                await self.novo_monitor.check_novo_problema(asn)
                await self.novo_monitor.check_novo_recuperacao(asn)
                
        except Exception as e:
            logger.error(f"Erro no ciclo de monitoramento: {e}")
```

### **4. Adicionar Endpoints de Teste**

#### **A. Endpoints na API**

**Arquivo:** `/app/api/main.py`

```python
@app.post("/test/novo_alerta")
async def test_novo_alerta():
    """Testar novo tipo de alerta"""
    telegram = TelegramService()
    
    await telegram.send_alert(
        alert_type="novo_tipo_alerta",
        message="Teste de novo alerta implementado",
        severity="MÉDIO",
        details={
            "asn": "AS64512",
            "param1": "Valor de teste",
            "param2": "Outro valor",
            "test": True
        }
    )
    
    return {"status": "Alerta de teste enviado"}

@app.post("/test/recovery/novo_tipo")
async def test_novo_recovery():
    """Testar recuperação do novo tipo"""
    telegram = TelegramService()
    
    await telegram.send_recovery_alert(
        alert_type="novo_tipo_recuperado",
        message="Teste de recuperação implementado",
        details={
            "asn": "AS64512",
            "downtime": "15 minutos",
            "resolved_at": datetime.now().strftime("%d/%m/%Y %H:%M BRT"),
            "test": True
        }
    )
    
    return {"status": "Alerta de recuperação enviado"}
```

### **5. Implementar Traduções**

#### **A. Adicionar ao arquivo de traduções**

**Arquivo:** `/app/config/translations/pt_br.json`

```json
{
  "alert_types": {
    "existing_types": "...",
    "novo_tipo_alerta": "Novo Tipo de Alerta",
    "novo_tipo_recuperado": "Novo Tipo Recuperado"
  },
  "messages": {
    "novo_tipo": {
      "detected": "Novo tipo de problema detectado",
      "resolved": "Novo tipo de problema resolvido",
      "description": "Descrição do novo tipo"
    }
  }
}
```

#### **B. Usar traduções no código**

```python
import json

class TranslationService:
    def __init__(self):
        with open('/app/config/translations/pt_br.json', 'r') as f:
            self.translations = json.load(f)
    
    def get_alert_type_name(self, alert_type: str) -> str:
        return self.translations.get("alert_types", {}).get(alert_type, alert_type)
    
    def get_message_template(self, message_key: str) -> str:
        return self.translations.get("messages", {}).get(message_key, "")
```

---

## 🧪 **Testes e Validação**

### **1. Script de Teste Personalizado**

**Arquivo:** `scripts/teste_novo_monitor.sh`

```bash
#!/bin/bash
# Teste do novo monitor

echo "🧪 Testando Novo Monitor BGP"
echo "================================"

# Testar alerta
echo "Testando alerta..."
curl -X POST http://localhost:8000/test/novo_alerta
echo

# Testar recuperação  
echo "Testando recuperação..."
curl -X POST http://localhost:8000/test/recovery/novo_tipo
echo

# Verificar logs
echo "Verificando logs..."
tail -n 5 /opt/bgp-monitor/logs/bgp_monitor.log | grep -i "novo"

echo "✅ Teste concluído"
```

### **2. Teste de Integração**

```python
import asyncio
from app.services.novo_monitor import NovoMonitor

async def test_integration():
    """Teste de integração do novo monitor"""
    monitor = NovoMonitor()
    
    # Testar detecção
    print("Testando detecção...")
    result = await monitor.check_novo_problema("AS64512")
    print(f"Detecção: {'✅' if result else '❌'}")
    
    # Simular problema ativo
    monitor.alert_cache["AS64512"] = datetime.now()
    
    # Testar recuperação
    print("Testando recuperação...")
    result = await monitor.check_novo_recuperacao("AS64512")
    print(f"Recuperação: {'✅' if result else '❌'}")

if __name__ == "__main__":
    asyncio.run(test_integration())
```

---

## 🔧 **Personalização Avançada**

### **1. Alertas Condicionais**

```python
def should_send_alert(self, alert_type: str, asn: str, details: Dict) -> bool:
    """Decidir se deve enviar alerta baseado em condições"""
    
    # Não alertar em horários específicos
    current_hour = datetime.now().hour
    if current_hour >= 23 or current_hour <= 6:  # 23h às 6h
        if alert_type in ["latency_high", "instability_detected"]:
            return False
    
    # Não alertar sobre ASNs específicos
    excluded_asns = ["AS65000", "AS65001"]
    if asn in excluded_asns:
        return False
    
    # Apenas alertar se valor exceder threshold significativo
    if alert_type == "latency_high":
        latency = details.get("current_latency", 0)
        if latency < 200:  # Menos que 200ms não é crítico
            return False
    
    return True
```

### **2. Múltiplos Canais de Notificação**

```python
class NotificationService:
    def __init__(self):
        self.telegram = TelegramService()
        self.email = EmailService()  # Implementar se necessário
        
    async def send_notification(self, alert_type: str, severity: str, **kwargs):
        """Enviar notificação por múltiplos canais"""
        
        # Sempre enviar via Telegram
        await self.telegram.send_alert(alert_type, severity=severity, **kwargs)
        
        # Enviar email apenas para alertas críticos
        if severity == "CRÍTICO":
            await self.email.send_alert(alert_type, severity=severity, **kwargs)
        
        # Log local sempre
        self._log_alert(alert_type, severity, kwargs)
```

### **3. Relatórios Periódicos**

```python
class ReportService:
    def __init__(self):
        self.telegram = TelegramService()
    
    async def send_daily_summary(self):
        """Enviar resumo diário"""
        summary = await self._generate_daily_summary()
        
        message = f"""📊 Resumo BGP Monitor - {datetime.now().strftime('%d/%m/%Y')}

📈 Estatísticas do Dia:
• Alertas Enviados: {summary['total_alerts']}
• Recuperações: {summary['recoveries']}
• Tempo Médio de Resolução: {summary['avg_resolution_time']}
• ASNs Monitorados: {summary['monitored_asns']}

🔴 Alertas Críticos: {summary['critical_alerts']}
🟠 Alertas Altos: {summary['high_alerts']}
🟡 Alertas Médios: {summary['medium_alerts']}

Status: {'✅ Tudo funcionando' if summary['all_clear'] else '⚠️ Alguns problemas ativos'}"""

        await self.telegram.send_message(message)
```

---

## 📊 **Monitoramento e Métricas**

### **1. Métricas de Alertas**

```python
class AlertMetrics:
    def __init__(self):
        self.metrics = {
            "alerts_sent": 0,
            "recoveries_detected": 0,
            "false_positives": 0,
            "avg_resolution_time": 0
        }
    
    def record_alert(self, alert_type: str):
        """Registrar envio de alerta"""
        self.metrics["alerts_sent"] += 1
        # Salvar em banco de dados se necessário
    
    def record_recovery(self, alert_type: str, duration: timedelta):
        """Registrar recuperação"""
        self.metrics["recoveries_detected"] += 1
        # Calcular tempo médio de resolução
        self._update_avg_resolution_time(duration)
    
    def get_metrics_summary(self) -> Dict:
        """Obter resumo das métricas"""
        return self.metrics.copy()
```

### **2. Dashboard de Status**

```python
@app.get("/dashboard/alerts")
async def get_alerts_dashboard():
    """Dashboard de alertas em tempo real"""
    metrics = AlertMetrics()
    
    return {
        "status": "online",
        "last_update": datetime.now().isoformat(),
        "metrics": metrics.get_metrics_summary(),
        "active_alerts": await get_active_alerts(),
        "recent_recoveries": await get_recent_recoveries(hours=24)
    }
```

---

## 🚀 **Deploy e Manutenção**

### **1. Checklist de Deploy**

```bash
# 1. Verificar configurações
./scripts/verificar_dependencias.py

# 2. Testar conexão Telegram
curl -X POST http://localhost:8000/test/telegram

# 3. Testar todos os tipos de alerta
./scripts/teste_endpoints_recuperacao.sh

# 4. Verificar logs
tail -f logs/bgp_monitor.log

# 5. Monitorar performance
curl http://localhost:8000/health
```

### **2. Manutenção Preventiva**

```bash
# Script de manutenção diária
#!/bin/bash

# Limpar logs antigos (manter 30 dias)
find /opt/bgp-monitor/logs -name "*.log" -mtime +30 -delete

# Verificar espaço em disco
df -h | grep -E "(80%|90%|100%)" && echo "⚠️ Disco quase cheio"

# Testar conectividade Telegram
curl -s -X POST http://localhost:8000/test/telegram > /dev/null || echo "❌ Telegram não funciona"

# Verificar processes
ps aux | grep "bgp-monitor" | grep -v grep || echo "❌ BGP Monitor não está rodando"

echo "✅ Manutenção concluída - $(date)"
```

---

## 📖 **Documentação Adicional**

### **Arquivos de Referência**
- `/docs/API.md` - Documentação completa da API
- `/docs/CONFIGURATION.md` - Guia de configuração
- `/docs/TROUBLESHOOTING.md` - Solução de problemas
- `/scripts/` - Scripts de teste e utilitários

### **Recursos Úteis**
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [RIPE Stat API](https://stat.ripe.net/docs/data_api)
- [BGP RFCs](https://tools.ietf.org/rfc/)

---

**Implementação Técnica BGP Monitor v1.2.0 - Sistema Completo em PT-BR** 🇧🇷