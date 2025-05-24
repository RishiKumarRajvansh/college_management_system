# College Management System

A comprehensive Django-based system for managing all aspects of a college or educational institution, including student management, faculty management, course management, attendance tracking, examination management, library management, hostel management, fee collection, and reporting.

## 📋 Features

### Core Features
- **User Authentication System** with role-based access control (Admin, Faculty, Student)
- **Student Management** - Registration, profiles, academic records, documents
- **Faculty Management** - Staff records, profiles, teaching assignments
- **Course Management** - Course catalog, curriculum planning, syllabus
- **Attendance Management** - Track daily attendance, reports, statistics
- **Examination System** - Exam scheduling, results management, grade reports
- **Fee Management** - Fee structure, payments tracking, receipts, due alerts
- **Library Management** - Book catalog, issuance, returns, fines
- **Hostel Management** - Room allocation, student tracking, complaints
- **Reporting Module** - Comprehensive reports with export options (PDF, Excel, CSV)

### Advanced Features
- **Dynamic Dashboards** with real-time data visualization using Chart.js
- **Notification System** for alerts, reminders, and announcements
- **Report Export Functionality** in multiple formats (PDF, Excel, CSV)
- **Responsive Design** for desktop and mobile accessibility
- **Rich UI/UX** with Bootstrap 5 and custom styling
- **Role-based Access Control** for security

## 🚀 Implementation Details

The College Management System is fully functional with:

- **Dynamic Data Visualization**: Four different chart types implemented:
  - Attendance distribution (doughnut chart)
  - Exam performance by course (bar chart)
  - Enrollment trends (line chart)
  - Fee collection analytics (bar chart)
- **Real-time Data**: All charts fetch data via AJAX from dedicated API endpoints
- **Responsive Design**: Charts resize based on viewport size
- **Performance Optimization**: Client-side caching to reduce server load
- **Auto-refresh**: Charts auto-refresh every 5 minutes

### Notification System
- Implemented `Notification` model for system messages
- Real-time notification counter in the navbar
- Mark-as-read functionality
- Categorized notifications (info, warning, success, danger)
- Admin capability to send notifications to users or groups

### Report Export Functionality
- Export any data table to PDF, Excel, or CSV formats
- Custom PDF template with college branding
- Excel exports with proper formatting and headers
- Bulk export capability for admin users

### UI/UX Improvements
- Responsive sidebar navigation
- Custom card designs for dashboard modules
- Consistent design language across all modules
- Loading animations and state indicators
- Form validation and error handling
- Mobile-friendly controls and layouts

## 📝 Requirements

- Python 3.8+
- Django 3.2+
- PostgreSQL/MySQL (production) or SQLite (development)
- Additional requirements listed in requirements.txt

## ⚙️ Installation for Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/college-management-system.git
cd college-management-system
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

6. Run the development server
```bash
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/

## 🌐 Production Deployment Guide

This section provides comprehensive instructions for deploying the College Management System to a production environment.

### Production Requirements

- Python 3.8+
- PostgreSQL 12+ (recommended) or MySQL 8.0+
- Nginx or Apache web server
- Domain name (optional but recommended)
- SSL certificate (strongly recommended)
- Linux server (Ubuntu 20.04+ recommended)
- At least 2GB RAM and 2 CPU cores
- 20GB+ disk space

### 1. Server Preparation

#### Update the system
```bash
sudo apt update
sudo apt upgrade -y
```

#### Install dependencies
```bash
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl build-essential libssl-dev
```

#### Create a Python virtual environment
```bash
sudo apt install -y python3-venv
mkdir -p /var/www/college_management_system
cd /var/www/college_management_system
python3 -m venv env
source env/bin/activate
```

### 2. Database Setup

#### PostgreSQL setup
```bash
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE college_management_system;
CREATE USER cms_user WITH PASSWORD 'secure_password';
ALTER ROLE cms_user SET client_encoding TO 'utf8';
ALTER ROLE cms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cms_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE college_management_system TO cms_user;
\q
```

### 3. Application Setup

#### Clone the repository and install requirements
```bash
git clone https://github.com/yourusername/college_management_system.git src
cd src
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### Create .env file for environment variables
```bash
cd college_management_system  # Directory with settings.py
cat > .env << EOF
DEBUG=False
SECRET_KEY=your_secure_secret_key_here
ALLOWED_HOSTS=your.domain.com,www.your.domain.com,your-server-ip
DB_NAME=college_management_system
DB_USER=cms_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EOF
```

#### Modify settings.py
```python
# Import environment variables
from decouple import config
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

#### Apply migrations and collect static files
```bash
cd /var/www/college_management_system/src
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py createsuperuser
```

### 4. Web Server Configuration

#### Create Gunicorn service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add the following content:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/college_management_system/src
ExecStart=/var/www/college_management_system/env/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/college_management_system/college_management_system.sock \
          college_management_system.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Start Gunicorn
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

#### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/college_management_system
```

