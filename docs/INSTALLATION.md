# 📦 Instalação do BGP Monitor v1.0.0

Guia completo de instalação do BGP Monitor v1.0.0 com **script de instalação unificado** e documentação de configuração completa.

## 📋 Pré-requisitos

### Sistema Operacional
- **Ubuntu 20.04+** ou **Debian 10+**
- **Python 3.8+**
- **PostgreSQL 12+**
- **4GB RAM** mínimo (8GB recomendado)
- **20GB espaço em disco** (para dados históricos)

### Permissões Necessárias
- Acesso root ou sudo
- Acesso à internet para download de dependências
- Permissões para criar usuários e banco de dados PostgreSQL

## 🚀 Instalação com Script Unificado (Recomendado)

### Novo Script de Instalação Único

A versão 1.0.0 introduz um **script de instalação unificado** que simplifica todo o processo:

```bash
# 1. Clonar ou extrair o projeto
cd /opt
sudo git clone https://github.com/netovaat/bgp-monitor.git
cd bgp-monitor

# 2. Executar instalação unificada
sudo chmod +x install.sh
sudo ./install.sh

# 3. Configurar variáveis (use .env.example como referência)
sudo cp .env.example .env
sudo nano .env

# 4. Iniciar serviço
sudo systemctl start bgp-monitor
sudo systemctl status bgp-monitor
```

### Funcionalidades do Script Unificado

O novo `install.sh` oferece:

- ✅ **Validação completa** do sistema operacional e dependências
- ✅ **Instalação automática** de PostgreSQL e Redis
- ✅ **Configuração de usuários** e bancos de dados
- ✅ **Ambiente Python virtual** otimizado
- ✅ **Migrações Alembic** automáticas
- ✅ **Serviço systemd** configurado automaticamente
- ✅ **Testes funcionais** automáticos
- ✅ **Logs coloridos** durante todo o processo
- ✅ **Recuperação de erros** inteligente
- ✅ **Limpeza automática** em caso de falha

## ⚙️ Configuração Completa com .env.example

### Documentação de Configuração Detalhada

A versão 1.0.0 inclui um arquivo `.env.example` **completamente documentado** com todas as variáveis de configuração:

```bash
# Copiar arquivo de exemplo
sudo cp .env.example .env

# Editar configurações
sudo nano .env
```

### Seções de Configuração Disponíveis

O arquivo `.env.example` está organizado nas seguintes seções:

- 🗄️ **Database Configuration** - PostgreSQL e conexões
- 🚀 **Cache Configuration** - Redis e performance
- 🌐 **HTTP Server Configuration** - Host, porta e debug
- 📡 **BGP Monitoring Configuration** - Intervalos e rate limiting
- 🔔 **Alert System Configuration** - Telegram e notificações
- 📊 **Anomaly Detection Configuration** - Sensibilidade e thresholds
- 🧹 **Data Retention Configuration** - Limpeza automática
- 📝 **Logging Configuration** - Níveis e formatação
- 🌍 **RIPE API Configuration** - Configurações específicas da API

### Configuração Mínima Necessária

Para funcionamento básico, configure pelo menos:

```bash
# Banco de dados
DB_HOST=localhost
DB_USER=bgp_monitor
DB_PASSWORD=sua_senha_segura

# Telegram (opcional)
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_CHAT_ID=seu_chat_id

# Aplicação
HOST=0.0.0.0
PORT=8000
```
sudo ./install.sh
```

## 🔧 Instalação Manual Detalhada

### Passo 1: Preparar o Sistema

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx supervisor \
    curl wget git \
    build-essential libpq-dev
```

### Passo 2: Configurar PostgreSQL

```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco de dados
sudo -u postgres psql << EOF
CREATE USER bgpmonitor WITH PASSWORD 'bgp_secure_2024!';
CREATE DATABASE bgpmonitor OWNER bgpmonitor;
GRANT ALL PRIVILEGES ON DATABASE bgpmonitor TO bgpmonitor;
ALTER USER bgpmonitor CREATEDB;
\\q
EOF
```

