#!/bin/bash

# =============================================================================
# BGP Monitor v2.1.0 - Script de Criação do Pacote Final
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging com timestamp
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Função para mostrar progresso
progress() {
    echo -e "${BLUE}>>> $1${NC}"
}

# Função para mostrar sucesso
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Função para mostrar aviso
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Função para mostrar erro
error() {
    echo -e "${RED}✗ $1${NC}"
}

log "Iniciando criação do pacote final BGP Monitor v2.1.0"

# Verificar se estamos no diretório correto
if [ ! -f "app/main.py" ]; then
    error "Não encontrado app/main.py. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Definir variáveis
PROJECT_DIR=$(pwd)
PACKAGE_NAME="bgp-monitor-v2.1.0"
TEMP_BASE="/tmp/bgp-package-build"
TEMP_DIR="${TEMP_BASE}/${PACKAGE_NAME}"
FINAL_PACKAGE="/tmp/${PACKAGE_NAME}.tar.gz"

progress "1. Preparando diretório temporário"
rm -rf "$TEMP_BASE"
mkdir -p "$TEMP_DIR"
success "Diretório temporário criado: $TEMP_DIR"

progress "2. Copiando arquivos do projeto"
# Usar rsync para evitar problemas de cópia recursiva
rsync -av --exclude="$TEMP_BASE" . "$TEMP_DIR/"
success "Arquivos copiados para diretório temporário"

progress "3. Limpando arquivos temporários e cache"
cd "$TEMP_DIR"

# Remover arquivos de cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# Remover arquivos temporários
rm -f *.log 2>/dev/null || true
rm -f *.tmp 2>/dev/null || true
rm -f .DS_Store 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remover diretórios temporários
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true

# Manter o ambiente virtual se existir, mas limpar cache
if [ -d "venv/" ]; then
    warning "Mantendo ambiente virtual, mas limpando cache..."
    find venv/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find venv/ -name "*.pyc" -delete 2>/dev/null || true
fi

success "Arquivos temporários e cache removidos"

progress "4. Definindo permissões corretas"
# Permissões para arquivos
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type f -name "*.md" -exec chmod 644 {} \;
find . -type f -name "*.txt" -exec chmod 644 {} \;
find . -type f -name "*.json" -exec chmod 644 {} \;
find . -type f -name "*.yml" -exec chmod 644 {} \;
find . -type f -name "*.yaml" -exec chmod 644 {} \;
find . -type f -name "*.sql" -exec chmod 644 {} \;
find . -type f -name "*.env*" -exec chmod 600 {} \;

# Permissões para scripts executáveis
find . -type f -name "*.sh" -exec chmod 755 {} \;

# Permissões para diretórios
find . -type d -exec chmod 755 {} \;

success "Permissões definidas corretamente"

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

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $file"
    else
        error "✗ $file (AUSENTE)"
    fi
done

progress "6. Criando arquivo de informações do pacote"
cat > PACKAGE-INFO.txt << EOF
BGP Monitor v2.1.0 - Pacote de Distribuição
===========================================

Data de Criação: $(date)
Versão: 2.1.0
Ambiente: Produção

Arquivos Incluídos:
- Aplicação completa BGP Monitor
- Scripts de instalação automatizados
- Sistema de testes abrangente
- Documentação completa
- Changelog e notas de lançamento

Scripts Principais:
- install-v2.1.0-final.sh: Instalação completa automatizada
- teste-final-v2.1.sh: Validação rápida do sistema
- test-system-v2.1.sh: Testes completos
- aplicar-correções.sh: Aplicação de correções

Correções Incluídas na v2.1.0:
- Correção de imports BGPScheduler
- Compatibilidade get_db
- Scripts de instalação otimizados
- Sistema de testes automatizados

Para instalar:
1. Extrair o pacote: tar -xzf bgp-monitor-v2.1.0.tar.gz
2. Executar: ./install-v2.1.0-final.sh
3. Testar: ./teste-final-v2.1.sh

Suporte: Consulte README.md e docs/
EOF

success "Arquivo PACKAGE-INFO.txt criado"

progress "7. Criando checksum do pacote"
cd "$TEMP_BASE"
rm -f "$FINAL_PACKAGE"
tar -czf "$FINAL_PACKAGE" "$PACKAGE_NAME/"

# Criar checksums
echo "Criando checksums..."
md5sum "$FINAL_PACKAGE" > "${FINAL_PACKAGE}.md5"
sha256sum "$FINAL_PACKAGE" > "${FINAL_PACKAGE}.sha256"

