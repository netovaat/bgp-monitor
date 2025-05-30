#!/usr/bin/env python3
"""
Test System Final - Teste completo do BGP Monitor v2.0
"""
import sys
import asyncio
import subprocess
import time
import requests
import json
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.append('/opt/bgp-monitor')

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

async def test_imports():
    """Testar todos os imports críticos"""
    print_header("TESTE DE IMPORTS")
    
    tests = [
        ("ASNSnapshotService", "from app.models.asn_snapshot import ASNSnapshotService"),
        ("BGPDataService", "from app.services.bgp_collector import BGPDataService"),
        ("BGPScheduler", "from app.services.scheduler import BGPScheduler"),
        ("ASN Router", "from app.api.routes.asn import router"),
        ("Monitoring Router", "from app.api.routes.monitoring import router"),
        ("FastAPI App", "from app.main import app"),
    ]
    
    passed = 0
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print_success(f"{name} importado com sucesso")
            passed += 1
        except Exception as e:
            print_error(f"{name} falhou: {e}")
    
    print_info(f"Imports: {passed}/{len(tests)} passaram")
    return passed == len(tests)

async def test_database():
    """Testar conectividade com banco de dados"""
    print_header("TESTE DE BANCO DE DADOS")
    
    try:
        from app.database.connection import db_manager
        from sqlalchemy import text
        
        await db_manager.initialize()
        print_success("Banco de dados inicializado")
        
        async with db_manager.get_session() as session:
            # Testar conectividade
            result = await session.execute(text('SELECT version();'))
            version = result.scalar()
            print_success(f"PostgreSQL conectado: {version.split(',')[0]}")
            
            # Verificar tabelas
            result = await session.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            ))
            tables = [row[0] for row in result.fetchall()]
            expected_tables = ['asn_snapshots', 'prefix_history', 'bgp_alerts', 'system_metrics']
            
            for table in expected_tables:
                if table in tables:
                    print_success(f"Tabela '{table}' encontrada")
                else:
                    print_error(f"Tabela '{table}' não encontrada")
        
        await db_manager.close()
        print_success("Conexão fechada com sucesso")
        return True
        
    except Exception as e:
        print_error(f"Erro de banco de dados: {e}")
        return False

def test_server_startup():
    """Testar inicialização do servidor"""
    print_header("TESTE DE SERVIDOR")
    
    try:
        # Iniciar servidor em background
        print_info("Iniciando servidor...")
        cmd = [
            '/opt/bgp-monitor/venv/bin/python3', '-m', 'uvicorn',
            'app.main:app', '--host', '0.0.0.0', '--port', '8000'
        ]
        
        server_process = subprocess.Popen(
            cmd,
            cwd='/opt/bgp-monitor',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguardar servidor inicializar
        time.sleep(5)
        
        # Testar se o processo está rodando
        if server_process.poll() is None:
            print_success("Servidor iniciado com sucesso")
        else:
            stdout, stderr = server_process.communicate()
            print_error(f"Servidor falhou ao iniciar: {stderr.decode()}")
            return False, None
        
        return True, server_process
        
    except Exception as e:
        print_error(f"Erro ao iniciar servidor: {e}")
        return False, None

def test_api_endpoints(base_url="http://localhost:8000"):
    """Testar endpoints da API"""
    print_header("TESTE DE ENDPOINTS")
    
    endpoints = [
        ("Health Check", "/health", "GET"),
        ("Root", "/", "GET"),
        ("BGP ASNs", "/api/v1/bgp/asns", "GET"),
        ("Documentation", "/docs", "GET"),
    ]
    
    passed = 0
    for name, endpoint, method in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print_success(f"{name} ({endpoint}): {response.status_code}")
                passed += 1
            else:
                print_error(f"{name} ({endpoint}): {response.status_code}")
        except Exception as e:
            print_error(f"{name} ({endpoint}): {e}")
    
    print_info(f"Endpoints: {passed}/{len(endpoints)} passaram")
    return passed == len(endpoints)

def test_file_structure():
    """Testar estrutura de arquivos"""
    print_header("TESTE DE ESTRUTURA DE ARQUIVOS")
    
    required_files = [
        "app/main.py",
        "app/scheduler.py",
        "app/models/database.py",
        "app/services/bgp_data_service.py",
        "app/api/bgp_historical.py",
        "requirements.txt",
        "alembic.ini",
        "docs/INSTALLATION.md",
        "docs/API.md",
        "docs/ARCHITECTURE.md",
        "docs/TROUBLESHOOTING.md",
        "install.sh",
        "aplicar-correções.sh",
    ]
    
    passed = 0
    base_path = Path("/opt/bgp-monitor")
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print_success(f"Arquivo encontrado: {file_path}")
            passed += 1
        else:
            print_error(f"Arquivo faltando: {file_path}")
    
    print_info(f"Arquivos: {passed}/{len(required_files)} encontrados")
    return passed == len(required_files)

async def main():
    """Executar todos os testes"""
    print("🚀 BGP Monitor v2.0 - Teste Final do Sistema")
    print("=" * 60)
    
    results = {}
    
    # Teste 1: Imports
    results['imports'] = await test_imports()
    
    # Teste 2: Banco de dados
    results['database'] = await test_database()
    
    # Teste 3: Estrutura de arquivos
    results['files'] = test_file_structure()
    
    # Teste 4: Servidor
    server_ok, server_process = test_server_startup()
    results['server'] = server_ok
    
    # Teste 5: API (se servidor estiver rodando)
    if server_ok:
        results['api'] = test_api_endpoints()
        
        # Parar servidor
        try:
            server_process.terminate()
            server_process.wait(timeout=10)
            print_success("Servidor parado com sucesso")
        except:
            server_process.kill()
            print_info("Servidor forçado a parar")
    else:
        results['api'] = False
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name.upper()}: {status}")
    
    print(f"\n🎯 RESULTADO: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print_success("🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print_info("O BGP Monitor v2.0 está pronto para uso.")
        return True
    else:
        print_error("⚠️  ALGUNS TESTES FALHARAM")
        print_info("Revise os erros acima antes de usar o sistema.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
