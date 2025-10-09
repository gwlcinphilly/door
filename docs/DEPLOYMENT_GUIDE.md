# Door Application - Multi-Environment Deployment Guide

## 🌍 Overview

The Door application supports **three deployment environments** with automatic detection and environment-specific configurations:

1. **LOCAL** - Development machine for testing and development
2. **MIRROR** - Internal production server with stable features
3. **RENDER** - Cloud production with authenticated access

## 📁 Project Structure

```
door/
├── app/                          # Main application code
│   ├── config.py                 # ⭐ Environment detection & configuration
│   ├── database.py               # Database connections (auto-configured)
│   ├── models.py                 # Database models
│   ├── routers/                  # API endpoints
│   └── source/                   # External integrations
│
├── deployment/                   # 🚀 Deployment configurations
│   ├── env.local.example         # Local dev environment config
│   ├── env.mirror.example        # Mirror production config
│   ├── env.render.example        # Render cloud config
│   ├── docker-compose.mirror.yml # Mirror Docker setup
│   ├── docker-compose.postgres.yml
│   ├── Dockerfile                # Docker image
│   ├── deploy-to-mirror.sh       # Mirror deployment script
│   ├── sync-db-to-mirror.sh      # Database sync script
│   ├── render.yaml               # Render configuration
│   └── start.sh                  # Startup script
│
├── docs/                         # 📚 Documentation
│   ├── DATABASE_MIRROR_SETUP.md
│   ├── DEPLOYMENT.md
│   └── ...
│
├── tools/                        # 🛠️ Utility scripts
│   └── database_sync.py          # Database synchronization
│
├── old/                          # 📦 Archived backups
│   └── ...
│
├── static/                       # Static assets (CSS, JS)
├── templates/                    # HTML templates
├── logs/                         # Application logs
├── main.py                       # ⭐ Main application (auto-detects env)
└── main_render.py                # Render compatibility wrapper
```

## 🔍 Environment Detection

The application **automatically detects** which environment it's running in:

### Detection Priority

1. **MIRROR** - If hostname contains "mirror"
2. **RENDER** - If `RENDER` env var exists or Neon database configured
3. **LOCAL** - Default for all other cases

### Manual Detection

Check your current environment:

```python
from app.config import get_environment, get_environment_info

print(get_environment())  # Returns: 'local', 'mirror', or 'render'
print(get_environment_info())  # Detailed detection info
```

## 🚀 Deployment Environments

### 1. LOCAL - Development Machine

**Purpose:** Development, testing, and unstable features

**Characteristics:**
- 🏠 Hostname: NOT "mirror" (e.g., "Pi.local", "macbook.local")
- 🗄️ Database: Local PostgreSQL
- 🔓 Auth: Disabled (no login required)
- 🔄 Sync: Pulls from MIRROR server
- 🔥 Hot Reload: Enabled
- 🐛 Debug: Full debug mode

**Setup:**

```bash
# 1. Copy environment config
cp deployment/env.local.example .env

# 2. Edit .env with your local database credentials
vim .env

# 3. Start local PostgreSQL
docker-compose -f deployment/docker-compose.postgres.yml up -d

# 4. Run application
python main.py
```

**Configuration Features:**
- Authentication: ❌ Disabled
- Database Sync: ✅ Enabled (from Mirror)
- Hot Reload: ✅ Enabled
- Experimental Features: ✅ Enabled
- Port: 8080

---

### 2. MIRROR - Internal Production Server

**Purpose:** Stable production environment for internal network

**Characteristics:**
- 🏠 Hostname: Contains "mirror"
- 🗄️ Database: PostgreSQL in Docker container
- 🔓 Auth: Disabled (trusted internal network)
- 🔄 Sync: Syncs with LOCAL dev
- 🎯 Features: Full stable features
- 📊 Monitoring: Enabled

**Setup:**

```bash
# On the mirror server:

# 1. Copy environment config
cp deployment/env.mirror.example .env

# 2. Edit .env (database will be in Docker)
vim .env

# 3. Deploy with Docker
cd deployment
docker-compose -f docker-compose.mirror.yml up -d

# 4. Check logs
docker-compose -f docker-compose.mirror.yml logs -f
```

**Configuration Features:**
- Authentication: ❌ Disabled (internal network)
- Database Sync: ✅ Enabled (with Local)
- SSL: ❌ (use reverse proxy)
- Full Features: ✅ Enabled
- Stable Build: ✅ Only stable features
- Port: 8080

---

### 3. RENDER - Cloud Production

**Purpose:** Public-facing production with secure access

**Characteristics:**
- ☁️ Platform: Render.com
- 🗄️ Database: Neon PostgreSQL (cloud)
- 🔐 Auth: **REQUIRED** on all pages
- 🌐 Access: Public internet
- 🔒 SSL: Enabled
- 🚫 Sync: Disabled (cloud DB is independent)

**Setup:**

