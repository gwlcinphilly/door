# FastAPI Tools

This directory contains utility tools and scripts for the FastAPI application.

## Database Sync Tool

### Files

- **`database_sync.py`** - Main database synchronization script
- **`sync_requirements.txt`** - Dependencies for the sync script
- **`DATABASE_SYNC_README.md`** - Detailed documentation for the database sync tool
- **`database_sync.log`** - Log file from database sync operations

### Quick Start

1. Install dependencies:
   ```bash
   pip install -r sync_requirements.txt
   ```

2. Run the sync script:
   ```bash
   python database_sync.py
   ```

3. Check the log file for details:
   ```bash
   tail -f database_sync.log
   ```

### Features

- ✅ Bidirectional sync between local PostgreSQL and Neon database
- ✅ UPSERT operations with conflict resolution
- ✅ Automatic table creation with sequence handling
- ✅ Dependency-aware table ordering
- ✅ Comprehensive error handling and logging

For detailed usage instructions, see [DATABASE_SYNC_README.md](DATABASE_SYNC_README.md).

## Usage

All tools in this directory can be run from the project root:

```bash
# From project root
python fastapi_app/tools/database_sync.py --help

# Or from tools directory
cd fastapi_app/tools
python database_sync.py --help
```

## Future Tools

This directory is ready for additional utility tools as the project grows.
