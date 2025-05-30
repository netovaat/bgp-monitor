#!/bin/bash
# BGP Monitor v2.1.0 - Script de Instalação Completa
# Este script instala e configura o BGP Monitor v2.1.0 com todas as correções

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner de início
echo -e "${BLUE}"
echo "================================================================"
echo "               BGP Monitor v2.1.0 - Instalação"
echo "================================================================"
echo -e "${NC}"

# Verificar se está executando como root
if [[ $EUID -ne 0 ]]; then
   log_error "Este script deve ser executado como root (use sudo)"
   exit 1
fi

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Verificar sistema operacional
log_info "Verificando sistema operacional..."
if ! command_exists lsb_release; then
    log_warning "lsb_release não encontrado, instalando..."
    apt-get update && apt-get install -y lsb-release
fi

OS_NAME=$(lsb_release -si)
OS_VERSION=$(lsb_release -sr)
log_info "Sistema detectado: $OS_NAME $OS_VERSION"

if [[ "$OS_NAME" != "Ubuntu" ]]; then
    log_warning "Este script foi testado apenas no Ubuntu. Continuando mesmo assim..."
fi

# 2. Atualizar sistema
log_info "Atualizando sistema..."
apt-get update

# 3. Instalar dependências do sistema
log_info "Instalando dependências do sistema..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    git \
    curl \
    wget \
    htop \
    supervisor \
    nginx \
    build-essential \
    libpq-dev \
    pkg-config

# 4. Verificar versão do Python
log_info "Verificando versão do Python..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
log_info "Python versão: $PYTHON_VERSION"

# Verificar se é Python 3.8+
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    log_success "Versão do Python é compatível (3.8+)"
else
    log_error "Python 3.8+ é necessário. Versão atual: $PYTHON_VERSION"
    exit 1
fi

# 5. Criar usuário bgpmonitor se não existir
log_info "Verificando usuário bgpmonitor..."
if ! id "bgpmonitor" &>/dev/null; then
    log_info "Criando usuário bgpmonitor..."
    useradd -r -s /bin/bash -d /opt/bgp-monitor bgpmonitor
    log_success "Usuário bgpmonitor criado"
else
    log_info "Usuário bgpmonitor já existe"
fi

# 6. Configurar PostgreSQL
log_info "Configurando PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Criar banco e usuário
sudo -u postgres psql << EOF
-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bgpmonitor') THEN
        CREATE ROLE bgpmonitor LOGIN PASSWORD 'bgpmonitor123';
    END IF;
END
\$\$;

-- Criar banco se não existir
SELECT 'CREATE DATABASE bgpmonitor OWNER bgpmonitor' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bgpmonitor')\gexec

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE bgpmonitor TO bgpmonitor;
EOF

log_success "PostgreSQL configurado"

# 7. Configurar Redis
log_info "Configurando Redis..."
systemctl start redis-server
systemctl enable redis-server
log_success "Redis configurado"

# 8. Definir diretório de instalação
INSTALL_DIR="/opt/bgp-monitor"
log_info "Diretório de instalação: $INSTALL_DIR"

# Se já existe, fazer backup
if [[ -d "$INSTALL_DIR" ]] && [[ "$INSTALL_DIR" != "$(pwd)" ]]; then
    BACKUP_DIR="${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    log_warning "Diretório já existe. Fazendo backup para: $BACKUP_DIR"
    mv "$INSTALL_DIR" "$BACKUP_DIR"
fi

# 9. Configurar diretório de trabalho atual como instalação
if [[ "$(pwd)" == "$INSTALL_DIR" ]]; then
    log_info "Usando diretório atual para instalação"
else
    log_error "Este script deve ser executado de dentro do diretório $INSTALL_DIR"
    exit 1
fi

# 10. Definir propriedade do diretório
log_info "Configurando permissões do diretório..."
chown -R bgpmonitor:bgpmonitor "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

# 11. Criar ambiente virtual Python
log_info "Criando ambiente virtual Python..."
sudo -u bgpmonitor python3 -m venv "$INSTALL_DIR/venv"
log_success "Ambiente virtual criado"

# 12. Ativar ambiente virtual e instalar dependências
log_info "Instalando dependências Python..."
sudo -u bgpmonitor bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
EOF
log_success "Dependências Python instaladas"

# 13. Aplicar correções críticas de imports
log_info "Aplicando correções críticas de imports..."

# Correção 1: Verificar e corrigir import do BGPScheduler
log_info "  Verificando import do BGPScheduler..."
if grep -q "from scheduler import BGPScheduler" app/services/scheduler.py 2>/dev/null; then
    log_info "  Corrigindo import incorreto no scheduler.py..."
    sudo -u bgpmonitor sed -i 's/from scheduler import BGPScheduler, scheduler/from app.services.scheduler import BGPScheduler as _BGPScheduler, scheduler/' app/services/scheduler.py
    log_success "  Import do BGPScheduler corrigido"
