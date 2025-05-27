# 📦 Guia de Instalação

Este guia detalha todos os métodos de instalação do BGP Monitor v1.0.

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux** (Ubuntu 18.04+, CentOS 7+, Debian 9+)
- **macOS** 10.14+
- **Windows** 10+ (via WSL recomendado)

### Software
- **Python 3.8 ou superior**
- **pip** (gerenciador de pacotes Python)
- **git** (para clonagem do repositório)
- **curl** (para testes da API)

## 🚀 Instalação Automática (Recomendada)

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/bgp-monitor.git
cd bgp-monitor
```

### 2. Execute o Script de Instalação

```bash
# Torna o script executável
chmod +x install.sh

# Executa a instalação
./install.sh
```

O script irá:
- Verificar dependências
- Instalar pacotes Python
- Configurar ambiente
- Criar arquivos de configuração
- Testar a instalação

## 🔧 Instalação Manual

### 1. Verificar Python

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
import structlog
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
