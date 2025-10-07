"""
Global configuration and environment detection system
Determines if the application is running locally or on Render
"""

import os
import sys
from enum import Enum
from typing import Dict, Any
from pathlib import Path

class EnvironmentType(Enum):
    LOCAL = "local"
    RENDER = "render"
    UNKNOWN = "unknown"

class SystemConfig:
    """Global system configuration and environment detection"""
    
    def __init__(self):
        self._environment = self._detect_environment()
        self._config = self._load_config()
    
    def _detect_environment(self) -> EnvironmentType:
        """Detect the current running environment"""
        
        # Check 1: Environment variables
        if os.getenv('RENDER'):
            return EnvironmentType.RENDER
        if os.getenv('USE_NEON', 'False').lower() == 'true':
            return EnvironmentType.RENDER
        
        # Check 2: Port detection
        try:
            port = int(os.getenv('PORT', '8000'))
            if port == 10000:  # Render's default port
                return EnvironmentType.RENDER
        except ValueError:
            pass
        
        # Check 3: Running file detection
        main_file = sys.argv[0] if sys.argv else ""
        if 'main_render.py' in main_file:
            return EnvironmentType.RENDER
        elif 'main.py' in main_file:
            return EnvironmentType.LOCAL
        
        # Check 4: Database connection type
        if os.getenv('NEON_HOST') and os.getenv('NEON_DATABASE_NAME'):
            return EnvironmentType.RENDER
        
        # Check 5: File system paths (Render has specific paths)
        if '/opt/render' in os.getcwd() or 'render' in os.getcwd().lower():
            return EnvironmentType.RENDER
        
        # Default to local if we can't determine
        return EnvironmentType.LOCAL
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration based on environment"""
        
        if self._environment == EnvironmentType.RENDER:
            return {
                'name': 'Render Production',
                'description': 'Production deployment on Render platform',
                'database': 'Neon PostgreSQL',
                'port': int(os.getenv('PORT', '10000')),
                'authentication': True,
                'debug': False,
                'features': {
                    'authentication': True,
                    'database_sync': True,
                    'external_apis': True,
                    'advanced_logging': True,
                    'production_monitoring': True,
                    'ssl_enabled': True,
                    'cors_restricted': True
                },
                'restrictions': {
                    'file_uploads': 'Limited',
                    'local_file_access': 'Restricted',
                    'debug_mode': 'Disabled'
                }
            }
        else:  # LOCAL
            return {
                'name': 'Local Development',
                'description': 'Local development environment',
                'database': 'Local PostgreSQL',
                'port': int(os.getenv('PORT', '8000')),
                'authentication': False,
                'debug': True,
                'features': {
                    'authentication': False,
                    'database_sync': True,
                    'external_apis': True,
                    'advanced_logging': True,
                    'production_monitoring': False,
                    'ssl_enabled': False,
                    'cors_restricted': False
                },
                'restrictions': {
                    'file_uploads': 'Unlimited',
                    'local_file_access': 'Full',
                    'debug_mode': 'Enabled'
                }
            }
    
    @property
    def environment(self) -> EnvironmentType:
        """Get the current environment type"""
        return self._environment
    
    @property
    def is_local(self) -> bool:
        """Check if running locally"""
        return self._environment == EnvironmentType.LOCAL
    
    @property
    def is_render(self) -> bool:
        """Check if running on Render"""
        return self._environment == EnvironmentType.RENDER
    
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
        """Get comprehensive environment information"""
        return {
            'environment': self._environment.value,
            'config': self._config,
            'detection_methods': {
                'render_env_var': bool(os.getenv('RENDER')),
                'neon_database': bool(os.getenv('NEON_HOST')),
                'port': int(os.getenv('PORT', '8000')),
                'main_file': sys.argv[0] if sys.argv else '',
                'working_directory': os.getcwd(),
                'python_executable': sys.executable
            }
        }

# Global instance
system_config = SystemConfig()

# Convenience functions
def is_local() -> bool:
    """Check if running in local development environment"""
    return system_config.is_local

def is_render() -> bool:
    """Check if running on Render production environment"""
    return system_config.is_render

def get_environment() -> str:
    """Get environment name"""
    return system_config.environment.value

def get_feature_status(feature: str) -> bool:
    """Check if a feature is available"""
    return system_config.get_feature_status(feature)

def get_environment_info() -> Dict[str, Any]:
    """Get comprehensive environment information"""
    return system_config.get_environment_info()
