#!/bin/bash

# Script de teste para endpoints de alarmes de recuperação
# Testa todos os novos endpoints da API BGP Monitor

API_BASE="http://localhost:8000"
DELAY=3

echo "🧪 === TESTE DOS ENDPOINTS DE ALARMES DE RECUPERAÇÃO ==="
echo "Base URL: $API_BASE"
echo "Delay entre testes: ${DELAY}s"
echo ""

# Função para fazer requisição e mostrar resultado
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    
    echo "📋 Testando: $description"
    echo "🔗 Endpoint: $endpoint"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_BASE$endpoint" \
        -H "Content-Type: application/json")
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ Status: $http_code - Sucesso"
        echo "📄 Resposta: $(echo $body | jq -r '.message // .status // "Sem mensagem"' 2>/dev/null || echo "Resposta JSON inválida")"
    else
        echo "❌ Status: $http_code - Erro"
        echo "📄 Erro: $(echo $body | jq -r '.detail // "Erro desconhecido"' 2>/dev/null || echo "Erro não estruturado")"
    fi
    
    echo ""
    sleep $DELAY
}

# Função para testar endpoint GET
test_get_endpoint() {
    local endpoint="$1"
    local description="$2"
    
    echo "📋 Testando: $description"
    echo "🔗 Endpoint: $endpoint"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_BASE$endpoint")
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ Status: $http_code - Sucesso"
        # Para endpoints informativos, mostrar parte do conteúdo
        if [[ "$endpoint" == *"/types"* ]] || [[ "$endpoint" == *"/examples"* ]]; then
            echo "📄 Dados disponíveis: $(echo $body | jq -r 'keys | join(", ")' 2>/dev/null || echo "Dados estruturados")"
        else
            echo "📄 Resposta: $(echo $body | jq -r '.message // .status // "Dados recebidos"' 2>/dev/null || echo "Resposta válida")"
        fi
    else
        echo "❌ Status: $http_code - Erro"
        echo "📄 Erro: $(echo $body | jq -r '.detail // "Erro desconhecido"' 2>/dev/null || echo "Erro não estruturado")"
    fi
    
    echo ""
    sleep $DELAY
}

# Verificar se o servidor está rodando
echo "🔍 Verificando disponibilidade do servidor..."
if ! curl -s "$API_BASE/" > /dev/null; then
    echo "❌ Servidor não está acessível em $API_BASE"
    echo "💡 Certifique-se de que o BGP Monitor está rodando:"
    echo "   cd /opt/bgp-monitor && python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✅ Servidor acessível"
echo ""

# Testes dos endpoints informativos
echo "=== 📊 ENDPOINTS INFORMATIVOS ==="
test_get_endpoint "/alerts/types" "Listar tipos de alertas disponíveis"
test_get_endpoint "/alerts/recovery/examples" "Exemplos de alertas de recuperação PT-BR"

# Testes individuais dos alarmes de recuperação
echo "=== 🟢 TESTES INDIVIDUAIS DE ALARMES DE RECUPERAÇÃO ==="
test_endpoint "/test/recovery/peer" "Alerta de peer recuperado"
test_endpoint "/test/recovery/upstreams" "Alerta de upstreams normalizados"
test_endpoint "/test/recovery/prefix" "Alerta de prefixo restaurado"
test_endpoint "/test/recovery/latency" "Alerta de latência normalizada"
test_endpoint "/test/recovery/instability" "Alerta de instabilidade resolvida"
test_endpoint "/test/recovery/anomaly" "Alerta de anomalia resolvida"

# Teste completo - todos os alertas
echo "=== 🚀 TESTE COMPLETO ==="
echo "📋 Enviando todos os tipos de alertas de recuperação..."
echo "⚠️  Este teste irá enviar 6 mensagens no Telegram com delay de 1s entre elas"
echo ""

response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_BASE/test/recovery/all" \
    -H "Content-Type: application/json")

http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')

if [ "$http_code" -eq 200 ]; then
    echo "✅ Status: $http_code - Teste completo executado"
    total=$(echo $body | jq -r '.total_alerts // 0' 2>/dev/null)
    successful=$(echo $body | jq -r '.successful // 0' 2>/dev/null)
    failed=$(echo $body | jq -r '.failed // 0' 2>/dev/null)
    
    echo "📊 Resultados:"
    echo "   Total de alertas: $total"
    echo "   Sucessos: $successful"
    echo "   Falhas: $failed"
    
    if [ "$failed" -gt 0 ]; then
        echo ""
        echo "❌ Alertas com falha:"
        echo $body | jq -r '.results[] | select(.status == "error") | "   - " + .type + ": " + .message' 2>/dev/null
    fi
else
    echo "❌ Status: $http_code - Erro no teste completo"
    echo "📄 Erro: $(echo $body | jq -r '.detail // "Erro desconhecido"' 2>/dev/null || echo "Erro não estruturado")"
fi

echo ""
echo "=== 📋 RESUMO DOS TESTES ==="
echo "✅ Testes de endpoints informativos concluídos"
echo "✅ Testes individuais de alertas de recuperação concluídos"
echo "✅ Teste completo de todos os alertas concluído"
echo ""
echo "💡 Para monitorar os logs do sistema:"
echo "   tail -f /opt/bgp-monitor/logs/bgp_monitor.log"
echo ""
echo "📱 Verifique suas mensagens no Telegram para confirmar o recebimento dos alertas!"
