# 🚀 QUICKSTART - 5 Phút Setup

## Bước 1: Cài Docker Desktop (nếu chưa có)

### Kiểm tra đã có Docker chưa:
```bash
docker --version
```

Nếu thấy version → **BỎ QUA bước này**

Nếu chưa có:
1. Tải: https://www.docker.com/products/docker-desktop/
2. Chọn: **Mac with Apple chip** (M1)
3. Cài đặt và khởi động Docker Desktop
4. Đợi Docker Desktop hiện icon ở menu bar (góc trên phải)

---

## Bước 2: Khởi động Odoo (1 lệnh duy nhất!)

```bash
cd /Users/trungns/dtx_project/odoo-dev
./start.sh
```

**Lần đầu tiên:** Sẽ download Odoo image (~2-3 phút tùy mạng)

**Lần sau:** Chỉ mất 5-10 giây

Đợi thấy dòng:
```
✅ Odoo is starting...
🌐 Open Odoo at: http://localhost:8069
```

---

## Bước 3: Tạo Database

1. Mở trình duyệt: **http://localhost:8069**

2. Điền form tạo database:
   - **Database Name:** `dtx_dev` ⚠️ BẮT BUỘC tên này
   - **Email:** `admin@dtx.com`
   - **Password:** `admin`
   - **Phone Number:** (bỏ trống)
   - **Language:** English hoặc Tiếng Việt
   - **Country:** Vietnam
   - **Demo data:** ❌ **BỎ CHỌN** (uncheck)

3. Click **Create Database**

4. Đợi 1-2 phút → Odoo sẽ tự động login

---

## Bước 4: Cài Module DTX Serial Extension

### 4.1. Bật Developer Mode
1. Click vào **Settings** (menu bên trái)
2. Kéo xuống dưới cùng
3. Click **Activate the developer mode**
4. Đợi page reload

### 4.2. Cài Module Stock (nếu chưa có)
1. Click **Apps** (menu bên trái)
2. Search: `Inventory`
3. Tìm **Inventory** (icon màu tím)
4. Click **Install** nếu chưa cài
5. Đợi cài xong (~30 giây)

### 4.3. Update Apps List
1. Vẫn ở **Apps** menu
2. Click nút **⋮** (3 chấm dọc) góc trên phải
3. Chọn **Update Apps List**
4. Click **Update** trong popup

### 4.4. Cài DTX Serial Extension
1. Bỏ filter "Apps" trong search box (xóa filter chip)
2. Search: `DTX Serial`
3. Click **Install** trên card "DTX Serial Extension"
4. Đợi ~10 giây

---

## Bước 5: Test Module

### Test 1: Xem menu mới
1. Click **Inventory** (menu bên trái)
2. Mở submenu **Products**
3. Phải thấy menu mới: **Device Serials** ✅

### Test 2: Tạo Product với Serial Tracking
1. **Inventory → Products → Products**
2. Click **Create**
3. Điền:
   - **Product Name:** `Test Kiosk`
   - **Product Type:** Storable Product
   - **Tracking:** By Unique Serial Number ⚠️ QUAN TRỌNG
4. Click **Save**

### Test 3: Tạo Serial Number
1. **Inventory → Products → Device Serials**
2. Click **Create**
3. Điền:
   - **Lot/Serial Number:** `KIOSK-SN-001`
   - **DTX Internal Serial:** `DTX-K-001`
   - **Product:** Test Kiosk (chọn product vừa tạo)
4. Click **Save**

### Test 4: Kiểm tra Features
✅ Lifecycle State badge màu xanh: "In Stock"
✅ Vendor Invoice State badge màu đỏ: "Invoice Missing"
✅ Display name hiện: "KIOSK-SN-001 [DTX-K-001]"

### Test 5: Search
1. Ở list view Device Serials
2. Search: `DTX-K-001`
3. Phải tìm thấy serial vừa tạo ✅

### Test 6: Vendor Invoice Auto-Update
1. Mở serial vừa tạo
2. Nhập **Vendor Invoice Reference:** `INV-2025-001`
3. Click **Save**
4. **Vendor Invoice State** tự động đổi sang màu xanh: "Invoice Linked" ✅

---

## ✅ HOÀN TẤT!

Bạn đã setup xong môi trường dev và test được module!

---

## 📚 Các Commands Hữu Ích

### Xem logs realtime (để debug)
```bash
cd /Users/trungns/dtx_project/odoo-dev
./logs.sh
```
Nhấn Ctrl+C để thoát

### Upgrade module sau khi sửa code
```bash
cd /Users/trungns/dtx_project/odoo-dev
./upgrade-module.sh dtx_serial_ext
```

### Restart Odoo
```bash
docker-compose restart odoo
```

### Dừng Odoo (giữ data)
```bash
docker-compose stop
```

### Khởi động lại (sau khi dừng)
```bash
./start.sh
```

### Reset toàn bộ (XÓA HẾT DATA)
```bash
./reset.sh
```

---

## 🔧 Development Workflow

### Khi sửa code Python (.py):
1. Sửa file trong: `/Users/trungns/dtx_project/odoo-dev/addons/dtx_serial_ext/`
2. Chạy: `./upgrade-module.sh`
3. Refresh browser

### Khi sửa XML views:
1. Sửa file `.xml`
2. Chạy: `./upgrade-module.sh`
3. Refresh browser

### Khi thêm field mới:
1. Sửa file Python
2. **BẮT BUỘC chạy:** `./upgrade-module.sh`
3. Refresh browser

---

## ⚠️ Troubleshooting

### Port 8069 bị chiếm
```bash
# Tìm và kill process
lsof -i :8069
kill -9 <PID>
```

### Docker không start
```bash
# Mở Docker Desktop
# Check icon ở menu bar phải hiện
```

### Module không xuất hiện
```bash
# Kiểm tra file có trong container
docker exec dtx_odoo16 ls -la /mnt/extra-addons/

# Restart và update apps list
docker-compose restart odoo
# Rồi vào Apps → Update Apps List
```

### Quên mật khẩu admin
```bash
# Reset database
./reset.sh
# Tạo database mới
```

---

## 📂 File Structure

```
odoo-dev/
├── start.sh              ← Khởi động Odoo
├── logs.sh               ← Xem logs
├── upgrade-module.sh     ← Upgrade module
├── reset.sh              ← Reset toàn bộ
├── docker-compose.yml    ← Config containers
├── config/
│   └── odoo.conf        ← Odoo settings
└── addons/
    └── dtx_serial_ext/  ← Module của bạn
```

---

## 🎯 Next Steps

Sau khi test OK module `dtx_serial_ext`:

1. ✅ Báo cho tôi → Tôi sẽ tạo module tiếp theo: `dtx_vendorbill_alert`
2. ✅ Test module 2
3. ✅ Tạo module 3: `dtx_ops_project`
4. ✅ Test tích hợp 3 modules
5. ✅ Deploy lên production

---

**Questions?**

Gặp lỗi gì cứ hỏi, tôi sẽ giúp debug!
