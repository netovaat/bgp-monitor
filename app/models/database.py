"""
Database models for BGP monitoring data
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, List, Optional

Base = declarative_base()


class ASNSnapshot(Base):
    """
    Snapshot histórico de um ASN em um momento específico
    """
    __tablename__ = "asn_snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asn = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    # Dados dos prefixos anunciados
    announced_prefixes = Column(JSON, nullable=False)  # Lista de prefixos
    prefix_count = Column(Integer, nullable=False)
    
    # Dados de peers/upstreams
    peer_data = Column(JSON, nullable=True)
    upstream_count = Column(Integer, nullable=True)
    
    # Status geral
    is_announcing = Column(Boolean, nullable=False, default=True)
    
    # Metadata
    data_source = Column(String(50), nullable=False, default="ripe")
    raw_data = Column(JSON, nullable=True)  # Dados brutos da API
    
    # Índices compostos para queries eficientes
    __table_args__ = (
        Index('idx_asn_timestamp', 'asn', 'timestamp'),
        Index('idx_timestamp_asn', 'timestamp', 'asn'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'asn': self.asn,
            'timestamp': self.timestamp.isoformat(),
            'announced_prefixes': self.announced_prefixes,
            'prefix_count': self.prefix_count,
            'peer_data': self.peer_data,
            'upstream_count': self.upstream_count,
            'is_announcing': self.is_announcing,
            'data_source': self.data_source
        }


class PrefixHistory(Base):
    """
    Histórico detalhado de prefixos específicos
    """
    __tablename__ = "prefix_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prefix = Column(String(43), nullable=False, index=True)  # IPv6 pode ter até 43 chars
    asn = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    # Status do prefixo
    is_announced = Column(Boolean, nullable=False)
    origin_asn = Column(Integer, nullable=True)
    
    # Dados de roteamento
    routing_status = Column(JSON, nullable=True)
    as_path = Column(JSON, nullable=True)  # Lista de ASNs no caminho
    
    # Origem dos dados
    data_source = Column(String(50), nullable=False, default="ripe")
    
    __table_args__ = (
        Index('idx_prefix_timestamp', 'prefix', 'timestamp'),
        Index('idx_asn_prefix_timestamp', 'asn', 'prefix', 'timestamp'),
    )


class BGPAlert(Base):
    """
    Histórico de alertas gerados pelo sistema
    """
    __tablename__ = "bgp_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asn = Column(Integer, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # 'prefix_withdrawal', 'new_prefix', etc.
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    # Conteúdo do alerta
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="info")  # info, warning, critical
    
    # Dados relacionados
    prefix = Column(String(43), nullable=True, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    
    # Status
    acknowledged = Column(Boolean, nullable=False, default=False)
    resolved = Column(Boolean, nullable=False, default=False)
    
    __table_args__ = (
        Index('idx_asn_alert_type_timestamp', 'asn', 'alert_type', 'timestamp'),
    )


class SystemMetrics(Base):
    """
    Métricas do sistema para monitoramento de performance
    """
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    # Métricas de API
    api_calls_count = Column(Integer, nullable=False, default=0)
    api_errors_count = Column(Integer, nullable=False, default=0)
    api_response_time_ms = Column(Integer, nullable=True)
    
    # Métricas de processamento
    asns_processed = Column(Integer, nullable=False, default=0)
    prefixes_processed = Column(Integer, nullable=False, default=0)
    alerts_generated = Column(Integer, nullable=False, default=0)
    
    # Dados detalhados
    metrics_data = Column(JSON, nullable=True)
