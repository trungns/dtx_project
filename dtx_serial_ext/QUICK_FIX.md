# Quick Fix: Update Vendor Invoice State

## Vấn đề
Bạn đã tạo vendor bill và register payment, nhưng serial vẫn hiển thị **Vendor Invoice State = "Invoice Missing"**

## Nguyên nhân
Module chỉ check vendor bill **KHI validate receipt**. Nếu bill được tạo SAU khi receipt đã validate, state không tự động update.

---

## ✅ Giải pháp nhanh - Chọn 1 trong 3 cách:

### Cách 1: Manual Update qua UI (Đơn giản nhất) ✅ RECOMMENDED

**Version 2.0.1+:** Field đã được làm editable!

1. Vào **Inventory > Device Serials**
2. Tìm serial cần update
3. Click vào serial để mở form (Edit mode)
4. Click vào dropdown **Vendor Invoice State**
5. Chọn "Invoice Linked" (từ "Invoice Missing")
6. (Optional) Thêm note vào **Vendor Invoice Notes**: "Linked to BILL/2024/XXX manually"
7. Click **Save**

**Ưu điểm:**
- ✅ Đơn giản nhất, không cần code
- ✅ Trực quan, thấy ngay kết quả
- ✅ Có thể undo nếu nhầm

**Nhược điểm:**
- ⚠️ Phải làm từng serial một (nếu nhiều serials, dùng Cách 2)

---

### Cách 2: Update qua Technical Menu (Nhiều serials cùng lúc)

**Yêu cầu:** Developer Mode phải được bật

1. **Bật Developer Mode:**
   - Settings > Developer Tools > Activate Developer Mode
   - Hoặc thêm `?debug=1` vào URL

2. **Mở Python Code:**
   - Settings > Technical > Python Code

3. **Copy paste code sau và click "Run":**

```python
# Update TẤT CẢ serials từ PO cụ thể (VD: P00007)
po_name = 'P00007'  # ← Thay đổi PO number ở đây

po = env['purchase.order'].search([('name', '=', po_name)], limit=1)
if po:
    # Tìm bill
    bills = env['account.move'].search([
        ('move_type', '=', 'in_invoice'),
        ('invoice_origin', '=', po.name),
        ('state', '=', 'posted'),
    ], limit=1, order='invoice_date desc')

    if bills:
        bill = bills[0]

        # Tìm tất cả serials từ PO này với state = missing
        lots = env['stock.lot'].search([
            ('purchase_order_ids', 'in', [po.id]),
            ('vendor_invoice_state', '=', 'missing'),
        ])

        # Update tất cả
        for lot in lots:
            lot.write({
                'vendor_invoice_state': 'linked',
                'vendor_invoice_note': f'Linked to {bill.name} dated {bill.invoice_date}',
            })
            lot.message_post(
                body=f"Vendor invoice {bill.name} linked manually via Python Code",
                subject="Vendor Invoice State Updated",
            )

        print(f"✓ Updated {len(lots)} serials to 'linked' state")
        print(f"  Bill: {bill.name}")
        print(f"  Serials: {lots.mapped('name')}")
    else:
        print(f"✗ No posted bill found for PO {po_name}")
else:
    print(f"✗ PO {po_name} not found")
```

**Ưu điểm:** Update nhiều serials cùng lúc
**Nhược điểm:** Cần Developer Mode

---

### Cách 3: Update qua Odoo Shell (Advanced)

**Cho admin/developer có quyền truy cập Docker:**

```bash
# 1. Vào container Odoo
cd /Users/trungns/dtx_project/odoo-dev
docker-compose exec web odoo shell -d dtx_dev

# 2. Trong Odoo shell, chạy:
from pathlib import Path
exec(Path('/mnt/extra-addons/dtx_serial_ext/scripts/recheck_vendor_invoices.py').read_text())

# 3. Chọn function tùy nhu cầu:

# Option A: Update TẤT CẢ serials có state = missing
recheck_all_missing_invoices(env)

# Option B: Update tất cả serials từ PO cụ thể
recheck_po_invoices(env, 'P00007')

# Option C: Update 1 serial cụ thể
recheck_serial_invoice(env, 'SN001')

# 4. Ctrl+D để thoát
```

---

## 🔍 Kiểm tra kết quả

Sau khi update, refresh page và kiểm tra:

1. **Vendor Invoice State** đã đổi sang "Invoice Linked" ✅
2. **Vendor Bills** field hiển thị bill đã link ✅
3. **Chatter** (tab Messages) có log về việc update ✅

---

## 📊 Ví dụ thực tế

### Scenario của bạn:
- PO: P00007
- Receipt: WH/IN/00007 (đã validated, serial đã assigned)
- Bill: Đã tạo và posted
- **Vấn đề:** Serial vẫn showing "Invoice Missing"

### Quick fix:
```python
# Dùng Cách 2 (Python Code trong Settings > Technical)
po_name = 'P00007'
# ... copy paste code từ Cách 2 ...
```

Hoặc đơn giản hơn: **Dùng Cách 1** - mở serial form và đổi state manually.

---

## ⚠️ Lưu ý

### Khi nào state tự động update?
Module **CHỈ** tự động check vendor bill khi:
- Validate receipt MỚI từ cùng PO đó
- Bill ĐÃ posted TRƯỚC khi validate receipt

### Best Practice để tránh manual update:
1. ✅ **Tạo bill TRƯỚC khi validate receipt** (recommended)
2. ✅ Hoặc validate receipt theo batches (nếu PO có nhiều dòng)

### Khi nào cần manual update?
- Bill được tạo SAU khi receipt đã validate ← Trường hợp của bạn
- Bulk import serials từ hệ thống cũ
- Fix data migration issues

---

## 🔮 Feature Request: Auto-recheck on bill post

**Hiện tại chưa có tính năng này.** Nếu cần, có thể enhance module để:
- Tự động recheck tất cả serials khi vendor bill được posted
- Thêm button "Recheck Invoice" trên serial form

Báo cho dev team nếu cần tính năng này!

---

## 📞 Cần giúp đỡ?

Nếu gặp lỗi khi chạy script:
1. Copy full error message
2. Check logs: `docker-compose logs -f web | grep "DTX Serial"`
3. Liên hệ dev team với:
   - PO number
   - Serial number
   - Bill number
   - Error message (nếu có)
