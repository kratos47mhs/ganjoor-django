# Deployment Checklist for Ganjoor Django

> ✅ Use this checklist before deploying to production

## 📋 Pre-Deployment Checklist

### 1. Environment Configuration

#### Required Settings
- [ ] Created `.env` file from `.env.example`
- [ ] Generated secure `SECRET_KEY` (50+ characters)
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] Set `DEBUG=False`
- [ ] Updated `ALLOWED_HOSTS` with production domain(s)
- [ ] Set production database credentials
- [ ] Updated `DB_HOST` to production database server
- [ ] Configured `DB_PASSWORD` securely

#### Security Settings
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Set `SECURE_HSTS_SECONDS=31536000` (1 year)
- [ ] Added production domain to `CSRF_TRUSTED_ORIGINS`
- [ ] Configured `CORS_ALLOWED_ORIGINS` if needed

#### Optional Settings
- [ ] Configured Redis for caching (`REDIS_URL`)
- [ ] Set up email configuration for notifications
- [ ] Configured OpenTelemetry endpoint (`OTEL_EXPORTER_OTLP_ENDPOINT`)
- [ ] Set custom `MEDIA_ROOT` and `STATIC_ROOT` paths

---

### 2. Database

- [ ] Database server is running and accessible
- [ ] Database created with correct name
- [ ] Database user created with appropriate privileges
- [ ] Database connection tested from application server
- [ ] Applied all migrations: `python manage.py migrate`
- [ ] Database backup strategy configured
- [ ] Database has appropriate indexes (already in models)
- [ ] Connection pooling configured (already in settings)

---

### 3. Static & Media Files

- [ ] Collected static files: `python manage.py collectstatic --noinput`
- [ ] Verified `STATIC_ROOT` directory exists and is writable
- [ ] Verified `MEDIA_ROOT` directory exists and is writable
- [ ] Configured web server to serve static files
- [ ] Configured web server to serve media files
- [ ] Set appropriate file permissions (644 for files, 755 for directories)

---

### 4. Dependencies

- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] Using production-grade WSGI server (Gunicorn, uWSGI)
  ```bash
  pip install gunicorn
  ```
- [ ] Redis installed if using Redis cache
- [ ] PostgreSQL client libraries installed (`psycopg2-binary`)

---

### 5. Application Server

#### Gunicorn Configuration
- [ ] Installed Gunicorn: `pip install gunicorn`
- [ ] Configured number of workers (2-4 × CPU cores)
  ```bash
  gunicorn ganjoor.wsgi:application --bind 0.0.0.0:8000 --workers 4
  ```
- [ ] Set up process manager (systemd, supervisor)
- [ ] Configured automatic restart on failure
- [ ] Set up log rotation

#### Example systemd service (`/etc/systemd/system/ganjoor.service`)
```ini
[Unit]
Description=Ganjoor Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/ganjoor-django
Environment="PATH=/path/to/ganjoor-django/.venv/bin"
ExecStart=/path/to/ganjoor-django/.venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/ganjoor.sock \
    --timeout 120 \
    --access-logfile /var/log/ganjoor/access.log \
    --error-logfile /var/log/ganjoor/error.log \
    ganjoor.wsgi:application

[Install]
WantedBy=multi-user.target
```

---

### 6. Web Server (Nginx/Apache)

#### Nginx Configuration
- [ ] Nginx installed and running
- [ ] Created site configuration file
- [ ] Configured proxy pass to Gunicorn
- [ ] Configured static file serving
- [ ] Configured media file serving
- [ ] Enabled gzip compression
- [ ] Set client max body size for uploads
- [ ] Configured proper timeouts

#### Example Nginx config (`/etc/nginx/sites-available/ganjoor`)
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /path/to/ganjoor-django/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/ganjoor-django/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/run/ganjoor.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

- [ ] Enabled site: `ln -s /etc/nginx/sites-available/ganjoor /etc/nginx/sites-enabled/`
- [ ] Tested configuration: `nginx -t`
- [ ] Reloaded Nginx: `systemctl reload nginx`

---

### 7. SSL/TLS Certificate

