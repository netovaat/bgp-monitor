# 🔧 Guia de Uso

Guia completo para usar o BGP Monitor v1.0 no dia a dia.

## 🚀 Iniciando o Sistema

### Inicialização Básica

```bash
# Método 1: Script de execução
./run.sh

# Método 2: Diretamente via Python
python3 -m app.main

# Método 3: Via script de gerenciamento
./bgp-monitor.sh start
```

### Verificação de Status

```bash
# Status completo do sistema
./bgp-monitor.sh status

# Status da API
curl http://localhost:8000/

# Saúde do sistema
curl http://localhost:8000/health
```

## 📊 Gerenciamento de Prefixos

### Adicionar Prefixos

```bash
# Via script (recomendado)
./bgp-monitor.sh add-prefix "203.0.113.0/24" "Rede principal"
./bgp-monitor.sh add-prefix "198.51.100.0/24" "Rede DMZ"

# Via API REST
curl -X POST http://localhost:8000/prefixes \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "203.0.113.0/24",
    "asn": 64512,
    "description": "Rede principal"
  }'
```

### Listar Prefixos

```bash
# Via script
./bgp-monitor.sh list-prefixes

# Via API
curl http://localhost:8000/prefixes
```

### Remover Prefixos

```bash
# Via script
./bgp-monitor.sh remove-prefix "203.0.113.0/24"

# Via API (usando ID do prefixo)
curl -X DELETE http://localhost:8000/prefixes/1
```

## 🔍 Monitoramento e Verificações

### Executar Verificações Manuais

```bash
# Todas as verificações
./bgp-monitor.sh check

# Verificação específica de prefixos
curl -X POST http://localhost:8000/monitoring/run-checks

# Verificação de peers
curl -X POST http://localhost:8000/monitoring/check-peers

# Validação IRR
curl -X POST http://localhost:8000/monitoring/check-irr
```

### Visualizar Métricas

```bash
# Métricas completas
curl http://localhost:8000/metrics | python3 -m json.tool

# Via script (formatado)
./bgp-monitor.sh metrics
```

### Histórico de Alertas

```bash
# Listar alertas recentes
curl http://localhost:8000/alerts

# Alertas por tipo
curl "http://localhost:8000/alerts?type=prefix_missing"

# Alertas por severidade
curl "http://localhost:8000/alerts?severity=critical"
```

## 📱 Notificações Telegram

### Testar Telegram

```bash
# Teste básico de conectividade
./bgp-monitor.sh test-telegram

# Teste via API
curl -X POST http://localhost:8000/test/telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste do BGP Monitor"}'
```

### Configurar Alertas

```bash
# Envio manual de alerta de teste
curl -X POST http://localhost:8000/test/alert \
  -H "Content-Type: application/json" \
  -d '{
    "type": "test",
    "severity": "info",
    "message": "Teste de alerta do BGP Monitor",
    "details": {"timestamp": "2025-05-27T10:00:00Z"}
  }'
```

## 📈 Monitoramento Contínuo

### Verificação Automática

O sistema executa automaticamente:

- **Prefixos BGP**: A cada 5 minutos (300s)
- **Peers BGP**: A cada 10 minutos (600s)
- **Validação IRR**: A cada 15 minutos (900s)
- **Health Check**: A cada 1 minuto (60s)
- **Relatório Diário**: Às 09:00 UTC

### Logs em Tempo Real

```bash
# Seguir logs do sistema
tail -f /var/log/bgp-monitor.log

# Logs estruturados (JSON)
tail -f /var/log/bgp-monitor.log | jq .

# Filtrar por nível
tail -f /var/log/bgp-monitor.log | grep "ERROR\|WARNING"
```

## 🛠️ Operações de Manutenção

### Parar o Sistema

```bash
# Parada graceful
./bgp-monitor.sh stop

# Parada forçada (se necessário)
./bgp-monitor.sh kill

# Verificar se parou
./bgp-monitor.sh status
```

### Reiniciar o Sistema

```bash
# Reinicialização completa
./bgp-monitor.sh restart

# Recarregar configuração (se disponível)
./bgp-monitor.sh reload
```

### Backup e Restore

```bash
# Backup da configuração
./bgp-monitor.sh backup

# Backup completo (inclui dados em memória)
./bgp-monitor.sh backup --full

# Restaurar configuração
./bgp-monitor.sh restore backup-2025-05-27.tar.gz
```

## 🔍 Diagnóstico e Troubleshooting

### Verificar Conectividade

