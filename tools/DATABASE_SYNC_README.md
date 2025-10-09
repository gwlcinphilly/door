# Database Sync Script

This script synchronizes data between your local PostgreSQL database and the remote Neon database.

## Features

- ✅ **Bidirectional Sync**: Sync from local to Neon, Neon to local, or both ways
- ✅ **Automatic Table Creation**: Creates missing tables in target database
- ✅ **UPSERT Operations**: Uses INSERT ... ON CONFLICT for handling existing data
- ✅ **Data Preservation**: Handles data transfer with proper type mapping
- ✅ **Dependency-Aware Ordering**: Syncs tables in proper order to avoid foreign key violations
- ✅ **Accurate Error Counting**: Counts both table-level and record-level errors
- ✅ **Smart Column Detection**: Handles tables with and without ID columns
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Progress Tracking**: Detailed sync statistics and progress reporting
- ✅ **Logging**: Full logging to log file with minimal console output

## Installation

1. Install required dependencies:
```bash
pip install -r sync_requirements.txt
```

2. Make the script executable:
```bash
chmod +x database_sync.py
```

## Usage

### Basic Usage

```bash
# Default: Sync from local PostgreSQL to Neon database
python database_sync.py

# Or make it executable and run directly
./database_sync.py
```

### Sync Directions

```bash
# Sync from local to Neon (default)
python database_sync.py --direction local-to-neon

# Sync from Neon to local
python database_sync.py --direction neon-to-local

# Bidirectional sync (both ways)
python database_sync.py --direction both
```

### Verbose Logging

```bash
# Enable verbose logging for debugging
python database_sync.py --verbose
```

### Help

```bash
# Show help and usage examples
python database_sync.py --help
```

## Database Configuration

The script automatically uses the database configurations from your Django settings:

### Local PostgreSQL
- **Host**: localhost
- **Port**: 5432
- **Database**: bdoor_postgres
- **User**: bdoor_user
- **Password**: bdoor_password

### Neon Database
- **Host**: your-project.us-east-1.aws.neon.tech (get from Neon dashboard)
- **Port**: 5432
- **Database**: your-database-name
- **User**: your-neon-username
- **Password**: your-neon-password (NEVER commit this!)
- **SSL**: Required

## What Gets Synced

The script synchronizes all tables in the `public` schema, excluding:
- Django system tables (`django_*`)
- Authentication tables (`auth_*`)

### Tables Typically Synced
- `information_information` - Information entries
- `information_infosource` - Information sources
- `information_infotag` - Information tags
- `information_comment` - Comments
- `notes_notes` - Notes entries
- `notes_notestypes` - Notes categories
- `notes_notestag` - Notes tags
- And other application tables

## Logging

The script creates detailed logs:
- **Console Output**: Only final status message
- **Log File**: `database_sync.log` with complete sync history and detailed progress

## Example Output

### Console Output (Minimal)
```
Database sync completed successfully. Check database_sync.log for details.
```

### Log File Output (Detailed)
```
2025-01-24 10:30:15 - INFO - ============================================================
2025-01-24 10:30:15 - INFO - 🗄️  DATABASE SYNC STARTED
2025-01-24 10:30:15 - INFO - ============================================================
2025-01-24 10:30:15 - INFO - Direction: local-to-neon
2025-01-24 10:30:15 - INFO - Start time: 2025-01-24 10:30:15.123456
2025-01-24 10:30:15 - INFO - Connecting to Local database...
2025-01-24 10:30:16 - INFO - ✅ Successfully connected to Local
2025-01-24 10:30:16 - INFO - Connecting to Neon database...
2025-01-24 10:30:17 - INFO - ✅ Successfully connected to Neon
2025-01-24 10:30:17 - INFO - 📤 Syncing Local → Neon
2025-01-24 10:30:17 - INFO - Found 8 tables to sync: information_information, information_infosource, information_infotag, information_comment, notes_notes, notes_notestypes, notes_notestag, notes_update
2025-01-24 10:30:17 - INFO - 🔄 Syncing table: information_information
2025-01-24 10:30:18 - INFO - Found 673 records in information_information
2025-01-24 10:30:19 - INFO - ✅ Inserted 673 records into information_information
...
2025-01-24 10:30:25 - INFO - ============================================================
2025-01-24 10:30:25 - INFO - 📊 SYNC SUMMARY
2025-01-24 10:30:25 - INFO - ============================================================
2025-01-24 10:30:25 - INFO - Tables synced: 8
2025-01-24 10:30:25 - INFO - Records synced: 1247
2025-01-24 10:30:25 - INFO - Errors: 0
2025-01-24 10:30:25 - INFO - Duration: 0:00:10.123456
2025-01-24 10:30:25 - INFO - Status: ✅ SUCCESS
```

## Error Handling

The script includes comprehensive error handling:
- **Connection Errors**: Graceful handling of database connection failures
- **Table Creation Errors**: Automatic table structure replication with sequence handling
- **Data Insertion Errors**: Individual record error tracking with UPSERT operations
- **Transaction Errors**: Automatic rollback and recovery from aborted transactions
- **Missing Tables**: Skips non-existent tables instead of failing
- **Duplicate Key Violations**: Handled with UPSERT operations (INSERT ... ON CONFLICT)
- **Foreign Key Violations**: Clear error messages and proper error counting
- **Missing Columns**: Smart detection of tables without ID columns
- **Sequence Creation**: Automatic creation of PostgreSQL sequences for auto-increment columns
- **Primary Key Detection**: Smart UPSERT logic that only uses ON CONFLICT for tables with primary keys
- **Network Issues**: SSL and timeout handling for Neon database

## Safety Features

- **Non-destructive**: Only adds/updates data, doesn't delete existing records
- **Transaction Safety**: Uses database transactions for data integrity
- **Rollback on Error**: Automatic rollback if sync fails
- **Connection Validation**: Tests connections before starting sync
- **Dependency Ordering**: Syncs parent tables before child tables to avoid foreign key violations
- **Accurate Error Reporting**: Properly counts and reports all errors (table-level and record-level)
- **Comprehensive Logging**: Full audit trail in `database_sync.log`

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL is running locally
- Check Neon database credentials
- Verify network connectivity to Neon

### Permission Issues
- Ensure database user has appropriate permissions
- Check table creation permissions in target database

### SSL Issues
- Neon requires SSL connections
- Script automatically handles SSL configuration

## Integration

This script can be integrated into:
- **Cron Jobs**: Regular automated syncs
- **CI/CD Pipelines**: Database deployment automation
- **Backup Scripts**: Data backup and restoration
- **Development Workflows**: Environment synchronization
