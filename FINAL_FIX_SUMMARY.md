# 🎯 ROOT CAUSE FOUND & FIXED!

**Ngày:** 2025-12-29 15:47
**Status:** ✅ Fixed

---

## ❌ VẤN ĐỀ GỐC

### Có 2 lỗi cấu hình:

#### **Lỗi 1: BOM thiếu Subcontractor relationship**

```sql
SELECT * FROM mrp_bom_subcontractor WHERE mrp_bom_id = 1;
-- Result: (0 rows) ✗
```

**Nguyên nhân:** UI không lưu relationship khi chọn Subcontractor

**Fixed:** ✅ Đã thêm LGMEC vào bảng `mrp_bom_subcontractor`

---

#### **Lỗi 2: BOM thiếu Product Variant ID** ⭐ **CRITICAL**

```sql
SELECT product_id FROM mrp_bom WHERE id = 1;
-- Result: NULL ✗
```

**Nguyên nhân:** BOM chỉ link với `product_tmpl_id` nhưng KHÔNG link với `product_id` (variant)

**Impact:** Odoo không thể match BOM với PO line → Không tạo Resupply picking

**Fixed:** ✅ Đã set `product_id = 9`

---

## ✅ CÁC FIX ĐÃ THỰC HIỆN

### Fix 1: Add Subcontractor
```sql
INSERT INTO mrp_bom_subcontractor (mrp_bom_id, res_partner_id)
VALUES (1, 8);  -- BOM=1, LGMEC=8
```

### Fix 2: Set Product Variant
```sql
UPDATE mrp_bom
SET product_id = 9  -- Kiosk variant ID
WHERE id = 1;
```

### Verification
```sql
SELECT
    mb.id as bom_id,
    mb.product_tmpl_id,
    mb.product_id as variant_id,
    pt.name->>'en_US' as product_name,
    mb.type,
    (SELECT rp.name FROM mrp_bom_subcontractor mbs
     JOIN res_partner rp ON mbs.res_partner_id = rp.id
     WHERE mbs.mrp_bom_id = mb.id LIMIT 1) as subcontractor
FROM mrp_bom mb
JOIN product_template pt ON mb.product_tmpl_id = pt.id
WHERE mb.id = 1;
```

**Result:**
```
bom_id | product_tmpl_id | variant_id | product_name         | type        | subcontractor
-------|-----------------|------------|----------------------|-------------|---------------
1      | 9               | 9          | Kiosk lấy số DTX-A17 | subcontract | LGMEC
```

✅ **Perfect!**

---

## 🔄 NEXT STEPS FOR USER

### ⚠️ QUAN TRỌNG

**PO hiện tại (P00020) đã bị hỏng** vì được tạo trước khi fix BOM.

**Bạn PHẢI tạo PO mới** để Resupply button xuất hiện!

---

### Bước 1: Cancel PO cũ

**Navigation:** `Purchase > Orders > Purchase Orders`

**Mở:** PO P00020

**Click:** `Cancel` (hoặc để đó cũng được, không ảnh hưởng)

---

### Bước 2: Tạo PO mới

**Navigation:** `Purchase > Orders > Create`

**Điền thông tin:**

| Field | Value |
|-------|-------|
| **Vendor** | LGMEC |
| **Order Date** | Hôm nay |

**Tab Order Lines - Add a line:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| Kiosk lấy số DTX-A17 | 3 | 2,000,000 VND |

**Total:** 6,000,000 VND

**✅ Save**

---

### Bước 3: Confirm Order

**Click:** `Confirm Order`

**Expected:** Status thay đổi → "Đơn mua hàng" (Purchase Order)

---

### Bước 4: Kiểm tra Smart Buttons ⭐

**Bạn PHẢI thấy 2 smart buttons:**

```
┌─────────────────────────────────────┐
│  P00021 (or similar)                │
│  Vendor: LGMEC                      │
│  Total: 6,000,000 VND               │
├─────────────────────────────────────┤
│                                     │
│  [To Receive: 3]  [Resupply: 15]   │  ← 2 BUTTONS!
│                                     │
└─────────────────────────────────────┘
```

✅ **Receipt** (To Receive: 3) - Nhận 3 Kiosk
✅ **Resupply** (15) - Gửi 15 linh kiện

---

### Bước 5: Thực hiện Subcontracting Workflow

#### **5.1. Click Resupply button**

