#!/bin/bash
# BGP Monitor v2.1.0 - Teste Rápido de Validação Final
# Este script testa rapidamente se todas as correções foram aplicadas

echo "🔍 BGP Monitor v2.1.0 - Teste de Validação Final"
echo "================================================"
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Execute este script no diretório /opt/bgp-monitor"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
else
    echo "⚠️ Ambiente virtual não encontrado"
fi

# Testar imports críticos
echo ""
echo "🧪 Testando imports críticos..."

python3 -c "
import sys
sys.path.insert(0, '.')

print('📋 Relatório de Imports:')
print('=' * 40)

# Teste 1: Import principal
try:
    from app.main import app
    print('✅ app.main: OK')
except Exception as e:
    print(f'❌ app.main: {e}')

# Teste 2: BGPScheduler
try:
    from app.services.scheduler import BGPScheduler
    print('✅ BGPScheduler: OK')
except Exception as e:
    print(f'❌ BGPScheduler: {e}')

# Teste 3: get_db
try:
    from app.database import get_db
    print('✅ get_db: OK')
except Exception as e:
    print(f'❌ get_db: {e}')

# Teste 4: get_db_session
try:
    from app.database import get_db_session
    print('✅ get_db_session: OK')
except Exception as e:
    print(f'❌ get_db_session: {e}')

# Teste 5: FastAPI
try:
    import fastapi
    print('✅ FastAPI: OK')
except Exception as e:
    print(f'❌ FastAPI: {e}')

# Teste 6: SQLAlchemy
try:
    import sqlalchemy
    print('✅ SQLAlchemy: OK')
except Exception as e:
    print(f'❌ SQLAlchemy: {e}')

# Teste 7: Alembic
try:
    import alembic
    print('✅ Alembic: OK')
except Exception as e:
    print(f'❌ Alembic: {e}')

# Teste 8: psycopg2
try:
    import psycopg2
    print('✅ psycopg2: OK')
except Exception as e:
    print(f'❌ psycopg2: {e}')

print('=' * 40)
print('🎯 Teste de imports concluído!')
"

echo ""
echo "📊 Verificando arquivos de configuração..."

# Verificar arquivos importantes
if [ -f ".env" ]; then
    echo "✅ Arquivo .env: Existe"
else
    echo "❌ Arquivo .env: Não encontrado"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt: Existe"
else
    echo "❌ requirements.txt: Não encontrado"
fi

if [ -f "alembic/script.py.mako" ]; then
    echo "✅ script.py.mako: Existe"
else
    echo "❌ script.py.mako: Não encontrado"
fi

# Verificar migrations
if [ -d "alembic/versions" ] && [ -n "$(ls -A alembic/versions/*.py 2>/dev/null)" ]; then
    echo "✅ Migrations: Existem"
    echo "   Migrations encontradas:"
    ls alembic/versions/*.py | sed 's/.*\//   - /'
else
    echo "❌ Migrations: Não encontradas"
fi

echo ""
echo "🔧 Verificando correções específicas..."

# Verificar correção do BGPScheduler
if grep -q "from app.services.scheduler import BGPScheduler" app/services/scheduler.py 2>/dev/null; then
    echo "✅ Import BGPScheduler: Corrigido"
elif grep -q "from scheduler import BGPScheduler" app/services/scheduler.py 2>/dev/null; then
    echo "❌ Import BGPScheduler: Ainda incorreto"
else
    echo "⚠️ Import BGPScheduler: Não encontrado"
fi

# Verificar função get_db
if grep -q "def get_db" app/database/__init__.py 2>/dev/null; then
    echo "✅ Função get_db: Existe"
else
    echo "❌ Função get_db: Não encontrada"
fi

# Verificar psycopg2 no requirements.txt
if grep -q "psycopg2-binary" requirements.txt 2>/dev/null; then
    echo "✅ psycopg2-binary: No requirements.txt"
else
    echo "❌ psycopg2-binary: Não encontrado no requirements.txt"
fi

echo ""
echo "📈 Resumo da Validação:"
echo "======================="

# Contar sucessos
TOTAL_CHECKS=8
SUCCESS_COUNT=$(python3 -c "
import sys
sys.path.insert(0, '.')

success = 0
try:
    from app.main import app
    success += 1
except: pass

try:
    from app.services.scheduler import BGPScheduler
    success += 1
except: pass

try:
    from app.database import get_db
    success += 1
except: pass

try:
    from app.database import get_db_session
    success += 1
except: pass

try:
    import fastapi
    success += 1
except: pass

try:
    import sqlalchemy
    success += 1
except: pass

try:
    import alembic
    success += 1
except: pass

try:
    import psycopg2
    success += 1
except: pass

print(success)
" 2>/dev/null || echo "0")

if [ "$SUCCESS_COUNT" -eq "$TOTAL_CHECKS" ]; then
    echo "🎉 Status: TODOS OS TESTES PASSARAM! ($SUCCESS_COUNT/$TOTAL_CHECKS)"
    echo "✅ Sistema BGP Monitor v2.1.0 está funcionando corretamente"
    echo ""
    echo "🚀 Pronto para uso!"
    exit 0
else
    echo "⚠️ Status: $SUCCESS_COUNT/$TOTAL_CHECKS testes passaram"
    echo "❌ Algumas correções ainda são necessárias"
    echo ""
    echo "💡 Execute: sudo ./aplicar-correções.sh"
    exit 1
fi
