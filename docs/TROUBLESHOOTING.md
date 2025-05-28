# 🛠️ Guia de Solução de Problemas - BGP Monitor v2.0

Este guia abrangente ajuda a resolver problemas do BGP Monitor v2.0 com PostgreSQL e detecção de anomalias.

## 🔧 Problemas de Inicialização

### 1. **Aplicação não inicia**

#### **Erro: "Connection to PostgreSQL failed"**
```bash
# Verificar status do PostgreSQL
sudo systemctl status postgresql
sudo systemctl start postgresql

# Testar conexão manual
psql -U bgp_monitor -d bgp_monitor -h localhost -p 5432

# Verificar configuração no .env
cat /opt/bgp-monitor/.env | grep DATABASE
```

**Solução:**
```bash
# Recriar banco se necessário
sudo -u postgres psql
DROP DATABASE IF EXISTS bgp_monitor;
DROP USER IF EXISTS bgp_monitor;
CREATE USER bgp_monitor WITH PASSWORD 'sua_senha_segura';
CREATE DATABASE bgp_monitor OWNER bgp_monitor;
GRANT ALL PRIVILEGES ON DATABASE bgp_monitor TO bgp_monitor;
\q

# Reexecutar migrations
cd /opt/bgp-monitor
python -m alembic upgrade head
```

#### **Erro: "Module not found" ou dependências**
```bash
# Reinstalar dependências completas
cd /opt/bgp-monitor
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verificar versões críticas
pip list | grep -E "(fastapi|asyncpg|sqlalchemy|alembic)"
```

#### **Erro: "Permission denied" em arquivos**
```bash
# Corrigir permissões do diretório
sudo chown -R bgp-monitor:bgp-monitor /opt/bgp-monitor/
chmod +x /opt/bgp-monitor/install.sh
chmod 600 /opt/bgp-monitor/.env

# Verificar usuário do systemd
sudo systemctl status bgp-monitor
```

### 2. **Problemas de Porta/Binding**

#### **Erro: "Port 8000 already in use"**
```bash
# Identificar processo na porta
sudo ss -tulpn | grep :8000
sudo lsof -i :8000

# Alterar porta no .env
sed -i 's/PORT=8000/PORT=8001/' /opt/bgp-monitor/.env

# Reiniciar serviço
sudo systemctl restart bgp-monitor
```

## 🌐 Problemas de Conectividade

### 1. **Falhas na API RIPE**

#### **Erro: "Rate limited by RIPE API"**
```bash
# Verificar rate limiting atual
curl -s "https://stat.ripe.net/data/network-info/data.json?resource=AS64512" \
  -I | grep -i "x-rate"

# Ajustar configuração no .env
RATE_LIMIT_DELAY=60  # Aumentar delay entre requests
BATCH_SIZE=2         # Reduzir tamanho do batch
```

**Monitoramento contínuo:**
```bash
# Verificar logs do rate limiting
journalctl -u bgp-monitor -f | grep "rate.limit"

# Testar endpoint específico
curl -X POST http://localhost:8000/test/ripe-api \
  -H "Content-Type: application/json" \
  -d '{"asn": 64512}'
```

#### **Erro: "Connection timeout to RIPE"**
```bash
# Verificar conectividade de rede
curl -s --max-time 10 "https://stat.ripe.net/data/network-info/data.json?resource=AS1"

# Verificar proxy/firewall corporativo
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=http://proxy.empresa.com:8080

# Adicionar no .env se necessário
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=http://proxy.empresa.com:8080
```

### 2. **Problemas de DNS**
```bash
# Verificar resolução DNS
nslookup stat.ripe.net
dig stat.ripe.net

# Configurar DNS alternativo se necessário
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

## 💾 Problemas de Banco de Dados

### 1. **Erros de Conexão PostgreSQL**

#### **Erro: "Too many connections"**
```bash
# Verificar conexões ativas
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Verificar configuração do pool
grep -E "(min_size|max_size)" /opt/bgp-monitor/app/database/connection.py

# Ajustar limites PostgreSQL
sudo -u postgres psql -c "ALTER SYSTEM SET max_connections = 200;"
sudo systemctl restart postgresql
```

#### **Erro: "Deadlock detected"**
```bash
# Verificar logs PostgreSQL para deadlocks
sudo tail -f /var/log/postgresql/postgresql-15-main.log | grep -i deadlock

# Analisar queries lentas
sudo -u postgres psql bgp_monitor -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"
```

### 2. **Problemas de Performance**

#### **Queries lentas**
```sql
-- Verificar índices faltantes
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE tablename IN ('bgp_data', 'anomalies', 'asns');