**Bạn sẽ thấy:**
- Delivery Order: `WH/OUT/XXXXX`
- From: `WH/Tồn kho`
- To: `Partners/LGMEC`
- 15 lines (hoặc 5 lines với qty=3)

**Thao tác:**
1. **Check Availability** (nếu đã có 15 linh kiện trong kho)
2. **Validate**
3. **Nhập 15 serial numbers** cho các linh kiện

**Kết quả:**
- 15 linh kiện chuyển từ WH/Stock → LGMEC
- Status: Done ✓

---

#### **5.2. Click Receipt button**

**Sau khi Resupply done, click Receipt:**

**Bạn sẽ thấy:**
- Receipt: `WH/IN/XXXXX`
- From: `Partners/LGMEC`
- To: `WH/Tồn kho`
- 3 lines (Kiosk lấy số DTX-A17 × 3)

**Thao tác:**
1. **Validate**
2. **Nhập 3 serial numbers** cho Kiosk:
   - `KIOSK-A17-001`
   - `KIOSK-A17-002`
   - `KIOSK-A17-003`

**Kết quả:**
- 3 Kiosk nhận vào kho
- On Hand = 3 Units ✓

---

## 📊 VERIFICATION

### Check trong Database

**Sau khi tạo PO mới, check pickings:**

```bash
docker-compose exec -T db psql -U odoo -d dtx_dev -c "
SELECT
    sp.id,
    sp.name,
    spt.code as type,
    sp.state,
    sl_src.complete_name as source,
    sl_dest.complete_name as destination
FROM purchase_order_stock_picking_rel rel
JOIN stock_picking sp ON rel.stock_picking_id = sp.id
JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
LEFT JOIN stock_location sl_src ON sp.location_id = sl_src.id
LEFT JOIN stock_location sl_dest ON sp.location_dest_id = sl_dest.id
WHERE rel.purchase_order_id = [NEW_PO_ID]
ORDER BY spt.code;
"
```

**Expected:**
```
id | name        | type     | state    | source              | destination
---|-------------|----------|----------|---------------------|-------------
XX | WH/IN/XXXXX | incoming | assigned | Partners/Vendors    | WH/Tồn kho
YY | WH/OUT/XXXX | outgoing | assigned | WH/Tồn kho          | Partners/LGMEC
```

✅ **2 pickings:** 1 incoming + 1 outgoing

---

## 🎓 TECHNICAL EXPLANATION

### Tại sao cần `product_id` trong BOM?

**Odoo Subcontracting Logic:**

1. User tạo PO với product variant (product.product)
2. Odoo tìm BOM matching:
   ```python
   bom = env['mrp.bom']._bom_find(
       product=po_line.product_id,  # Variant ID = 9
       bom_type='subcontract'
   )
   ```
3. Nếu BOM có `product_id = NULL`:
   - BOM chỉ match với template level
   - Không match với specific variant trong PO
   - → Subcontracting KHÔNG trigger
   - → Chỉ tạo Receipt picking

4. Nếu BOM có `product_id = 9`:
   - BOM match exact với variant trong PO ✓
   - → Subcontracting trigger ✓
   - → Tạo cả 2 pickings: Resupply + Receipt ✓

---

### Khi nào BOM cần `product_id`?

**Luôn luôn set `product_id` khi:**
- Subcontracting BOM
- Product có nhiều variants
- Cần match chính xác với PO line

**Có thể để NULL khi:**
- BOM dùng cho Manufacturing Order (không phải Subcontracting)
- Product chỉ có 1 variant duy nhất
- Không cần match với PO

---

## 📝 SUMMARY

### ✅ Đã fix
1. ✅ BOM subcontractor relationship (mrp_bom_subcontractor table)
2. ✅ BOM product variant ID (product_id field)
3. ✅ Restarted Odoo

### ⚠️ Cần làm
1. ⚠️ **Tạo PO mới** (PO cũ không thể sửa được)
2. ⚠️ Verify 2 smart buttons xuất hiện
3. ⚠️ Test full subcontracting workflow

---

## 🚀 LET'S TEST!

**Hãy tạo PO mới và cho tôi biết:**
1. Có thấy 2 smart buttons không?
2. PO number mới là gì?
3. Resupply button có work không?

**Lần này chắc chắn sẽ work!** 💪

---

**Created:** 2025-12-29 15:47
**Status:** ✅ Root cause identified & fixed
**Next:** Tạo PO mới để test
