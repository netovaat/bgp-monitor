# 📦 Guia de Instalação

Este guia detalha todos os métodos de instalação do BGP Monitor v1.0.1.

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux** (Ubuntu 20.04+, CentOS 8+, Debian 10+)
- **macOS** 11.0+
- **Windows** 10+ (via WSL2 recomendado)

### Software Obrigatório
- **Python 3.10 ou superior**
- **pip3** (gerenciador de pacotes Python)
- **git** (para clonagem do repositório)
- **build-essential** (compiladores para dependências)

### Software Opcional
- **curl** (para testes da API)
- **systemd** (para executar como serviço)

## 🚀 Instalação Completa (Recomendada)

### 1. Preparação do Sistema

#### Ubuntu/Debian:
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y python3 python3-pip python3-venv git build-essential curl wget

# Verificar versão do Python
python3 --version  # Deve ser 3.10+
```

#### CentOS/RHEL/Fedora:
```bash
# Atualizar sistema
sudo dnf update -y

# Instalar dependências
sudo dnf install -y python3 python3-pip git gcc gcc-c++ curl wget

# Verificar versão
python3 --version
```

### 2. Instalação do BGP Monitor

```bash
# Criar diretório (opcional)
sudo mkdir -p /opt/bgp-monitor
cd /opt/bgp-monitor

# Clonar repositório
git clone https://github.com/seu-usuario/bgp-monitor.git .

# Instalar dependências Python
pip3 install -r requirements.txt

# Verificar instalação das dependências
python3 -c "
import fastapi, uvicorn, httpx, telegram, schedule, pandas
print('✅ Todas as dependências instaladas com sucesso!')
"
```

### 3. Configuração Inicial

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações (usar seu editor preferido)
nano .env
# ou
vim .env

# Tornar scripts executáveis
chmod +x run.sh bgp-monitor.sh
```

### 4. Verificação da Instalação

```bash
# Testar importações
python3 -c "
from app.core.config import settings
from app.main import app
print('✅ BGP Monitor instalado corretamente!')
print(f'🎯 ASN configurado: {settings.target_asn}')
"
```

## 🔧 Instalação Manual Detalhada

### 1. Verificar Requisitos do Sistema

```bash
python3 --version
# Deve retornar Python 3.8.0 ou superior
```

Se não tiver Python 3.8+:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.8 python3-pip python3-venv
```

**CentOS/RHEL:**
```bash
sudo yum install python38 python38-pip
```

**macOS:**
```bash
brew install python@3.8
```

### 2. Clone e Entre no Diretório

```bash
git clone https://github.com/seu-usuario/bgp-monitor.git
cd bgp-monitor
```

### 3. Criar Ambiente Virtual (Recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env  # ou vim, gedit, etc.
```

### 6. Testar Instalação

```bash
# Teste básico de importação
python3 -c "import app.main; print('✅ Instalação OK')"

# Teste da API
./bgp-monitor.sh test
```

## 🐳 Instalação via Docker (Alternativa)

Se preferir usar Docker (não recomendado para este projeto):

```bash
# Build da imagem
docker build -t bgp-monitor .

# Executar container
docker run -d \
  --name bgp-monitor \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env \
  bgp-monitor
```

## 🔍 Verificação da Instalação

### 1. Verificar Dependências

```bash
# Testar importações principais
python3 -c "
import fastapi
import logging
import httpx
import pandas
print('✅ Todas as dependências OK')
"
```

### 2. Testar Serviços

```bash
# Executar testes unitários
python3 -m pytest tests/ -v

# Verificar configuração
./bgp-monitor.sh config
```

### 3. Iniciar Sistema

```bash
# Iniciar BGP Monitor
./run.sh

# Em outro terminal, testar API
curl http://localhost:8000/health
```

## 🛠️ Instalação em Produção

### 1. Usuário Dedicado

```bash
# Criar usuário para BGP Monitor
sudo useradd -r -s /bin/false bgpmonitor
sudo mkdir -p /opt/bgp-monitor
sudo chown bgpmonitor:bgpmonitor /opt/bgp-monitor
```

### 2. Instalação no Diretório Sistema

```bash
# Clonar para diretório de produção
sudo git clone https://github.com/seu-usuario/bgp-monitor.git /opt/bgp-monitor
sudo chown -R bgpmonitor:bgpmonitor /opt/bgp-monitor

# Instalar dependências como usuário dedicado
sudo -u bgpmonitor bash -c "
cd /opt/bgp-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
"
```

### 3. Serviço Systemd

```bash
# Criar arquivo de serviço
sudo tee /etc/systemd/system/bgp-monitor.service > /dev/null <<EOF
[Unit]
Description=BGP Monitor Service
After=network.target

[Service]
Type=simple
User=bgpmonitor
Group=bgpmonitor
WorkingDirectory=/opt/bgp-monitor
Environment=PATH=/opt/bgp-monitor/venv/bin
ExecStart=/opt/bgp-monitor/venv/bin/python -m app.main
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar serviço
sudo systemctl enable bgp-monitor
sudo systemctl start bgp-monitor
sudo systemctl status bgp-monitor
```

## 🔧 Configuração de Proxy Reverso

### Nginx

```nginx
server {
    listen 80;
    server_name bgp-monitor.exemplo.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache

```apache
<VirtualHost *:80>
    ServerName bgp-monitor.exemplo.com
    
    ProxyPreserveHost On
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
</VirtualHost>
```

## 🐛 Troubleshooting da Instalação

### Erro: "ModuleNotFoundError"

```bash
# Verificar se está no ambiente virtual
which python3
pip list

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro: "Permission denied"

```bash
# Verificar permissões
ls -la /opt/bgp-monitor

# Corrigir permissões
sudo chown -R $USER:$USER /opt/bgp-monitor
chmod +x run.sh bgp-monitor.sh
```

### Erro: "Port 8000 already in use"

```bash
# Verificar processo usando a porta
lsof -i :8000
# ou
ss -tlnp | grep 8000

# Parar processo ou alterar porta no .env
```

### Erro de Conectividade

```bash
# Testar acesso à RIPE API
curl -s "https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS64512"

# Verificar DNS
nslookup stat.ripe.net
```

## 📚 Próximos Passos

Após a instalação bem-sucedida:

1. [⚙️ Configure o sistema](CONFIGURATION.md)
2. [🔧 Aprenda a usar](USAGE.md)
3. [🏗️ Entenda a arquitetura](ARCHITECTURE.md)

## 💡 Dicas de Performance

- Use ambiente virtual para isolamento
- Configure logs em produção
- Monitor recursos do sistema
- Configure backup das configurações
- Use proxy reverso em produção
