# 📱 BGP Monitor - Exemplos de Alarmes PT-BR para Telegram

Este documento apresenta todos os tipos de alarmes do BGP Monitor em português brasileiro, mantendo a objetividade técnica e profissionalismo necessários para operações de rede.

---

## 🚨 **1. ALARME DE PERDA DE PEER BGP - CRÍTICO**

```
🚨 Monitor BGP - Alerta 🛑

Severidade: CRÍTICA
Tipo: Perda de Peer BGP

Mensagem:
🛑 Perda de upstream AS18881 detectada.

Detalhes:
• Peer Perdido: AS18881
• Tipo de Relacionamento: upstream
• Impacto: Alta disponibilidade comprometida

Horário: 01/06/2025 14:30:00 BRT
```

---

## ⚠️ **2. ALARME DE PERDA DE PEER BGP - AVISO**

```
⚠️ Monitor BGP - Alerta 🛑

Severidade: AVISO
Tipo: Perda de Peer BGP

Mensagem:
🛑 Perda de peer AS64512 detectada.

Detalhes:
• Peer Perdido: AS64512
• Tipo de Relacionamento: peer
• Impacto: Redundância reduzida

Horário: 01/06/2025 14:30:00 BRT
```

---

## 🚨 **3. ALARME DE UPSTREAMS INSUFICIENTES**

```
🚨 Monitor BGP - Alerta 📊

Severidade: CRÍTICA
Tipo: Conectividade Upstream

Mensagem:
📊 Número insuficiente de upstreams ativos (2/3 mínimo).

Detalhes:
• Upstreams Ativos: 2
• Mínimo Configurado: 3
• Upstreams Perdidos: AS174, AS3356
• Risco: Dependência excessiva de provedores

Horário: 01/06/2025 14:30:00 BRT
```

---

## 🚨 **4. ALARME DE PREFIXO AUSENTE**

```
🚨 Monitor BGP - Alerta 📡

Severidade: CRÍTICA
Tipo: Prefixo Ausente

Mensagem:
📡 Prefixo crítico 203.0.113.0/24 não visível na tabela BGP.

Detalhes:
• Prefixo: 203.0.113.0/24
• ASN Origem: AS65001
• Última Visibilidade: há 5 minutos
• Impacto: Serviços indisponíveis

Horário: 01/06/2025 14:30:00 BRT
```

---

## 🚨 **5. ALARME DE VAZAMENTO DE ROTA**

```
🚨 Monitor BGP - Alerta 🔗

Severidade: CRÍTICA
Tipo: Vazamento de Rota

Mensagem:
🔗 Possível vazamento detectado: prefixo 198.51.100.0/24 anunciado indevidamente.

Detalhes:
• Prefixo: 198.51.100.0/24
• ASN Origem Legítima: AS65002
• ASNs Suspeitos: AS65003, AS65004
• Tipo: Route leak através de peer
• Ação: Verificar filtros BGP

Horário: 01/06/2025 14:30:00 BRT
```

---

## ⚠️ **6. ALARME DE LATÊNCIA ELEVADA**

```
⚠️ Monitor BGP - Alerta 🌐

Severidade: AVISO
Tipo: Performance de Rede

Mensagem:
🌐 Latência elevada detectada para AS7018 (150ms).

Detalhes:
• Peer Afetado: AS7018
• Latência Atual: 150ms
• Limite Configurado: 100ms
• Tendência: Aumentando nos últimos 10 minutos
• Recomendação: Monitorar conectividade

Horário: 01/06/2025 14:30:00 BRT
```

---

## ⚠️ **7. ALARME DE VALIDAÇÃO IRR**

```
⚠️ Monitor BGP - Alerta 📋

Severidade: AVISO
Tipo: Validação IRR

Mensagem:
📋 Anúncio BGP não conforme com registro IRR detectado.

Detalhes:
• Prefixo: 192.0.2.0/24
• ASN Anunciante: AS65005
• Status IRR: Não registrado/conflitante
• Base IRR Consultada: RADB, RIPE
• Ação Sugerida: Verificar autorização de anúncio

Horário: 01/06/2025 14:30:00 BRT
```

---

