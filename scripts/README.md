# DTX SETUP SCRIPTS

**Mục đích**: Tự động setup cấu hình chuẩn cho DTX Odoo 16

**Sử dụng**: Chạy sau khi cài đặt Odoo 16 và modules DTX

---

## 📋 DANH SÁCH SCRIPTS

### 1. Setup Scripts (Chạy lần đầu)

| Script | Chức năng | Thứ tự |
|--------|-----------|--------|
| **01_setup_taxes.py** | Tạo VAT 0%, 5%, 8%, 10% | 1 |
| **02_setup_product_categories.py** | Tạo danh mục sản phẩm với AVCO | 2 |
| **03_setup_dtx_product_types.py** | Cấu hình 4 loại sản phẩm DTX | 3 |
| **04_setup_payment_terms.py** | Tạo điều khoản thanh toán (15, 30, 60 ngày) | 4 |
| **05_setup_locations.py** | Tạo locations cho kho & đối tác | 5 |
| **06_create_sample_products.py** | Tạo sản phẩm mẫu (optional) | 6 |

### 2. Utility Scripts

| Script | Chức năng |
|--------|-----------|
| **utils/odoo_client.py** | Odoo XML-RPC client helper |
| **utils/config.py** | Configuration manager |
| **run_all_setup.py** | Chạy tất cả setup scripts |

---

## 🚀 CÁCH SỬ DỤNG

### Quick Start (Tự động - Khuyến nghị)

```bash
# 1. Cấu hình kết nối
cp config.example.ini config.ini
nano config.ini  # Sửa URL, database, username, password

# 2. Chạy tất cả setup scripts
python3 run_all_setup.py

# Kết quả:
# ✅ Taxes created
# ✅ Product categories created
# ✅ DTX product types configured
# ✅ Payment terms created
# ✅ Locations created
```

### Manual Setup (Từng bước)

```bash
# 1. Setup taxes
python3 setup/01_setup_taxes.py

# 2. Setup product categories
python3 setup/02_setup_product_categories.py

# 3. Setup DTX product types
python3 setup/03_setup_dtx_product_types.py

# 4. Setup payment terms
python3 setup/04_setup_payment_terms.py

# 5. Setup locations
python3 setup/05_setup_locations.py

# 6. (Optional) Create sample products
python3 setup/06_create_sample_products.py
```

---

## 📝 CẤU HÌNH

### config.ini

```ini
[odoo]
url = http://localhost:8069
database = dtx_dev
username = admin
password = admin

[setup]
# Skip nếu đã tồn tại
skip_existing = true

# Tạo sample data
create_samples = false
```

---

## 📦 CÁC CẤU HÌNH ĐƯỢC TẠO

### 1. Taxes (VAT)

| Tax | Type | Amount | Scope |
|-----|------|--------|-------|
| VAT 0% | Sale/Purchase | 0% | Sale |
| VAT 5% | Sale/Purchase | 5% | Sale |
| VAT 8% | Sale/Purchase | 8% | Sale |
| VAT 10% | Sale/Purchase | 10% | Sale |

**Lý do**: PAKD auto-map VAT% → account.tax

---

### 2. Product Categories (với AVCO)

| Category | Parent | Costing Method | Description |
|----------|--------|----------------|-------------|
| **DTX Products** | All | - | Root category |
| └─ **DTX Hardware** | DTX Products | AVCO | Thiết bị phần cứng |
|    ├─ DTX Components | DTX Hardware | AVCO | Linh kiện |
|    ├─ DTX Finished Products | DTX Hardware | AVCO | Thành phẩm (Kiosk) |
|    └─ DTX Accessories | DTX Hardware | AVCO | Phụ kiện |
| └─ **DTX Services** | DTX Products | - | Dịch vụ |

**Lý do**:
- AVCO (Average Cost) chuẩn cho serial tracking
- Phân loại rõ ràng Components vs Finished Products

---

### 3. DTX Product Types (x_dtx_type)

Script sẽ verify/guide setup 4 loại:

1. **device_serial**: Thiết bị quản lý theo Serial
   - Tracking: By Unique Serial Number
   - Type: Storable Product
   - Can be Purchased/Sold: True

2. **component**: Linh kiện / vật tư tiêu hao
   - Tracking: No Tracking (hoặc By Lots)
   - Type: Storable Product
   - Can be Purchased: True, Can be Sold: False

3. **kiosk**: Kiosk / Thiết bị hoàn chỉnh
   - Tracking: By Unique Serial Number
   - Type: Storable Product
   - Can be Purchased: False, Can be Sold: True
   - Cần có BOM

4. **service**: Dịch vụ
   - Type: Service
   - Tracking: No Tracking

**Lý do**: Module `dtx_product_standards` cần 4 loại này

---

### 4. Payment Terms

