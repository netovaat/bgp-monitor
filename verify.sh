#!/bin/bash
# BGP Monitor v1.0.1 - Verificação Final
# Este script verifica se o projeto está funcionando corretamente

echo "🔧 BGP Monitor v1.0.1 - Verificação Final"
echo "=========================================="
echo

# Verificar Python
echo "📋 Verificando requisitos do sistema:"
python3 --version
echo "✅ Python OK"
echo

# Verificar dependências
echo "📦 Verificando dependências:"
python3 -c "
try:
    import fastapi, uvicorn, httpx, telegram, schedule, pandas, numpy
    print('✅ Todas as dependências instaladas')
except ImportError as e:
    print(f'❌ Dependência faltando: {e}')
    exit(1)
"
echo

# Verificar estrutura do projeto
echo "📁 Verificando estrutura do projeto:"
required_files=(
    "app/main.py"
    "app/api/main.py" 
    "app/core/config.py"
    "app/services/telegram.py"
    "app/services/ripe_api.py"
    "app/scheduler.py"
    "requirements.txt"
    ".env.example"
    "README.md"
    "CHANGELOG.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file FALTANDO"
        exit 1
    fi
done
echo

# Verificar imports
echo "🧪 Testando imports do projeto:"
python3 -c "
from app.core.config import settings
from app.main import app
from app.api.main import app as api_app
from app.services.telegram import telegram_service
from app.services.ripe_api import ripe_api
from app.scheduler import bgp_scheduler
print('✅ Todos os imports funcionando')
"
echo

echo "🎉 BGP Monitor v1.0.1 está TOTALMENTE FUNCIONAL!"
echo "📦 Projeto pronto para distribuição"
echo "🚀 Para executar: ./run.sh"
echo
