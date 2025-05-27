# Guia de Solução de Problemas - BGP Monitor v1.0

Este guia ajuda a resolver problemas comuns do BGP Monitor simplificado.

## 🔧 Problemas Comuns

### 1. Aplicação não inicia

#### Erro: "Module not found"
```bash
# Solução: Instalar dependências
pip install -r requirements.txt

# Ou usando Python específico
python3 -m pip install -r requirements.txt
```

#### Erro: "Permission denied"
```bash
# Solução: Dar permissão aos scripts
chmod +x run.sh
chmod +x bgp-monitor.sh

# Ou executar diretamente
python app/main.py
```

#### Erro: "Port already in use"
```bash
# Verificar processo usando a porta 8000
sudo netstat -tlnp | grep :8000
sudo lsof -i :8000

# Matar processo se necessário
sudo kill -9 <PID>

# Ou alterar porta no .env
echo "PORT=8001" >> .env
```

### 2. Problemas de Conectividade

#### Erro: "Failed to connect to RIPE API"
```bash
# Verificar conectividade de rede
curl -s "https://stat.ripe.net/data/network-info/data.json?resource=1.1.1.0/24"

# Verificar proxy/firewall
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

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
