# Exemplos de Alertas Telegram - BGP Monitor v1.2.0

## 📱 Guia Completo de Notificações Telegram

Este documento apresenta exemplos reais de como os alertas BGP aparecem no Telegram, incluindo formatação, emojis e conteúdo das mensagens.

## 🔴 Alertas de Problemas BGP

### 1. Peer BGP Offline (`peer_down`)

```
🔴 **ALERTA BGP - PEER OFFLINE**

📍 **Peer**: AS64512 (192.168.1.1)
⏰ **Horário**: 15:30:25 BRT
🌐 **Localização**: São Paulo, BR
📊 **Prefixos Afetados**: 150
🔗 **Sessão**: IPv4 BGP Session

⚠️ **Impacto**: Conectividade comprometida
📋 **Ação**: Verificar conectividade de rede

#BGPAlert #PeerDown #ASN64512
```

### 2. Hijack BGP Detectado (`hijack_detected`)

```
🚨 **ALERTA CRÍTICO - HIJACK BGP DETECTADO**

🎯 **Prefixo**: 200.150.10.0/24
🏢 **AS Legítimo**: AS64500 (Provedor Brasil Telecom)
👤 **AS Anunciante**: AS99999 (Origem Suspeita)
⏰ **Detectado em**: 09:45:12 BRT
🌍 **Região**: América do Sul

🔍 **Detalhes**:
• AS Path: 64501 99999 (anômalo)
• AS Path Legítimo: 64501 64500
• Confiança: 92%

⚠️ **AÇÃO URGENTE NECESSÁRIA**
📞 Contatar NOC imediatamente

#BGPHijack #Crítico #Segurança
```

### 3. Route Leak Detectado (`route_leak`)

```
⚠️ **ALERTA BGP - ROUTE LEAK DETECTADO**

📡 **Prefixo**: 10.20.0.0/16 (Rede Interna)
🔄 **Vazamento**: AS64600 → Internet
⏰ **Início**: 14:20:33 BRT
📈 **Propagação**: 45 ASes afetados

🔍 **AS Path Anômalo**:
`64501 64600 64700 10.20.0.0/16`

⚠️ **Impacto**: Roteamento sub-ótimo
📋 **Ação**: Filtrar anúncios no AS64600

#RouteLeaks #BGPLeak #AS64600
```

### 4. Prefixo Retirado (`prefix_withdrawn`)

```
📉 **ALERTA BGP - PREFIXO RETIRADO**

📍 **Prefixo**: 200.100.50.0/24
🏢 **AS Origem**: AS64300 (DataCenter SP)
⏰ **Retirado em**: 11:15:45 BRT
📊 **Serviços Afetados**: 25 clientes

🔍 **Última Propagação**:
• AS Path: 64501 64300
• Next Hop: 192.168.10.5
• Comunidades: 64300:100

⚠️ **Impacto**: Perda de conectividade
📋 **Verificar**: Configuração BGP no AS64300

#PrefixWithdrawn #BGPUpdate #AS64300
```

### 5. Route Flapping (`route_flapping`)

```
🔄 **ALERTA BGP - ROUTE FLAPPING**

📍 **Prefixo**: 172.16.0.0/12
🔄 **Oscilações**: 8 vezes em 5 minutos
⏰ **Início**: 16:22:10 BRT
📊 **Frequência**: 1.6/minuto

🔍 **Padrão de Oscilação**:
• 16:22:10 - Anunciado
• 16:22:45 - Retirado
• 16:23:20 - Anunciado
• 16:23:55 - Retirado

⚠️ **Impacto**: Instabilidade de roteamento
📋 **Ação**: Aplicar route dampening

#RouteFlapping #BGPInstability #Dampening
```

### 6. AS Path Anômalo (`anomalous_aspath`)

```
🔍 **ALERTA BGP - AS PATH ANÔMALO**

📍 **Prefixo**: 203.0.113.0/24
🛤️ **AS Path**: 64501 64999 64888 64777 64500
⏰ **Detectado**: 13:40:28 BRT
📏 **Comprimento**: 5 ASes (anormal para esta rota)

🔍 **Análise**:
• AS Path Normal: 64501 64500 (2 hops)
• AS Path Atual: 64501 64999 64888 64777 64500 (5 hops)
• Desvio: +150% de comprimento

⚠️ **Possíveis Causas**:
• Route leak intermediário
• Configuração incorreta
• Path prepending excessivo

#AnomalousPath #BGPAnalysis #PathLength
```

## 🟢 Alertas de Recuperação BGP

### 1. Peer Recuperado (`peer_recovered`)

