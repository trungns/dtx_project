# DTX Serial Extension - Testing Guide

## 🎉 Version 2.1.0+ : FULLY AUTOMATIC!

**Vendor Invoice State bây giờ TỰ ĐỘNG cập nhật** khi bill được post/cancel.
Không cần manual trigger hay script Python nữa!

---

## Scenario 1: Normal Flow (Receipt → Bill) ✅ RECOMMENDED

**Flow tự nhiên nhất trong Odoo:**

1. **Tạo PO:**
   - Purchase > Orders > Create
   - Chọn vendor, product có serial tracking
   - Confirm Order

2. **Validate Receipt & Assign Serial:**
   - Vào receipt (WH/IN/XXXXX)
   - Click "Check Availability"
   - Click "Validate"
   - Assign serial number (VD: SN001)
   - Confirm

3. **Kiểm tra Serial (sau validate receipt):**
   - Inventory > Device Serials
   - Tìm serial vừa tạo (SN001)
   - **Kết quả mong đợi:**
     - ✅ Lifecycle State = "In Stock"
     - ✅ Purchase Orders = [P00007]
     - ✅ Vendor Bills = [] (trống)
     - ✅ Vendor Invoice State = "Invoice Missing" (ĐÚNG - vì chưa có bill)

4. **Tạo Vendor Bill:**
   - Purchase > Orders > Mở PO vừa tạo
   - Click "Create Bill"
   - Điền thông tin invoice date, bill reference
   - Click "Confirm" (Post)

5. **✨ AUTO-UPDATE (v2.1.0+) - KHÔNG CẦN LÀM GÌ:**
   - **Refresh serial page** (F5)
   - **Kết quả mong đợi:**
     - ✅ Vendor Bills = [BILL/2024/XXX] (tự động)
     - ✅ Vendor Invoice State = **"Invoice Linked"** (TỰ ĐỘNG UPDATE!) ✨

   **KHÔNG CẦN:**
   - ❌ Trigger manual script
   - ❌ Validate receipt mới
   - ❌ Edit field manually

   **Chỉ cần Post Bill → State tự động linked!**

---

## Scenario 2: Bill BEFORE Receipt ⚠️

**Flow này CÓ THỂ gây missing state:**

1. Tạo PO → Confirm
2. ❌ **TẠO BILL TRƯỚC** (không nên)
3. Validate Receipt → Assign Serial
4. **Kết quả:**
   - Module check bill khi validate receipt
   - Nếu bill đã posted → state = "linked" ✅
   - Nếu bill còn draft → state = "missing" (phải post bill sau đó manual update)

---

## Scenario 3: Multiple Receipts from Same PO

**Test auto-linking với nhiều receipts:**

1. Tạo PO với quantity = 10
2. Validate receipt 1: quantity = 3 → Assign 3 serials
3. Tạo bill từ PO → Post
4. Validate receipt 2: quantity = 7 → Assign 7 serials
5. **Kết quả mong đợi:**
   - Receipt 1 serials: vendor_invoice_state = "missing" (bill được tạo SAU receipt)
   - Receipt 2 serials: vendor_invoice_state = "linked" (bill đã tồn tại KHI validate receipt)

---

## Manual Update Vendor Invoice State

**Khi bill được tạo MUỘN sau receipt:**

### Cách 1: Qua UI (Đơn giản)

1. Mở serial record
2. Chuyển "Vendor Invoice State" từ "Invoice Missing" → "Invoice Linked"
3. Thêm note vào "Vendor Invoice Notes": "Bill BILL/2024/001 posted on 2024-12-25"

### Cách 2: Bulk Update qua Python

