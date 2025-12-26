# DTX Serial Extension - Troubleshooting Guide

## Common Issues and Solutions

### Issue: "Bản ghi thiếu" / "Missing Record" Error

**Error Message:**
```
Dữ liệu không tồn tại hoặc đã bị xóa.
(Dữ liệu: stock.move.line(12,), Người dùng: 2)
```

**Mô tả:**
Lỗi này xảy ra khi module cố gắng truy cập vào stock.move.line đã bị xóa hoặc không còn tồn tại trong quá trình xử lý.

**Nguyên nhân có thể:**
1. Module được kích hoạt sau khi `_action_done()` của parent đã xử lý xong và xóa một số move lines
2. Race condition khi nhiều module cùng xử lý move lines
3. Transaction rollback do lỗi khác trong hệ thống

**Giải pháp đã áp dụng (Version 2.0.1):**
- Thêm kiểm tra `move_line.exists()` trước khi xử lý
- Bọc tất cả xử lý trong try-except blocks
- Thêm logging chi tiết để debug
- Skip các move lines không tồn tại thay vì raise error

**Cách kiểm tra logs:**

1. **Xem logs trong container Odoo:**
```bash
cd /Users/trungns/dtx_project/odoo-dev
docker-compose logs -f --tail=100 web
```

2. **Filter logs của DTX Serial Extension:**
```bash
docker-compose logs -f web | grep "DTX Serial"
```

3. **Logs bạn sẽ thấy khi module hoạt động đúng:**
```
INFO - DTX Serial Extension: _action_done called for X move lines
INFO - DTX Serial: Processing move line 123 - Lot: ABC123, From: Vendor/Location -> To: WH/Stock
INFO - DTX Serial: Lot ABC123 -> STOCK (incoming from supplier)
INFO - DTX Serial: Updating lot ABC123 state from 'stock' to 'stock'
```

4. **Logs khi có lỗi:**
```
WARNING - DTX Serial: Move line 12 no longer exists, skipping
ERROR - DTX Serial: Error processing move line 12: [error details]
```

---

## Debugging Steps

### Step 1: Enable Debug Mode in Odoo

1. Truy cập Odoo UI
2. Settings > Activate Developer Mode
3. Hoặc thêm `?debug=1` vào URL

### Step 2: Check Module Installation

```bash
# Vào Odoo shell
docker-compose exec web odoo shell -d dtx_dev

# Kiểm tra module
env['ir.module.module'].search([('name', '=', 'dtx_serial_ext')]).state
# Kết quả phải là 'installed'
```

### Step 3: Verify Database Consistency

```bash
# Kiểm tra serial numbers
SELECT id, name, lifecycle_state, vendor_invoice_state
FROM stock_lot
WHERE create_date > NOW() - INTERVAL '1 day';

# Kiểm tra move lines
SELECT sml.id, sml.lot_id, sm.purchase_line_id
FROM stock_move_line sml
JOIN stock_move sm ON sml.move_id = sm.id
WHERE sml.create_date > NOW() - INTERVAL '1 day';
```

### Step 4: Test Flow with Logging

**Purchase Order → Receipt → Serial Assignment:**

1. Tạo Purchase Order mới
2. Confirm PO
3. Vào Receipt (WH/IN/XXXXX)
4. Assign serial number
5. Validate
6. **Quan sát logs ngay lập tức:**
   ```bash
   docker-compose logs -f web | grep "DTX Serial"
   ```

**Logs mong đợi:**
```
=== DTX Serial Extension: _action_done called for 1 move lines ===
DTX Serial: Processing move line 456 - Lot: SN001, From: Vendors (supplier) -> To: WH/Stock (internal)
DTX Serial: Lot SN001 -> STOCK (incoming from supplier)
DTX Serial: Updating lot SN001 state from 'stock' to 'stock'
=== DTX Serial: Checking vendor invoice state for 1 move lines ===
DTX Serial: Checking vendor invoice for lot SN001 from PO P00123
DTX Serial: No posted vendor bill found for PO P00123
```

---

## Known Issues

### 1. Move Line Deletion Race Condition

**Status:** FIXED in v2.0.1
**Fix:** Added `exists()` check before processing

### 2. Vendor Bill Not Auto-Linked

**Symptom:** Vendor invoice state stays "missing" even after bill is posted

**Possible causes:**
- Bill was posted BEFORE receipt was validated
- Bill's `invoice_origin` field doesn't match PO name exactly

**Solution:**
```python
# Manual fix via Odoo shell
lot = env['stock.lot'].search([('name', '=', 'YOUR_SERIAL')])
lot.vendor_invoice_state = 'linked'
```

**Permanent fix:** Create bill AFTER validating receipt, or manually update state

---

## Reporting Issues

Khi gặp lỗi, vui lòng cung cấp:

1. **Error message đầy đủ** (screenshot hoặc copy text)
2. **Steps to reproduce:**
   - Đang ở màn hình nào
   - Thao tác gì đã làm
   - Record nào (PO number, Serial number, etc.)

3. **Logs from Docker:**
   ```bash
   docker-compose logs --tail=200 web > odoo_logs.txt
   ```

4. **Module version:**
   ```python
   # Trong Odoo shell
   env['ir.module.module'].search([('name', '=', 'dtx_serial_ext')]).installed_version
   ```

5. **Odoo environment:**
   - Odoo version: 16.0
   - Database name
   - Other installed modules

---

## Development & Testing

### Run Tests
```bash
# Unit tests (if available)
docker-compose exec web odoo -d dtx_dev -i dtx_serial_ext --test-enable

# Manual testing checklist
- [ ] Create PO with serial tracking product
- [ ] Validate receipt and assign serial
- [ ] Check serial lifecycle state = 'stock'
- [ ] Create and post vendor bill
- [ ] Check vendor_invoice_state = 'linked'
- [ ] Create SO and deliver
- [ ] Check lifecycle state = 'delivered'
```

### Debug Mode Settings

File: `/Users/trungns/dtx_project/odoo-dev/config/odoo.conf`
```ini
dev_mode = reload,qweb,werkzeug,xml
log_level = debug
log_handler = :DEBUG
```

---

## Version History

### v2.0.1 (2025-12-25)
- ✅ Added comprehensive logging
- ✅ Added `exists()` checks for move lines
- ✅ Wrapped all processing in try-except blocks
- ✅ Fixed "Missing Record" error when processing deleted move lines

### v2.0.0 (2025-12-25)
- Refactored to use Many2many relationships
- Automatic PO/SO/Invoice linking via stock moves
- Vendor invoice state tracking

---

## Contact

**DTX Development Team**
- Email: dev@dtx.com
- Documentation: `/Users/trungns/dtx_project/docs/`
