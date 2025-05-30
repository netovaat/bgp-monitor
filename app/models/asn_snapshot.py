"""
ASN Snapshot model - Wrapper and utilities for ASN snapshot data
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .database import ASNSnapshot


class ASNSnapshotService:
    """
    Service class for handling ASN snapshot operations
    """
    
    @staticmethod
    def create_snapshot(asn: int, announced_prefixes: List[str], 
                       peer_data: Optional[Dict] = None, 
                       data_source: str = "ripe") -> Dict[str, Any]:
        """
        Create a new ASN snapshot
        """
        return {
            'asn': asn,
            'timestamp': datetime.utcnow(),
            'announced_prefixes': announced_prefixes,
            'prefix_count': len(announced_prefixes),
            'peer_data': peer_data,
            'upstream_count': len(peer_data.get('upstreams', [])) if peer_data else 0,
            'is_announcing': len(announced_prefixes) > 0,
            'data_source': data_source
        }
    
    @staticmethod
    def calculate_changes(old_snapshot: ASNSnapshot, new_snapshot: ASNSnapshot) -> Dict[str, Any]:
        """
        Calculate changes between two snapshots
        """
        old_prefixes = set(old_snapshot.announced_prefixes)
        new_prefixes = set(new_snapshot.announced_prefixes)
        
        return {
            'asn': new_snapshot.asn,
            'timestamp': new_snapshot.timestamp,
            'added_prefixes': list(new_prefixes - old_prefixes),
            'removed_prefixes': list(old_prefixes - new_prefixes),
            'prefix_count_change': new_snapshot.prefix_count - old_snapshot.prefix_count,
            'upstream_count_change': (new_snapshot.upstream_count or 0) - (old_snapshot.upstream_count or 0)
        }
    
    @staticmethod
    def detect_anomalies(snapshots: List[ASNSnapshot], threshold: float = 0.2) -> List[Dict[str, Any]]:
        """
        Detect anomalies in ASN snapshots based on prefix count changes
        """
        anomalies = []
        
        for i in range(1, len(snapshots)):
            current = snapshots[i]
            previous = snapshots[i-1]
            
            if previous.prefix_count == 0:
                continue
                
            change_ratio = abs(current.prefix_count - previous.prefix_count) / previous.prefix_count
            
            if change_ratio > threshold:
                anomalies.append({
                    'asn': current.asn,
                    'timestamp': current.timestamp,
                    'type': 'prefix_count_anomaly',
                    'change_ratio': change_ratio,
                    'previous_count': previous.prefix_count,
                    'current_count': current.prefix_count,
                    'severity': 'high' if change_ratio > 0.5 else 'medium'
                })
        
        return anomalies
