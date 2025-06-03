# Changelog - BGP Monitor

## [1.2.0] - 2025-06-01

### 🟢 Sistema de Alarmes de Recuperação
- **NOVO**: Sistema completo de notificações de recuperação em português brasileiro
- **6 tipos de recuperação**: peer_recovered, upstreams_normalized, prefix_restored, latency_normalized, instability_resolved, anomaly_resolved
- **Detecção automática**: Identificação em tempo real quando problemas são resolvidos
- **Cálculo de downtime**: Tempo automático de inatividade/problema calculado para cada recuperação

### 📱 Aprimoramentos do Telegram
- **Templates PT-BR**: Mensagens profissionais em português brasileiro para todos os tipos
- **Emojis específicos**: 🟢, ✅, 🔄, ⚡, 📊, 📉 para diferentes tipos de recuperação  
- **Formatação BRT**: Horários automaticamente formatados para fuso brasileiro
- **Método send_recovery_alert()**: Nova função dedicada para alertas de recuperação

### 🔧 Serviços Aprimorados
- **Peer Monitor**: Detecção de recuperação de peers perdidos e normalização de latência
- **Prefix Monitor**: Detecção de restauração de prefixos ausentes
- **Anomaly Detector**: Detecção de resolução de anomalias estatísticas e instabilidades
- **Cache inteligente**: Sistema de cache para detectar transições problema → recuperação

### 🔌 API Estendida
- **8 novos endpoints**: Testes individuais e coletivos de recuperação
- **Endpoints informativos**: `/alerts/types` e `/alerts/recovery/examples`
- **Teste completo**: `/test/recovery/all` para validar todos os tipos

### 🧪 Scripts de Teste
- **teste_endpoints_recuperacao.sh**: Validação completa de API
- **teste_deteccao_recuperacao.sh**: Teste de lógica automática
- **teste_alarmes_recuperacao_pt_br.sh**: Simulação de mensagens

### 📚 Documentação
- **RESUMO_RECUPERACAO_PT_BR.md**: Documentação técnica completa
- **ALARMES_PT_BR_TELEGRAM.md**: Exemplos práticos atualizados
- **RELEASE-NOTES-v1.2.0.md**: Release notes detalhadas

### ✅ Compatibilidade
- **Zero breaking changes**: Totalmente compatível com v1.0.1
- **Funcionalidades mantidas**: Todos os recursos anteriores preservados
- **Configuração inalterada**: Mesmo arquivo .env e configurações

---

## [1.0.1] - 2025-01-12

### 🔧 Melhorias e Novas Funcionalidades
- **Monitoramento de Peers ASN-específico**: Nova funcionalidade para análise detalhada de peers BGP para ASNs específicos
- **Novo endpoint API**: `/monitoring/peers/{asn}` - Endpoint REST para consulta de peers de ASN específico
- **Análise aprimorada de peers**: Categorização de peers (upstreams, customers, peers) com validação de saúde da rede
- **Detecção de diversidade de upstreams**: Validação automática da redundância de conexões BGP

### 📈 Validação Completa
- **Testes realizados**: Validação com múltiplos ASNs (AS267357, AS262993, AS53013, AS61922)
- **Taxa de sucesso**: 100% nos testes de integração
- **Exemplo AS267357**: 5 peers detectados (3 upstreams, 1 peer, 1 customer) com status HEALTHY

### 🔄 Otimizações
- **Código limpo**: Remoção de arquivos desnecessários e cache
- **Pacote otimizado**: Redução significativa do tamanho do package
- **Documentação atualizada**: README.md e documentação técnica atualizados

### 📦 Entrega
- **Package ZIP**: bgp-monitor-v1.0.1.zip pronto para distribuição
- **Compatibilidade mantida**: Totalmente compatível com versão 1.0.0

---

## [1.0.0] - 2025-01-12

### 🚀 Release Inicial
Esta é a primeira versão estável do BGP Monitor, um sistema completo de monitoramento BGP com API REST, dashboard web e coleta automatizada de dados.

### 🎯 Funcionalidades Principais
- **Monitoramento BGP completo**: Coleta automatizada de informações de ASNs via RIPEstat API
- **API REST robusta**: Interface completa para gerenciar ASNs e consultar dados históricos
- **Dashboard interativo**: Interface web para visualização de dados e estatísticas
- **Banco de dados PostgreSQL**: Armazenamento persistente com suporte a consultas complexas
- **Cache Redis**: Sistema de cache para otimização de performance
- **Coleta agendada**: Scheduler automático para coleta periódica de dados
- **Serviço systemd**: Execução como serviço do sistema operacional

### 🔧 Componentes Técnicos
- **FastAPI**: Framework web moderno para API REST
- **SQLAlchemy**: ORM para gerenciamento de banco de dados
- **Alembic**: Sistema de migrações de banco de dados
- **APScheduler**: Agendador de tarefas para coleta automática
- **Redis**: Sistema de cache distribuído
- **PostgreSQL**: Banco de dados relacional principal

