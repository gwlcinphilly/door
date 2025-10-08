#!/usr/bin/env python3
"""
Database Sync Script for Door System
====================================

This script synchronizes data between local PostgreSQL and remote Neon databases.
Supports bidirectional sync with configurable direction.

Usage:
    python database_sync.py                         # Default: smart-sync (recommended)
    python database_sync.py --direction smart-sync  # Smart bidirectional sync
    python database_sync.py --direction local-to-neon
    python database_sync.py --direction neon-to-local
    python database_sync.py --direction both
    python database_sync.py --help

Smart Sync Mode (Recommended):
    The smart-sync mode intelligently handles bidirectional synchronization:
    1. First syncs NEW records from Neon → Local (preserves Neon-only additions)
    2. Then syncs ALL records from Local → Neon (ensures Neon has complete data)
    This approach ensures no data loss while treating Local as the source of truth.

Author: AI Assistant
Date: 2025-01-24
Updated: 2025-10-08
"""

import os
import sys
import argparse
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple
import time
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory's .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_sync.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration class"""
    
    @staticmethod
    def get_local_config() -> Dict[str, str]:
        """Get local PostgreSQL configuration"""
        return {
            'host': 'localhost',
            'port': '5432',
            'database': 'bdoor_postgres',
            'user': 'bdoor_user',
            'password': 'bdoor_password'
        }
    
    @staticmethod
    def get_neon_config() -> Dict[str, str]:
        """Get Neon database configuration from environment variables"""
        neon_host = os.getenv('NEON_HOST')
        neon_user = os.getenv('NEON_USER')
        neon_password = os.getenv('NEON_PASSWORD')
        neon_database = os.getenv('NEON_DATABASE_NAME')

        if not all([neon_host, neon_user, neon_password, neon_database]):
            raise ValueError("Missing required Neon configuration. Please set NEON_HOST, NEON_USER, NEON_PASSWORD, and NEON_DATABASE_NAME in .env file")

        return {
            'host': neon_host,
            'port': os.getenv('NEON_PORT', '5432'),
            'database': neon_database,
            'user': neon_user,
            'password': neon_password,
            'sslmode': 'require'
        }

