# Main Files Comparison

This document explains the differences between the two main application files.

## 📊 Quick Comparison

| Feature | `main.py` | `main_render.py` |
|---------|-----------|------------------|
| **Purpose** | Local Development | Render Production |
| **Database** | Local PostgreSQL | Neon PostgreSQL |
| **Port** | 80 | Dynamic (`$PORT`) |
| **Host** | 127.0.0.1 | 0.0.0.0 |
| **Hot Reload** | ✅ Enabled | ❌ Disabled |
| **Routers** | ✅ All included | ✅ All included |
| **Database Tables** | ✅ Auto-created | ✅ Auto-created |
| **Environment** | Development | Production |

## 🔍 Detailed Differences

### `main.py` - Local Development

```python
# Key characteristics:
- Host: "127.0.0.1" (localhost only)
- Port: 80 (standard web port)
- Reload: True (auto-reload on file changes)
- Database: Local PostgreSQL via environment variables
- Health message: "Door application is running"

# Usage:
python main.py
# Access: http://127.0.0.1:80
```

**Best for:**
- Local development and testing
- When you have local PostgreSQL running
- When you want hot reload for rapid development

### `main_render.py` - Render Production

```python
# Key characteristics:
- Host: "0.0.0.0" (accepts connections from anywhere)
- Port: int(os.environ.get("PORT", 10000)) (Render's dynamic port)
- Reload: False (production stability)
- Database: Neon PostgreSQL via environment variables
- Health message: "Door application is running on Render"

# Usage:
python main_render.py
# Access: https://your-app.onrender.com
```

**Best for:**
- Production deployment on Render
- When you want to use Neon cloud database
- When you need production-ready settings


## 🗄️ Database Configuration

### Local Development (`main.py`)
```bash
# .env file
USE_NEON=false
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bdoor_postgres
DB_USER=bdoor_user
DB_PASSWORD=bdoor_password
```

### Render Production (`main_render.py`)
```bash
# Render environment variables
USE_NEON=true
NEON_HOST=your-neon-host
NEON_PORT=5432
NEON_DATABASE_NAME=your-database-name
NEON_USER=your-username
NEON_PASSWORD=your-password
PORT=10000
```


## 🚀 Deployment Workflow

### Development → Production

1. **Develop locally** with `main.py`
2. **Sync database** from local to Neon
3. **Deploy to Render** using `main_render.py`

### Commands

```bash
# 1. Local development
python main.py

# 2. Sync data to production
python fastapi_app/tools/database_sync.py --direction local-to-neon

# 3. Deploy to Render (uses main_render.py automatically)
# Render will run: python main_render.py
```

## 🔧 Environment Setup

### For Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env_example.txt .env
# Edit .env to set USE_NEON=false

# Start local PostgreSQL
# Run the application
python main.py
```

### For Render Deployment
```bash
# Install production dependencies
pip install -r requirements_render.txt

# Set environment variables in Render dashboard
# Deploy (Render will use main_render.py)
```

## 📝 Notes

- **Always use `main.py` for local development**
- **Always use `main_render.py` for Render deployment**
- **Database sync tool works with both local and Neon databases**
- **Environment variables control database connection behavior**
