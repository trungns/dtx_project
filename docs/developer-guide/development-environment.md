# DTX Odoo Development Environment

## Quick Start (5 phút)

### 1. Khởi động Odoo
```bash
cd /Users/trungns/dtx_project/odoo-dev
docker-compose up -d
```

**Lần đầu tiên:** Download image ~2-3 phút (tùy tốc độ mạng)

### 2. Kiểm tra đã chạy chưa
```bash
docker-compose ps
```

Phải thấy 2 containers đang chạy:
- `dtx_postgres` (database)
- `dtx_odoo16` (odoo server)

### 3. Xem logs
```bash
# Xem logs realtime
docker-compose logs -f odoo

# Hoặc chỉ xem 50 dòng cuối
docker-compose logs --tail=50 odoo
```

Đợi đến khi thấy dòng:
```
odoo.service.server: HTTP service (werkzeug) running on 0.0.0.0:8069
```

### 4. Mở trình duyệt
```
http://localhost:8069
```

**Lần đầu tiên sẽ thấy trang tạo database:**
- Database Name: `dtx_dev`
- Email: `admin@dtx.com`
- Password: `admin`
- Language: Vietnamese / English
- Country: Vietnam
- Demo data: **KHÔNG CHỌN** (uncheck)

Click **Create Database** → Đợi 1-2 phút

---

## Quản lý Containers

### Dừng Odoo (không xóa data)
```bash
docker-compose stop
```

### Khởi động lại
```bash
docker-compose start
```

### Khởi động lại + xem logs
```bash
docker-compose restart && docker-compose logs -f odoo
```

### Tắt và xóa containers (GIỮ database)
```bash
docker-compose down
```

### Xóa HOÀN TOÀN (bao gồm database)
```bash
docker-compose down -v
```

---

## Cài đặt Module DTX

### 1. Copy module vào addons folder
```bash
cd /Users/trungns/dtx_project/odoo-dev
cp -r ../dtx_serial_ext addons/
```

### 2. Restart Odoo để nhận module
```bash
docker-compose restart odoo
```

### 3. Vào Odoo UI

1. Login: http://localhost:8069
2. Vào **Settings**
3. Click **Activate the developer mode** (góc dưới bên trái)
4. Vào **Apps** menu
5. Click nút **Update Apps List** (góc trên bên phải)
6. Bỏ filter "Apps" trong search box
7. Search "DTX Serial"
8. Click **Install**

---

## Development Workflow

### Khi sửa code Python (.py files):

**Option 1: Auto-reload (khuyến nghị)**
```bash
# Đã cấu hình `--dev=all` trong docker-compose.yml
# Chỉ cần save file → tự động reload
```

**Option 2: Manual restart**
```bash
docker-compose restart odoo
```

### Khi sửa XML views:

**Option 1: Reload từ UI**
1. Developer mode ON
2. Vào view bị thay đổi
3. Mở debug menu (bug icon)
4. Click **Edit View: FormView** (hoặc TreeView, etc.)
5. Click **Reload**

**Option 2: Upgrade module**
1. Apps menu
2. Tìm module "DTX Serial Extension"
3. Click **Upgrade**

**Option 3: Command line**
```bash
docker exec dtx_odoo16 odoo --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons -d dtx_dev -u dtx_serial_ext --stop-after-init
docker-compose restart odoo
```

### Khi thêm field mới:

1. Sửa code Python
2. **Phải upgrade module:**
```bash
# Vào Apps → tìm module → Upgrade
# HOẶC
docker exec dtx_odoo16 odoo -d dtx_dev -u dtx_serial_ext --stop-after-init
docker-compose restart odoo
```

---

## Testing

### Test cơ bản

1. **Tạo Product:**
   - Inventory → Products → Create
   - Name: Test Kiosk
   - Product Type: Storable Product
   - Tracking: By Unique Serial Number
   - Save

2. **Tạo Serial:**
   - Inventory → Products → Device Serials → Create
   - Lot/Serial Number: TEST-001
   - DTX Internal Serial: DTX-TEST-001
   - Product: Test Kiosk
   - Save