```
✅ **RECUPERAÇÃO BGP - PEER ONLINE**

📍 **Peer**: AS64512 (192.168.1.1)
⏰ **Recuperado em**: 15:45:30 BRT
🕐 **Downtime**: 15 minutos 5 segundos
📊 **Prefixos Restaurados**: 150

🔄 **Correlação**:
• Problema: 15:30:25 BRT (Peer Offline)
• Duração Total: 00:15:05

✅ **Status**: Conectividade restaurada
📋 **Verificado**: Todos os prefixos ativos

#BGPRecovered #PeerUp #AS64512
```

### 2. Hijack Resolvido (`hijack_resolved`)

```
🛡️ **RECUPERAÇÃO BGP - HIJACK RESOLVIDO**

🎯 **Prefixo**: 200.150.10.0/24
🏢 **AS Legítimo**: AS64500 (Brasil Telecom)
⏰ **Resolvido em**: 10:20:45 BRT
🕐 **Duração do Incidente**: 35 minutos 33 segundos

🔄 **Histórico**:
• Hijack Detectado: 09:45:12 BRT
• AS Malicioso: AS99999
• Resolução: Filtro aplicado

✅ **Status**: Roteamento normalizado
📋 **Confirmado**: AS Path legítimo restaurado

#HijackResolved #Segurança #BGPSecurity
```

### 3. Route Leak Resolvido (`route_leak_resolved`)

```
🔒 **RECUPERAÇÃO BGP - ROUTE LEAK RESOLVIDO**

📡 **Prefixo**: 10.20.0.0/16
🔄 **Vazamento**: AS64600 (Resolvido)
⏰ **Correção em**: 14:55:18 BRT
🕐 **Duração**: 34 minutos 45 segundos

🔄 **Resolução**:
• Filtro aplicado no AS64600
• Propagação interrompida
• Roteamento otimizado

✅ **Status**: Prefixo privado protegido
📋 **Verificado**: Sem vazamento externo

#RouteLeakResolved #BGPFilters #AS64600
```

### 4. Prefixo Restaurado (`prefix_restored`)

```
📈 **RECUPERAÇÃO BGP - PREFIXO RESTAURADO**

📍 **Prefixo**: 200.100.50.0/24
🏢 **AS Origem**: AS64300 (DataCenter SP)
⏰ **Restaurado em**: 11:42:20 BRT
🕐 **Indisponibilidade**: 26 minutos 35 segundos

🔄 **Recuperação**:
• Configuração BGP corrigida
• Anúncio reativado
• Propagação confirmada

✅ **Status**: Conectividade restaurada
📋 **Serviços**: 25 clientes reconectados

#PrefixRestored #BGPRecovery #AS64300
```

### 5. Flapping Resolvido (`route_flapping_resolved`)

```
🎯 **RECUPERAÇÃO BGP - FLAPPING RESOLVIDO**

📍 **Prefixo**: 172.16.0.0/12
🔄 **Estabilizado em**: 16:45:55 BRT
🕐 **Período Instável**: 23 minutos 45 segundos
📊 **Total de Oscilações**: 15

🔄 **Resolução**:
• Route dampening aplicado
• Peer estabilizado
• Timer resetado

✅ **Status**: Rota estável há 10 minutos
📋 **Monitoramento**: Continuado por 24h

#FlappingResolved #RouteStability #Dampening
```

### 6. AS Path Normalizado (`aspath_normalized`)

```
🛤️ **RECUPERAÇÃO BGP - AS PATH NORMALIZADO**

📍 **Prefixo**: 203.0.113.0/24
🛤️ **AS Path**: 64501 64500 (Normalizado)
⏰ **Correção em**: 14:15:42 BRT
🕐 **Duração da Anomalia**: 35 minutos 14 segundos

🔄 **Normalização**:
• Path Anômalo: 64501 64999 64888 64777 64500
• Path Normal: 64501 64500
• Redução: 60% menos hops

✅ **Status**: Roteamento otimizado
📋 **Performance**: Latência reduzida em 40ms

#PathNormalized #BGPOptimization #Performance
```

## 🎛️ Configuração de Formatação

### Emojis Utilizados

#### Problemas
- 🔴 Peer Offline
- 🚨 Hijack (Crítico)
- ⚠️ Route Leak / Geral
- 📉 Prefixo Retirado
- 🔄 Route Flapping
- 🔍 AS Path Anômalo

#### Recuperações
- ✅ Recuperação Geral
- 🛡️ Hijack Resolvido
- 🔒 Route Leak Resolvido
- 📈 Prefixo Restaurado
- 🎯 Flapping Resolvido
- 🛤️ AS Path Normalizado

#### Informações
- 📍 Localização/Prefixo
- ⏰ Horário
- 🌐 Região/Localização
- 📊 Estatísticas
- 🔗 Conexão
- 🕐 Duração