-- Analisar planos de execução
EXPLAIN ANALYZE 
SELECT * FROM bgp_data 
WHERE asn = 64512 AND timestamp >= NOW() - INTERVAL '7 days';

-- Recriar índices se necessário
REINDEX TABLE bgp_data;
```

#### **Espaço em disco**
```bash
# Verificar tamanho das tabelas
sudo -u postgres psql bgp_monitor -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Limpeza manual de dados antigos
curl -X POST http://localhost:8000/admin/cleanup \
  -H "Content-Type: application/json" \
  -d '{"older_than_days": 365, "dry_run": false}'
```

## 📱 Problemas do Telegram

### 1. **Bot não responde**

#### **Erro: "Unauthorized: bot token invalid"**
```bash
# Verificar token no .env
grep TELEGRAM_BOT_TOKEN /opt/bgp-monitor/.env

# Testar token via API direta
curl "https://api.telegram.org/bot<SEU_TOKEN>/getMe"

# Gerar novo token se necessário via @BotFather
```

#### **Erro: "Chat not found"**
```bash
# Verificar chat_id correto
grep TELEGRAM_CHAT_ID /opt/bgp-monitor/.env

# Obter chat_id via bot
curl "https://api.telegram.org/bot<SEU_TOKEN>/getUpdates"

# Testar envio manual
curl -X POST http://localhost:8000/telegram/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste de conectividade"}'
```

### 2. **Mensagens não chegam**

#### **Problema de rate limiting Telegram**
```bash
# Verificar logs de rate limiting
journalctl -u bgp-monitor | grep -i "telegram.*rate"

# Verificar configuração de rate limiting
curl http://localhost:8000/telegram/status | jq '.rate_limiting'
```

#### **Bot banido ou bloqueado**
```bash
# Verificar status do bot no chat
curl "https://api.telegram.org/bot<SEU_TOKEN>/getChatMember?chat_id=<CHAT_ID>&user_id=<BOT_ID>"

# Logs detalhados de entrega
curl http://localhost:8000/telegram/history?limit=20
```

## 🔍 Problemas de Detecção de Anomalias

### 1. **Anomalias não são detectadas**

#### **Baseline insuficiente**
```bash
# Verificar quantidade de dados históricos
curl "http://localhost:8000/historical/64512?days=30" | jq '.data | length'

# Forçar recálculo de baseline
curl -X POST http://localhost:8000/admin/recalculate-baselines \
  -H "Content-Type: application/json" \
  -d '{"asn": 64512}'
```

#### **Thresholds muito altos**
```bash
# Verificar configuração atual
grep -E "(Z_SCORE_THRESHOLD|MINIMUM_BASELINE_DAYS)" /opt/bgp-monitor/.env

# Ajustar sensibilidade
sed -i 's/Z_SCORE_THRESHOLD=2.5/Z_SCORE_THRESHOLD=2.0/' /opt/bgp-monitor/.env
sudo systemctl restart bgp-monitor
```

### 2. **Falsos positivos**

#### **Muitas anomalias irrelevantes**
```bash
# Analisar padrões de anomalias
curl http://localhost:8000/anomalies/stats | jq '.by_type'

# Ajustar thresholds específicos
# No .env:
SUDDEN_INCREASE_THRESHOLD=3.0
SUDDEN_DECREASE_THRESHOLD=2.8
INSTABILITY_THRESHOLD=2.2
```

#### **Anomalias durante manutenções**
```bash
# Implementar janelas de manutenção
curl -X POST http://localhost:8000/asns/64512/maintenance \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-05-28T02:00:00Z",
    "end_time": "2025-05-28T06:00:00Z",
    "description": "Manutenção programada"
  }'
```

## ⚙️ Problemas do Scheduler

### 1. **Coletas não executam**

#### **Scheduler parado**
```bash
# Verificar status do scheduler
curl http://localhost:8000/scheduler/status

# Verificar logs específicos
journalctl -u bgp-monitor | grep -i scheduler

# Reiniciar apenas o scheduler (se suportado)
curl -X POST http://localhost:8000/admin/restart-scheduler
```

#### **Erro em coletas específicas**
```bash
# Verificar histórico de coletas
curl http://localhost:8000/collect/history?limit=20

# Forçar coleta manual para debug
curl -X POST http://localhost:8000/collect/force \
  -H "Content-Type: application/json" \
  -d '{"asn": 64512}'

# Verificar logs detalhados da coleta
journalctl -u bgp-monitor -f | grep "collection_id"
```

### 2. **Performance de coletas**

#### **Coletas muito lentas**
```bash
# Analisar duração das coletas
curl http://localhost:8000/admin/logs?component=scheduler&limit=50 | \
  jq '.[] | select(.operation == "collect_data") | .duration_ms'