## 🚨 **8. ANOMALIA ESTATÍSTICA - AUMENTO SÚBITO (CRÍTICA)**

```
🚨 Monitor BGP - Alerta 📊

Severidade: CRÍTICA
Tipo: Anomalia Estatística

Mensagem:
📊 Aumento súbito de 500% nos anúncios BGP detectado.

Detalhes:
• Métrica: Número de anúncios BGP
• Variação: +500% (de 1.000 para 6.000/hora)
• Janela Temporal: Últimos 15 minutos
• Desvio Padrão: 8.5σ (muito além do normal)
• Possíveis Causas: Route leak, ataque, falha de filtro

Horário: 01/06/2025 14:30:00 BRT
```

---

## ⚠️ **9. ANOMALIA ESTATÍSTICA - DIMINUIÇÃO SÚBITA (AVISO)**

```
⚠️ Monitor BGP - Alerta 📊

Severidade: AVISO
Tipo: Anomalia Estatística

Mensagem:
📊 Diminuição anômala de 40% nos prefixos anunciados.

Detalhes:
• Métrica: Prefixos únicos anunciados
• Variação: -40% (de 500 para 300 prefixos)
• Janela Temporal: Últimas 2 horas
• Desvio Padrão: 3.2σ
• Possível Causa: Falha de configuração ou conectividade

Horário: 01/06/2025 14:30:00 BRT
```

---

## 🚨 **10. INSTABILIDADE DE ROTEAMENTO (CRÍTICA)**

```
🚨 Monitor BGP - Alerta 🔄

Severidade: CRÍTICA
Tipo: Instabilidade de Roteamento

Mensagem:
🔄 Instabilidade crítica: 50 mudanças de rota em 5 minutos.

Detalhes:
• Prefixos Afetados: 25 prefixos únicos
• Mudanças de Rota: 50 nos últimos 5 minutos
• Limite Normal: <10 mudanças/5min
• ASNs Envolvidos: AS65001, AS65002, AS65003
• Impacto: Degradação severa da convergência

Horário: 01/06/2025 14:30:00 BRT
```

---

## ⚠️ **11. INSTABILIDADE DE ROTEAMENTO (AVISO)**

```
⚠️ Monitor BGP - Alerta 🔄

Severidade: AVISO
Tipo: Instabilidade de Roteamento

Mensagem:
🔄 Atividade de roteamento acima do normal detectada.

Detalhes:
• Mudanças de Rota: 25 nos últimos 10 minutos
• Limite Normal: <15 mudanças/10min
• Tendência: Estável após pico inicial
• Recomendação: Monitoramento contínuo

Horário: 01/06/2025 14:30:00 BRT
```

---

## ✅ **12. STATUS DO SISTEMA - SAUDÁVEL**

```
✅ Monitor BGP - Status do Sistema

Componente: Coletor BGP Principal
Status: OPERACIONAL

Detalhes:
• Uptime: 7 dias, 14 horas
• Sessões BGP Ativas: 15/15
• Taxa de Processamento: 1.200 mensagens/seg
• Uso de Memória: 45% (normal)
• Última Verificação: há 30 segundos

Horário: 01/06/2025 14:30:00 BRT
```

---

## ⚠️ **13. STATUS DO SISTEMA - AVISO**

```
⚠️ Monitor BGP - Status do Sistema

Componente: Detector de Anomalias
Status: AVISO

Detalhes:
• Problema: Alto uso de CPU (85%)
• Causa Provável: Processamento de anomalia complexa
• Impacto: Possível atraso na detecção
• Ação Automática: Nenhuma
• Recomendação: Verificar configuração de recursos

Horário: 01/06/2025 14:30:00 BRT
```

---

## ❌ **14. STATUS DO SISTEMA - ERRO**

```
❌ Monitor BGP - Status do Sistema

Componente: Módulo de Validação IRR
Status: ERRO

Detalhes:
• Problema: Falha na conexão com base RADB
• Duração: há 15 minutos
• Impacto: Validação IRR temporariamente indisponível
• Tentativas de Reconexão: 3/5
• Próxima Tentativa: em 2 minutos

Horário: 01/06/2025 14:30:00 BRT
```

