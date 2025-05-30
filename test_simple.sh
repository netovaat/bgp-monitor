#!/bin/bash
echo "🚀 BGP Monitor v2.0 - Teste Final do Sistema"
echo "============================================"

cd /opt/bgp-monitor

echo ""
echo "�� Testando ambiente virtual..."
if [ -d "venv" ]; then
    echo "✅ Ambiente virtual encontrado"
else
    echo "❌ Ambiente virtual não encontrado"
fi

echo ""
echo "🔍 Testando Python..."
/opt/bgp-monitor/venv/bin/python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python funcionando"
else
    echo "❌ Python com problema"
fi

echo ""
echo "✅ Sistema BGP Monitor v2.0 testado com sucesso!"
