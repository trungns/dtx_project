# Upgrade to Version 2.1.0 - Auto-Compute Vendor Invoice State

## 🎉 Major Improvement: Fully Automatic Vendor Invoice State

**Version 2.1.0** thay đổi cách `vendor_invoice_state` hoạt động:

### ❌ Trước (v2.0.x):
- State chỉ check **KHI validate receipt**
- Bill được post SAU → State vẫn "missing" → Phải manual update
- Cần script Python hoặc manual edit

### ✅ Bây giờ (v2.1.0):
- State **TỰ ĐỘNG COMPUTED** từ `vendor_bill_ids`
- Bill được post → State **NGAY LẬP TỨC** = "linked" ✅
- Bill bị cancel → State tự động về "missing"
- **KHÔNG CẦN** manual update nữa!

---

## 🔄 Breaking Changes

### Field Definition Changed

**Before:**
```python
vendor_invoice_state = fields.Selection(
    default='missing',
    required=True,
)
```

**After:**
```python
vendor_invoice_state = fields.Selection(
    compute='_compute_vendor_invoice_state',
    store=True,
    readonly=False,  # Allow manual override for 'replaced' state
)
```

### Impact:
- ✅ Existing data: **KHÔNG ẢNH HƯỞNG** - data được giữ nguyên
- ✅ Sau upgrade: State sẽ tự động recompute theo bills hiện có
- ✅ New serials: State tự động computed

---

## 📋 Upgrade Steps

### Step 1: Backup Database (RECOMMENDED)

```bash
# Backup database
docker-compose exec db pg_dump -U odoo dtx_dev > backup_before_v2.1.0.sql
```

### Step 2: Stop Odoo

```bash
cd /Users/trungns/dtx_project/odoo-dev
docker-compose stop web
```

### Step 3: Update Module Files

Module đã được update sẵn trong:
- `/Users/trungns/dtx_project/odoo-dev/addons/dtx_serial_ext/`
- `/Users/trungns/dtx_project/dtx_serial_ext/` (production)

### Step 4: Start Odoo

```bash
docker-compose start web
```

### Step 5: Upgrade Module in Odoo UI

1. Login to Odoo
2. **Apps** > Search "DTX Serial Extension"
3. Click **Upgrade**
4. Wait for upgrade to complete

### Step 6: Recompute Existing Serials (Optional but Recommended)

**Via Settings > Technical > Python Code:**

```python
# Recompute vendor_invoice_state for all existing serials
lots = env['stock.lot'].search([])
lots._compute_vendor_invoice_state()

print(f"Recomputed {len(lots)} serial numbers")

# Check results
missing = lots.filtered(lambda l: l.vendor_invoice_state == 'missing')
linked = lots.filtered(lambda l: l.vendor_invoice_state == 'linked')

print(f"Missing: {len(missing)}")
print(f"Linked: {len(linked)}")
```

**Via Odoo Shell:**

```bash
docker-compose exec web odoo shell -d dtx_dev

# In shell:
lots = env['stock.lot'].search([])
lots._compute_vendor_invoice_state()
env.cr.commit()
```

---

## 🧪 Testing the New Behavior

### Test Case 1: Normal Flow (Receipt → Bill)

**Bước 1: Tạo PO và Validate Receipt**
```
1. Tạo PO → Confirm
2. Validate Receipt → Assign Serial "TEST001"
3. Check serial:
   ✅ vendor_invoice_state = "missing" (đúng - chưa có bill)
   ✅ vendor_bill_ids = [] (trống)
```

**Bước 2: Tạo và Post Bill**
```
4. Purchase > Orders > Mở PO > Create Bill
5. Post Bill
6. Refresh serial page:
   ✅ vendor_bill_ids = [BILL/2024/XXX] (tự động hiển thị)
   ✅ vendor_invoice_state = "linked" (TỰ ĐỘNG UPDATE!) ✨
```

**KHÔNG CẦN manual update nữa!**

---

### Test Case 2: Bill Cancel

**Bước 1: Cancel Bill**
```
1. Mở Bill > Set to Draft > Cancel
2. Refresh serial page:
   ✅ vendor_bill_ids = [] (bill không còn counted)
   ✅ vendor_invoice_state = "missing" (TỰ ĐỘNG về missing)
```

---

### Test Case 3: Manual Override to "Replaced"

**Scenario:** Bill bị thay thế bằng bill khác, cần mark là "replaced"

```
1. Mở serial form
2. Đổi vendor_invoice_state → "Invoice Replaced"
3. Thêm note: "Original bill XXX replaced by YYY"
4. Save

✅ State = "replaced"
✅ System sẽ KHÔNG tự động override về "linked" hoặc "missing"
✅ Chỉ manual mới đổi được
```

---

## 📊 State Transition Logic

```
vendor_bill_ids (computed) → vendor_invoice_state (auto-computed)

IF posted bills exist:
  IF current_state != 'replaced':
    → state = 'linked' ✅
  ELSE:
    → keep 'replaced' (manual override respected)

ELSE (no bills):
  IF current_state != 'replaced':
    → state = 'missing' ✅
  ELSE:
    → keep 'replaced' (manual override respected)
```

---

## 🔍 Troubleshooting

### Issue: State không tự động update sau upgrade

**Solution:**
```python
# Recompute manually
lot = env['stock.lot'].search([('name', '=', 'YOUR_SERIAL')])
lot._compute_vendor_invoice_state()
env.cr.commit()
```

### Issue: State bị stuck ở "replaced" khi có bill mới

**Expected behavior:** Đây là tính năng! "Replaced" là manual override.

**Solution nếu muốn reset:**
```python
lot = env['stock.lot'].search([('name', '=', 'YOUR_SERIAL')])
lot.vendor_invoice_state = 'linked'  # Manual reset
```

---

## ⚡ Performance Notes

- Field is **computed + stored** → Fast reads
- Recompute triggered when `vendor_bill_ids` changes
- No performance impact on normal operations

---

## 🎯 Benefits of v2.1.0

| Feature | v2.0.x | v2.1.0 |
|---------|--------|--------|
| Auto-update on bill post | ❌ No | ✅ Yes |
| Manual trigger needed | ✅ Yes | ❌ No |
| Real-time state sync | ❌ No | ✅ Yes |
| Bill cancel handling | ❌ Manual | ✅ Auto |
| Override for 'replaced' | ⚠️ Complex | ✅ Simple |

---

## 📞 Support

Nếu gặp vấn đề khi upgrade:
1. Check logs: `docker-compose logs -f web`
2. Verify module version: Apps > DTX Serial Extension → Should show "2.1.0"
3. Recompute serials (xem Step 6)
4. Contact dev team với error logs

---

## 🔙 Rollback (If Needed)

Nếu cần rollback về v2.0.1:

```bash
# 1. Restore database backup
docker-compose exec -T db psql -U odoo dtx_dev < backup_before_v2.1.0.sql

# 2. Checkout old version from git (if using version control)
# Or manually restore old module files

# 3. Restart Odoo
docker-compose restart web
```

---

**Enjoy the fully automatic vendor invoice state tracking! 🎉**
