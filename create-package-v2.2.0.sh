#!/bin/bash

# =============================================================================
# BGP Monitor v2.2.0 - Script de Empacotamento
# =============================================================================
# Autor: netovaat
# GitHub: https://github.com/netovaat/bgp-monitor
# 
# Este script cria pacotes de distribuição otimizados para o BGP Monitor v2.2.0
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES
# -----------------------------------------------------------------------------
readonly VERSION="2.2.0"
readonly PROJECT_NAME="bgp-monitor"
readonly SOURCE_DIR="/opt/bgp-monitor"
readonly BUILD_DIR="/tmp/bgp-monitor-build"
readonly PACKAGE_DIR="/tmp/bgp-monitor-packages"

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# -----------------------------------------------------------------------------
# FUNÇÕES DE UTILIDADE
# -----------------------------------------------------------------------------
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}"
    echo "============================================================================="
    echo " BGP Monitor v${VERSION} - Script de Empacotamento"
    echo "============================================================================="
    echo -e "${NC}"
}

# -----------------------------------------------------------------------------
# VALIDAÇÕES
# -----------------------------------------------------------------------------
validate_environment() {
    log_info "Validando ambiente..."
    
    # Verificar se tem permissões necessárias (pode ser root ou ter sudo)
    if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
        log_error "Este script precisa de permissões sudo ou root"
        exit 1
    fi
    
    # Verificar se o diretório fonte existe
    if [[ ! -d "$SOURCE_DIR" ]]; then
        log_error "Diretório fonte não encontrado: $SOURCE_DIR"
        exit 1
    fi
    
    # Verificar se os comandos necessários existem
    for cmd in tar gzip zip md5sum sha256sum; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Comando necessário não encontrado: $cmd"
            exit 1
        fi
    done
    
    log_success "Ambiente validado"
}

# -----------------------------------------------------------------------------
# LIMPEZA E PREPARAÇÃO
# -----------------------------------------------------------------------------
clean_and_prepare() {
    log_info "Limpando e preparando diretórios..."
    
    # Remover diretórios de build anteriores
    sudo rm -rf "$BUILD_DIR" "$PACKAGE_DIR"
    
    # Criar diretórios de trabalho
    mkdir -p "$BUILD_DIR" "$PACKAGE_DIR"
    
    log_success "Diretórios preparados"
}

# -----------------------------------------------------------------------------
# CÓPIA DE ARQUIVOS
# -----------------------------------------------------------------------------
copy_project_files() {
    log_info "Copiando arquivos do projeto..."
    
    # Copiar todo o projeto
    sudo cp -r "$SOURCE_DIR" "$BUILD_DIR/"
    
    # Entrar no diretório de build
    cd "$BUILD_DIR/bgp-monitor"
    
    # Remover arquivos desnecessários para distribuição
    log_info "Removendo arquivos desnecessários..."
    
    # Cache Python e arquivos compilados
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    find . -name "*.pyd" -delete 2>/dev/null || true
    
    # Cache de pip e outros caches
    rm -rf .cache/ 2>/dev/null || true
    rm -rf .pip-cache/ 2>/dev/null || true
    rm -rf pip-cache/ 2>/dev/null || true
    
    # Logs e arquivos temporários
    find . -name "*.log" -delete 2>/dev/null || true
    find . -name "*.pid" -delete 2>/dev/null || true
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.temp" -delete 2>/dev/null || true
    find . -name "*.bak" -delete 2>/dev/null || true
    find . -name "*~" -delete 2>/dev/null || true
    
    # Ambiente virtual (será recriado na instalação)
    rm -rf venv/ 2>/dev/null || true
    rm -rf env/ 2>/dev/null || true
    rm -rf .venv/ 2>/dev/null || true
    
    # Arquivos de configuração específicos (manter apenas .env.example)
    rm -f .env 2>/dev/null || true
    rm -f .env.local 2>/dev/null || true
    rm -f .env.production 2>/dev/null || true
    rm -f .env.development 2>/dev/null || true
    
    # Arquivos Git (opcional, manter .gitignore mas remover .git)
    rm -rf .git/ 2>/dev/null || true
    rm -f .gitmodules 2>/dev/null || true
    
    # Diretórios de build anteriores
    rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true
    rm -rf node_modules/ 2>/dev/null || true
    
    # Arquivos de desenvolvimento
    rm -rf .pytest_cache/ 2>/dev/null || true
    rm -rf .coverage 2>/dev/null || true
    rm -rf .tox/ 2>/dev/null || true
    rm -rf .mypy_cache/ 2>/dev/null || true
    
    # Arquivos de IDE
    rm -rf .vscode/ 2>/dev/null || true
    rm -rf .idea/ 2>/dev/null || true
    rm -rf *.swp 2>/dev/null || true
    rm -rf *.swo 2>/dev/null || true
    
    # Arquivos de sistema
    find . -name ".DS_Store" -delete 2>/dev/null || true
    find . -name "Thumbs.db" -delete 2>/dev/null || true
    
    # Scripts de empacotamento antigos (manter apenas o atual)
    rm -f create-package-v2.1.1.sh 2>/dev/null || true
    rm -f install-v2.1.sh 2>/dev/null || true
    rm -f validate-v2.2.0.sh 2>/dev/null || true
    
    log_success "Arquivos copiados e limpos"
}

