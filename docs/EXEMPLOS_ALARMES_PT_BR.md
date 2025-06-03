# 📱 Exemplos de Alarmes BGP Monitor - PT-BR

## 🎯 **Exemplos Práticos de Alertas**

Esta seção contém exemplos reais de como os alertas aparecem no Telegram em situações do mundo real.

---

## 🚨 **Cenários de Problemas**

### **Exemplo 1: Perda de Conectividade com Provedor Principal**

**Situação:** O link com o provedor principal (AS174 - Cogent) falha às 14:35

```
🔴 Monitor BGP - Alerta Crítico 🔗

Severidade: CRÍTICO
Tipo: Peer Perdido

Mensagem:
❌ Peer AS174 não está mais acessível via BGP.

Detalhes:
• Peer: AS174 - Cogent Communications
• Tipo: upstream
• Última Conexão: 03/06/2025 14:35 BRT
• Status: Desconectado há 2 minutos
• Prefixos Afetados: ~150.000

Horário: 03/06/2025 14:37:00 BRT
```

**Consequência:** Após 3 minutos, segundo alerta:

```
🟠 Monitor BGP - Alerta Alto 🔗

Severidade: ALTO
Tipo: Upstreams Insuficientes

Mensagem:
⚠️ AS64512 com apenas 1 upstream ativo (mínimo: 2).

Detalhes:
• ASN: AS64512
• Upstreams Ativos: 1 (AS3356)
• Upstreams Mínimos: 2
• Upstreams Perdidos: AS174
• Redundância: Comprometida

Horário: 03/06/2025 14:40:00 BRT
```

---

### **Exemplo 2: Problema de Anúncio de Prefixo**

**Situação:** Prefixo da empresa para de ser anunciado devido a erro de configuração

```
🟡 Monitor BGP - Alerta Médio 📡

Severidade: MÉDIO
Tipo: Prefixo Ausente

Mensagem:
📡 Prefixo 198.51.100.0/24 não encontrado na tabela BGP.

Detalhes:
• Prefixo: 198.51.100.0/24
• ASN Origem: AS64512
• Última Visão: 03/06/2025 09:30 BRT
• Caminhos BGP: 0 (anterior: 25)
• Status: Não anunciado há 5 horas

Horário: 03/06/2025 14:30:00 BRT
```

---

### **Exemplo 3: Degradação de Performance**

**Situação:** Latência alta devido a congestionamento de rede

```
🟡 Monitor BGP - Alerta Médio 🌐

Severidade: MÉDIO
Tipo: Performance Degradada

Mensagem:
⚡ Latência alta detectada para AS3356 (450ms).

Detalhes:
• Peer: AS3356 - Level3 Communications
• Latência Atual: 450ms
• Limite: 100ms
• Aumento: +350ms (+350%)
• Medições: 8/10 acima do limite
• Tendência: Subindo

Horário: 03/06/2025 14:30:00 BRT
```

---

### **Exemplo 4: Instabilidade de Roteamento**

**Situação:** Flapping de rotas causado por problema em equipamento

```
🟠 Monitor BGP - Alerta Alto 📊

Severidade: ALTO
Tipo: Instabilidade de Roteamento

Mensagem:
📊 Instabilidade de roteamento detectada para AS64512.

Detalhes:
• ASN: AS64512
• Mudanças de Rota: 45 em 5 minutos
• Limite: 10 mudanças/5min
• Prefixos Afetados: 8
• Peers com Flapping: AS174, AS3356
• Duração: 12 minutos

Horário: 03/06/2025 14:30:00 BRT
```

---

## 🟢 **Cenários de Recuperação**

### **Exemplo 1: Restauração de Conectividade**

**Situação:** Após 47 minutos, o link com AS174 volta ao normal

```
🟢 Monitor BGP - Recuperação 🔗

Severidade: INFORMATIVO
Tipo: Peer Recuperado

Mensagem:
🟢 Upstream AS174 recuperado com sucesso.

Detalhes:
• Peer: AS174 - Cogent Communications
• Tipo: upstream
• Tempo Offline: 47 minutos
• Reconectado: 03/06/2025 15:22 BRT
• Status: Conectividade BGP restaurada
• Prefixos Restaurados: ~150.000

Horário: 03/06/2025 15:22:00 BRT
```

