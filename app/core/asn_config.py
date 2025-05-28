"""
ASN Configuration Manager
Gerencia a lista de ASNs para monitoramento histórico
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ASNConfig:
    """Configuração para um ASN específico"""
    
    def __init__(self, asn: int, name: str = "", description: str = "", 
                 monitoring_enabled: bool = True, alert_enabled: bool = True,
                 custom_thresholds: Optional[Dict[str, Any]] = None):
        self.asn = asn
        self.name = name or f"AS{asn}"
        self.description = description
        self.monitoring_enabled = monitoring_enabled
        self.alert_enabled = alert_enabled
        self.custom_thresholds = custom_thresholds or {}
        self.added_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'asn': self.asn,
            'name': self.name,
            'description': self.description,
            'monitoring_enabled': self.monitoring_enabled,
            'alert_enabled': self.alert_enabled,
            'custom_thresholds': self.custom_thresholds,
            'added_date': self.added_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ASNConfig':
        config = cls(
            asn=data['asn'],
            name=data.get('name', ''),
            description=data.get('description', ''),
            monitoring_enabled=data.get('monitoring_enabled', True),
            alert_enabled=data.get('alert_enabled', True),
            custom_thresholds=data.get('custom_thresholds', {})
        )
        config.added_date = data.get('added_date', datetime.now().isoformat())
        return config


class ASNConfigManager:
    """Gerenciador de configurações de ASNs"""
    
    def __init__(self, config_file: str = "asn_config.json"):
        self.config_file = config_file
        self.asn_configs: Dict[int, ASNConfig] = {}
        self.load_config()
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                self.asn_configs = {}
                for asn_data in data.get('asns', []):
                    config = ASNConfig.from_dict(asn_data)
                    self.asn_configs[config.asn] = config
                
                logger.info(f"Loaded {len(self.asn_configs)} ASN configurations")
                
            except Exception as e:
                logger.error(f"Failed to load ASN config: {e}")
                self.asn_configs = {}
        else:
            logger.info("No ASN config file found, starting with empty configuration")
            self.asn_configs = {}
    
    def save_config(self):
        """Salva configurações no arquivo"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'asns': [config.to_dict() for config in self.asn_configs.values()]
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.asn_configs)} ASN configurations")
            
        except Exception as e:
            logger.error(f"Failed to save ASN config: {e}")
    
    def add_asn(self, asn: int, name: str = "", description: str = "", 
                monitoring_enabled: bool = True, alert_enabled: bool = True,
                custom_thresholds: Optional[Dict[str, Any]] = None) -> bool:
        """Adiciona um ASN ao monitoramento"""
        if asn in self.asn_configs:
            logger.warning(f"ASN {asn} already exists in configuration")
            return False
        
        config = ASNConfig(asn, name, description, monitoring_enabled, 
                          alert_enabled, custom_thresholds)
        self.asn_configs[asn] = config
        self.save_config()
        
        logger.info(f"Added AS{asn} ({name}) to monitoring configuration")
        return True
    
    def remove_asn(self, asn: int) -> bool:
        """Remove um ASN do monitoramento"""
        if asn not in self.asn_configs:
            logger.warning(f"ASN {asn} not found in configuration")
            return False
        
        del self.asn_configs[asn]
        self.save_config()
        
        logger.info(f"Removed AS{asn} from monitoring configuration")
        return True
    
    def update_asn(self, asn: int, **kwargs) -> bool:
        """Atualiza configurações de um ASN"""
        if asn not in self.asn_configs:
            logger.warning(f"ASN {asn} not found in configuration")
            return False
        
        config = self.asn_configs[asn]
        
        # Atualizar campos permitidos
        allowed_fields = ['name', 'description', 'monitoring_enabled', 'alert_enabled', 'custom_thresholds']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(config, field, value)
        
        self.save_config()
        logger.info(f"Updated AS{asn} configuration")
        return True
    
    def get_asn_config(self, asn: int) -> Optional[ASNConfig]:
        """Obtém configuração de um ASN específico"""
        return self.asn_configs.get(asn)
    
    def get_all_asns(self) -> List[int]:
        """Obtém lista de todos os ASNs configurados"""
        return list(self.asn_configs.keys())
    
    def get_enabled_asns(self) -> List[int]:
        """Obtém lista de ASNs com monitoramento habilitado"""
        return [asn for asn, config in self.asn_configs.items() 
                if config.monitoring_enabled]
    
    def get_alert_enabled_asns(self) -> List[int]:
        """Obtém lista de ASNs com alertas habilitados"""
        return [asn for asn, config in self.asn_configs.items() 
                if config.alert_enabled]
    
    def bulk_add_asns(self, asn_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Adiciona múltiplos ASNs em lote"""
        results = {'added': 0, 'skipped': 0, 'errors': 0}
        
        for asn_data in asn_list:
            try:
                asn = asn_data.get('asn')
                if not asn:
                    results['errors'] += 1
                    continue
                
                if asn in self.asn_configs:
                    results['skipped'] += 1
                    continue
                
                success = self.add_asn(
                    asn=asn,
                    name=asn_data.get('name', ''),
                    description=asn_data.get('description', ''),
                    monitoring_enabled=asn_data.get('monitoring_enabled', True),
                    alert_enabled=asn_data.get('alert_enabled', True),
                    custom_thresholds=asn_data.get('custom_thresholds')
                )
                
                if success:
                    results['added'] += 1
                else:
                    results['errors'] += 1
                    
            except Exception as e:
                logger.error(f"Error adding ASN from bulk data: {e}")
                results['errors'] += 1
        
        # Salvar apenas uma vez no final
        if results['added'] > 0:
            self.save_config()
        
        return results
    
    def export_config(self) -> Dict[str, Any]:
        """Exporta configuração completa para backup"""
        return {
            'exported_at': datetime.now().isoformat(),
            'total_asns': len(self.asn_configs),
            'asns': [config.to_dict() for config in self.asn_configs.values()]
        }
    
    def import_config(self, config_data: Dict[str, Any], merge: bool = True) -> Dict[str, int]:
        """Importa configuração de backup"""
        results = {'imported': 0, 'skipped': 0, 'errors': 0}
        
        if not merge:
            # Limpar configurações existentes
            self.asn_configs = {}
        
        for asn_data in config_data.get('asns', []):
            try:
                config = ASNConfig.from_dict(asn_data)
                
                if merge and config.asn in self.asn_configs:
                    results['skipped'] += 1
                    continue
                
                self.asn_configs[config.asn] = config
                results['imported'] += 1
                
            except Exception as e:
                logger.error(f"Error importing ASN config: {e}")
                results['errors'] += 1
        
        if results['imported'] > 0:
            self.save_config()
        
        return results


# Instância global do gerenciador
asn_config_manager = ASNConfigManager()
