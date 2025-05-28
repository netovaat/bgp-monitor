# 🏗️ Arquitetura

Documentação detalhada da arquitetura do BGP Monitor v2.0.

## 🎯 Visão Geral

O BGP Monitor v2.0 foi projetado como **sistema robusto de produção** com arquitetura escalável, priorizando:

- **Persistência**: PostgreSQL para dados históricos confiáveis
- **Escalabilidade**: Suporte a múltiplos ASNs simultaneamente
- **Inteligência**: Detecção de anomalias com análise estatística
- **Confiabilidade**: Rate limiting e recuperação de falhas
- **Observabilidade**: Logs, métricas e alertas avançados

## 📋 Princípios de Design v2.0

### 1. **Production-Ready Architecture**
- PostgreSQL para persistência de dados
- Rate limiting inteligente para APIs
- Sistema de alertas robusto
- Monitoramento e observabilidade

### 2. **Data-Driven Intelligence**
- Histórico de 1 ano para análise de tendências
- Algoritmos estatísticos para detecção de anomalias
- Baseline dinâmico para maior precisão
- Métricas contextuais e correlações

### 3. **Multi-ASN Scale**
- Monitoramento simultâneo de 50+ ASNs
- Batching otimizado para APIs externas
- Paralelização inteligente de coletas
- Gestão granular por ASN

### 4. **Enterprise Features**
- API REST completa com autenticação
- Sistema de backup e recuperação
- Logs estruturados para auditoria
- Dashboard em tempo real

## 🏛️ Arquitetura de Alto Nível v2.0

```
┌─────────────────────────────────────────────────────────────┐
│                    BGP Monitor v2.0                        │
├─────────────────────────────────────────────────────────────┤
│  🌐 API Layer      │  📊 Analytics    │  🔔 Alerting       │
│  ├─ REST API       │  ├─ Dashboard    │  ├─ Telegram Bot   │
│  ├─ FastAPI        │  ├─ Metrics      │  ├─ Alert Queue    │
│  └─ Authentication │  └─ Reporting    │  └─ Notifications  │
├─────────────────────────────────────────────────────────────┤
│  🧠 Intelligence   │  ⏰ Scheduling   │  🎯 ASN Management │
│  ├─ Anomaly Det.   │  ├─ Cron Jobs    │  ├─ Multi-ASN      │
│  ├─ Z-score Anal.  │  ├─ Rate Limit   │  ├─ CRUD Ops       │
│  └─ Pattern Rec.   │  └─ Queue Mgmt   │  └─ Batch Import   │
├─────────────────────────────────────────────────────────────┤
│  🌍 External APIs  │  💾 Data Layer   │  🛠️ Infrastructure │
│  ├─ RIPE Stat      │  ├─ PostgreSQL   │  ├─ Systemd        │
│  ├─ BGPView        │  ├─ Alembic      │  ├─ Docker Ready   │
│  └─ Resilience     │  └─ Migrations   │  └─ Log Rotation   │
```

## 📁 Estrutura de Diretórios v2.0

