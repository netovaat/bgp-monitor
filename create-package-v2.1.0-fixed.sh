#!/bin/bash

# =============================================================================
# BGP Monitor v2.1.0 - Script de Criação do Pacote Final (CORRIGIDO)
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
mkdir -p "$TEMP_BASE"
success "Diretório base criado: $TEMP_BASE"

progress "2. Copiando arquivos do projeto"
# Copiar usando rsync com exclusões apropriadas
if command -v rsync >/dev/null 2>&1; then
    rsync -av \
        --exclude="*.log" \
        --exclude="*.tmp" \
        --exclude=".git/" \
        --exclude="__pycache__/" \
        --exclude="*.pyc" \
        --exclude="*.pyo" \
        --exclude="*.pyd" \
        --exclude=".pytest_cache/" \
        --exclude=".coverage" \
        --exclude="htmlcov/" \
        --exclude=".DS_Store" \
        --exclude="/tmp/" \
        "$PROJECT_DIR/" "$TEMP_DIR/"
else
    # Fallback para cp se rsync não estiver disponível
    cp -r "$PROJECT_DIR" "$TEMP_BASE/"
fi
success "Arquivos copiados para: $TEMP_DIR"

progress "3. Entrando no diretório do pacote e limpando"
cd "$TEMP_DIR"

# Verificar se estamos no lugar certo
if [ ! -f "app/main.py" ]; then
    error "Erro na cópia dos arquivos. app/main.py não encontrado no diretório temporário."
    exit 1
fi

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
rm -rf .git/ 2>/dev/null || true

# Limpar cache do ambiente virtual se existir
if [ -d "venv/" ]; then
    warning "Limpando cache do ambiente virtual..."
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
    "test-system-v2.1.sh"
    "aplicar-correções.sh"
)

MISSING_FILES=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $file"
    else
        error "✗ $file (AUSENTE)"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    error "Arquivos críticos ausentes. Abortando criação do pacote."
    exit 1
fi

progress "6. Verificando versão nos arquivos principais"
echo "Verificando versão 2.1.0 nos arquivos:"
if grep -q "2\.1\.0" app/__init__.py 2>/dev/null; then
    success "Versão encontrada em app/__init__.py"
fi
if grep -q "2\.1\.0" app/main.py 2>/dev/null; then
    success "Versão encontrada em app/main.py"
fi
if grep -q "2\.1\.0" README.md 2>/dev/null; then
    success "Versão encontrada em README.md"
fi

progress "7. Criando arquivo de informações do pacote"
cat > PACKAGE-INFO.txt << EOF
BGP Monitor v2.1.0 - Pacote de Distribuição
===========================================

Data de Criação: $(date)
Versão: 2.1.0
Ambiente: Produção
Diretório de Origem: $PROJECT_DIR

Arquivos Incluídos:
- Aplicação completa BGP Monitor
- Scripts de instalação automatizados
- Sistema de testes abrangente
- Documentação completa
- Changelog e notas de lançamento
- Ambiente virtual configurado

Scripts Principais:
- install-v2.1.0-final.sh: Instalação completa automatizada
- teste-final-v2.1.sh: Validação rápida do sistema (8 testes)
- test-system-v2.1.sh: Testes completos (40+ testes)
- aplicar-correções.sh: Aplicação de correções de imports

Correções Incluídas na v2.1.0:
- Correção crítica de imports BGPScheduler
- Compatibilidade get_db/get_db_session
- Scripts de instalação otimizados
- Sistema de testes automatizados
- Fallback inteligente para imports

Estrutura do Projeto:
$(find . -maxdepth 2 -type d | head -15)

Para instalar:
1. Extrair o pacote: tar -xzf bgp-monitor-v2.1.0.tar.gz
2. Entrar no diretório: cd bgp-monitor-v2.1.0
3. Executar instalação: sudo ./install-v2.1.0-final.sh
4. Testar sistema: ./teste-final-v2.1.sh

Para testes completos:
- ./test-system-v2.1.sh (requer mais tempo)

Suporte: Consulte README.md e docs/INSTALLATION.md
EOF

success "Arquivo PACKAGE-INFO.txt criado"

progress "8. Criando o pacote final"
cd "$TEMP_BASE"
rm -f "$FINAL_PACKAGE"

# Criar o pacote tar.gz
tar -czf "$FINAL_PACKAGE" "$PACKAGE_NAME/"

if [ ! -f "$FINAL_PACKAGE" ]; then
    error "Falha ao criar o pacote tar.gz"
    exit 1
fi

success "Pacote criado: $FINAL_PACKAGE"

progress "9. Gerando checksums"
cd /tmp
md5sum "$(basename "$FINAL_PACKAGE")" > "${FINAL_PACKAGE}.md5"
sha256sum "$(basename "$FINAL_PACKAGE")" > "${FINAL_PACKAGE}.sha256"

success "Checksums gerados"

progress "10. Informações finais do pacote"
echo -e "\n${GREEN}=== INFORMAÇÕES DO PACOTE FINAL ===${NC}"
echo "Arquivo: $FINAL_PACKAGE"
echo "Tamanho: $(du -h "$FINAL_PACKAGE" | cut -f1)"
echo "MD5: $(cat "${FINAL_PACKAGE}.md5" | awk '{print $1}')"
echo "SHA256: $(cat "${FINAL_PACKAGE}.sha256" | awk '{print $1}')"

echo -e "\n${BLUE}=== ESTRUTURA DO PACOTE ===${NC}"
echo "Primeiros 25 arquivos/diretórios:"
tar -tzf "$FINAL_PACKAGE" | head -25
total_files=$(tar -tzf "$FINAL_PACKAGE" | wc -l)
echo "..."
echo "Total de arquivos: $total_files"

echo -e "\n${BLUE}=== ARQUIVOS DE CHECKSUM ===${NC}"
ls -la "${FINAL_PACKAGE}"*

echo -e "\n${YELLOW}=== INSTRUÇÕES DE INSTALAÇÃO ===${NC}"
echo "1. Transferir para servidor de destino:"
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
echo ""
echo "5. Para testes completos:"
echo "   cd /opt/$PACKAGE_NAME && ./test-system-v2.1.sh"

# Limpar diretório temporário
rm -rf "$TEMP_BASE"
success "Diretório temporário removido"

echo -e "\n${GREEN}🎉 PACOTE BGP MONITOR v2.1.0 CRIADO COM SUCESSO! 🎉${NC}"
echo -e "${GREEN}Arquivo: $FINAL_PACKAGE${NC}"
echo -e "${GREEN}Pronto para distribuição!${NC}"

log "Processo de criação do pacote concluído com sucesso!"
