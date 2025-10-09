# 🔐 Render Environment Variables Setup

This guide shows how to securely set up environment variables for your Door application on Render.

## 🚨 Security Notice

**NEVER commit real passwords or secret keys to git!** The values below are EXAMPLES ONLY. Use your own secure credentials.

## 📋 Required Environment Variables

Set these environment variables in your Render dashboard:

### Database Configuration
```
USE_NEON=true
NEON_HOST=your-project.us-east-1.aws.neon.tech
NEON_PORT=5432
NEON_DATABASE_NAME=your-database-name
NEON_USER=your-neon-username
NEON_PASSWORD=your-secure-neon-password-here
```

### Authentication Configuration
```
SECRET_KEY=your-randomly-generated-secret-key-at-least-32-chars
ADMIN_PASSWORD=your-strong-admin-password-change-this
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
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
4. **Add each variable** with YOUR OWN secure values
5. **Save and redeploy**

### Method 2: Using render.yaml (Alternative)

If you prefer to use `render.yaml`, replace the placeholder values with real values, but **DO NOT commit them to git**.

## 🔒 Security Best Practices

### ✅ DO:
- Set environment variables in Render dashboard
- Use strong, unique passwords (at least 16 characters)
- Generate random SECRET_KEY using the command above
- Keep secret keys secure
- Use HTTPS (provided by Render)
- Change default credentials immediately

### ❌ DON'T:
- Commit passwords to git
- Share credentials in public repositories
- Use weak passwords (like "admin123")
- Store credentials in code files
- Reuse passwords across services

## 🔑 Password Requirements

**ADMIN_PASSWORD** should be:
- At least 16 characters long
- Include uppercase and lowercase letters
- Include numbers and special characters
- Unique (not used elsewhere)

## 🚀 Deployment Steps

1. **Generate secure credentials:**
   ```bash
   # Generate SECRET_KEY
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
   
   # Use a password manager to generate ADMIN_PASSWORD
   ```

2. **Set environment variables** in Render dashboard with YOUR values
3. **Set a strong ADMIN_PASSWORD** (required for security)
4. **Deploy your application**
5. **Test login** with your credentials
6. **Verify security** - ensure authentication is working

## 📞 Support

If you encounter issues:
1. Check Render build logs
2. Verify all environment variables are set correctly
3. Ensure database is accessible
4. Check authentication logs
5. Test with curl or Postman first

## 🔐 Where to Get Neon Database Credentials

1. Log into your Neon dashboard: https://console.neon.tech
2. Select your project
3. Go to "Connection Details"
4. Copy the connection string or individual credentials
5. **IMPORTANT**: Never share or commit these credentials!

---

**Remember**: Security is your responsibility. Keep your credentials safe!  
**Never use example passwords in production!**
