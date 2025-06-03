# 📱 Alertas BGP Monitor - Português Brasileiro

## 🎯 **Visão Geral**

O BGP Monitor v1.2.0 oferece um sistema completo de alertas em português brasileiro, incluindo notificações de problemas e recuperação via Telegram.

---

## 🚨 **Tipos de Alertas de Problemas**

### **1. Peer Perdido** (`peer_lost`)
**Quando:** Um peer BGP é perdido ou não está mais acessível
```
🔴 Monitor BGP - Alerta Crítico 🔗

Severidade: CRÍTICO
Tipo: Peer Perdido

Mensagem:
❌ Peer AS64512 não está mais acessível via BGP.

Detalhes:
• Peer: AS64512 - Provedor Exemplo
• Tipo: upstream
• Última Conexão: 01/06/2025 14:30 BRT
• Status: Desconectado há 15 minutos

Horário: 01/06/2025 14:45:00 BRT
```

### **2. Upstreams Insuficientes** (`upstreams_insufficient`)
**Quando:** Número de upstreams BGP está abaixo do mínimo recomendado
```
🟠 Monitor BGP - Alerta Alto 🔗

Severidade: ALTO
Tipo: Upstreams Insuficientes

Mensagem:
⚠️ AS64512 com apenas 1 upstream ativo (mínimo: 2).

Detalhes:
• ASN: AS64512
• Upstreams Ativos: 1
• Upstreams Mínimos: 2
• Upstreams Perdidos: AS174, AS3356
• Redundância: Comprometida

Horário: 01/06/2025 14:45:00 BRT
```

### **3. Prefixo Ausente** (`prefix_missing`)
**Quando:** Um prefixo monitorado não está sendo anunciado
```
🟡 Monitor BGP - Alerta Médio 📡

Severidade: MÉDIO
Tipo: Prefixo Ausente

Mensagem:
📡 Prefixo 203.0.113.0/24 não encontrado na tabela BGP.

Detalhes:
• Prefixo: 203.0.113.0/24
• ASN Origem: AS64512
• Última Visão: 01/06/2025 14:30 BRT
• Caminhos BGP: 0 (anterior: 15)
• Status: Não anunciado

Horário: 01/06/2025 14:45:00 BRT
```

### **4. Latência Alta** (`latency_high`)
**Quando:** Latência para um peer excede o limite configurado
```
🟡 Monitor BGP - Alerta Médio 🌐

Severidade: MÉDIO
Tipo: Performance Degradada

Mensagem:
⚡ Latência alta detectada para AS64512 (850ms).

Detalhes:
• Peer: AS64512 - Provedor Exemplo
• Latência Atual: 850ms
• Limite: 100ms
• Aumento: +750ms (+881%)
• Medições: 5/5 acima do limite

Horário: 01/06/2025 14:45:00 BRT
```

### **5. Instabilidade Detectada** (`instability_detected`)
**Quando:** Instabilidade de roteamento é detectada
```
🟠 Monitor BGP - Alerta Alto 📊

Severidade: ALTO
Tipo: Instabilidade de Roteamento

Mensagem:
📊 Instabilidade de roteamento detectada para AS64512.

Detalhes:
• ASN: AS64512
• Mudanças de Rota: 25 em 5 minutos
• Limite: 10 mudanças/5min
• Prefixos Afetados: 12
• Flapping: Detectado em 3 peers

Horário: 01/06/2025 14:45:00 BRT
```

### **6. Anomalia Detectada** (`anomaly_detected`)
**Quando:** Anomalia estatística é identificada
```
🟠 Monitor BGP - Alerta Alto 📉

Severidade: ALTO
Tipo: Anomalia Estatística

Mensagem:
📉 Anomalia estatística detectada em AS64512.

Detalhes:
• ASN: AS64512
• Métrica Afetada: Número de peers
• Valor Atual: 5
• Valor Esperado: 15 ±3
• Desvio: -67% (10 peers abaixo)
• Confiança: 95%

Horário: 01/06/2025 14:45:00 BRT
```

---

## 🟢 **Tipos de Alertas de Recuperação**

### **1. Peer Recuperado** (`peer_recovered`)
```
🟢 Monitor BGP - Recuperação 🔗

Severidade: INFORMATIVO
Tipo: Peer Recuperado

Mensagem:
🟢 Upstream AS64512 recuperado com sucesso.

Detalhes:
• Peer: AS64512 - Provedor Exemplo
• Tipo: upstream
• Tempo Offline: 47 minutos
• Reconectado: 01/06/2025 14:30 BRT
• Status: Conectividade BGP restaurada

Horário: 01/06/2025 14:30:00 BRT
```

### **2. Upstreams Normalizados** (`upstreams_normalized`)
```
✅ Monitor BGP - Recuperação 🔗

Severidade: INFORMATIVO
Tipo: Redundância Restaurada

Mensagem:
✅ Redundância de upstreams restaurada para AS64512.

Detalhes:
• ASN: AS64512
• Upstreams Ativos: 3
• Upstreams Mínimos: 2
• Recuperados: AS174, AS3356
• Tempo sem Redundância: 23 minutos
• Status: Redundância adequada

Horário: 01/06/2025 14:30:00 BRT
```

