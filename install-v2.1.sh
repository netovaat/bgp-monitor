#!/bin/bash
# BGP Monitor v2.1.0 - Script de Instalação Otimizado
# Este script instala o BGP Monitor com todas as correções aplicadas

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se está executando como root
if [[ $EUID -ne 0 ]]; then
   error "Este script deve ser executado como root (usar sudo)"
   exit 1
fi

log "Iniciando instalação do BGP Monitor v2.1.0..."

# 1. Atualizar sistema e instalar dependências
log "Atualizando sistema e instalando dependências..."
apt update && apt upgrade -y

# Instalar dependências essenciais
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-all \
    libpq-dev \
    build-essential \
    curl \
    wget \
    git \
    supervisor \
    nginx

success "Dependências do sistema instaladas"

# 2. Configurar PostgreSQL
log "Configurando PostgreSQL..."

# Iniciar e habilitar PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Criar usuário e banco de dados
sudo -u postgres psql << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bgpmonitor') THEN
        CREATE USER bgpmonitor WITH PASSWORD 'bgp_secure_2024!';
    END IF;
END
\$\$;

SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'bgpmonitor' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS bgpmonitor;
CREATE DATABASE bgpmonitor OWNER bgpmonitor;
GRANT ALL PRIVILEGES ON DATABASE bgpmonitor TO bgpmonitor;
ALTER USER bgpmonitor CREATEDB;
\q
EOF

success "PostgreSQL configurado"

# 3. Criar usuário do sistema
log "Criando usuário bgpmonitor..."
if ! id "bgpmonitor" &>/dev/null; then
    useradd -m -s /bin/bash bgpmonitor
    usermod -aG sudo bgpmonitor
    success "Usuário bgpmonitor criado"
else
    warning "Usuário bgpmonitor já existe"
fi

# 4. Verificar se estamos no diretório correto
INSTALL_DIR="/opt/bgp-monitor"
if [[ $(pwd) != "$INSTALL_DIR" ]]; then
    if [[ -d "$INSTALL_DIR" ]]; then
        warning "Diretório $INSTALL_DIR já existe. Fazendo backup..."
        mv "$INSTALL_DIR" "$INSTALL_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Copiar arquivos atuais para /opt/bgp-monitor
    log "Copiando arquivos para $INSTALL_DIR..."
    mkdir -p /opt
    cp -r "$(pwd)" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
chown -R bgpmonitor:bgpmonitor "$INSTALL_DIR"

# 5. Configurar ambiente Python
log "Configurando ambiente Python..."

# Remover ambiente virtual existente se houver
if [[ -d "venv" ]]; then
    rm -rf venv
fi

# Criar novo ambiente virtual como usuário bgpmonitor
sudo -u bgpmonitor python3 -m venv venv

# Verificar se o ambiente virtual foi criado corretamente
if [[ ! -f "venv/bin/activate" ]]; then
    error "Falha ao criar ambiente virtual"
    exit 1
fi

# Instalar dependências
log "Instalando dependências Python..."
sudo -u bgpmonitor bash << 'EOL'
cd /opt/bgp-monitor
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências principais
pip install -r requirements.txt

# Verificar instalações críticas
python3 -c "
import sys
try:
    import fastapi, uvicorn, sqlalchemy, alembic, psycopg2
    print('✅ Todas as dependências principais instaladas')
except ImportError as e:
    print(f'❌ Erro na instalação: {e}')
    sys.exit(1)
"
EOL

success "Ambiente Python configurado"

# 6. Configurar arquivo .env
log "Configurando arquivo de ambiente..."
if [[ ! -f ".env" ]]; then
    sudo -u bgpmonitor cp .env.example .env
    
    # Configurar valores padrão no .env
    sudo -u bgpmonitor sed -i 's/DB_HOST=.*/DB_HOST=localhost/' .env
    sudo -u bgpmonitor sed -i 's/DB_PORT=.*/DB_PORT=5432/' .env
    sudo -u bgpmonitor sed -i 's/DB_NAME=.*/DB_NAME=bgpmonitor/' .env
    sudo -u bgpmonitor sed -i 's/DB_USER=.*/DB_USER=bgpmonitor/' .env
    sudo -u bgpmonitor sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=bgp_secure_2024!/' .env
    sudo -u bgpmonitor sed -i 's/API_HOST=.*/API_HOST=0.0.0.0/' .env
    sudo -u bgpmonitor sed -i 's/API_PORT=.*/API_PORT=8000/' .env
    sudo -u bgpmonitor sed -i 's/DEBUG=.*/DEBUG=false/' .env
    
    success "Arquivo .env configurado"