**Consequência:** 2 minutos depois, redundância restaurada:

```
✅ Monitor BGP - Recuperação 🔗

Severidade: INFORMATIVO
Tipo: Redundância Restaurada

Mensagem:
✅ Redundância de upstreams restaurada para AS64512.

Detalhes:
• ASN: AS64512
• Upstreams Ativos: 2
• Upstreams Mínimos: 2
• Recuperados: AS174
• Tempo sem Redundância: 49 minutos
• Status: Redundância adequada

Horário: 03/06/2025 15:24:00 BRT
```

---

### **Exemplo 2: Prefixo Restaurado**

**Situação:** Configuração corrigida, prefixo volta a ser anunciado

```
🔄 Monitor BGP - Recuperação 📡

Severidade: INFORMATIVO
Tipo: Prefixo Restaurado

Mensagem:
🔄 Prefixo 198.51.100.0/24 restaurado na tabela BGP.

Detalhes:
• Prefixo: 198.51.100.0/24
• ASN Origem: AS64512
• Tempo Ausente: 5 horas e 23 minutos
• Caminhos BGP Restaurados: 28
• Status: Totalmente propagado
• Visibilidade Global: 98%

Horário: 03/06/2025 14:53:00 BRT
```

---

### **Exemplo 3: Normalização de Latência**

**Situação:** Congestionamento resolvido, latência volta ao normal

```
⚡ Monitor BGP - Recuperação 🌐

Severidade: INFORMATIVO
Tipo: Performance Normalizada

Mensagem:
🟢 Latência normalizada para AS3356 (65ms).

Detalhes:
• Peer: AS3356 - Level3 Communications
• Latência Atual: 65ms
• Latência Anterior: 450ms
• Limite: 100ms
• Melhoria: -86% (385ms de redução)
• Tempo de Problema: 25 minutos

Horário: 03/06/2025 14:55:00 BRT
```

---

### **Exemplo 4: Estabilidade Restaurada**

**Situação:** Equipamento corrigido, rotas se estabilizam

```
📊 Monitor BGP - Recuperação 📈

Severidade: INFORMATIVO
Tipo: Estabilidade Restaurada

Mensagem:
📊 Instabilidade de roteamento resolvida para AS64512.

Detalhes:
• ASN: AS64512
• Mudanças de Rota: 3 em 5 minutos
• Limite: 10 mudanças/5min
• Tempo de Instabilidade: 1 hora e 15 minutos
• Prefixos Estabilizados: 8
• Status: Roteamento estável

Horário: 03/06/2025 15:45:00 BRT
```

---

## 🚨 **Cenários Complexos**

### **Exemplo: Incidente Múltiplo - DDoS Attack**

**14:30** - Início do ataque:
```
🟡 Monitor BGP - Alerta Médio 🌐

Severidade: MÉDIO
Tipo: Performance Degradada

Mensagem:
⚡ Latência alta detectada para múltiplos peers.

Detalhes:
• Peers Afetados: AS174, AS3356, AS6939
• Latência Média: 890ms
• Limite: 100ms
• Tipo de Problema: Possível sobrecarga
```

**14:35** - Escalação:
```
🟠 Monitor BGP - Alerta Alto 📊

Severidade: ALTO
Tipo: Instabilidade de Roteamento

Mensagem:
📊 Instabilidade massiva detectada - possível ataque DDoS.

Detalhes:
• Mudanças de Rota: 150 em 5 minutos
• Peers Afetados: 6
• Prefixos com Flapping: 25
• Tráfego Anômalo: Detectado
```

**14:40** - Perda de conectividade:
```
🔴 Monitor BGP - Alerta Crítico 🔗

Severidade: CRÍTICO
Tipo: Peer Perdido

Mensagem:
❌ Múltiplos peers perdidos simultaneamente.

Detalhes:
• Peers Perdidos: AS174, AS6939
• Upstreams Restantes: 1 (AS3356)
• Causa Provável: Ataque DDoS
• Ação: Ativando mitigação
```

