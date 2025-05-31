# ⚙️ Configuração

Guia completo de configuração do BGP Monitor v1.0.0 com PostgreSQL.

## 📄 Arquivo .env

O BGP Monitor v1.0.0 usa um arquivo `.env` para todas as configurações do sistema.

### Configuração Básica

```bash
# BGP Monitor v1.0.0 Configuration

# === DATABASE CONFIGURATION ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bgp_monitor
DB_USER=bgp_monitor
DB_PASSWORD=your_secure_password_here

# === TELEGRAM BOT CONFIGURATION ===
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_example_token
TELEGRAM_CHAT_ID=-1001234567890

# === APPLICATION SETTINGS ===
HOST=0.0.0.0
PORT=8000
DEBUG=false

# === BGP MONITORING SETTINGS ===
COLLECTION_INTERVAL=900          # Coleta de dados (15 minutos)
API_RATE_LIMIT_PER_ASN=45       # Limite entre requests por ASN (45s)
API_BATCH_SIZE=3                 # ASNs processados por batch
API_TIMEOUT=30                   # Timeout para RIPE API

# === ANOMALY DETECTION ===
ANOMALY_SENSITIVITY=2.0          # Sensibilidade Z-score (2.0 = 95% confiança)
MIN_HISTORICAL_DAYS=7            # Mínimo de dias para baseline
BASELINE_CALCULATION_DAYS=30     # Dias para cálculo de baseline

# === DATA RETENTION ===
DATA_RETENTION_DAYS=365          # Retenção de dados históricos (1 ano)
CLEANUP_INTERVAL_HOURS=24        # Limpeza automática a cada 24h

# === LOG SETTINGS ===
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
```

## 🗄️ Configuração do Banco PostgreSQL

### 1. Configuração Manual

Se não usou o script `install.sh`, configure manualmente:

```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Criar usuário e banco
sudo -u postgres psql << EOF
CREATE USER bgp_monitor WITH PASSWORD 'your_secure_password_here';
CREATE DATABASE bgp_monitor OWNER bgp_monitor;
GRANT ALL PRIVILEGES ON DATABASE bgp_monitor TO bgp_monitor;
\q
EOF

# Testar conexão
psql -h localhost -U bgp_monitor -d bgp_monitor -c "SELECT version();"
```

### 2. Configurações Avançadas PostgreSQL

Para ambientes de alta performance:

```bash
# Em postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 3. Backup e Restore

```bash
# Backup diário automatizado
pg_dump -h localhost -U bgp_monitor bgp_monitor > backup_$(date +%Y%m%d).sql

# Restore de backup
psql -h localhost -U bgp_monitor bgp_monitor < backup_20231201.sql
```

## 🤖 Configuração do Telegram

### 1. Criar Bot do Telegram

1. Acesse [@BotFather](https://t.me/BotFather) no Telegram
2. Envie `/newbot`
3. Escolha um nome para seu bot (ex: "BGP Monitor v1.0.0")
4. Escolha um username (ex: "meu_bgp_monitor_v2_bot")
5. Copie o token fornecido

### 2. Obter Chat ID

**Método 1: Bot UserInfo**
1. Acesse [@userinfobot](https://t.me/userinfobot)
2. Envie `/start`
3. Copie seu Chat ID

**Método 2: API do Telegram**
```bash
# Substitua SEU_BOT_TOKEN pelo token do seu bot
curl -s "https://api.telegram.org/botSEU_BOT_TOKEN/getUpdates" | grep -o '"id":[0-9-]*' | head -1
```

**Método 3: Chat em Grupo**
1. Adicione o bot ao grupo
2. Torne o bot administrador
3. Use o método 2 para obter o Chat ID do grupo (será negativo)

### 3. Testar Configuração

```bash
# Testar envio de mensagem via API
curl -X POST "http://localhost:8000/test/telegram" \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste do BGP Monitor v1.0.0"}'
```

## 🌐 Configuração de ASNs para Monitoramento

### Adicionar ASNs via API

```bash
# Adicionar ASN individual
curl -X POST "http://localhost:8000/asns" \
  -H "Content-Type: application/json" \
  -d '{
    "asn": 64512,
    "name": "Minha Rede",
    "description": "ASN principal da empresa",
    "enabled": true
  }'