else
    log_success "  Import do BGPScheduler já está correto"
fi

# Correção 2: Verificar função get_db no database/__init__.py
log_info "  Verificando função get_db..."
if ! grep -q "def get_db" app/database/__init__.py 2>/dev/null; then
    log_info "  Adicionando função get_db ao database/__init__.py..."
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
    log_success "  Função get_db adicionada"
else
    log_success "  Função get_db já existe"
fi

log_success "Correções de imports aplicadas"

# 14. Configurar arquivo .env se não existir
log_info "Configurando arquivo .env..."
if [[ ! -f "$INSTALL_DIR/.env" ]]; then
    if [[ -f "$INSTALL_DIR/.env.example" ]]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        log_info "Arquivo .env criado a partir do .env.example"
    else
        log_warning "Arquivo .env.example não encontrado, criando .env básico"
        cat > "$INSTALL_DIR/.env" << EOF
# BGP Monitor v2.1.0 Configuration
DATABASE_URL=postgresql://bgpmonitor:bgpmonitor123@localhost/bgpmonitor
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DEBUG=false
EOF
    fi
    chown bgpmonitor:bgpmonitor "$INSTALL_DIR/.env"
else
    log_info "Arquivo .env já existe"
fi

# 15. Executar migrações do banco
log_info "Executando migrações do banco de dados..."
sudo -u bgpmonitor bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
python -m alembic upgrade head
EOF
log_success "Migrações executadas"

# 16. Testar importações críticas
log_info "Testando importações Python..."
sudo -u bgpmonitor bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
python -c "
import sys
sys.path.insert(0, '.')

# Testar importações críticas
try:
    from app.main import app
    print('✓ app.main: OK')
    
    from app.database import get_db
    print('✓ get_db: OK')
    
    from app.services.scheduler import BGPScheduler
    print('✓ BGPScheduler: OK')
    
    print('✓ Todas as importações funcionaram')
except Exception as e:
    print(f'✗ Erro na importação: {e}')
    sys.exit(1)
"
EOF
log_success "Importações testadas com sucesso"

# 17. Configurar serviço systemd
log_info "Configurando serviço systemd..."
cat > /etc/systemd/system/bgp-monitor.service << EOF
[Unit]
Description=BGP Monitor v2.1.0
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=bgpmonitor
Group=bgpmonitor
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$INSTALL_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable bgp-monitor
log_success "Serviço systemd configurado"

# 18. Configurar scripts de controle
log_info "Configurando scripts de controle..."
chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true

# 19. Teste final
log_info "Executando teste final do sistema..."
sudo -u bgpmonitor bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
timeout 10s uvicorn app.main:app --host 127.0.0.1 --port 8001 &
SERVER_PID=\$!
sleep 5

# Testar se o servidor responde
if curl -s http://127.0.0.1:8001/health >/dev/null; then
    echo "✓ Servidor responde corretamente"
    kill \$SERVER_PID 2>/dev/null || true
else
    echo "✗ Servidor não responde"
    kill \$SERVER_PID 2>/dev/null || true
    exit 1
fi
EOF

# 20. Relatório final
echo
echo -e "${GREEN}"
echo "================================================================"
echo "                   INSTALAÇÃO CONCLUÍDA!"
echo "================================================================"
echo -e "${NC}"
echo
log_success "BGP Monitor v2.1.0 foi instalado com sucesso!"
echo
echo -e "${BLUE}Informações importantes:${NC}"
echo "• Diretório de instalação: $INSTALL_DIR"
echo "• Usuário do sistema: bgpmonitor"
echo "• Banco de dados: PostgreSQL (bgpmonitor/bgpmonitor123)"
echo "• Cache: Redis"
echo "• Porta padrão: 8000"
echo
echo -e "${BLUE}Para iniciar o serviço:${NC}"
echo "  sudo systemctl start bgp-monitor"
echo
echo -e "${BLUE}Para verificar status:${NC}"
echo "  sudo systemctl status bgp-monitor"
echo
echo -e "${BLUE}Para iniciar manualmente:${NC}"
echo "  cd $INSTALL_DIR"
echo "  sudo -u bgpmonitor bash"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo
echo -e "${BLUE}Para acessar a aplicação:${NC}"
echo "  http://localhost:8000"
echo "  http://localhost:8000/docs (Swagger UI)"
echo
echo -e "${YELLOW}IMPORTANTE:${NC}"
echo "• Configure o arquivo .env com suas credenciais do Telegram"
echo "• Ajuste as configurações conforme necessário"
echo "• Consulte a documentação em docs/ para mais detalhes"
echo
log_success "Instalação completa! Sistema pronto para uso."
