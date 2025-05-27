# 🏗️ Arquitetura

Documentação detalhada da arquitetura do BGP Monitor v1.0.

## 🎯 Visão Geral

O BGP Monitor foi projetado com arquitetura **simplificada e modular**, priorizando:

- **Simplicidade**: Sem dependências externas complexas
- **Confiabilidade**: Menos componentes = menos falhas
- **Performance**: Operações em memória
- **Manutenibilidade**: Código limpo e bem estruturado

## 📋 Princípios de Design

### 1. **Single Process Architecture**
- Um único processo Python
- Sem microserviços complexos
- Comunicação interna via imports diretos

### 2. **In-Memory Storage**
- Dados temporários em memória
- Sem banco de dados persistente
- Cache inteligente para otimização

### 3. **Async-First**
- Operações assíncronas por padrão
- Non-blocking I/O para APIs externas
- Scheduler baseado em asyncio

### 4. **Fail-Fast & Resilient**
- Detecção rápida de problemas
- Recuperação automática de falhas
- Isolamento de componentes

## 🏛️ Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────┐
│                    BGP Monitor v1.0                     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │     API     │  │  Scheduler  │  │   Services  │    │
│  │   FastAPI   │  │   asyncio   │  │   Monitors  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│                   Core Components                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Config    │  │   Metrics   │  │    Utils    │    │
│  │  Settings   │  │  Tracking   │  │  Helpers    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│                 External Integrations                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  RIPE API   │  │  Telegram   │  │     IRR     │    │
│  │   Client    │  │     Bot     │  │  Databases  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 📁 Estrutura de Diretórios

```
bgp-monitor/
├── app/                          # Aplicação principal
│   ├── main.py                   # Ponto de entrada
│   ├── scheduler.py              # Agendador de tarefas
│   ├── api/                      # API REST
│   │   └── main.py               # Endpoints FastAPI
│   ├── core/                     # Componentes centrais
│   │   └── config.py             # Configurações
│   ├── services/                 # Serviços de monitoramento
│   │   ├── prefix_monitor.py     # Monitor de prefixos
│   │   ├── peer_monitor.py       # Monitor de peers
│   │   ├── irr_validator.py      # Validador IRR
│   │   ├── telegram.py           # Cliente Telegram
│   │   └── ripe_api.py           # Cliente RIPE
│   └── utils/                    # Utilitários
│       └── metrics.py            # Sistema de métricas
├── docs/                         # Documentação
├── run.sh                        # Script de execução
├── bgp-monitor.sh               # Script de gerenciamento
├── requirements.txt             # Dependências Python
├── .env                         # Configurações
└── README.md                    # Documentação principal
```

## 🔧 Componentes Principais

### 1. **Application Core (app/main.py)**

```python
# Responsabilidades:
- Inicialização da aplicação
- Configuração de eventos de lifecycle
- Gerenciamento de sinais do sistema
- Coordenação entre componentes
```

**Características:**
- Ponto de entrada único
- Configuração de logging estruturado
- Handlers para SIGINT/SIGTERM
- Integração FastAPI + Scheduler

### 2. **API Layer (app/api/main.py)**

```python
# Endpoints principais:
- GET /health           # Saúde do sistema
- GET /metrics          # Métricas detalhadas
- GET /prefixes         # Listar prefixos
- POST /prefixes        # Adicionar prefixo
- POST /monitoring/*    # Executar verificações
```

**Características:**
- FastAPI com documentação automática
- CORS configurado para desenvolvimento
- Validação de dados com Pydantic
- Responses estruturados em JSON

### 3. **Scheduler (app/scheduler.py)**

```python
# Tarefas agendadas:
- Verificação de prefixos (5 min)
- Verificação de peers (10 min)
- Validação IRR (15 min)
- Health checks (1 min)
- Relatórios diários (09:00 UTC)
```

**Características:**
- Baseado em asyncio
- Execução paralela de tarefas
- Recuperação automática de falhas
- Logging detalhado de execuções

### 4. **Configuration (app/core/config.py)**

```python
# Configurações suportadas:
- Variáveis de ambiente (.env)
- Defaults seguros
- Validação de tipos
- Configuração de logging
```

**Características:**
- Pydantic Settings para validação
- Carregamento automático do .env
- Configurações imutáveis em runtime
- Defaults para desenvolvimento

## 🔍 Serviços de Monitoramento

### 1. **Prefix Monitor (prefix_monitor.py)**

```python
class PrefixMonitor:
    # Funcionalidades:
    - Consulta RIPE API para prefixos anunciados
    - Compara com lista de prefixos monitorados
    - Detecta prefixos ausentes ou não anunciados
    - Cache de alertas para evitar spam
    - Métricas de performance
```

**Fluxo de Operação:**
1. Obter lista de prefixos monitorados (memória)
2. Consultar RIPE API para prefixos anunciados
3. Comparar listas e identificar discrepâncias
4. Gerar alertas para prefixos ausentes
5. Enviar notificações via Telegram
6. Atualizar métricas e logs

### 2. **Peer Monitor (peer_monitor.py)**

```python
class PeerMonitor:
    # Funcionalidades:
    - Monitora relacionamentos BGP
    - Detecta perda de peers e upstreams
    - Simula verificações de latência
    - Cache de peers conhecidos
    - Alertas para mudanças críticas
```

**Fluxo de Operação:**
1. Consultar peers atuais via RIPE API
2. Comparar com peers conhecidos anteriormente
3. Detectar peers perdidos ou novos
4. Verificar se upstreams estão ativos
5. Calcular métricas de latência
6. Gerar alertas conforme thresholds

### 3. **IRR Validator (irr_validator.py)**

```python
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