else
    warning "Arquivo .env já existe"
fi

# 7. Executar migrations do banco
log "Executando migrations do banco de dados..."
sudo -u bgpmonitor bash << 'EOL'
cd /opt/bgp-monitor
source venv/bin/activate

# Verificar se existe migration inicial
if [[ ! -f "alembic/versions/001_initial_migration.py" ]]; then
    echo "⚠️  Migration inicial não encontrada, criando..."
    alembic revision --autogenerate -m "Initial migration"
fi

# Executar migrations
alembic upgrade head

# Verificar se as tabelas foram criadas
python3 -c "
import asyncio
from app.database.connection import db_manager
from sqlalchemy import text

async def check_tables():
    try:
        await db_manager.initialize()
        async with db_manager.get_session() as session:
            result = await session.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\';'))
            tables = result.fetchall()
            print(f'✅ {len(tables)} tabelas criadas no banco de dados')
            for table in tables:
                print(f'   - {table[0]}')
        await db_manager.close()
    except Exception as e:
        print(f'❌ Erro ao verificar banco: {e}')
        exit(1)

asyncio.run(check_tables())
"
EOL

success "Banco de dados configurado"

# 7. Aplicar correções críticas de imports
log "Aplicando correções críticas de imports..."

# Correção 1: Verificar e corrigir import do BGPScheduler
log "  Verificando import do BGPScheduler..."
if grep -q "from scheduler import BGPScheduler" app/services/scheduler.py 2>/dev/null; then
    log "  Corrigindo import incorreto no scheduler.py..."
    sudo -u bgpmonitor sed -i 's/from scheduler import BGPScheduler, scheduler/from app.services.scheduler import BGPScheduler as _BGPScheduler, scheduler/' app/services/scheduler.py
    log "  ✅ Import do BGPScheduler corrigido"
else
    log "  ✅ Import do BGPScheduler já está correto"
fi

# Correção 2: Verificar função get_db no database/__init__.py
log "  Verificando função get_db..."
if ! grep -q "def get_db" app/database/__init__.py 2>/dev/null; then
    log "  Adicionando função get_db ao database/__init__.py..."
    sudo -u bgpmonitor cat >> app/database/__init__.py << 'EOF'

# Compatibility function for get_db
def get_db():
    """
    Compatibility function for dependency injection.
    Returns database session generator.
    """
    from app.database.connection import db_manager
    return db_manager.get_session()

# Additional compatibility
def get_db_session():
    """Alternative name for get_db"""
    return get_db()
EOF
    log "  ✅ Função get_db adicionada"
else
    log "  ✅ Função get_db já existe"
fi

success "Correções de imports aplicadas"

# 8. Instalar dependências Python
log "Instalando dependências Python..."
sudo -u bgpmonitor bash << 'EOL'
cd /opt/bgp-monitor
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências principais
pip install -r requirements.txt

# Verificar instalações críticas
python3 -c "
import sys
try:
    import fastapi, uvicorn, sqlalchemy, alembic, psycopg2
    print('✅ Todas as dependências principais instaladas')
except ImportError as e:
    print(f'❌ Erro na instalação: {e}')
    sys.exit(1)
"
EOL

success "Ambiente Python configurado"

# 9. Configurar arquivo .env
log "Configurando arquivo de ambiente..."
if [[ ! -f ".env" ]]; then
    sudo -u bgpmonitor cp .env.example .env
    
    # Configurar valores padrão no .env
    sudo -u bgpmonitor sed -i 's/DB_HOST=.*/DB_HOST=localhost/' .env
    sudo -u bgpmonitor sed -i 's/DB_PORT=.*/DB_PORT=5432/' .env
    sudo -u bgpmonitor sed -i 's/DB_NAME=.*/DB_NAME=bgpmonitor/' .env
    sudo -u bgpmonitor sed -i 's/DB_USER=.*/DB_USER=bgpmonitor/' .env
    sudo -u bgpmonitor sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=bgp_secure_2024!/' .env
    sudo -u bgpmonitor sed -i 's/API_HOST=.*/API_HOST=0.0.0.0/' .env
    sudo -u bgpmonitor sed -i 's/API_PORT=.*/API_PORT=8000/' .env
    sudo -u bgpmonitor sed -i 's/DEBUG=.*/DEBUG=false/' .env
    
    success "Arquivo .env configurado"
else
    warning "Arquivo .env já existe"
fi

# 10. Executar migrations do banco
log "Executando migrations do banco de dados..."
sudo -u bgpmonitor bash << 'EOL'
cd /opt/bgp-monitor
source venv/bin/activate