### Passo 3: Criar Usuário do Sistema

```bash
# Criar usuário dedicado
sudo useradd -m -s /bin/bash bgpmonitor
sudo usermod -aG sudo bgpmonitor
```

### Passo 4: Instalar BGP Monitor

```bash
# Extrair para diretório correto
sudo mkdir -p /opt
sudo tar -xzf bgp-monitor-v1.0.0.tar.gz -C /opt/
sudo chown -R bgpmonitor:bgpmonitor /opt/bgp-monitor
```

### Passo 5: Configurar Ambiente Python

```bash
# Mudar para usuário bgpmonitor
sudo -u bgpmonitor bash

# Criar ambiente virtual
cd /opt/bgp-monitor
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 6: Configurar Environment

```bash
# Criar arquivo de configuração
sudo -u bgpmonitor cp /opt/bgp-monitor/.env.example /opt/bgp-monitor/.env

# Editar configurações (ajustar conforme necessário)
sudo -u bgpmonitor nano /opt/bgp-monitor/.env
```

**Configuração mínima no .env:**
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bgpmonitor
DB_USER=bgpmonitor
DB_PASSWORD=bgp_secure_2024!

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Monitoring
ENABLE_ANOMALY_DETECTION=true
ANOMALY_THRESHOLD=0.3
CHECK_INTERVAL=300

# Telegram (opcional)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Passo 7: Inicializar Banco de Dados

```bash
# Ativar ambiente virtual
cd /opt/bgp-monitor
source venv/bin/activate

# Executar migrations
alembic upgrade head

# Verificar tabelas criadas
python3 -c "
import asyncio
from app.database.connection import db_manager
from sqlalchemy import text

async def check_tables():
    await db_manager.initialize()
    async with db_manager.get_session() as session:
        result = await session.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\';'))
        tables = result.fetchall()
        print('Tabelas criadas:')
        for table in tables:
            print(f'  - {table[0]}')
    await db_manager.close()