| Name | Days | Description |
|------|------|-------------|
| 15 Days | 15 | Net 15 Days |
| 30 Days | 30 | Net 30 Days (mặc định) |
| 60 Days | 60 | Net 60 Days |
| Immediate Payment | 0 | Thanh toán ngay |

**Lý do**: Chuẩn cho B2B sales

---

### 5. Locations

| Location | Type | Usage |
|----------|------|-------|
| WH/Stock | Internal | Kho chính (mặc định có sẵn) |
| WH/Stock/Components | Internal | Kho linh kiện |
| WH/Stock/Finished | Internal | Kho thành phẩm |
| WH/Maintenance | Internal | Kho bảo trì |
| Partner Locations/Subcontractors | External | Đối tác gia công |

**Lý do**: Phân loại kho rõ ràng

---

## 🔧 DEPENDENCIES

### Python Packages

Không cần package ngoài, chỉ dùng built-in Python 3:
- `xmlrpc.client` - Odoo XML-RPC
- `configparser` - Read config.ini
- `argparse` - CLI arguments

### Odoo Modules Required

- `account` - Taxes, payment terms
- `product` - Product categories
- `stock` - Locations, tracking
- `dtx_product_standards` - DTX product types

---

## ⚠️ LƯU Ý QUAN TRỌNG

### 1. Chạy sau khi cài modules

```bash
# Đảm bảo đã install 3 modules:
# - dtx_product_standards
# - dtx_serial_ext
# - dtx_sales_pakd_contract
```

### 2. Backup trước khi chạy

```bash
# Backup database trước
./backup.sh
```

### 3. Idempotent Scripts

Tất cả scripts đều **idempotent** - có thể chạy nhiều lần:
- Check exist trước khi create
- Skip nếu đã tồn tại (với `skip_existing = true`)
- Update nếu cần (với `skip_existing = false`)

### 4. Logs

Tất cả scripts ghi log vào console:
```
[INFO] Checking taxes...
[OK] VAT 10% already exists, skipped
[CREATE] VAT 0% created successfully
```

---

## 🧪 TESTING

### Dry Run Mode

```bash
# Chạy thử không tạo thật (planned)
python3 run_all_setup.py --dry-run
```

### Verify Setup

```bash
# Verify tất cả cấu hình đã OK
python3 utils/verify_setup.py

# Output:
# ✅ Taxes: 4/4
# ✅ Categories: 6/6
# ✅ Payment Terms: 4/4
# ✅ Locations: 5/5
```

---

## 📚 EXAMPLES

### Example 1: Setup trên máy Windows mới

```powershell
# 1. Clone repo
git clone https://github.com/trungns/dtx_project.git
cd dtx_project\scripts

# 2. Cấu hình
copy config.example.ini config.ini
notepad config.ini

# 3. Chạy setup
python run_all_setup.py

# 4. Verify
python utils\verify_setup.py
```

### Example 2: Setup trên Production Server

```bash
# 1. SSH vào server
ssh user@production-server

# 2. Clone hoặc copy scripts
cd /opt/dtx/scripts

# 3. Cấu hình production
nano config.ini
# [odoo]
# url = http://localhost:8069
# database = dtx_production
# username = admin
# password = STRONG_PASSWORD

# 4. Chạy setup
python3 run_all_setup.py

# 5. Verify
python3 utils/verify_setup.py
```

---

## 🔄 UPDATE/RESET

### Reset tất cả

```bash
# Xóa tất cả cấu hình đã tạo (NGUY HIỂM!)
python3 utils/reset_all.py --confirm

# Chạy lại setup
python3 run_all_setup.py
```

### Update một phần

```bash
# Update chỉ taxes
python3 setup/01_setup_taxes.py --force-update
```

---

## 🐛 TROUBLESHOOTING

### Lỗi kết nối

```
Error: Cannot connect to Odoo
```

**Fix**:
1. Kiểm tra Odoo đã chạy: `docker-compose ps`
2. Kiểm tra URL trong `config.ini`
3. Kiểm tra username/password

### Lỗi quyền

```
Error: Access Denied
```

**Fix**:
1. Kiểm tra user có quyền `Settings` (Admin)
2. Kiểm tra module `dtx_product_standards` đã install

### Module chưa cài

```
Error: Model 'product.template' has no field 'x_dtx_type'
```

**Fix**:
```bash
# Install module dtx_product_standards
docker-compose exec odoo odoo -d dtx_dev -i dtx_product_standards --stop-after-init
```

---

## 📞 HỖ TRỢ

- **Documentation**: `/PRODUCTION_DOCS/`
- **Issues**: Tạo ticket nội bộ
- **Dev Team**: contact@dtx.com

---

**DTX Setup Scripts v1.0**
**Date**: 2026-01-09
**Status**: ✅ READY TO USE
