# HƯỚNG DẪN CÀI ĐẶT ODOO 16 - DTX PRODUCTION

**Phiên bản**: 2.0.0
**Cập nhật**: 2026-01-09

---

## TÀI LIỆU THAM KHẢO

Chi tiết cài đặt development xem:
- **[/MACBOOK_SETUP.md](/MACBOOK_SETUP.md)** - macOS setup
- **[/WINDOWS_SETUP.md](/WINDOWS_SETUP.md)** - Windows setup
- **[/QUICK_START.md](/QUICK_START.md)** - Quick start guide

---

## PRODUCTION DEPLOYMENT

### Option 1: Docker Deployment (Khuyến nghị)

**Prerequisites**:
- Ubuntu 22.04 LTS
- Docker 24.x+
- Docker Compose v2.x+
- 16GB RAM, 4 CPU cores, 100GB SSD

**Steps**:

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. Clone repository
git clone https://github.com/trungns/dtx_project.git
cd dtx_project/odoo-dev

# 3. Production docker-compose
cp docker-compose.yml docker-compose.prod.yml

# Edit docker-compose.prod.yml:
# - Set strong passwords
# - Enable backups
# - Configure volumes for persistence

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Check logs
docker-compose -f docker-compose.prod.yml logs -f odoo
```

**Access**:
- URL: `http://your-server-ip:8069`
- Database: `dtx_production`
- Admin: Tạo trong setup wizard

---

### Option 2: Native Installation

**Prerequisites**:
- Ubuntu 22.04 LTS
- Python 3.10
- PostgreSQL 15
- Nginx (reverse proxy)

**Steps**:

```bash
# 1. Install PostgreSQL
sudo apt update
sudo apt install postgresql-15

# 2. Install Python dependencies
sudo apt install python3-pip python3-dev libxml2-dev libxslt1-dev \
                 libldap2-dev libsasl2-dev libjpeg-dev zlib1g-dev

# 3. Install wkhtmltopdf (for PDF reports)
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6-1.focal_amd64.deb

# 4. Install Odoo 16
wget https://nightly.odoo.com/16.0/nightly/deb/odoo_16.0.latest_all.deb
sudo dpkg -i odoo_16.0.latest_all.deb
sudo apt-get install -f

# 5. Create Odoo user
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# 6. Copy custom addons
sudo cp -r dtx_project/odoo-dev/addons/* /opt/odoo/custom-addons/

# 7. Configure Odoo
sudo nano /etc/odoo/odoo.conf
```

**Odoo Config** (`/etc/odoo/odoo.conf`):
```ini
[options]
admin_passwd = STRONG_PASSWORD_HERE
db_host = localhost
db_port = 5432
db_user = odoo
db_password = DB_PASSWORD_HERE
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons
xmlrpc_port = 8069
logfile = /var/log/odoo/odoo.log
limit_time_cpu = 600
limit_time_real = 1200
workers = 4
max_cron_threads = 2
```

**Start Odoo**:
```bash
sudo systemctl start odoo
sudo systemctl enable odoo
sudo systemctl status odoo
```

---

### Option 3: Khôi phục từ Backup

Nếu đã có database backup từ môi trường dev:

```bash
# 1. Copy backup file
scp dtx_dev_backup_*.zip production-server:/tmp/

# 2. Restore
cd /tmp
unzip dtx_dev_backup_*.zip

# 3. Create database
sudo -u postgres psql
CREATE DATABASE dtx_production;
\q

# 4. Restore data
sudo -u postgres pg_restore -d dtx_production dtx_dev_backup.sql

# 5. Update admin password (if needed)
sudo -u postgres psql -d dtx_production -c "UPDATE res_users SET password='NEW_PASSWORD' WHERE id=2;"
```

Chi tiết: [05_MAINTENANCE/01_BACKUP_RESTORE.md](../05_MAINTENANCE/01_BACKUP_RESTORE.md)

---

## POST-INSTALLATION CHECKLIST

### 1. Bảo mật

- [ ] Đổi admin password mạnh
- [ ] Tắt debug mode
- [ ] Enable HTTPS (SSL certificate)
- [ ] Configure firewall (chỉ mở port 80, 443)
- [ ] Disable database manager (`list_db = False`)

### 2. Performance

- [ ] Configure PostgreSQL tuning
- [ ] Enable Nginx caching
- [ ] Setup CDN cho static files (optional)
- [ ] Configure workers (4-8 workers khuyến nghị)

### 3. Backup

- [ ] Configure automated daily backup
- [ ] Test restore procedure
- [ ] Setup offsite backup storage

### 4. Monitoring

- [ ] Setup log rotation
- [ ] Configure email notifications
- [ ] Monitor disk space
- [ ] Monitor database size

---

## NGINX REVERSE PROXY (Khuyến nghị)

**Install Nginx**:
```bash
sudo apt install nginx
```

**Config** (`/etc/nginx/sites-available/odoo`):
```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL config
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Headers
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Locations
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    location /longpolling {
        proxy_pass http://odoochat;
    }

    # Static files caching
    location ~* /web/static/ {
        proxy_cache_valid 200 60m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    # Fileupload size
    client_max_body_size 50M;
}
```

**Enable & Start**:
```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## SSL CERTIFICATE (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl status certbot.timer
```

---

## TROUBLESHOOTING

### Odoo không start

```bash
# Check logs
sudo journalctl -u odoo -f

# Common issues:
# 1. PostgreSQL not running
sudo systemctl status postgresql

# 2. Port already in use
sudo lsof -i :8069

# 3. Permission errors
sudo chown -R odoo:odoo /opt/odoo
```

### Database connection error

```bash
# Test PostgreSQL connection
sudo -u postgres psql

# Check pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## NEXT STEPS

1. **Cài đặt modules**: [02_MODULE_INSTALLATION.md](02_MODULE_INSTALLATION.md)
2. **Cấu hình ban đầu**: [../02_CONFIGURATION/](../02_CONFIGURATION/)
3. **Đào tạo users**: [../03_USER_GUIDES/](../03_USER_GUIDES/)

---

**DTX Odoo 16 - Production Installation Guide**