### 📦 Scripts de Instalação
- **install.sh**: Script de instalação unificado com validações automáticas
- **Configuração .env**: Arquivo de exemplo com todas as variáveis documentadas
- **Serviço systemd**: Configuração automática para execução como serviço
- **Ambiente virtual**: Isolamento de dependências Python

### 🌐 API Endpoints
- `/api/v1/bgp/asns` - Gerenciamento de ASNs
- `/api/v1/bgp/overview` - Dashboard principal
- `/api/v1/bgp/collect/force` - Coleta forçada de dados
- `/api/v1/metrics` - Métricas do sistema
- `/health` - Status de saúde da aplicação

### 🔍 Recursos de Monitoramento
- **Coleta automática**: Dados atualizados periodicamente
- **Histórico completo**: Armazenamento de dados históricos para análise
- **Detecção de anomalias**: Identificação de mudanças significativas
- **Alertas configuráveis**: Sistema de notificações personalizáveis
- **Métricas detalhadas**: Estatísticas completas de performance

### 👨‍💻 Informações Técnicas
- **Autor**: netovaat
- **Versão**: 1.0.0
- **Compatibilidade**: Ubuntu 20.04+, Debian 10+
- **Python**: 3.8+
- **Licença**: MIT
- **Validação**: Sistema de testes completo funcionando

## [2.1.0] - 2024-12-29

### 🚀 Novidades
- **Sistema de imports corrigido**: Todos os módulos agora importam corretamente sem erros
- **Documentação de instalação completa**: Arquivo `docs/INSTALLATION.md` completamente reescrito com 450+ linhas
- **Scripts de instalação aprimorados**: Scripts `install.sh` e `aplicar-correções.sh` melhorados
- **Sistema de testes implementado**: Script `test_system_final.py` para validação completa do sistema

### 🔧 Correções
- **Imports de módulos**: Corrigido problema com `BGPScheduler` importação
- **Ambiente virtual**: Criação e configuração automática do venv
- **Dependências**: Validação e instalação automática de todas as dependências
- **Migrations**: Sistema de migrations Alembic funcionando corretamente
- **Database**: Conectividade PostgreSQL validada e otimizada

### 📚 Documentação
- **INSTALLATION.md**: Guia completo com instalação rápida, manual detalhada e troubleshooting
- **Scripts de correção**: Documentação de problemas conhecidos e soluções
- **Configurações de performance**: Guias para ambiente de produção
- **Monitoramento pós-instalação**: Logs, métricas e verificações

### ⚡ Melhorias de Performance
- **Ambiente virtual otimizado**: Instalação correta de todas as dependências
- **Sistema de cache limpo**: Remoção automática de arquivos `__pycache__` e `.pyc`
- **Configurações PostgreSQL**: Otimizações para produção documentadas

### 🧪 Sistema de Testes
- **Testes de imports**: Validação de todos os módulos Python
- **Testes de conectividade**: Verificação de banco de dados e APIs
- **Testes funcionais**: Validação de endpoints e funcionalidades core
- **Testes de instalação**: Scripts para verificar instalação completa

### 📦 Dependências Atualizadas
- Validação de `requirements.txt` completa
- Instalação correta de `psycopg2-binary`, `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`
- Configuração correta do ambiente virtual Python 3.11+

### 🐛 Bugs Corrigidos
- Correção de imports circulares entre módulos
- Correção de alias em `app/services/scheduler.py`
- Correção de paths em imports relativos
- Correção de dependências faltantes no ambiente virtual

---

## [2.0.0] - 2024-12-28

### 🚀 Primeira versão com PostgreSQL
- Migração completa de SQLite para PostgreSQL
- Sistema de migrations com Alembic
- APIs REST com FastAPI
- Monitoramento histórico de ASNs
- Sistema de alertas via Telegram
- Detecção de anomalias em tempo real

### 📊 Funcionalidades Core
- Coleta automática de dados BGP via RIPE Stat API
- Armazenamento de snapshots históricos
- Monitoramento de prefixes e peers
- Sistema de alertas configurável
- APIs para consulta de dados históricos

### 🔧 Arquitetura
- FastAPI para APIs REST
- PostgreSQL para persistência
- SQLAlchemy ORM com suporte async
- Alembic para migrations
- Scheduler para coletas automáticas
- Sistema modular e extensível

---

## Formato do Changelog

Este arquivo segue o formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

### Tipos de mudanças
- **🚀 Novidades** - para novas funcionalidades
- **🔧 Correções** - para correções de bugs
- **📚 Documentação** - para mudanças na documentação
- **⚡ Melhorias** - para melhorias de performance
- **🧪 Testes** - para adição ou correção de testes
- **📦 Dependências** - para mudanças em dependências
- **🐛 Bugs** - para listagem de bugs corrigidos