# Adicionar múltiplos ASNs
curl -X POST "http://localhost:8000/asns/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "asns": [
      {"asn": 64512, "name": "Rede Principal", "enabled": true},
      {"asn": 64513, "name": "Rede Backup", "enabled": true},
      {"asn": 13335, "name": "Cloudflare", "enabled": false}
    ]
  }'
```

### Importar Lista de ASNs

```bash
# Criar arquivo asns.json
cat > asns.json << EOF
{
  "asns": [
    {"asn": 64512, "name": "Empresa A", "description": "ASN principal", "enabled": true},
    {"asn": 64513, "name": "Empresa B", "description": "ASN secundário", "enabled": true},
    {"asn": 13335, "name": "Cloudflare", "description": "Cloudflare Inc.", "enabled": false}
  ]
}
EOF

# Importar via API
curl -X POST "http://localhost:8000/asns/import" \
  -H "Content-Type: application/json" \
  -d @asns.json
```

## ⏱️ Configuração de Intervalos e Rate Limiting

### Coleta de Dados BGP

```bash
# Intervalo principal de coleta (recomendado: 900s = 15 minutos)
COLLECTION_INTERVAL=900

# Rate limiting para proteger contra bloqueios da RIPE API
API_RATE_LIMIT_PER_ASN=45    # 45 segundos entre requests do mesmo ASN
API_BATCH_SIZE=3             # Processar 3 ASNs por vez

# Timeout para requests
API_TIMEOUT=30               # 30 segundos
```

### Configurações Otimizadas por Cenário

**Monitoramento Intensivo (Poucos ASNs):**
```bash
COLLECTION_INTERVAL=300      # 5 minutos
API_RATE_LIMIT_PER_ASN=30   # 30 segundos
API_BATCH_SIZE=5            # 5 ASNs por vez
```

**Monitoramento Normal (50+ ASNs):**
```bash
COLLECTION_INTERVAL=900      # 15 minutos
API_RATE_LIMIT_PER_ASN=45   # 45 segundos
API_BATCH_SIZE=3            # 3 ASNs por vez
```

**Monitoramento Conservador (100+ ASNs):**
```bash
COLLECTION_INTERVAL=1800     # 30 minutos
API_RATE_LIMIT_PER_ASN=60   # 60 segundos
API_BATCH_SIZE=2            # 2 ASNs por vez
```

## 🔍 Configuração de Detecção de Anomalias

### Sensibilidade da Detecção

```bash
# Sensibilidade Z-score (quanto maior, menos sensível)
ANOMALY_SENSITIVITY=2.0      # 95% confiança (recomendado)
ANOMALY_SENSITIVITY=1.5      # 87% confiança (mais sensível)
ANOMALY_SENSITIVITY=2.5      # 99% confiança (menos sensível)

# Baseline para cálculos estatísticos
MIN_HISTORICAL_DAYS=7        # Mínimo 7 dias de dados
BASELINE_CALCULATION_DAYS=30 # Usar últimos 30 dias para baseline
```

### Tipos de Anomalias Detectadas

O sistema detecta automaticamente:

- **sudden_increase**: Aumento súbito de prefixos (>Z-score)
- **sudden_decrease**: Diminuição súbita de prefixos (>Z-score)
- **routing_instability**: Instabilidade alta nas rotas
- **missing_prefixes**: Prefixos esperados ausentes
- **bgp_leak**: Possível vazamento BGP
- **peer_loss**: Perda significativa de peers
- **latency_increase**: Aumento na latência de updates

## 🗂️ Configuração de Retenção de Dados

### Limpeza Automática

```bash
# Retenção de dados históricos
DATA_RETENTION_DAYS=365      # 1 ano (recomendado)
DATA_RETENTION_DAYS=180      # 6 meses (economia de espaço)
DATA_RETENTION_DAYS=730      # 2 anos (análise estendida)

