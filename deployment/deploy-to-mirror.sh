#!/bin/bash
# Deploy Door FastAPI application to mirror staging server
# This script syncs local changes to the mirror container

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
MIRROR_HOST="root@mirror"
REMOTE_APP_DIR="/opt/door"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_KEY="$HOME/.ssh/id_ed25519_mirror_root"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Door FastAPI - Deploy to Mirror Staging${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ SSH key not found: $SSH_KEY${NC}"
    exit 1
fi

# Test SSH connection
echo -e "${YELLOW}🔌 Testing SSH connection to mirror...${NC}"
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$MIRROR_HOST" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Failed to connect to mirror${NC}"
    exit 1
fi
echo -e "${GREEN}✅ SSH connection successful${NC}"
echo ""

# Create remote directory if it doesn't exist
echo -e "${YELLOW}📁 Setting up remote directory...${NC}"
ssh -i "$SSH_KEY" "$MIRROR_HOST" "mkdir -p $REMOTE_APP_DIR"
echo -e "${GREEN}✅ Remote directory ready${NC}"
echo ""

# Sync code to mirror (exclude venv, __pycache__, .git, etc.)
echo -e "${YELLOW}📦 Syncing code to mirror...${NC}"
rsync -avz --progress \
    -e "ssh -i $SSH_KEY" \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    --exclude '.env' \
    --exclude '*.log' \
    --exclude '.DS_Store' \
    --exclude 'database_sync.log' \
    "$LOCAL_DIR/" "$MIRROR_HOST:$REMOTE_APP_DIR/"

echo -e "${GREEN}✅ Code synced successfully${NC}"
echo ""

# Copy the mirror environment file
echo -e "${YELLOW}⚙️  Setting up environment configuration...${NC}"
ssh -i "$SSH_KEY" "$MIRROR_HOST" "cd $REMOTE_APP_DIR && cp .env.mirror .env"
echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

# Check if container is running and stop it
echo -e "${YELLOW}🛑 Checking for existing container...${NC}"
CONTAINER_EXISTS=$(ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker ps -a -q -f name=door-staging" || echo "")
if [ -n "$CONTAINER_EXISTS" ]; then
    echo -e "${YELLOW}   Stopping and removing existing container...${NC}"
    ssh -i "$SSH_KEY" "$MIRROR_HOST" "cd $REMOTE_APP_DIR && docker compose -f docker-compose.mirror.yml down"
    echo -e "${GREEN}✅ Existing container removed${NC}"
else
    echo -e "${BLUE}   No existing container found${NC}"
fi
echo ""

# Build and start the container
echo -e "${YELLOW}🏗️  Building and starting container...${NC}"
ssh -i "$SSH_KEY" "$MIRROR_HOST" "cd $REMOTE_APP_DIR && docker compose -f docker-compose.mirror.yml up -d --build"
echo -e "${GREEN}✅ Container started${NC}"
echo ""

# Wait for container to be healthy
echo -e "${YELLOW}⏳ Waiting for application to be ready...${NC}"
for i in {1..30}; do
    if ssh -i "$SSH_KEY" "$MIRROR_HOST" "curl -s http://localhost:8080/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is healthy and running${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Application failed to start within 30 seconds${NC}"
        echo -e "${YELLOW}   Checking logs...${NC}"
        ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker logs door-staging --tail 50"
        exit 1
    fi
    echo -e "   Attempt $i/30..."
    sleep 1
done
echo ""

# Show container status
echo -e "${YELLOW}📊 Container status:${NC}"
ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker ps -f name=door-staging"
echo ""

# Show recent logs
echo -e "${YELLOW}📋 Recent logs (last 20 lines):${NC}"
ssh -i "$SSH_KEY" "$MIRROR_HOST" "docker logs door-staging --tail 20"
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  ✅ Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Access the application at:${NC}"
echo -e "  ${GREEN}http://mirror:8080${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "  View logs:    ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'docker logs door-staging -f'${NC}"
echo -e "  Restart:      ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'cd $REMOTE_APP_DIR && docker compose -f docker-compose.mirror.yml restart'${NC}"
echo -e "  Stop:         ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'cd $REMOTE_APP_DIR && docker compose -f docker-compose.mirror.yml down'${NC}"
echo -e "  Shell access: ${YELLOW}ssh -i $SSH_KEY $MIRROR_HOST 'docker exec -it door-staging /bin/bash'${NC}"
echo ""
