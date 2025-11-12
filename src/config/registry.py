from typing import Dict
from src.connectors.base_connector import BaseSchemeConnector
from src.connectors.discovery_connector import DiscoveryConnector
from src.connectors.gems_connector import GEMSConnector
from src.connectors.medscheme_connector import MedschemeConnector
from src.connectors.hapi_fhir_connector import HAPIFHIRConnector
from src.config.settings import settings

def load_connectors() -> Dict[str, BaseSchemeConnector]:
    """Load and initialize all medical scheme connectors"""
    connectors = {}
    
    # Initialize Discovery connector if API key is available
    if settings.DISCOVERY_API_KEY and settings.DISCOVERY_API_KEY != "your_discovery_key_here":
        connectors["discovery"] = DiscoveryConnector(settings.DISCOVERY_API_KEY)
    else:
        # Use mock key for development
        connectors["discovery"] = DiscoveryConnector("mock_discovery_key")
    
    # Initialize GEMS connector if API key is available
    if settings.GEMS_API_KEY and settings.GEMS_API_KEY != "your_gems_key_here":
        connectors["gems"] = GEMSConnector(settings.GEMS_API_KEY)
    else:
        # Use mock key for development
        connectors["gems"] = GEMSConnector("mock_gems_key")
    
    # Initialize Medscheme connector if API key is available
    if settings.MEDSCHEME_API_KEY and settings.MEDSCHEME_API_KEY != "your_medscheme_key_here":
        connectors["medscheme"] = MedschemeConnector(settings.MEDSCHEME_API_KEY)
    else:
        # Use mock key for development
        connectors["medscheme"] = MedschemeConnector("mock_medscheme_key")
    
    # Initialize HAPI FHIR connector (always available - public API)
    connectors["fhir"] = HAPIFHIRConnector()
    
    return connectors

def get_available_schemes() -> list:
    """Get list of available medical schemes"""
    return list(load_connectors().keys())

def get_connector(scheme_name: str) -> BaseSchemeConnector:
    """Get a specific connector by scheme name"""
    connectors = load_connectors()
    if scheme_name not in connectors:
        raise ValueError(f"Scheme '{scheme_name}' not supported. Available schemes: {list(connectors.keys())}")
    return connectors[scheme_name]