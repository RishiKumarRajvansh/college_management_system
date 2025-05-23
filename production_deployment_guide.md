# College Management System - Production Deployment Guide

This guide provides comprehensive instructions for deploying the College Management System to a production environment. Follow these steps to ensure a secure, performant, and maintainable deployment.

## Prerequisites

Before proceeding with the deployment, ensure you have the following:

- Python 3.8+ installed on the server
- PostgreSQL 12+ or MySQL 8+ database server
- Nginx or Apache web server
- A domain name (recommended)
- SSL certificate (recommended for security)

## Step 1: Prepare the Environment

1. Create a dedicated user for the application:
   ```bash
   sudo useradd -m -s /bin/bash collegeapp
   sudo passwd collegeapp
   ```

2. Install required system packages:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx supervisor
   ```

3. Configure the virtual environment:
   ```bash
   sudo -u collegeapp bash
   cd /home/collegeapp
   python3 -m venv venv
   source venv/bin/activate
   ```

## Step 2: Set Up the Application

1. Clone the repository:
   ```bash
   git clone https://your-repository-url.git college_management
   cd college_management
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install gunicorn psycopg2-binary
   ```

3. Create a production settings file (`production_settings.py`):
   ```python
   from .settings import *
   
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   
   # Configure security settings
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_SSL_REDIRECT = True
   SECURE_HSTS_SECONDS = 31536000  # 1 year
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True
   SECURE_BROWSER_XSS_FILTER = True
   
   # Configure database
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'college_management_db',
           'USER': 'your_db_user',
           'PASSWORD': 'your_secure_password',
           'HOST': 'localhost',
           'PORT': '',
       }
   }
   
   # Configure static files
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   
   # Configure logging
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {message}',
               'style': '{',
           },
       },
       'handlers': {
           'file': {
               'level': 'WARNING',
               'class': 'logging.FileHandler',
               'filename': '/var/log/college_management/app.log',
               'formatter': 'verbose',
           },
       },
       'loggers': {
           'django': {
               'handlers': ['file'],
               'level': 'WARNING',
               'propagate': True,
           },
       },
   }
   ```

4. Create database:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE college_management_db;
   CREATE USER your_db_user WITH PASSWORD 'your_secure_password';
   ALTER ROLE your_db_user SET client_encoding TO 'utf8';
   ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE your_db_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE college_management_db TO your_db_user;
   \q
   ```

5. Apply migrations and collect static files:
   ```bash
   python manage.py migrate --settings=college_management.production_settings
   python manage.py collectstatic --settings=college_management.production_settings
   python manage.py createsuperuser --settings=college_management.production_settings
   ```

## Step 3: Configure Gunicorn

1. Create a Gunicorn configuration file (`gunicorn_config.py`):
   ```python
   import multiprocessing
   
   bind = "127.0.0.1:8000"
   workers = multiprocessing.cpu_count() * 2 + 1
   max_requests = 1000
   timeout = 30
   keepalive = 2
   ```

2. Create a Supervisor configuration file:
   ```bash
   sudo nano /etc/supervisor/conf.d/college_management.conf
   ```

3. Add the following configuration:
   ```ini
   [program:college_management]
   command=/home/collegeapp/venv/bin/gunicorn college_management.wsgi:application --config /home/collegeapp/college_management/gunicorn_config.py
   directory=/home/collegeapp/college_management
   user=collegeapp
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/college_management/gunicorn.log
   environment=DJANGO_SETTINGS_MODULE="college_management.production_settings"
   ```

4. Create log directory and files:
   ```bash
   sudo mkdir -p /var/log/college_management
   sudo touch /var/log/college_management/gunicorn.log /var/log/college_management/app.log
   sudo chown -R collegeapp:collegeapp /var/log/college_management
   ```

