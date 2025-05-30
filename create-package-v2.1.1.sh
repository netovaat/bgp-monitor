#!/bin/bash

# =============================================================================
# BGP Monitor v2.1.1 - Script de Criação do Pacote Final
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

log "Iniciando criação do pacote final BGP Monitor v2.1.1"

# Verificar se estamos no diretório correto
if [ ! -f "app/main.py" ]; then
    error "Não encontrado app/main.py. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Definir variáveis
PROJECT_DIR=$(pwd)
PACKAGE_NAME="bgp-monitor-v2.1.1"
TEMP_BASE="/tmp/bgp-package-build"
TEMP_DIR="${TEMP_BASE}/${PACKAGE_NAME}"
FINAL_PACKAGE="/tmp/${PACKAGE_NAME}.tar.gz"
FINAL_ZIP="/tmp/${PACKAGE_NAME}.zip"

progress "1. Preparando diretório temporário"
rm -rf "$TEMP_BASE"
mkdir -p "$TEMP_DIR"
success "Diretório temporário criado: $TEMP_DIR"

progress "2. Copiando arquivos do projeto"
# Usar rsync para evitar problemas de cópia recursiva e excluir diretórios desnecessários
if command -v rsync >/dev/null 2>&1; then
    rsync -av \
        --exclude="$TEMP_BASE" \
        --exclude="venv/" \
        --exclude=".git/" \
        --exclude=".pytest_cache/" \
        --exclude="*.egg-info/" \
        --exclude="__pycache__/" \
        --exclude="*.pyc" \
        --exclude="*.pyo" \
        --exclude="*.log" \
        --exclude=".env" \
        --exclude="node_modules/" \
        . "$TEMP_DIR/"
else
    # Fallback para cp (menos eficiente mas funciona)
    cp -r . "$TEMP_DIR/"
    # Remover diretórios desnecessários manualmente
    rm -rf "$TEMP_DIR/venv" 2>/dev/null || true
    rm -rf "$TEMP_DIR/.git" 2>/dev/null || true
    rm -rf "$TEMP_DIR/.pytest_cache" 2>/dev/null || true
    rm -rf "$TEMP_DIR/node_modules" 2>/dev/null || true
fi
success "Arquivos copiados para diretório temporário (excluindo venv, .git, cache)"

progress "3. Limpando arquivos temporários e cache"
cd "$TEMP_DIR"

# Remover ambiente virtual se existir
rm -rf venv/ 2>/dev/null || true

# Remover arquivos de controle de versão
rm -rf .git/ 2>/dev/null || true
rm -rf .gitignore 2>/dev/null || true

# Remover arquivos de cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# Remover arquivos temporários e logs
rm -f *.log 2>/dev/null || true
rm -f .env 2>/dev/null || true
rm -f .env.* 2>/dev/null || true

# Remover diretórios de teste e cache
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true
rm -rf node_modules/ 2>/dev/null || true

# Remover scripts de desenvolvimento obsoletos
rm -f create-package-v2.1.0.sh 2>/dev/null || true
rm -f create-package-v2.1.0-fixed.sh 2>/dev/null || true
rm -f create-zip-package.sh 2>/dev/null || true
rm -f *.tmp 2>/dev/null || true
rm -f .DS_Store 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remover diretórios temporários
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true
rm -rf logs/ 2>/dev/null || true
rm -rf tmp/ 2>/dev/null || true

# Limpar cache do ambiente virtual se existir
if [ -d "venv/" ]; then
    warning "Mantendo ambiente virtual, mas limpando cache..."
    find venv/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find venv/ -name "*.pyc" -delete 2>/dev/null || true
fi

# Remover scripts de empacotamento antigos
rm -f create-package-v2.1.0.sh 2>/dev/null || true
rm -f create-package-v2.1.0-fixed.sh 2>/dev/null || true
rm -f create-zip-package.sh 2>/dev/null || true

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
    "RELEASE-NOTES-v2.1.1.md"
    "install-v2.1.0-final.sh"
    "teste-final-v2.1.sh"
    "bgp-monitor.sh"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $file"
    else
        error "✗ $file (AUSENTE)"
    fi
done

progress "6. Verificando versão nos arquivos"
echo "Verificando versão 2.1.1 nos arquivos:"
grep -n "2\.1\.1" app/__init__.py 2>/dev/null && success "Versão encontrada em app/__init__.py"
grep -n "2\.1\.1" app/main.py 2>/dev/null && success "Versão encontrada em app/main.py"
grep -n "2\.1\.1" README.md 2>/dev/null && success "Versão encontrada em README.md"

