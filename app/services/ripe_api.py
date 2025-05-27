import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class RIPEStatAPI:
    """Cliente para interagir com a API do RIPE Stat"""
    
    def __init__(self):
        self.base_url = settings.ripe_base_url
        self.timeout = httpx.Timeout(30.0)
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Faz uma requisição para a API do RIPE Stat"""
        url = f"{self.base_url}/{endpoint}"
        
        if settings.ripe_api_key:
            params["api_key"] = settings.ripe_api_key
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error("RIPE API request failed", endpoint=endpoint, error=str(e))
                raise
    
    async def get_announced_prefixes(self, asn: int) -> List[Dict[str, Any]]:
        """Obtém todos os prefixos anunciados por um ASN"""
        params = {"resource": f"AS{asn}"}
        data = await self._make_request("announced-prefixes", params)
        
        if data.get("status") != "ok":
            raise Exception(f"RIPE API error: {data.get('status_code')}")
            
        return data.get("data", {}).get("prefixes", [])
    
    async def get_routing_status(self, prefix: str) -> Dict[str, Any]:
        """Verifica o status de roteamento de um prefixo"""
        params = {"resource": prefix}
        data = await self._make_request("routing-status", params)
        
        if data.get("status") != "ok":
            raise Exception(f"RIPE API error: {data.get('status_code')}")
            
        return data.get("data", {})
    
    async def get_as_path_length(self, prefix: str) -> List[Dict[str, Any]]:
        """Obtém informações do AS-PATH para um prefixo"""
        params = {"resource": prefix}
        data = await self._make_request("as-path-length", params)
        
        if data.get("status") != "ok":
            raise Exception(f"RIPE API error: {data.get('status_code')}")
            
        return data.get("data", {}).get("routes", [])
    
    async def get_asn_neighbours(self, asn: int) -> Dict[str, Any]:
        """Obtém os vizinhos BGP de um ASN"""
        params = {"resource": f"AS{asn}"}
        data = await self._make_request("asn-neighbours", params)
        
        if data.get("status") != "ok":
            raise Exception(f"RIPE API error: {data.get('status_code')}")
            
        return data.get("data", {})
    
    async def get_rir_stats_country(self, prefix: str) -> Dict[str, Any]:
        """Obtém informações de registro do prefixo"""
        params = {"resource": prefix}
        data = await self._make_request("rir-stats-country", params)
        
        if data.get("status") != "ok":
            raise Exception(f"RIPE API error: {data.get('status_code')}")
            
        return data.get("data", {})
    
    async def get_atlas_measurements(self, target: str, probe_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Obtém medições do RIPE Atlas para um alvo"""
        params = {
            "resource": target,
            "measurement_type": "ping"
        }
        
        if probe_ids:
            params["probe_ids"] = ",".join(map(str, probe_ids))
            
        data = await self._make_request("atlas-measurements", params)
        
        if data.get("status") != "ok":
            raise Exception(f"RIPE API error: {data.get('status_code')}")
            
        return data.get("data", {}).get("measurements", [])
    
    async def check_irr_validation(self, prefix: str, origin_asn: int) -> Dict[str, Any]:
        """Verifica validação IRR para um prefixo/ASN"""
        params = {
            "resource": prefix,
            "origin_asn": origin_asn
        }
        data = await self._make_request("rpki-validation", params)
        
        if data.get("status") != "ok":
            raise Exception(f"RIPE API error: {data.get('status_code')}")
            
        return data.get("data", {})


# Instância global do cliente RIPE
ripe_api = RIPEStatAPI()