# -----------------------------------------------------------------------------
# VALIDAÇÃO DE ARQUIVOS ESSENCIAIS
# -----------------------------------------------------------------------------
validate_essential_files() {
    log_info "Validando arquivos essenciais..."
    
    local essential_files=(
        "install.sh"
        ".env.example"
        "requirements.txt"
        "app/__init__.py"
        "app/main.py"
        "README.md"
        "CHANGELOG.md"
        "RELEASE-NOTES-v2.2.0.md"
        "docs/INSTALLATION.md"
    )
    
    local missing_files=()
    
    for file in "${essential_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_error "Arquivos essenciais não encontrados:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
    
    # Verificar se o script de instalação é executável
    if [[ ! -x "install.sh" ]]; then
        chmod +x install.sh
        log_warn "Permissão de execução adicionada ao install.sh"
    fi
    
    log_success "Todos os arquivos essenciais estão presentes"
}

# -----------------------------------------------------------------------------
# CRIAÇÃO DE METADADOS
# -----------------------------------------------------------------------------
create_metadata() {
    log_info "Criando metadados do pacote..."
    
    # Arquivo de informações da versão
    cat > VERSION.txt << EOF
BGP Monitor v${VERSION}
Autor: netovaat
GitHub: https://github.com/netovaat/bgp-monitor
Data do Build: $(date '+%Y-%m-%d %H:%M:%S')
Sistema: $(uname -a)
EOF
    
    # Arquivo de checksums dos arquivos importantes
    cat > CHECKSUMS.txt << EOF
# Checksums MD5 dos arquivos principais
$(md5sum install.sh .env.example requirements.txt app/__init__.py README.md)
EOF
    
    # Lista de arquivos incluídos
    echo "# Lista de arquivos incluídos no pacote v${VERSION}" > FILES.txt
    find . -type f | sort >> FILES.txt
    
    log_success "Metadados criados"
}

# -----------------------------------------------------------------------------
# CRIAÇÃO DE PACOTES
# -----------------------------------------------------------------------------
create_packages() {
    log_info "Criando pacotes de distribuição..."
    
    cd "$BUILD_DIR"
    
    local base_name="${PROJECT_NAME}-v${VERSION}"
    
    # Pacote TAR.GZ (formato principal)
    log_info "Criando pacote TAR.GZ..."
    tar -czf "${PACKAGE_DIR}/${base_name}.tar.gz" bgp-monitor/
    
    # Pacote ZIP (compatibilidade Windows)
    log_info "Criando pacote ZIP..."
    zip -r "${PACKAGE_DIR}/${base_name}.zip" bgp-monitor/ > /dev/null
    
    # Pacote TAR.XZ (compressão máxima)
    log_info "Criando pacote TAR.XZ..."
    tar -cJf "${PACKAGE_DIR}/${base_name}.tar.xz" bgp-monitor/
    
    log_success "Pacotes criados"
}

# -----------------------------------------------------------------------------
# GERAÇÃO DE CHECKSUMS
# -----------------------------------------------------------------------------
generate_checksums() {
    log_info "Gerando checksums dos pacotes..."
    
    cd "$PACKAGE_DIR"
    
    # MD5
    md5sum *.tar.gz *.zip *.tar.xz > "${PROJECT_NAME}-v${VERSION}-checksums-md5.txt"
    
    # SHA256
    sha256sum *.tar.gz *.zip *.tar.xz > "${PROJECT_NAME}-v${VERSION}-checksums-sha256.txt"
    
    log_success "Checksums gerados"
}

# -----------------------------------------------------------------------------
# RELATÓRIO FINAL
# -----------------------------------------------------------------------------
generate_report() {
    log_info "Gerando relatório final..."
    
    cd "$PACKAGE_DIR"
    
    local report_file="${PROJECT_NAME}-v${VERSION}-release-info.txt"
    
    cat > "$report_file" << EOF
# BGP Monitor v${VERSION} - Informações de Release

## Arquivos Gerados

### Pacotes de Distribuição
$(ls -lh *.tar.gz *.zip *.tar.xz)

### Checksums
- MD5: ${PROJECT_NAME}-v${VERSION}-checksums-md5.txt
- SHA256: ${PROJECT_NAME}-v${VERSION}-checksums-sha256.txt

## Verificação de Integridade

### MD5
$(cat *-checksums-md5.txt)

### SHA256
$(cat *-checksums-sha256.txt)

## Instalação Recomendada

# Download e extração
wget https://github.com/netovaat/bgp-monitor/releases/download/v${VERSION}/${PROJECT_NAME}-v${VERSION}.tar.gz
tar -xzf ${PROJECT_NAME}-v${VERSION}.tar.gz
cd bgp-monitor

# Instalação
sudo chmod +x install.sh
sudo ./install.sh

## Notas da Versão

- Script de instalação unificado
- Documentação de configuração completa (.env.example)
- Estrutura otimizada e limpa
- Compatibilidade mantida com v2.1.1

## Suporte

- GitHub: https://github.com/netovaat/bgp-monitor
- Documentação: docs/
- Issues: GitHub Issues

---
Gerado em: $(date '+%Y-%m-%d %H:%M:%S')
Sistema: $(uname -a)
EOF
    
    log_success "Relatório gerado: $report_file"
}

# -----------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# -----------------------------------------------------------------------------
main() {
    print_header
    
    validate_environment
    clean_and_prepare
    copy_project_files
    validate_essential_files
    create_metadata
    create_packages
    generate_checksums
    generate_report
    
    echo ""
    log_success "🎉 Empacotamento concluído com sucesso!"
    echo ""
    echo -e "${CYAN}Pacotes criados em:${NC} $PACKAGE_DIR"
    echo ""
    echo -e "${YELLOW}Arquivos gerados:${NC}"
    ls -lh "$PACKAGE_DIR"
    echo ""
    echo -e "${GREEN}✅ BGP Monitor v${VERSION} pronto para distribuição!${NC}"
}

# -----------------------------------------------------------------------------
# EXECUÇÃO
# -----------------------------------------------------------------------------
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
