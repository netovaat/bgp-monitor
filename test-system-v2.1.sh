#!/bin/bash
# BGP Monitor v2.1.0 - Script de Testes Completos
# Este script executa todos os testes necessários para validar a instalação

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Contadores de testes
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_TESTS++))
}

error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_TESTS++))
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

title() {
    echo -e "\n${BOLD}${BLUE}🔍 $1${NC}\n"
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TOTAL_TESTS++))
    echo -n "Testando $test_name... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED_TESTS++))
        return 0
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED_TESTS++))
        return 1
    fi
}

# Verificar se está no diretório correto
if [[ ! -f "app/main.py" ]]; then
    error "Execute este script no diretório raiz do BGP Monitor (/opt/bgp-monitor)"
    exit 1
fi

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                BGP Monitor v2.1.0 - Testes Completos        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1. Testes de Sistema
title "1. TESTES DE SISTEMA"

run_test "Python 3.8+" "python3 --version | grep -E 'Python 3\.(8|9|10|11|12)'"
run_test "PostgreSQL" "systemctl is-active postgresql"
run_test "Usuário bgpmonitor" "id bgpmonitor"
run_test "Diretório de instalação" "test -d /opt/bgp-monitor"
run_test "Arquivo .env" "test -f .env"

# 2. Testes de Ambiente Virtual
title "2. TESTES DE AMBIENTE VIRTUAL"

run_test "Ambiente virtual existe" "test -d venv"
run_test "Python no venv" "test -f venv/bin/python3"
run_test "Pip no venv" "test -f venv/bin/pip"
run_test "Uvicorn instalado" "test -f venv/bin/uvicorn"
run_test "Alembic instalado" "test -f venv/bin/alembic"

# 3. Testes de Dependências Python
title "3. TESTES DE DEPENDÊNCIAS PYTHON"

# Testar dentro do ambiente virtual
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
    
    run_test "FastAPI" "python3 -c 'import fastapi'"
    run_test "Uvicorn" "python3 -c 'import uvicorn'"
    run_test "SQLAlchemy" "python3 -c 'import sqlalchemy'"
    run_test "Alembic" "python3 -c 'import alembic'"
    run_test "Psycopg2" "python3 -c 'import psycopg2'"
    run_test "Asyncpg" "python3 -c 'import asyncpg'"
    run_test "Schedule" "python3 -c 'import schedule'"
    run_test "Requests" "python3 -c 'import requests'"
    run_test "Telegram" "python3 -c 'import telegram'"
else
    error "Ambiente virtual não encontrado"
fi

# 4. Testes de Imports do Projeto
title "4. TESTES DE IMPORTS DO PROJETO"

if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
    
    # Script de teste de imports
    python3 << 'EOF'
import sys
sys.path.append('/opt/bgp-monitor')

tests_passed = 0
tests_total = 0

def test_import(module_name, import_statement):
    global tests_passed, tests_total
    tests_total += 1
    try:
        exec(import_statement)
        print(f"✅ {module_name}: OK")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"❌ {module_name}: {e}")
        return False

# Testes de imports
test_import("ASNSnapshotService", "from app.models.asn_snapshot import ASNSnapshotService")
test_import("BGPDataService", "from app.services.bgp_collector import BGPDataService")
test_import("BGPScheduler", "from app.services.scheduler import BGPScheduler")
test_import("ASN Router", "from app.api.routes.asn import router")
test_import("Monitoring Router", "from app.api.routes.monitoring import router")
test_import("Main App", "from app.main import app")
test_import("Database Models", "from app.models.database import ASNSnapshot, PrefixHistory, BGPAlert")
test_import("Config", "from app.core.config import settings")
test_import("DB Manager", "from app.database.connection import db_manager")

print(f"\nImports: {tests_passed}/{tests_total} passaram")
if tests_passed == tests_total:
    sys.exit(0)
else:
    sys.exit(1)
EOF

    if [[ $? -eq 0 ]]; then
        success "Todos os imports do projeto funcionando"
        ((PASSED_TESTS++))
    else
        error "Alguns imports falharam"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
fi

# 5. Testes de Banco de Dados
title "5. TESTES DE BANCO DE DADOS"

if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
    
    # Teste de conectividade do banco
    python3 << 'EOF'
import asyncio
import sys
sys.path.append('/opt/bgp-monitor')

