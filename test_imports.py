#!/usr/bin/env python3
"""
Script de teste rápido para validar imports corrigidos
"""
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, '/opt/bgp-monitor')
os.chdir('/opt/bgp-monitor')

def test_imports():
    print("🔍 Testando imports críticos corrigidos...")
    
    tests = []
    
    # Teste 1: Import principal
    try:
        from app.main import app
        tests.append(("app.main", True, "OK"))
    except Exception as e:
        tests.append(("app.main", False, str(e)))
    
    # Teste 2: Scheduler corrigido
    try:
        from app.services.scheduler import BGPScheduler
        tests.append(("BGPScheduler", True, "OK"))
    except Exception as e:
        tests.append(("BGPScheduler", False, str(e)))
    
    # Teste 3: Database corrigido
    try:
        from app.database import get_db
        tests.append(("Database get_db", True, "OK"))
    except Exception as e:
        tests.append(("Database get_db", False, str(e)))
    
    # Teste 4: Database session
    try:
        from app.database import get_db_session
        tests.append(("Database get_db_session", True, "OK"))
    except Exception as e:
        tests.append(("Database get_db_session", False, str(e)))
    
    # Mostrar resultados
    print("\n📊 Resultados dos testes:")
    all_passed = True
    for test_name, passed, message in tests:
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}: {message}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Todos os imports críticos funcionam!")
        return 0
    else:
        print("\n⚠️  Alguns imports ainda têm problemas")
        return 1

if __name__ == "__main__":
    exit(test_imports())