1. **Create Render Web Service:**
   - Go to https://render.com
   - Create new "Web Service"
   - Connect your GitHub repository
   - Use `deployment/render.yaml` for configuration

2. **Configure Environment Variables:**
   In Render Dashboard, set these:

   ```
   # Neon Database (from Neon dashboard)
   NEON_HOST=your-project.neon.tech
   NEON_USER=your-username
   NEON_PASSWORD=your-password
   NEON_DATABASE_NAME=your-database
   
   # Authentication (REQUIRED)
   AUTH_USERNAME=your-admin-username
   AUTH_PASSWORD=your-secure-password
   SECRET_KEY=your-random-secret-key
   
   # Optional
   USE_NEON=true
   ```

3. **Deploy:**
   - Render will automatically deploy on git push
   - Or manually deploy from dashboard

**Configuration Features:**
- Authentication: ✅ **REQUIRED** (all pages)
- SSL: ✅ Enabled
- CORS: ✅ Restricted
- Database: ☁️ Neon Cloud PostgreSQL
- Monitoring: ✅ Enabled
- Port: 10000 (auto-configured)

## 🎛️ Feature Flags

Each environment has different features enabled automatically:

| Feature | LOCAL | MIRROR | RENDER |
|---------|-------|--------|--------|
| Authentication | ❌ | ❌ | ✅ |
| Database Sync | ✅ | ✅ | ❌ |
| Hot Reload | ✅ | ❌ | ❌ |
| Debug Mode | ✅ | ❌ | ❌ |
| SSL | ❌ | ❌ | ✅ |
| Experimental Features | ✅ | ❌ | ❌ |
| Production Monitoring | ❌ | ✅ | ✅ |

### Using Feature Flags in Code

```python
from app.config import get_feature_status, requires_auth

# Check if feature is available
if get_feature_status('experimental_features'):
    # This code only runs in LOCAL
    enable_experimental_ui()

# Check if auth is required
if requires_auth():
    # This code only runs in RENDER
    verify_user_session()
```

## 🔄 Database Synchronization

### LOCAL ↔️ MIRROR Sync

The LOCAL and MIRROR environments can sync their databases:

```bash
# On LOCAL machine:
cd tools
python database_sync.py --direction smart-sync

# Sync automatically runs on LOCAL startup
python main.py  # Auto-syncs before starting
```

### RENDER Database

RENDER uses a separate Neon cloud database and does NOT sync with LOCAL/MIRROR.
This keeps cloud data independent from internal data.

## 📝 Environment Configuration Files

### Creating .env Files

1. **For LOCAL:**
   ```bash
   cp deployment/env.local.example .env
   ```

2. **For MIRROR:**
   ```bash
   cp deployment/env.mirror.example .env
   ```

3. **For RENDER:**
   Configure in Render Dashboard (don't use .env file)

## 🐛 Debugging

### Check Current Environment

```bash
# From Python
python -c "from app.config import get_environment_info; import json; print(json.dumps(get_environment_info(), indent=2))"

# Check hostname
hostname

# View environment info in logs
python main.py  # Check startup logs
```

### Common Issues

**Issue: Application detects wrong environment**

Solution: Check hostname and environment variables
```bash
hostname  # Should contain "mirror" for MIRROR environment
echo $RENDER  # Should be set for RENDER environment
```

**Issue: Database connection fails**

Solution: Check database configuration for your environment
```bash
# LOCAL: Check local PostgreSQL is running
psql -U bdoor_user -d bdoor_postgres -h localhost

# MIRROR: Check Docker container
docker ps | grep postgres

# RENDER: Verify Neon credentials in Render dashboard
```

## 🚦 Quick Start

### LOCAL Development
```bash
cp deployment/env.local.example .env
docker-compose -f deployment/docker-compose.postgres.yml up -d
python main.py
# Open http://localhost:8080
```

### MIRROR Production
```bash
# On mirror server
cp deployment/env.mirror.example .env
cd deployment
docker-compose -f docker-compose.mirror.yml up -d
# Access via http://mirror:8080
```

### RENDER Production
```bash
# Configure in Render Dashboard
# Push to GitHub
git push origin main
# Render auto-deploys
```

## 📊 Monitoring

- **LOCAL**: Check `logs/app.log` and `logs/access.log`
- **MIRROR**: `docker-compose logs -f`
- **RENDER**: View logs in Render Dashboard

## 🔐 Security Notes

- **LOCAL**: No authentication (trusted dev machine)
- **MIRROR**: No authentication (trusted internal network)
- **RENDER**: **Authentication required** on ALL pages

## 📚 Additional Documentation

- `docs/DATABASE_MIRROR_SETUP.md` - Database architecture
- `docs/DEPLOYMENT.md` - Detailed deployment guide
- `docs/SECURITY_CHECKLIST.md` - Security configuration
- `tools/DATABASE_SYNC_README.md` - Database sync details

## 🆘 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review environment detection with `get_environment_info()`
3. Verify .env configuration matches your environment

---

**Last Updated:** October 2025
**Version:** 2.0.0

