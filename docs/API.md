# 🌐 Referência da API

Documentação completa da API REST do BGP Monitor v1.0.0.

## 📋 Visão Geral

- **Base URL**: `http://localhost:8000`
- **Formato**: JSON
- **Autenticação**: Não requerida (local)
- **Versionamento**: v1.0.0
- **Documentação Interativa**: 
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

## 🏠 Endpoints de Sistema

### Status do Sistema

#### `GET /health`
Verificação de saúde do sistema.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-05-28T10:00:00Z",
  "uptime_seconds": 86400,
  "version": "1.0.0",
  "database_connected": true,
  "scheduler_running": true,
  "asns_monitored": 52,
  "last_collection": "2025-05-28T09:45:00Z"
}
```

#### `GET /dashboard`
Dashboard principal com visão geral de todos os ASNs.

**Resposta:**
```json
{
  "total_asns": 52,
  "active_asns": 48,
  "last_collection": "2025-05-28T09:45:00Z",
  "collection_duration": 420.5,
  "recent_anomalies": 3,
  "asn_stats": [
    {
      "asn": 64512,
      "name": "Empresa A",
      "prefix_count": 24,
      "last_update": "2025-05-28T09:45:12Z",
      "anomaly_count": 0,
      "status": "active"
    }
  ],
  "top_prefixes": [
    {"asn": 15169, "count": 8520},
    {"asn": 8075, "count": 5680}
  ]
}
```

#### `GET /metrics`
Métricas detalhadas do sistema.

**Resposta:**
```json
{
  "system_metrics": {
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "disk_usage": 12.3
  },
  "collection_performance": {
    "total_collections": 1547,
    "avg_duration": 380.5,
    "success_rate": 98.7,
    "last_collection": "2025-05-28T09:45:00Z"
  },
  "rate_limiting": {
    "requests_per_hour": 240,
    "limit_reached": false,
    "next_collection": "2025-05-28T10:00:00Z"
  },
  "database_stats": {
    "total_snapshots": 45000,
    "size_mb": 2048,
    "oldest_record": "2024-05-28T10:00:00Z"
  },
  "anomaly_detection": {
    "total_anomalies": 127,
    "last_24h": 8,
    "sensitivity": 2.0,
    "baseline_days": 30
  }
## 🎯 Gestão de ASNs

### Listar ASNs

#### `GET /asns`
Lista todos os ASNs configurados.

**Parâmetros Query:**
- `enabled` (bool): Filtrar por ASNs ativos/inativos
- `limit` (int): Limite de resultados (padrão: 100)
- `offset` (int): Offset para paginação

**Resposta:**
```json
[
  {
    "asn": 64512,
    "name": "Minha Empresa",
    "description": "ASN principal da rede",
    "enabled": true,
    "created_at": "2025-05-28T08:00:00Z",
    "updated_at": "2025-05-28T08:00:00Z",
    "last_snapshot": "2025-05-28T09:45:00Z",
    "prefix_count": 24,
    "status": "active"
  }
]
```

### Obter ASN Específico

#### `GET /asns/{asn}`
Obtém detalhes de um ASN específico.

**Resposta:**
```json
{
  "asn": 64512,
  "name": "Minha Empresa",
  "description": "ASN principal da rede",
  "enabled": true,
  "created_at": "2025-05-28T08:00:00Z",
  "updated_at": "2025-05-28T08:00:00Z",
  "last_snapshot": "2025-05-28T09:45:00Z",
  "prefix_count": 24,
  "recent_anomalies": 2,
  "prefixes": [
    "203.0.113.0/24",
    "198.51.100.0/24"
  ]
}
```

### Adicionar ASN

#### `POST /asns`
Adiciona um novo ASN para monitoramento.

**Body:**
```json
{
  "asn": 64512,
  "name": "Minha Empresa",
  "description": "ASN principal da rede",
  "enabled": true
}
```

**Resposta:**
```json
{
  "asn": 64512,
  "name": "Minha Empresa",
  "description": "ASN principal da rede",
  "enabled": true,
  "created_at": "2025-05-28T10:00:00Z",
  "status": "created"
}
```

### Adicionar Múltiplos ASNs

#### `POST /asns/batch`
Adiciona múltiplos ASNs em uma única operação.

**Body:**
```json
{
  "asns": [
    {
      "asn": 64512,
      "name": "Empresa A",
      "description": "ASN principal",
      "enabled": true
    },
    {
      "asn": 64513,
      "name": "Empresa B",
      "description": "ASN secundário",
      "enabled": false
    }
  ]
}
```

**Resposta:**
```json
{
  "created": 2,
  "failed": 0,
  "results": [
    {"asn": 64512, "status": "created"},
    {"asn": 64513, "status": "created"}
  ]
}
```

### Atualizar ASN

#### `PUT /asns/{asn}`
Atualiza configurações de um ASN existente.

**Body:**
```json
{
  "name": "Novo Nome",
  "description": "Nova descrição",
  "enabled": false
}
```

### Deletar ASN

#### `DELETE /asns/{asn}`
Remove um ASN do monitoramento.

**Resposta:**
```json
{
  "asn": 64512,
  "status": "deleted",
  "message": "ASN removido com sucesso"
}
```

### Import/Export

#### `GET /asns/export`
Exporta configuração de todos os ASNs.

**Resposta:**
```json
{
  "version": "1.0.0",
  "exported_at": "2025-05-28T10:00:00Z",
  "asns": [
    {
      "asn": 64512,
      "name": "Minha Empresa",
      "description": "ASN principal",
      "enabled": true
    }
  ]
}
```

#### `POST /asns/import`
Importa configuração de ASNs.

**Body:**
```json
{
  "asns": [
    {
      "asn": 64512,
      "name": "Minha Empresa",
      "description": "ASN principal",
      "enabled": true
    }
  ]
}
```
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

## 🧪 Endpoints de Teste

### Testar Detecção de Anomalias

#### `POST /test/simulate-anomaly`
Simula uma anomalia para teste do sistema de detecção.

**Body:**
```json
{
  "asn": 64512,
  "type": "sudden_increase",
  "magnitude": 0.5,
  "data_type": "prefixes"
}
```

**Resposta:**
```json
{
  "status": "simulated",
  "anomaly_id": 5678,
  "message": "Anomalia simulada com sucesso",
  "details": {
    "asn": 64512,
    "type": "sudden_increase",
    "baseline": 1250,
    "simulated_value": 1875,
    "z_score": 3.2,
    "severity": "warning"
  }
}
```

### Testar Coleta RIPE

#### `POST /test/ripe-api`
Testa conectividade e resposta da API RIPE.

**Body:**
```json
{
  "asn": 64512
}
```

**Resposta:**
```json
{
  "status": "success",
  "response_time": 245.7,
  "api_version": "v1",
  "data_retrieved": {
    "prefixes": 1250,
    "peers": 45,
    "countries": 15
  },
  "rate_limit_status": {
    "remaining": 950,
    "reset_time": "2025-05-28T11:00:00Z"
  }
}
```

### Validar Configuração

#### `POST /test/validate-config`
Valida configuração completa do sistema.

**Resposta:**
```json
{
  "status": "valid",
  "checks": {
    "database": {
      "status": "connected",
      "version": "PostgreSQL 15.3",
      "tables": "all_present"
    },
    "telegram": {
      "status": "configured",
      "bot_token": "valid",
      "chat_id": "reachable"
    },
    "ripe_api": {
      "status": "accessible",
      "response_time": 156.2
    },
    "scheduler": {
      "status": "running",
      "next_run": "2025-05-28T10:15:00Z"
    }
  },
  "warnings": [],
  "errors": []
}
```

## 📱 Alertas Telegram

### Configurar Telegram

#### `POST /telegram/config`
Configura ou atualiza configurações do Telegram.

**Body:**
```json
{
  "bot_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh",
  "chat_id": "-1001234567890",
  "enabled": true,
  "alert_levels": ["critical", "warning"]
}
```

**Resposta:**
```json
{
  "status": "configured",
  "message": "Configuração salva com sucesso",
  "bot_info": {
    "username": "BGPMonitorBot",
    "first_name": "BGP Monitor",
    "verified": true
  },
  "chat_info": {
    "type": "supergroup",
    "title": "BGP Alerts",
    "member_count": 15
  }
}
```

### Testar Telegram

#### `POST /telegram/test`
Envia uma mensagem de teste para verificar funcionamento.

**Body (opcional):**
```json
{
  "message": "Teste personalizado do sistema",
  "alert_type": "info"
}
```

**Resposta:**
```json
{
  "status": "sent",
  "message_id": 12345,
  "sent_at": "2025-05-28T10:05:00Z",
  "delivery_time": 1.2,
  "message_preview": "🧪 TESTE BGP Monitor v1.0.0..."
}
```

### Status do Telegram

#### `GET /telegram/status`
Status atual do sistema Telegram.

**Resposta:**
```json
{
  "configured": true,
  "enabled": true,
  "bot_status": "active",
  "last_message": "2025-05-28T09:47:23Z",
  "total_sent": 1247,
  "success_rate": 99.8,
  "alert_queue": 0,
  "rate_limiting": {
    "enabled": true,
    "max_per_minute": 20,
    "current_usage": 3
  }
}
```

### Histórico de Alertas

#### `GET /telegram/history`
Histórico de alertas enviados via Telegram.

**Parâmetros Query:**
- `limit` (int): Número de registros (padrão: 50)
- `severity` (string): Filtrar por severidade
- `asn` (int): Filtrar por ASN

**Resposta:**
```json
[
  {
    "id": 9876,
    "asn": 64512,
    "message": "🚨 CRÍTICO: ASN 64512 - Perda súbita de 85% dos prefixos",
    "severity": "critical",
    "sent_at": "2025-05-28T09:47:23Z",
    "delivered": true,
    "message_id": 12344,
    "anomaly_id": 5677
  }
]
```

## ⚙️ Administração

### Informações do Sistema

#### `GET /admin/system-info`
Informações detalhadas do sistema.

**Resposta:**
```json
{
  "version": "1.0.0",
  "uptime": 172800,
  "python_version": "3.11.4",
  "system": {
    "os": "Linux Ubuntu 22.04.3",
    "cpu_cores": 4,
    "memory_total": "8 GB",
    "memory_used": "2.1 GB",
    "disk_usage": "45%"
  },
  "database": {
    "type": "PostgreSQL",
    "version": "15.3",
    "size": "2.3 GB",
    "connections": 12,
    "table_count": 8
  },
  "monitoring": {
    "active_asns": 48,
    "total_records": 2847392,
    "oldest_record": "2024-05-28T10:00:00Z",
    "collection_rate": "15 min"
  }
}
```

### Logs do Sistema

#### `GET /admin/logs`
Últimos logs do sistema.

**Parâmetros Query:**
- `level` (string): info, warning, error, critical
- `limit` (int): Número de linhas (padrão: 100)
- `component` (string): scheduler, api, telegram, anomaly

**Resposta:**
```json
[
  {
    "timestamp": "2025-05-28T10:05:00Z",
    "level": "INFO",
    "component": "scheduler",
    "message": "Coleta concluída: 48 ASNs processados",
    "details": {
      "duration": 435.2,
      "success_count": 47,
      "anomalies": 2
    }
  }
]
```

### Limpeza de Dados

#### `POST /admin/cleanup`
Executa limpeza manual de dados antigos.

**Body:**
```json
{
  "older_than_days": 365,
  "dry_run": false
}
```

**Resposta:**
```json
{
  "status": "completed",
  "records_deleted": 125847,
  "space_freed": "1.2 GB",
  "duration": 45.3,
  "tables_affected": [
    "bgp_data",
    "anomalies", 
    "collection_logs"
  ]
}
```

### Backup de Configuração

#### `GET /admin/export-config`
Exporta configuração completa do sistema.

**Resposta:**
```json
{
  "version": "1.0.0",
  "exported_at": "2025-05-28T10:10:00Z",
  "asns": [
    {
      "asn": 64512,
      "name": "Empresa A",
      "description": "ASN principal",
      "enabled": true
    }
  ],
  "settings": {
    "collection_interval": 900,
    "retention_days": 365,
    "rate_limiting": true,
    "anomaly_thresholds": {
      "z_score_threshold": 2.5,
      "minimum_baseline_days": 7
    }
  },
  "telegram": {
    "enabled": true,
    "alert_levels": ["critical", "warning"]
  }
}
```

### Restaurar Configuração

#### `POST /admin/import-config`
Importa configuração do sistema.

**Body:**
```json
{
  "config": {
    "asns": [...],
    "settings": {...},
    "telegram": {...}
  },
  "overwrite_existing": false
}
```

**Resposta:**
```json
{
  "status": "imported",
  "imported_asns": 48,
  "updated_settings": 12,
  "warnings": [
    "ASN 64512 já existe, mantida configuração atual"
  ],
  "errors": []
}
```

### Reset do Sistema

#### `POST /admin/reset`
Reset completo do sistema (usar com cuidado).

**Body:**
```json
{
  "confirm": "RESET_BGP_MONITOR",
  "keep_data": false,
  "keep_config": false
}
```

**Resposta:**
```json
{
  "status": "reset_completed",
  "message": "Sistema resetado com sucesso",
  "actions_performed": [
    "Dados BGP removidos",
    "Configurações resetadas",
    "Cache limpo",
    "Scheduler reiniciado"
  ],
  "restart_required": true
}
```

## 📈 Exemplos de Uso Completos

### Configuração Inicial do Sistema

```bash
# 1. Verificar saúde do sistema
curl http://localhost:8000/health

# 2. Configurar Telegram
curl -X POST http://localhost:8000/telegram/config \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "SEU_BOT_TOKEN",
    "chat_id": "SEU_CHAT_ID",
    "enabled": true,
    "alert_levels": ["critical", "warning"]
  }'

# 3. Adicionar ASNs para monitoramento
curl -X POST http://localhost:8000/asns/batch \
  -H "Content-Type: application/json" \
  -d '{
    "asns": [
      {"asn": 64512, "name": "Empresa A", "enabled": true},
      {"asn": 64513, "name": "Empresa B", "enabled": true}
    ]
  }'

# 4. Testar sistema completo
curl -X POST http://localhost:8000/test/validate-config
```

### Monitoramento Diário

```bash
# Dashboard geral
curl http://localhost:8000/dashboard

# Verificar anomalias recentes
curl http://localhost:8000/anomalies?limit=10

# Status do scheduler
curl http://localhost:8000/scheduler/status

# Forçar coleta se necessário
curl -X POST http://localhost:8000/collect/force
```

### Análise de Problemas

```bash
# Dados históricos de um ASN problemático
curl http://localhost:8000/historical/64512?days=7

# Anomalias específicas do ASN
curl http://localhost:8000/anomalies/64512

# Logs do sistema
curl "http://localhost:8000/admin/logs?level=error&limit=50"

# Teste de conectividade
curl -X POST http://localhost:8000/test/ripe-api \
  -H "Content-Type: application/json" \
  -d '{"asn": 64512}'
```

---

## 🔗 Links Úteis

- **Documentação Completa**: [docs/](../docs/)
- **Configuração**: [CONFIGURATION.md](CONFIGURATION.md)
- **Guia de Uso**: [USAGE.md](USAGE.md)
- **Arquitetura**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**BGP Monitor v1.0.0** - Sistema completo de monitoramento BGP com PostgreSQL e detecção de anomalias.
