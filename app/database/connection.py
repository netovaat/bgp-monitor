"""
Database connection and session management
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, text
from typing import AsyncGenerator, Optional
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.models.database import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerenciador de conexões com o banco de dados"""
    
    def __init__(self):
        self.engine: Optional[create_async_engine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self._initialized = False
    
    async def initialize(self):
        """Inicializa a conexão com o banco de dados"""
        if self._initialized:
            return
            
        try:
            # URL de conexão para PostgreSQL
            database_url = (
                f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
                f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
            )
            
            # Criar engine assíncrono
            self.engine = create_async_engine(
                database_url,
                echo=settings.debug,  # Log SQL queries em modo debug
                pool_size=20,         # Pool de conexões para 50 ASNs
                max_overflow=30,
                pool_pre_ping=True,   # Verifica conexões antes de usar
                pool_recycle=3600,    # Recria conexões a cada hora
            )
            
            # Criar factory de sessões
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Criar tabelas se não existirem
            await self.create_tables()
            
            self._initialized = True
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def create_tables(self):
        """Cria as tabelas no banco de dados"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager para obter uma sessão do banco de dados"""
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Verifica se o banco de dados está funcionando"""
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()


# Funções de conveniência
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Obtém uma sessão do banco de dados"""
    async with db_manager.get_session() as session:
        yield session


async def init_database():
    """Inicializa o banco de dados"""
    await db_manager.initialize()


async def close_database():
    """Fecha a conexão com o banco de dados"""
    await db_manager.close()
