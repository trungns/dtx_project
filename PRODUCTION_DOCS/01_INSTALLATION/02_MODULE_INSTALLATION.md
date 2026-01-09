# CÀI ĐẶT CÁC MODULE DTX

**Phiên bản**: 2.0.0
**Cập nhật**: 2026-01-09

---

## CÁC MODULE CẦN CÀI

### 1. dtx_serial_ext (v2.2.0)
**Chức năng**: Quản lý Serial Numbers nâng cao

### 2. dtx_product_standards (v1.1.0)
**Chức năng**: Chuẩn hóa danh mục sản phẩm

### 3. dtx_sales_pakd_contract (v1.4.0)
**Chức năng**: Quản lý PAKD và Hợp đồng

---

## CÁCH CÀI ĐẶT

### Option 1: Qua Odoo UI (Khuyến nghị)

```
1. Login as admin
2. Vào Apps → Update Apps List
3. Tìm "DTX" → Sẽ thấy 3 modules
4. Click Install cho từng module theo thứ tự:
   - dtx_product_standards (cài trước)
   - dtx_serial_ext
   - dtx_sales_pakd_contract (cài sau cùng)
5. Đợi installation hoàn tất
```

### Option 2: Qua Command Line

```bash
# Docker environment
docker-compose exec odoo odoo -d dtx_production \
  -i dtx_product_standards,dtx_serial_ext,dtx_sales_pakd_contract \
  --stop-after-init

docker-compose restart odoo

# Native installation
sudo -u odoo odoo -d dtx_production \
  -i dtx_product_standards,dtx_serial_ext,dtx_sales_pakd_contract \
  --stop-after-init

sudo systemctl restart odoo
```

---

## SAU KHI CÀI ĐẶT

### 1. Kiểm tra modules đã installed

```
Apps → Filters: Installed
→ Tìm 3 modules DTX
→ Status: Installed ✓
```

### 2. Kiểm tra menus xuất hiện

- **Sales**: Menu "PAKD", "Hợp đồng"
- **Inventory**: Menu "Device Serials", "DTX - Chuẩn hóa dữ liệu"

### 3. Cấu hình ban đầu

Xem: [../02_CONFIGURATION/](../02_CONFIGURATION/)

---

## UPGRADE MODULES

Khi có phiên bản mới:

```bash
# Backup trước khi upgrade!
# Xem: ../05_MAINTENANCE/01_BACKUP_RESTORE.md

# Docker
docker-compose exec odoo odoo -d dtx_production \
  -u dtx_product_standards,dtx_serial_ext,dtx_sales_pakd_contract \
  --stop-after-init

docker-compose restart odoo

# Native
sudo -u odoo odoo -d dtx_production \
  -u dtx_product_standards,dtx_serial_ext,dtx_sales_pakd_contract \
  --stop-after-init

sudo systemctl restart odoo
```

Chi tiết: [../05_MAINTENANCE/02_MODULE_UPGRADE.md](../05_MAINTENANCE/02_MODULE_UPGRADE.md)

---

**DTX Odoo 16 - Module Installation**