progress "7. Criando arquivo de informações do pacote"
cat > PACKAGE-INFO.txt << EOF
BGP Monitor v2.1.1 - Pacote de Distribuição
===========================================

Data de Criação: $(date)
Versão: 2.1.1
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
- bgp-monitor.sh: Gerenciamento manual da aplicação

Correções Incluídas na v2.1.1:
- Serviço systemd funcional e persistente
- Scripts bgp-monitor.sh corrigidos
- Dependências completas no ambiente virtual
- Pacote otimizado para distribuição

Para instalar:
1. Extrair o pacote: tar -xzf bgp-monitor-v2.1.1.tar.gz
2. Executar: ./install-v2.1.0-final.sh
3. Testar: ./teste-final-v2.1.sh

Gerenciamento como serviço:
- sudo systemctl start bgp-monitor
- sudo systemctl status bgp-monitor
- sudo journalctl -u bgp-monitor -f

Suporte: Consulte README.md e docs/
EOF

success "Arquivo PACKAGE-INFO.txt criado"

progress "8. Criando pacote TAR.GZ"
cd "$TEMP_BASE"
rm -f "$FINAL_PACKAGE"
tar -czf "$FINAL_PACKAGE" "$PACKAGE_NAME/"

# Criar checksums
echo "Criando checksums..."
md5sum "$FINAL_PACKAGE" > "${FINAL_PACKAGE}.md5"
sha256sum "$FINAL_PACKAGE" > "${FINAL_PACKAGE}.sha256"

success "Pacote TAR.GZ criado: $FINAL_PACKAGE"

progress "9. Criando pacote ZIP"
if command -v zip >/dev/null 2>&1; then
    rm -f "$FINAL_ZIP"
    zip -r "$FINAL_ZIP" "$PACKAGE_NAME/" >/dev/null
    
    # Criar checksums para ZIP
    md5sum "$FINAL_ZIP" > "${FINAL_ZIP}.md5"
    sha256sum "$FINAL_ZIP" > "${FINAL_ZIP}.sha256"
    
    success "Pacote ZIP criado: $FINAL_ZIP"
else
    warning "Comando 'zip' não encontrado. Apenas TAR.GZ foi criado."
fi

progress "10. Informações finais dos pacotes"
echo -e "\n=== INFORMAÇÕES DOS PACOTES FINAIS ==="
echo "Arquivos criados:"
if [ -f "$FINAL_PACKAGE" ]; then
    echo "  TAR.GZ: $FINAL_PACKAGE"
    echo "  Tamanho: $(du -h "$FINAL_PACKAGE" | cut -f1)"
    echo "  MD5: $(cat "${FINAL_PACKAGE}.md5" | cut -d' ' -f1)"
fi

if [ -f "$FINAL_ZIP" ]; then
    echo "  ZIP: $FINAL_ZIP"
    echo "  Tamanho: $(du -h "$FINAL_ZIP" | cut -f1)"
    echo "  MD5: $(cat "${FINAL_ZIP}.md5" | cut -d' ' -f1)"
fi

echo -e "\n=== CONTEÚDO DO PACOTE ==="
tar -tzf "$FINAL_PACKAGE" | head -20
echo "..."
echo "Total de arquivos: $(tar -tzf "$FINAL_PACKAGE" | wc -l)"

echo -e "\n=== ARQUIVOS DE CHECKSUM ==="
ls -la /tmp/bgp-monitor-v2.1.1.*

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
echo "4. Verificar funcionamento:"
echo "   sudo systemctl status bgp-monitor"
echo "   curl http://localhost:8000/health"

success "✅ Pacote BGP Monitor v2.1.1 criado com sucesso!"

# Limpar diretório temporário
rm -rf "$TEMP_DIR"
success "Diretório temporário removido"

log "Processo de criação do pacote concluído com sucesso!"
echo -e "\n${GREEN}🎉 BGP Monitor v2.1.1 pronto para distribuição!${NC}"
echo -e "\n${BLUE}📦 Pacotes disponíveis em /tmp/${NC}"
echo -e "${BLUE}   - bgp-monitor-v2.1.1.tar.gz${NC}"
if [ -f "$FINAL_ZIP" ]; then
    echo -e "${BLUE}   - bgp-monitor-v2.1.1.zip${NC}"
fi
