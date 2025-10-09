# Deployment Files

This directory contains all deployment-related configuration files for the three environments.

## 📁 Files Overview

### Environment Configuration Templates

- **`env.local.example`** - Local development environment
- **`env.mirror.example`** - Mirror internal production
- **`env.render.example`** - Render cloud production

Copy the appropriate file to `.env` in the project root:

```bash
# For LOCAL
cp deployment/env.local.example .env

# For MIRROR
cp deployment/env.mirror.example .env
```

### Docker Configuration

- **`docker-compose.postgres.yml`** - Standalone PostgreSQL for LOCAL
- **`docker-compose.mirror.yml`** - Full stack for MIRROR (app + database)
- **`Dockerfile`** - Docker image for application

### Deployment Scripts

- **`deploy-to-mirror.sh`** - Deploy application to MIRROR server
- **`sync-db-to-mirror.sh`** - Sync database from LOCAL to MIRROR
- **`start.sh`** - Application startup script

### Cloud Configuration

- **`render.yaml`** - Render.com deployment configuration

## 🚀 Quick Deployment

### LOCAL Development

```bash
# 1. Copy config
cp deployment/env.local.example .env

# 2. Start database
docker-compose -f deployment/docker-compose.postgres.yml up -d

# 3. Run app
python main.py
```

### MIRROR Production

```bash
# 1. SSH to mirror
ssh root@mirror

# 2. Navigate to project
cd /q/Docker/door

# 3. Copy config
cp deployment/env.mirror.example .env

# 4. Edit config
vim .env

# 5. Deploy
docker-compose -f deployment/docker-compose.mirror.yml up -d

# 6. Check logs
docker-compose -f deployment/docker-compose.mirror.yml logs -f
```

### RENDER Production

1. Configure environment variables in Render Dashboard
2. Use values from `env.render.example`
3. Push to GitHub - Render auto-deploys

## 🔄 Database Sync

### LOCAL → MIRROR

```bash
# From LOCAL machine
cd tools
python database_sync.py --direction push
```

### MIRROR → LOCAL

```bash
# From LOCAL machine
cd tools
python database_sync.py --direction pull
```

### Smart Sync (Automatic)

```bash
# From LOCAL machine
python main.py  # Auto-syncs on startup
```

## 🐳 Docker Commands

### MIRROR Deployment

```bash
# Start services
docker-compose -f deployment/docker-compose.mirror.yml up -d

# Stop services
docker-compose -f deployment/docker-compose.mirror.yml down

# View logs
docker-compose -f deployment/docker-compose.mirror.yml logs -f

# Restart
docker-compose -f deployment/docker-compose.mirror.yml restart

# Rebuild
docker-compose -f deployment/docker-compose.mirror.yml up -d --build
```

### LOCAL Database Only

```bash
# Start PostgreSQL
docker-compose -f deployment/docker-compose.postgres.yml up -d

# Stop PostgreSQL
docker-compose -f deployment/docker-compose.postgres.yml down

# View logs
docker-compose -f deployment/docker-compose.postgres.yml logs -f
```

## 📝 Environment Variables

### Required for All Environments

```env
DB_USER=bdoor_user
DB_PASSWORD=bdoor_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bdoor_postgres
SECRET_KEY=your-secret-key
```

### RENDER Specific (Neon Database)

```env
NEON_HOST=your-project.neon.tech
NEON_USER=your-user
NEON_PASSWORD=your-password
NEON_DATABASE_NAME=your-database
AUTH_USERNAME=admin
AUTH_PASSWORD=secure-password
```

## 🔍 Verification

### Check Environment

```bash
python -c "from app.config import get_environment; print(get_environment())"
```

### Test Database Connection

```bash
python -c "from app.database import test_connection; test_connection()"
```

### View Full Environment Info

```bash
python -c "from app.config import get_environment_info; import json; print(json.dumps(get_environment_info(), indent=2))"
```

## 🔐 Security Notes

- Never commit `.env` files to git
- Use strong passwords for production
- Rotate SECRET_KEY regularly
- RENDER requires authentication on all pages
- LOCAL and MIRROR are for trusted networks only

## 📊 Monitoring

### View Logs

**LOCAL:**
```bash
tail -f logs/app.log
tail -f logs/access.log
```

**MIRROR:**
```bash
docker-compose -f deployment/docker-compose.mirror.yml logs -f
```

**RENDER:**
- View in Render Dashboard

## 🆘 Troubleshooting

### Container Won't Start

```bash
# Check container status
docker ps -a

# View container logs
docker logs <container-name>

# Check for port conflicts
netstat -an | grep :8080
```

### Database Connection Failed

```bash
# Test PostgreSQL connection
psql -U bdoor_user -d bdoor_postgres -h localhost

# Check Docker network
docker network ls
docker network inspect door_default
```

### Wrong Environment Detected

```bash
# Check hostname
hostname

# Check environment variables
env | grep -E "RENDER|NEON|DB_"
```

## 📚 Additional Resources

- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [README.md](../README.md) - Main project documentation
- [docs/](../docs/) - Additional documentation

---

**Last Updated:** October 2025

