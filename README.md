# BGP Monitor v1.0.1

Sistema simplificado de monitoramento BGP com notificações via Telegram.

## 🎯 Visão Geral

O BGP Monitor é uma ferramenta leve e autônoma para monitoramento de infraestrutura BGP, oferecendo:

- **Monitoramento de Prefixos BGP** - Verifica se seus prefixos estão sendo anunciados globalmente
- **Monitoramento de Peers** - Detecta perda de relacionamentos BGP e upstreams
- **Validação IRR** - Verifica consistência com bancos de dados IRR
- **Notificações Telegram** - Alertas em tempo real via bot do Telegram
- **API REST** - Interface completa para gerenciamento e consultas
- **Sistema de Métricas** - Monitoramento de saúde e estatísticas

## ⚡ Características

- ✅ **Zero dependências externas** - Sem Docker, bancos de dados ou Redis
- ✅ **Leve e rápido** - Armazenamento em memória
- ✅ **Fácil instalação** - Apenas Python 3.10+ e dependências Python
- ✅ **Configuração simples** - Arquivo .env único
- ✅ **Altamente confiável** - Menos componentes = menos falhas
- ✅ **Scheduler automático** - Verificações periódicas automáticas

## 📋 Requisitos

### Sistema Operacional
- Linux (Ubuntu 20.04+ recomendado)
- Python 3.10 ou superior
- Git para instalação
- Acesso à internet para consultas RIPE API

### Dependências Opcionais
- Bot do Telegram (recomendado para alertas)
- Curl (para testes da API)

## 🚀 Instalação Completa

### 1. Preparação do Sistema
```bash
# Atualizar sistema (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y python3 python3-pip python3-venv git build-essential curl

# Verificar versão do Python (deve ser 3.10+)
python3 --version
```

### 2. Instalação do BGP Monitor
```bash
# Clonar repositório
git clone https://github.com/seu-usuario/bgp-monitor.git
cd bgp-monitor

# Instalar dependências Python
pip3 install -r requirements.txt

# Configurar ambiente
cp .env.example .env
nano .env  # Editar configurações

# Tornar scripts executáveis
chmod +x run.sh bgp-monitor.sh
```

### 3. Configuração Básica
```bash
# Editar arquivo .env com suas configurações:
# TARGET_ASN=65001          # Seu ASN
# HOST=0.0.0.0             # IP da API
# PORT=8000                # Porta da API
# TELEGRAM_BOT_TOKEN=...   # Token do bot (opcional)
# TELEGRAM_CHAT_ID=...     # ID do chat (opcional)
```

### 4. Execução
```bash
# Executar em foreground (desenvolvimento)
./run.sh

# Ou executar em background (produção)
./bgp-monitor.sh start
```

## 📖 Documentação Completa

- [📦 Guia de Instalação](docs/INSTALLATION.md)
- [⚙️ Configuração](docs/CONFIGURATION.md)
- [🔧 Guia de Uso](docs/USAGE.md)
- [🌐 Referência da API](docs/API.md)
- [🏗️ Arquitetura](docs/ARCHITECTURE.md)
- [🔍 Troubleshooting](docs/TROUBLESHOOTING.md)

## 🎯 Uso Básico

```bash
# Verificar status do sistema
./bgp-monitor.sh status

# Adicionar prefixo para monitoramento
./bgp-monitor.sh add-prefix "203.0.113.0/24" "Rede principal"

# Listar prefixos monitorados
./bgp-monitor.sh list-prefixes

# Executar verificações manuais
./bgp-monitor.sh check

# Parar o sistema
./bgp-monitor.sh stop
```

## 📊 Status da API

Acesse `http://localhost:8000` para:
- Ver status geral do sistema
- Gerenciar prefixos monitorados
- Consultar métricas e alertas
- Executar verificações manuais

## 📱 Configuração do Telegram

1. Crie um bot no [@BotFather](https://t.me/BotFather)
2. Obtenha o token do bot
3. Obtenha seu Chat ID (use [@userinfobot](https://t.me/userinfobot))
4. Configure no arquivo `.env`

## 📈 Monitoramento

O sistema executa automaticamente:
- **Verificação de prefixos** - A cada 5 minutos
- **Verificação de peers** - A cada 10 minutos  
- **Validação IRR** - A cada 15 minutos
- **Health checks** - A cada 1 minuto
- **Relatórios diários** - Às 09:00 UTC

## 🤝 Contribuição

Contribuições são bem-vindas! Veja como:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- 📧 **Issues**: [GitHub Issues](https://github.com/seu-usuario/bgp-monitor/issues)
- 📖 **Documentação**: [docs/](docs/)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/bgp-monitor/discussions)

---

**BGP Monitor v1.0** - Sistema simplificado de monitoramento BGP