# Frequência de limpeza
CLEANUP_INTERVAL_HOURS=24    # Limpeza diária
CLEANUP_INTERVAL_HOURS=168   # Limpeza semanal
```

### Estimativa de Espaço em Disco

Para 50 ASNs monitorados:
- **1 ano**: ~2-5 GB
- **6 meses**: ~1-2.5 GB 
- **2 anos**: ~4-10 GB

## 📊 Configuração de Logs

### Níveis de Log

```bash
# Desenvolvimento e troubleshooting
LOG_LEVEL=DEBUG              # Máximo detalhe

# Produção normal
LOG_LEVEL=INFO               # Informações gerais (recomendado)

# Produção crítica
LOG_LEVEL=WARNING            # Apenas alertas e erros
LOG_LEVEL=ERROR              # Apenas erros críticos
```

### Logs Estruturados

Logs são salvos em:
- `/opt/bgp-monitor/logs/bgp-monitor.log` - Log principal
- `/opt/bgp-monitor/logs/scheduler.log` - Log do scheduler
- `/opt/bgp-monitor/logs/anomaly.log` - Log de anomalias

### Rotação de Logs

Configure rotação automática no sistema:

```bash
# Criar arquivo de configuração logrotate
sudo tee /etc/logrotate.d/bgp-monitor << EOF
/opt/bgp-monitor/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 bgp-monitor bgp-monitor
    postrotate
        systemctl reload bgp-monitor || true
    endscript
}
EOF
```

## 🚀 Configuração para Produção

### 1. Segurança

```bash
# Desabilitar debug
DEBUG=false

# Bind específico se usar proxy reverso
HOST=127.0.0.1
PORT=8000

# Senha forte para PostgreSQL
DB_PASSWORD=$(openssl rand -base64 32)
```

### 2. Performance Otimizada

```bash
# Configurações para produção
COLLECTION_INTERVAL=900
API_RATE_LIMIT_PER_ASN=45
API_BATCH_SIZE=3
ANOMALY_SENSITIVITY=2.0
DATA_RETENTION_DAYS=365
LOG_LEVEL=INFO
```

### 3. Monitoramento de Sistema

```bash
# Adicionar ao crontab para verificação de saúde
echo "*/5 * * * * curl -s http://localhost:8000/health > /dev/null || systemctl restart bgp-monitor" | crontab -
```

## 🔧 Configurações Avançadas

### Proxy/Firewall

Para ambientes corporativos:

```bash
# Configurar proxy HTTP no ambiente
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=http://proxy.empresa.com:8080
export NO_PROXY=localhost,127.0.0.1

# Timeout maior para consultas
API_TIMEOUT=60
```

### Múltiplos Ambientes

Para separar desenvolvimento/produção:

```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
COLLECTION_INTERVAL=300
DB_NAME=bgp_monitor_dev

# .env.production  
DEBUG=false
LOG_LEVEL=INFO
COLLECTION_INTERVAL=900
DB_NAME=bgp_monitor_prod
```

## 📱 Configurações Avançadas do Telegram

### Formatação Rica

```bash
# Habilitar HTML/Markdown
TELEGRAM_PARSE_MODE=HTML
TELEGRAM_USE_EMOJIS=true

# Configurações de alertas
TELEGRAM_SILENT_MODE=false          # Notificações normais
TELEGRAM_CRITICAL_ONLY=false       # Apenas alertas críticos
```

### Múltiplos Destinos

```bash
# Chat IDs separados por vírgula para diferentes tipos
TELEGRAM_CHAT_ID=-1001234567890                    # Chat principal
TELEGRAM_CRITICAL_CHAT_ID=-1001234567890          # Alertas críticos
TELEGRAM_INFO_CHAT_ID=-1009876543210              # Informações gerais
```

### Relatórios Automatizados

O sistema envia automaticamente:
- **Relatório Diário**: Resumo das últimas 24h
- **Alertas em Tempo Real**: Anomalias detectadas
- **Status de Saúde**: A cada 6 horas

## 🗂️ Arquivo de Configuração Completo

### Exemplo .env para Produção

```bash
# === BGP Monitor v1.0.0 Production Configuration ===

