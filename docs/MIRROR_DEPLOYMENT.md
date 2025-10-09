# Mirror Deployment Guide

This guide explains the three-tier deployment setup for the Door FastAPI application.

## 🏗️ Deployment Architecture

### Three Environments

1. **Local Development** (`main.py`)
   - Uses local PostgreSQL database
   - Hot reload enabled
   - Runs on `localhost:8080`
   - For active development and testing

2. **Mirror Staging** (Docker on mirror server)
   - Uses Neon PostgreSQL database (same as production)
   - Runs in Docker container
   - Accessible at `http://mirror:8080`
   - For staging/testing before pushing to production

3. **Production** (Render + Neon)
   - Uses Neon PostgreSQL database
   - Deployed via GitHub → Render
   - Public production environment

## 🔄 Development Workflow

```
Local Dev → Test locally → Deploy to Mirror → Test on Mirror → Push to GitHub → Auto-deploy to Render
```

### Step-by-Step Workflow

1. **Develop Locally**
   ```bash
   cd /Users/qianglu/Code/git/door
   python main.py
   ```
   - Make changes to your code
   - Test with local PostgreSQL database
   - Verify everything works locally

2. **Deploy to Mirror for Staging**
   ```bash
   ./deploy-to-mirror.sh
   ```
   - Syncs your local code to mirror server
   - Builds and runs Docker container
   - Uses Neon database (same as production)
   - Access at: `http://mirror:8080`

3. **Test on Mirror**
   - Verify the application works with Neon database
   - Test in an environment similar to production
   - Check logs if needed: `ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs door-staging -f'`

4. **Push to Production**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```
   - Render automatically deploys from GitHub
   - Production site updates with your changes

## 📦 Files Created

### Deployment Files

- **`Dockerfile`** - Container definition for the FastAPI app
- **`.env.mirror`** - Environment configuration for mirror (uses Neon DB)
- **`docker-compose.mirror.yml`** - Docker Compose configuration for mirror
- **`deploy-to-mirror.sh`** - Automated deployment script

### SSH Configuration

- SSH key created: `~/.ssh/id_ed25519_mirror_root`
- Passwordless access to: `root@mirror`

## 🚀 Quick Commands

### Deploy to Mirror
```bash
cd /Users/qianglu/Code/git/door
./deploy-to-mirror.sh
```

### View Mirror Logs
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs door-staging -f'
```

### Restart Mirror Container
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.mirror.yml restart'
```

### Stop Mirror Container
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.mirror.yml down'
```

### Access Mirror Container Shell
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker exec -it door-staging /bin/bash'
```

### Check Mirror Container Status
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker ps -f name=door-staging'
```

## 🗄️ Database Configuration

### Local Development
- Host: `localhost`
- Port: `5432`
- Database: `bdoor_postgres`
- User: `bdoor_user`
- Set in `.env`: `USE_NEON=false`

### Mirror Staging & Production
- Host: `ep-icy-violet-adv1dwix.c-2.us-east-1.aws.neon.tech`
- Port: `5432`
- Database: `neondb`
- User: `neondb_owner`
- Set in `.env.mirror`: `USE_NEON=true`

## 🔍 Troubleshooting

### Deployment Failed

Check the deployment script output for errors:
```bash
./deploy-to-mirror.sh
```

### Container Not Starting

Check container logs:
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'docker logs door-staging'
```

### Database Connection Issues

1. Verify `.env.mirror` has correct Neon credentials
2. Check if Neon database is accessible
3. Review container logs for database errors

### Port Already in Use

Check what's using port 8080:
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'lsof -i :8080'
```

Stop the conflicting container:
```bash
ssh -i ~/.ssh/id_ed25519_mirror_root root@mirror 'cd /opt/door && docker compose -f docker-compose.mirror.yml down'
```

## 🎯 Benefits of This Setup

1. **Safe Testing** - Test with production database before going live
2. **Fast Iteration** - Quick deployment to staging without GitHub push
3. **Isolated Environments** - Local, staging, and production are separate
4. **Easy Rollback** - Mirror staging doesn't affect production
5. **Database Parity** - Staging uses same Neon DB as production

## 📝 Notes

- **Mirror staging** shares the Neon database with production, so be careful with data modifications
- The deploy script automatically rebuilds the container to include latest code changes
- Hot reload is enabled in the container for faster iteration during staging
- Health checks ensure the application is running before marking deployment as successful
- All containers use non-root user for security

## 🔐 Security

- SSH access uses key-based authentication (no passwords)
- Container runs as non-root user (appuser)
- Database credentials stored in `.env.mirror` (not committed to git)
- `.gitignore` configured to exclude sensitive files
