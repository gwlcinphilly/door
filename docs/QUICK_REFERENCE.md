# Door Application - Quick Reference Card

## 🚀 Quick Commands

### Deploy Application to Mirror
```bash
./deploy-to-mirror.sh
```

### Sync Database to Mirror
```bash
./sync-db-to-mirror.sh
```

### Start Local Development
```bash
python main.py
```

## 🌐 Access URLs

| Environment | URL | Database |
|-------------|-----|----------|
| Local Dev | `http://localhost:8080` | Local PostgreSQL |
| Mirror Staging | `http://mirror:8080` | Neon (production) |
| Mirror Database | `mirror:5432` | PostgreSQL (Docker) |
| Production | (Your Render URL) | Neon |

## 🐳 Mirror Containers

| Container | Port | Status |
|-----------|------|--------|
| `door-staging` | 8080 | ✅ Healthy |
| `postgres-mirror` | 5432 | ✅ Healthy |

## 📊 View Logs

```bash
# Application logs
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs door-staging -f'

# Database logs
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs postgres-mirror -f'
```

## 🔄 Typical Workflow

```
1. Develop locally           → python main.py
2. Sync database to mirror   → ./sync-db-to-mirror.sh
3. Deploy app to mirror      → ./deploy-to-mirror.sh
4. Test on mirror            → http://mirror:8080
5. Push to production        → git push origin main
```

## 🗄️ Database Commands

### Connect to Mirror Database
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker exec -it postgres-mirror psql -U bdoor_user -d bdoor_postgres'
```

### Backup Mirror Database
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker exec postgres-mirror pg_dump -U bdoor_user bdoor_postgres' > backup.sql
```

## 🛠️ Container Management

### Restart Containers
```bash
# Restart app
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.mirror.yml restart'

# Restart database
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml restart'
```

### Stop Containers
```bash
# Stop app
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.mirror.yml down'

# Stop database
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml down'
```

### Check Container Status
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker ps'
```

## 🔐 SSH Access

```bash
# SSH to mirror server
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror
```

## 📚 Documentation

- **`DEPLOYMENT_SUMMARY.md`** - Complete overview
- **`MIRROR_DEPLOYMENT.md`** - Application deployment guide
- **`DATABASE_MIRROR_SETUP.md`** - Database setup guide
- **`QUICK_REFERENCE.md`** - This file

## 🆘 Quick Troubleshooting

### Application Not Working
```bash
# Check logs
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs door-staging --tail 50'

# Restart
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.mirror.yml restart'

# Redeploy
./deploy-to-mirror.sh
```

### Database Issues
```bash
# Check logs
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs postgres-mirror --tail 50'

# Restart
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml restart'

# Resync data
./sync-db-to-mirror.sh
```

### Container Not Running
```bash
# Check status
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker ps -a'

# Start manually
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.mirror.yml up -d'
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.postgres.yml up -d'
```

## 💡 Pro Tips

1. **Always sync database before testing** - Ensures mirror has latest data
2. **Check logs first** - Most issues show up in container logs
3. **Health checks work** - Containers show healthy status when working
4. **Scripts handle setup** - Just run the scripts, they handle everything
5. **Mirror is disposable** - Can always redeploy and resync

---

**Keep this handy!** Print or bookmark for quick access.
