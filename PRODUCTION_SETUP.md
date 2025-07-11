# iMarket Production Deployment Guide

## Required Environment Variables for Production

### 🔐 Critical Security Credentials

#### 1. **Django Secret Key** (REQUIRED)
```bash
DJANGO_SECRET_KEY=your-super-secret-django-key-here-make-it-long-and-random
```
- **How to get**: Generate at https://djecrety.ir/
- **Security**: Must be unique, long, and kept secret
- **Impact**: Used for cryptographic signing

#### 2. **Debug Mode** (REQUIRED)
```bash
DJANGO_DEBUG=False
```
- **Production Value**: Always `False`
- **Security**: Never set to `True` in production

#### 3. **Allowed Hosts** (REQUIRED)
```bash
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
```
- **Format**: Comma-separated list
- **Include**: Your domain name(s) and server IP

### 🗄️ Database Configuration (REQUIRED)

#### PostgreSQL (Recommended)
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=imarket_production
DB_USER=your_db_username
DB_PASSWORD=your_secure_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 📧 Email Configuration (REQUIRED for OTP)

#### Gmail SMTP - ✅ CONFIGURED
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=adeniyiokunoye202020@gmail.com
EMAIL_HOST_PASSWORD=wwcm zyyc rmsp fjzx
DEFAULT_FROM_EMAIL=iMarket <adeniyiokunoye202020@gmail.com>
```

**✅ Gmail Setup Status:**
- Email: `adeniyiokunoye202020@gmail.com`
- App Password: `wwcm zyyc rmsp fjzx`
- Ready for OTP email delivery

**Gmail Setup Steps:**
1. Enable 2-Factor Authentication
2. Generate App-Specific Password
3. Use app password (not your regular Gmail password)

#### Alternative Email Providers
- **SendGrid**: `EMAIL_HOST=smtp.sendgrid.net`
- **Mailgun**: `EMAIL_HOST=smtp.mailgun.org`
- **AWS SES**: `EMAIL_HOST=email-smtp.region.amazonaws.com`

### 📱 SMS Configuration (REQUIRED for Phone OTP)

#### Twilio (Recommended)
```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

**Twilio Setup:**
1. Create account at https://twilio.com
2. Get Account SID and Auth Token from dashboard
3. Purchase a phone number for sending SMS

### 🗺️ Mapping APIs (REQUIRED for Navigation)

#### Google Maps
```bash
GOOGLE_MAPS_API_KEY=AIzaSyC40r6UnxIHqT452IytpkY92MK8aeq-108
```

**Google Maps Setup:**
1. Go to Google Cloud Console
2. Enable Maps JavaScript API, Places API, Directions API
3. Create API key and restrict it to your domain

**✅ Current API Key Status:**
- API Key: `AIzaSyC40r6UnxIHqT452IytpkY92MK8aeq-108`
- All map services enabled
- Ready for production use

#### Mapbox (Alternative)
```bash
MAPBOX_ACCESS_TOKEN=your_mapbox_access_token
```

### 🔗 WebSocket Configuration (REQUIRED for Chat)

#### Redis (Production)
```bash
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

**Redis Setup:**
1. Install Redis server
2. Configure Redis for production
3. Update `settings.py` to use Redis channel layer

### 🌐 CORS Configuration

```bash
CORS_ALLOW_ALL_ORIGINS=False
```

**Production CORS Setup:**
- Set specific allowed origins in `settings.py`
- Never use `CORS_ALLOW_ALL_ORIGINS=True` in production

## 📁 Environment File Setup

1. **Copy template**:
   ```bash
   cp .env.production.template .env
   ```

2. **Fill in values**:
   Edit `.env` with your actual credentials

3. **Secure the file**:
   ```bash
   chmod 600 .env
   ```

4. **Never commit**:
   Ensure `.env` is in `.gitignore`

## 🚀 Production Deployment Checklist

### Pre-deployment
- [ ] All environment variables set
- [ ] Database created and configured
- [ ] Email provider configured and tested
- [ ] SMS provider configured and tested
- [ ] Domain name configured
- [ ] SSL certificate obtained

### Django Setup
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` configured
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Database migrated (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)

