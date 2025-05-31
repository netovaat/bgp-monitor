# Changelog - BGP Monitor

## [2.2.0] - 2025-01-12

### 🚀 Novidades
- **Script de instalação unificado**: Novo `install.sh` único que substitui todos os scripts anteriores
- **Documentação de configuração completa**: Arquivo `.env.example` totalmente documentado com 25+ variáveis
- **Processo de instalação robusto**: Validações automáticas, logs coloridos e recuperação de erros
- **Limpeza estrutural**: Remoção de 10+ arquivos obsoletos e otimização da estrutura do projeto

### 🔧 Melhorias
- **Script install.sh único**: Processo simplificado com validação completa de sistema e dependências
- **Documentação .env.example**: Todas as flags de configuração documentadas com comentários explicativos
- **Logs de instalação**: Sistema de logging colorido e informativo durante o processo
- **Validações robustas**: Testes automáticos de conectividade PostgreSQL, Redis e APIs
- **Recuperação de erros**: Sistema inteligente de detecção e correção de problemas

### 📦 Otimizações
- **Código limpo**: Remoção de scripts obsoletos (aplicar-correções.sh, fix-*.sh, install-v2.1.*.sh)
- **Documentação atualizada**: README.md e docs/ atualizados para v2.2.0
- **Estrutura organizada**: Projeto mais limpo e fácil de manter
- **Performance**: Otimizações no processo de instalação e configuração

### 🗑️ Arquivos Removidos
- Scripts obsoletos: `aplicar-correções.sh`, `create-package-v2.1.0*.sh`, `fix-*.sh`, `install-v2.1.*.sh`
- Documentação desatualizada: `CORREÇÕES-INSTALAÇÃO.md`, `README_v2.md`, `RELEASE-NOTES-v2.0.md`
- Arquivos temporários: logs, cache Python, arquivos PID

### 👨‍💻 Técnico
- **Autor atualizado**: Metadados atualizados para `netovaat`
- **Versão consolidada**: Todas as funcionalidades da v2.1.1 mantidas
- **Ambiente virtual**: Configuração otimizada e validada
- **Compatibilidade**: Totalmente compatível com configurações existentes

## [2.1.1] - 2025-05-30

### 🚀 Novidades
- **Serviço systemd funcionando**: BGP Monitor agora roda como serviço do sistema
- **Scripts bgp-monitor.sh aprimorados**: Ativação automática do ambiente virtual
- **Persistência garantida**: Aplicação continua rodando após fechar terminal
- **Pacote final otimizado**: Distribuição pronta para produção

### 🔧 Correções
- **Script bgp-monitor.sh**: Agora ativa o ambiente virtual automaticamente
- **Dependências completas**: Todas as dependências Python instaladas corretamente
- **Serviço systemd**: Configuração e inicialização automática funcionando
- **Ambiente virtual**: Instalação e ativação correta das dependências

### 📦 Melhorias
- **Distribuição**: Pacote final limpo e otimizado para distribuição
- **Instalação**: Processo de instalação mais robusto e confiável
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
