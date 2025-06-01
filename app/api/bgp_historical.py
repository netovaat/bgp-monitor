"""
BGP Historical Data API
Endpoints para visualizar e gerenciar dados históricos BGP
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.services.bgp_data_service import bgp_data_service
from app.services.anomaly_detector import anomaly_detector
from app.core.asn_config import asn_config_manager
from app.scheduler import bgp_scheduler

router = APIRouter(prefix="/api/v1/bgp", tags=["BGP Historical Data"])


# Modelos Pydantic
class ASNConfigRequest(BaseModel):
    asn: int
    name: Optional[str] = ""
    description: Optional[str] = ""
    monitoring_enabled: Optional[bool] = True
    alert_enabled: Optional[bool] = True
    custom_thresholds: Optional[Dict[str, Any]] = None


class BulkASNRequest(BaseModel):
    asns: List[ASNConfigRequest]


class ASNConfigResponse(BaseModel):
    asn: int
    name: str
    description: str
    monitoring_enabled: bool
    alert_enabled: bool
    custom_thresholds: Dict[str, Any]
    added_date: str


@router.get("/asns", response_model=List[ASNConfigResponse])
async def get_all_asns():
    """Lista todos os ASNs configurados para monitoramento"""
    asns = asn_config_manager.get_all_asns()
    return [
        ASNConfigResponse(**asn_config_manager.get_asn_config(asn).to_dict())
        for asn in asns
    ]


@router.post("/asns", response_model=Dict[str, str])
async def add_asn(asn_config: ASNConfigRequest):
    """Adiciona um novo ASN ao monitoramento"""
    success = asn_config_manager.add_asn(
        asn=asn_config.asn,
        name=asn_config.name,
        description=asn_config.description,
        monitoring_enabled=asn_config.monitoring_enabled,
        alert_enabled=asn_config.alert_enabled,
        custom_thresholds=asn_config.custom_thresholds
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=f"ASN {asn_config.asn} already exists")
    
    # Adicionar ao scheduler
    if asn_config.monitoring_enabled:
        bgp_scheduler.add_asn_to_monitoring(asn_config.asn)
    
    return {"message": f"ASN {asn_config.asn} added successfully"}


@router.post("/asns/bulk", response_model=Dict[str, Any])
async def add_bulk_asns(bulk_request: BulkASNRequest):
    """Adiciona múltiplos ASNs em lote"""
    asn_data = [asn.dict() for asn in bulk_request.asns]
    results = asn_config_manager.bulk_add_asns(asn_data)
    
    # Adicionar ASNs habilitados ao scheduler
    for asn_config in bulk_request.asns:
        if asn_config.monitoring_enabled:
            bgp_scheduler.add_asn_to_monitoring(asn_config.asn)
    
    return {
        "message": "Bulk operation completed",
        "results": results
    }


@router.put("/asns/{asn}", response_model=Dict[str, str])
async def update_asn(asn: int, asn_config: ASNConfigRequest):
    """Atualiza configurações de um ASN"""
    config = asn_config_manager.get_asn_config(asn)
    if not config:
        raise HTTPException(status_code=404, detail=f"ASN {asn} not found")
    
    # Verificar se monitoramento mudou
    old_monitoring = config.monitoring_enabled
    
    success = asn_config_manager.update_asn(
        asn=asn,
        name=asn_config.name,
        description=asn_config.description,
        monitoring_enabled=asn_config.monitoring_enabled,
        alert_enabled=asn_config.alert_enabled,
        custom_thresholds=asn_config.custom_thresholds
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update ASN")
    
    # Atualizar scheduler
    if old_monitoring and not asn_config.monitoring_enabled:
        bgp_scheduler.remove_asn_from_monitoring(asn)
    elif not old_monitoring and asn_config.monitoring_enabled:
        bgp_scheduler.add_asn_to_monitoring(asn)
    
    return {"message": f"ASN {asn} updated successfully"}


@router.delete("/asns/{asn}", response_model=Dict[str, str])
async def remove_asn(asn: int):
    """Remove um ASN do monitoramento"""
    success = asn_config_manager.remove_asn(asn)
    if not success:
        raise HTTPException(status_code=404, detail=f"ASN {asn} not found")
    
    # Remover do scheduler
    bgp_scheduler.remove_asn_from_monitoring(asn)
    
    return {"message": f"ASN {asn} removed successfully"}


@router.get("/asns/{asn}/statistics")
async def get_asn_statistics(
    asn: int,
    days_back: int = Query(30, ge=1, le=365, description="Days of historical data")
):
    """Obtém estatísticas históricas de um ASN"""
    config = asn_config_manager.get_asn_config(asn)
    if not config:
        raise HTTPException(status_code=404, detail=f"ASN {asn} not found in configuration")
    
    stats = await bgp_data_service.get_asn_statistics(asn, days_back)
    
    if 'error' in stats:
        raise HTTPException(status_code=404, detail=stats['error'])
    
    return stats


@router.get("/asns/{asn}/changes")
async def get_asn_changes(
    asn: int,
    hours_back: int = Query(24, ge=1, le=168, description="Hours to look back")
):
    """Obtém histórico de alterações de prefixos de um ASN"""
    config = asn_config_manager.get_asn_config(asn)
    if not config:
        raise HTTPException(status_code=404, detail=f"ASN {asn} not found in configuration")
    
    changes = await bgp_data_service.detect_prefix_changes(asn, hours_back)
    
    return {
        "asn": asn,
        "hours_back": hours_back,
        "total_changes": len(changes),
        "changes": changes
    }


@router.get("/asns/{asn}/anomalies")
async def get_asn_anomalies(
    asn: int,
    sensitivity: str = Query("medium", regex="^(low|medium|high)$")
):
    """Detecta anomalias em um ASN específico"""
    config = asn_config_manager.get_asn_config(asn)
    if not config:
        raise HTTPException(status_code=404, detail=f"ASN {asn} not found in configuration")
    
    anomalies = await anomaly_detector.detect_sudden_changes(asn, sensitivity)
    
    return {
        "asn": asn,
        "sensitivity": sensitivity,
        "total_anomalies": len(anomalies),
        "anomalies": anomalies
    }


@router.get("/asns/{asn}/instability")
async def get_asn_instability(
    asn: int,
    window_hours: int = Query(6, ge=1, le=48, description="Analysis window in hours")
):
    """Analisa instabilidade de roteamento de um ASN"""
    config = asn_config_manager.get_asn_config(asn)
    if not config:
        raise HTTPException(status_code=404, detail=f"ASN {asn} not found in configuration")
    
    instability = await anomaly_detector.detect_routing_instability(asn, window_hours)
    
    return instability


@router.get("/overview")
async def get_monitoring_overview(
    limit: int = Query(10, ge=1, le=50, description="Limit number of ASNs in detailed view"),
    days_back: int = Query(7, ge=1, le=30, description="Days of historical data for statistics"),
    include_inactive: bool = Query(False, description="Include disabled ASNs in overview")
):
    """
    Obtém visão geral do monitoramento de todos os ASNs
    
    Parâmetros opcionais:
    - limit: Número máximo de ASNs para análise detalhada (padrão: 10)
    - days_back: Dias de dados históricos para estatísticas (padrão: 7)
    - include_inactive: Incluir ASNs desabilitados na visão geral (padrão: False)
    """
    if include_inactive:
        enabled_asns = asn_config_manager.get_all_asns()
    else:
        enabled_asns = asn_config_manager.get_enabled_asns()
    
    if not enabled_asns:
        return {
            "message": "No ASNs configured for monitoring",
            "total_asns": 0,
            "enabled_asns": 0,
            "asns": []
        }
    
    # Gerar relatório consolidado
    anomaly_report = await anomaly_detector.monitor_multiple_asns(enabled_asns)
    
    # Estatísticas por ASN
    asn_summaries = []
    for asn in enabled_asns[:10]:  # Limitar a 10 para performance
        try:
            stats = await bgp_data_service.get_asn_statistics(asn, days_back=7)
            instability = await anomaly_detector.detect_routing_instability(asn, window_hours=24)
            
            if 'error' not in stats:
                asn_summaries.append({
                    "asn": asn,
                    "name": asn_config_manager.get_asn_config(asn).name,
                    "current_prefixes": stats.get('prefix_statistics', {}).get('current_count', 0),
                    "stability_score": stats.get('stability_score', 0),
                    "instability_status": instability.get('status', 'unknown')
                })
        except Exception as e:
            continue
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_asns": len(asn_config_manager.get_all_asns()),
        "enabled_asns": len(enabled_asns),
        "monitoring_active": len(bgp_scheduler.get_monitored_asns()),
        "anomaly_summary": anomaly_report['summary'],
        "asn_summaries": asn_summaries
    }


@router.get("/config/export")
async def export_configuration():
    """Exporta configuração completa para backup"""
    return asn_config_manager.export_config()


@router.post("/config/import")
async def import_configuration(
    config_data: Dict[str, Any],
    merge: bool = Query(True, description="Merge with existing config or replace")
):
    """Importa configuração de backup"""
    results = asn_config_manager.import_config(config_data, merge)
    
    # Atualizar scheduler com novos ASNs
    enabled_asns = asn_config_manager.get_enabled_asns()
    current_monitored = set(bgp_scheduler.get_monitored_asns())
    
    for asn in enabled_asns:
        if asn not in current_monitored:
            bgp_scheduler.add_asn_to_monitoring(asn)
    
    return {
        "message": "Configuration imported successfully",
        "results": results
    }


@router.post("/collect/force")
async def force_collection_all():
    """Força coleta manual de dados para todos os ASNs ativos"""
    enabled_asns = asn_config_manager.get_enabled_asns()
    
    if not enabled_asns:
        raise HTTPException(status_code=404, detail="No ASNs enabled for monitoring")
    
    results = []
    failed_asns = []
    
    for asn in enabled_asns:
        try:
            result = await bgp_data_service.collect_asn_snapshot(asn)
            if result:
                results.append({
                    "asn": asn,
                    "status": "success",
                    "snapshot": result
                })
            else:
                failed_asns.append(asn)
        except Exception as e:
            failed_asns.append(asn)
            logger.error(f"Failed to collect data for AS{asn}: {str(e)}")
    
    return {
        "message": f"Force collection completed for {len(results)} ASNs",
        "total_asns": len(enabled_asns),
        "successful": len(results),
        "failed": len(failed_asns),
        "failed_asns": failed_asns,
        "results": results
    }


@router.post("/asns/{asn}/collect")
async def manual_collection(asn: int):
    """Força coleta manual de dados para um ASN específico"""
    config = asn_config_manager.get_asn_config(asn)
    if not config:
        raise HTTPException(status_code=404, detail=f"ASN {asn} not found in configuration")
    
    result = await bgp_data_service.collect_asn_snapshot(asn)
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to collect data")
    
    return {
        "message": f"Data collected successfully for AS{asn}",
        "snapshot": result
    }