# === DATABASE ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bgp_monitor
DB_USER=bgp_monitor
DB_PASSWORD=ultra_secure_password_change_me

# === TELEGRAM ===
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_real_token
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_PARSE_MODE=HTML
TELEGRAM_USE_EMOJIS=true

# === APPLICATION ===
HOST=0.0.0.0
PORT=8000
DEBUG=false

# === BGP MONITORING ===
COLLECTION_INTERVAL=900
API_RATE_LIMIT_PER_ASN=45
API_BATCH_SIZE=3
API_TIMEOUT=30

# === ANOMALY DETECTION ===
ANOMALY_SENSITIVITY=2.0
MIN_HISTORICAL_DAYS=7
BASELINE_CALCULATION_DAYS=30

# === DATA MANAGEMENT ===
DATA_RETENTION_DAYS=365
CLEANUP_INTERVAL_HOURS=24

# === LOGGING ===
LOG_LEVEL=INFO
```

## ✅ Validação da Configuração

### Verificar Configuração

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar conectividade do banco
python -c "
from app.database.connection import DatabaseManager
import asyncio
async def test():
    db = DatabaseManager()
    await db.initialize()
    print('✅ Banco conectado com sucesso!')
    await db.close()
asyncio.run(test())
"

# Testar API
curl -s http://localhost:8000/health | jq

# Testar Telegram
curl -X POST "http://localhost:8000/test/telegram" \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste de configuração BGP Monitor v1.0.0"}'
```

### Validar ASNs Configurados

```bash
# Listar ASNs ativos
curl -s "http://localhost:8000/asns" | jq '.[] | select(.enabled == true)'

# Verificar última coleta
curl -s "http://localhost:8000/dashboard" | jq '.last_collection'

# Status do scheduler
curl -s "http://localhost:8000/scheduler/status" | jq
```

### Debug de Configuração

```bash
# Executar em modo debug
DEBUG=true python main.py

# Verificar logs em tempo real
tail -f logs/bgp-monitor.log | grep -E "(ERROR|WARNING|DEBUG)"

# Testar coleta manual
curl -X POST "http://localhost:8000/collect/force" \
  -H "Content-Type: application/json" \
  -d '{"asn": 64512}'
```

## 🔄 Recarregamento de Configuração

### Aplicar Mudanças

```bash
# Para aplicar mudanças na configuração:

# 1. Parar o sistema
sudo systemctl stop bgp-monitor

# 2. Editar configuração
nano .env

# 3. Reiniciar o sistema  
sudo systemctl start bgp-monitor

# 4. Verificar status
sudo systemctl status bgp-monitor

# 5. Verificar logs
sudo journalctl -u bgp-monitor -f
```

### Recarregamento sem Downtime

```bash
# Recarregar configuração via API (se implementado)
curl -X POST "http://localhost:8000/admin/reload-config"

# Verificar se aplicou
curl -s "http://localhost:8000/health" | jq '.config_last_reload'
```

## 📈 Monitoramento da Configuração

### Métricas de Performance

```bash
# Verificar performance da coleta
curl -s "http://localhost:8000/metrics" | jq '.collection_performance'

# Estatísticas de rate limiting
curl -s "http://localhost:8000/metrics" | jq '.rate_limiting'

# Uso de memória e CPU
curl -s "http://localhost:8000/metrics" | jq '.system_metrics'
```

### Alertas de Configuração

O sistema alerta automaticamente sobre:
- **Problemas de conectividade** com PostgreSQL
- **Rate limiting** atingido com RIPE API
- **Disk space** baixo para logs/dados
- **Configurações inválidas** detectadas

## 📚 Próximos Passos

Após configurar o sistema:

1. [🔧 Aprenda a usar o sistema](USAGE.md)
2. [🌐 Explore a API REST](API.md)
3. [🏗️ Entenda a arquitetura](ARCHITECTURE.md)
4. [🔍 Troubleshooting](TROUBLESHOOTING.md)
