#!/usr/bin/env python3
"""
Script para verificar dependências do BGP Monitor
Autor: netovaat
"""

import sys
import subprocess
import pkg_resources

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    
    dependencies = []
    for req in requirements:
        if req.strip() and not req.startswith('#'):
            dependencies.append(req.strip())
    
    print("🔍 Verificando dependências do BGP Monitor...")
    print(f"Total de dependências: {len(dependencies)}")
    print("-" * 50)
    
    missing = []
    installed = []
    
    for dependency in dependencies:
        try:
            # Remove version specifications for checking
            pkg_name = dependency.split('==')[0].split('>=')[0].split('<=')[0]
            pkg_resources.get_distribution(pkg_name)
            installed.append(dependency)
            print(f"✅ {dependency}")
        except pkg_resources.DistributionNotFound:
            missing.append(dependency)
            print(f"❌ {dependency}")
    
    print("-" * 50)
    print(f"✅ Instaladas: {len(installed)}")
    print(f"❌ Faltando: {len(missing)}")
    
    if missing:
        print("\n📦 Para instalar as dependências faltantes:")
        print("pip install " + " ".join(missing))
        return False
    else:
        print("\n🎉 Todas as dependências estão instaladas!")
        return True

if __name__ == "__main__":
    if verificar_dependencias():
        sys.exit(0)
    else:
        sys.exit(1)