5. Enable and start Supervisor:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start college_management
   ```

## Step 4: Configure Nginx

1. Create an Nginx configuration file:
   ```bash
   sudo nano /etc/nginx/sites-available/college_management
   ```

2. Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
       return 301 https://$host$request_uri;
   }
   
   server {
       listen 443 ssl;
       server_name your-domain.com www.your-domain.com;
   
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_prefer_server_ciphers on;
       ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
       ssl_session_timeout 1d;
       ssl_session_cache shared:SSL:50m;
       ssl_stapling on;
       ssl_stapling_verify on;
       
       location /static/ {
           alias /home/collegeapp/college_management/staticfiles/;
           expires 30d;
           add_header Cache-Control "public, max-age=2592000";
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/college_management /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Step 5: SSL Certificate with Let's Encrypt

1. Install Certbot:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. Obtain SSL certificate:
   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

3. Set up automatic renewal:
   ```bash
   sudo systemctl status certbot.timer
   ```

## Step 6: Configure Backup Strategy

1. Create a backup script (`/home/collegeapp/backup.sh`):
   ```bash
   #!/bin/bash
   
   # Database backup
   TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
   BACKUP_DIR="/home/collegeapp/backups"
   DB_BACKUP="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"
   
   # Ensure backup directory exists
   mkdir -p $BACKUP_DIR
   
   # Create database backup
   PGPASSWORD=your_secure_password pg_dump -U your_db_user -h localhost college_management_db > $DB_BACKUP
   
   # Compress backup
   gzip $DB_BACKUP
   
   # Remove backups older than 7 days
   find $BACKUP_DIR -name "db_backup_*.sql.gz" -type f -mtime +7 -delete
   
   # Media files backup (if applicable)
   tar -czf ${BACKUP_DIR}/media_backup_${TIMESTAMP}.tar.gz /home/collegeapp/college_management/media
   
   # Remove media backups older than 7 days
   find $BACKUP_DIR -name "media_backup_*.tar.gz" -type f -mtime +7 -delete
   ```

2. Make the script executable:
   ```bash
   chmod +x /home/collegeapp/backup.sh
   ```

3. Schedule the backup with cron:
   ```bash
   sudo -u collegeapp crontab -e
   ```

4. Add the following line to run the backup daily at 2 AM:
   ```
   0 2 * * * /home/collegeapp/backup.sh
   ```

## Step 7: Performance Monitoring and Optimization

1. Install and configure Prometheus for monitoring:
   ```bash
   sudo apt install prometheus prometheus-node-exporter
   ```

2. Install and configure Grafana for visualization:
   ```bash
   sudo apt install -y software-properties-common
   sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
   curl https://packages.grafana.com/gpg.key | sudo apt-key add -
   sudo apt update
   sudo apt install grafana
   ```

3. Configure database connection pooling:
   ```bash
   pip install django-db-connection-pool
   ```

4. Update production settings:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'dj_db_conn_pool.backends.postgresql',
           'NAME': 'college_management_db',
           'USER': 'your_db_user',
           'PASSWORD': 'your_secure_password',
           'HOST': 'localhost',
           'PORT': '',
           'POOL_OPTIONS': {
               'POOL_SIZE': 10,
               'MAX_OVERFLOW': 10,
               'RECYCLE': 300,  # 5 minutes
           }
       }
   }
   ```

## Step 8: Setup Regular Maintenance Tasks

1. Create a maintenance script (`/home/collegeapp/maintenance.sh`):
   ```bash
   #!/bin/bash
   
   # Activate virtual environment
   source /home/collegeapp/venv/bin/activate
   cd /home/collegeapp/college_management
   
   # Clear expired sessions
   python manage.py clearsessions --settings=college_management.production_settings
   
   # Vacuum analyze database (if PostgreSQL)
   PGPASSWORD=your_secure_password psql -U your_db_user -d college_management_db -c "VACUUM ANALYZE;"
   
   # Check for Django security updates
   pip list --outdated | grep -E 'django|pillow|requests'
   ```

2. Make the script executable and schedule it:
   ```bash
   chmod +x /home/collegeapp/maintenance.sh
   sudo -u collegeapp crontab -e
   ```

3. Add to crontab:
   ```
   0 1 * * 0 /home/collegeapp/maintenance.sh > /home/collegeapp/maintenance_log.txt 2>&1
   ```

## Post-Deployment Verification

After completing the deployment, perform these checks:

1. Visit the website and try to log in as an admin
2. Check that the dashboard loads correctly with all charts
3. Test the notification system functionality
4. Verify that report exports work in different formats
5. Validate that mobile responsiveness is working
6. Check server logs for any errors or warnings

## Additional Recommendations

1. **Content Delivery Network (CDN)**: Consider using a CDN for static assets to improve load times
2. **Rate Limiting**: Implement rate limiting to protect against brute force attacks
3. **Web Application Firewall**: Consider implementing a WAF like ModSecurity
4. **Automated Testing**: Set up CI/CD pipeline for automated testing before deployment
5. **Load Testing**: Conduct load testing using tools like Apache JMeter
6. **Disaster Recovery Plan**: Document a step-by-step disaster recovery procedure

## Troubleshooting

### Common Issues and Solutions:

1. **502 Bad Gateway**:
   - Check if Gunicorn is running: `sudo supervisorctl status college_management`
   - Check Gunicorn logs: `cat /var/log/college_management/gunicorn.log`

2. **Static Files Not Loading**:
   - Verify STATIC_ROOT is set correctly
   - Check if collectstatic was run: `python manage.py collectstatic --settings=college_management.production_settings`
   - Check Nginx configuration for static files path

3. **Database Connection Issues**:
   - Check database credentials in settings
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database connection: `psql -U your_db_user -h localhost -d college_management_db`

4. **Permission Denied Errors**:
   - Check file permissions: `ls -la /var/log/college_management/`
   - Ensure correct user ownership: `sudo chown -R collegeapp:collegeapp /home/collegeapp/`

## Maintenance Contact

For any technical issues or maintenance requests, contact:

- System Administrator: admin@example.com
- Technical Support: support@example.com