Add the following content:
```nginx
server {
    listen 80;
    server_name your.domain.com www.your.domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/college_management_system/src;
    }

    location /media/ {
        root /var/www/college_management_system/src;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/college_management_system/college_management_system.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/college_management_system /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Configuration

#### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### Obtain SSL certificate
```bash
sudo certbot --nginx -d your.domain.com -d www.your.domain.com
```

### 6. Security Measures

#### Set up firewall
```bash
sudo apt install -y ufw
sudo ufw allow 'Nginx Full'
sudo ufw allow 'OpenSSH'
sudo ufw enable
```

#### Configure automatic security updates
```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 7. Backup Strategy

#### Setup daily database backups
```bash
sudo apt install -y postgresql-client

# Create backup script
sudo nano /usr/local/bin/backup_database.sh
```

Add the following content:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="college_management_system"
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"

mkdir -p $BACKUP_DIR

# Backup the database
PGPASSWORD="secure_password" pg_dump -U cms_user -h localhost -F p $DB_NAME > $BACKUP_FILE

# Compress the backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -type f -name "${DB_NAME}_*.sql.gz" -mtime +30 -delete
```

Make the script executable and configure cron job:
```bash
sudo chmod +x /usr/local/bin/backup_database.sh
sudo crontab -e
```

Add the following line to run daily at 2 AM:
```
0 2 * * * /usr/local/bin/backup_database.sh
```

### 8. Performance Optimization

#### Configure caching
```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
pip install django-redis
```

Add to settings.py:
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

#### Media file optimization
Install Pillow optimizers:
```bash
sudo apt install -y jpegoptim optipng
```

### 9. Monitoring

#### Setup basic monitoring with Monit
```bash
sudo apt install -y monit
```

Configure Monit for Gunicorn and Nginx:
```bash
sudo nano /etc/monit/conf.d/gunicorn
```

Add:
```
check process gunicorn with pidfile /var/run/gunicorn.pid
    start program = "/bin/systemctl start gunicorn"
    stop program = "/bin/systemctl stop gunicorn"
    if failed unixsocket /var/www/college_management_system/college_management_system.sock then restart
    if 5 restarts within 5 cycles then timeout
```

```bash
sudo nano /etc/monit/conf.d/nginx
```

Add:
```
check process nginx with pidfile /var/run/nginx.pid
    start program = "/bin/systemctl start nginx"
    stop program = "/bin/systemctl stop nginx"
    if failed port 80 protocol http request "/" then restart
    if 5 restarts within 5 cycles then timeout
```

Restart Monit:
```bash
sudo systemctl restart monit
```

### 10. Maintenance

#### Create maintenance mode script
```bash
sudo nano /usr/local/bin/maintenance_mode.sh
```

Add:
```bash
#!/bin/bash
NGINX_CONF="/etc/nginx/sites-available/college_management_system"
MAINTENANCE_CONF="/etc/nginx/sites-available/maintenance"

if [ "$1" == "on" ]; then
    # Create maintenance page
    mkdir -p /var/www/html/maintenance
    cat > /var/www/html/maintenance/index.html << EOF
    <!DOCTYPE html>
    <html>
    <head>
        <title>Maintenance Mode</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding-top: 100px; }
            h1 { color: #333; }
            p { color: #666; }
        </style>
    </head>
    <body>
        <h1>We'll be back soon!</h1>
        <p>The College Management System is currently undergoing scheduled maintenance.</p>
        <p>Please check back in a few minutes.</p>
    </body>
    </html>
EOF

    # Create maintenance Nginx config
    cat > "$MAINTENANCE_CONF" << EOF
    server {
        listen 80 default_server;
        server_name _;
        root /var/www/html/maintenance;
        index index.html;
        location / {
            try_files \$uri \$uri/ =404;
        }
    }
EOF
    sudo ln -sf "$MAINTENANCE_CONF" /etc/nginx/sites-enabled/default
    sudo systemctl reload nginx
    echo "Maintenance mode activated."
elif [ "$1" == "off" ]; then
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo systemctl reload nginx
    echo "Maintenance mode deactivated."
else
    echo "Usage: $0 [on|off]"
    exit 1
fi
```

Make the script executable:
```bash
sudo chmod +x /usr/local/bin/maintenance_mode.sh
```

## 📊 Database Schema

The system uses a relational database with the following key models:

1. **User & Profile** - Authentication and user information
2. **Student** - Student details, academic records, etc.
3. **Faculty** - Faculty details, subjects, etc.
4. **Course** - Course information, curriculum, etc.
5. **Attendance** - Daily attendance records
6. **Examination & Result** - Exam schedules and student results
7. **FeeStructure & Payment** - Fee details and payment records
8. **Book & BookIssue** - Library book catalog and lending records
9. **Hostel & Room** - Hostel and room management
10. **Report & Notification** - Reporting and notification system

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

* [Django](https://www.djangoproject.com/) - The web framework used
* [Bootstrap 5](https://getbootstrap.com/) - Frontend framework
* [Chart.js](https://www.chartjs.org/) - JavaScript charting library
* [DataTables](https://datatables.net/) - Table plugin for jQuery
* [Font Awesome](https://fontawesome.com/) - Icon toolkit
