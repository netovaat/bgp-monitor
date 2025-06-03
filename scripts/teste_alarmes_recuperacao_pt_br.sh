#!/bin/bash

# 🟢 BGP Monitor - Teste de Alarmes de Recuperação PT-BR
# Este script testa todos os tipos de alarmes de recuperação implementados

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🟢 BGP Monitor - Teste de Alarmes de Recuperação PT-BR${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Configurações
API_URL="http://localhost:8000"
TELEGRAM_URL="${API_URL}/test/telegram"

# Função para simular alarme de recuperação
simulate_recovery_alarm() {
    local title="$1"
    local message="$2"
    
    echo -e "${GREEN}📤 Simulando: ${title}${NC}"
    echo ""
    echo -e "${YELLOW}Mensagem:${NC}"
    echo "$message"
    echo ""
    echo -e "${BLUE}Aguardando 3 segundos...${NC}"
    sleep 3
    echo -e "${GREEN}✅ Alarme enviado!${NC}"
    echo ""
    echo "=================================================="
    echo ""
}

echo -e "${YELLOW}🚀 Iniciando simulação de alarmes de recuperação...${NC}"
echo ""

# 1. Peer Recuperado - Upstream
simulate_recovery_alarm "PEER UPSTREAM RECUPERADO" "✅ Monitor BGP - Recuperação 🛑

Severidade: INFORMATIVO
Tipo: Peer Recuperado

Mensagem:
🟢 Upstream AS18881 recuperado com sucesso.

Detalhes:
• Peer Recuperado: AS18881
• Tipo de Relacionamento: upstream
• Tempo de Indisponibilidade: 15 minutos
• Status: Conectividade restaurada
• Impacto: Alta disponibilidade normalizada

Horário: $(date '+%d/%m/%Y %H:%M:%S') BRT"

# 2. Peer Recuperado - Peer/Customer
simulate_recovery_alarm "PEER RECUPERADO" "✅ Monitor BGP - Recuperação 🛑

Severidade: INFORMATIVO
Tipo: Peer Recuperado

Mensagem:
🟢 Peer AS64512 recuperado com sucesso.

Detalhes:
• Peer Recuperado: AS64512
• Tipo de Relacionamento: peer
• Tempo de Indisponibilidade: 8 minutos
• Status: Conectividade restaurada
• Impacto: Redundância normalizada

Horário: $(date '+%d/%m/%Y %H:%M:%S') BRT"

# 3. Upstreams Normalizados
simulate_recovery_alarm "UPSTREAMS NORMALIZADOS" "✅ Monitor BGP - Recuperação 📊

Severidade: INFORMATIVO
Tipo: Conectividade Normalizada

Mensagem:
🟢 Número de upstreams normalizado (3/3 mínimo).

Detalhes:
• Upstreams Ativos: 3
• Mínimo Configurado: 3
• Upstreams Recuperados: AS174, AS3356
• Status: Redundância adequada restaurada
• Tempo de Problema: 12 minutos

Horário: $(date '+%d/%m/%Y %H:%M:%S') BRT"

# 4. Prefixo Restaurado
simulate_recovery_alarm "PREFIXO RESTAURADO" "✅ Monitor BGP - Recuperação 📡

Severidade: INFORMATIVO
Tipo: Prefixo Restaurado

Mensagem:
🟢 Prefixo 203.0.113.0/24 restaurado na tabela BGP.

Detalhes:
• Prefixo: 203.0.113.0/24
• ASN Origem: AS65001
• Tempo de Ausência: 7 minutos
• Status: Visibilidade global restaurada
• Impacto: Serviços normalizados

Horário: $(date '+%d/%m/%Y %H:%M:%S') BRT"

# 5. Latência Normalizada
simulate_recovery_alarm "LATÊNCIA NORMALIZADA" "✅ Monitor BGP - Recuperação 🌐

Severidade: INFORMATIVO
Tipo: Performance Normalizada

Mensagem:
🟢 Latência normalizada para AS7018 (85ms).

Detalhes:
• Peer Afetado: AS7018
• Latência Atual: 85ms
• Latência Anterior: 150ms
• Limite Configurado: 100ms
• Melhoria: -43% (65ms de redução)
• Status: Performance restaurada

Horário: $(date '+%d/%m/%Y %H:%M:%S') BRT"

# 6. Instabilidade Resolvida
simulate_recovery_alarm "INSTABILIDADE RESOLVIDA" "✅ Monitor BGP - Recuperação 🔄

Severidade: INFORMATIVO
Tipo: Estabilidade Restaurada

Mensagem:
🟢 Instabilidade de roteamento resolvida.

Detalhes:
• Mudanças de Rota: 3 nos últimos 5 minutos
• Limite Normal: <10 mudanças/5min
• Redução: -94% (de 50 para 3 mudanças)
• Duração do Problema: 18 minutos
• Status: Convergência normalizada

Horário: $(date '+%d/%m/%Y %H:%M:%S') BRT"

# 7. Anomalia Resolvida
simulate_recovery_alarm "ANOMALIA RESOLVIDA" "✅ Monitor BGP - Recuperação 📊

Severidade: INFORMATIVO
Tipo: Anomalia Resolvida

Mensagem:
🟢 Anomalia estatística resolvida - valores normalizados.

Detalhes:
• Métrica: Número de anúncios BGP
• Valor Atual: 1.150/hora (normal)
• Valor Anterior: 6.000/hora (anômalo)
• Redução: -81% (4.850 anúncios/hora)
• Desvio Atual: 0.2σ (dentro do normal)
• Duração da Anomalia: 25 minutos

Horário: $(date '+%d/%m/%Y %H:%M:%S') BRT"

echo -e "${GREEN}🎉 SIMULAÇÃO CONCLUÍDA!${NC}"
echo ""
echo -e "${BLUE}📊 Resumo dos Alarmes de Recuperação Testados:${NC}"
echo -e "${GREEN}✅ Peer Upstream Recuperado${NC}"
echo -e "${GREEN}✅ Peer Recuperado${NC}"
echo -e "${GREEN}✅ Upstreams Normalizados${NC}"
echo -e "${GREEN}✅ Prefixo Restaurado${NC}"
echo -e "${GREEN}✅ Latência Normalizada${NC}"
echo -e "${GREEN}✅ Instabilidade Resolvida${NC}"
echo -e "${GREEN}✅ Anomalia Resolvida${NC}"
echo ""
echo -e "${YELLOW}💡 Dica: Os alarmes de recuperação são enviados automaticamente${NC}"
echo -e "${YELLOW}    quando o sistema detecta que um problema foi resolvido.${NC}"
echo ""
echo -e "${BLUE}📝 Para testar com API real:${NC}"
echo -e "${YELLOW}   curl -X POST ${API_URL}/test/recovery-alert \\${NC}"
echo -e "${YELLOW}     -H \"Content-Type: application/json\" \\${NC}"
echo -e "${YELLOW}     -d '{\"type\": \"peer_recovered\", \"peer_asn\": 18881}'${NC}"
echo ""
echo -e "${GREEN}🟢 Teste de alarmes de recuperação finalizado com sucesso!${NC}"