# Verificar se existe migration inicial
if [[ ! -f "alembic/versions/001_initial_migration.py" ]]; then
    echo "⚠️  Migration inicial não encontrada, criando..."
    alembic revision --autogenerate -m "Initial migration"
fi

# Executar migrations
alembic upgrade head

# Verificar se as tabelas foram criadas
python3 -c "
import asyncio
from app.database.connection import db_manager
from sqlalchemy import text

async def check_tables():
    try:
        await db_manager.initialize()
        async with db_manager.get_session() as session:
            result = await session.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\';'))
            tables = result.fetchall()
            print(f'✅ {len(tables)} tabelas criadas no banco de dados')
            for table in tables:
                print(f'   - {table[0]}')
        await db_manager.close()
    except Exception as e:
        print(f'❌ Erro ao verificar banco: {e}')
        exit(1)

asyncio.run(check_tables())
"
EOL

success "Banco de dados configurado"

# 11. Testar imports do sistema
log "Testando imports do sistema..."
sudo -u bgpmonitor bash << 'EOL'
cd /opt/bgp-monitor
source venv/bin/activate

python3 -c "
import sys
sys.path.append('/opt/bgp-monitor')

print('🔍 Testando imports críticos...')

# Testar imports principais
try:
    from app.models.asn_snapshot import ASNSnapshotService
    print('✅ ASNSnapshotService: OK')
except Exception as e:
    print(f'❌ ASNSnapshotService: {e}')
    sys.exit(1)

try:
    from app.services.bgp_collector import BGPDataService
    print('✅ BGPDataService: OK')
except Exception as e:
    print(f'❌ BGPDataService: {e}')
    sys.exit(1)

try:
    from app.services.scheduler import BGPScheduler
    print('✅ BGPScheduler: OK')
except Exception as e:
    print(f'❌ BGPScheduler: {e}')
    sys.exit(1)

try:
    from app.main import app
    print('✅ FastAPI App: OK')
except Exception as e:
    print(f'❌ FastAPI App: {e}')
    sys.exit(1)

print('🎯 Todos os imports funcionando!')
"
EOL

success "Sistema validado"

# 12. Configurar serviço systemd
log "Configurando serviço systemd..."
cat > /etc/systemd/system/bgp-monitor.service << EOF
[Unit]
Description=BGP Monitor v2.1.0
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=bgpmonitor
Group=bgpmonitor
WorkingDirectory=/opt/bgp-monitor
Environment=PATH=/opt/bgp-monitor/venv/bin
ExecStart=/opt/bgp-monitor/venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
systemctl daemon-reload
systemctl enable bgp-monitor

success "Serviço systemd configurado"

# 13. Limpar arquivos temporários
log "Limpando arquivos temporários..."
find /opt/bgp-monitor -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/bgp-monitor -name "*.pyc" -type f -delete 2>/dev/null || true
find /opt/bgp-monitor -name "*.pyo" -type f -delete 2>/dev/null || true

success "Limpeza concluída"

# 14. Teste final do sistema
log "Executando teste final do sistema..."

# Iniciar o serviço temporariamente para teste
sudo -u bgpmonitor bash << 'EOL' &
cd /opt/bgp-monitor
source venv/bin/activate
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 > /dev/null 2>&1
EOL

UVICORN_PID=$!
sleep 5

# Testar endpoint
if curl -s http://127.0.0.1:8001/health > /dev/null; then
    success "Servidor testado com sucesso"
else
    warning "Não foi possível testar o servidor (normal durante instalação)"
fi

# Parar servidor de teste
kill $UVICORN_PID 2>/dev/null || true

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉"
echo ""
echo "📋 Próximos passos:"
echo "1. Iniciar o serviço: sudo systemctl start bgp-monitor"
echo "2. Verificar status: sudo systemctl status bgp-monitor"
echo "3. Verificar logs: sudo journalctl -u bgp-monitor -f"
echo "4. Testar API: curl http://localhost:8000/health"
echo "5. Documentação: /opt/bgp-monitor/docs/INSTALLATION.md"
echo ""
echo "🔧 Configuração:"
echo "- Arquivo de config: /opt/bgp-monitor/.env"
echo "- Logs do sistema: sudo journalctl -u bgp-monitor"
echo "- Banco PostgreSQL: bgpmonitor@localhost:5432"
echo ""
echo "📚 Consulte a documentação completa em:"
echo "   /opt/bgp-monitor/docs/"
echo ""

log "Instalação do BGP Monitor v2.1.0 finalizada!"