### Templates de Mensagem

#### Estrutura Padrão
```
[EMOJI] **TIPO DE ALERTA - DESCRIÇÃO**

📍 **Campo Principal**: Valor
⏰ **Horário**: Timestamp
[Campos específicos do tipo]

🔍 **Detalhes**:
• Informação adicional 1
• Informação adicional 2

⚠️ **Impacto/Status**: Descrição
📋 **Ação**: Próximos passos

#HashTags #Relevantes
```

### Personalização de Mensagens

#### Configuração no `config/telegram_config.json`
```json
{
  "message_format": {
    "use_emojis": true,
    "use_bold": true,
    "use_hashtags": true,
    "timezone": "America/Sao_Paulo",
    "language": "pt_br"
  },
  "notification_settings": {
    "group_related": true,
    "max_message_length": 4096,
    "retry_failed": true,
    "rate_limit": 30
  }
}
```

## 📊 Exemplos de Agrupamento

### Múltiplos Problemas Relacionados

```
🔴 **MÚLTIPLOS ALERTAS BGP - AS64512**

⏰ **Período**: 15:30-15:35 BRT

📋 **Problemas Detectados**:
1. 🔴 Peer 192.168.1.1 offline (15:30:25)
2. 📉 150 prefixos retirados (15:30:28)
3. 🔄 Route flapping em 3 prefixos (15:31:15)

📊 **Impacto Total**:
• 150 prefixos afetados
• 1.2k clientes impactados
• 3 datacenters com problemas

⚠️ **Status**: Investigação em andamento
📞 **NOC**: Equipe acionada

#MultipleAlerts #AS64512 #Outage
```

### Recuperação Completa

```
✅ **RECUPERAÇÃO COMPLETA - AS64512**

⏰ **Restaurado em**: 15:55:30 BRT
🕐 **Downtime Total**: 25 minutos 5 segundos

📋 **Problemas Resolvidos**:
1. ✅ Peer 192.168.1.1 online (15:45:30)
2. 📈 150 prefixos restaurados (15:50:15)
3. 🎯 Route flapping resolvido (15:55:30)

📊 **Status Final**:
• 100% dos serviços restaurados
• Monitoramento reforçado por 24h
• RCA programado para amanhã

✅ **Tudo normalizado!**

#FullRecovery #AS64512 #AllGood
```

## 🔧 Configuração Avançada

### Rate Limiting
```json
{
  "rate_limiting": {
    "max_alerts_per_minute": 10,
    "burst_detection": true,
    "group_similar_alerts": true,
    "suppress_duplicates": 300
  }
}
```

### Filtros de Alerta
```json
{
  "alert_filters": {
    "minimum_severity": "medium",
    "exclude_asns": [64999, 65000],
    "include_prefixes": ["200.150.0.0/16"],
    "time_windows": {
      "maintenance": {
        "start": "02:00",
        "end": "06:00",
        "suppress_alerts": false,
        "reduce_verbosity": true
      }
    }
  }
}
```

### Integração com Grupos

#### Configuração para Grupos Telegram
```json
{
  "telegram_groups": {
    "noc_alerts": {
      "chat_id": "-1001234567890",
      "alert_types": ["critical", "high"],
      "include_recovery": true
    },
    "engineering": {
      "chat_id": "-1001234567891",
      "alert_types": ["all"],
      "detailed_analysis": true
    }
  }
}
```

## 📱 Comandos Interativos

### Comandos Disponíveis no Bot
```
/status - Status atual do sistema
/alerts - Últimos alertas (1h)
/peers - Status dos peers BGP
/recovery - Últimas recuperações
/help - Lista de comandos
/mute [tempo] - Silenciar alertas
/config - Configurações atuais
```

### Exemplo de Interação
```
Usuário: /status
Bot: 📊 **Status BGP Monitor v1.2.0**
• 🟢 Sistema: Online
• 📡 Peers: 15/15 ativos
• ⏰ Uptime: 5d 12h 30m
• 📈 Últimas 24h: 0 problemas
```

## 🎯 Melhores Práticas

### Para Administradores
1. **Configure grupos separados** para diferentes níveis de alerta
2. **Use rate limiting** para evitar spam em situações críticas
3. **Mantenha logs** de todas as notificações enviadas
4. **Configure backup** para múltiplos canais de notificação

### Para Operadores
1. **Monitore hashtags** para filtrar tipos específicos
2. **Use comandos** para obter informações adicionais
3. **Configure notificações** para seus turnos específicos
4. **Documente** padrões de alertas para análise posterior

---

**Nota**: Todos os exemplos mostram timestamps em horário de Brasília (BRT/BRST) e utilizam terminologia técnica apropriada para o contexto brasileiro de redes e telecomunicações.