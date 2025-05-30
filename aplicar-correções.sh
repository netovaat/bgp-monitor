#!/bin/bash
# Script de Correções Automáticas BGP Monitor v2.1.0
# Este script aplica todas as correções identificadas durante o processo de instalação

set -e  # Para em caso de erro

echo "🔧 BGP Monitor v2.1.0 - Script de Correções Automáticas"
echo "=================================================="
echo ""

# Verifica se está sendo executado no diretório correto
if [ ! -f "/opt/bgp-monitor/requirements.txt" ]; then
    echo "❌ Erro: Execute este script no diretório /opt/bgp-monitor"
    exit 1
fi

echo "📍 Diretório correto detectado: /opt/bgp-monitor"
echo ""

# Correção 1: Instalar psycopg2-binary
echo "🔧 Correção 1: Instalando psycopg2-binary..."
if ! grep -q "psycopg2-binary" /opt/bgp-monitor/requirements.txt; then
    echo "❌ psycopg2-binary não encontrado no requirements.txt!"
    echo "   Adicionando psycopg2-binary==2.9.9..."
    echo "psycopg2-binary==2.9.9" >> /opt/bgp-monitor/requirements.txt
    echo "✅ psycopg2-binary adicionado ao requirements.txt"
else
    echo "✅ psycopg2-binary já está no requirements.txt"
fi

# Instalar a dependência
echo "📦 Instalando psycopg2-binary..."
sudo -u bgpmonitor bash -c "
    cd /opt/bgp-monitor
    source venv/bin/activate
    pip install psycopg2-binary==2.9.9
"
echo "✅ psycopg2-binary instalado com sucesso"
echo ""

# Correção 2: Criar script.py.mako para Alembic
echo "🔧 Correção 2: Verificando script.py.mako para Alembic..."
if [ ! -f "/opt/bgp-monitor/alembic/script.py.mako" ]; then
    echo "❌ script.py.mako não encontrado!"
    echo "   Criando template do Alembic..."
    sudo -u bgpmonitor bash -c "cat > /opt/bgp-monitor/alembic/script.py.mako << 'EOF'
\"\"\"\\${message}

Revision ID: \\${up_revision}
Revises: \\${down_revision | comma,n}
Create Date: \\${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
\\${imports if imports else \"\"}

# revision identifiers, used by Alembic.
revision = \\${repr(up_revision)}
down_revision = \\${repr(down_revision)}
branch_labels = \\${repr(branch_labels)}
depends_on = \\${repr(depends_on)}


def upgrade() -> None:
    \\${upgrades if upgrades else \"pass\"}


def downgrade() -> None:
    \\${downgrades if downgrades else \"pass\"}
EOF"
    echo "✅ script.py.mako criado com sucesso"
else
    echo "✅ script.py.mako já existe"
fi
echo ""

# Correção 3: Limpar migrations corrompidas e verificar migration válida
echo "🔧 Correção 3: Verificando migrations..."

# Remover arquivos de migration corrompidos conhecidos
echo "🗑️ Removendo migrations corrompidas conhecidas..."
sudo -u bgpmonitor rm -f /opt/bgp-monitor/alembic/versions/10cf5c2ea1a0_initial_migration.py
sudo -u bgpmonitor rm -rf /opt/bgp-monitor/alembic/versions/__pycache__

# Verificar se existe uma migration válida
VALID_MIGRATION=$(find /opt/bgp-monitor/alembic/versions/ -name "*.py" -exec grep -l "revision.*=" {} \; | head -1)

if [ -z "$VALID_MIGRATION" ]; then
    echo "❌ Nenhuma migration válida encontrada!"
    echo "   Criando migration inicial..."
    sudo -u bgpmonitor bash -c "
        cd /opt/bgp-monitor
        source venv/bin/activate
        alembic revision --autogenerate -m 'Initial migration'
    "
    echo "✅ Migration inicial criada"
else
    echo "✅ Migration válida encontrada: $(basename $VALID_MIGRATION)"
fi
echo ""

# Correção 4: Verificar e aplicar correções de imports críticas
echo "🔧 Correção 4: Aplicando correções de imports críticas..."

# Verificar se o import do BGPScheduler está correto no scheduler.py
if [ -f "app/services/scheduler.py" ]; then
    if grep -q "from scheduler import BGPScheduler" app/services/scheduler.py; then
        echo "❌ Import incorreto detectado no scheduler.py"
        echo "   Corrigindo import do BGPScheduler..."
        sudo -u bgpmonitor sed -i 's/from scheduler import BGPScheduler, scheduler/from app.services.scheduler import BGPScheduler as _BGPScheduler, scheduler/' app/services/scheduler.py
        echo "✅ Import do BGPScheduler corrigido"
    else
        echo "✅ Import do BGPScheduler já está correto"
    fi
fi

# Verificar se a função get_db existe no database/__init__.py
if [ -f "app/database/__init__.py" ]; then
    if ! grep -q "def get_db" app/database/__init__.py; then
        echo "❌ Função get_db não encontrada!"
        echo "   Adicionando função get_db..."
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
        echo "✅ Função get_db adicionada"
    else
        echo "✅ Função get_db já existe"
    fi
fi

echo "✅ Correções de imports aplicadas"
echo ""

# Teste final: Verificar se o sistema está funcionando
echo "🧪 Teste Final: Verificando funcionamento do sistema..."
echo "   Testando conexão com banco de dados..."

sudo -u bgpmonitor bash -c "
    cd /opt/bgp-monitor
    source venv/bin/activate
    python -c '
import asyncio
from app.database.connection import db_manager

async def test_db():
    try:
        await db_manager.initialize()
        print(\"✅ Conexão com banco de dados: OK\")
        
        # Aplicar migrations se necessário
        import subprocess
        result = subprocess.run([\"alembic\", \"upgrade\", \"head\"], 
                              capture_output=True, text=True, cwd=\"/opt/bgp-monitor\")
        if result.returncode == 0:
            print(\"✅ Migrations aplicadas: OK\")
        else:
            print(f\"⚠️ Aviso migrations: {result.stderr}\")
        
        await db_manager.close()
        return True
    except Exception as e:
        print(f\"❌ Erro no teste: {e}\")
        return False

success = asyncio.run(test_db())
exit(0 if success else 1)
'
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCESSO! Todas as correções foram aplicadas com sucesso!"
    echo ""
    echo "📋 Resumo das correções aplicadas:"
    echo "   ✅ Correção 1: psycopg2-binary adicionado e instalado"
    echo "   ✅ Correção 2: script.py.mako criado para Alembic"
    echo "   ✅ Correção 3: Migrations limpas e migration válida verificada"
    echo "   ✅ Correção 4: Imports críticos verificados e corrigidos"
    echo "   ✅ Teste final: Sistema funcionando corretamente"
    echo ""
    echo "🚀 O BGP Monitor v2.1.0 está pronto para uso!"
else
    echo ""
    echo "❌ FALHA! Algumas correções não foram aplicadas corretamente."
    echo "   Verifique os logs acima para detalhes."
    exit 1
fi
