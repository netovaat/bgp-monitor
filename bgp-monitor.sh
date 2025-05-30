#!/bin/bash
# BGP Monitor - Script de gerenciamento simplificado

set -e

show_help() {
    echo "BGP Monitor - Sistema de Monitoramento BGP"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos:"
    echo "  start       Inicia o BGP Monitor"
    echo "  stop        Para o BGP Monitor"
    echo "  status      Verifica status do sistema"
    echo "  test        Executa testes básicos"
    echo "  help        Mostra esta ajuda"
    echo ""
}

start_service() {
    echo "🚀 Iniciando BGP Monitor..."
    python3 -m app.main
}

stop_service() {
    echo "🛑 Parando BGP Monitor..."
    pkill -f "app.main" || echo "Processo não encontrado"
}

check_status() {
    echo "📊 Verificando status..."
    curl -s http://localhost:8000/health || echo "❌ BGP Monitor não está rodando"
}

run_tests() {
    echo "🧪 Executando testes..."
    echo "1. Testando API..."
    curl -s http://localhost:8000/ && echo "✅ API OK"
    echo "2. Testando saúde..."
    curl -s http://localhost:8000/health && echo "✅ Health OK"
}

case "${1:-help}" in
    start) start_service ;;
    stop) stop_service ;;
    status) check_status ;;
    test) run_tests ;;
    *) show_help ;;
esac

check_dependencies() {
    echo "Verificando dependências..."
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 não encontrado"
        exit 1
    fi
    
    if ! python3 -c "import fastapi" 2>/dev/null; then
        echo "❌ FastAPI não instalado. Execute: $0 install"
        exit 1
    fi
    
    echo "✅ Dependências OK"
}

start_service() {
    echo "🚀 Iniciando BGP Monitor..."
    
    # Verificar se o ambiente virtual existe
    if [[ ! -d "venv" ]]; then
        echo "❌ Ambiente virtual não encontrado. Execute o script de instalação primeiro."
        exit 1
    fi
    
    check_dependencies
    
    if pgrep -f "app.main" > /dev/null; then
        echo "⚠️  BGP Monitor já está rodando"
        return 0
    fi
    
    echo "Carregando configurações..."
    if [[ ! -f ".env" ]]; then
        echo "⚠️  Arquivo .env não encontrado, usando configurações padrão"
    fi
    
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
    
    echo "Iniciando servidor..."
    python -m app.main &
    echo $! > bgp-monitor.pid
    
    sleep 3
    if check_status_quiet; then
        echo "✅ BGP Monitor iniciado com sucesso!"
        echo "🌐 API disponível em: http://localhost:8000"
        echo "📊 Métricas em: http://localhost:8000/metrics"
    else
        echo "❌ Falha ao iniciar BGP Monitor"
        exit 1
    fi
}

stop_service() {
    echo "🛑 Parando BGP Monitor..."
    
    if [[ -f "bgp-monitor.pid" ]]; then
        PID=$(cat bgp-monitor.pid)
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f bgp-monitor.pid
            echo "✅ BGP Monitor parado"
        else
            echo "⚠️  Processo não encontrado, removendo PID file"
            rm -f bgp-monitor.pid
        fi
    else
        # Tenta matar pelo nome do processo
        if pgrep -f "app.main" > /dev/null; then
            pkill -f "app.main"
            echo "✅ BGP Monitor parado"
        else
            echo "⚠️  BGP Monitor não estava rodando"
        fi
    fi
}

check_status_quiet() {
    curl -s http://localhost:8000/health > /dev/null 2>&1
}

check_status() {
    echo "📊 Verificando status do BGP Monitor..."
    
    if check_status_quiet; then
        echo "✅ BGP Monitor está rodando"
        echo ""
        echo "Status da API:"
        curl -s http://localhost:8000/ | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"  Serviço: {data['service']} v{data['version']}\")
print(f\"  Status: {data['status']}\")
print(f\"  ASN Alvo: {data['target_asn']}\")
print(f\"  Uptime: {data['uptime']}s\")
"
        echo ""
        echo "Saúde do sistema:"
        curl -s http://localhost:8000/health | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"  Status: {data['status']}\")
print(f\"  Componentes saudáveis: {data['healthy_components']}\")
print(f\"  Total de alertas: {data['total_alerts']}\")
"
    else
        echo "❌ BGP Monitor não está rodando"
        return 1
    fi
}

run_tests() {
    echo "🧪 Executando testes básicos..."
    
    if ! check_status_quiet; then
        echo "❌ BGP Monitor não está rodando. Execute: $0 start"
        exit 1
    fi
    
    echo "1. Testando endpoint raiz..."
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "   ✅ OK"
    else
        echo "   ❌ Falha"
    fi
    
    echo "2. Testando endpoint de saúde..."
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "   ✅ OK"
    else
        echo "   ❌ Falha"
    fi
    
    echo "3. Testando endpoint de métricas..."
    if curl -s http://localhost:8000/metrics > /dev/null; then
        echo "   ✅ OK"
    else
        echo "   ❌ Falha"
    fi
    
    echo "4. Testando verificações manuais..."
    if curl -s -X POST http://localhost:8000/monitoring/run-checks > /dev/null; then
        echo "   ✅ OK"
    else
        echo "   ❌ Falha"
    fi
    
    echo ""
    echo "🎉 Testes concluídos!"
}

install_deps() {
    echo "📦 Instalando dependências..."
    
    if [[ ! -f "requirements.txt" ]]; then
        echo "❌ Arquivo requirements.txt não encontrado"
        exit 1
    fi
    
    python3 -m pip install -r requirements.txt
    echo "✅ Dependências instaladas!"
}

show_config() {
    echo "⚙️  Configuração atual:"
    echo ""
    
    if [[ -f ".env" ]]; then
        echo "Arquivo .env:"
        grep -E "^[^#]" .env | while IFS='=' read -r key value; do
            if [[ "$key" =~ TOKEN ]]; then
                echo "  $key=***hidden***"
            else
                echo "  $key=$value"
            fi
        done
    else
        echo "  ⚠️  Arquivo .env não encontrado"
    fi
    
    echo ""
    if check_status_quiet; then
        echo "Configuração da API:"
        curl -s http://localhost:8000/config | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"  ASN Alvo: {data['target_asn']}\")
print(f\"  Latência Máxima: {data['max_latency_ms']}ms\")
print(f\"  Upstreams Mínimos: {data['min_upstreams']}\")
print(f\"  Intervalos de Check:\")
for check, interval in data['check_intervals'].items():
    print(f\"    {check}: {interval}s\")
"
    fi
}

show_logs() {
    echo "📝 Logs do BGP Monitor (Ctrl+C para sair)..."
    if [[ -f "bgp-monitor.pid" ]]; then
        PID=$(cat bgp-monitor.pid)
        tail -f /proc/$PID/fd/1 2>/dev/null || echo "❌ Não foi possível acessar os logs"
    else
        echo "❌ BGP Monitor não está rodando ou PID file não encontrado"
    fi
}

case "${1:-help}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 2
        start_service
        ;;
    status)
        check_status
        ;;
    test)
        run_tests
        ;;
    install)
        install_deps
        ;;
    config)
        show_config
        ;;
    logs)
        show_logs
        ;;
    help|*)
        show_help
        ;;
esac
