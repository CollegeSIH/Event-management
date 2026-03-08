# 🔐 EventHub API Keys & Security Summary

## Currently Used Keys/Secrets

### 1. **JWT_SECRET** (Authentication)
**Status:** ✅ Configured with default value  
**Location:** `backend/app.py` line 20  
**Current Value:** `'your-secret-key-change-in-production'`
**Purpose:** Signing and verifying JWT authentication tokens
**Usage:**
```python
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
```

**⚠️ Important:** The current default value should be changed for production!

---

### 2. **Email Service Credentials** (SMTP)
**Status:** ⚠️ Not configured (development mode)  
**Location:** `backend/.env`  
**Currently Active:** NONE (all commented out)

**Available Options:**

#### Option A: Gmail
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=your-email@gmail.com
```

#### Option B: SendGrid
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=your-verified-sender@yourdomain.com
```

#### Option C: Other SMTP Providers
```
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
FROM_EMAIL=noreply@yourdomain.com
```

**Current Status:** Development mode - verification codes logged to console

---

### 3. **MongoDB Connection** (Optional)
**Status:** ⚠️ Not configured  
**Location:** `backend/app.py` line 19  
**Current Value:** `'mongodb://localhost:27017'`
**Purpose:** Optional database storage (currently using CSV)
**Configuration:**
```python
USE_MONGO = os.getenv('USE_MONGO', 'false')  # Set to 'true' to enable
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
```

---

## Security Checklist

### ✅ What's Implemented
- [x] JWT-based authentication
- [x] Token expiration (24 hours)
- [x] Protected API endpoints
- [x] CORS support
- [x] Email verification system

### ⚠️ What Needs Configuration for Production
- [ ] Change JWT_SECRET to a strong random value
- [ ] Configure SMTP credentials for real email sending
- [ ] Use HTTPS instead of HTTP
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add request validation

### 🔧 How to Configure

#### Step 1: Change JWT Secret
Edit `backend/.env` or set environment variable:
```bash
export JWT_SECRET=your-super-secret-random-key-here
```

Generate a secure secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 2: Configure Email (Optional)
Edit `backend/.env`:
```bash
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### Step 3: Enable MongoDB (Optional)
```bash
USE_MONGO=true
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/eventhub
```

---

## Current Security Level

| Component | Status | Notes |
|-----------|--------|-------|
| JWT Secret | ⚠️ Default | Uses placeholder value |
| Email Creds | ⚠️ None | Development mode only |
| Database | ✅ CSV | Secure for dev, upgrade for production |
| API Auth | ✅ Protected | All endpoints require JWT token |
| CORS | ✅ Enabled | Allows localhost:3000 |
| Data Encryption | ❌ None | Add HTTPS in production |

---

## No Third-Party API Keys Currently Used

The application **does NOT require**:
- ❌ OpenAI/AI API keys
- ❌ Payment processing keys (Stripe, PayPal)
- ❌ Cloud storage keys (AWS S3, Azure)
- ❌ Analytics keys (Google Analytics, Mixpanel)
- ❌ External service keys

It only uses:
- ✅ Internal JWT secret
- ✅ Optional SMTP credentials (for email)
- ✅ Optional MongoDB connection string

---

## Production Recommendations

### Before Deploying:
1. **Generate Strong JWT Secret**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Configure Email Service**
   - Choose Gmail, SendGrid, or other SMTP provider
   - Generate API key/app password
   - Add to `.env` file

3. **Enable HTTPS**
   - Use SSL certificates
   - Update CORS_ORIGIN in code

4. **Database Migration** (Optional)
   - Migrate from CSV to MongoDB for better scalability
   - Set MongoDB connection string

5. **Environment Variables**
   - Never commit `.env` to git
   - Use `.env.example` template for developers
   - Set production env vars on server

---

## Testing API Keys

To verify current configuration:
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('JWT_SECRET configured:', bool(os.getenv('JWT_SECRET')))
print('SMTP_USERNAME configured:', bool(os.getenv('SMTP_USERNAME')))
print('MONGO_URI configured:', bool(os.getenv('MONGO_URI')))
print('USE_MONGO enabled:', os.getenv('USE_MONGO', 'false').lower() == 'true')
"
```

---

## Summary

**Current Status:** 🟡 Development Ready
- All required keys for development are in place
- No real API keys needed for basic testing
- Ready for production after configuration