asyncio.run(check_tables())
"
```

### Passo 8: Configurar ASNs para Monitoramento

```bash
# Configurar ASNs iniciais
sudo -u bgpmonitor python3 setup_asns.py
```

### Passo 9: Configurar Serviços do Sistema

```bash
# Criar arquivo de serviço systemd
sudo tee /etc/systemd/system/bgp-monitor.service << EOF
[Unit]
Description=BGP Monitor v1.0.0
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=bgpmonitor
Group=bgpmonitor
WorkingDirectory=/opt/bgp-monitor
Environment=PATH=/opt/bgp-monitor/venv/bin
ExecStart=/opt/bgp-monitor/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd e habilitar serviço
sudo systemctl daemon-reload
sudo systemctl enable bgp-monitor
```

### Passo 10: Configurar Nginx (Opcional)

```bash
# Criar configuração do Nginx
sudo tee /etc/nginx/sites-available/bgp-monitor << EOF
server {
    listen 80;
    server_name your-domain.com;  # Alterar para seu domínio
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Habilitar site
sudo ln -s /etc/nginx/sites-available/bgp-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## ✅ Verificação da Instalação

### Iniciar o Sistema

```bash
# Iniciar BGP Monitor
sudo systemctl start bgp-monitor

# Verificar status
sudo systemctl status bgp-monitor

# Verificar logs
sudo journalctl -u bgp-monitor -f
```

### Testar API

```bash
# Testar endpoint de health
curl http://localhost:8000/health

# Testar endpoint de configuração
curl http://localhost:8000/api/v1/config

# Testar coleta de dados
curl http://localhost:8000/api/v1/asn/13335/current
```

### Verificar Banco de Dados

```bash
# Conectar ao PostgreSQL
sudo -u postgres psql -d bgpmonitor

# Verificar tabelas
\dt

# Verificar dados (após algumas coletas)
SELECT COUNT(*) FROM asn_snapshots;
SELECT COUNT(*) FROM prefix_history;
\q
```

## 🔧 Problemas Conhecidos e Soluções

### Erro: ModuleNotFoundError: No module named 'psycopg2'

**Solução:**
```bash
sudo -u bgpmonitor bash -c "
    source /opt/bgp-monitor/venv/bin/activate
    pip install psycopg2-binary==2.9.9
"
```

### Erro: FileNotFoundError: 'alembic/script.py.mako'

**Solução:**
```bash
sudo -u bgpmonitor bash -c "cat > /opt/bgp-monitor/alembic/script.py.mako << 'EOF'
\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else \"\"}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else \"pass\"}

def downgrade() -> None:
    ${downgrades if downgrades else \"pass\"}
EOF"
```

### Erro: Could not determine revision id from filename

**Solução:**
```bash
# Remover migrations corrompidas
sudo -u bgpmonitor rm -f /opt/bgp-monitor/alembic/versions/*_initial_migration.py
sudo -u bgpmonitor rm -rf /opt/bgp-monitor/alembic/versions/__pycache__

# Recriar migration inicial
sudo -u bgpmonitor bash -c "
    cd /opt/bgp-monitor
    source venv/bin/activate
    alembic revision --autogenerate -m 'Initial migration'
    alembic upgrade head
"
```

### Usar Script de Correção Automática

Para resolver todos os problemas conhecidos automaticamente:

```bash
cd /opt/bgp-monitor
sudo chmod +x aplicar-correções.sh
sudo ./aplicar-correções.sh
```

## 📊 Configurações de Performance

### Para Ambientes de Produção

```bash
# Ajustar configurações do PostgreSQL
sudo tee -a /etc/postgresql/*/main/postgresql.conf << EOF

# Configurações para BGP Monitor
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
EOF

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### Para Monitoramento de Muitos ASNs

```bash
# Ajustar no arquivo .env
echo "
# Performance para muitos ASNs
MAX_CONCURRENT_REQUESTS=20
BATCH_SIZE=10
REQUEST_DELAY=0.5
RATE_LIMIT_PER_MINUTE=300
" >> /opt/bgp-monitor/.env
```

## 🔄 Atualização

### Atualizar para Nova Versão

```bash
# Parar o serviço
sudo systemctl stop bgp-monitor

# Backup dos dados
sudo -u postgres pg_dump bgpmonitor > /tmp/bgp-backup-$(date +%Y%m%d).sql

# Extrair nova versão
sudo tar -xzf bgp-monitor-v1.0.0.tar.gz -C /opt/
sudo chown -R bgpmonitor:bgpmonitor /opt/bgp-monitor

# Atualizar dependências
sudo -u bgpmonitor bash -c "
    cd /opt/bgp-monitor
    source venv/bin/activate
    pip install -r requirements.txt
"

# Executar migrations
sudo -u bgpmonitor bash -c "
    cd /opt/bgp-monitor
    source venv/bin/activate
    alembic upgrade head
"

# Reiniciar serviço
sudo systemctl start bgp-monitor
```

## 🔍 Monitoramento Pós-Instalação

### Logs Importantes

```bash
# Logs do sistema
sudo journalctl -u bgp-monitor -f

# Logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log

# Logs do Nginx (se configurado)
sudo tail -f /var/log/nginx/access.log
```

### Métricas de Sistema

```bash
# Status do BGP Monitor
curl http://localhost:8000/api/v1/admin/system-info

# Verificar uso de recursos
htop
iostat 1
```

## 🆘 Suporte

Para problemas não cobertos neste guia:

1. **Consulte**: `docs/TROUBLESHOOTING.md`
2. **Verifique logs**: `sudo journalctl -u bgp-monitor`
3. **Execute diagnóstico**: `python3 test_bgp_system.py`
4. **Consulte**: `CORREÇÕES-INSTALAÇÃO.md` para problemas conhecidos

---

**Versão**: 1.0.0 Final  
**Compatibilidade**: Ubuntu 20.04+ / Debian 10+ / Python 3.8+  
**Última atualização**: Janeiro 2025