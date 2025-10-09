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

2. Run the sync script (smart-sync mode - recommended):
   ```bash
   python database_sync.py
   ```

3. Or specify a sync direction:
   ```bash
   # Smart bidirectional sync (default - recommended)
   python database_sync.py --direction smart-sync
   
   # One-way sync: Local → Neon
   python database_sync.py --direction local-to-neon
   
   # One-way sync: Neon → Local
   python database_sync.py --direction neon-to-local
   
   # Both directions (full bidirectional)
   python database_sync.py --direction both
   ```

4. Check the log file for details:
   ```bash
   tail -f database_sync.log
   ```

### Features

- ✅ **Smart Sync Mode** - Intelligent bidirectional sync that preserves all data
- ✅ Bidirectional sync between local PostgreSQL and Neon database
- ✅ UPSERT operations with conflict resolution
- ✅ Automatic table creation with sequence handling
- ✅ Dependency-aware table ordering
- ✅ Comprehensive error handling and logging
- ✅ Syncs all tables including associations

### Smart Sync Mode (Recommended)

The **smart-sync** mode is the recommended way to synchronize your databases. It intelligently handles bidirectional synchronization:

1. **Step 1:** Syncs NEW records from Neon → Local (preserves Neon-only additions)
2. **Step 2:** Syncs ALL records from Local → Neon (ensures Neon has complete data)

This approach ensures:
- No data loss from either database
- Local database is treated as the source of truth
- New entries created on Neon (e.g., from production) are preserved
- All local changes are pushed to Neon

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
