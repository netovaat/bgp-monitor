#!/bin/bash

# =============================================================================
# BGP Monitor v2.1.0 - Script de Criação de Pacote ZIP Simples
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para mostrar progresso
progress() {
    echo -e "${BLUE}>>> $1${NC}"
}

# Função para mostrar sucesso
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Função para mostrar erro
error() {
    echo -e "${RED}✗ $1${NC}"
}

echo "=== BGP Monitor v2.1.0 - Criação de Pacote ZIP ==="

# Verificar se estamos no diretório correto
if [ ! -f "app/main.py" ]; then
    error "Não encontrado app/main.py. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Definir variáveis
PROJECT_DIR=$(pwd)
PACKAGE_NAME="bgp-monitor-v2.1.0"
TEMP_DIR="/tmp/${PACKAGE_NAME}"
FINAL_PACKAGE="/tmp/${PACKAGE_NAME}.zip"

progress "1. Preparando diretório temporário"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
success "Diretório temporário criado: $TEMP_DIR"

progress "2. Copiando arquivos essenciais do projeto"
# Copiar estrutura principal
cp -r app/ "$TEMP_DIR/"
cp -r docs/ "$TEMP_DIR/"
cp -r alembic/ "$TEMP_DIR/"

# Copiar arquivos de configuração
cp requirements.txt "$TEMP_DIR/"
cp alembic.ini "$TEMP_DIR/"
cp LICENSE "$TEMP_DIR/"

# Copiar documentação
cp README.md "$TEMP_DIR/"
cp CHANGELOG.md "$TEMP_DIR/"
cp RELEASE-NOTES-v2.1.0.md "$TEMP_DIR/"

# Copiar scripts principais
cp install-v2.1.0-final.sh "$TEMP_DIR/"
cp test-system-v2.1.sh "$TEMP_DIR/"
cp teste-final-v2.1.sh "$TEMP_DIR/"
cp aplicar-correções.sh "$TEMP_DIR/"

success "Arquivos essenciais copiados"

progress "3. Limpando cache e arquivos temporários"
cd "$TEMP_DIR"

# Remover cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# Remover arquivos temporários
find . -name "*.log" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remover diretórios de teste temporários
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true

success "Cache e arquivos temporários removidos"

progress "4. Definindo permissões corretas"
# Permissões para arquivos Python
find . -type f -name "*.py" -exec chmod 644 {} \;

# Permissões para documentação
find . -type f -name "*.md" -exec chmod 644 {} \;
find . -type f -name "*.txt" -exec chmod 644 {} \;

# Permissões para scripts
find . -type f -name "*.sh" -exec chmod 755 {} \;

# Permissões para diretórios
find . -type d -exec chmod 755 {} \;

success "Permissões definidas"

progress "5. Validando arquivos críticos"
CRITICAL_FILES=(
    "app/main.py"
    "app/__init__.py"
    "requirements.txt"
    "README.md"
    "CHANGELOG.md"
    "install-v2.1.0-final.sh"
    "teste-final-v2.1.sh"
)

echo "Validando arquivos críticos:"
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (AUSENTE)"
    fi
done

progress "6. Criando arquivo de informações"
cat > PACKAGE-INFO.txt << 'EOF'
BGP Monitor v2.1.0 - Pacote ZIP de Distribuição
===============================================

Data de Criação: $(date)
Versão: 2.1.0
Tipo: Pacote ZIP Limpo

Conteúdo:
- Aplicação BGP Monitor completa
- Scripts de instalação automatizados
- Sistema de testes
- Documentação completa
- Arquivos de configuração

Scripts Incluídos:
- install-v2.1.0-final.sh: Instalação automatizada
- teste-final-v2.1.sh: Validação rápida
- test-system-v2.1.sh: Testes completos
- aplicar-correções.sh: Aplicar correções

Instalação:
1. Extrair: unzip bgp-monitor-v2.1.0.zip
2. Instalar: cd bgp-monitor-v2.1.0 && sudo ./install-v2.1.0-final.sh
3. Testar: ./teste-final-v2.1.sh

Suporte: Consulte README.md e docs/
EOF

# Substituir a data no arquivo
sed -i "s/\$(date)/$(date)/" PACKAGE-INFO.txt

success "Arquivo de informações criado"

progress "7. Criando pacote ZIP"
cd /tmp
rm -f "$FINAL_PACKAGE"

# Criar o arquivo ZIP
zip -r "$FINAL_PACKAGE" "$PACKAGE_NAME/" -x "*.pyc" "*/__pycache__/*" "*.log" "*.tmp"

success "Pacote ZIP criado: $FINAL_PACKAGE"

progress "8. Verificando o pacote criado"
echo ""
echo "=== INFORMAÇÕES DO PACOTE ==="
echo "Arquivo: $FINAL_PACKAGE"
echo "Tamanho: $(du -h "$FINAL_PACKAGE" | cut -f1)"

echo ""
echo "=== CONTEÚDO DO PACOTE ==="
unzip -l "$FINAL_PACKAGE" | head -20
echo "..."
echo "Total de arquivos: $(unzip -l "$FINAL_PACKAGE" | tail -1 | awk '{print $2}')"

echo ""
echo "=== ESTRUTURA PRINCIPAL ==="
unzip -l "$FINAL_PACKAGE" | grep -E "/$" | head -10

echo ""
echo "=== ARQUIVOS PRINCIPAIS ==="
unzip -l "$FINAL_PACKAGE" | grep -E "\.(py|md|txt|sh)$" | head -15

echo ""
echo "=== INSTRUÇÕES DE USO ==="
echo "1. Transferir para servidor destino:"
echo "   scp $FINAL_PACKAGE usuario@servidor:/tmp/"
echo ""
echo "2. Extrair no servidor:"
echo "   cd /opt && sudo unzip /tmp/$(basename $FINAL_PACKAGE)"
echo ""
echo "3. Executar instalação:"
echo "   cd /opt/$PACKAGE_NAME && sudo ./install-v2.1.0-final.sh"
echo ""
echo "4. Testar instalação:"
echo "   cd /opt/$PACKAGE_NAME && ./teste-final-v2.1.sh"

# Limpar diretório temporário
rm -rf "$TEMP_DIR"
success "Diretório temporário removido"

echo ""
echo -e "${GREEN}🎉 Pacote ZIP BGP Monitor v2.1.0 criado com sucesso!${NC}"
echo -e "${BLUE}Arquivo: $FINAL_PACKAGE${NC}"
