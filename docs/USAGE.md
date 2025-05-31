# 🔧 Guia de Uso

Guia completo para usar o BGP Monitor v1.0.0 com PostgreSQL no dia a dia.

## 🚀 Iniciando o Sistema

### Via Systemd (Recomendado)

```bash
# Iniciar o serviço
sudo systemctl start bgp-monitor

# Verificar status
sudo systemctl status bgp-monitor

# Habilitar inicialização automática
sudo systemctl enable bgp-monitor

# Verificar logs
sudo journalctl -u bgp-monitor -f
```

### Execução Manual (Desenvolvimento)

```bash
# Ativar ambiente virtual
cd /opt/bgp-monitor
source venv/bin/activate

# Executar aplicação
python main.py

# Ou executar em background
nohup python main.py > logs/app.log 2>&1 &
```

### Verificação de Status

```bash
# Status da API
curl -s http://localhost:8000/health | jq

# Dashboard geral
curl -s http://localhost:8000/dashboard | jq

# Status do scheduler
curl -s http://localhost:8000/scheduler/status | jq
```

## 🌐 Gerenciamento de ASNs

### Adicionar ASNs

```bash
# ASN individual
curl -X POST "http://localhost:8000/asns" \
  -H "Content-Type: application/json" \
  -d '{
    "asn": 64512,
    "name": "Minha Empresa",
    "description": "ASN principal da rede",
    "enabled": true
  }'

# Múltiplos ASNs em batch
curl -X POST "http://localhost:8000/asns/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "asns": [
      {"asn": 64512, "name": "Empresa A", "enabled": true},
      {"asn": 64513, "name": "Empresa B", "enabled": true},
      {"asn": 13335, "name": "Cloudflare", "enabled": false}
    ]
  }'
```

### Listar e Gerenciar ASNs

```bash
# Listar todos os ASNs
curl -s "http://localhost:8000/asns" | jq

# Listar apenas ASNs ativos
curl -s "http://localhost:8000/asns?enabled=true" | jq

# Obter ASN específico
curl -s "http://localhost:8000/asns/64512" | jq

# Atualizar ASN
curl -X PUT "http://localhost:8000/asns/64512" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Novo Nome",
    "description": "Nova descrição",
    "enabled": false
  }'

# Deletar ASN
curl -X DELETE "http://localhost:8000/asns/64512"
```

### Importar/Exportar Configurações

```bash
# Exportar configuração atual
curl -s "http://localhost:8000/asns/export" > asns_backup.json

# Importar configuração
curl -X POST "http://localhost:8000/asns/import" \
  -H "Content-Type: application/json" \
  -d @asns_backup.json
```

## 📊 Coleta de Dados e Histórico

### Coleta Manual Forçada

```bash
# Forçar coleta de todos os ASNs ativos
curl -X POST "http://localhost:8000/collect/force"

# Forçar coleta de ASN específico
curl -X POST "http://localhost:8000/collect/force" \
  -H "Content-Type: application/json" \
  -d '{"asn": 64512}'

# Verificar status da última coleta
curl -s "http://localhost:8000/dashboard" | jq '.last_collection'
```

### Visualizar Dados Históricos

```bash
# Histórico de ASN específico (últimos 7 dias)
curl -s "http://localhost:8000/historical/64512?days=7" | jq

# Histórico com filtro de período
curl -s "http://localhost:8000/historical/64512?start_date=2025-01-01&end_date=2025-01-31" | jq

# Estatísticas resumidas
curl -s "http://localhost:8000/historical/64512/stats" | jq
```

### Dados de Prefixos

```bash
# Prefixos atuais do ASN
curl -s "http://localhost:8000/historical/64512/prefixes" | jq

# Histórico de mudanças de prefixos
curl -s "http://localhost:8000/historical/64512/prefix-changes?days=30" | jq
```

## 🚨 Detecção de Anomalias

### Verificar Anomalias

```bash
# Anomalias recentes de todos os ASNs
curl -s "http://localhost:8000/anomalies" | jq

# Anomalias de ASN específico
curl -s "http://localhost:8000/anomalies/64512" | jq

# Anomalias por tipo
curl -s "http://localhost:8000/anomalies?type=sudden_increase" | jq

# Anomalias críticas apenas
curl -s "http://localhost:8000/anomalies?severity=critical" | jq
```

### Configurar Sensibilidade

```bash
# Verificar configuração atual
curl -s "http://localhost:8000/metrics" | jq '.anomaly_detection'

# Ajustar sensibilidade via .env
ANOMALY_SENSITIVITY=1.5  # Mais sensível
ANOMALY_SENSITIVITY=2.5  # Menos sensível
```

