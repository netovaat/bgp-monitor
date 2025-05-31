#!/bin/bash

# =============================================================================
# BGP Monitor v2.2.0 - Script de Instalação Unificado
# =============================================================================
# Autor: netovaat
# GitHub: https://github.com/netovaat/bgp-monitor
# 
# Este script instala e configura completamente o BGP Monitor v2.2.0
# incluindo todas as dependências, banco de dados e serviço systemd.
# =============================================================================

set -e  # Parar em caso de erro

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES E CONSTANTES
# -----------------------------------------------------------------------------
readonly VERSION="2.2.0"
readonly INSTALL_DIR="/opt/bgp-monitor"
readonly SERVICE_USER="bgpmonitor"
readonly DB_NAME="bgp_monitor"
readonly DB_USER="bgp_monitor"
readonly DB_PASS="bgp_monitor_password"

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# FUNÇÕES DE LOGGING
# -----------------------------------------------------------------------------
log_header() {
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}================================================================${NC}"
}

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

log_step() {
    echo -e "${CYAN}>>> $1${NC}"
}

# -----------------------------------------------------------------------------
# FUNÇÕES DE VALIDAÇÃO
# -----------------------------------------------------------------------------
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script deve ser executado como root (use sudo)"
        exit 1
    fi
}

check_os() {
    if ! command -v lsb_release >/dev/null 2>&1; then
        log_warning "Instalando lsb_release..."
        apt-get update -qq && apt-get install -y lsb-release
    fi
    
    local os_name=$(lsb_release -si)
    local os_version=$(lsb_release -sr)
    
    log_info "Sistema detectado: $os_name $os_version"
    
    if [[ "$os_name" != "Ubuntu" && "$os_name" != "Debian" ]]; then
        log_warning "Este script foi testado apenas no Ubuntu/Debian"
        read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

check_python() {
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python versão: $python_version"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "Python 3.8+ é necessário. Versão atual: $python_version"
        exit 1
    fi
    
    log_success "Versão do Python é compatível (3.8+)"
}

check_directory() {
    if [[ "$(pwd)" != "$INSTALL_DIR" ]]; then
        log_error "Este script deve ser executado de dentro do diretório $INSTALL_DIR"
        log_info "Diretório atual: $(pwd)"
        exit 1
    fi
    
    if [[ ! -f "app/main.py" ]]; then
        log_error "Arquivos do BGP Monitor não encontrados no diretório atual"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# FUNÇÕES DE INSTALAÇÃO
# -----------------------------------------------------------------------------
install_system_packages() {
    log_step "Atualizando sistema e instalando dependências"
    
    apt-get update -qq
    
    local packages=(
        python3 python3-pip python3-venv python3-dev
        postgresql postgresql-contrib
        redis-server
        git curl wget htop
        build-essential libpq-dev pkg-config
        nginx supervisor
        jq zip whois
    )
    
    log_info "Instalando: ${packages[*]}"
    apt-get install -y "${packages[@]}"
    
    log_success "Dependências do sistema instaladas"
}

create_system_user() {
    log_step "Configurando usuário do sistema"
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        log_info "Criando usuário $SERVICE_USER..."
        useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_USER"
        log_success "Usuário $SERVICE_USER criado"
    else
        log_info "Usuário $SERVICE_USER já existe"
    fi
    
    # Configurar permissões do diretório
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    log_success "Permissões configuradas"
}

setup_postgresql() {
    log_step "Configurando PostgreSQL"
    
    systemctl start postgresql
    systemctl enable postgresql
    
    # Configurar banco e usuário
    sudo -u postgres psql -v ON_ERROR_STOP=1 << EOF
-- Remover usuários e bancos antigos se existirem
DROP ROLE IF EXISTS bgpmonitor;
DROP ROLE IF EXISTS $DB_USER;
DROP DATABASE IF EXISTS bgpmonitor;
DROP DATABASE IF EXISTS $DB_NAME;

-- Criar usuário
CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASS';

-- Criar banco
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT CREATE ON DATABASE $DB_NAME TO $DB_USER;

-- Confirmar criação
\\l $DB_NAME
\\du $DB_USER
EOF
    
    log_success "PostgreSQL configurado"
}

setup_redis() {
    log_step "Configurando Redis"
    
    systemctl start redis-server
    systemctl enable redis-server
    
    # Testar Redis
    if redis-cli ping >/dev/null 2>&1; then
        log_success "Redis configurado e funcionando"
    else
        log_warning "Redis pode não estar funcionando corretamente"
    fi
}

setup_python_environment() {
    log_step "Configurando ambiente Python"
    
    # Remover ambiente virtual antigo se existir
    if [[ -d "$INSTALL_DIR/venv" ]]; then
        log_info "Removendo ambiente virtual antigo..."
        rm -rf "$INSTALL_DIR/venv"
    fi
    
    # Criar novo ambiente virtual
    log_info "Criando ambiente virtual..."
    sudo -u "$SERVICE_USER" python3 -m venv "$INSTALL_DIR/venv"
    
    # Instalar dependências
    log_info "Instalando dependências Python..."
    sudo -u "$SERVICE_USER" bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
EOF
    
    log_success "Ambiente Python configurado"
}

setup_configuration() {
    log_step "Configurando arquivos de ambiente"
    
    # Criar arquivo .env se não existir
    if [[ ! -f "$INSTALL_DIR/.env" ]]; then
        if [[ -f "$INSTALL_DIR/.env.example" ]]; then
            log_info "Criando .env a partir do .env.example..."
            cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        else
            log_info "Criando arquivo .env básico..."
            cat > "$INSTALL_DIR/.env" << EOF
# BGP Monitor v$VERSION Configuration
# Generated automatically on $(date)

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME

# Redis
REDIS_URL=redis://localhost:6379/0

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# BGP Monitoring (CONFIGURE THESE!)
TARGET_ASN=0
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Monitoring intervals (seconds)
PREFIX_CHECK_INTERVAL=300
PEER_CHECK_INTERVAL=600
ASPATH_CHECK_INTERVAL=300
LATENCY_CHECK_INTERVAL=900
IRR_CHECK_INTERVAL=3600

# Alerting
ALERT_COOLDOWN=1800
MAX_LATENCY_MS=250
MIN_UPSTREAMS=2

# RIPE API
RIPE_BASE_URL=https://stat.ripe.net/data
RIPE_API_KEY=

# Data retention
DATA_RETENTION_DAYS=365
CLEANUP_INTERVAL_HOURS=24

# Rate limiting
API_RATE_LIMIT_PER_ASN=30
API_BATCH_SIZE=5
EOF
        fi
        
        chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
        chmod 600 "$INSTALL_DIR/.env"
        log_success "Arquivo .env configurado"
    else
        log_info "Arquivo .env já existe, mantendo configuração atual"
    fi
}

run_database_migrations() {
    log_step "Executando migrações do banco de dados"
    
    sudo -u "$SERVICE_USER" bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
python -m alembic upgrade head
EOF
    
    log_success "Migrações executadas"
}

create_systemd_service() {
    log_step "Criando serviço systemd"
    
    cat > "/etc/systemd/system/bgp-monitor.service" << EOF
[Unit]
Description=BGP Monitor v$VERSION
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service
Documentation=https://github.com/netovaat/bgp-monitor

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$INSTALL_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$INSTALL_DIR
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable bgp-monitor
    
    log_success "Serviço systemd criado e habilitado"
}

# -----------------------------------------------------------------------------
# FUNÇÕES DE TESTE
# -----------------------------------------------------------------------------
test_database_connection() {
    log_step "Testando conexão com o banco de dados"
    
    sudo -u "$SERVICE_USER" bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
python3 -c "
import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host='localhost',
        database='$DB_NAME',
        user='$DB_USER',
        password='$DB_PASS'
    )
    print('✓ Conexão com PostgreSQL OK')
    conn.close()
except Exception as e:
    print(f'✗ Erro na conexão: {e}')
    sys.exit(1)
"
EOF
    
    log_success "Conexão com banco de dados testada"
}

test_python_imports() {
    log_step "Testando importações Python"
    
    sudo -u "$SERVICE_USER" bash << EOF
cd "$INSTALL_DIR"
source venv/bin/activate
python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from app.main import app
    print('✓ app.main: OK')
    
    from app.database.connection import db_manager
    print('✓ database.connection: OK')
    
    from app.core.config import settings
    print('✓ core.config: OK')
    
    print('✓ Todas as importações funcionaram')
except Exception as e:
    print(f'✗ Erro na importação: {e}')
    sys.exit(1)
"
EOF
    
    log_success "Importações Python testadas"
}

test_service_startup() {
    log_step "Testando inicialização do serviço"
    
    systemctl start bgp-monitor
    sleep 5
    
    if systemctl is-active --quiet bgp-monitor; then
        log_success "Serviço BGP Monitor iniciado com sucesso"
        
        # Testar API
        local retries=5
        local count=0
        
        while [[ $count -lt $retries ]]; do
            if curl -s http://localhost:8000/health >/dev/null 2>&1; then
                log_success "API respondendo corretamente"
                return 0
            fi
            
            count=$((count + 1))
            log_info "Tentativa $count/$retries - Aguardando API..."
            sleep 2
        done
        
        log_warning "API ainda não está respondendo, mas serviço foi iniciado"
    else
        log_error "Serviço não iniciou corretamente"
        log_info "Verificando logs:"
        journalctl -u bgp-monitor --no-pager -n 10
        return 1
    fi
}

# -----------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# -----------------------------------------------------------------------------
main() {
    log_header "BGP Monitor v$VERSION - Instalação Unificada"
    
    echo -e "${BLUE}Este script irá instalar e configurar o BGP Monitor v$VERSION${NC}"
    echo -e "${BLUE}Diretório de instalação: $INSTALL_DIR${NC}"
    echo -e "${BLUE}Usuário do serviço: $SERVICE_USER${NC}"
    echo
    
    # Validações iniciais
    check_root
    check_os
    check_directory
    check_python
    
    # Processo de instalação
    install_system_packages
    create_system_user
    setup_postgresql
    setup_redis
    setup_python_environment
    setup_configuration
    run_database_migrations
    create_systemd_service
    
    # Testes
    test_database_connection
    test_python_imports
    test_service_startup
    
    # Relatório final
    log_header "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    
    echo
    log_success "BGP Monitor v$VERSION foi instalado e configurado!"
    echo
    echo -e "${CYAN}INFORMAÇÕES DO SISTEMA:${NC}"
    echo "• Diretório: $INSTALL_DIR"
    echo "• Usuário: $SERVICE_USER"
    echo "• Banco: PostgreSQL ($DB_NAME)"
    echo "• Cache: Redis"
    echo "• Serviço: bgp-monitor.service"
    echo "• Porta: 8000"
    echo
    echo -e "${CYAN}COMANDOS ÚTEIS:${NC}"
    echo "  sudo systemctl status bgp-monitor     # Status do serviço"
    echo "  sudo systemctl restart bgp-monitor    # Reiniciar serviço"
    echo "  sudo journalctl -u bgp-monitor -f     # Logs em tempo real"
    echo "  curl http://localhost:8000/health     # Testar API"
    echo "  curl http://localhost:8000/docs       # Documentação Swagger"
    echo
    echo -e "${YELLOW}PRÓXIMOS PASSOS:${NC}"
    echo "1. Edite o arquivo $INSTALL_DIR/.env"
    echo "2. Configure TARGET_ASN com seu ASN"
    echo "3. Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID"
    echo "4. Reinicie o serviço: sudo systemctl restart bgp-monitor"
    echo
    echo -e "${GREEN}GitHub: https://github.com/netovaat/bgp-monitor${NC}"
    echo -e "${GREEN}Autor: netovaat${NC}"
    echo
    log_success "Instalação completa! Sistema pronto para configuração e uso."
}

# -----------------------------------------------------------------------------
# TRATAMENTO DE SINAIS
# -----------------------------------------------------------------------------
cleanup() {
    log_warning "Instalação interrompida"
    exit 130
}

trap cleanup SIGINT SIGTERM

# -----------------------------------------------------------------------------
# EXECUÇÃO
# -----------------------------------------------------------------------------
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
