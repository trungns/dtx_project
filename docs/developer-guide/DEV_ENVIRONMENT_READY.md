# ✅ MÔI TRƯỜNG PHÁT TRIỂN ĐÃ SẴN SÀNG!

## 📦 Đã Setup Xong

Tôi đã tạo cho bạn môi trường dev Odoo 16 hoàn chỉnh với Docker trên MacBook M1.

---

## 🚀 BẮT ĐẦU NGAY (3 BƯỚC - 5 PHÚT)

### Bước 1: Đảm bảo Docker đang chạy

```bash
# Kiểm tra Docker
docker --version
```

- ✅ Nếu thấy version → OK, next bước 2
- ❌ Nếu lỗi → Cài Docker Desktop: https://www.docker.com/products/docker-desktop/
  - Chọn: "Mac with Apple chip" (M1)
  - Cài và mở Docker Desktop

### Bước 2: Khởi động Odoo

```bash
cd /Users/trungns/dtx_project/odoo-dev
./start.sh
```

**Lần đầu tiên:**
- Sẽ tải Odoo image (~2-3 phút)
- Khởi động PostgreSQL và Odoo
- Đợi thấy: "🌐 Open Odoo at: http://localhost:8069"

### Bước 3: Mở trình duyệt

Vào: **http://localhost:8069**

**Tạo database:**
- Database Name: `dtx_dev`
- Email: `admin@dtx.com`
- Password: `admin`
- Language: English / Tiếng Việt
- Demo data: ❌ UNCHECK
- Click **Create Database**

---

## 📚 HƯỚNG DẪN CHI TIẾT

### Đọc file này để bắt đầu:
```bash
# Hướng dẫn nhanh (đọc trước)
open /Users/trungns/dtx_project/odoo-dev/QUICKSTART.md

# Hoặc xem trong terminal
cat /Users/trungns/dtx_project/odoo-dev/QUICKSTART.md
```

### Hoặc đọc README đầy đủ:
```bash
open /Users/trungns/dtx_project/odoo-dev/README.md
```

---

## 📂 CẤU TRÚC PROJECT

```
dtx_project/
├── dtx_serial_ext/           ← Module gốc (backup)
│   ├── models/
│   ├── views/
│   └── ...
│
└── odoo-dev/                 ← Môi trường development
    ├── QUICKSTART.md         ← ĐỌC FILE NÀY TRƯỚC!
    ├── README.md             ← Hướng dẫn đầy đủ
    │
    ├── start.sh              ← Khởi động Odoo
    ├── logs.sh               ← Xem logs
    ├── upgrade-module.sh     ← Upgrade module khi sửa code
    ├── reset.sh              ← Reset database
    │
    ├── docker-compose.yml    ← Config Docker
    ├── config/
    │   └── odoo.conf         ← Config Odoo
    │
    └── addons/               ← Folder chứa modules
        └── dtx_serial_ext/   ← Module đã được copy sẵn
```

---

## ⚡ COMMANDS THƯỜNG DÙNG

```bash
cd /Users/trungns/dtx_project/odoo-dev

# Khởi động Odoo
./start.sh

# Xem logs (realtime)
./logs.sh

# Upgrade module sau khi sửa code
./upgrade-module.sh dtx_serial_ext

# Restart Odoo
docker-compose restart odoo

# Dừng Odoo (giữ data)
docker-compose stop

# Reset toàn bộ (XÓA data)
./reset.sh
```

---

## 🔧 WORKFLOW PHÁT TRIỂN

### 1. Khi sửa code Python (.py):
```bash
# 1. Sửa file trong:
#    /Users/trungns/dtx_project/odoo-dev/addons/dtx_serial_ext/

# 2. Upgrade module
./upgrade-module.sh

# 3. Refresh browser
```

### 2. Khi sửa XML views (.xml):
```bash
# 1. Sửa file .xml

# 2. Upgrade module
./upgrade-module.sh

# 3. Refresh browser
```

### 3. Khi thêm field mới vào model:
```bash
# 1. Sửa file Python thêm field

# 2. BẮT BUỘC upgrade module
./upgrade-module.sh

# 3. Refresh browser
```

---

## 🧪 TEST MODULE DTX SERIAL EXTENSION

### Quick Test (5 phút):

1. **Cài Inventory module:**
   - Apps → Search "Inventory" → Install