success "Pacote criado: $FINAL_PACKAGE"

progress "8. Informações finais do pacote"
echo -e "\n=== INFORMAÇÕES DO PACOTE FINAL ==="
echo "Arquivo: $FINAL_PACKAGE"
echo "Tamanho: $(du -h "$FINAL_PACKAGE" | cut -f1)"
echo "MD5: $(cat "${FINAL_PACKAGE}.md5" | cut -d' ' -f1)"
echo "SHA256: $(cat "${FINAL_PACKAGE}.sha256" | cut -d' ' -f1)"

echo -e "\n=== CONTEÚDO DO PACOTE ==="
tar -tzf "$FINAL_PACKAGE" | head -20
echo "..."
echo "Total de arquivos: $(tar -tzf "$FINAL_PACKAGE" | wc -l)"

echo -e "\n=== INSTRUÇÕES DE USO ==="
echo "1. Copiar para o servidor de destino:"
echo "   scp $FINAL_PACKAGE usuario@servidor:/tmp/"
echo ""
echo "2. Extrair no servidor:"
echo "   cd /opt && sudo tar -xzf /tmp/$(basename $FINAL_PACKAGE)"
echo ""
echo "3. Executar instalação:"
echo "   cd /opt/$PACKAGE_NAME && sudo ./install-v2.1.0-final.sh"
echo ""
echo "4. Testar instalação:"
echo "   cd /opt/$PACKAGE_NAME && ./teste-final-v2.1.sh"

success "✅ Pacote BGP Monitor v2.1.0 criado com sucesso!"

# Limpar diretório temporário
rm -rf "$TEMP_DIR"
success "Diretório temporário removido"

log "Processo de criação do pacote concluído com sucesso!"
echo -e "\n${GREEN}🎉 BGP Monitor v2.1.0 pronto para distribuição!${NC}"
TEMP_DIR="/tmp/${PACKAGE_NAME}"
FINAL_PACKAGE="/tmp/${PACKAGE_NAME}.tar.gz"

progress "1. Preparando diretório temporário"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
success "Diretório temporário criado: $TEMP_DIR"

progress "2. Copiando arquivos do projeto"
cp -r . "$TEMP_DIR/"
success "Arquivos copiados para diretório temporário"

progress "3. Limpando arquivos temporários e cache"
cd "$TEMP_DIR"

# Remover arquivos de cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# Remover arquivos temporários
rm -f *.log 2>/dev/null || true
rm -f *.tmp 2>/dev/null || true
rm -f .DS_Store 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remover diretórios temporários
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true

# Manter o ambiente virtual se existir, mas limpar cache
if [ -d "venv/" ]; then
    warning "Mantendo ambiente virtual, mas limpando cache..."
    find venv/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find venv/ -name "*.pyc" -delete 2>/dev/null || true
fi

success "Arquivos temporários e cache removidos"

progress "4. Definindo permissões corretas"
# Permissões para arquivos
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type f -name "*.md" -exec chmod 644 {} \;
find . -type f -name "*.txt" -exec chmod 644 {} \;
find . -type f -name "*.json" -exec chmod 644 {} \;
find . -type f -name "*.yml" -exec chmod 644 {} \;
find . -type f -name "*.yaml" -exec chmod 644 {} \;
find . -type f -name "*.sql" -exec chmod 644 {} \;
find . -type f -name "*.env*" -exec chmod 600 {} \;

# Permissões para scripts executáveis
find . -type f -name "*.sh" -exec chmod 755 {} \;
chmod 755 install-v2.1.0-final.sh 2>/dev/null || true
chmod 755 test-system-v2.1.sh 2>/dev/null || true
chmod 755 teste-final-v2.1.sh 2>/dev/null || true
chmod 755 aplicar-correções.sh 2>/dev/null || true

# Permissões para diretórios
find . -type d -exec chmod 755 {} \;

success "Permissões definidas corretamente"

progress "5. Verificando estrutura do projeto"
echo "Estrutura principal do projeto:"
tree -L 3 . 2>/dev/null || ls -la

echo -e "\nArquivos principais:"
ls -la *.md *.txt *.sh 2>/dev/null || echo "Nenhum arquivo principal encontrado"

echo -e "\nDiretório app/:"
ls -la app/ | head -10

success "Estrutura verificada"

