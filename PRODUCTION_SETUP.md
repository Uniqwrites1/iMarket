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

#### Gmail SMTP
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

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
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

**Google Maps Setup:**
1. Go to Google Cloud Console
2. Enable Maps JavaScript API, Places API, Directions API
3. Create API key and restrict it to your domain

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

## 📞 Support

For deployment issues:
1. Check Django logs
2. Verify environment variables
3. Test individual services
4. Check firewall and network settings
