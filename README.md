# BGP Monitor v2.2.0

🚀 **Sistema avançado de monitoramento BGP com PostgreSQL e detecção de anomalias estatísticas**

Monitor em tempo real aproximadamente 50 ASNs, detecte alterações bruscas nos dados BGP, armazene histórico por 1 ano e receba alertas inteligentes. Sistema completo com rate limiting otimizado para não ser bloqueado pela API RIPE.

**✅ Versão 2.2.0 - Script de Instalação Unificado**
- **S## 📚 **Documentação Completa**

- [📖 Guia de Instalação](docs/INSTALLATION.md)
- [⚙️ Configuração Detalhada](docs/CONFIGURATION.md)
- [🔧 Guia de Uso](docs/USAGE.md)
- [🌐 Referência da API](docs/API.md)
- [🏗️ Arquitetura do Sistema](docs/ARCHITECTURE.md)
- [🔍 Troubleshooting](docs/TROUBLESHOOTING.md)

## 🆕 **Novidades da v2.2.0**

### 🎯 **Script de Instalação Unificado**
- **Um único script** substitui todos os scripts anteriores
- **Processo robusto** com validações automáticas e recuperação de erros
- **Logs coloridos** e informativos durante a instalação
- **Testes automáticos** de conectividade e funcionalidade

### 📖 **Documentação de Configuração Completa**
- **`.env.example` documentado** com todas as 25+ variáveis disponíveis
- **Seções organizadas** por funcionalidade (Database, Cache, BGP, Alertas, etc.)
- **Comentários explicativos** detalhados para cada configuração
- **Exemplos práticos** de configuração mínima e avançada

### 🧹 **Otimização e Limpeza**
- **Remoção de arquivos obsoletos** (10+ scripts antigos removidos)
- **Código consolidado** e estrutura mais limpa
- **Dependências otimizadas** no ambiente virtual
- **Performance melhorada** no processo de instalação

### 🔧 **Melhorias Técnicas**
- **Autor atualizado** para `netovaat` 
- **Compatibilidade mantida** com todas as funcionalidades da v2.1.1
- **Sistema de logs** aprimorado durante instalação
- **Validações robustas** de sistema e dependências

## ✨ Principais Funcionalidades

### 🎯 **Monitoramento Avançado**
- **Multi-ASN**: Monitore até 50+ ASNs simultaneamente
- **Histórico Completo**: 1 ano de dados históricos no PostgreSQL
- **Rate Limiting Inteligente**: 45s entre coletas + batches de 3-5 ASNs
- **Coleta Automática**: A cada 15 minutos com scheduler integrado

### 📊 **Detecção de Anomalias Estatísticas**
- **Análise Z-score**: Detecção baseada em desvio padrão
- **Baseline Dinâmico**: Cálculo automático de linha de base
- **Tipos de Anomalias**: Aumentos/diminuições súbitas, instabilidade
- **Sensibilidade Configurável**: Thresholds ajustáveis por necessidade

### 🔔 **Sistema de Alertas**
- **Telegram Integrado**: Alertas em tempo real em português
- **Severidades**: Crítico 🚨, Aviso ⚠️, Info ℹ️
- **Contexto Detalhado**: Causas possíveis e recomendações
- **Relatórios Diários**: Resumo automático de atividades

### 🚀 **API REST Completa**
- **Gestão de ASNs**: CRUD completo para configuração
- **Dados Históricos**: Acesso a snapshots e estatísticas
- **Dashboard**: Visão geral de todos os ASNs monitorados
- **Import/Export**: Backup e restauração de configurações

## 🏗️ **Arquitetura do Sistema**

```
┌─────────────────────────────────────────────────────────────┐
│                    BGP Monitor v2.0                        │
├─────────────────────────────────────────────────────────────┤
│  🌐 API REST (FastAPI)     │  📊 Dashboard & Endpoints      │
│  ⏰ Scheduler              │  🔄 Coletas Automáticas        │
│  🎯 ASN Manager            │  ⚙️ Configuração Multi-ASN     │
│  📈 Anomaly Detector       │  🧮 Análise Estatística        │
│  💾 Database Layer         │  🐘 PostgreSQL + Alembic       │
│  🔌 RIPE API Client        │  🌍 Rate Limiting Inteligente  │
│  📱 Telegram Alerts        │  🇧🇷 Mensagens em Português    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Instalação Rápida (Ubuntu/Debian)**

### **Instalação Automatizada com Script Unificado**

A versão 2.2.0 introduz um **script de instalação único** que substitui todos os scripts anteriores e oferece um processo simplificado e robusto:

```bash
# 1. Baixar e executar o script de instalação unificado
cd /opt
sudo git clone https://github.com/netovaat/bgp-monitor.git
cd bgp-monitor
sudo chmod +x install.sh
sudo ./install.sh

