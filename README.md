# Door - Multi-Environment Web Application

A modern FastAPI web application for managing stocks, information, and notes with support for three deployment environments.

## 🚀 Quick Start

### Choose Your Environment

The application **automatically detects** which environment it's running in:

| Environment | Detection | Use Case |
|------------|-----------|----------|
| **LOCAL** | Hostname ≠ "mirror" | Development & testing |
| **MIRROR** | Hostname contains "mirror" | Internal production |
| **RENDER** | `RENDER` env var present | Cloud production |

### Start Development

```bash
# 1. Copy environment config
cp deployment/env.local.example .env

# 2. Start local database
docker-compose -f deployment/docker-compose.postgres.yml up -d

# 3. Run application
python main.py

# 4. Open browser
open http://localhost:8080
```

## 🌍 Three Deployment Environments

### 1. LOCAL - Development Machine

**Current Machine:** `Pi.local`

- 🎯 **Purpose**: Development and testing
- 🗄️ **Database**: Local PostgreSQL
- 🔓 **Auth**: Disabled
- 🔄 **Sync**: Pulls from Mirror
- 🔥 **Features**: All experimental features enabled

**Start:**
```bash
python main.py
```

### 2. MIRROR - Internal Production

**Server:** `mirror` (internal network)

- 🎯 **Purpose**: Stable production for internal use
- 🗄️ **Database**: PostgreSQL in Docker
- 🔓 **Auth**: Disabled (trusted network)
- 🔄 **Sync**: Syncs with Local
- ✅ **Features**: Stable features only

**Deploy:**
```bash
cd deployment
docker-compose -f docker-compose.mirror.yml up -d
```

### 3. RENDER - Cloud Production

**Platform:** Render.com

- 🎯 **Purpose**: Public access from anywhere
- 🗄️ **Database**: Neon PostgreSQL (cloud)
- 🔐 **Auth**: **REQUIRED** on all pages
- 🌐 **Access**: Public internet (authenticated)
- ✅ **Features**: Stable features only

**Deploy:** Configure in Render Dashboard (auto-deploys from GitHub)

## 📁 Project Structure

```
door/
├── app/                    # Application code
│   ├── config.py          # ⭐ Environment detection
│   ├── database.py        # Database connections
│   ├── routers/           # API endpoints
│   └── ...
│
├── deployment/            # 🚀 Deployment configs
│   ├── env.*.example     # Environment templates
│   ├── docker-compose.*  # Docker setups
│   └── ...
│
├── docs/                  # 📚 Documentation
├── tools/                 # 🛠️ Utility scripts
├── old/                   # 📦 Archived backups
├── main.py               # ⭐ Main application
└── .env                  # Your local config
```

## 🎛️ Features by Environment

| Feature | LOCAL | MIRROR | RENDER |
|---------|:-----:|:------:|:------:|
| Authentication | ❌ | ❌ | ✅ |
| Database Sync | ✅ | ✅ | ❌ |
| Hot Reload | ✅ | ❌ | ❌ |
| Debug Mode | ✅ | ❌ | ❌ |
| Experimental | ✅ | ❌ | ❌ |

## 🔧 Configuration

### Environment Files

Choose the appropriate template:

```bash
# LOCAL Development
cp deployment/env.local.example .env

# MIRROR Production
cp deployment/env.mirror.example .env

# RENDER Production
# Configure in Render Dashboard
```

### Key Settings

**LOCAL:**
```env
DB_HOST=localhost
PORT=8080
DEBUG=True
```

**MIRROR:**
```env
DB_HOST=postgres  # Docker service
PORT=8080
DEBUG=False
```

**RENDER:**
```env
NEON_HOST=your-project.neon.tech
NEON_USER=your-user
NEON_PASSWORD=your-password
AUTH_USERNAME=admin
AUTH_PASSWORD=secure-password
```

## 🔄 Database Synchronization

LOCAL and MIRROR can sync databases:

```bash
# Automatic sync (LOCAL only)
python main.py  # Syncs before starting

# Manual sync
cd tools
python database_sync.py --direction smart-sync
```

**Note:** RENDER uses independent Neon database (no sync)

## 🔍 Check Your Environment

```bash
# Check hostname
hostname

# View environment info
python -c "from app.config import get_environment_info; import json; print(json.dumps(get_environment_info(), indent=2))"

# Current environment
python -c "from app.config import get_environment; print(get_environment())"
```

## 📊 Application URLs

- **LOCAL**: http://localhost:8080
- **MIRROR**: http://mirror:8080 (internal)
- **RENDER**: https://your-app.onrender.com

## 🐛 Troubleshooting

### Wrong Environment Detected

Check your hostname:
```bash
hostname
# Should contain "mirror" for MIRROR environment
```

### Database Connection Failed

**LOCAL:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres
psql -U bdoor_user -d bdoor_postgres -h localhost
```

**MIRROR:**
```bash
# Check Docker containers
docker-compose -f deployment/docker-compose.mirror.yml ps
docker-compose logs postgres
```

**RENDER:**
- Verify Neon credentials in Render Dashboard
- Check Render logs for connection errors

### View Logs

```bash
# LOCAL/MIRROR
tail -f logs/app.log
tail -f logs/access.log

# RENDER
# View in Render Dashboard
```

## 📚 Documentation

- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - Quick start and common tasks
- **[docs/REORGANIZATION_SUMMARY.md](docs/REORGANIZATION_SUMMARY.md)** - Project reorganization details
- **[docs/](docs/)** - All documentation files
- **[tools/DATABASE_SYNC_README.md](tools/DATABASE_SYNC_README.md)** - Database sync details

## 🔐 Security

- **LOCAL**: No authentication (development only)
- **MIRROR**: No authentication (internal network)
- **RENDER**: **Authentication required** on ALL pages

## 🛠️ Development Workflow

1. **Develop** on LOCAL machine
   ```bash
   python main.py
   # Edit code, hot reload enabled
   ```

2. **Deploy** to MIRROR for testing
   ```bash
   ssh root@mirror
   cd /q/Docker/door
   docker-compose -f deployment/docker-compose.mirror.yml up -d
   ```

3. **Sync** database changes
   ```bash
   # On LOCAL
   cd tools
   python database_sync.py --direction smart-sync
   ```

4. **Deploy** to RENDER for production
   ```bash
   git push origin main
   # Render auto-deploys
   ```

## 🆘 Getting Help

1. Check environment detection: `from app.config import get_environment_info`
2. Review logs: `logs/app.log` and `logs/access.log`
3. Verify configuration: Check `.env` file
4. Read documentation: `DEPLOYMENT_GUIDE.md`

## 📦 Dependencies

- Python 3.8+
- PostgreSQL 14+
- FastAPI
- SQLAlchemy
- Docker (for MIRROR)

Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Features

- 📊 Stock management
- 📝 Information tracking
- 📋 Notes organization
- 🔄 Multi-environment support
- 🔐 Secure authentication (RENDER)
- 🗄️ Database synchronization
- 📱 Responsive web interface

## 📄 License

Proprietary - Internal Use Only

---

**Version:** 2.0.0  
**Last Updated:** October 2025  
**Current Host:** `Pi.local` (LOCAL environment)

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

