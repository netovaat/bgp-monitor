"""
BGP Monitor v2.1.0 - Database Module

Módulo de banco de dados do BGP Monitor v2.1.0 com:
- Gerenciamento de conexões PostgreSQL assíncronas
- Pool de conexões otimizado
- Session management
- Health checks de conectividade

Utiliza SQLAlchemy 2.0 com async/await para performance
otimizada com pool de até 20 conexões simultâneas.
"""

# Importar e exportar principais funções de conexão
from .connection import (
    DatabaseManager,
    db_manager,
    get_db_session,
    init_database,
    close_database
)

# Alias para compatibilidade
get_db = get_db_session

__all__ = [
    'DatabaseManager',
    'db_manager', 
    'get_db_session',
    'get_db',  # Alias
    'init_database',
    'close_database'
]

__version__ = "2.0.0"
# Compatibility function for get_db
def get_db():
    """
    Compatibility function for dependency injection.
    Returns database session generator.
    """
    from app.database.connection import db_manager
    return db_manager.get_session()

# Additional compatibility
def get_db_session():
    """Alternative name for get_db"""
    return get_db()
