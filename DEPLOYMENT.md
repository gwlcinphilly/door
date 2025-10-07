# FastAPI Deployment Guide

This guide explains how to deploy the Door FastAPI application to different environments.

## 📁 File Overview

### Main Application Files

- **`main.py`** - Local development server (connects to local PostgreSQL)
- **`main_render.py`** - Production deployment for Render (connects to Neon database)

### Configuration Files

- **`requirements.txt`** - Development dependencies
- **`requirements_render.txt`** - Production dependencies for Render
- **`env_example.txt`** - Environment variable template

## 🏠 Local Development

### Prerequisites

1. **PostgreSQL Database**: Install and configure local PostgreSQL
2. **Python Environment**: Python 3.8+ with virtual environment
3. **Environment Variables**: Copy `env_example.txt` to `.env`

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp env_example.txt .env
# Edit .env file to set USE_NEON=false

# 3. Start local PostgreSQL service
# (depends on your installation method)

# 4. Run the application
python main.py
```

The application will be available at `http://127.0.0.1:80`

## 🚀 Render Deployment

### Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **Neon Database**: Set up Neon PostgreSQL database
3. **GitHub Repository**: Push your code to GitHub

### Render Setup

#### 1. Create Web Service

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

```
Name: door-fastapi-app
Environment: Python 3
Build Command: pip install -r requirements_render.txt
Start Command: python main_render.py
```

#### 2. Environment Variables

Set these environment variables in Render:

```
USE_NEON=true
NEON_HOST=your-neon-host
NEON_PORT=5432
NEON_DATABASE_NAME=your-database-name
NEON_USER=your-username
NEON_PASSWORD=your-password
PORT=10000
```

#### 3. Database Setup

The application will automatically create database tables on first run.

### Database Sync

Use the database sync tool to migrate data from local to Neon:

```bash
# From project root
python fastapi_app/tools/database_sync.py --direction local-to-neon
```

## 🔧 Configuration Differences

### Local Development (`main.py`)

```python
# Runs on localhost:80
# Connects to local PostgreSQL
# Hot reload enabled
# Development-friendly settings
```

### Render Production (`main_render.py`)

```python
# Runs on Render's assigned port
# Connects to Neon database
# Hot reload disabled
# Production-optimized settings
```

## 🌐 Environment Variables

### Database Configuration

| Variable | Local Development | Render Production |
|----------|------------------|-------------------|
| `USE_NEON` | `false` | `true` |
| `DB_HOST` | `localhost` | Not used |
| `DB_PORT` | `5432` | Not used |
| `DB_NAME` | `bdoor_postgres` | Not used |
| `DB_USER` | `bdoor_user` | Not used |
| `DB_PASSWORD` | `bdoor_password` | Not used |
| `NEON_HOST` | Not used | `your-neon-host` |
| `NEON_PORT` | Not used | `5432` |
| `NEON_DATABASE_NAME` | Not used | `your-database-name` |
| `NEON_USER` | Not used | `your-username` |
| `NEON_PASSWORD` | Not used | `your-password` |

### Port Configuration

| Environment | Host | Port | Notes |
|-------------|------|------|-------|
| Local Dev | `127.0.0.1` | `80` | Standard web port for development |
| Render | `0.0.0.0` | `$PORT` | Dynamic port assigned by Render |

## 🔄 Database Migration

### From Local to Production

1. **Sync Data**: Use the database sync tool
2. **Verify Connection**: Check health endpoint
3. **Test Functionality**: Verify all features work

### Sync Commands

```bash
# Sync from local to Neon
python fastapi_app/tools/database_sync.py --direction local-to-neon

# Sync from Neon to local
python fastapi_app/tools/database_sync.py --direction neon-to-local

# Bidirectional sync
python fastapi_app/tools/database_sync.py --direction both
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check environment variables
   - Verify database credentials
   - Ensure database is accessible

2. **Port Already in Use**
   - Change port in `main.py` if needed
   - Check if another service is running

3. **Render Deployment Failed**
   - Check build logs in Render dashboard
   - Verify all dependencies are in `requirements_render.txt`
   - Ensure environment variables are set

### Health Checks

- **Local**: `http://127.0.0.1:80/health`
- **Render**: `https://your-app.onrender.com/health`

## 📝 Notes

- **Local Development**: Always use `main.py` for local development
- **Render Deployment**: Always use `main_render.py` for Render deployment
- **Database Sync**: Use tools in `fastapi_app/tools/` for data migration
