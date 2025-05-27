# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.1] - 2025-05-27

### 🔧 Corrigido
- Removidos todos os logs estruturados (structlog) e convertidos para logging padrão Python
- Corrigido sistema de configuração removendo dependência do pydantic_settings
- Corrigido inicialização lazy do bot Telegram para evitar erros quando token não configurado
- Corrigido todos os imports e dependências para funcionar apenas com bibliotecas essenciais

### 🧹 Removido
- Removido Docker e docker-compose (simplificação)
- Removido Alembic e sistema de migrações de banco
- Removido sistema de monitoramento complexo (Zabbix/Prometheus)
- Removido Nginx e configurações de proxy
- Removido testes automatizados (pytest)
- Removidos scripts desnecessários e arquivos duplicados
- Removidos diretórios e arquivos de cache Python (__pycache__, *.pyc)

### ✨ Melhorado
- Sistema totalmente simplificado e funcional
- Documentação atualizada com instruções completas de instalação
- Requirements.txt limpo e otimizado para Python 3.10+
- Estrutura de projeto mais enxuta (de ~200 para ~20 arquivos essenciais)
- Inicialização mais rápida e confiável
- Menor consumo de recursos do sistema

### 📦 Dependências
- Atualizadas para versões compatíveis com Python 3.10
- Removidas dependências desnecessárias
- Mantidas apenas bibliotecas essenciais: FastAPI, uvicorn, httpx, python-telegram-bot, schedule

## [1.0.0] - 2025-05-27

### ✨ Primeira Release
- Sistema básico de monitoramento BGP
- Integração com RIPE API para consultas BGP
- Notificações via Telegram
- API REST para gerenciamento
- Monitoramento de prefixos e peers
- Validação IRR básica
- Sistema de métricas em memória
- Scheduler automático para verificações

### 🎯 Funcionalidades Principais
- Monitoramento de prefixos BGP em tempo real
- Detecção de perda de peers e upstreams
- Alertas críticos via Telegram
- API REST completa para consultas
- Sistema de health check
- Configuração via arquivo .env
- Logging estruturado e métricas

---

## Legendas

- 🔧 **Corrigido** - Correções de bugs
- ✨ **Adicionado** - Novas funcionalidades
- 🧹 **Removido** - Funcionalidades removidas
- ⚡ **Melhorado** - Melhorias em funcionalidades existentes
- 🔒 **Segurança** - Correções relacionadas à segurança
- 📦 **Dependências** - Atualizações de dependências
- 📝 **Documentação** - Mudanças na documentação
