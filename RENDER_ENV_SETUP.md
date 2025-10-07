# 🔐 Render Environment Variables Setup

This guide shows how to securely set up environment variables for your Door application on Render.

## 🚨 Security Notice

**NEVER commit real passwords or secret keys to git!** The `render.yaml` file contains placeholder values only.

## 📋 Required Environment Variables

Set these environment variables in your Render dashboard:

### Database Configuration
```
USE_NEON=true
NEON_HOST=ep-icy-violet-adv1dwix.c-2.us-east-1.aws.neon.tech
NEON_PORT=5432
NEON_DATABASE_NAME=neondb
NEON_USER=neondb_owner
NEON_PASSWORD=npg_EntrThk1V8KI
```

### Authentication Configuration
```
SECRET_KEY=QkUqe3w0afBLrDIza80p-49-aNsQyOcEQDEw9hCLU4g
ADMIN_PASSWORD=admin123
```

### System Configuration
```
PYTHON_VERSION=3.11.0
```

## 🛠️ How to Set Environment Variables in Render

### Method 1: Render Dashboard (Recommended)

1. **Go to your Render dashboard**
2. **Select your web service** (door-fastapi-app)
3. **Click "Environment" tab**
4. **Add each variable** with the exact values above
5. **Save and redeploy**

### Method 2: Using render.yaml (Alternative)

If you prefer to use `render.yaml`, replace the placeholder values with real values, but **DO NOT commit them to git**.

## 🔒 Security Best Practices

### ✅ DO:
- Set environment variables in Render dashboard
- Use strong, unique passwords
- Keep secret keys secure
- Use HTTPS (provided by Render)

### ❌ DON'T:
- Commit passwords to git
- Share credentials in public repositories
- Use weak passwords
- Store credentials in code files

## 🔑 Default Credentials

```
Username: admin
Password: admin123 (or your custom ADMIN_PASSWORD)
```

## 🚀 Deployment Steps

1. **Set environment variables** in Render dashboard
2. **Deploy your application**
3. **Test login** with admin credentials
4. **Change default password** if needed

## 📞 Support

If you encounter issues:
1. Check Render build logs
2. Verify all environment variables are set
3. Ensure database is accessible
4. Check authentication logs

---

**Remember**: Security is your responsibility. Keep your credentials safe!