**15:20** - Início da recuperação:
```
🟢 Monitor BGP - Recuperação 🔗

Severidade: INFORMATIVO
Tipo: Peer Recuperado

Mensagem:
🟢 Primeiro peer recuperado após mitigação DDoS.

Detalhes:
• Peer: AS6939 - Hurricane Electric
• Tempo Offline: 40 minutos
• Status: Mitigação DDoS ativa
• Conectividade: Restaurada parcialmente
```

---

## 📊 **Tipos de Anomalias Estatísticas**

### **Exemplo: Hijack de Prefixo Detectado**

```
🔴 Monitor BGP - Alerta Crítico 📉

Severidade: CRÍTICO
Tipo: Anomalia Crítica

Mensagem:
🚨 Possível hijack detectado para 198.51.100.0/24!

Detalhes:
• Prefixo: 198.51.100.0/24
• ASN Legítimo: AS64512
• ASN Anunciando: AS65001
• Caminhos Suspeitos: 15
• Confiança: 98%
• Ação: Investigação urgente necessária

Horário: 03/06/2025 16:45:00 BRT
```

### **Exemplo: Route Leak Detectado**

```
🟠 Monitor BGP - Alerta Alto 📉

Severidade: ALTO
Tipo: Anomalia de Roteamento

Mensagem:
📉 Route leak detectado envolvendo AS64512.

Detalhes:
• Prefixos Vazados: 1.200
• AS Fonte: AS65002
• AS Destino: Internet global
• Tipo: Customer-to-Provider leak
• Impacto: Roteamento subótimo
• Duração: 15 minutos

Horário: 03/06/2025 17:30:00 BRT
```

---

## 🔧 **Configurações de Exemplo**

### **Configuração Conservadora (Mais Alertas)**
```bash
BGP_LATENCY_THRESHOLD=50          # 50ms
BGP_MIN_UPSTREAMS=3               # 3 upstreams mínimos
BGP_INSTABILITY_THRESHOLD=5       # 5 mudanças/5min
BGP_ANOMALY_SENSITIVITY=0.8       # Alta sensibilidade
```

### **Configuração Balanceada (Padrão)**
```bash
BGP_LATENCY_THRESHOLD=100         # 100ms
BGP_MIN_UPSTREAMS=2               # 2 upstreams mínimos
BGP_INSTABILITY_THRESHOLD=10      # 10 mudanças/5min
BGP_ANOMALY_SENSITIVITY=0.9       # Sensibilidade normal
```

### **Configuração Relaxada (Menos Alertas)**
```bash
BGP_LATENCY_THRESHOLD=200         # 200ms
BGP_MIN_UPSTREAMS=1               # 1 upstream mínimo
BGP_INSTABILITY_THRESHOLD=20      # 20 mudanças/5min
BGP_ANOMALY_SENSITIVITY=0.95      # Baixa sensibilidade
```

---

## 📱 **Formatação das Mensagens**

### **Estrutura Padrão**
```
[Emoji de Status] Monitor BGP - [Tipo] [Emoji do Contexto]

Severidade: [NÍVEL]
Tipo: [Descrição do Tipo]

Mensagem:
[Emoji] [Mensagem principal em português]

Detalhes:
• [Item 1]: [Valor]
• [Item 2]: [Valor]
• [Item N]: [Valor]

Horário: [DD/MM/AAAA HH:MM:SS BRT]
```

### **Emojis por Tipo de Alerta**
- 🔴 Crítico - Problemas que afetam conectividade
- 🟠 Alto - Problemas de redundância
- 🟡 Médio - Problemas menores
- 🟢 Recuperação - Problemas resolvidos
- ✅ Normalização - Retorno ao normal
- 🔄 Restauração - Dados/conectividade restaurados

---

**BGP Monitor v1.2.0 - Exemplos Reais de Alertas em Português Brasileiro** 🇧🇷