```
bgp-monitor/
├── app/                          # Aplicação principal
│   ├── main.py                   # Ponto de entrada
│   ├── scheduler.py              # Agendador de tarefas
│   ├── api/                      # API REST
│   │   ├── __init__.py
│   │   ├── main.py               # Endpoints FastAPI
│   │   ├── endpoints/            # Endpoints organizados
│   │   │   ├── asns.py           # Gestão de ASNs
│   │   │   ├── data.py           # Dados históricos
│   │   │   ├── anomalies.py      # Anomalias
│   │   │   ├── telegram.py       # Alertas
│   │   │   └── admin.py          # Administração
│   │   └── dependencies.py       # Dependências FastAPI
│   ├── core/                     # Componentes centrais
│   │   ├── config.py             # Configurações
│   │   ├── logging.py            # Sistema de logs
│   │   └── security.py           # Autenticação
│   ├── database/                 # Camada de dados
│   │   ├── connection.py         # Pool PostgreSQL
│   │   ├── migrations/           # Migrações Alembic
│   │   └── repositories/         # Padrão Repository
│   ├── models/                   # Modelos de dados
│   │   ├── database.py           # SQLAlchemy models
│   │   ├── schemas.py            # Pydantic schemas
│   │   └── enums.py              # Enumerações
│   ├── services/                 # Serviços de negócio
│   │   ├── bgp_service.py        # Coleta BGP
│   │   ├── anomaly_service.py    # Detecção anomalias
│   │   ├── alert_service.py      # Sistema de alertas
│   │   ├── telegram_service.py   # Cliente Telegram
│   │   └── ripe_client.py        # Cliente RIPE
│   └── utils/                    # Utilitários
│       ├── metrics.py            # Sistema de métricas
│       ├── rate_limiter.py       # Rate limiting
│       └── statistics.py         # Cálculos estatísticos
├── docs/                         # Documentação completa
│   ├── API.md                    # Documentação da API
│   ├── CONFIGURATION.md          # Guia de configuração
│   ├── USAGE.md                  # Guia de uso
│   ├── ARCHITECTURE.md           # Este arquivo
│   └── TROUBLESHOOTING.md        # Resolução de problemas
├── scripts/                      # Scripts auxiliares
│   ├── install.sh                # Instalação automatizada
│   ├── backup.sh                 # Backup de dados
│   └── maintenance.sh            # Manutenção
├── requirements.txt              # Dependências Python
├── alembic.ini                   # Configuração migrations
├── .env.example                  # Template configuração
└── README.md                     # Documentação principal
```

## 🔧 Componentes Principais v2.0

### 1. **Application Core (app/main.py)**

```python
# Responsabilidades:
- Inicialização da aplicação PostgreSQL
- Configuração de pools de conexão
- Sistema de migrations automático
- Coordenação de serviços assíncronos
- Gestão de recursos e cleanup
```

**Características:**
- Pool de conexões PostgreSQL otimizado
- Migrations automáticas na inicialização
- Logging estruturado com correlação IDs
- Graceful shutdown com cleanup
- Health checks internos

### 2. **API Layer (app/api/)**

```python
# Estrutura modular:
- endpoints/asns.py      # CRUD ASNs + batch operations
- endpoints/data.py      # Dados históricos + estatísticas
- endpoints/anomalies.py # Detecção + listagem anomalias
- endpoints/telegram.py  # Configuração + teste alertas
- endpoints/admin.py     # Administração + logs + backup
```

**Características:**
- FastAPI com autenticação opcional
- Documentação OpenAPI automática
- Validação avançada com Pydantic v2
- Rate limiting por endpoint
- Logs de auditoria para operações críticas

### 3. **Scheduler v2.0 (app/scheduler.py)**

```python
# Tarefas otimizadas:
- Coleta BGP inteligente (15 min, batches de 3-5 ASNs)
- Rate limiting adaptativo (45s entre coletas)
- Detecção de anomalias em tempo real
- Limpeza automática de dados antigos (diária)
- Relatórios estatísticos (semanais)
- Health checks com alertas (1 min)
```

**Características:**
- Algoritmo de batching inteligente
- Recovery automático de falhas
- Métricas de performance detalhadas
- Queue de prioridades para ASNs críticos
- Checkpoint e resumo de operações

### 4. **Database Layer (app/database/)**

```python
# Arquitetura de dados:
- connection.py     # Pool assíncrono PostgreSQL
- repositories/     # Padrão Repository para abstração
- migrations/       # Versionamento de schema
```

**Características:**
- Async pool otimizado (min=5, max=20 conexões)
- Índices otimizados para consultas temporais
- Particionamento automático por tempo
- Retenção de dados configurável (365 dias)
- Backup automático via pg_dump

### 5. **Intelligence Engine (app/services/anomaly_service.py)**

```python
# Configurações suportadas:
- Variáveis de ambiente (.env)
- Defaults seguros
- Validação de tipos
- Configuração de logging
```

