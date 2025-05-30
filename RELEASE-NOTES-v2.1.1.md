# 🚀 BGP Monitor v2.1.1 - Release Notes

**Data de Lançamento**: 30 de Maio de 2025  
**Versão**: 2.1.1  
**Tipo**: Patch Release  

---

## 📋 **Resumo da Versão**

A versão 2.1.1 do BGP Monitor é uma versão de correção focada em **estabilidade do serviço** e **melhorias na distribuição**. Esta versão corrige problemas identificados na v2.1.0 relacionados à execução como serviço do sistema e garante que a aplicação funcione corretamente após a instalação.

---

## ✨ **Principais Melhorias**

### 🔧 **Correções Críticas**
- **Serviço systemd funcional**: BGP Monitor agora inicia corretamente como serviço do sistema
- **Scripts corrigidos**: `bgp-monitor.sh` agora ativa automaticamente o ambiente virtual
- **Dependências completas**: Todas as dependências Python são instaladas no ambiente virtual
- **Persistência garantida**: Aplicação continua rodando mesmo após fechar o terminal

### 📦 **Melhorias de Distribuição**
- **Pacote otimizado**: Remoção de cache e arquivos temporários
- **Instalação robusta**: Processo de instalação mais confiável
- **Validação completa**: Testes automatizados funcionando corretamente

---

## 🔄 **Mudanças Específicas**

### **Arquivos Modificados:**
- `app/__init__.py` - Versão atualizada para 2.1.1
- `app/main.py` - Log de startup atualizado
- `README.md` - Título atualizado para v2.1.1
- `CHANGELOG.md` - Adicionada seção v2.1.1
- `bgp-monitor.sh` - Correção na ativação do ambiente virtual

### **Correções de Scripts:**
```bash
# Antes (problema)
python -m app.main &

# Depois (corrigido)
source venv/bin/activate
python -m app.main &
```

### **Serviço systemd:**
- ✅ Inicialização automática funcionando
- ✅ Logs integrados com journald
- ✅ Reinicialização automática em caso de falha
- ✅ Gerenciamento via systemctl

---

## 🚀 **Como Usar Esta Versão**

### **Instalação Nova:**
```bash
# 1. Extrair pacote
tar -xzf bgp-monitor-v2.1.1.tar.gz
cd bgp-monitor-v2.1.1

# 2. Executar instalação
sudo ./install-v2.1.0-final.sh

# 3. Verificar funcionamento
sudo systemctl status bgp-monitor
curl http://localhost:8000/health
```

### **Atualização da v2.1.0:**
```bash
# 1. Parar serviço atual
sudo systemctl stop bgp-monitor

# 2. Fazer backup (opcional)
sudo cp -r /opt/bgp-monitor /opt/bgp-monitor-backup

# 3. Extrair nova versão
cd /opt && sudo tar -xzf bgp-monitor-v2.1.1.tar.gz
sudo chown -R bgpmonitor:bgpmonitor /opt/bgp-monitor

# 4. Reinstalar dependências
cd /opt/bgp-monitor
sudo -u bgpmonitor bash -c "source venv/bin/activate && pip install -r requirements.txt"

# 5. Reiniciar serviço
sudo systemctl start bgp-monitor
```

---

## ✅ **Validação da Instalação**

### **Verificar Serviço:**
```bash
# Status do serviço
sudo systemctl status bgp-monitor

# Logs do serviço
sudo journalctl -u bgp-monitor -f

# Testar API
curl http://localhost:8000/health
```

### **Comandos de Gerenciamento:**
```bash
# Parar/Iniciar
sudo systemctl stop bgp-monitor
sudo systemctl start bgp-monitor

# Reiniciar
sudo systemctl restart bgp-monitor

# Habilitar/Desabilitar inicialização automática
sudo systemctl enable bgp-monitor
sudo systemctl disable bgp-monitor
```

---

## 🔧 **Problemas Corrigidos**

| Problema | Descrição | Solução |
|----------|-----------|---------|
| **Script não funcionava** | `bgp-monitor.sh` não ativava o ambiente virtual | Adicionado `source venv/bin/activate` |
| **Dependências ausentes** | FastAPI não estava instalado no venv | Instalação completa de `requirements.txt` |
| **Serviço não persistia** | Aplicação parava ao fechar terminal | Configurado como serviço systemd |
| **Cache desnecessário** | Arquivos `__pycache__` no pacote | Limpeza automática antes do empacotamento |

---

## 📊 **Compatibilidade**

- **Sistema Operacional**: Ubuntu 20.04+ / Debian 10+
- **Python**: 3.8+ (recomendado 3.11+)
- **PostgreSQL**: 12+
- **Memória RAM**: 4GB mínimo (8GB recomendado)
- **Espaço em Disco**: 20GB (para dados históricos)

---

## 🆘 **Suporte e Documentação**

### **Documentação Completa:**
- `README.md` - Guia principal
- `docs/INSTALLATION.md` - Instalação detalhada
- `docs/TROUBLESHOOTING.md` - Resolução de problemas
- `CHANGELOG.md` - Histórico de mudanças

### **Testes e Validação:**
- `teste-final-v2.1.sh` - Testes rápidos
- `test-system-v2.1.sh` - Testes completos

### **Scripts Úteis:**
- `install-v2.1.0-final.sh` - Instalação automatizada
- `aplicar-correções.sh` - Correções automáticas
- `bgp-monitor.sh` - Gerenciamento manual

---

## 🎯 **Próximos Passos**

A v2.1.1 estabelece uma base estável para:
- ✅ Sistema funcionando como serviço
- ✅ Distribuição confiável
- ✅ Instalação automatizada
- ✅ Persistência garantida

**Esta versão está pronta para produção!** 🚀

---

**BGP Monitor v2.1.1** - Sistema profissional de monitoramento BGP com PostgreSQL  
*Desenvolvido para ambientes de produção com alta disponibilidade*
