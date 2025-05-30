# 🔧 Correções na Instalação do BGP Monitor v2.0

Este documento lista todas as correções aplicadas durante o processo de instalação para garantir funcionamento sem erros.

## ❌ Problema 1: ModuleNotFoundError: No module named 'psycopg2'

### **Erro Encontrado:**
```bash
ModuleNotFoundError: No module named 'psycopg2'
```

### **Causa:**
O arquivo `alembic.ini` está configurado para usar `postgresql+psycopg2://` mas o `psycopg2` não está incluído no `requirements.txt`.

### **Solução:**
Adicionar `psycopg2-binary` ao `requirements.txt` para suporte ao PostgreSQL no Alembic.

### **Arquivo Alterado:**
- `/opt/bgp-monitor/requirements.txt`

### **Mudança Aplicada:**
```diff
# Banco de Dados PostgreSQL
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.23
alembic==1.12.1
+ psycopg2-binary==2.9.9
```

### **Comando para Aplicar:**
```bash
# Reinstalar dependências com a correção
sudo -u bgpmonitor bash -c "
    source /opt/bgp-monitor/venv/bin/activate
    pip install psycopg2-binary==2.9.9
"
```

---

## ❌ Problema 2: FileNotFoundError: 'alembic/script.py.mako'

### **Erro Encontrado:**
```bash
FileNotFoundError: [Errno 2] No such file or directory: 'alembic/script.py.mako'
```

### **Causa:**
O template do Alembic (`script.py.mako`) não foi criado durante a inicialização do Alembic. Este arquivo é necessário para gerar as migrations.

### **Solução:**
Criar o arquivo `script.py.mako` com o template padrão do Alembic.

### **Arquivo Criado:**
- `/opt/bgp-monitor/alembic/script.py.mako`

### **Comando para Aplicar:**
```bash
# Criar o template necessário
sudo -u bgpmonitor bash -c "cat > /opt/bgp-monitor/alembic/script.py.mako << 'EOF'
\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else \"\"}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else \"pass\"}


def downgrade() -> None:
    ${downgrades if downgrades else \"pass\"}
EOF"
```

---

## ❌ Problema 3: FAILED: Could not determine revision id from filename

### **Erro Encontrado:**
```bash
FAILED: Could not determine revision id from filename 10cf5c2ea1a0_initial_migration.py. Be sure the 'revision' variable is declared inside the script
```

### **Causa:**
O arquivo de migration `/opt/bgp-monitor/alembic/versions/10cf5c2ea1a0_initial_migration.py` existe mas está vazio, não contendo as variáveis necessárias para o Alembic.

### **Solução:**
1. Remover o arquivo de migration vazio
2. Recriar a migration inicial com conteúdo correto

### **Arquivos Afetados:**
- `/opt/bgp-monitor/alembic/versions/10cf5c2ea1a0_initial_migration.py`

### **Comandos para Aplicar:**
```bash
# Remover arquivo de migration vazio
sudo -u bgpmonitor rm -f /opt/bgp-monitor/alembic/versions/10cf5c2ea1a0_initial_migration.py
sudo -u bgpmonitor rm -rf /opt/bgp-monitor/alembic/versions/__pycache__

# Recriar migration inicial
sudo -u bgpmonitor bash -c "
    cd /opt/bgp-monitor
    source venv/bin/activate
    alembic revision --autogenerate -m 'Initial migration'
"
```

---

## 📋 Status das Correções

- [x] **Correção 1**: Adicionado psycopg2-binary ao requirements.txt ✅
- [x] **Correção 2**: Criado script.py.mako para template do Alembic ✅
- [x] **Correção 3**: Removido arquivo de migration vazio e recriada a migration inicial ✅
- [x] **Migration aplicada**: Database inicializado com todas as tabelas criadas ✅

### ✅ **TODAS AS CORREÇÕES APLICADAS COM SUCESSO!**

O sistema BGP Monitor v2.0 agora está totalmente funcional e pronto para instalação em máquinas novas.

---

## 🔄 Script de Aplicação Rápida de Correções

```bash
#!/bin/bash
# Script para aplicar todas as correções conhecidas

echo "🔧 Aplicando correções do BGP Monitor v2.0..."

# Correção 1: Instalar psycopg2-binary
echo "📦 Instalando psycopg2-binary..."
sudo -u bgpmonitor bash -c "
    source /opt/bgp-monitor/venv/bin/activate
    pip install psycopg2-binary==2.9.9
"

# Correção 2: Criar script.py.mako para Alembic
echo "📂 Criando script.py.mako para Alembic..."
sudo -u bgpmonitor bash -c "cat > /opt/bgp-monitor/alembic/script.py.mako << 'EOF'
\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else \"\"}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else \"pass\"}


def downgrade() -> None:
    ${downgrades if downgrades else \"pass\"}
EOF"

# Correção 3: Remover arquivo de migration vazio e recriar migration inicial
echo "🗑️ Removendo arquivo de migration vazio e recriando migration inicial..."
sudo -u bgpmonitor rm -f /opt/bgp-monitor/alembic/versions/10cf5c2ea1a0_initial_migration.py
sudo -u bgpmonitor rm -rf /opt/bgp-monitor/alembic/versions/__pycache__
sudo -u bgpmonitor bash -c "
    cd /opt/bgp-monitor
    source venv/bin/activate
    alembic revision --autogenerate -m 'Initial migration'
"

echo "✅ Correções aplicadas com sucesso!"
```

---

**Data da última atualização**: $(date)
**Versão**: 1.0