# Verificar configuração de batching
grep -E "(BATCH_SIZE|RATE_LIMIT_DELAY)" /opt/bgp-monitor/.env

# Otimizar configuração
BATCH_SIZE=5           # Aumentar se API permite
RATE_LIMIT_DELAY=30    # Reduzir com cuidado
MAX_CONCURRENT=3       # Paralelização
```

## 🔧 Ferramentas de Diagnóstico

### 1. **Health Check Completo**
```bash
# Verificação básica
curl http://localhost:8000/health

# Verificação detalhada
curl http://localhost:8000/test/validate-config | jq '.'

# Informações do sistema
curl http://localhost:8000/admin/system-info | jq '.'
```

### 2. **Logs Estruturados**
```bash
# Logs por componente
journalctl -u bgp-monitor | grep '"component": "bgp_service"'
journalctl -u bgp-monitor | grep '"component": "anomaly_service"'
journalctl -u bgp-monitor | grep '"component": "telegram_service"'

# Logs por severidade
journalctl -u bgp-monitor | grep '"level": "ERROR"'
journalctl -u bgp-monitor | grep '"level": "WARNING"'

# Logs com correlação
journalctl -u bgp-monitor | grep '"correlation_id": "abc123"'
```

### 3. **Métricas Detalhadas**
```bash
# Dashboard completo
curl http://localhost:8000/dashboard | jq '.'

# Métricas por ASN
curl http://localhost:8000/metrics?asn=64512

# Estatísticas de performance
curl http://localhost:8000/admin/performance-stats
```

## 🚨 Resolução de Problemas Críticos

### 1. **Sistema totalmente não responsivo**
```bash
# Verificar recursos do sistema
top -p $(pgrep -f "bgp-monitor")
free -h
df -h /opt/bgp-monitor

# Reiniciar serviço
sudo systemctl restart bgp-monitor

# Verificar logs durante inicialização
sudo systemctl restart bgp-monitor && journalctl -u bgp-monitor -f
```

### 2. **Corrupção de dados**
```bash
# Backup antes de qualquer ação
sudo -u postgres pg_dump bgp_monitor > /tmp/bgp_monitor_backup.sql

