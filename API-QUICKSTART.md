# BGP Monitor v1.0.0 - API Quick Start Guide

Este guia mostra como usar a API REST do BGP Monitor para configurar e monitorar ASNs.

## 🚀 **Pré-requisitos**

- BGP Monitor v1.0.0 instalado e rodando
- Serviço ativo: `sudo systemctl status bgp-monitor`
- API disponível em: http://localhost:8000

## 🔍 **Verificar Status do Sistema**

```bash
# Status básico da API
curl -s http://localhost:8000/health | jq

# Dashboard completo
curl -s http://localhost:8000/api/v1/bgp/overview | jq

# Documentação interativa
curl http://localhost:8000/docs
```

## 📋 **Gerenciar ASNs**

### **Listar ASNs Configurados**
```bash
curl -s http://localhost:8000/api/v1/bgp/asns | jq
```

### **Adicionar Novo ASN**
```bash
curl -X POST "http://localhost:8000/api/v1/bgp/asns" \
  -H "Content-Type: application/json" \
  -d '{
    "asn": 13335,
    "name": "Cloudflare",
    "description": "Cloudflare Inc.",
    "monitoring_enabled": true,
    "alert_enabled": true
  }'
```

### **Adicionar Múltiplos ASNs**
```bash
curl -X POST "http://localhost:8000/api/v1/bgp/asns/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "asns": [
      {"asn": 15169, "name": "Google", "description": "Google LLC"},
      {"asn": 32934, "name": "Facebook", "description": "Meta Platforms"},
      {"asn": 8075, "name": "Microsoft", "description": "Microsoft Corporation"}
    ]
  }'
```

### **Atualizar ASN**
```bash
curl -X PUT "http://localhost:8000/api/v1/bgp/asns/13335" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cloudflare Updated",
    "description": "Cloudflare Inc. - Updated",
    "monitoring_enabled": true,
    "alert_enabled": false
  }'
```

### **Remover ASN**
```bash
curl -X DELETE "http://localhost:8000/api/v1/bgp/asns/13335"
```

## 📊 **Coleta e Monitoramento de Dados**

### **Forçar Coleta de um ASN**
```bash
curl -X POST "http://localhost:8000/api/v1/bgp/asns/13335/collect"
```

### **Ver Estatísticas de um ASN**
```bash
curl -s http://localhost:8000/api/v1/bgp/asns/13335/statistics | jq
```

### **Verificar Anomalias Detectadas**
```bash
curl -s http://localhost:8000/api/v1/bgp/asns/13335/anomalies | jq
```

### **Ver Mudanças Recentes**
```bash
curl -s http://localhost:8000/api/v1/bgp/asns/13335/changes | jq
```

### **Verificar Instabilidade**
```bash
curl -s http://localhost:8000/api/v1/bgp/asns/13335/instability | jq
```

## 🔔 **Testes de Alertas**

### **Testar Telegram**
```bash
curl -X POST "http://localhost:8000/test/telegram" \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste de alerta do BGP Monitor v2.2.0"}'
```

## 📈 **Métricas e Monitoramento**

### **Métricas do Sistema**
```bash
curl -s http://localhost:8000/metrics | jq
```

### **Overview Geral (Dashboard)**
```bash
curl -s http://localhost:8000/api/v1/bgp/overview | jq
```

## 🛠️ **Backup e Restauração**

### **Exportar Configurações**
```bash
curl -s http://localhost:8000/api/v1/bgp/config/export > backup-asns.json
```

### **Importar Configurações**
```bash
curl -X POST "http://localhost:8000/api/v1/bgp/config/import" \
  -H "Content-Type: application/json" \
  -d @backup-asns.json
```

## 💡 **Exemplos Práticos**

### **Script de Setup Inicial**
```bash
#!/bin/bash

# ASNs importantes para monitorar
ASNS=(
    "13335:Cloudflare:Cloudflare Inc."
    "15169:Google:Google LLC"
    "32934:Facebook:Meta Platforms"
    "8075:Microsoft:Microsoft Corporation"
    "16509:Amazon:Amazon.com Inc."
)

echo "Configurando ASNs para monitoramento..."

for asn_data in "${ASNS[@]}"; do
    IFS=':' read -r asn name description <<< "$asn_data"
    
    echo "Adicionando AS$asn - $name"
    curl -X POST "http://localhost:8000/api/v1/bgp/asns" \
      -H "Content-Type: application/json" \
      -d "{
        \"asn\": $asn,
        \"name\": \"$name\",
        \"description\": \"$description\",
        \"monitoring_enabled\": true,
        \"alert_enabled\": true
      }" && echo
done

echo "Setup concluído!"
```

### **Script de Monitoramento**
```bash
#!/bin/bash

echo "=== BGP Monitor Dashboard ==="
curl -s http://localhost:8000/api/v1/bgp/overview | jq '{
  total_asns,
  enabled_asns,
  monitoring_active,
  anomaly_summary
}'

echo -e "\n=== ASNs Configurados ==="
curl -s http://localhost:8000/api/v1/bgp/asns | jq '.[] | {
  asn,
  name,
  monitoring_enabled,
  alert_enabled
}'
```

## 🔧 **Troubleshooting**

### **Verificar Logs**
```bash
sudo journalctl -u bgp-monitor -f
```

### **Reiniciar Serviço**
```bash
sudo systemctl restart bgp-monitor
```

### **Verificar Conectividade**
```bash
curl -I http://localhost:8000/health
```

---

**BGP Monitor v2.2.0** - Sistema completo de monitoramento BGP 🚀
