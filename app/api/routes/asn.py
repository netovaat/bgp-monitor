"""
ASN Routes - Alias for BGP Historical API
"""
# This module is an alias for the ASN routes in bgp_historical
from ..bgp_historical import router

# Export the router
asn_router = router

__all__ = ['asn_router', 'router']