class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self, config: Dict[str, str], name: str):
        self.config = config
        self.name = name
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            logger.info(f"Connecting to {self.name} database...")
            self.connection = psycopg2.connect(**self.config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info(f"✅ Successfully connected to {self.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to {self.name}: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info(f"Disconnected from {self.name}")
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """Execute a SELECT query and return results"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            # Rollback to clear any aborted transaction state
            try:
                self.connection.rollback()
            except:
                pass
            return []
    
    def execute_update(self, query: str, params: Tuple = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE query"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            error_msg = str(e)
            if "foreign key constraint" in error_msg.lower():
                logger.error(f"Foreign key constraint violation: {error_msg}")
            elif "violates foreign key constraint" in error_msg.lower():
                logger.error(f"Foreign key constraint violation: {error_msg}")
            elif "duplicate key value violates unique constraint" in error_msg.lower():
                logger.error(f"Duplicate key violation: {error_msg}")
            elif "current transaction is aborted" in error_msg.lower():
                logger.error(f"Transaction aborted: {error_msg}")
                # Try to rollback and start a new transaction
                try:
                    self.connection.rollback()
                    self.connection.commit()  # Start new transaction
                except:
                    pass
            elif "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                logger.error(f"Column does not exist: {error_msg}")
            else:
                logger.error(f"Update execution failed: {e}")
            logger.error(f"Query: {query}")
            try:
                self.connection.rollback()
            except:
                pass
            return False

class DatabaseSyncer:
    """Main database synchronization class"""
    
    def __init__(self, direction: str = "local-to-neon"):
        self.direction = direction
        self.local_db = DatabaseConnection(DatabaseConfig.get_local_config(), "Local")
        self.neon_db = DatabaseConnection(DatabaseConfig.get_neon_config(), "Neon")
        self.sync_stats = {
            'tables_synced': 0,
            'records_synced': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def get_table_list(self) -> str:
        """Get list of tables to sync"""
        # Get all tables from information_schema
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE 'django_%'
        AND table_name NOT LIKE 'auth_%'
        ORDER BY table_name
        """
        return query
    
    def get_ordered_table_list(self, db_conn: DatabaseConnection) -> List[str]:
        """Get tables in dependency order to avoid foreign key violations"""
        # Define table dependency order (parent tables first)
        dependency_order = [
            # Core reference tables first
            'information_infosource',
            'information_infotag', 
            'notes_notestypes',
            'notes_notestag',
            'stocks_stocktypes',
            'stocks_stockstatus',
            'stocks_stocktags',
            'stocks_stock',
            'stocks_stockaccount',
            'stocktypes',
            'stockstatus', 
            'stocktags',
            
            # Main data tables
            'information_information',
            'notes_notes',
            'stocks_stocktrans',
            
            # Junction tables
            'information_information_tags',
            'information_infosourcemap',
            'information_infotagsourcemap',
            'information_tags',
            'notes_notestagtypemap',
            'information_infostocks',
            'information_infostockstype',
            
            # Dependent tables last
            'information_comment',
            'notes_update'
        ]
        
        # Get all available tables
        query = self.get_table_list()
        available_tables = [row['table_name'] for row in db_conn.execute_query(query)]
        
        logger.info(f"Available tables in source database: {available_tables}")
        
        # Order tables according to dependency, then add any remaining tables
        ordered_tables = []
        for table in dependency_order:
            if table in available_tables:
                ordered_tables.append(table)
        
        # Add any tables not in the dependency list
        for table in available_tables:
            if table not in ordered_tables:
                ordered_tables.append(table)
        
        # Filter out tables that don't exist
        existing_tables = []
        for table in ordered_tables:
            if self.table_exists(table, db_conn):
                existing_tables.append(table)
            else:
                logger.warning(f"Table {table} does not exist in source database, skipping")
                
        return existing_tables
    
    def table_exists(self, table_name: str, db_conn: DatabaseConnection) -> bool:
        """Check if a table exists in the database"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
        """
        result = db_conn.execute_query(query, (table_name,))
        return result and result[0]['exists']
    
    def get_table_structure(self, table_name: str, db_conn: DatabaseConnection) -> List[Dict]:
        """Get table structure (columns and types)"""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """
        return db_conn.execute_query(query, (table_name,))
    
    def get_table_data(self, table_name: str, db_conn: DatabaseConnection) -> List[Dict]:
        """Get all data from a table"""
        # First check if table has an 'id' column
        structure = self.get_table_structure(table_name, db_conn)
        if not structure:
            return []
        
        # Check if table has an 'id' column
        has_id_column = any(col['column_name'] == 'id' for col in structure)
        
        if has_id_column:
            query = f"SELECT * FROM {table_name} ORDER BY id"
        else:
            # Use the first column for ordering if no 'id' column
            first_column = structure[0]['column_name']
            query = f"SELECT * FROM {table_name} ORDER BY {first_column}"
        
        return db_conn.execute_query(query)
    
    def get_new_records(self, table_name: str, source_db: DatabaseConnection, target_db: DatabaseConnection) -> List[Dict]:
        """Get records that exist in source but not in target (based on ID)"""
        # Check if table has an 'id' column
        structure = self.get_table_structure(table_name, source_db)
        if not structure:
            return []
        
        has_id_column = any(col['column_name'] == 'id' for col in structure)
        
        if not has_id_column:
            # If no ID column, can't determine new records, return empty
            return []
        
        # Check if table exists in both databases
        if not self.table_exists(table_name, source_db) or not self.table_exists(table_name, target_db):
            # If table doesn't exist in target, all source records are "new"
            if self.table_exists(table_name, source_db):
                return self.get_table_data(table_name, source_db)
            return []
        
        # Get all IDs from target
        target_ids_query = f"SELECT id FROM {table_name}"
        target_ids_result = target_db.execute_query(target_ids_query)
        target_ids = {row['id'] for row in target_ids_result}
        
        # Get all records from source
        source_records = self.get_table_data(table_name, source_db)
        
        # Filter records that don't exist in target
        new_records = [record for record in source_records if record['id'] not in target_ids]
        
        return new_records
    
    def get_existing_record_ids(self, table_name: str, db_conn: DatabaseConnection) -> set:
        """Get set of all IDs from a table"""
        structure = self.get_table_structure(table_name, db_conn)
        if not structure:
            return set()
        
        has_id_column = any(col['column_name'] == 'id' for col in structure)
        if not has_id_column:
            return set()
        
        query = f"SELECT id FROM {table_name}"
        result = db_conn.execute_query(query)
        return {row['id'] for row in result}
    
    def create_table_if_not_exists(self, table_name: str, structure: List[Dict], target_db: DatabaseConnection) -> bool:
        """Create table if it doesn't exist"""
        # Check if table exists
        check_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
        """
        exists = target_db.execute_query(check_query, (table_name,))
        
        if exists and exists[0]['exists']:
            logger.info(f"Table {table_name} already exists in target database")
            return True
        
        # Create table with proper sequence handling
        columns = []
        sequences_to_create = []
        
        for col in structure:
            col_def = f'"{col["column_name"]}" {col["data_type"]}'
            if col["is_nullable"] == "NO":
                col_def += " NOT NULL"
            
            # Handle sequence defaults properly
            if col["column_default"] and "nextval" in col["column_default"]:
                # Extract sequence name from nextval('sequence_name'::regclass)
                seq_match = re.search(r"nextval\('([^']+)'", col["column_default"])
                if seq_match:
                    sequence_name = seq_match.group(1)
                    sequences_to_create.append(sequence_name)
                    # Use SERIAL type instead of nextval
                    if "integer" in col["data_type"]:
                        col_def = f'"{col["column_name"]}" SERIAL'
                    else:
                        col_def = f'"{col["column_name"]}" {col["data_type"]}'
                else:
                    # Fallback to original default
                    col_def += f" DEFAULT {col['column_default']}"
            elif col["column_default"]:
                col_def += f" DEFAULT {col['column_default']}"
            
            columns.append(col_def)
        
        # Create sequences first if needed
        for seq_name in sequences_to_create:
            seq_query = f"CREATE SEQUENCE IF NOT EXISTS {seq_name}"
            if not target_db.execute_update(seq_query):
                logger.warning(f"Failed to create sequence {seq_name}, continuing...")
        
        # Create table
        create_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        
        if target_db.execute_update(create_query):
            logger.info(f"✅ Created table {table_name} in target database")
            
            # Set sequence ownership if needed
            for seq_name in sequences_to_create:
                set_owner_query = f"ALTER SEQUENCE {seq_name} OWNED BY {table_name}.id"
                target_db.execute_update(set_owner_query)
            
            return True
        else:
            logger.error(f"❌ Failed to create table {table_name}")
            return False
    
    def insert_data(self, table_name: str, data: List[Dict], target_db: DatabaseConnection) -> Tuple[int, int]:
        """Insert data into target table using UPSERT. Returns (inserted_count, error_count)"""
        if not data:
            return 0, 0
        
        # Get column names from first record
        columns = list(data[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f'"{col}"' for col in columns])
        
        # Check if table has an 'id' column and primary key constraint
        structure = self.get_table_structure(table_name, target_db)
        has_id_column = any(col['column_name'] == 'id' for col in structure) if structure else False
        has_primary_key = self.has_primary_key(table_name, target_db) if structure else False
        
        if has_id_column and has_primary_key:
            # Use UPSERT with ON CONFLICT for tables with ID column and primary key
            conflict_columns = ', '.join([f'"{col}"' for col in columns if col != 'id'])
            update_clause = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns if col != 'id'])
            
            upsert_query = f"""
            INSERT INTO {table_name} ({column_names}) 
            VALUES ({placeholders})
            ON CONFLICT (id) DO UPDATE SET {update_clause}
            """
        else:
            # For tables without ID column or primary key, try simple insert
            upsert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        inserted_count = 0
        error_count = 0
        
        # Process records in batches to avoid transaction issues
        batch_size = 100
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            for record in batch:
                values = tuple(record.values())
                if target_db.execute_update(upsert_query, values):
                    inserted_count += 1
                else:
                    error_count += 1
                    logger.error(f"Failed to upsert record into {table_name}")
        
        return inserted_count, error_count
    
    def has_primary_key(self, table_name: str, db_conn: DatabaseConnection) -> bool:
        """Check if a table has a primary key constraint"""
        query = """
        SELECT COUNT(*) as count
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' 
        AND table_name = %s 
        AND constraint_type = 'PRIMARY KEY'
        """
        result = db_conn.execute_query(query, (table_name,))
        return result and result[0]['count'] > 0
    
    def sync_table(self, table_name: str, source_db: DatabaseConnection, target_db: DatabaseConnection) -> bool:
        """Sync a single table from source to target"""
        logger.info(f"🔄 Syncing table: {table_name}")
        
        try:
            # Check if table exists in source
            if not self.table_exists(table_name, source_db):
                logger.warning(f"Table {table_name} does not exist in source database, skipping")
                return True  # Not an error, just skip
            
            # Get table structure from source
            structure = self.get_table_structure(table_name, source_db)
            if not structure:
                logger.warning(f"No structure found for table {table_name}")
                self.sync_stats['errors'] += 1
                return False
            
            # Create table in target if it doesn't exist
            if not self.create_table_if_not_exists(table_name, structure, target_db):
                self.sync_stats['errors'] += 1
                return False
            
            # Get data from source
            data = self.get_table_data(table_name, source_db)
            logger.info(f"Found {len(data)} records in {table_name}")
            
            # Insert data into target
            inserted_count, error_count = self.insert_data(table_name, data, target_db)
            logger.info(f"✅ Inserted {inserted_count} records into {table_name}")
            
            # Count errors and successful records
            self.sync_stats['records_synced'] += inserted_count
            self.sync_stats['errors'] += error_count
            
            if error_count > 0:
                logger.warning(f"⚠️ {error_count} records failed to insert into {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error syncing table {table_name}: {e}")
            self.sync_stats['errors'] += 1
            return False
    
    def sync_new_records_only(self, table_name: str, source_db: DatabaseConnection, target_db: DatabaseConnection) -> bool:
        """Sync only new records (records in source but not in target) from source to target"""
        logger.info(f"🔄 Syncing new records for table: {table_name}")
        
        try:
            # Check if table exists in source
            if not self.table_exists(table_name, source_db):
                logger.warning(f"Table {table_name} does not exist in source database, skipping")
                return True  # Not an error, just skip
            
            # Get table structure from source
            structure = self.get_table_structure(table_name, source_db)
            if not structure:
                logger.warning(f"No structure found for table {table_name}")
                self.sync_stats['errors'] += 1
                return False
            
            # Create table in target if it doesn't exist
            if not self.create_table_if_not_exists(table_name, structure, target_db):
                self.sync_stats['errors'] += 1
                return False
            
            # Get only new records
            new_records = self.get_new_records(table_name, source_db, target_db)
            
            if not new_records:
                logger.info(f"No new records to sync for {table_name}")
                return True
            
            logger.info(f"Found {len(new_records)} new records in {table_name}")
            
            # Insert only new records into target
            inserted_count, error_count = self.insert_data(table_name, new_records, target_db)
            logger.info(f"✅ Inserted {inserted_count} new records into {table_name}")
            
            # Count errors and successful records
            self.sync_stats['records_synced'] += inserted_count
            self.sync_stats['errors'] += error_count
            
            if error_count > 0:
                logger.warning(f"⚠️ {error_count} new records failed to insert into {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error syncing new records for table {table_name}: {e}")
            self.sync_stats['errors'] += 1
            return False
    
    def sync_database(self, source_db: DatabaseConnection, target_db: DatabaseConnection, direction: str):
        """Sync entire database from source to target"""
        logger.info(f"🚀 Starting database sync: {direction}")
        
        # Get list of tables in dependency order
        table_names = self.get_ordered_table_list(source_db)
        
        if not table_names:
            logger.error("No tables found in source database")
            return False
        
        logger.info(f"Found {len(table_names)} tables to sync in dependency order:")
        for i, table in enumerate(table_names, 1):
            logger.info(f"  {i}. {table}")
        
        # Sync each table in order
        for table_name in table_names:
            if self.sync_table(table_name, source_db, target_db):
                self.sync_stats['tables_synced'] += 1
            else:
                logger.error(f"Failed to sync table {table_name}")
        
        logger.info(f"✅ Database sync completed: {direction}")
        return True
    
    def sync_new_records_from_database(self, source_db: DatabaseConnection, target_db: DatabaseConnection, direction: str):
        """Sync only new records from source to target database"""
        logger.info(f"🚀 Starting new records sync: {direction}")
        
        # Get list of tables in dependency order
        table_names = self.get_ordered_table_list(source_db)
        
        if not table_names:
            logger.error("No tables found in source database")
            return False
        
        logger.info(f"Found {len(table_names)} tables to check for new records:")
        for i, table in enumerate(table_names, 1):
            logger.info(f"  {i}. {table}")
        
        # Sync new records for each table in order
        tables_with_new_records = 0
        for table_name in table_names:
            # Check if there are new records first
            new_records = self.get_new_records(table_name, source_db, target_db)
            if new_records:
                tables_with_new_records += 1
                if self.sync_new_records_only(table_name, source_db, target_db):
                    # Don't increment tables_synced here, just log
                    pass
                else:
                    logger.error(f"Failed to sync new records for table {table_name}")
        
        logger.info(f"✅ New records sync completed: {direction}")
        logger.info(f"Tables with new records: {tables_with_new_records}")
        return True
    
    def run_sync(self):
        """Run the synchronization process"""
        self.sync_stats['start_time'] = datetime.now()
        
        logger.info("=" * 60)
        logger.info("🗄️  DATABASE SYNC STARTED")
        logger.info("=" * 60)
        logger.info(f"Direction: {self.direction}")
        logger.info(f"Start time: {self.sync_stats['start_time']}")
        
        # Connect to databases
        local_connected = self.local_db.connect()
        neon_connected = self.neon_db.connect()
        
        if not local_connected or not neon_connected:
            logger.error("❌ Failed to connect to one or both databases")
            return False
        
        try:
            success = True
            
            if self.direction == "smart-sync":
                # Smart sync: First pull new records from Neon to Local, then push everything from Local to Neon
                logger.info("\n🧠 SMART SYNC MODE")
                logger.info("Step 1: Sync new records from Neon → Local")
                logger.info("Step 2: Sync all records from Local → Neon")
                logger.info("-" * 60)
                
                # Step 1: Sync only new records from Neon to Local
                logger.info("\n📥 Step 1: Syncing NEW records Neon → Local")
                if not self.sync_new_records_from_database(self.neon_db, self.local_db, "Neon → Local (new records only)"):
                    success = False
                    logger.warning("⚠️ Step 1 had issues, but continuing to Step 2...")
                
                # Step 2: Sync all records from Local to Neon (full sync)
                logger.info("\n📤 Step 2: Syncing ALL records Local → Neon")
                if not self.sync_database(self.local_db, self.neon_db, "Local → Neon (full sync)"):
                    success = False
                
            elif self.direction in ["local-to-neon", "both"]:
                logger.info("\n📤 Syncing Local → Neon")
                if not self.sync_database(self.local_db, self.neon_db, "Local → Neon"):
                    success = False
            
            if self.direction in ["neon-to-local", "both"]:
                logger.info("\n📥 Syncing Neon → Local")
                if not self.sync_database(self.neon_db, self.local_db, "Neon → Local"):
                    success = False
            
            self.sync_stats['end_time'] = datetime.now()
            duration = self.sync_stats['end_time'] - self.sync_stats['start_time']
            
            # Log summary
            logger.info("\n" + "=" * 60)
            logger.info("📊 SYNC SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Tables synced: {self.sync_stats['tables_synced']}")
            logger.info(f"Records synced: {self.sync_stats['records_synced']}")
            logger.info(f"Errors: {self.sync_stats['errors']}")
            logger.info(f"Duration: {duration}")
            logger.info(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
            
            # Print only final status to console
            print(f"Database sync {'completed successfully' if success else 'failed'}. Check database_sync.log for details.")
            
            return success
            
        finally:
            # Always disconnect
            self.local_db.disconnect()
            self.neon_db.disconnect()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Sync database between local PostgreSQL and Neon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python database_sync.py                           # Default: smart-sync (recommended)
  python database_sync.py --direction smart-sync    # Smart bidirectional sync
  python database_sync.py --direction local-to-neon # Explicit: local → neon
  python database_sync.py --direction neon-to-local # neon → local
  python database_sync.py --direction both          # Bidirectional sync (both directions)

Smart Sync Mode (Recommended):
  The smart-sync mode does the following:
  1. First syncs NEW records from Neon → Local (preserves Neon changes)
  2. Then syncs ALL records from Local → Neon (ensures Neon has everything)
  This ensures no data loss and Local is the source of truth while preserving Neon additions.
        """
    )
    
    parser.add_argument(
        '--direction',
        choices=['smart-sync', 'local-to-neon', 'neon-to-local', 'both'],
        default='smart-sync',
        help='Sync direction (default: smart-sync)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run syncer
    syncer = DatabaseSyncer(args.direction)
    success = syncer.run_sync()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
