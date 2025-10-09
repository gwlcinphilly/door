# Door Application - Quick Start Guide

## 🎯 Your Current Environment: LOCAL (Pi.local)

The application is running on your **LOCAL development machine**.

## ⚡ Quick Commands

### Start Development Server
```bash
python main.py
# Opens on http://localhost:8080
```

### Check Environment
```bash
python check_environment.py
```

### Start Database (if not running)
```bash
docker-compose -f deployment/docker-compose.postgres.yml up -d
```

### Sync Database from Mirror
```bash
cd tools
python database_sync.py --direction pull
```

## 🌍 Three Environments Explained

### 🟡 LOCAL (You are here!)
- **Machine:** Your development machine (Pi.local)
- **Database:** Local PostgreSQL
- **Auth:** No login required
- **Purpose:** Development and testing

### 🟢 MIRROR
- **Machine:** Internal server (hostname: "mirror")
- **Database:** PostgreSQL in Docker
- **Auth:** No login required (trusted network)
- **Purpose:** Stable internal production

### 🔵 RENDER
- **Platform:** Render.com (cloud)
- **Database:** Neon PostgreSQL
- **Auth:** Login REQUIRED
- **Purpose:** Public internet access

## 📋 Common Tasks

### 1. Start Development
```bash
# Make sure database is running
docker ps | grep postgres

# Start application
python main.py
```

### 2. Check Configuration
```bash
# View detailed environment info
python check_environment.py

# Quick environment check
python -c "from app.config import get_environment; print(get_environment())"
```

### 3. Sync with Mirror
```bash
# Pull latest data from mirror
cd tools
python database_sync.py --direction pull

# Push local changes to mirror
python database_sync.py --direction push

# Smart sync (auto-detect direction)
python database_sync.py --direction smart-sync
```

### 4. View Logs
```bash
# Application logs
tail -f logs/app.log

# Access logs
tail -f logs/access.log
```

## 🔄 Typical Development Workflow

1. **Start your day:**
   ```bash
   python main.py  # Auto-syncs database from mirror
   ```

2. **Develop features:**
   - Edit code
   - Hot reload is enabled
   - No authentication required
   - Full debug mode

3. **Test on Mirror:**
   ```bash
   # Deploy to mirror
   rsync -avz --progress -e "ssh -i ~/.ssh/id_ed25519_mirror_root" \
     --exclude 'venv/' --exclude '__pycache__/' --exclude 'logs/' \
     /Users/qianglu/Code/git/door/ root@mirror:/q/Docker/door/
   
   # Restart mirror service
   ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror \
     "cd /q/Docker/door/deployment && docker-compose -f docker-compose.mirror.yml restart"
   ```

4. **Deploy to Render:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   # Render auto-deploys
   ```

## 📁 Important Files

### Configuration
- `.env` - Your local configuration
- `deployment/env.*.example` - Config templates

### Main Application
- `main.py` - Start application (use this!)
- `app/config.py` - Environment detection
- `app/database.py` - Database connections

### Documentation
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `README.md` - Project overview
- `deployment/README.md` - Deployment files guide

### Tools
- `check_environment.py` - Verify environment
- `tools/database_sync.py` - Database synchronization

## 🎛️ Features Available in LOCAL

✅ **Enabled:**
- Hot reload (code changes auto-reload)
- Debug mode (detailed error messages)
- Debug toolbar
- Experimental features
- Database sync with mirror
- Full file access
- All external APIs

❌ **Disabled:**
- Authentication (no login needed)
- SSL (not needed for dev)
- Production monitoring
- CORS restrictions

## 🐛 Troubleshooting

### Application won't start
```bash
# Check if database is running
docker ps | grep postgres

# Start database
docker-compose -f deployment/docker-compose.postgres.yml up -d

# Check database connection
python -c "from app.database import test_connection; test_connection()"
```

### Wrong environment detected
```bash
# Check hostname
hostname
# Should NOT contain "mirror" for LOCAL

# Check environment variables
env | grep -E "RENDER|NEON"
# Should be empty for LOCAL
```

### Database sync fails
```bash
# Test SSH connection to mirror
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror

# Check mirror database is running
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror \
  "docker ps | grep postgres"
```

## 📊 Monitoring

### Check Application Status
```bash
# Is it running?
curl http://localhost:8080/health

# View logs
tail -f logs/app.log

# Check database
python -c "from app.database import test_connection; test_connection()"
```

### View Environment Details
```bash
python check_environment.py
```

## 🚀 Next Steps

1. **Read the guides:**
   - `DEPLOYMENT_GUIDE.md` - Comprehensive deployment info
   - `README.md` - Project overview
   - `deployment/README.md` - Deployment specifics

2. **Configure your environment:**
   ```bash
   vim .env  # Edit local configuration
   ```

3. **Start developing:**
   ```bash
   python main.py
   ```

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start app | `python main.py` |
| Check env | `python check_environment.py` |
| Start DB | `docker-compose -f deployment/docker-compose.postgres.yml up -d` |
| Sync DB | `cd tools && python database_sync.py --direction smart-sync` |
| View logs | `tail -f logs/app.log` |
| Test DB | `python -c "from app.database import test_connection; test_connection()"` |

## 🆘 Getting Help

1. Check environment: `python check_environment.py`
2. View logs: `tail -f logs/app.log`
3. Read docs: `DEPLOYMENT_GUIDE.md`
4. Test connection: Database, Mirror, Network

---

**Your Current Setup:**
- Environment: LOCAL
- Hostname: Pi.local
- Database: Local PostgreSQL
- Port: 8080
- Auth: Disabled

**Ready to start:** `python main.py`

