"""
FastAPI Main Application for Render Deployment
This is a compatibility wrapper - the main.py now auto-detects all environments

NOTE: You can now use main.py directly for all environments!
The application will automatically detect if it's running on:
- LOCAL: Development machine
- MIRROR: Internal production server (hostname contains "mirror")
- RENDER: Cloud deployment (RENDER env var present)

This file is kept for backward compatibility with existing Render configuration.
"""

# Import everything from main module
from main import *

if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🔵 Starting in RENDER mode (via main_render.py compatibility wrapper)")
    logger.info("💡 TIP: You can now use 'main.py' directly - it auto-detects environments!")
    
    # Get configuration
    config = get_config()
    port = config.get('port', int(os.environ.get("PORT", 10000)))
    host = config.get('host', '0.0.0.0')
    
    # Render deployment configuration
    uvicorn.run(
        "main:app",  # Use main.app for consistency
        host=host,
        port=port,
        reload=False,  # Always disable reload in production
        log_level="info"
    )
