# ⚙️ Configuração

Guia completo de configuração do BGP Monitor v1.0.

## 📄 Arquivo .env

O BGP Monitor usa um único arquivo `.env` para todas as configurações.

### Configuração Básica

```bash
# BGP Monitor Configuration

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_example_token
TELEGRAM_CHAT_ID=-1001234567890

# Target ASN to monitor
TARGET_ASN=64512

# Application Settings
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Monitoring Intervals (in seconds)
PREFIX_CHECK_INTERVAL=300     # 5 minutos
PEER_CHECK_INTERVAL=600       # 10 minutos
IRR_CHECK_INTERVAL=900        # 15 minutos
HEALTH_CHECK_INTERVAL=60      # 1 minuto

# Monitoring Thresholds
MIN_PEERS=3                   # Mínimo de peers BGP
MIN_UPSTREAMS=2              # Mínimo de upstreams

# Log Level
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
```

## 🤖 Configuração do Telegram

### 1. Criar Bot do Telegram

1. Acesse [@BotFather](https://t.me/BotFather) no Telegram
2. Envie `/newbot`
3. Escolha um nome para seu bot (ex: "Meu BGP Monitor")
4. Escolha um username (ex: "meu_bgp_monitor_bot")
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
# Testar envio de mensagem
./bgp-monitor.sh test-telegram
```

## 🌐 Configuração de Rede

### ASN Alvo

Configure o ASN que você deseja monitorar:

```bash
TARGET_ASN=64512  # Substitua pelo seu ASN
```

### Prefixos para Monitoramento

Adicione prefixos via API ou script:

```bash
# Via script
./bgp-monitor.sh add-prefix "203.0.113.0/24" "Rede principal"
./bgp-monitor.sh add-prefix "198.51.100.0/24" "Rede secundária"

# Via API
curl -X POST http://localhost:8000/prefixes \
  -H "Content-Type: application/json" \
  -d '{"prefix": "203.0.113.0/24", "description": "Rede principal"}'
```

## ⏱️ Configuração de Intervalos

Ajuste os intervalos de verificação conforme sua necessidade:

```bash
# Verificações mais frequentes (uso mais recursos)
PREFIX_CHECK_INTERVAL=120     # 2 minutos
PEER_CHECK_INTERVAL=300       # 5 minutos

# Verificações menos frequentes (economiza recursos)
PREFIX_CHECK_INTERVAL=900     # 15 minutos
PEER_CHECK_INTERVAL=1800      # 30 minutos
```

## 🔍 Configuração de Thresholds

Configure limites para alertas:

```bash
# Alertar se menos de 3 peers BGP
MIN_PEERS=3

# Alertar se menos de 2 upstreams
MIN_UPSTREAMS=2

# Timeout para consultas à RIPE API (segundos)
API_TIMEOUT=30

# Máximo de tentativas para consultas
MAX_RETRIES=3
```

## 📊 Configuração de Logs

Ajuste o nível de logging:

```bash
# Níveis disponíveis
LOG_LEVEL=DEBUG    # Máximo detalhe (desenvolvimento)
LOG_LEVEL=INFO     # Informações gerais (produção)
LOG_LEVEL=WARNING  # Apenas alertas e erros
LOG_LEVEL=ERROR    # Apenas erros críticos
```

### Logs Estruturados

O sistema usa logs estruturados (JSON) por padrão. Para alternar:

```python
# Em app/core/config.py
STRUCTURED_LOGS = True   # JSON logs
STRUCTURED_LOGS = False  # Logs texto simples
```

## 🚀 Configuração para Produção

### 1. Segurança

```bash
# Desabilitar debug
DEBUG=false

# Bind apenas localhost se usar proxy reverso
HOST=127.0.0.1

# Usar porta não privilegiada
PORT=8000
```

### 2. Performance

```bash
# Intervalos otimizados para produção
PREFIX_CHECK_INTERVAL=300
PEER_CHECK_INTERVAL=600
IRR_CHECK_INTERVAL=900

# Logs menos verbosos
LOG_LEVEL=INFO
```

### 3. Monitoramento

```bash
# Habilitar métricas detalhadas
ENABLE_METRICS=true

# Salvar histórico de checks
SAVE_CHECK_HISTORY=true
```

## 🔧 Configurações Avançadas

### Proxy/Firewall

Se estiver atrás de proxy/firewall:

```bash
# Configurar proxy HTTP
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=http://proxy.empresa.com:8080

# Timeout maior para consultas
API_TIMEOUT=60
```

### Múltiplos ASNs (Futuro)

Para monitorar múltiplos ASNs:

```bash
# Lista de ASNs separados por vírgula
TARGET_ASNS=64512,65001,65002
```

## 📱 Configurações do Telegram Avançadas

### Formatação de Mensagens

```bash
# Habilitar formatação rica
TELEGRAM_PARSE_MODE=HTML     # HTML ou Markdown

# Incluir emoji nas mensagens
TELEGRAM_USE_EMOJIS=true

# Silenciar notificações não críticas
TELEGRAM_SILENT_MODE=false
```

### Múltiplos Destinos

```bash
# Chat IDs separados por vírgula
TELEGRAM_CHAT_IDS=-1001234567890,-1009876543210

# Diferentes níveis para diferentes chats
TELEGRAM_CRITICAL_CHAT_ID=-1001234567890
TELEGRAM_WARNING_CHAT_ID=-1009876543210
```

## 🗂️ Configuração de Arquivo

### Exemplo Completo (.env)

```bash
# BGP Monitor v1.0 Configuration

# === TELEGRAM CONFIGURATION ===
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_example_token
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_PARSE_MODE=HTML
TELEGRAM_USE_EMOJIS=true

# === MONITORING TARGET ===
TARGET_ASN=64512

# === APPLICATION SETTINGS ===
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# === MONITORING INTERVALS (seconds) ===
PREFIX_CHECK_INTERVAL=300
PEER_CHECK_INTERVAL=600
IRR_CHECK_INTERVAL=900
HEALTH_CHECK_INTERVAL=60

# === THRESHOLDS ===
MIN_PEERS=3
MIN_UPSTREAMS=2
API_TIMEOUT=30
MAX_RETRIES=3

# === FEATURES ===
ENABLE_METRICS=true
SAVE_CHECK_HISTORY=true
STRUCTURED_LOGS=true
```

## ✅ Validação da Configuração

### Testar Configuração

```bash
# Verificar sintaxe do .env
./bgp-monitor.sh validate-config

# Testar conectividade
./bgp-monitor.sh test-connectivity

# Verificar configurações carregadas
./bgp-monitor.sh config
```

### Debug de Configuração

```bash
# Executar em modo debug
DEBUG=true ./run.sh

# Verificar logs de inicialização
tail -f logs/bgp-monitor.log
```

## 🔄 Recarregamento de Configuração

Para aplicar mudanças na configuração:

```bash
# Parar o sistema
./bgp-monitor.sh stop

# Editar configuração
nano .env

# Reiniciar o sistema
./bgp-monitor.sh start

# Ou usar reload (se disponível)
./bgp-monitor.sh reload
```

## 📚 Próximos Passos

Após configurar o sistema:

1. [🔧 Aprenda a usar](USAGE.md)
2. [🌐 Explore a API](API.md)
3. [🔍 Troubleshooting](TROUBLESHOOTING.md)