# Algoritmos de detecção:
- Z-score para identificação de outliers
- Baseline dinâmico baseado em janela móvel
- Correlação temporal entre métricas
- Machine learning para padrões complexos
```

**Características:**
- Análise estatística avançada com Z-score ≥ 2.5
- Baseline calculado com mínimo 7 dias de dados
- Detecção de tipos específicos: sudden_increase, sudden_decrease, routing_instability
- Severidades automáticas: critical, warning, info
- Correlação entre ASNs para detecção de eventos globais

### 6. **Rate Limiting Engine (app/utils/rate_limiter.py)**

```python
# Sistema inteligente:
- 45 segundos entre coletas de ASNs individuais
- Batches de 3-5 ASNs para otimização
- Detecção automática de rate limiting da API
- Backoff exponencial em caso de erro 429
- Queue de prioridades para ASNs críticos
```

**Características:**
- Algoritmo adaptativo baseado em response headers
- Balanceamento de carga entre endpoints RIPE
- Recuperação automática de failures temporários
- Métricas de utilização de rate limits

## 🔍 Serviços de Negócio v2.0

### 1. **BGP Service (app/services/bgp_service.py)**

```python
class BGPCollectionService:
    # Responsabilidades:
    - Coleta multi-ASN com batching inteligente
    - Cache de dados para otimização de consultas
    - Correlação temporal entre snapshots
    - Detecção de mudanças significativas
    - Persistência otimizada no PostgreSQL
```

**Fluxo de Operação v2.0:**
1. **Seleção Inteligente**: Priorizar ASNs por criticidade e tempo desde última coleta
2. **Batching Otimizado**: Agrupar 3-5 ASNs respeitando rate limits
3. **Coleta Paralela**: Executar consultas RIPE de forma assíncrona
4. **Análise em Tempo Real**: Detectar anomalias durante a coleta
5. **Persistência Eficiente**: Bulk insert no PostgreSQL com transações
6. **Alertas Imediatos**: Disparar notificações para anomalias críticas

### 2. **Anomaly Detection Service (app/services/anomaly_service.py)**

```python
class AnomalyDetectionService:
    # Algoritmos implementados:
    - Z-score analysis para mudanças estatísticas
    - Seasonal decomposition para padrões temporais
    - Correlation analysis entre ASNs relacionados
    - Pattern matching para eventos conhecidos
    - Machine learning para detecção avançada
```

**Tipos de Anomalias Detectadas:**
- **sudden_increase**: Aumento súbito > 2.5σ em prefixes/peers
- **sudden_decrease**: Diminuição súbita > 2.5σ em prefixes/peers  
- **routing_instability**: Variação alta em curto período
- **missing_prefixes**: Prefixos esperados não anunciados
- **bgp_leak**: Anúncios suspeitos de prefixos de terceiros
- **peer_loss**: Perda significativa de relacionamentos BGP

### 3. **Alert Service (app/services/alert_service.py)**

```python
class AlertService:
    # Funcionalidades avançadas:
    - Queue de alertas com priorização
    - Aggregation de alertas similares
    - Rate limiting para evitar spam
    - Templates contextuais em português
    - Escalation automática por severidade
```

**Severidades e Ações:**
- **🚨 CRITICAL**: Notificação imediata + escalation
- **⚠️ WARNING**: Notificação agrupada (max 5 min)
- **ℹ️ INFO**: Incluído em relatório diário

### 4. **Telegram Service (app/services/telegram_service.py)**

```python
class TelegramService:
    # Features empresariais:
    - Bot dedicado com webhooks
    - Formatação rica com Markdown
    - Buttons interativos para ações
    - Queue resiliente com retry
    - Métricas de entrega detalhadas
