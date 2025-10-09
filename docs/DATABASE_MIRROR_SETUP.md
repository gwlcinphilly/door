# Mirror PostgreSQL Database Setup

## 📊 Overview

This setup creates a PostgreSQL database container on the mirror server and provides a sync script to replicate data from your local database to the mirror database.

## 🗄️ Database Architecture

```
┌─────────────────────┐
│  Local PostgreSQL   │
│  (Development)      │
│  localhost:5432     │
└──────────┬──────────┘
           │
           │ sync-db-to-mirror.sh
           │
           ▼
┌─────────────────────┐
│  Mirror PostgreSQL  │
│  (Staging/Testing)  │
│  mirror:5432        │
│  Docker Container   │
└─────────────────────┘
```

## ✅ What Was Created

### 1. Docker Configuration
- **`docker-compose.postgres.yml`** - PostgreSQL container configuration
  - Image: `postgres:16`
  - Container: `postgres-mirror`
  - Port: `5432`
  - Persistent volume for data
  - Health checks enabled

### 2. Sync Script
- **`sync-db-to-mirror.sh`** - Automated database sync script
  - Dumps local database using `pg_dump`
  - Transfers dump to mirror via SSH
  - Restores to PostgreSQL container
  - Verifies sync by counting tables
  - Cleans up temporary files

## 🚀 Quick Start

### Sync Database to Mirror
```bash
cd /Users/qianglu/Code/git/door
./sync-db-to-mirror.sh
```

The script will:
1. ✅ Check local database connection
2. ✅ Check SSH connection to mirror
3. ✅ Start PostgreSQL container if needed
4. ✅ Dump local database
5. ✅ Transfer dump to mirror
6. ✅ Restore database on mirror
7. ✅ Verify sync
8. ✅ Clean up temporary files

## 📋 Database Details

### Local PostgreSQL
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `bdoor_postgres`
- **User:** `bdoor_user`
- **Password:** `bdoor_password`

### Mirror PostgreSQL (Docker)
- **Host:** `mirror` (or mirror's IP)
- **Port:** `5432`
- **Database:** `bdoor_postgres`
- **User:** `bdoor_user`
- **Password:** `bdoor_password`
- **Container:** `postgres-mirror`

## 🔧 Common Operations

### Check Container Status
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker ps -f name=postgres-mirror'
```

### View Container Logs
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs postgres-mirror -f'
```

### Connect to Database (via SSH)
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker exec -it postgres-mirror psql -U bdoor_user -d bdoor_postgres'
```

### Connect to Database (from local machine)
If you have network access to mirror:
```bash
PGPASSWORD=bdoor_password psql -h mirror -p 5432 -U bdoor_user -d bdoor_postgres
```

### Restart PostgreSQL Container
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml restart'
```

### Stop PostgreSQL Container
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml down'
```

### Start PostgreSQL Container
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml up -d'
```

### View Container Stats
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker stats postgres-mirror --no-stream'
```

## 🔄 Typical Workflow

### 1. Develop Locally
```bash
# Work with local PostgreSQL database
python main.py
# Make changes, add data, test features
```

### 2. Sync Database to Mirror
```bash
# When ready to test on mirror
./sync-db-to-mirror.sh
```

### 3. Test on Mirror
- Mirror database now has same data as local
- Test your application with mirror database
- Verify everything works as expected

### 4. Repeat as Needed
- Continue development locally
- Sync to mirror when you want to test
- Database on mirror always reflects latest local data

## 📊 Data Sync Details

### What Gets Synced
- ✅ All tables and their data
- ✅ Sequences and their current values
- ✅ Indexes
- ✅ Constraints
- ✅ Table structure/schema

### What Doesn't Get Synced
- ❌ PostgreSQL roles/users (uses container's default)
- ❌ Database settings (uses container's defaults)

### Sync Strategy
- The script uses `pg_dump` with `--clean --if-exists` flags
- This means: **Mirror database is completely replaced**
- Any data on mirror that's not in local will be **lost**
- This is intentional - mirror should match local exactly

## 🔍 Troubleshooting

### Sync Script Fails: "Cannot connect to local database"
**Solution:** Ensure local PostgreSQL is running
```bash
# Check PostgreSQL status (macOS)
brew services list | grep postgresql

# Start if needed
brew services start postgresql@14
```

### Sync Script Fails: "Container not starting"
**Solution:** Check container logs
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs postgres-mirror'
```

### Container Won't Start: "Port already in use"
**Solution:** Check what's using port 5432 on mirror
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'lsof -i :5432'
```

### Database Connection from Local Machine Fails
**Solution:** Check network connectivity
```bash
# Test if port is accessible
nc -zv mirror 5432
```

### Data Doesn't Match After Sync
**Solution:** Run sync again and check output
```bash
./sync-db-to-mirror.sh
# Script shows table counts for verification
```

## 💾 Data Persistence

- Database data is stored in Docker volume: `postgres_mirror_data`
- Data persists across container restarts
- Data is lost if you run `docker compose down -v` (with -v flag)
- To preserve data, use `docker compose down` (without -v)

### Backup Mirror Database
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker exec postgres-mirror pg_dump -U bdoor_user bdoor_postgres' > mirror_backup_$(date +%Y%m%d).sql
```

### Restore from Backup
```bash
cat mirror_backup_20251008.sql | ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker exec -i postgres-mirror psql -U bdoor_user -d bdoor_postgres'
```

## 🔐 Security Notes

- ✅ Database runs in isolated Docker container
- ✅ Only port 5432 exposed (can be limited by firewall)
- ✅ Database password stored in compose file (not in git)
- ⚠️  For production, consider using secrets management
- ⚠️  Database credentials are the same as local (acceptable for staging)

## 📝 Notes

- **Mirror database is for staging/testing only**
- Database can be synced as many times as needed
- Each sync completely replaces mirror database
- Container auto-restarts unless manually stopped
- Health checks ensure database is always ready
- Volume ensures data persists across restarts

## 🎯 Best Practices

1. **Sync Regularly** - Keep mirror in sync with local development
2. **Test Before Production** - Use mirror to test database changes
3. **Backup Important Data** - If mirror has unique data, back it up first
4. **Monitor Logs** - Check container logs if issues arise
5. **Clean Syncs** - Let the script do full clean syncs for consistency

## 🆘 Emergency Recovery

### Container Crashed or Won't Start
```bash
# Stop and remove container
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml down'

# Start fresh
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml up -d'

# Restore data
./sync-db-to-mirror.sh
```

### Lost All Data
```bash
# Sync from local (this is your source of truth)
./sync-db-to-mirror.sh
```

### Container Deleted
```bash
# Redeploy and sync
./sync-db-to-mirror.sh
# Script will recreate container automatically
```

---

**Created:** October 8, 2025
**Mirror PostgreSQL:** ✅ Running and Healthy
**Container:** postgres-mirror on mirror:5432
**Data:** Synced with 24 tables and all sequences