## 📱 Notificações Telegram

### Testar Telegram

```bash
# Teste básico
curl -X POST "http://localhost:8000/test/telegram" \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste BGP Monitor v2.0 🚀"}'

# Teste com formatação HTML
curl -X POST "http://localhost:8000/test/telegram" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "<b>BGP Monitor v2.0</b>\n<i>Sistema funcionando perfeitamente!</i>\n\n✅ PostgreSQL: Conectado\n🔄 Scheduler: Ativo\n📊 ASNs: 52 monitorados"
  }'
```

### Simulador de Alertas

```bash
# Alerta de prefixos ausentes
curl -X POST "http://localhost:8000/test/alert" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "missing_prefixes",
    "asn": 64512,
    "severity": "critical",
    "prefixes": ["203.0.113.0/24", "198.51.100.0/24"]
  }'

# Alerta de anomalia
curl -X POST "http://localhost:8000/test/alert" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sudden_increase", 
    "asn": 64512,
    "severity": "warning",
    "change_percentage": 25.5,
    "baseline": 120,
    "current": 151
  }'
```

## 📈 Monitoramento e Métricas

### Dashboard Principal

```bash
# Visão geral do sistema
curl -s "http://localhost:8000/dashboard" | jq

# Métricas de performance
curl -s "http://localhost:8000/metrics" | jq

# Status detalhado
curl -s "http://localhost:8000/health" | jq
```

### Estatísticas por ASN

```bash
# Top ASNs por número de prefixos
curl -s "http://localhost:8000/dashboard" | jq '.asn_stats | sort_by(.prefix_count) | reverse'

# ASNs com mais anomalias
curl -s "http://localhost:8000/dashboard" | jq '.asn_stats | sort_by(.anomaly_count) | reverse'
```

### Alertas e Histórico

```bash
# Alertas das últimas 24h
curl -s "http://localhost:8000/alerts?hours=24" | jq

# Histórico de alertas por tipo
curl -s "http://localhost:8000/alerts/stats" | jq

# Alertas não resolvidos
curl -s "http://localhost:8000/alerts?status=active" | jq
```

## 🔧 Manutenção e Operações

### Controle do Serviço

```bash
# Parar o sistema
sudo systemctl stop bgp-monitor

# Iniciar o sistema
sudo systemctl start bgp-monitor

# Reiniciar o sistema
sudo systemctl restart bgp-monitor

# Verificar status
sudo systemctl status bgp-monitor

# Verificar logs
sudo journalctl -u bgp-monitor -f
```

### Backup e Restore

```bash
# Backup do banco PostgreSQL
pg_dump -h localhost -U bgp_monitor bgp_monitor > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup da configuração
cp .env .env.backup.$(date +%Y%m%d)
cp -r logs logs.backup.$(date +%Y%m%d)

# Restore do banco
psql -h localhost -U bgp_monitor bgp_monitor < backup_20250527_120000.sql
```

### Limpeza Manual

```bash
# Limpeza de dados antigos via API
curl -X POST "http://localhost:8000/admin/cleanup" \
  -H "Content-Type: application/json" \
  -d '{"days": 365}'

# Verificar espaço usado
curl -s "http://localhost:8000/metrics" | jq '.database_size'

# Limpeza de logs
find logs/ -name "*.log" -mtime +30 -delete
```

## 🔍 Diagnóstico e Troubleshooting

### Verificar Conectividade

```bash
# Teste de conectividade PostgreSQL
psql -h localhost -U bgp_monitor -d bgp_monitor -c "SELECT version();"

# Teste RIPE API
curl -s "https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS64512" | jq '.data.prefixes | length'

# Teste Telegram
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | jq
```

### Debug do Sistema

```bash
# Executar em modo debug
DEBUG=true python main.py

# Verificar configuração carregada
curl -s "http://localhost:8000/health" | jq '.configuration'

# Logs em tempo real
tail -f logs/bgp-monitor.log | jq -r '.timestamp + " " + .level + " " + .message'
```

### Verificar Performance

```bash
# Métricas de coleta
curl -s "http://localhost:8000/metrics" | jq '.collection_performance'

# Status do rate limiting
curl -s "http://localhost:8000/metrics" | jq '.rate_limiting'

# Uso de recursos
curl -s "http://localhost:8000/metrics" | jq '.system_metrics'
```

## 📊 Relatórios e Análises

### Relatórios Automatizados