```python
# Tìm tất cả serials từ PO cụ thể với state = missing
po = env['purchase.order'].search([('name', '=', 'P00007')])

# Tìm vendor bill của PO này
bill = env['account.move'].search([
    ('move_type', '=', 'in_invoice'),
    ('invoice_origin', '=', po.name),
    ('state', '=', 'posted')
], limit=1)

if bill:
    # Tìm tất cả serials từ PO này
    move_lines = env['stock.move.line'].search([
        ('move_id.purchase_line_id.order_id', '=', po.id),
        ('lot_id', '!=', False)
    ])

    lots = move_lines.mapped('lot_id').filtered(
        lambda l: l.vendor_invoice_state == 'missing'
    )

    # Update tất cả
    for lot in lots:
        lot.write({
            'vendor_invoice_state': 'linked',
            'vendor_invoice_note': f'Bill {bill.name} posted on {bill.invoice_date}, linked manually'
        })

    print(f"Updated {len(lots)} serials to 'linked' state")
else:
    print("No posted bill found for this PO")
```

---

## Testing Logs

**Khi validate receipt, kiểm tra logs:**

```bash
cd /Users/trungns/dtx_project/odoo-dev
docker-compose logs -f web | grep "DTX Serial"
```

**Logs mong đợi khi validate receipt:**

```
=== DTX Serial Extension: _action_done called for 1 move lines ===
DTX Serial: Processing move line 123 - Lot: SN001, From: Vendors (supplier) -> To: WH/Stock (internal)
DTX Serial: Lot SN001 -> STOCK (incoming from supplier)
DTX Serial: Updating lot SN001 state from 'stock' to 'stock'
=== DTX Serial: Checking vendor invoice state for 1 move lines ===
DTX Serial: Checking vendor invoice for lot SN001 from PO P00007
```

**Nếu bill CHƯA tồn tại:**
```
DTX Serial: No posted vendor bill found for PO P00007
```

**Nếu bill ĐÃ posted:**
```
DTX Serial: Found vendor bill BILL/2024/001 for lot SN001, updating state to 'linked'
```

---

## Expected Behavior Summary

| Timing | Receipt Validated | Bill Posted | Expected State | Auto-Update? |
|--------|------------------|-------------|----------------|--------------|
| Bill BEFORE Receipt | ❌ Not yet | ✅ Posted | ✅ "linked" | ✅ Yes |
| Bill AFTER Receipt | ✅ Done | ❌ Not yet | ✅ "missing" | ❌ Need manual update |
| Bill AFTER Receipt | ✅ Done | ✅ Posted later | ⚠️ "missing" | ❌ Need manual trigger |

---

## Troubleshooting

### Issue: State stuck at "missing" even after bill posted

**Nguyên nhân:** Bill được post SAU khi receipt đã validate

**Giải pháp:**
1. Manual update state qua UI
2. Hoặc trigger lại check qua Python (xem Scenario 1, Bước 5, Cách B)
3. Hoặc đợi validate receipt tiếp theo từ cùng PO (nếu có)

### Issue: Multiple bills for same PO

**Module behavior:** Lấy bill MỚI NHẤT (order by invoice_date desc)

**Nếu muốn link bill khác:**
- Manual update state = "replaced"
- Add note: "Original bill BILL/001 replaced by BILL/002 dated ..."

---

## Recommended Workflow

✅ **BEST PRACTICE:**

1. Create PO
2. Validate Receipt → Assign Serial
3. **Check serial: state should be "missing"** ✅
4. Create Bill from PO → Post
5. **Option A:** Validate next receipt from same PO (auto-update)
6. **Option B:** Manual update serial state to "linked"

❌ **AVOID:**
- Creating bill before validating receipt (timing issue)
- Posting bill long after receipt (requires manual update)

---

## Future Enhancement Ideas

**Auto-recheck on bill post (không có trong v2.0.1):**

```python
# Potential enhancement: Add to account.move
class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()

        # If this is a vendor bill
        if self.move_type == 'in_invoice' and self.invoice_origin:
            # Find all serials from this PO with missing state
            lots = self.env['stock.lot'].search([
                ('purchase_order_ids.name', '=', self.invoice_origin),
                ('vendor_invoice_state', '=', 'missing'),
            ])

            # Auto-update to linked
            for lot in lots:
                lot.write({'vendor_invoice_state': 'linked'})
                lot.message_post(
                    body=f"Vendor invoice {self.name} posted and auto-linked",
                    subject="Invoice State Auto-Updated"
                )

        return res
```

**Nếu cần tính năng này, báo cho team dev!**