### Security
- [ ] Strong secret key generated
- [ ] Database credentials secured
- [ ] API keys restricted to domain
- [ ] HTTPS configured
- [ ] Firewall configured

### Testing
- [ ] All API endpoints working
- [ ] Email OTP working
- [ ] SMS OTP working
- [ ] WebSocket chat working
- [ ] Navigation features working

## 🔒 Security Best Practices

1. **Environment Variables**:
   - Never hardcode credentials
   - Use different credentials for each environment
   - Rotate credentials regularly

2. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Restrict database access

3. **API Security**:
   - Rate limiting
   - API key restrictions
   - Input validation

4. **Server Security**:
   - Keep OS updated
   - Configure firewall
   - Use HTTPS only
   - Regular security audits

## 🚨 Common Issues

### Email Not Working
- Check Gmail app password (not regular password)
- Verify 2FA is enabled on Gmail
- Test with simple email first

### SMS Not Working
- Verify Twilio credentials
- Check phone number format (+country code)
- Ensure sufficient Twilio balance

### Database Connection Failed
- Check database is running
- Verify credentials
- Test connection manually

### CORS Errors
- Add frontend domain to CORS settings
- Don't use wildcard (*) in production
- Check preflight requests

## 🚀 Render.com Deployment Guide

### Step 1: Create New Web Service
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `imarket-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn iMarket.wsgi:application`
   - **Instance Type**: `Free` (or `Starter` for better performance)

### Step 2: Add Environment Variables
In your Render service dashboard, add these environment variables:

#### Required Environment Variables:
```bash
# Django Configuration
DJANGO_SECRET_KEY=your-super-secret-django-key-here-make-it-long-and-random
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=imarket.onrender.com
DATABASE_URL=postgresql://username:password@hostname:port/database_name
RENDER=1

# Google Maps API (✅ CONFIGURED)
GOOGLE_MAPS_API_KEY=AIzaSyC40r6UnxIHqT452IytpkY92MK8aeq-108

# Email Configuration (Gmail) - ✅ CONFIGURED
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=adeniyiokunoye202020@gmail.com
EMAIL_HOST_PASSWORD=wwcm zyyc rmsp fjzx
DEFAULT_FROM_EMAIL=iMarket <adeniyiokunoye202020@gmail.com>

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS=False
```

### Step 3: Add PostgreSQL Database
1. In Render Dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `imarket-database`
   - **Database**: `imarket_production`
   - **User**: `imarket_user`
   - **Region**: Same as your web service
3. Copy the **External Database URL** and add it as `DATABASE_URL` in your web service environment variables

### Step 4: Deploy
1. Push your code to GitHub (if not already done)
2. Render will automatically build and deploy
3. Check the build logs for any errors
4. Your app will be available at `https://your-app-name.onrender.com`

### Step 5: Post-Deployment Setup
After successful deployment, you need to:

1. **Create Superuser** (via Render Shell):
   ```bash
   python manage.py createsuperuser
   ```

2. **Access Admin Panel**:
   Go to `https://your-app-name.onrender.com/admin/`

### 📋 Render Deployment Checklist
- [ ] Repository connected to Render
- [ ] `requirements.txt` file present
- [ ] `build.sh` script created
- [ ] Environment variables configured
- [ ] PostgreSQL database created and connected
- [ ] Build successful
- [ ] Deployment successful
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] API endpoints working

### 🔧 Common Render Issues & Solutions

#### Build Fails
- Check `requirements.txt` for correct package versions
- Ensure `build.sh` has proper permissions
- Review build logs for specific errors

#### Database Connection Issues
- Verify `DATABASE_URL` is correctly set
- Ensure database and web service are in same region
- Check database is not sleeping (upgrade to paid plan if needed)

#### Static Files Not Loading
- Ensure `WhiteNoise` is properly configured
- Check `STATIC_ROOT` and `STATICFILES_STORAGE` settings
- Verify `collectstatic` runs during build

#### Environment Variables Not Working
- Double-check variable names (case-sensitive)
- Ensure no extra spaces in values
- Restart service after adding variables
