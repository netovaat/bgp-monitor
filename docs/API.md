# 🌐 Referência da API

Documentação completa da API REST do BGP Monitor v1.0.

## 📋 Visão Geral

- **Base URL**: `http://localhost:8000`
- **Formato**: JSON
- **Autenticação**: Não requerida (local)
- **Versionamento**: v1 (implícito)

## 🏠 Endpoints Principais

### Status do Sistema

#### `GET /`
Informações básicas do sistema.

**Resposta:**
```json
{
  "service": "BGP Monitor",
  "version": "1.0.0",
  "status": "running",
  "target_asn": 64512,
  "uptime": 1234
}
```

#### `GET /health`
Verificação de saúde do sistema.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-05-27T10:00:00Z",
  "uptime_seconds": 1234,
  "total_alerts": 0,
  "healthy_components": 3
}
```

#### `GET /metrics`
Métricas detalhadas do sistema.

**Resposta:**
```json
{
  "uptime_seconds": 1234,
  "total_alerts": 5,
  "healthy_components": 3,
  "total_components": 3,
  "last_checks": {
    "prefix_check": "2025-05-27T09:55:00Z",
    "peer_check": "2025-05-27T09:50:00Z"
  },
  "alert_breakdown": {
    "prefix_missing": 2,
    "peer_loss": 3
  }
}
```

## 📡 Gerenciamento de Prefixos

### `GET /prefixes`
Lista todos os prefixos monitorados.

**Resposta:**
```json
[
  {
    "id": 1,
    "prefix": "203.0.113.0/24",
    "asn": 64512,
    "description": "Rede principal",
    "created_at": "2025-05-27T08:00:00Z",
    "is_active": true
  }
]
```

### `POST /prefixes`
Adiciona um novo prefixo para monitoramento.

**Requisição:**
```json
{
  "prefix": "203.0.113.0/24",
  "asn": 64512,
  "description": "Rede principal"
}
```

**Resposta (201):**
```json
{
  "id": 1,
  "prefix": "203.0.113.0/24",
  "asn": 64512,
  "description": "Rede principal",
  "created_at": "2025-05-27T10:00:00Z",
  "is_active": true
}
```

**Erros:**
- `400`: Dados inválidos
- `409`: Prefixo já existe

### `DELETE /prefixes/{prefix_id}`
Remove um prefixo do monitoramento.

**Resposta (200):**
```json
{
  "message": "Prefixo removido com sucesso",
  "prefix": "203.0.113.0/24"
}
```

**Erros:**
- `404`: Prefixo não encontrado

## 🚨 Alertas

### `GET /alerts`
Lista alertas recentes.

**Parâmetros:**
- `type` (opcional): Filtrar por tipo de alerta
- `severity` (opcional): Filtrar por severidade
- `limit` (opcional): Limitar número de resultados (padrão: 50)

**Resposta:**
```json
[
  {
    "id": 1,
    "alert_type": "prefix_missing",
    "severity": "critical",
    "title": "Prefixo 203.0.113.0/24 não encontrado",
    "message": "🚨 O prefixo 203.0.113.0/24 do AS64512 não foi encontrado nos anúncios globais do BGP.",
    "timestamp": "2025-05-27T09:30:00Z",
    "details": {
      "prefix": "203.0.113.0/24",
      "asn": 64512,
      "last_seen": null
    },
    "resolved": false
  }
]
```

### `POST /alerts/silence`
Silencia alertas específicos.

**Requisição:**
```json
{
  "type": "prefix_missing",
  "prefix": "203.0.113.0/24",
  "duration": 3600
}
```

## 🔍 Monitoramento

### `POST /monitoring/run-checks`
Executa todas as verificações manualmente.

**Resposta:**
```json
{
  "message": "Verificações iniciadas",
  "checks": [
    "prefix_announcements",
    "peer_relationships", 
    "irr_validation"
  ],
  "estimated_duration": 30
}
```

### `GET /monitoring/status`
Status detalhado dos monitores.

**Resposta:**
```json
{
  "monitors": {
    "prefix_monitor": {
      "status": "healthy",
      "last_check": "2025-05-27T09:55:00Z",
      "next_check": "2025-05-27T10:00:00Z",
      "prefixes_monitored": 5,
      "issues_found": 0
    },
    "peer_monitor": {
      "status": "healthy", 
      "last_check": "2025-05-27T09:50:00Z",
      "next_check": "2025-05-27T10:00:00Z",
      "peers_monitored": 12,
      "issues_found": 1
    },
    "irr_validator": {
      "status": "healthy",
      "last_check": "2025-05-27T09:45:00Z", 
      "next_check": "2025-05-27T10:00:00Z",
      "validations_cached": 15,
      "inconsistencies": 0
    }
  }
}
```

## 📊 Relatórios

### `GET /reports/daily`
Relatório diário consolidado.

**Resposta:**
```json
{
  "date": "2025-05-27",
  "summary": {
    "total_checks": 288,
    "alerts_generated": 5,
    "prefixes_monitored": 10,
    "avg_response_time": 1.2
  },
  "alerts": [
    {
      "time": "09:30:00",
      "type": "prefix_missing",
      "prefix": "203.0.113.0/24",
      "duration": 15
    }
  ],
  "performance": {
    "prefix_checks": {
      "total": 144,
      "avg_duration": 2.1,
      "failures": 0
    }
  }
}
```

### `GET /reports/custom`
Relatório personalizado.

**Parâmetros:**
- `from`: Data/hora início (ISO 8601)
- `to`: Data/hora fim (ISO 8601)
- `include`: Seções a incluir (alerts,metrics,performance)

## 🧪 Testes

### `POST /test/telegram`
Testa conectividade com Telegram.

**Requisição:**
```json
{
  "message": "Teste do BGP Monitor"
}
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "Mensagem enviada com sucesso",
  "chat_id": "-1001234567890"
}
```

**Erros:**
- `401`: Token inválido
- `404`: Chat não encontrado
- `500`: Erro de conectividade

### `POST /test/connectivity`
Testa conectividade com serviços externos.

**Resposta:**
```json
{
  "ripe_api": {
    "status": "ok",
    "response_time": 245
  },
  "telegram": {
    "status": "ok", 
    "response_time": 156
  },
  "dns": {
    "status": "ok",
    "servers": ["8.8.8.8", "1.1.1.1"]
  }
}
```

## ⚙️ Configuração

### `GET /config`
Retorna configurações atuais do sistema.

**Resposta:**
```json
{
  "target_asn": 64512,
  "intervals": {
    "prefix_check": 300,
    "peer_check": 600,
    "irr_check": 900
  },
  "thresholds": {
    "min_peers": 3,
    "min_upstreams": 2
  },
  "telegram": {
    "configured": true,
    "chat_id": "-1001234567890"
  }
}
```

### `PUT /config/intervals`
Atualiza intervalos de verificação.

**Requisição:**
```json
{
  "prefix_check": 180,
  "peer_check": 300
}
```

## 📤 Export

### `GET /export/config`
Exporta configuração completa.

**Formatos:** `json`, `yaml`
**Parâmetro:** `?format=json`

### `GET /export/metrics`
Exporta métricas históricas.

**Formatos:** `json`, `csv`, `prometheus`
**Parâmetros:**
- `format`: Formato de saída
- `from`: Data início
- `to`: Data fim

## 🔍 Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisição inválida |
| 401 | Não autorizado |
| 404 | Não encontrado |
| 409 | Conflito (recurso já existe) |
| 422 | Dados inválidos |
| 500 | Erro interno do servidor |
| 503 | Serviço indisponível |

## 🚀 Exemplos com cURL

### Adicionar Prefixo
```bash
curl -X POST http://localhost:8000/prefixes \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "203.0.113.0/24",
    "asn": 64512,
    "description": "Rede principal"
  }'
