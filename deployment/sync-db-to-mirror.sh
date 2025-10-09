#!/bin/bash
# Sync PostgreSQL database from local machine to mirror server
# This script dumps the local database and restores it to the mirror container

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
MIRROR_HOST="root@mirror"
SSH_KEY="$HOME/.ssh/id_ed25519_mirror_root"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Local PostgreSQL Configuration
LOCAL_DB_HOST="localhost"
LOCAL_DB_PORT="5432"
LOCAL_DB_NAME="bdoor_postgres"
LOCAL_DB_USER="bdoor_user"
LOCAL_DB_PASSWORD="bdoor_password"

# Mirror PostgreSQL Configuration (in Docker)
MIRROR_CONTAINER="postgres-mirror"
MIRROR_DB_NAME="bdoor_postgres"
MIRROR_DB_USER="bdoor_user"
MIRROR_DB_PASSWORD="bdoor_password"

# Temporary files
DUMP_FILE="/tmp/door_db_dump_$(date +%Y%m%d_%H%M%S).sql"
REMOTE_DUMP_FILE="/tmp/door_db_dump.sql"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  PostgreSQL Database Sync${NC}"
echo -e "${BLUE}  Local → Mirror Server${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if local database is accessible
echo -e "${YELLOW}📊 Checking local database connection...${NC}"
if ! PGPASSWORD="$LOCAL_DB_PASSWORD" psql -h "$LOCAL_DB_HOST" -p "$LOCAL_DB_PORT" -U "$LOCAL_DB_USER" -d "$LOCAL_DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to local database${NC}"
    echo -e "${RED}   Host: $LOCAL_DB_HOST:$LOCAL_DB_PORT${NC}"
    echo -e "${RED}   Database: $LOCAL_DB_NAME${NC}"
    echo -e "${RED}   User: $LOCAL_DB_USER${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Local database connection successful${NC}"
echo ""

# Check SSH connection
echo -e "${YELLOW}🔌 Testing SSH connection to mirror...${NC}"
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$MIRROR_HOST" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Failed to connect to mirror${NC}"
    exit 1
fi
echo -e "${GREEN}✅ SSH connection successful${NC}"
echo ""

# Check if mirror container is running
echo -e "${YELLOW}🐳 Checking mirror PostgreSQL container...${NC}"
CONTAINER_STATUS=$(ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker ps -f name=$MIRROR_CONTAINER --format '{{.Status}}'" || echo "")
if [ -z "$CONTAINER_STATUS" ]; then
    echo -e "${RED}❌ PostgreSQL container not running on mirror${NC}"
    echo -e "${YELLOW}   Starting PostgreSQL container...${NC}"

    # Deploy docker-compose file if not exists
    ssh -i "$SSH_KEY" "$MIRROR_HOST" "mkdir -p /opt/door"
    scp -i "$SSH_KEY" "$LOCAL_DIR/docker-compose.postgres.yml" "$MIRROR_HOST:/opt/door/"

    # Start the container
    ssh -i "$SSH_KEY" "$MIRROR_HOST" "cd /opt/door && docker compose -f docker-compose.postgres.yml up -d"

    # Wait for container to be healthy
    echo -e "${YELLOW}   Waiting for PostgreSQL to be ready...${NC}"
    for i in {1..30}; do
        if ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker exec $MIRROR_CONTAINER pg_isready -U $MIRROR_DB_USER" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ PostgreSQL container is ready${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ PostgreSQL container failed to start${NC}"
            exit 1
        fi
        echo -e "   Attempt $i/30..."
        sleep 2
    done
else
    echo -e "${GREEN}✅ PostgreSQL container is running${NC}"
fi
echo ""

# Dump local database
echo -e "${YELLOW}💾 Dumping local database...${NC}"
echo -e "   Database: $LOCAL_DB_NAME"
echo -e "   Output: $DUMP_FILE"

PGPASSWORD="$LOCAL_DB_PASSWORD" pg_dump \
    -h "$LOCAL_DB_HOST" \
    -p "$LOCAL_DB_PORT" \
    -U "$LOCAL_DB_USER" \
    -d "$LOCAL_DB_NAME" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    -f "$DUMP_FILE"

DUMP_SIZE=$(du -h "$DUMP_FILE" | cut -f1)
echo -e "${GREEN}✅ Database dumped successfully (Size: $DUMP_SIZE)${NC}"
echo ""

# Transfer dump file to mirror
echo -e "${YELLOW}📤 Transferring dump file to mirror...${NC}"
scp -i "$SSH_KEY" "$DUMP_FILE" "$MIRROR_HOST:$REMOTE_DUMP_FILE"
echo -e "${GREEN}✅ File transferred successfully${NC}"
echo ""

# Restore database on mirror
echo -e "${YELLOW}📥 Restoring database on mirror...${NC}"
ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker exec -i $MIRROR_CONTAINER psql -U $MIRROR_DB_USER -d $MIRROR_DB_NAME" < "$DUMP_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database restored successfully${NC}"
else
    echo -e "${RED}❌ Database restore failed${NC}"
    exit 1
fi
echo ""

# Verify the sync
echo -e "${YELLOW}🔍 Verifying sync...${NC}"

# Count tables in local database
LOCAL_TABLE_COUNT=$(PGPASSWORD="$LOCAL_DB_PASSWORD" psql -h "$LOCAL_DB_HOST" -p "$LOCAL_DB_PORT" -U "$LOCAL_DB_USER" -d "$LOCAL_DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" | xargs)

# Count tables in mirror database
MIRROR_TABLE_COUNT=$(ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker exec -i $MIRROR_CONTAINER psql -U $MIRROR_DB_USER -d $MIRROR_DB_NAME -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'\"" | xargs)

echo -e "   Local tables: $LOCAL_TABLE_COUNT"
echo -e "   Mirror tables: $MIRROR_TABLE_COUNT"

if [ "$LOCAL_TABLE_COUNT" -eq "$MIRROR_TABLE_COUNT" ]; then
    echo -e "${GREEN}✅ Table count matches${NC}"
else
    echo -e "${YELLOW}⚠️  Table count mismatch (might be okay if databases differ)${NC}"
fi
echo ""

# Clean up
echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
rm -f "$DUMP_FILE"
ssh -i "$SSH_KEY" "$MIRROR_HOST" "rm -f $REMOTE_DUMP_FILE"
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  ✅ Database Sync Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Mirror PostgreSQL Details:${NC}"
echo -e "  Host: mirror"
echo -e "  Port: 5432"
echo -e "  Database: $MIRROR_DB_NAME"
echo -e "  User: $MIRROR_DB_USER"
echo -e "  Container: $MIRROR_CONTAINER"
echo ""
echo -e "${BLUE}Connect from local machine:${NC}"
echo -e "  ${YELLOW}psql -h mirror -p 5432 -U $MIRROR_DB_USER -d $MIRROR_DB_NAME${NC}"
echo ""
echo -e "${BLUE}Connect via SSH tunnel:${NC}"
echo -e "  ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'docker exec -it $MIRROR_CONTAINER psql -U $MIRROR_DB_USER -d $MIRROR_DB_NAME'${NC}"
echo ""
echo -e "${BLUE}Container management:${NC}"
echo -e "  View logs:    ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'docker logs $MIRROR_CONTAINER -f'${NC}"
echo -e "  Restart:      ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'cd /opt/door && docker compose -f docker-compose.postgres.yml restart'${NC}"
echo -e "  Stop:         ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'cd /opt/door && docker compose -f docker-compose.postgres.yml down'${NC}"
echo ""