# 2. Configurar suas variáveis (use .env.example como referência)
sudo cp .env.example .env
sudo nano .env

# 3. Iniciar o serviço
sudo systemctl start bgp-monitor
sudo systemctl status bgp-monitor
```

### **Funcionalidades do Script de Instalação Unificado**

O novo `install.sh` inclui:
- ✅ **Validação completa** de sistema e dependências
- ✅ **Instalação automática** de PostgreSQL e Redis
- ✅ **Configuração de ambiente** Python virtual otimizado
- ✅ **Migrações de banco** com Alembic
- ✅ **Configuração de serviço** systemd
- ✅ **Testes funcionais** automáticos
- ✅ **Logs coloridos** e informativos
- ✅ **Recuperação de erros** inteligente

### **Opção 2: Instalação Manual**

#### **1. Dependências do Sistema**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    postgresql-15 \
    postgresql-client-15 \
    postgresql-contrib-15 \
    git \
    curl \
    build-essential

# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### **2. Configurar Banco de Dados**
```bash
# Criar usuário e banco
sudo -u postgres psql -c "CREATE USER bgp_monitor WITH PASSWORD 'bgp_monitor_password';"
sudo -u postgres psql -c "CREATE DATABASE bgp_monitor OWNER bgp_monitor;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bgp_monitor TO bgp_monitor;"
```

#### **3. Instalar Aplicação**
```bash
# Criar usuário do sistema
sudo useradd -r -s /bin/bash -d /opt/bgp-monitor -m bgpmonitor

# Clonar repositório
git clone https://github.com/seu-usuario/bgp-monitor.git /opt/bgp-monitor
sudo chown -R bgpmonitor:bgpmonitor /opt/bgp-monitor

# Criar ambiente virtual
cd /opt/bgp-monitor
sudo -u bgpmonitor python3.11 -m venv venv

# Instalar dependências Python
sudo -u bgpmonitor bash -c "
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"

# Configurar ambiente
sudo -u bgpmonitor cp .env.example .env
sudo -u bgpmonitor nano .env

# Executar migrações
sudo -u bgpmonitor bash -c "
    source venv/bin/activate
    alembic upgrade head
"
```

## ⚙️ **Configuração**

### **Configuração Completa com .env.example**

A versão 2.2.0 inclui um arquivo `.env.example` **completamente documentado** com todas as variáveis de configuração disponíveis:

```bash
# Copiar e editar configurações
sudo cp .env.example .env
sudo nano .env
```

O arquivo `.env.example` inclui:

- 🗄️ **Configurações de Banco de Dados** (PostgreSQL)
- 🚀 **Cache e Performance** (Redis)
- 🌐 **Servidor HTTP** (Host, porta, debug)
- 📡 **Monitoramento BGP** (intervalos, rate limiting, timeouts)
- 🔔 **Sistema de Alertas** (Telegram, severidades)
- 📊 **Detecção de Anomalias** (sensibilidade, baseline)
- 🧹 **Retenção de Dados** (limpeza automática)
- 📝 **Sistema de Logs** (níveis, formatação)
- 🌍 **API RIPE** (configurações específicas)

### **Configuração Mínima Essencial**

Para um funcionamento básico, configure apenas:

```bash
# === BANCO DE DADOS ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bgp_monitor
DB_USER=bgp_monitor
DB_PASSWORD=sua_senha_segura_aqui

# === TELEGRAM BOT (Opcional) ===
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# === APLICAÇÃO ===
HOST=0.0.0.0
PORT=8000
DEBUG=false
MIN_HISTORICAL_DAYS=7            # Mínimo de dados históricos
BASELINE_CALCULATION_DAYS=30     # Dias para baseline

# === RETENÇÃO DE DADOS ===
DATA_RETENTION_DAYS=365          # 1 ano de retenção
CLEANUP_INTERVAL_HOURS=24        # Limpeza diária

# === LOGS ===
LOG_LEVEL=INFO
```

### **Configurar ASNs para Monitoramento**

Via API REST:
```bash
# Adicionar ASN individual
curl -X POST "http://localhost:8000/asns" \
  -H "Content-Type: application/json" \
  -d '{
    "asn": 64512,
    "name": "Minha Empresa",
    "description": "ASN principal",
    "enabled": true
  }'

# Adicionar múltiplos ASNs
curl -X POST "http://localhost:8000/asns/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "asns": [
      {"asn": 15169, "name": "Google", "enabled": true},
      {"asn": 32934, "name": "Facebook", "enabled": true},
      {"asn": 13335, "name": "Cloudflare", "enabled": false}
    ]
  }'