```

### Listar Alertas Críticos
```bash
curl "http://localhost:8000/alerts?severity=critical&limit=10"
```

### Executar Verificações
```bash
curl -X POST http://localhost:8000/monitoring/run-checks
```

### Testar Telegram
```bash
curl -X POST http://localhost:8000/test/telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste do BGP Monitor"}'
```

### Obter Relatório Diário
```bash
curl http://localhost:8000/reports/daily | jq .
```

## 📱 SDK/Clientes

### Python
```python
import requests

class BGPMonitorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def add_prefix(self, prefix, asn, description=""):
        response = requests.post(
            f"{self.base_url}/prefixes",
            json={
                "prefix": prefix,
                "asn": asn, 
                "description": description
            }
        )
        return response.json()
    
    def get_health(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Uso
client = BGPMonitorClient()
client.add_prefix("203.0.113.0/24", 64512, "Rede principal")
```

### Bash
```bash
#!/bin/bash

BGP_API="http://localhost:8000"

function bgp_add_prefix() {
    local prefix=$1
    local asn=$2
    local desc=$3
    
    curl -X POST "$BGP_API/prefixes" \
        -H "Content-Type: application/json" \
        -d "{\"prefix\":\"$prefix\",\"asn\":$asn,\"description\":\"$desc\"}"
}

function bgp_get_status() {
    curl -s "$BGP_API/health" | jq .
}
```

## 🔒 Segurança

### Rate Limiting
- 100 requisições por minuto por IP
- 10 requisições por segundo para endpoints de teste

### Headers de Segurança
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### CORS
Configurado para aceitar requisições de qualquer origem em desenvolvimento.
Para produção, configure origins específicas.

## 📚 Próximos Passos

Para entender melhor o sistema:

1. [🏗️ Arquitetura do Sistema](ARCHITECTURE.md)
2. [🔍 Troubleshooting](TROUBLESHOOTING.md)
3. [🤝 Como Contribuir](../CONTRIBUTING.md)