O sistema envia automaticamente:
- **Relatório Diário**: Resumo das últimas 24h às 09:00 UTC
- **Relatório Semanal**: Resumo semanal aos domingos às 09:00 UTC
- **Alertas em Tempo Real**: Conforme anomalias são detectadas

### Relatórios Manuais

```bash
# Relatório de ASN específico
curl -s "http://localhost:8000/reports/asn/64512" | jq

# Relatório de período customizado
curl -s "http://localhost:8000/reports/custom?start_date=2025-01-01&end_date=2025-01-31" | jq

# Estatísticas de anomalias
curl -s "http://localhost:8000/reports/anomalies" | jq
```

## 🎯 Casos de Uso Avançados

### 1. Monitoramento de Migração BGP

```bash
# Antes da migração - adicionar ASNs envolvidos
curl -X POST "http://localhost:8000/asns/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "asns": [
      {"asn": 64512, "name": "ASN Origem", "enabled": true},
      {"asn": 64513, "name": "ASN Destino", "enabled": true}
    ]
  }'

# Durante a migração - monitoramento intensivo
COLLECTION_INTERVAL=300 # Reduzir para 5 minutos

# Verificar transferência de prefixos
curl -s "http://localhost:8000/historical/64512/prefixes" | jq
curl -s "http://localhost:8000/historical/64513/prefixes" | jq
```

### 2. Detecção de BGP Hijacking

```bash
# Monitorar prefixos específicos suspeitos
curl -s "http://localhost:8000/anomalies?type=bgp_leak" | jq

# Verificar origem dos anúncios
curl -s "http://localhost:8000/historical/search/prefix/203.0.113.0%2F24" | jq
```

### 3. Análise de Estabilidade

```bash
# Verificar instabilidade histórica
curl -s "http://localhost:8000/anomalies?type=routing_instability&days=30" | jq

# Análise de tendências
curl -s "http://localhost:8000/historical/64512/trends" | jq
```

## 📈 Otimização e Tuning

### Para Ambientes de Alto Volume

```bash
# Aumentar pool de conexões PostgreSQL
# Em postgresql.conf:
max_connections = 200
shared_buffers = 512MB

# Ajustar configurações do sistema
COLLECTION_INTERVAL=1800
API_RATE_LIMIT_PER_ASN=60
API_BATCH_SIZE=2
```

### Para Monitoramento Crítico

```bash
# Configurações de alta responsividade
COLLECTION_INTERVAL=300
ANOMALY_SENSITIVITY=1.5
API_RATE_LIMIT_PER_ASN=30
```

## 🔐 Segurança e Compliance

### Auditoria de Acesso

```bash
# Verificar logs de acesso à API
grep "GET\|POST\|PUT\|DELETE" logs/bgp-monitor.log | jq

# Estatísticas de uso
curl -s "http://localhost:8000/metrics" | jq '.api_usage'
```

### Validação de Configuração

```bash
# Verificar configuração de segurança
curl -s "http://localhost:8000/health" | jq '.security_check'

# Testar configurações
curl -X POST "http://localhost:8000/admin/validate-config"
```

## 📚 Próximos Passos

Após dominar o uso básico:

1. [🌐 Explore toda a API REST](API.md)
2. [🏗️ Entenda a arquitetura do sistema](ARCHITECTURE.md)
3. [⚙️ Configure alertas avançados](CONFIGURATION.md)
4. [🔍 Troubleshooting avançado](TROUBLESHOOTING.md)

## 💡 Dicas e Truques

### Comandos Úteis do Dia a Dia

```bash
# Verificação rápida de saúde
alias bgp-health='curl -s http://localhost:8000/health | jq .status'

# Dashboard resumido
alias bgp-dash='curl -s http://localhost:8000/dashboard | jq "{asns: .total_asns, last_collection: .last_collection, anomalies: .recent_anomalies}"'

# Status do scheduler
alias bgp-scheduler='curl -s http://localhost:8000/scheduler/status | jq'

# Logs em tempo real formatados
alias bgp-logs='tail -f logs/bgp-monitor.log | jq -r ".timestamp + \" \" + .level + \" \" + .message"'
```

### Automatização com Scripts

```bash
#!/bin/bash
# check-bgp-status.sh
curl -s http://localhost:8000/health | jq .status | grep -q "healthy" || {
    echo "BGP Monitor não está saudável!"
    sudo systemctl restart bgp-monitor
}
```

Esta documentação cobre todos os aspectos práticos do uso do BGP Monitor v2.0. Para informações mais técnicas, consulte os outros documentos na pasta `docs/`.

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