2. **Update Apps List:**
   - Apps → ⋮ (3 chấm) → Update Apps List

3. **Cài DTX Serial Extension:**
   - Apps → Search "DTX Serial" → Install

4. **Tạo Product:**
   - Inventory → Products → Create
   - Name: Test Kiosk
   - Type: Storable Product
   - Tracking: By Unique Serial Number
   - Save

5. **Tạo Serial:**
   - Inventory → Products → Device Serials → Create
   - Lot/Serial: KIOSK-001
   - DTX Serial: DTX-001
   - Product: Test Kiosk
   - Save

6. **Check Features:**
   - ✅ Lifecycle State: màu xanh "In Stock"
   - ✅ Vendor Invoice State: màu đỏ "Invoice Missing"
   - ✅ Search "DTX-001" → tìm thấy
   - ✅ Nhập Vendor Invoice Ref → auto chuyển "Invoice Linked"

---

## 🎯 TIẾP THEO LÀM GÌ?

### Sau khi test OK module dtx_serial_ext:

1. ✅ Báo cho tôi
2. ✅ Tôi sẽ tạo module 2: `dtx_vendorbill_alert`
3. ✅ Test module 2
4. ✅ Tạo module 3: `dtx_ops_project`
5. ✅ Test cả 3 modules tích hợp
6. ✅ Deploy lên production server

---

## 📊 THÔNG TIN KỸ THUẬT

### Môi trường:
- **OS:** macOS (M1 chip)
- **Odoo:** 16.0 Community Edition
- **Database:** PostgreSQL 15
- **Container Engine:** Docker Desktop
- **Port:** 8069 (Odoo), 5432 (PostgreSQL)

### Default credentials:
- **Odoo URL:** http://localhost:8069
- **Database:** dtx_dev
- **Admin user:** admin@dtx.com
- **Admin password:** admin
- **DB user:** odoo
- **DB password:** odoo

### Module đã cài sẵn:
- ✅ dtx_serial_ext (trong addons folder)

---

## ⚠️ TROUBLESHOOTING

### Lỗi: Port 8069 đã được dùng
```bash
lsof -i :8069
kill -9 <PID>
./start.sh
```

### Lỗi: Docker không chạy
```bash
# Mở Docker Desktop
# Check icon ở menu bar
```

### Module không hiện trong Apps
```bash
# Restart Odoo
docker-compose restart odoo

# Vào Apps → Developer Mode → Update Apps List
```

### Reset database khi cần
```bash
./reset.sh
# Rồi vào http://localhost:8069 tạo database mới
```

---

## 💡 TIPS

### Tăng tốc development:
1. Giữ terminal mở với `./logs.sh` để xem logs realtime
2. Dùng browser developer tools (F12) để debug JS/CSS
3. Enable Odoo developer mode để xem technical info
4. Dùng `./upgrade-module.sh` thay vì restart toàn bộ

### Backup data:
```bash
# Backup database
docker exec dtx_postgres pg_dump -U odoo dtx_dev > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20250123.sql | docker exec -i dtx_postgres psql -U odoo -d dtx_dev
```

---

## ✅ CHECKLIST

Trước khi phát triển module mới, đảm bảo:

- [ ] Docker Desktop đang chạy
- [ ] Odoo đã start: `./start.sh`
- [ ] Vào được http://localhost:8069
- [ ] Database `dtx_dev` đã tạo
- [ ] Module `dtx_serial_ext` đã cài
- [ ] Test được các features cơ bản
- [ ] Hiểu workflow: sửa code → upgrade → refresh

---

## 📞 HỖ TRỢ

**Có vấn đề?**

1. Đọc QUICKSTART.md trong odoo-dev/
2. Check logs: `./logs.sh`
3. Hỏi tôi với thông tin:
   - Lệnh đã chạy
   - Error message
   - Screenshot nếu có

---

## 🎉 SẴN SÀNG CODE!

Môi trường dev đã setup xong. Bạn có thể:

✅ Phát triển và test module local
✅ Thử nghiệm không sợ hỏng production
✅ Reset và test lại dễ dàng
✅ Deploy lên production khi đã ổn

**Bắt đầu thôi:**
```bash
cd /Users/trungns/dtx_project/odoo-dev
./start.sh
```

Sau đó mở: http://localhost:8069

Good luck! 🚀
