"""
BGP Collector - Alias for BGP Data Service
"""
# This module is an alias for bgp_data_service for backward compatibility
from .bgp_data_service import BGPDataService, bgp_data_service

# Export the same interface
__all__ = ['BGPDataService', 'bgp_data_service']