3. **Kiểm tra:**
   - Search "DTX-TEST-001" → phải tìm thấy
   - Check lifecycle state badge → màu xanh (In Stock)
   - Check vendor invoice state → màu đỏ (Missing)

### Reset database khi cần

```bash
# Xóa database cũ
docker-compose down -v

# Khởi động lại
docker-compose up -d

# Vào http://localhost:8069 tạo database mới
```

---

## Useful Commands

### Vào container Odoo (như SSH)
```bash
docker exec -it dtx_odoo16 bash
```

### Vào PostgreSQL
```bash
docker exec -it dtx_postgres psql -U odoo -d dtx_dev
```

### Xem toàn bộ databases
```bash
docker exec dtx_postgres psql -U odoo -c "\l"
```

### Backup database
```bash
docker exec dtx_postgres pg_dump -U odoo dtx_dev > backup_$(date +%Y%m%d).sql
```

### Restore database
```bash
cat backup_20250123.sql | docker exec -i dtx_postgres psql -U odoo -d dtx_dev
```

### Xem resource usage
```bash
docker stats
```

---

## Troubleshooting

### Port 8069 đã được dùng
```bash
# Tìm process đang dùng port
lsof -i :8069

# Kill process đó
kill -9 <PID>
```

### Port 5432 (PostgreSQL) đã được dùng
```bash
# Đổi port trong docker-compose.yml
ports:
  - "5433:5432"  # Dùng 5433 thay vì 5432
```

### Container không start
```bash
# Xem logs chi tiết
docker-compose logs odoo
docker-compose logs db

# Xóa và tạo lại
docker-compose down
docker-compose up -d
```

### Module không xuất hiện trong Apps
```bash
# Check file có trong container không
docker exec dtx_odoo16 ls -la /mnt/extra-addons/

# Restart Odoo
docker-compose restart odoo

# Update Apps List với developer mode ON
```

### Odoo chạy chậm
```bash
# Tăng RAM cho Docker Desktop
# Docker Desktop → Settings → Resources → Memory → 4GB+
```

---

## Project Structure

```
odoo-dev/
├── docker-compose.yml       # Container config
├── config/
│   └── odoo.conf           # Odoo settings
├── addons/                 # Your custom modules here
│   ├── dtx_serial_ext/
│   ├── dtx_vendorbill_alert/  (coming soon)
│   └── dtx_ops_project/       (coming soon)
└── data/                   # Auto-created by Docker
    ├── filestore/
    └── sessions/
```

---

## Performance Tips

### Tăng tốc development

1. **Disable auto-reload cho một số file:**
```bash
# Thêm vào odoo.conf nếu reload quá nhiều
dev_mode = qweb,xml
```

2. **Tắt log debug khi không cần:**
```bash
# Sửa trong odoo.conf
log_level = info
```

3. **Dùng SSD cho Docker volumes:**
```bash
# Docker Desktop → Settings → Resources → Advanced
# Ensure using VirtioFS
```

---

## Deploy to Production Later

Khi đã test xong trên local:

1. **Export module:**
```bash
cd /Users/trungns/dtx_project/odoo-dev/addons
tar -czf dtx_serial_ext.tar.gz dtx_serial_ext/
```

2. **Copy lên production server:**
```bash
scp dtx_serial_ext.tar.gz user@production-server:/opt/odoo/custom-addons/
```

3. **Trên production:**
```bash
cd /opt/odoo/custom-addons/
tar -xzf dtx_serial_ext.tar.gz
sudo systemctl restart odoo
# Vào Apps → Update Apps List → Install
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose stop` |
| Restart | `docker-compose restart odoo` |
| Logs | `docker-compose logs -f odoo` |
| Shell | `docker exec -it dtx_odoo16 bash` |
| Remove all | `docker-compose down -v` |

**Odoo URL:** http://localhost:8069
**Database name:** dtx_dev
**Admin password:** admin

---

Ready to code! 🚀
