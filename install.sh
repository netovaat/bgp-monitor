#!/bin/bash

# BGP Monitor v2.0 - Script de Instalação Automatizada
# Sistema de monitoramento BGP com PostgreSQL e detecção de anomalias
# Suporte: Ubuntu 20.04+ / Debian 11+

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está executando como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Este script deve ser executado como root (sudo)"
        exit 1
    fi
}

# Detectar distribuição
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        print_error "Não foi possível detectar a distribuição Linux"
        exit 1
    fi
    
    print_status "Distribuição detectada: $DISTRO $VERSION"
}

# Atualizar sistema
update_system() {
    print_status "Atualizando sistema..."
    apt-get update
    apt-get upgrade -y
    print_success "Sistema atualizado"
}

# Instalar dependências do sistema
install_system_deps() {
    print_status "Instalando dependências do sistema..."
    
    # Dependências básicas
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    # Python 3.11 ou superior
    if ! command -v python3.11 &> /dev/null; then
        print_status "Instalando Python 3.11..."
        add-apt-repository ppa:deadsnakes/ppa -y
        apt-get update
        apt-get install -y python3.11 python3.11-venv python3.11-dev
    fi
    
    # pip
    if ! command -v pip3 &> /dev/null; then
        print_status "Instalando pip..."
        apt-get install -y python3-pip
    fi
    
    print_success "Dependências básicas instaladas"
}

# Instalar PostgreSQL
install_postgresql() {
    print_status "Instalando PostgreSQL..."
    
    # Adicionar repositório oficial do PostgreSQL
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
    
    apt-get update
    apt-get install -y postgresql-15 postgresql-client-15 postgresql-contrib-15
    
    # Iniciar e habilitar PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    print_success "PostgreSQL instalado e iniciado"
}

# Configurar banco de dados
setup_database() {
    print_status "Configurando banco de dados BGP Monitor..."
    
    # Criar usuário e banco de dados
    sudo -u postgres psql -c "CREATE USER bgp_monitor WITH PASSWORD 'bgp_monitor_password';"
    sudo -u postgres psql -c "CREATE DATABASE bgp_monitor OWNER bgp_monitor;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bgp_monitor TO bgp_monitor;"
    
    print_success "Banco de dados configurado"
}

# Criar usuário do sistema
create_system_user() {
    print_status "Criando usuário do sistema bgpmonitor..."
    
    if ! id "bgpmonitor" &>/dev/null; then
        useradd -r -s /bin/bash -d /opt/bgp-monitor -m bgpmonitor
        print_success "Usuário bgpmonitor criado"
    else
        print_warning "Usuário bgpmonitor já existe"
    fi
}

# Configurar diretórios
setup_directories() {
    print_status "Configurando diretórios..."
    
    mkdir -p /opt/bgp-monitor/{logs,backups}
    chown -R bgpmonitor:bgpmonitor /opt/bgp-monitor
    chmod -R 755 /opt/bgp-monitor
    
    print_success "Diretórios configurados"
}

# Instalar aplicação
install_application() {
    print_status "Instalando BGP Monitor v2.0..."
    
    cd /opt/bgp-monitor
    
    # Criar ambiente virtual
    sudo -u bgpmonitor python3.11 -m venv venv
    
    # Ativar venv e instalar dependências
    sudo -u bgpmonitor bash -c "
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt
    "
    
    # Copiar arquivo de configuração
    sudo -u bgpmonitor cp .env.example .env
    
    print_success "Aplicação instalada"
}

# Configurar banco de dados da aplicação
setup_app_database() {
    print_status "Configurando banco de dados da aplicação..."
    
    cd /opt/bgp-monitor
    sudo -u bgpmonitor bash -c "
        source venv/bin/activate
        alembic upgrade head
    "
    
    print_success "Banco de dados da aplicação configurado"
}

# Criar serviço systemd
create_systemd_service() {
    print_status "Criando serviço systemd..."
    
    cat > /etc/systemd/system/bgp-monitor.service << EOF
[Unit]
Description=BGP Monitor v2.0 - Sistema de Monitoramento BGP
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=bgpmonitor
Group=bgpmonitor
WorkingDirectory=/opt/bgp-monitor
Environment=PATH=/opt/bgp-monitor/venv/bin
ExecStart=/opt/bgp-monitor/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bgp-monitor

# Variáveis de ambiente
Environment=PYTHONPATH=/opt/bgp-monitor
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable bgp-monitor
    
    print_success "Serviço systemd criado e habilitado"
}

# Configurar firewall
setup_firewall() {
    print_status "Configurando firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 8000/tcp
        print_success "Firewall configurado (porta 8000 liberada)"
    else
        print_warning "UFW não encontrado, configure o firewall manualmente para liberar a porta 8000"
    fi
}

# Criar scripts auxiliares
create_helper_scripts() {
    print_status "Criando scripts auxiliares..."
    
    # Script de start
    cat > /opt/bgp-monitor/start.sh << 'EOF'
#!/bin/bash
cd /opt/bgp-monitor
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF

    # Script de stop
    cat > /opt/bgp-monitor/stop.sh << 'EOF'
#!/bin/bash
sudo systemctl stop bgp-monitor
EOF

    # Script de status
    cat > /opt/bgp-monitor/status.sh << 'EOF'
#!/bin/bash
sudo systemctl status bgp-monitor
EOF

    # Script de logs
    cat > /opt/bgp-monitor/logs.sh << 'EOF'
#!/bin/bash
sudo journalctl -u bgp-monitor -f
EOF

    # Script de backup
    cat > /opt/bgp-monitor/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/bgp-monitor/backups"
mkdir -p $BACKUP_DIR

echo "Fazendo backup do banco de dados..."
sudo -u postgres pg_dump bgp_monitor > $BACKUP_DIR/bgp_monitor_$DATE.sql
echo "Backup salvo em: $BACKUP_DIR/bgp_monitor_$DATE.sql"
EOF

    chmod +x /opt/bgp-monitor/*.sh
    chown bgpmonitor:bgpmonitor /opt/bgp-monitor/*.sh
    
    print_success "Scripts auxiliares criados"
}

# Função principal
main() {
    echo -e "${BLUE}"
    echo "================================================="
    echo "    BGP Monitor v2.0 - Instalação Automatizada"
    echo "================================================="
    echo -e "${NC}"
    
    check_root
    detect_distro
    
    print_status "Iniciando instalação..."
    
    update_system
    install_system_deps
    install_postgresql
    setup_database
    create_system_user
    setup_directories
    install_application
    setup_app_database
    create_systemd_service
    setup_firewall
    create_helper_scripts
    
    echo -e "${GREEN}"
    echo "================================================="
    echo "           INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "================================================="
    echo -e "${NC}"
    
    echo "Para iniciar o BGP Monitor:"
    echo "  sudo systemctl start bgp-monitor"
    echo ""
    echo "Para verificar o status:"
    echo "  sudo systemctl status bgp-monitor"
    echo ""
    echo "Para ver logs em tempo real:"
    echo "  sudo journalctl -u bgp-monitor -f"
    echo ""
    echo "API REST disponível em: http://localhost:8000"
    echo "Documentação da API: http://localhost:8000/docs"
    echo ""
    echo "Configurações em: /opt/bgp-monitor/.env"
    echo ""
    print_warning "IMPORTANTE: Edite o arquivo .env com suas configurações antes de iniciar!"
}

main "$@"