```

**Recursos Avançados:**
- Templates contextuais para cada tipo de anomalia
- Botões inline para ações rápidas (acknowlege, escalate)
- Relatórios automáticos diários/semanais
- Comandos administrativos via chat
- Suporte a múltiplos canais por severidade

## 💾 Camada de Dados PostgreSQL

### **Esquema Principal**

```sql
-- Tabela de ASNs monitorados
CREATE TABLE asns (
    asn INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Snapshots de dados BGP (particionada por tempo)
CREATE TABLE bgp_data (
    id BIGSERIAL PRIMARY KEY,
    asn INTEGER REFERENCES asns(asn),
    timestamp TIMESTAMP NOT NULL,
    prefixes_ipv4 INTEGER,
    prefixes_ipv6 INTEGER,
    peers INTEGER,
    countries INTEGER,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (timestamp);

-- Anomalias detectadas
CREATE TABLE anomalies (
    id BIGSERIAL PRIMARY KEY,
    asn INTEGER REFERENCES asns(asn),
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    detected_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP NULL,
    z_score DECIMAL(5,2),
    baseline_value DECIMAL(12,2),
    actual_value DECIMAL(12,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Logs de coleta para auditoria
CREATE TABLE collection_logs (
    id BIGSERIAL PRIMARY KEY,
    collection_id UUID UNIQUE,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    asns_processed INTEGER,
    success_count INTEGER,
    error_count INTEGER,
    duration_seconds DECIMAL(8,2),
    metadata JSONB
);
```

### **Particionamento e Índices**

```sql
-- Partições automáticas por mês
CREATE TABLE bgp_data_y2025m01 PARTITION OF bgp_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Índices otimizados para consultas temporais
CREATE INDEX idx_bgp_data_asn_timestamp ON bgp_data (asn, timestamp DESC);
CREATE INDEX idx_anomalies_asn_detected ON anomalies (asn, detected_at DESC);
CREATE INDEX idx_anomalies_type_severity ON anomalies (type, severity, detected_at);

-- Índices para agregações estatísticas
CREATE INDEX idx_bgp_data_metrics ON bgp_data (asn, timestamp) 
    INCLUDE (prefixes_ipv4, prefixes_ipv6, peers);
```

### **Retenção e Manutenção**

```python
# Política de retenção automática:
- BGP Data: 365 dias (configurável)
- Anomalias: 730 dias (histórico longo)
- Collection Logs: 90 dias
- Limpeza automática diária via cron job
```

## ⚡ Performance e Escalabilidade

### **Otimizações de Performance**

1. **Pool de Conexões Assíncrono**:
   - Min: 5 conexões, Max: 20 conexões
   - Connection recycling: 3600s
   - Query timeout: 30s

2. **Cache Inteligente**:
   - Redis opcional para ASNs ativos
   - Cache em memória para baselines
   - TTL baseado em frequência de mudança

3. **Batching de Operações**:
   - Bulk inserts para dados BGP (batches de 100)
   - Prepared statements para queries repetitivas
   - Transações otimizadas por collection cycle

### **Escalabilidade Horizontal**

```python
# Preparado para crescimento:
- Múltiplas instâncias com shared PostgreSQL
- Load balancer para API endpoints
- Queue externa (Redis/RabbitMQ) para alertas
- Clustering PostgreSQL para alta disponibilidade
```

## 📊 Monitoramento e Observabilidade

### **Métricas Coletadas**

```python
# Sistema de métricas completo:
- collection_duration_seconds: Tempo de coleta por ASN
- api_requests_total: Contador de requests RIPE
- anomalies_detected_total: Anomalias por tipo e severidade
- telegram_messages_sent: Mensagens enviadas com sucesso
- database_connections_active: Conexões PostgreSQL ativas
- memory_usage_bytes: Uso de memória da aplicação
```

### **Estrutura de Logs**

```json
{
  "timestamp": "2025-05-28T10:00:00.123Z",
  "level": "INFO",
  "component": "bgp_service",
  "correlation_id": "abc123",
  "asn": 64512,
  "operation": "collect_data",
  "duration_ms": 1250,
  "metadata": {
    "prefixes_collected": 1250,
    "anomalies_detected": 1,
    "api_response_time": 156.3
  }
}
```

### **Health Checks**

```python
# Multi-layer health checks:
- /health: Basic application status
- /health/detailed: Database + external APIs
- /health/ready: Readiness for traffic
- Internal monitoring: Connection pools, queue sizes
```

## 🔄 Deployment e Infraestrutura

### **Deployment via Systemd**

```ini
# /etc/systemd/system/bgp-monitor.service
[Unit]
Description=BGP Monitor v2.0
After=postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=bgp-monitor
WorkingDirectory=/opt/bgp-monitor
ExecStart=/opt/bgp-monitor/venv/bin/python app/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### **Container-Ready**

```dockerfile
# Dockerfile para produção
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY app/ /app/
WORKDIR /app

# Configure runtime
EXPOSE 8000
CMD ["python", "main.py"]
```

### **Backup e Recuperação**

```bash
# Backup automático PostgreSQL
pg_dump -h localhost -U bgp_monitor bgp_monitor \
  --format=custom \
  --compress=9 \
  --file=/backup/bgp_monitor_$(date +%Y%m%d_%H%M%S).backup

# Backup configuração
cp /opt/bgp-monitor/.env /backup/config_$(date +%Y%m%d).env
```

## 🎯 Casos de Uso Avançados

### **Detecção de BGP Hijacking**

```python
# Algoritmo de detecção:
1. Monitorar prefixos conhecidos por ASN
2. Detectar anúncios inesperados por ASNs não-proprietários  
3. Validar contra IRR databases (RADB, RIPE, etc.)
4. Correlacionar com feeds de threat intelligence
5. Alertar com contexto geográfico e reputação do ASN
```

### **Análise de Tendências**

```python
# Machine learning para padrões:
1. Seasonal decomposition de métricas BGP
2. Clustering de comportamentos similares entre ASNs
3. Predição de anomalias baseada em histórico
4. Correlação entre eventos BGP e incidentes de rede
5. Alertas preditivos para manutenções programadas
```

### **Multi-Tenant Management**

```python
# Preparado para múltiplos clientes:
1. Isolamento de dados por organização
2. RBAC (Role-Based Access Control)
3. Rate limiting por tenant
4. Dashboards personalizados
5. APIs dedicadas por cliente
```

---

## 🔗 Próximos Passos

### **Roadmap v2.1**
- [ ] Integração com OpenTelemetry
- [ ] Dashboard web interativo  
- [ ] API GraphQL para consultas complexas
- [ ] Machine learning para detecção avançada
- [ ] Suporte a IPv6 nativo

### **Roadmap v3.0**
- [ ] Microserviços com event sourcing
- [ ] Streaming real-time com Apache Kafka
- [ ] Multi-cloud deployment
- [ ] AI-powered incident response
- [ ] Blockchain para auditoria imutável

---

**BGP Monitor v2.0** - Arquitetura robusta para monitoramento BGP empresarial com PostgreSQL e inteligência artificial.
class IRRValidator:
    # Funcionalidades:
    - Valida consistência com bancos IRR
    - Consulta múltiplos bancos (RADB, ARIN, etc.)
    - Cache de validações recentes
    - Detecta inconsistências
    - Alertas para objetos inválidos
```

**Fluxo de Operação:**
1. Obter objetos IRR registrados para ASN
2. Comparar com prefixos realmente anunciados
3. Identificar inconsistências ou ausências
4. Validar policies e route objects
5. Cache resultados para otimização
6. Alertar sobre problemas encontrados

## 🌐 Integrações Externas

### 1. **RIPE API Client (ripe_api.py)**

```python
# Endpoints utilizados:
- announced-prefixes    # Prefixos anunciados por ASN
- bgp-updates          # Mudanças recentes no BGP
- as-overview          # Visão geral do ASN
- looking-glass        # Informações de roteamento
```

**Características:**
- Cliente HTTP assíncrono (httpx)
- Retry automático para falhas temporárias
- Cache inteligente para reduzir requests
- Rate limiting respeitoso
- Parsing robusto de responses

### 2. **Telegram Integration (telegram.py)**

```python
# Funcionalidades:
- Envio de mensagens formatadas
- Suporte a HTML/Markdown
- Diferentes tipos de alerta
- Rate limiting interno
- Fallback para falhas
```

**Tipos de Mensagem:**
- 🚨 Alertas críticos (prefix missing)
- ⚠️ Avisos (peer loss)
- ℹ️ Informações (relatórios)
- ✅ Confirmações (recovery)

## 📊 Sistema de Métricas

### 1. **Metrics Collection (utils/metrics.py)**

```python
class SimpleMetrics:
    # Métricas coletadas:
    - Uptime do sistema
    - Contadores de alertas por tipo
    - Saúde dos componentes
    - Tempos de execução de checks
    - Estatísticas de performance
```

**Características:**
- Armazenamento em memória
- Agregação automática
- Reset periódico para evitar overflow
- Export em múltiplos formatos
- Thread-safe operations

### 2. **Health Monitoring**

```python
# Indicadores de saúde:
- Component status (healthy/unhealthy)
- Last successful check timestamp
- Error rates and patterns
- Resource utilization
- External service availability
```

## 🔄 Fluxo de Dados

### 1. **Inicialização**

```
1. Carregar configurações (.env)
2. Inicializar logging estruturado
3. Configurar cliente HTTP
4. Inicializar componentes de monitoramento
5. Registrar handlers de sinal
6. Iniciar API FastAPI
7. Iniciar scheduler de tarefas
```

### 2. **Ciclo de Monitoramento**

```
1. Scheduler dispara verificação
2. Serviço coleta dados via API externa
3. Comparação com estado anterior (cache)
4. Detecção de anomalias/problemas
5. Geração de alertas se necessário
6. Envio de notificações (Telegram)
7. Atualização de métricas e logs
8. Persistência de estado em memória
```

### 3. **Tratamento de Alertas**

```
1. Evento detectado por monitor
2. Verificação de rate limiting (evitar spam)
3. Formatação da mensagem de alerta
4. Tentativa de envio via Telegram
5. Retry em caso de falha
6. Log do resultado da operação
7. Atualização de métricas de alertas
```

## 🛡️ Resiliência e Confiabilidade

### 1. **Error Handling**

- **Graceful degradation**: Sistema continua funcionando mesmo com falhas parciais
- **Circuit breaker**: Proteção contra falhas em cascata
- **Exponential backoff**: Retry inteligente para APIs externas
- **Timeout configurável**: Evita travamentos

### 2. **Recovery Mechanisms**

- **Auto-restart**: Componentes se recuperam automaticamente
- **Health checks**: Detecção proativa de problemas
- **Fallback modes**: Operação limitada quando serviços estão indisponíveis
- **State preservation**: Manutenção de dados críticos em memória

### 3. **Monitoring & Observability**

- **Structured logging**: Logs em formato JSON para análise
- **Metrics collection**: Métricas detalhadas de performance
- **Health endpoints**: APIs para verificação externa
- **Debug modes**: Logging detalhado para troubleshooting

## 🚀 Performance e Escalabilidade

### 1. **Performance Optimizations**

- **Async I/O**: Operações não-bloqueantes
- **Connection pooling**: Reutilização de conexões HTTP
- **Intelligent caching**: Cache de dados frequentemente acessados
- **Batch operations**: Agrupamento de operações similares

### 2. **Memory Management**

- **Limited cache size**: Prevenção de memory leaks
- **Periodic cleanup**: Limpeza automática de dados antigos
- **Efficient data structures**: Uso otimizado de memória
- **GC-friendly design**: Estruturas compatíveis com garbage collector

### 3. **Resource Utilization**

- **CPU-bound tasks**: Otimização para operações de processamento
- **I/O-bound tasks**: Assíncrono para operações de rede
- **Memory footprint**: Mínimo uso de memória
- **Network efficiency**: Requests otimizados

## 🔮 Extensibilidade

### 1. **Plugin Architecture** (Futuro)

```python
# Interface para novos monitores:
class BaseMonitor:
    async def check(self) -> List[Alert]
    def get_metrics(self) -> Dict
    def get_health(self) -> HealthStatus
```

### 2. **Configuration Extensions**

- **Custom intervals**: Intervalos personalizáveis por monitor
- **Threshold tuning**: Limites ajustáveis para alertas
- **Output formats**: Múltiplos formatos de export
- **Integration hooks**: Webhooks para sistemas externos

### 3. **API Extensions**

- **Custom endpoints**: Adição de novos endpoints
- **Authentication**: Suporte a autenticação/autorização
- **Rate limiting**: Controle de taxa por endpoint
- **Versioning**: Suporte a múltiplas versões da API

## 📚 Próximos Passos

Para entender melhor a implementação:

1. [🔧 Guia de Uso](USAGE.md)
2. [🌐 Referência da API](API.md)
3. [🔍 Troubleshooting](TROUBLESHOOTING.md)
4. [🤝 Como Contribuir](../CONTRIBUTING.md)