# Verificar integridade do banco
sudo -u postgres psql bgp_monitor -c "
SELECT schemaname, tablename, pg_size_pretty(pg_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname = 'public';"

# Recriar estrutura se necessário
cd /opt/bgp-monitor
python -m alembic downgrade base
python -m alembic upgrade head
```

### 3. **Recovery de emergência**
```bash
# Parar serviço
sudo systemctl stop bgp-monitor

# Restaurar backup do banco
sudo -u postgres psql -c "DROP DATABASE bgp_monitor;"
sudo -u postgres psql -c "CREATE DATABASE bgp_monitor OWNER bgp_monitor;"
sudo -u postgres psql bgp_monitor < /backup/bgp_monitor_latest.sql

# Restaurar configuração
cp /backup/config_latest.env /opt/bgp-monitor/.env

# Reiniciar com validação
sudo systemctl start bgp-monitor
curl http://localhost:8000/test/validate-config
```

## 📞 Suporte e Logs

### **Coleta de informações para suporte**
```bash
#!/bin/bash
# Script de coleta de debug
echo "=== BGP Monitor v2.0 Debug Info ===" > debug_info.txt
echo "Timestamp: $(date)" >> debug_info.txt
echo "" >> debug_info.txt

# Informações do sistema
echo "=== System Info ===" >> debug_info.txt
curl -s http://localhost:8000/admin/system-info >> debug_info.txt
echo "" >> debug_info.txt

# Status dos serviços
echo "=== Service Status ===" >> debug_info.txt
systemctl status bgp-monitor >> debug_info.txt
systemctl status postgresql >> debug_info.txt
echo "" >> debug_info.txt

# Últimos logs
echo "=== Recent Logs ===" >> debug_info.txt
journalctl -u bgp-monitor --since "1 hour ago" >> debug_info.txt
echo "" >> debug_info.txt

# Configuração (sem senhas)
echo "=== Configuration ===" >> debug_info.txt
grep -v "PASSWORD\|TOKEN\|SECRET" /opt/bgp-monitor/.env >> debug_info.txt

echo "Debug info collected in debug_info.txt"
```

### **Contato para suporte**
- **Logs críticos**: Sempre incluir últimas 100 linhas de logs
- **Configuração**: Arquivo .env (remover senhas/tokens)
- **Ambiente**: Versão OS, Python, PostgreSQL
- **Reprodução**: Passos para reproduzir o problema

---

**BGP Monitor v2.0** - Sistema robusto com ferramentas completas de diagnóstico e recuperação.

#### Erro: "IRR validation failed"
```bash
# Verificar conectividade IRR
dig whois.radb.net
telnet whois.radb.net 43

# Verificar configuração no .env
grep IRR_ .env
```

### 3. Problemas do Telegram

#### Notificações não chegam
```bash
# Verificar token do bot
grep TELEGRAM_BOT_TOKEN .env

# Testar manualmente
curl -X GET "https://api.telegram.org/bot<TOKEN>/getMe"

# Verificar chat ID
curl -X GET "https://api.telegram.org/bot<TOKEN>/getUpdates"
```

#### Bot não responde
```bash
# Verificar se bot está ativo
curl -X GET "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Enviar mensagem de teste
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Teste do BGP Monitor"
```

### 4. Problemas de Performance

#### CPU alta
```bash
# Verificar threads em uso
ps -eLf | grep python | grep bgp

# Ajustar intervalo de verificação no .env
echo "MONITOR_INTERVAL=300" >> .env  # 5 minutos
```

#### Memória alta
```bash
# Verificar uso de memória
ps aux | grep python | grep bgp

# Limpar cache interno (reiniciar aplicação)
./bgp-monitor.sh restart
```

### 5. Problemas da API

#### API retorna 500
```bash
# Verificar logs da aplicação
tail -f logs/bgp-monitor.log

# Verificar status dos serviços
curl http://localhost:8000/health
```

#### Endpoints não respondem
```bash
# Verificar se API está rodando
curl -s http://localhost:8000/health | jq .

# Verificar documentação da API
curl http://localhost:8000/docs
```

## 📊 Comandos de Diagnóstico

### Verificar Status Geral
```bash
# Status completo do sistema
./bgp-monitor.sh status

# Verificar health da API
curl -s http://localhost:8000/health | jq .

# Listar prefixos monitorados
./bgp-monitor.sh list-prefixes
```

### Verificar Logs
```bash
# Logs da aplicação (se configurado)
tail -f logs/bgp-monitor.log

# Logs do sistema
journalctl -u bgp-monitor -f

# Logs de erro Python
python app/main.py 2>&1 | tee debug.log
```

### Testar Componentes
```bash
# Testar verificação manual
curl -X POST http://localhost:8000/api/v1/prefixes/192.168.1.0%2F24/check

# Testar adição de prefixo
curl -X POST http://localhost:8000/api/v1/prefixes \
  -H "Content-Type: application/json" \
  -d '{"prefix":"10.0.0.0/24","description":"Teste"}'

# Verificar métricas
curl -s http://localhost:8000/metrics | grep bgp_
```

## 🐛 Debug Avançado

### Habilitar Debug Detalhado
```bash
# No .env, adicionar:
echo "LOG_LEVEL=DEBUG" >> .env

# Reiniciar aplicação
./bgp-monitor.sh restart
```

### Executar em Modo Debug
```bash
# Executar com debug Python
python -u app/main.py

# Executar com verbose
PYTHONUNBUFFERED=1 python app/main.py
```

### Verificar Dependências
```bash
# Listar pacotes instalados
pip list | grep -E "(fastapi|uvicorn|httpx|pandas|numpy)"

# Verificar versões compatíveis
python --version
pip --version
```

## ⚠️ Problemas Conhecidos

### 1. Rate Limiting
- **Problema**: RIPE API limita requisições
- **Solução**: Usar cache interno e intervalos maiores
- **Configuração**: `MONITOR_INTERVAL=300` no .env

### 2. Timeout em Redes Lentas
- **Problema**: Timeouts em APIs externas
- **Solução**: Aumentar timeout no .env
- **Configuração**: `HTTP_TIMEOUT=30`

### 3. Encoding de Caracteres
- **Problema**: Caracteres especiais em notificações
- **Solução**: Usar UTF-8 no sistema
- **Comando**: `export LANG=en_US.UTF-8`

## 🆘 Suporte

### Informações para Suporte
Ao reportar problemas, inclua:

```bash
# Informações do sistema
uname -a
python --version
pip --version

# Status da aplicação
./bgp-monitor.sh status

# Configuração (sem dados sensíveis)
cat .env | grep -v TOKEN | grep -v SECRET

# Últimas linhas de log
tail -20 logs/bgp-monitor.log
```

### Reset Completo
Se nada funcionar, reset completo:

```bash
# Parar aplicação
./bgp-monitor.sh stop

# Limpar cache Python
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Recriar configuração
cp .env.example .env
# Editar .env com suas configurações

# Reiniciar
./bgp-monitor.sh start
```

---

Para mais ajuda, consulte os outros documentos em `/docs/` ou verifique o README.md principal.
