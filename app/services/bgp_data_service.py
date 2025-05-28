"""
BGP Data Service - Gerencia o armazenamento e análise de dados BGP históricos
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.database import ASNSnapshot, PrefixHistory, BGPAlert, SystemMetrics
from app.database.connection import db_manager
from app.services.ripe_api import RIPEStatAPI

logger = logging.getLogger(__name__)


class BGPDataService:
    """Serviço para gerenciar dados BGP históricos"""
    
    def __init__(self):
        self.ripe_api = RIPEStatAPI()
        self.last_collection_time = {}  # Cache para rate limiting por ASN
    
    async def collect_asn_snapshot(self, asn: int) -> Optional[Dict[str, Any]]:
        """
        Coleta um snapshot atual do ASN e armazena no banco de dados
        Implementa rate limiting inteligente
        """
        current_time = datetime.now()
        
        # Rate limiting: mínimo 30 segundos entre coletas do mesmo ASN
        if asn in self.last_collection_time:
            time_diff = (current_time - self.last_collection_time[asn]).total_seconds()
            if time_diff < 30:
                logger.debug(f"Rate limiting: skipping ASN {asn} (last collection {time_diff}s ago)")
                return None
        
        try:
            # Coletar dados da API do RIPE
            prefixes_data = await self.ripe_api.get_announced_prefixes(asn)
            
            # Processar dados
            announced_prefixes = [p.get('prefix') for p in prefixes_data if p.get('prefix')]
            prefix_count = len(announced_prefixes)
            
            # Criar snapshot
            snapshot_data = {
                'asn': asn,
                'timestamp': current_time,
                'announced_prefixes': announced_prefixes,
                'prefix_count': prefix_count,
                'is_announcing': prefix_count > 0,
                'data_source': 'ripe',
                'raw_data': prefixes_data
            }
            
            # Armazenar no banco de dados
            async with db_manager.get_session() as session:
                snapshot = ASNSnapshot(**snapshot_data)
                session.add(snapshot)
                await session.commit()
                
                logger.info(f"Collected snapshot for AS{asn}: {prefix_count} prefixes")
                
                # Atualizar cache de rate limiting
                self.last_collection_time[asn] = current_time
                
                return snapshot.to_dict()
                
        except Exception as e:
            logger.error(f"Failed to collect snapshot for AS{asn}: {e}")
            return None
    
    async def collect_multiple_asns(self, asn_list: List[int], batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Coleta snapshots de múltiplos ASNs com rate limiting otimizado
        """
        results = []
        
        # Processar em batches para não sobrecarregar a API
        for i in range(0, len(asn_list), batch_size):
            batch = asn_list[i:i + batch_size]
            
            # Criar tasks para processamento paralelo (limitado por batch)
            tasks = [self.collect_asn_snapshot(asn) for asn in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrar resultados válidos
            for result in batch_results:
                if isinstance(result, dict):
                    results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Batch collection error: {result}")
            
            # Delay entre batches para respeitar rate limits
            if i + batch_size < len(asn_list):
                await asyncio.sleep(2)  # 2 segundos entre batches
        
        return results
    
    async def detect_prefix_changes(self, asn: int, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Detecta alterações bruscas nos prefixos de um ASN nas últimas N horas
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        async with db_manager.get_session() as session:
            # Buscar snapshots recentes
            query = select(ASNSnapshot).where(
                and_(
                    ASNSnapshot.asn == asn,
                    ASNSnapshot.timestamp >= cutoff_time
                )
            ).order_by(desc(ASNSnapshot.timestamp))
            
            result = await session.execute(query)
            snapshots = result.scalars().all()
            
            if len(snapshots) < 2:
                return []
            
            changes = []
            
            # Comparar snapshots consecutivos
            for i in range(len(snapshots) - 1):
                current = snapshots[i]
                previous = snapshots[i + 1]
                
                current_prefixes = set(current.announced_prefixes)
                previous_prefixes = set(previous.announced_prefixes)
                
                # Detectar alterações
                added = current_prefixes - previous_prefixes
                removed = previous_prefixes - current_prefixes
                
                if added or removed:
                    change = {
                        'timestamp': current.timestamp.isoformat(),
                        'asn': asn,
                        'added_prefixes': list(added),
                        'removed_prefixes': list(removed),
                        'net_change': len(added) - len(removed),
                        'total_before': len(previous_prefixes),
                        'total_after': len(current_prefixes)
                    }
                    changes.append(change)
            
            return changes
    
    async def get_asn_statistics(self, asn: int, days_back: int = 30) -> Dict[str, Any]:
        """
        Gera estatísticas históricas de um ASN
        """
        cutoff_time = datetime.now() - timedelta(days=days_back)
        
        async with db_manager.get_session() as session:
            # Buscar dados históricos
            query = select(ASNSnapshot).where(
                and_(
                    ASNSnapshot.asn == asn,
                    ASNSnapshot.timestamp >= cutoff_time
                )
            ).order_by(ASNSnapshot.timestamp)
            
            result = await session.execute(query)
            snapshots = result.scalars().all()
            
            if not snapshots:
                return {'error': 'No data available'}
            
            # Calcular estatísticas
            prefix_counts = [s.prefix_count for s in snapshots]
            
            stats = {
                'asn': asn,
                'period_days': days_back,
                'total_snapshots': len(snapshots),
                'first_snapshot': snapshots[0].timestamp.isoformat(),
                'last_snapshot': snapshots[-1].timestamp.isoformat(),
                'prefix_statistics': {
                    'current_count': prefix_counts[-1],
                    'min_count': min(prefix_counts),
                    'max_count': max(prefix_counts),
                    'avg_count': sum(prefix_counts) / len(prefix_counts),
                    'variance': self._calculate_variance(prefix_counts)
                },
                'stability_score': self._calculate_stability_score(prefix_counts)
            }
            
            return stats
    
    def _calculate_variance(self, values: List[int]) -> float:
        """Calcula a variância dos valores"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _calculate_stability_score(self, prefix_counts: List[int]) -> float:
        """
        Calcula um score de estabilidade (0-100)
        100 = muito estável, 0 = muito instável
        """
        if len(prefix_counts) < 2:
            return 100.0
            
        variance = self._calculate_variance(prefix_counts)
        mean = sum(prefix_counts) / len(prefix_counts)
        
        if mean == 0:
            return 0.0
            
        # Coeficiente de variação normalizado
        cv = (variance ** 0.5) / mean
        
        # Converter para score 0-100 (quanto menor CV, maior estabilidade)
        stability = max(0, 100 - (cv * 100))
        return round(stability, 2)
    
    async def cleanup_old_data(self, keep_days: int = 365):
        """
        Remove dados antigos para manter o banco de dados otimizado
        Mantém dados dos últimos N dias
        """
        cutoff_time = datetime.now() - timedelta(days=keep_days)
        
        async with db_manager.get_session() as session:
            # Limpar snapshots antigos
            deleted_snapshots = await session.execute(
                ASNSnapshot.__table__.delete().where(
                    ASNSnapshot.timestamp < cutoff_time
                )
            )
            
            # Limpar histórico de prefixos antigos
            deleted_prefix_history = await session.execute(
                PrefixHistory.__table__.delete().where(
                    PrefixHistory.timestamp < cutoff_time
                )
            )
            
            # Limpar alertas antigos (manter apenas últimos 90 dias)
            alert_cutoff = datetime.now() - timedelta(days=90)
            deleted_alerts = await session.execute(
                BGPAlert.__table__.delete().where(
                    BGPAlert.timestamp < alert_cutoff
                )
            )
            
            await session.commit()
            
            logger.info(
                f"Cleanup completed: {deleted_snapshots.rowcount} snapshots, "
                f"{deleted_prefix_history.rowcount} prefix history, "
                f"{deleted_alerts.rowcount} alerts deleted"
            )


# Instância global do serviço
bgp_data_service = BGPDataService()
