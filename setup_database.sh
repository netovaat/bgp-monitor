#!/bin/bash

# BGP Monitor Database Setup Script
# Este script configura o PostgreSQL e inicializa o banco de dados

set -e

echo "🚀 Configurando banco de dados BGP Monitor..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações do banco
DB_NAME="bgp_monitor"
DB_USER="bgp_monitor"
DB_PASSWORD="bgp_monitor_password"
DB_HOST="localhost"
DB_PORT="5432"

# Função para imprimir status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar se PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL não está instalado!"
    echo "Para instalar no Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install postgresql postgresql-contrib"
    echo ""
    echo "Para instalar no CentOS/RHEL:"
    echo "  sudo yum install postgresql postgresql-server"
    exit 1
fi

print_status "PostgreSQL encontrado"

# Verificar se o serviço PostgreSQL está rodando
if ! systemctl is-active --quiet postgresql; then
    print_warning "Iniciando serviço PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
fi

print_status "Serviço PostgreSQL ativo"

# Criar usuário e banco de dados
print_warning "Criando usuário e banco de dados..."

sudo -u postgres psql << EOF
-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${DB_USER}') THEN
        CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;

-- Criar banco de dados se não existir
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
ALTER USER ${DB_USER} CREATEDB;
EOF

print_status "Usuário e banco de dados criados"

# Instalar extensões necessárias
print_warning "Instalando extensões do PostgreSQL..."

sudo -u postgres psql -d ${DB_NAME} << EOF
-- Criar extensões úteis para análise de dados
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- TimescaleDB (opcional - descomentar se instalado)
-- CREATE EXTENSION IF NOT EXISTS timescaledb;
EOF

print_status "Extensões instaladas"

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    print_warning "Criando arquivo .env..."
    cat > .env << EOF
# Database Configuration
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# Data Retention
DATA_RETENTION_DAYS=365
CLEANUP_INTERVAL_HOURS=24

# API Rate Limiting
API_RATE_LIMIT_PER_ASN=30
API_BATCH_SIZE=5

# Existing configurations...
# (adicionar suas configurações existentes aqui)
EOF
    print_status "Arquivo .env criado"
else
    print_warning "Arquivo .env já existe - atualizando configurações do banco..."
    
    # Adicionar configurações de banco se não existirem
    if ! grep -q "DB_HOST" .env; then
        cat >> .env << EOF

# Database Configuration
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# Data Retention
DATA_RETENTION_DAYS=365
CLEANUP_INTERVAL_HOURS=24

# API Rate Limiting
API_RATE_LIMIT_PER_ASN=30
API_BATCH_SIZE=5
EOF
        print_status "Configurações de banco adicionadas ao .env"
    fi
fi

# Instalar dependências Python
print_warning "Instalando dependências do banco de dados..."
pip install -r requirements-db.txt

print_status "Dependências instaladas"

# Inicializar Alembic se necessário
if [ ! -d "alembic/versions" ]; then
    print_warning "Inicializando Alembic..."
    mkdir -p alembic/versions
    alembic revision --autogenerate -m "Initial migration"
fi

# Executar migrações
print_warning "Executando migrações do banco de dados..."
alembic upgrade head

print_status "Migrações executadas"

# Testar conexão
print_warning "Testando conexão com o banco de dados..."

python3 << EOF
import asyncio
import sys
sys.path.append('.')

async def test_connection():
    try:
        from app.database.connection import db_manager
        await db_manager.initialize()
        health = await db_manager.health_check()
        if health:
            print("✓ Conexão com banco de dados funcionando!")
            return True
        else:
            print("✗ Falha no health check do banco de dados")
            return False
    except Exception as e:
        print(f"✗ Erro na conexão: {e}")
        return False
    finally:
        await db_manager.close()

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
EOF

if [ $? -eq 0 ]; then
    print_status "Teste de conexão bem-sucedido"
else
    print_error "Falha no teste de conexão"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Configuração do banco de dados concluída com sucesso!${NC}"
echo ""
echo "Próximos passos:"
echo "1. Configure seus ASNs para monitoramento"
echo "2. Execute: python -m app.main para iniciar o BGP Monitor"
echo "3. Os dados históricos serão coletados automaticamente"
echo ""
echo "Configurações do banco:"
echo "  Host: ${DB_HOST}:${DB_PORT}"
echo "  Database: ${DB_NAME}"
echo "  User: ${DB_USER}"
echo ""
echo "Para acessar o banco diretamente:"
echo "  psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME}"