### **3. Prefixo Restaurado** (`prefix_restored`)
```
🔄 Monitor BGP - Recuperação 📡

Severidade: INFORMATIVO
Tipo: Prefixo Restaurado

Mensagem:
🔄 Prefixo 203.0.113.0/24 restaurado na tabela BGP.

Detalhes:
• Prefixo: 203.0.113.0/24
• ASN Origem: AS64512
• Tempo Ausente: 15 minutos
• Caminhos BGP Restaurados: 12
• Status: Totalmente propagado

Horário: 01/06/2025 14:30:00 BRT
```

### **4. Latência Normalizada** (`latency_normalized`)
```
⚡ Monitor BGP - Recuperação 🌐

Severidade: INFORMATIVO
Tipo: Performance Normalizada

Mensagem:
🟢 Latência normalizada para AS64512 (45ms).

Detalhes:
• Peer: AS64512 - Provedor Exemplo
• Latência Atual: 45ms
• Latência Anterior: 850ms
• Limite: 100ms
• Melhoria: -94% (805ms de redução)
• Tempo de Problema: 8 minutos

Horário: 01/06/2025 14:30:00 BRT
```

### **5. Instabilidade Resolvida** (`instability_resolved`)
```
📊 Monitor BGP - Recuperação 📈

Severidade: INFORMATIVO
Tipo: Estabilidade Restaurada

Mensagem:
📊 Instabilidade de roteamento resolvida para AS64512.

Detalhes:
• ASN: AS64512
• Mudanças de Rota: 2 em 5 minutos
• Limite: 10 mudanças/5min
• Tempo de Instabilidade: 12 minutos
• Status: Roteamento estável

Horário: 01/06/2025 14:30:00 BRT
```

### **6. Anomalia Resolvida** (`anomaly_resolved`)
```
📈 Monitor BGP - Recuperação 📊

Severidade: INFORMATIVO
Tipo: Anomalia Resolvida

Mensagem:
📈 Anomalia estatística resolvida em AS64512.

Detalhes:
• ASN: AS64512
• Métrica Normalizada: Número de peers
• Valor Atual: 14
• Valor Esperado: 15 ±3
• Tempo de Anomalia: 25 minutos
• Status: Dentro da normalidade

Horário: 01/06/2025 14:30:00 BRT
```

---

## ⚙️ **Configuração de Alertas**

### **Níveis de Severidade**
- 🔴 **CRÍTICO**: Problemas que afetam conectividade
- 🟠 **ALTO**: Problemas que afetam redundância/performance
- 🟡 **MÉDIO**: Problemas menores mas importantes
- 🔵 **BAIXO**: Avisos informativos
- 🟢 **INFORMATIVO**: Recuperações e normalizações

### **Configuração no .env**
```bash
# Configurações Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id

# Configurações de Limites
BGP_LATENCY_THRESHOLD=100
BGP_MIN_UPSTREAMS=2
BGP_INSTABILITY_THRESHOLD=10
```

---

## 🧪 **Testando Alertas**

### **Teste Manual via API**
```bash
# Testar alerta de problema
curl -X POST http://localhost:8000/test/alert/peer_lost

# Testar alerta de recuperação
curl -X POST http://localhost:8000/test/recovery/peer

# Testar todos os tipos
curl -X POST http://localhost:8000/test/recovery/all
```

### **Scripts de Teste**
```bash
# Testar endpoints
./scripts/teste_endpoints_recuperacao.sh

# Testar detecção automática
./scripts/teste_deteccao_recuperacao.sh

# Simular alertas completos
./scripts/teste_alarmes_recuperacao_pt_br.sh
```

---

## 📊 **Monitoramento de Alertas**

### **Logs de Alertas**
```bash
# Ver todos os alertas
tail -f logs/bgp_monitor.log | grep -i alert

# Filtrar por tipo
tail -f logs/bgp_monitor.log | grep "peer_lost"

# Ver apenas recuperações
tail -f logs/bgp_monitor.log | grep -i recovery
```

### **Métricas via API**
```bash
# Status geral
curl http://localhost:8000/alerts

# Tipos de alertas
curl http://localhost:8000/alerts/types

# Exemplos de recuperação
curl http://localhost:8000/alerts/recovery/examples
```

---

## 🔧 **Personalização**

### **Modificar Mensagens**
As mensagens podem ser personalizadas em:
- `/app/services/telegram.py` - Templates das mensagens
- `/app/config/translations/pt_br.json` - Traduções

### **Ajustar Limites**
Configure os limites de alertas em:
- `/app/core/config.py` - Configurações globais
- `.env` - Variáveis de ambiente

### **Adicionar Novos Tipos**
Para adicionar novos tipos de alertas:
1. Adicione o tipo em `telegram.py`
2. Implemente a lógica de detecção no monitor apropriado
3. Adicione o endpoint de teste em `api/main.py`

---

**Sistema de Alertas BGP Monitor v1.2.0 - Completo em Português Brasileiro** 🇧🇷