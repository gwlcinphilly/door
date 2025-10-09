"""
Global configuration and environment detection system
Supports three deployment environments:
1. LOCAL - Development machine (hostname != "mirror")
2. MIRROR - Internal production server (hostname == "mirror")
3. RENDER - Cloud deployment on Render platform
"""

import os
import sys
import socket
from enum import Enum
from typing import Dict, Any
from pathlib import Path

class EnvironmentType(Enum):
    """Supported deployment environments"""
    LOCAL = "local"      # Development machine - unstable, testing features
    MIRROR = "mirror"    # Internal production - stable, full features
    RENDER = "render"    # Cloud production - stable, authenticated access
    UNKNOWN = "unknown"  # Fallback

class SystemConfig:
    """Global system configuration and environment detection"""
    
    def __init__(self):
        self._environment = self._detect_environment()
        self._config = self._load_config()
    
    def _detect_environment(self) -> EnvironmentType:
        """
        Detect the current running environment with priority order:
        1. Hostname check (mirror = MIRROR)
        2. Render platform indicators (RENDER)
        3. Default to LOCAL
        """
        
        # Priority 1: Check hostname for mirror server
        try:
            hostname = socket.gethostname().lower()
            if 'mirror' in hostname:
                return EnvironmentType.MIRROR
        except Exception:
            pass
        
        # Priority 2: Check for Render environment variables
        if os.getenv('RENDER'):
            return EnvironmentType.RENDER
        if os.getenv('USE_NEON', 'False').lower() == 'true':
            return EnvironmentType.RENDER
        
        # Priority 3: Check for Neon database (Render indicator)
        if os.getenv('NEON_HOST') and os.getenv('NEON_DATABASE_NAME'):
            return EnvironmentType.RENDER
        
        # Priority 4: Running file detection
        main_file = sys.argv[0] if sys.argv else ""
        if 'main_render.py' in main_file:
            return EnvironmentType.RENDER
        
        # Priority 5: Port detection
        try:
            port = int(os.getenv('PORT', '8000'))
            if port == 10000:  # Render's default port
                return EnvironmentType.RENDER
        except ValueError:
            pass
        
        # Priority 6: File system paths (Render specific)
        if '/opt/render' in os.getcwd() or 'render' in os.getcwd().lower():
            return EnvironmentType.RENDER
        
        # Default: Assume LOCAL development environment
        return EnvironmentType.LOCAL
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration based on detected environment"""
        
        if self._environment == EnvironmentType.RENDER:
            # RENDER: Cloud production - secure, authenticated, external access
            return {
                'name': 'Render Production',
                'description': 'Cloud deployment on Render platform - accessible from anywhere',
                'database': 'Neon PostgreSQL (Cloud)',
                'database_type': 'neon',
                'port': int(os.getenv('PORT', '10000')),
                'host': '0.0.0.0',
                'authentication_required': True,
                'debug': False,
                'auto_reload': False,
                'features': {
                    # Security features
                    'authentication': True,           # ALL pages require login
                    'session_management': True,
                    'ssl_enabled': True,
                    'cors_restricted': True,
                    
                    # Database features
                    'database_sync': False,           # No sync to local
                    'database_backup': True,
                    
                    # Application features
                    'external_apis': True,
                    'advanced_logging': True,
                    'production_monitoring': True,
                    'error_tracking': True,
                    
                    # Development features
                    'debug_toolbar': False,
                    'hot_reload': False,
                },
                'restrictions': {
                    'file_uploads': 'Limited (10MB)',
                    'local_file_access': 'Restricted',
                    'debug_mode': 'Disabled',
                    'experimental_features': 'Disabled'
                },
                'access': 'Public Internet (Authenticated)'
            }
            
        elif self._environment == EnvironmentType.MIRROR:
            # MIRROR: Internal production - stable, full features, no auth
            return {
                'name': 'Mirror Production',
                'description': 'Internal production server - stable build with full features',
                'database': 'PostgreSQL (Docker Container)',
                'database_type': 'postgres_docker',
                'port': int(os.getenv('PORT', '8080')),
                'host': '0.0.0.0',
                'authentication_required': False,
                'debug': False,
                'auto_reload': False,
                'features': {
                    # Security features (internal network, no auth needed)
                    'authentication': False,          # No login required (trusted network)
                    'session_management': False,
                    'ssl_enabled': False,             # Internal HTTPS via reverse proxy
                    'cors_restricted': False,
                    
                    # Database features
                    'database_sync': True,            # Sync with local dev
                    'database_backup': True,
                    
                    # Application features
                    'external_apis': True,
                    'advanced_logging': True,
                    'production_monitoring': True,
                    'error_tracking': True,
                    
                    # Development features
                    'debug_toolbar': False,
                    'hot_reload': False,
                },
                'restrictions': {
                    'file_uploads': 'Unlimited',
                    'local_file_access': 'Full',
                    'debug_mode': 'Disabled',
                    'experimental_features': 'Disabled'
                },
                'access': 'Internal Network Only'
            }
            
        else:  # LOCAL
            # LOCAL: Development - unstable, testing, full access
            return {
                'name': 'Local Development',
                'description': 'Local development machine - testing and unstable features',
                'database': 'PostgreSQL (Local)',
                'database_type': 'postgres_local',
                'port': int(os.getenv('PORT', '8080')),
                'host': '0.0.0.0',
                'authentication_required': False,
                'debug': True,
                'auto_reload': True,
                'features': {
                    # Security features (dev mode, no restrictions)
                    'authentication': False,          # No login needed for dev
                    'session_management': False,
                    'ssl_enabled': False,
                    'cors_restricted': False,
                    
                    # Database features
                    'database_sync': True,            # Sync with mirror
                    'database_backup': False,
                    
                    # Application features
                    'external_apis': True,
                    'advanced_logging': True,
                    'production_monitoring': False,
                    'error_tracking': False,
                    
                    # Development features
                    'debug_toolbar': True,
                    'hot_reload': True,
                },
                'restrictions': {
                    'file_uploads': 'Unlimited',
                    'local_file_access': 'Full',
                    'debug_mode': 'Enabled',
                    'experimental_features': 'Enabled'
                },
                'access': 'Local Network'
            }
    
    @property
    def environment(self) -> EnvironmentType:
        """Get the current environment type"""
        return self._environment
    
    @property
    def is_local(self) -> bool:
        """Check if running on local development machine"""
        return self._environment == EnvironmentType.LOCAL
    
    @property
    def is_mirror(self) -> bool:
        """Check if running on internal mirror server"""
        return self._environment == EnvironmentType.MIRROR
    
    @property
    def is_render(self) -> bool:
        """Check if running on Render cloud platform"""
        return self._environment == EnvironmentType.RENDER
    
    @property
    def is_production(self) -> bool:
        """Check if running in any production environment (Mirror or Render)"""
        return self._environment in [EnvironmentType.MIRROR, EnvironmentType.RENDER]
    
    @property
    def requires_auth(self) -> bool:
        """Check if authentication is required"""
        return self._config.get('authentication_required', False)
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration"""
        return self._config
    
    def get_feature_status(self, feature: str) -> bool:
        """Check if a specific feature is available"""
        return self._config.get('features', {}).get(feature, False)
    
    def get_restriction(self, restriction: str) -> str:
        """Get restriction information for a specific area"""
        return self._config.get('restrictions', {}).get(restriction, 'Unknown')
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information for debugging"""
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "Unknown"
            
        return {
            'environment': self._environment.value,
            'environment_name': self._config.get('name'),
            'description': self._config.get('description'),
            'config': self._config,
            'detection_methods': {
                'hostname': hostname,
                'render_env_var': bool(os.getenv('RENDER')),
                'use_neon': os.getenv('USE_NEON', 'False'),
                'neon_database': bool(os.getenv('NEON_HOST')),
                'port': int(os.getenv('PORT', '8000')),
                'main_file': sys.argv[0] if sys.argv else 'Unknown',
                'working_directory': os.getcwd(),
                'python_executable': sys.executable
            }
        }
    
    def __str__(self) -> str:
        """String representation for logging"""
        return f"Environment: {self._config.get('name')} ({self._environment.value})"

# Global instance - auto-detect environment on import
system_config = SystemConfig()

# Convenience functions for easy access throughout the application
def is_local() -> bool:
    """Check if running in local development environment"""
    return system_config.is_local

def is_mirror() -> bool:
    """Check if running on internal mirror production server"""
    return system_config.is_mirror

def is_render() -> bool:
    """Check if running on Render cloud production environment"""
    return system_config.is_render

def is_production() -> bool:
    """Check if running in any production environment"""
    return system_config.is_production

def requires_auth() -> bool:
    """Check if authentication is required"""
    return system_config.requires_auth

def get_environment() -> str:
    """Get environment name as string"""
    return system_config.environment.value

def get_environment_type() -> EnvironmentType:
    """Get environment type enum"""
    return system_config.environment

def get_feature_status(feature: str) -> bool:
    """Check if a feature is available in current environment"""
    return system_config.get_feature_status(feature)

def get_environment_info() -> Dict[str, Any]:
    """Get comprehensive environment information"""
    return system_config.get_environment_info()

def get_config() -> Dict[str, Any]:
    """Get full configuration for current environment"""
    return system_config.config

# Print environment info on import for debugging
if __name__ != "__main__":
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 {system_config}")
    logger.info(f"   Database: {system_config.config.get('database')}")
    logger.info(f"   Authentication: {'Required' if system_config.requires_auth else 'Disabled'}")
    logger.info(f"   Access: {system_config.config.get('access')}")