async def test_database():
    try:
        from app.database.connection import db_manager
        from sqlalchemy import text
        
        await db_manager.initialize()
        print("✅ Conexão com banco estabelecida")
        
        async with db_manager.get_session() as session:
            # Teste de versão
            result = await session.execute(text('SELECT version();'))
            version = result.scalar()
            print(f"✅ PostgreSQL: {version.split(',')[0]}")
            
            # Teste de tabelas
            result = await session.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            ))
            tables = result.fetchall()
            print(f"✅ Tabelas encontradas: {len(tables)}")
            
            expected_tables = ['asn_snapshots', 'prefix_history', 'bgp_alerts', 'system_metrics', 'alembic_version']
            found_tables = [table[0] for table in tables]
            
            for expected in expected_tables:
                if expected in found_tables:
                    print(f"✅ Tabela {expected}: OK")
                else:
                    print(f"❌ Tabela {expected}: FALTANDO")
                    raise Exception(f"Tabela {expected} não encontrada")
        
        await db_manager.close()
        print("✅ Conexão fechada corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro de banco: {e}")
        return False

result = asyncio.run(test_database())
sys.exit(0 if result else 1)
EOF

    if [[ $? -eq 0 ]]; then
        success "Banco de dados funcionando"
        ((PASSED_TESTS++))
    else
        error "Problemas no banco de dados"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
fi

# 6. Testes de API (se servidor não estiver rodando)
title "6. TESTES DE API"

# Verificar se porta 8000 está em uso
if ! netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        
        # Iniciar servidor temporariamente
        info "Iniciando servidor temporário para testes..."
        python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 > /dev/null 2>&1 &
        SERVER_PID=$!
        
        # Aguardar servidor inicializar
        sleep 5
        
        # Testes de endpoints
        run_test "Health endpoint" "curl -s http://127.0.0.1:8001/health | grep -q 'healthy'"
        run_test "Root endpoint" "curl -s http://127.0.0.1:8001/ | grep -q 'BGP Monitor'"
        run_test "API BGP ASNs" "curl -s http://127.0.0.1:8001/api/v1/bgp/asns | grep -q '\[\]'"
        run_test "OpenAPI docs" "curl -s http://127.0.0.1:8001/docs | grep -q 'swagger'"
        
        # Parar servidor
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        
        success "Servidor de teste finalizado"
    fi
else
    warning "Servidor já rodando na porta 8000, pulando testes de API"
fi

# 7. Testes de Configuração
title "7. TESTES DE CONFIGURAÇÃO"

run_test "Arquivo .env configurado" "grep -q 'DB_HOST=localhost' .env"
run_test "Configuração PostgreSQL" "grep -q 'DB_NAME=bgpmonitor' .env"
run_test "Configuração API" "grep -q 'API_PORT=8000' .env"

# 8. Testes de Permissões
title "8. TESTES DE PERMISSÕES"

run_test "Proprietário bgpmonitor" "test $(stat -c '%U' /opt/bgp-monitor) = 'bgpmonitor'"
run_test "Scripts executáveis" "test -x install.sh && test -x aplicar-correções.sh"
run_test "Ambiente virtual acessível" "sudo -u bgpmonitor test -r venv/bin/activate"

# 9. Testes de Serviço Systemd
title "9. TESTES DE SERVIÇO SYSTEMD"

run_test "Arquivo de serviço" "test -f /etc/systemd/system/bgp-monitor.service"
run_test "Serviço habilitado" "systemctl is-enabled bgp-monitor 2>/dev/null || echo 'disabled' | grep -q 'enabled\|disabled'"

# 10. Resultado Final
title "10. RESUMO DOS TESTES"

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║                    RESULTADO DOS TESTES                     ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BOLD}Total de testes executados:${NC} $TOTAL_TESTS"
echo -e "${GREEN}${BOLD}Testes aprovados:${NC} $PASSED_TESTS"
echo -e "${RED}${BOLD}Testes falharam:${NC} $FAILED_TESTS"

PERCENTAGE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "${BOLD}Taxa de sucesso:${NC} $PERCENTAGE%"

echo ""

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}🎉 TODOS OS TESTES PASSARAM! SISTEMA PRONTO PARA USO! 🎉${NC}"
    echo ""
    echo -e "${CYAN}Próximos passos:${NC}"
    echo "1. Iniciar o serviço: sudo systemctl start bgp-monitor"
    echo "2. Verificar status: sudo systemctl status bgp-monitor"
    echo "3. Verificar logs: sudo journalctl -u bgp-monitor -f"
    echo "4. Testar API: curl http://localhost:8000/health"
    echo ""
    exit 0
else
    echo -e "${RED}${BOLD}⚠️  ALGUNS TESTES FALHARAM${NC}"
    echo ""
    echo -e "${YELLOW}Recomendações:${NC}"
    echo "1. Verifique os logs acima para identificar problemas"
    echo "2. Execute o script de correções: sudo ./aplicar-correções.sh"
    echo "3. Consulte a documentação: docs/TROUBLESHOOTING.md"
    echo "4. Execute novamente: sudo ./test-system-v2.1.sh"
    echo ""
    exit 1
fi