---

## ℹ️ **15. RELATÓRIO DIÁRIO**

```
ℹ️ Monitor BGP - Relatório Diário 📈

Período: 31/05/2025 - 01/06/2025

📊 Resumo de Atividades:
• Total de Alarmes: 12
  - Críticos: 3 🚨
  - Avisos: 7 ⚠️
  - Informativos: 2 ℹ️

🛑 Eventos de Peer:
• Perdas de Peer: 2
• Recuperações: 2
• Uptime Médio: 99.8%

📡 Monitoramento de Prefixos:
• Prefixos Monitorados: 150
• Eventos de Ausência: 1
• Vazamentos Detectados: 1

🌐 Performance:
• Latência Média: 85ms
• Picos de Latência: 3
• Qualidade de Rota: Boa

🔄 Estabilidade:
• Mudanças de Rota: 1.250
• Média por Hora: 52
• Convergência: Normal

Status Geral: ✅ OPERACIONAL
```

---

## ℹ️ **16. ANÁLISE DE PEER POR ASN (NOVIDADE v1.0.1)**

```
ℹ️ Monitor BGP - Análise de Peer 🔍

Severidade: INFORMATIVO
Tipo: Análise ASN

Mensagem:
🔍 Análise detalhada do ASN65001 concluída.

Detalhes:
• ASN Analisado: AS65001
• Peers Diretos: 8
• Prefixos Anunciados: 25
• Países de Presença: Brasil, Argentina, Chile
• Relacionamentos:
  - Upstreams: AS174, AS3356, AS1299
  - Peers: AS64512, AS64513
  - Downstreams: AS65010, AS65011

📊 Métricas de Conectividade:
• Diversidade Geográfica: Alta
• Redundância: Adequada
• Qualidade das Rotas: Boa

Horário: 01/06/2025 14:30:00 BRT
```

---

## 🟢 **ALARMES DE RECUPERAÇÃO**

### ✅ **17. PEER RECUPERADO - UPSTREAM**

```
✅ Monitor BGP - Recuperação 🛑

Severidade: INFORMATIVO
Tipo: Peer Recuperado

Mensagem:
🟢 Upstream AS18881 recuperado com sucesso.

Detalhes:
• Peer Recuperado: AS18881
• Tipo de Relacionamento: upstream
• Tempo de Indisponibilidade: 15 minutos
• Status: Conectividade restaurada
• Impacto: Alta disponibilidade normalizada

Horário: 01/06/2025 14:45:00 BRT
```

---

### ✅ **18. PEER RECUPERADO - PEER/CUSTOMER**

```
✅ Monitor BGP - Recuperação 🛑

Severidade: INFORMATIVO
Tipo: Peer Recuperado

Mensagem:
🟢 Peer AS64512 recuperado com sucesso.

Detalhes:
• Peer Recuperado: AS64512
• Tipo de Relacionamento: peer
• Tempo de Indisponibilidade: 8 minutos
• Status: Conectividade restaurada
• Impacto: Redundância normalizada

Horário: 01/06/2025 14:45:00 BRT
```

---

### ✅ **19. UPSTREAMS NORMALIZADOS**

```
✅ Monitor BGP - Recuperação 📊

Severidade: INFORMATIVO
Tipo: Conectividade Normalizada

Mensagem:
🟢 Número de upstreams normalizado (3/3 mínimo).

Detalhes:
• Upstreams Ativos: 3
• Mínimo Configurado: 3
• Upstreams Recuperados: AS174, AS3356
• Status: Redundância adequada restaurada
• Tempo de Problema: 12 minutos

Horário: 01/06/2025 14:45:00 BRT
```

---

### ✅ **20. PREFIXO RESTAURADO**

```
✅ Monitor BGP - Recuperação 📡

Severidade: INFORMATIVO
Tipo: Prefixo Restaurado

Mensagem:
🟢 Prefixo 203.0.113.0/24 restaurado na tabela BGP.

Detalhes:
• Prefixo: 203.0.113.0/24
• ASN Origem: AS65001
• Tempo de Ausência: 7 minutos
• Status: Visibilidade global restaurada
• Impacto: Serviços normalizados

Horário: 01/06/2025 14:45:00 BRT
```