progress "6. Validando arquivos críticos"
CRITICAL_FILES=(
    "app/main.py"
    "app/__init__.py"
    "requirements.txt"
    "README.md"
    "CHANGELOG.md"
    "install-v2.1.0-final.sh"
    "teste-final-v2.1.sh"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $file"
    else
        error "✗ $file (AUSENTE)"
    fi
done

progress "7. Verificando versão nos arquivos"
echo "Verificando versão 2.1.0 nos arquivos:"
grep -n "2\.1\.0" app/__init__.py 2>/dev/null && success "Versão encontrada em app/__init__.py"
grep -n "2\.1\.0" app/main.py 2>/dev/null && success "Versão encontrada em app/main.py"
grep -n "2\.1\.0" README.md 2>/dev/null && success "Versão encontrada em README.md"

progress "8. Criando arquivo de informações do pacote"
cat > PACKAGE-INFO.txt << EOF
BGP Monitor v2.1.0 - Pacote de Distribuição
===========================================

Data de Criação: $(date)
Versão: 2.1.0
Ambiente: Produção

Arquivos Incluídos:
- Aplicação completa BGP Monitor
- Scripts de instalação automatizados
- Sistema de testes abrangente
- Documentação completa
- Changelog e notas de lançamento

Scripts Principais:
- install-v2.1.0-final.sh: Instalação completa automatizada
- teste-final-v2.1.sh: Validação rápida do sistema
- test-system-v2.1.sh: Testes completos
- aplicar-correções.sh: Aplicação de correções

Correções Incluídas na v2.1.0:
- Correção de imports BGPScheduler
- Compatibilidade get_db
- Scripts de instalação otimizados
- Sistema de testes automatizados

Para instalar:
1. Extrair o pacote: tar -xzf bgp-monitor-v2.1.0.tar.gz
2. Executar: ./install-v2.1.0-final.sh
3. Testar: ./teste-final-v2.1.sh

Suporte: Consulte README.md e docs/
EOF

success "Arquivo PACKAGE-INFO.txt criado"

progress "9. Criando checksum do pacote"
cd /tmp
rm -f "$FINAL_PACKAGE"
tar -czf "$FINAL_PACKAGE" "$PACKAGE_NAME"

# Criar checksums
echo "Criando checksums..."
md5sum "$FINAL_PACKAGE" > "${FINAL_PACKAGE}.md5"
sha256sum "$FINAL_PACKAGE" > "${FINAL_PACKAGE}.sha256"

success "Pacote criado: $FINAL_PACKAGE"

progress "10. Informações finais do pacote"
echo -e "\n=== INFORMAÇÕES DO PACOTE FINAL ==="
echo "Arquivo: $FINAL_PACKAGE"
echo "Tamanho: $(du -h "$FINAL_PACKAGE" | cut -f1)"
echo "MD5: $(cat "${FINAL_PACKAGE}.md5" | cut -d' ' -f1)"
echo "SHA256: $(cat "${FINAL_PACKAGE}.sha256" | cut -d' ' -f1)"

echo -e "\n=== CONTEÚDO DO PACOTE ==="
tar -tzf "$FINAL_PACKAGE" | head -20
echo "..."
echo "Total de arquivos: $(tar -tzf "$FINAL_PACKAGE" | wc -l)"

echo -e "\n=== ARQUIVOS DE CHECKSUM ==="
ls -la "${FINAL_PACKAGE}"*

echo -e "\n=== INSTRUÇÕES DE USO ==="
echo "1. Copiar para o servidor de destino:"
echo "   scp $FINAL_PACKAGE usuario@servidor:/tmp/"
echo ""
echo "2. Extrair no servidor:"
echo "   cd /opt && sudo tar -xzf /tmp/$(basename $FINAL_PACKAGE)"
echo ""
echo "3. Executar instalação:"
echo "   cd /opt/$PACKAGE_NAME && sudo ./install-v2.1.0-final.sh"
echo ""
echo "4. Testar instalação:"
echo "   cd /opt/$PACKAGE_NAME && ./teste-final-v2.1.sh"

success "✅ Pacote BGP Monitor v2.1.0 criado com sucesso!"

# Limpar diretório temporário
rm -rf "$TEMP_DIR"
success "Diretório temporário removido"

log "Processo de criação do pacote concluído com sucesso!"
echo -e "\n${GREEN}🎉 BGP Monitor v2.1.0 pronto para distribuição!${NC}"