```

## 🏃 **Execução em Background**

### **Como Serviço Systemd (Produção)**
```bash
# O script install.sh já cria o serviço automaticamente
# Comandos de gerenciamento:

# Iniciar serviço
sudo systemctl start bgp-monitor

# Parar serviço
sudo systemctl stop bgp-monitor

# Reiniciar serviço
sudo systemctl restart bgp-monitor

# Status do serviço
sudo systemctl status bgp-monitor

# Habilitar inicialização automática
sudo systemctl enable bgp-monitor

# Ver logs em tempo real
sudo journalctl -u bgp-monitor -f
```

### **Execução Manual em Background**
```bash
# Ativar ambiente virtual
cd /opt/bgp-monitor
source venv/bin/activate

# Executar em background
nohup python main.py > logs/bgp-monitor.log 2>&1 &

# Verificar processo
ps aux | grep main.py
```

## 📋 **Comandos Úteis**

### **Verificação de Status**
```bash
# Status da API
curl -s http://localhost:8000/health | jq

# Dashboard geral
curl -s http://localhost:8000/dashboard | jq

# Status do scheduler
curl -s http://localhost:8000/scheduler/status | jq

# Listar ASNs configurados
curl -s http://localhost:8000/asns | jq
```

### **Coleta de Dados**
```bash
# Forçar coleta de todos os ASNs
curl -X POST "http://localhost:8000/collect/force"

# Coleta de ASN específico
curl -X POST "http://localhost:8000/collect/force" \
  -H "Content-Type: application/json" \
  -d '{"asn": 64512}'

# Verificar última coleta
curl -s "http://localhost:8000/dashboard" | jq '.last_collection'
```

### **Gestão do Banco de Dados**
```bash
# Conectar ao banco
psql -h localhost -U bgp_monitor -d bgp_monitor

# Backup do banco
pg_dump -h localhost -U bgp_monitor bgp_monitor > backup_$(date +%Y%m%d).sql

# Verificar estatísticas
curl -s "http://localhost:8000/metrics" | jq '.database_stats'
```

## 📊 **API e Dashboard**

### **Endpoints Principais**
```bash
# Dashboard geral
curl http://localhost:8000/dashboard

# Dados históricos de ASN
curl http://localhost:8000/historical/64512

# Anomalias detectadas
curl http://localhost:8000/anomalies

# Estatísticas do sistema
curl http://localhost:8000/metrics

# Gestão de ASNs
curl http://localhost:8000/asns
```

### **Documentação Interativa**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 **Troubleshooting**

### **Problemas Comuns**

#### **Erro de Conexão PostgreSQL**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão manual
psql -h localhost -U bgp_monitor -d bgp_monitor -c "SELECT version();"

# Verificar logs do PostgreSQL
sudo journalctl -u postgresql -f
```

#### **Rate Limiting da API RIPE**
```bash
# Verificar configurações atuais
curl -s http://localhost:8000/metrics | jq '.rate_limiting'

# Ajustar se necessário em .env:
# API_RATE_LIMIT_PER_ASN=60
# API_BATCH_SIZE=2
```

#### **Problemas de Permissão**
```bash
# Corrigir permissões
sudo chown -R bgpmonitor:bgpmonitor /opt/bgp-monitor
sudo chmod +x /opt/bgp-monitor/install.sh
```

#### **Telegram não funciona**
```bash
# Testar bot manualmente
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | jq

# Testar via API
curl -X POST "http://localhost:8000/test/telegram" \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste BGP Monitor v2.0"}'
```

## 📈 **Monitoramento e Métricas**

### **Verificar Performance**
```bash
# Métricas de sistema
curl -s http://localhost:8000/metrics | jq

# Performance da coleta
curl -s http://localhost:8000/metrics | jq '.collection_performance'

# Estatísticas de anomalias
curl -s http://localhost:8000/anomalies/stats | jq
```

### **Logs Estruturados**
```bash
# Logs em tempo real
sudo journalctl -u bgp-monitor -f

# Filtrar por nível de erro
sudo journalctl -u bgp-monitor | grep ERROR

# Filtrar anomalias
sudo journalctl -u bgp-monitor | grep ANOMALY
```

## 📚 **Documentação Completa**

- [📖 Guia de Instalação](docs/INSTALLATION.md)
- [⚙️ Configuração Detalhada](docs/CONFIGURATION.md)
- [🔧 Guia de Uso](docs/USAGE.md)
- [🌐 Referência da API](docs/API.md)
- [🏗️ Arquitetura do Sistema](docs/ARCHITECTURE.md)
- [🔍 Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 **Contribuindo**

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 **Suporte**

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/bgp-monitor/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/bgp-monitor/wiki)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/bgp-monitor/discussions)

---

**BGP Monitor v2.0** - Monitoramento BGP profissional com PostgreSQL 🚀