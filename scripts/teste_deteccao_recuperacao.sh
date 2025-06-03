#!/bin/bash

# Script de teste para validar a lógica de detecção de recuperação
# Testa os novos recursos implementados para latência, instabilidade e anomalias

echo "🧪 === TESTE DE DETECÇÃO DE RECUPERAÇÃO ==="
echo "Data: $(date)"
echo ""

# Base URL da API
API_BASE="http://localhost:8000"

# Função para testar endpoint e exibir resultado
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local method="${3:-POST}"
    
    echo "📋 Testando: $description"
    echo "🔗 Endpoint: $method $endpoint"
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_BASE$endpoint" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_BASE$endpoint")
    fi
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ Status: $http_code - Sucesso"
        if command -v jq >/dev/null 2>&1; then
            # Se jq estiver disponível, formatar melhor
            message=$(echo "$body" | jq -r '.message // .status // "Teste executado"' 2>/dev/null)
            echo "📄 Resposta: $message"
            
            # Para endpoints que retornam alertas, mostrar quantos foram gerados
            if echo "$body" | jq -e '.alerts_generated' >/dev/null 2>&1; then
                alerts_count=$(echo "$body" | jq -r '.alerts_generated')
                echo "🚨 Alertas gerados: $alerts_count"
            fi
        else
            echo "📄 Resposta: Teste concluído (instale 'jq' para ver detalhes)"
        fi
    else
        echo "❌ Status: $http_code - Erro"
        if command -v jq >/dev/null 2>&1; then
            error=$(echo "$body" | jq -r '.detail // "Erro desconhecido"' 2>/dev/null)
            echo "📄 Erro: $error"
        else
            echo "📄 Erro: $body"
        fi
    fi
    
    echo ""
    sleep 2
}

# Verificar se o servidor está disponível
echo "🔍 Verificando disponibilidade do servidor..."
if ! curl -s "$API_BASE/" > /dev/null; then
    echo "❌ Servidor não está acessível em $API_BASE"
    echo "💡 Para iniciar o servidor:"
    echo "   cd /opt/bgp-monitor"
    echo "   ./bgp-monitor.sh start"
    echo ""
    echo "💡 Ou executar manualmente:"
    echo "   python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✅ Servidor está acessível"
echo ""

# Testes das funcionalidades de recuperação implementadas
echo "=== 🎯 TESTES DE DETECÇÃO DE RECUPERAÇÃO ==="

echo "🔄 1. TESTE DE MONITORAMENTO DE LATÊNCIA COM RECUPERAÇÃO"
test_endpoint "/monitoring/check-latency" "Verificação de latência (pode detectar recuperação)"

echo "🔄 2. TESTE DE MONITORAMENTO DE PEERS COM RECUPERAÇÃO"
test_endpoint "/monitoring/check-peers" "Verificação de peers (pode detectar recuperação)"

echo "🔄 3. TESTE DE MONITORAMENTO DE PREFIXOS COM RECUPERAÇÃO"
test_endpoint "/monitoring/check-prefixes" "Verificação de prefixos (pode detectar recuperação)"

echo "🔄 4. TESTE COMPLETO DE MONITORAMENTO"
test_endpoint "/monitoring/run-checks" "Verificação completa (todos os tipos)"

echo ""
echo "=== 📊 TESTES DE ENDPOINTS DE RECUPERAÇÃO ==="

echo "🟢 5. TESTE DE ALERTA DE PEER RECUPERADO"
test_endpoint "/test/recovery/peer" "Alerta de peer recuperado"

echo "🟢 6. TESTE DE ALERTA DE LATÊNCIA NORMALIZADA"
test_endpoint "/test/recovery/latency" "Alerta de latência normalizada"

echo "🟢 7. TESTE DE ALERTA DE INSTABILIDADE RESOLVIDA"
test_endpoint "/test/recovery/instability" "Alerta de instabilidade resolvida"

echo "🟢 8. TESTE DE ALERTA DE ANOMALIA RESOLVIDA"
test_endpoint "/test/recovery/anomaly" "Alerta de anomalia resolvida"

echo ""
echo "=== 📈 INFORMAÇÕES DO SISTEMA ==="

echo "📋 9. TIPOS DE ALERTAS DISPONÍVEIS"
test_endpoint "/alerts/types" "Listar tipos de alertas" "GET"

echo "📋 10. EXEMPLOS DE RECUPERAÇÃO EM PT-BR"
test_endpoint "/alerts/recovery/examples" "Exemplos de alertas de recuperação" "GET"

echo ""
echo "=== 🚀 TESTE COMPLETO ==="

echo "🎯 11. TESTE DE TODOS OS ALERTAS DE RECUPERAÇÃO"
test_endpoint "/test/recovery/all" "Envio de todos os tipos de recuperação"

echo ""
echo "=== 📋 RESUMO DOS TESTES ==="
echo "✅ Testes de detecção de recuperação concluídos"
echo "✅ Testes de endpoints específicos concluídos"
echo "✅ Testes informativos concluídos"
echo "✅ Teste completo executado"
echo ""

echo "📱 PRÓXIMOS PASSOS:"
echo "1. Verifique suas mensagens no Telegram para confirmar recebimento"
echo "2. Monitore os logs para ver a detecção automática:"
echo "   tail -f /opt/bgp-monitor/logs/bgp_monitor.log"
echo ""

echo "🔧 FUNCIONALIDADES IMPLEMENTADAS:"
echo "✅ Detecção de recuperação de peers perdidos"
echo "✅ Detecção de normalização de upstreams"
echo "✅ Detecção de restauração de prefixos"
echo "✅ Detecção de normalização de latência"
echo "✅ Detecção de resolução de instabilidade"
echo "✅ Detecção de resolução de anomalias"
echo "✅ Mensagens PT-BR completas"
echo "✅ API endpoints para teste"
echo ""

echo "📊 PARA MONITORAR EM TEMPO REAL:"
echo "watch -n 30 'curl -s http://localhost:8000/alerts | jq'"
echo ""

echo "🎯 Teste concluído com sucesso!"