```bash
# Teste de conectividade com RIPE
./bgp-monitor.sh test-connectivity

# Teste manual da RIPE API
curl -s "https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS64512"

# Teste de resolução DNS
nslookup stat.ripe.net
```

### Debug do Sistema

```bash
# Executar em modo debug
DEBUG=true ./run.sh

# Verificar configuração carregada
./bgp-monitor.sh config

# Validar arquivo .env
./bgp-monitor.sh validate-config
```

### Verificar Saúde dos Componentes

```bash
# Saúde detalhada
curl http://localhost:8000/health?detailed=true

# Status individual dos monitores
curl http://localhost:8000/monitoring/status
```

## 📊 Relatórios e Análises

### Relatório Diário

```bash
# Gerar relatório manual
./bgp-monitor.sh report

# Relatório via API
curl http://localhost:8000/reports/daily

# Relatório personalizado
curl "http://localhost:8000/reports/custom?from=2025-05-26&to=2025-05-27"
```

### Estatísticas de Performance

```bash
# Métricas de performance
curl http://localhost:8000/metrics/performance

# Tempo de resposta das verificações
curl http://localhost:8000/metrics/timing

# Estatísticas de alertas
curl http://localhost:8000/metrics/alerts
```

## 🎯 Casos de Uso Comuns

### 1. Monitoramento de Mudança de Provider

```bash
# Adicionar novos prefixos antes da migração
./bgp-monitor.sh add-prefix "203.0.113.0/24" "Rede principal - Provider A"

# Monitorar durante a migração
./bgp-monitor.sh check --continuous

# Verificar se anúncio está ativo
curl "http://localhost:8000/prefixes/203.0.113.0%2F24/status"
```

### 2. Auditoria de Segurança BGP

```bash
# Verificar todos os prefixos anunciados
curl "http://localhost:8000/monitoring/audit/prefixes"

# Validar conformidade IRR
curl "http://localhost:8000/monitoring/audit/irr"

# Gerar relatório de conformidade
curl "http://localhost:8000/reports/compliance"
```

### 3. Resposta a Incidentes

```bash
# Verificação imediata de todos os prefixos
./bgp-monitor.sh emergency-check

# Forçar envio de relatório de status
./bgp-monitor.sh force-report

# Alterar nível de alertas temporariamente
./bgp-monitor.sh set-alert-level critical
```

## 🔧 Personalização

### Alterar Intervalos Temporariamente

```bash
# Via variáveis de ambiente
PREFIX_CHECK_INTERVAL=60 ./run.sh

# Via API (se implementado)
curl -X PUT http://localhost:8000/config/intervals \
  -H "Content-Type: application/json" \
  -d '{"prefix_check": 60, "peer_check": 120}'
```

### Filtros de Alertas

```bash
# Silenciar alertas específicos
curl -X POST http://localhost:8000/alerts/silence \
  -H "Content-Type: application/json" \
  -d '{"type": "peer_loss", "duration": 3600}'

# Alterar severidade de alertas
curl -X PUT http://localhost:8000/alerts/severity \
  -H "Content-Type: application/json" \
  -d '{"type": "prefix_missing", "severity": "warning"}'
```

## 📱 Interface Web (Futuro)

Para uma interface web amigável, acesse:

```bash
# Interface principal
http://localhost:8000/

# Dashboard de métricas
http://localhost:8000/dashboard

# Configuração via web
http://localhost:8000/config
```

## 🔄 Integração com Outros Sistemas

### Webhook para Alertas

```bash
# Configurar webhook externo
curl -X POST http://localhost:8000/config/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://meu-sistema.com/bgp-alerts",
    "events": ["prefix_missing", "peer_loss"],
    "format": "json"
  }'
```

### Export de Dados

```bash
# Export JSON das configurações
curl http://localhost:8000/export/config > bgp-config.json

# Export CSV das métricas
curl http://localhost:8000/export/metrics?format=csv > metrics.csv

# Export de alertas para SIEM
curl http://localhost:8000/export/alerts?format=syslog
```

## 📚 Próximos Passos

Após dominar o uso básico:

1. [🌐 Explore a API completa](API.md)
2. [🏗️ Entenda a arquitetura](ARCHITECTURE.md)
3. [🔍 Troubleshooting avançado](TROUBLESHOOTING.md)
4. [🤝 Contribua para o projeto](../CONTRIBUTING.md)

## 💡 Dicas de Produtividade

- Use aliases para comandos frequentes
- Configure monitoramento do próprio BGP Monitor
- Mantenha backup das configurações
- Monitore logs regularmente
- Configure alertas para falhas do próprio sistema