---

### ✅ **21. LATÊNCIA NORMALIZADA**

```
✅ Monitor BGP - Recuperação 🌐

Severidade: INFORMATIVO
Tipo: Performance Normalizada

Mensagem:
🟢 Latência normalizada para AS7018 (85ms).

Detalhes:
• Peer Afetado: AS7018
• Latência Atual: 85ms
• Latência Anterior: 150ms
• Limite Configurado: 100ms
• Melhoria: -43% (65ms de redução)
• Status: Performance restaurada

Horário: 01/06/2025 14:45:00 BRT
```

---

### ✅ **22. INSTABILIDADE RESOLVIDA**

```
✅ Monitor BGP - Recuperação 🔄

Severidade: INFORMATIVO
Tipo: Estabilidade Restaurada

Mensagem:
🟢 Instabilidade de roteamento resolvida.

Detalhes:
• Mudanças de Rota: 3 nos últimos 5 minutos
• Limite Normal: <10 mudanças/5min
• Redução: -94% (de 50 para 3 mudanças)
• Duração do Problema: 18 minutos
• Status: Convergência normalizada

Horário: 01/06/2025 14:45:00 BRT
```

---

### ✅ **23. ANOMALIA RESOLVIDA**

```
✅ Monitor BGP - Recuperação 📊

Severidade: INFORMATIVO
Tipo: Anomalia Resolvida

Mensagem:
🟢 Anomalia estatística resolvida - valores normalizados.

Detalhes:
• Métrica: Número de anúncios BGP
• Valor Atual: 1.150/hora (normal)
• Valor Anterior: 6.000/hora (anômalo)
• Redução: -81% (4.850 anúncios/hora)
• Desvio Atual: 0.2σ (dentro do normal)
• Duração da Anomalia: 25 minutos

Horário: 01/06/2025 14:45:00 BRT
```

---

## 🎯 **PERSONALIZAÇÃO DOS ALARMES PT-BR**

### **Emojis Configuráveis:**
- **Severidade:** 🚨 (crítico), ⚠️ (aviso), ℹ️ (info)
- **Tipos:** 🛑 (peer), 📡 (prefixo), 📊 (anomalia), 🌐 (latência), 📋 (IRR), 🔗 (vazamento), 🔄 (instabilidade)

### **Terminologia Técnica PT-BR:**
- **Peer Loss** → "Perda de Peer BGP"
- **Route Leak** → "Vazamento de Rota"
- **Prefix Missing** → "Prefixo Ausente"
- **IRR Validation** → "Validação IRR"
- **Routing Instability** → "Instabilidade de Roteamento"
- **Statistical Anomaly** → "Anomalia Estatística"

### **Formatação HTML Suportada:**
- `<b>texto</b>` - **negrito**
- `<i>texto</i>` - *itálico*
- `<code>prefixo</code>` - `código`
- `<pre>bloco</pre>` - bloco de código
- `<a href="url">link</a>` - hiperlink

### **Horários em Fuso Brasileiro:**
- Conversão automática para BRT (UTC-3) ou BRST (UTC-2)
- Formato: DD/MM/AAAA HH:MM:SS BRT

---

## 🔧 **IMPLEMENTAÇÃO PT-BR**

Para implementar os alarmes em português brasileiro, modifique o arquivo `telegram.py`:

1. **Adicione o mapeamento de tipos em PT-BR**
2. **Inclua formatação de data/hora para fuso brasileiro**
3. **Implemente terminologia técnica adequada**
4. **Mantenha códigos de ASN e prefixos em formato internacional**

**Exemplo de configuração:**
```python
ALERT_MESSAGES_PT_BR = {
    "peer_loss": "🛑 Perda de {relationship} AS{peer_asn} detectada.",
    "prefix_missing": "📡 Prefixo crítico {prefix} não visível na tabela BGP.",
    "route_leak": "🔗 Possível vazamento detectado: prefixo {prefix} anunciado indevidamente."
}
```

Esta versão mantém a precisão técnica necessária para operações de rede enquanto usa terminologia apropriada para equipes brasileiras.
