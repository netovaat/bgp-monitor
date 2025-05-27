import asyncio
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from app.services.telegram import telegram_service
from app.core.config import settings
from app.utils.metrics import metrics

logger = structlog.get_logger()


class IRRValidationService:
    """Serviço para validação de prefixos em bancos IRR"""
    
    def __init__(self):
        self.irr_databases = [
            "RIPE", "RADB", "APNIC", "AFRINIC", "ARIN", "LACNIC"
        ]
        self.timeout = httpx.Timeout(30.0)
        self.validation_cache = {}  # Cache de validações recentes
        self.last_alerts = {}  # Cache de alertas
        
    async def validate_prefix_irr(self, prefix: str, origin_asn: int) -> Dict[str, Any]:
        """Valida um prefixo específico contra bancos IRR"""
        validation_results = {}
        
        try:
            logger.info("Starting IRR validation", prefix=prefix, origin_asn=origin_asn)
            
            for irr_db in self.irr_databases:
                result = await self._check_irr_database(prefix, origin_asn, irr_db)
                validation_results[irr_db] = result
                
            # Armazena resultado no cache
            cache_key = f"{prefix}:{origin_asn}"
            self.validation_cache[cache_key] = {
                "results": validation_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Verifica se há inconsistências
            await self._check_irr_inconsistencies(prefix, origin_asn, validation_results)
            
            return validation_results
            
        except Exception as e:
            logger.error("IRR validation failed", prefix=prefix, origin_asn=origin_asn, error=str(e))
            return {}
    
    async def validate_all_monitored_prefixes(self, monitored_prefixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida todos os prefixos monitorados"""
        alerts = []
        
        if not monitored_prefixes:
            logger.info("No prefixes to validate")
            return alerts
            
        logger.info("Validating monitored prefixes", count=len(monitored_prefixes))
        
        for prefix_data in monitored_prefixes:
            if not prefix_data.get("is_active"):
                continue
                
            prefix = prefix_data["prefix"]
            origin_asn = prefix_data["asn"]
            
            try:
                validation_results = await self.validate_prefix_irr(prefix, origin_asn)
                
                # Analisa resultados e cria alertas se necessário
                alert = await self._analyze_validation_results(prefix, origin_asn, validation_results)
                if alert:
                    alerts.append(alert)
                    
            except Exception as e:
                logger.error("Error validating prefix", prefix=prefix, error=str(e))
                
        return alerts
    
    async def _check_irr_database(self, prefix: str, origin_asn: int, irr_db: str) -> Dict[str, Any]:
        """Verifica um prefixo específico em um banco IRR"""
        try:
            # Simulação de verificação IRR - em produção usaria APIs específicas de cada IRR
            logger.debug("Checking IRR database", prefix=prefix, origin_asn=origin_asn, irr_db=irr_db)
            
            # Para fins de demonstração, retorna resultados simulados
            # Em produção, isso faria consultas reais aos bancos IRR
            
            simulated_result = {
                "valid": True,  # Maioria dos prefixos são válidos
                "database": irr_db,
                "route_object": f"route: {prefix}\\norigin: AS{origin_asn}",
                "last_modified": "2024-01-01",
                "maintainer": "MAINT-EXAMPLE"
            }
            
            # Simula alguns casos de invalidez para demonstração
            if irr_db == "RADB" and origin_asn > 65000:
                simulated_result["valid"] = False
                simulated_result["error"] = "Route object not found"
                
            return simulated_result
            
        except Exception as e:
            logger.error("IRR database check failed", irr_db=irr_db, error=str(e))
            return {
                "valid": False,
                "database": irr_db,
                "error": str(e)
            }
    
    async def _check_irr_inconsistencies(self, prefix: str, origin_asn: int, validation_results: Dict[str, Any]):
        """Verifica inconsistências entre bancos IRR"""
        valid_count = sum(1 for result in validation_results.values() if result.get("valid"))
        total_count = len(validation_results)
        
        if valid_count < total_count * 0.5:  # Menos de 50% são válidos
            alert_data = {
                "alert_type": "irr_inconsistency",
                "severity": "warning",
                "title": f"Inconsistência IRR para {prefix}",
                "message": f"⚠️ Prefixo {prefix} (AS{origin_asn}) tem validação inconsistente em bancos IRR ({valid_count}/{total_count} válidos)",
                "details": {
                    "prefix": prefix,
                    "origin_asn": origin_asn,
                    "valid_databases": valid_count,
                    "total_databases": total_count,
                    "validation_results": validation_results,
                    "check_time": datetime.utcnow().isoformat()
                }
            }
            
            if not self._has_recent_alert("irr_inconsistency", f"{prefix}:{origin_asn}"):
                self._record_alert("irr_inconsistency", f"{prefix}:{origin_asn}")
                await telegram_service.send_alert(alert_data)
                metrics.increment_alert_counter("irr_inconsistency")
                
                logger.warning("IRR inconsistency detected", 
                             prefix=prefix, origin_asn=origin_asn, 
                             valid_count=valid_count, total_count=total_count)
    
    async def _analyze_validation_results(self, prefix: str, origin_asn: int, validation_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analisa resultados de validação e retorna alerta se necessário"""
        if not validation_results:
            return None
            
        valid_dbs = [db for db, result in validation_results.items() if result.get("valid")]
        invalid_dbs = [db for db, result in validation_results.items() if not result.get("valid")]
        
        # Se nenhum banco tem o prefixo como válido
        if not valid_dbs:
            return {
                "alert_type": "irr_invalid",
                "severity": "critical",
                "title": f"Prefixo {prefix} inválido em todos os bancos IRR",
                "message": f"🚨 Prefixo {prefix} (AS{origin_asn}) é inválido em todos os bancos IRR verificados",
                "details": {
                    "prefix": prefix,
                    "origin_asn": origin_asn,
                    "invalid_databases": invalid_dbs,
                    "validation_results": validation_results,
                    "check_time": datetime.utcnow().isoformat()
                }
            }
        
        return None
    
    def _has_recent_alert(self, alert_type: str, identifier: str) -> bool:
        """Verifica se já existe alerta recente para evitar spam"""
        key = f"{alert_type}:{identifier}"
        last_alert = self.last_alerts.get(key)
        
        if last_alert:
            time_diff = datetime.utcnow() - datetime.fromisoformat(last_alert)
            return time_diff < timedelta(hours=6)  # IRR checks são menos frequentes
            
        return False
    
    def _record_alert(self, alert_type: str, identifier: str):
        """Registra um alerta para controle de frequência"""
        key = f"{alert_type}:{identifier}"
        self.last_alerts[key] = datetime.utcnow().isoformat()
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Retorna resumo das validações realizadas"""
        total_validations = len(self.validation_cache)
        
        if total_validations == 0:
            return {"total_validations": 0, "last_check": None}
            
        # Conta validações por resultado
        valid_count = 0
        invalid_count = 0
        
        for validation in self.validation_cache.values():
            results = validation["results"]
            if any(result.get("valid") for result in results.values()):
                valid_count += 1
            else:
                invalid_count += 1
                
        return {
            "total_validations": total_validations,
            "valid_prefixes": valid_count,
            "invalid_prefixes": invalid_count,
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def manual_validation(self, prefix: str, origin_asn: int) -> Dict[str, Any]:
        """Executa validação manual de um prefixo específico"""
        logger.info("Manual IRR validation requested", prefix=prefix, origin_asn=origin_asn)
        
        validation_results = await self.validate_prefix_irr(prefix, origin_asn)
        
        return {
            "prefix": prefix,
            "origin_asn": origin_asn,
            "validation_results": validation_results,
            "summary": self._summarize_validation(validation_results),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _summarize_validation(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Cria resumo da validação"""
        if not validation_results:
            return {"status": "error", "message": "No validation results"}
            
        valid_dbs = [db for db, result in validation_results.items() if result.get("valid")]
        total_dbs = len(validation_results)
        
        if len(valid_dbs) == total_dbs:
            status = "valid"
            message = "Válido em todos os bancos IRR"
        elif len(valid_dbs) > total_dbs / 2:
            status = "mostly_valid"
            message = f"Válido em {len(valid_dbs)}/{total_dbs} bancos IRR"
        elif len(valid_dbs) > 0:
            status = "partially_valid"
            message = f"Válido em apenas {len(valid_dbs)}/{total_dbs} bancos IRR"
        else:
            status = "invalid"
            message = "Inválido em todos os bancos IRR"
            
        return {
            "status": status,
            "message": message,
            "valid_databases": valid_dbs,
            "total_databases": total_dbs
        }


# Instância global do validador
irr_validator = IRRValidationService()