- [ ] Obtained SSL certificate (Let's Encrypt recommended)
  ```bash
  sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
  ```
- [ ] Verified certificate is valid
- [ ] Configured auto-renewal
- [ ] Tested HTTPS connection
- [ ] Verified HTTP → HTTPS redirect works

---

### 8. Security Hardening

#### Firewall
- [ ] UFW/iptables configured
- [ ] Only necessary ports open (80, 443, 22)
- [ ] SSH port changed (optional but recommended)
- [ ] Fail2ban installed and configured

#### Application Security
- [ ] All sensitive data in environment variables
- [ ] `.env` file has restricted permissions (600)
- [ ] No `.env` in version control
- [ ] Database password is strong (16+ characters)
- [ ] Admin user password is strong
- [ ] Rate limiting configured (already in settings)
- [ ] CORS properly configured if using separate frontend

#### Server Security
- [ ] Server OS updated: `apt update && apt upgrade`
- [ ] Automatic security updates enabled
- [ ] SSH key-based authentication enabled
- [ ] Password authentication disabled for SSH
- [ ] Root login disabled
- [ ] Non-root user created for deployment

---

### 9. Monitoring & Logging

#### Application Logs
- [ ] Logs directory exists: `/var/log/ganjoor/` or `logs/`
- [ ] Log rotation configured
- [ ] Proper log levels set (INFO for production)
- [ ] Error notifications configured

#### System Monitoring
- [ ] CPU monitoring configured
- [ ] Memory monitoring configured
- [ ] Disk space monitoring configured
- [ ] Database connection monitoring
- [ ] Application health check endpoint (recommended)

#### Optional: OpenTelemetry/SigNoz
- [ ] SigNoz server running
- [ ] OTLP endpoint configured in `.env`
- [ ] Application sending traces
- [ ] Dashboards configured

---

### 10. Backup Strategy

- [ ] Database backup script created
  ```bash
  pg_dump ganjoor > /backups/ganjoor_$(date +%Y%m%d_%H%M%S).sql
  ```
- [ ] Daily automated backups scheduled (cron)
- [ ] Backups stored offsite/cloud
- [ ] Backup restoration tested
- [ ] Media files backup configured
- [ ] Retention policy defined (e.g., keep 30 days)

#### Example backup cron job
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup-script.sh >> /var/log/backup.log 2>&1
```

---

### 11. Performance Optimization

- [ ] Database queries optimized (already done)
- [ ] Redis cache configured and working
- [ ] Static files compressed (gzip)
- [ ] CDN configured for static files (optional)
- [ ] Database indexes verified
- [ ] Connection pooling enabled (already done)
- [ ] Proper number of Gunicorn workers

---

### 12. Testing

#### Pre-Deployment Testing
- [ ] Ran `python manage.py check --deploy`
- [ ] All tests passing (if tests exist)
- [ ] Manual testing of critical paths:
  - [ ] User registration/login
  - [ ] Browsing poets
  - [ ] Viewing poems
  - [ ] Search functionality
  - [ ] Adding favorites (authenticated users)
  - [ ] Admin panel access
  - [ ] API endpoints working
  - [ ] Swagger UI accessible

#### Post-Deployment Testing
- [ ] Homepage loads correctly
- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] Static files loading
- [ ] Admin panel accessible
- [ ] API endpoints responding
- [ ] Database connections working
- [ ] Logs being written correctly
- [ ] Error pages displaying correctly (404, 500)

---

### 13. Documentation

- [ ] Updated README.md with production info
- [ ] Deployment procedures documented
- [ ] Environment variables documented
- [ ] Backup/restore procedures documented
- [ ] Emergency contacts listed
- [ ] Runbook created for common issues

---

### 14. DNS & Domain

- [ ] Domain pointed to server IP
- [ ] DNS records configured (A, AAAA, CNAME)
- [ ] DNS propagation verified
- [ ] WWW subdomain configured
- [ ] TTL values appropriate

---

### 15. Final Checks

- [ ] All services started and enabled
  ```bash
  systemctl enable ganjoor
  systemctl start ganjoor
  systemctl enable nginx
  systemctl start nginx
  systemctl enable redis  # if using Redis
  systemctl start redis
  ```
- [ ] Services restart on reboot
- [ ] Application accessible from internet
- [ ] No debug information exposed
- [ ] No stack traces visible to users
- [ ] Proper error pages showing
- [ ] Performance acceptable under load
- [ ] Monitoring alerts working
- [ ] Team notified of deployment

---

## 🚀 Deployment Commands Quick Reference

```bash
# 1. Update code
git pull origin main

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install/update dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart application
sudo systemctl restart ganjoor

# 7. Restart web server
sudo systemctl reload nginx

# 8. Check logs
tail -f /var/log/ganjoor/error.log
tail -f logs/error.log

# 9. Check application status
sudo systemctl status ganjoor
curl https://yourdomain.com/
```

---

## 🆘 Rollback Plan

If deployment fails:

```bash
# 1. Revert code
git reset --hard previous_commit_hash

# 2. Restore database (if needed)
psql ganjoor < /backups/latest_backup.sql

# 3. Restart services
sudo systemctl restart ganjoor
sudo systemctl reload nginx

# 4. Verify rollback
curl https://yourdomain.com/
```

---

## 📞 Post-Deployment Support

### Monitoring First 24 Hours
- [ ] Check error logs hourly
- [ ] Monitor CPU/memory usage
- [ ] Monitor database connections
- [ ] Check response times
- [ ] Verify no 500 errors
- [ ] Check user feedback

### Week 1 Monitoring
- [ ] Review error logs daily
- [ ] Monitor disk space
- [ ] Check backup success
- [ ] Review performance metrics
- [ ] User feedback review

---

## ⚠️ Common Issues & Solutions

### Issue: 502 Bad Gateway
- Check if Gunicorn is running: `systemctl status ganjoor`
- Check Gunicorn logs: `journalctl -u ganjoor -f`
- Verify socket file exists: `ls -l /run/ganjoor.sock`

### Issue: Static files not loading
- Run: `python manage.py collectstatic --noinput`
- Check Nginx configuration
- Verify file permissions

### Issue: Database connection errors
- Check database is running
- Verify credentials in `.env`
- Check firewall rules
- Test connection: `psql -h DB_HOST -U DB_USER -d DB_NAME`

### Issue: High memory usage
- Reduce number of Gunicorn workers
- Enable Redis caching
- Optimize database queries

---

## 📊 Performance Benchmarks (Target)

- [ ] Homepage loads in < 2 seconds
- [ ] API responses < 500ms
- [ ] Search results < 1 second
- [ ] Database queries < 100ms average
- [ ] CPU usage < 70% under normal load
- [ ] Memory usage < 80%

---

## ✅ Sign-Off

Deployment completed by: ________________  
Date: ________________  
Time: ________________  
Version deployed: ________________  

All checklist items verified: ☐ Yes ☐ No  
Post-deployment tests passed: ☐ Yes ☐ No  
Monitoring configured: ☐ Yes ☐ No  
Team notified: ☐ Yes ☐ No  

---

**🎉 Congratulations! Your Ganjoor Django application is now live!**

Remember to:
- Monitor logs regularly
- Keep system updated
- Test backups monthly
- Review security quarterly
- Update documentation as needed