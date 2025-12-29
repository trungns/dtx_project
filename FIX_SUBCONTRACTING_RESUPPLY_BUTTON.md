# 🔧 FIX: Nút "Resupply" không xuất hiện trong Purchase Order

**Ngày:** 2025-12-29
**Vấn đề:** Khi tạo PO cho sản phẩm Kiosk với vendor LGMEC, chỉ thấy nút "Receipt" mà không có nút "Resupply"

---

## ❌ TRIỆU CHỨNG

**Bạn đã làm đúng:**
- ✓ Tạo BOM cho Kiosk DTX-A17
- ✓ Chọn Subcontractor = LGMEC trong BOM form
- ✓ BOM có 5 component lines
- ✓ Tạo PO với Vendor = LGMEC, Product = Kiosk
- ✓ Confirm PO

**Nhưng:**
- ✗ Chỉ thấy smart button "Receipt"
- ✗ Không thấy smart button "Resupply"
- ✗ Không thể gửi linh kiện cho LGMEC

---

## 🔍 NGUYÊN NHÂN

### Phát hiện

**BOM Configuration:**
```
BOM Type: subcontract ✓ (Đúng)
Subcontractor Field: LGMEC (Hiển thị trên form) ✓
```

**Database Reality:**
```sql
SELECT * FROM mrp_bom_subcontractor WHERE mrp_bom_id = 1;
-- Result: (0 rows) ✗ EMPTY!
```

### Root Cause

**Odoo UI bug hoặc workflow issue:**

Khi bạn chọn Subcontractor trong BOM form và click Save:
- UI hiển thị "LGMEC" ✓
- Field `type` được set = `'subcontract'` ✓
- **NHƯNG:** Relationship không được ghi vào bảng `mrp_bom_subcontractor` ✗

**Kết quả:**
- Odoo không nhận diện BOM này là subcontracting
- Purchase Order không tạo Resupply button
- Workflow bị block

---

## ✅ GIẢI PHÁP (ĐÃ FIX)

### Fix Manual qua Database

Tôi đã chạy SQL để fix:

```sql
INSERT INTO mrp_bom_subcontractor (mrp_bom_id, res_partner_id)
VALUES (1, 8);  -- BOM ID = 1, LGMEC Partner ID = 8
```

**Verification:**
```sql
SELECT
    mb.id as bom_id,
    pt.name->>'en_US' as product,
    mb.type,
    rp.name as subcontractor
FROM mrp_bom mb
JOIN product_template pt ON mb.product_tmpl_id = pt.id
LEFT JOIN mrp_bom_subcontractor mbs ON mbs.mrp_bom_id = mb.id
LEFT JOIN res_partner rp ON mbs.res_partner_id = rp.id
WHERE mb.id = 1;
```

**Result:**
```
bom_id |       product        |    type     | subcontractor
--------+----------------------+-------------+---------------
      1 | Kiosk lấy số DTX-A17 | subcontract | LGMEC
```

✅ **Fixed!**

---

## 🧪 KIỂM TRA SAU KHI FIX

### Bước 1: Xóa PO cũ

**Navigation:** `Purchase > Orders`

**Tìm:** PO với Product = Kiosk lấy số DTX-A17, Vendor = LGMEC

**Action:** Cancel → Delete (hoặc để đó cũng được)

---

### Bước 2: Tạo PO mới

**Navigation:** `Purchase > Orders > Create`

**Điền:**

| Field | Value |
|-------|-------|
| **Vendor** | LGMEC |
| **Order Lines** | |
| └─ Product | Kiosk lấy số DTX-A17 |
| └─ Quantity | 3 |
| └─ Unit Price | 2,000,000 VND |

**Click:** `Confirm Order`

---

### Bước 3: Kiểm tra Smart Buttons

**Sau khi Confirm, bạn phải thấy 2 smart buttons:**

```
┌─────────────────────────────────────┐
│  PO/00XXX                           │
│  Vendor: LGMEC                      │
│  Total: 6,000,000 VND               │
├─────────────────────────────────────┤
│  [To Receive: 3] [Resupply: 15] ←  │  ← CẢ 2 NÚT
└─────────────────────────────────────┘
```

✅ **Receipt (To Receive):** Nhận 3 Kiosk từ LGMEC
✅ **Resupply:** Gửi 15 linh kiện cho LGMEC

---

### Bước 4: Xử lý Resupply (Gửi linh kiện)

**Click:** Smart button `Resupply`

**Bạn sẽ thấy:**
- 1 Delivery Order từ `WH/Stock` → `LGMEC`
- 15 lines (5 component types × 3 qty)

**Thao tác:**

1. **Check Availability** (nếu đã có stock)
2. **Validate** → Nhập 15 serial numbers
3. **Done** ✓

**Kết quả:**
- 15 linh kiện được chuyển từ `WH/Stock` → `Partner Locations/LGMEC`

---

### Bước 5: Nhận Kiosk (Receipt)

**Sau khi Resupply done, quay lại PO:**

**Click:** Smart button `Receipt` (To Receive)

**Bạn sẽ thấy:**
- 1 Receipt từ `LGMEC` → `WH/Stock`
- 3 lines (Kiosk lấy số DTX-A17 × 3)

**Thao tác:**

1. **Validate** → Nhập 3 serial numbers cho Kiosk
   - `KIOSK-A17-001`
   - `KIOSK-A17-002`
   - `KIOSK-A17-003`
2. **Done** ✓

**Kết quả:**
- 3 Kiosk được nhận vào `WH/Stock`
- On Hand = 3

---

## 🎯 EXPECTED BEHAVIOR

### Workflow đúng

```
┌──────────────────────────────────────────────────────────┐
│  PHASE 1: CREATE PURCHASE ORDER                          │
│  ─────────────────────────────────────────────────────   │
│  ✓ Create PO: Vendor=LGMEC, Product=Kiosk, Qty=3         │
│  ✓ Confirm Order                                         │
│  ✓ 2 Smart buttons appear: Receipt + Resupply           │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  PHASE 2: RESUPPLY (Gửi linh kiện)                       │
│  ─────────────────────────────────────────────────────   │
│  ✓ Click Resupply button                                │
│  ✓ Delivery Order: WH/Stock → LGMEC                      │
│  ✓ 15 lines (Touch×3, Printer×3, PC×3, Cam×3, CCCD×3)   │
│  ✓ Check Availability → Validate → Enter serials        │
│  ✓ 15 components moved to LGMEC location                │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  PHASE 3: RECEIPT (Nhận Kiosk)                           │
│  ─────────────────────────────────────────────────────   │
│  ✓ Click Receipt button                                 │
│  ✓ Receipt: LGMEC → WH/Stock                             │
│  ✓ 3 lines (Kiosk × 3)                                   │
│  ✓ Validate → Enter 3 Kiosk serials                     │
│  ✓ 3 Kiosks received in stock                           │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  RESULT: SUBCONTRACTING COMPLETE                         │
│  ✓ 15 components → LGMEC (tracked by serial)            │
│  ✓ 3 Kiosks ← LGMEC (tracked by serial)                 │
│  ✓ Full traceability maintained                         │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 NẾU VẪN KHÔNG THẤY RESUPPLY BUTTON

### Check 1: BOM Subcontractor trong database

```bash
docker-compose exec -T db psql -U odoo -d dtx_dev -c "
SELECT
    mb.id,
    pt.name->>'en_US' as product,
    mb.type,
    rp.name as subcontractor
FROM mrp_bom mb
JOIN product_template pt ON mb.product_tmpl_id = pt.id
LEFT JOIN mrp_bom_subcontractor mbs ON mbs.mrp_bom_id = mb.id
LEFT JOIN res_partner rp ON mbs.res_partner_id = rp.id
WHERE pt.name->>'en_US' LIKE '%Kiosk%';
"
```

**Expected:**
```
id |       product        |    type     | subcontractor
----+----------------------+-------------+---------------
 1 | Kiosk lấy số DTX-A17 | subcontract | LGMEC
```

**Nếu `subcontractor = NULL`:**

→ Chạy lại fix:
```sql
INSERT INTO mrp_bom_subcontractor (mrp_bom_id, res_partner_id)
VALUES (1, 8)
ON CONFLICT DO NOTHING;
```

---

### Check 2: Manufacturing module

```bash
docker-compose exec -T db psql -U odoo -d dtx_dev -c "
SELECT name, state FROM ir_module_module
WHERE name IN ('mrp', 'mrp_subcontracting');
"
```

**Expected:**
```
       name        |   state
-------------------+-----------
 mrp               | installed
 mrp_subcontracting| installed
```

**Nếu không installed:**

→ Install via Odoo UI: `Apps > Search "Manufacturing" > Install`

---

### Check 3: PO Product & Vendor

**PO phải match BOM:**

| BOM | PO Requirement |
|-----|----------------|
| Product Template = Kiosk DTX-A17 | PO Product = Kiosk lấy số DTX-A17 ✓ |
| Subcontractor = LGMEC | PO Vendor = LGMEC ✓ |

**Nếu không match:**
- Resupply button sẽ KHÔNG xuất hiện
- Chỉ có Receipt button (normal purchase)

---

### Check 4: PO State

**Resupply button chỉ xuất hiện khi:**
- PO State = `purchase` (Confirmed)
- Không xuất hiện khi State = `draft` hoặc `sent`

**Fix:** Click `Confirm Order` button

---

## 📊 DEBUGGING COMMANDS

### Check BOM configuration

```bash
docker-compose exec -T db psql -U odoo -d dtx_dev -c "
SELECT
    mb.id as bom_id,
    pt.name->>'en_US' as product,
    mb.type,
    mb.product_tmpl_id,
    (SELECT COUNT(*) FROM mrp_bom_line WHERE bom_id = mb.id) as component_count,
    (SELECT COUNT(*) FROM mrp_bom_subcontractor WHERE mrp_bom_id = mb.id) as subcontractor_count
FROM mrp_bom mb
JOIN product_template pt ON mb.product_tmpl_id = pt.id;
"
```

**Expected for Kiosk BOM:**
```
bom_id | product              | type        | component_count | subcontractor_count
-------|----------------------|-------------|-----------------|--------------------
1      | Kiosk lấy số DTX-A17 | subcontract | 5               | 1
```

---

### Check PO and pickings

```bash
docker-compose exec -T db psql -U odoo -d dtx_dev -c "
SELECT
    po.id as po_id,
    po.name as po_number,
    po.state,
    rp.name as vendor,
    pt.name->>'en_US' as product,
    (SELECT COUNT(*) FROM stock_picking WHERE purchase_id = po.id) as picking_count,
    (SELECT string_agg(sp.picking_type_code, ',')
     FROM stock_picking sp
     WHERE sp.purchase_id = po.id) as picking_types
FROM purchase_order po
JOIN res_partner rp ON po.partner_id = rp.id
JOIN purchase_order_line pol ON pol.order_id = po.id
JOIN product_product pp ON pol.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE pt.name->>'en_US' LIKE '%Kiosk%';
"
```

**Expected after creating PO:**
```
po_id | po_number | state    | vendor | product              | picking_count | picking_types
------|-----------|----------|--------|----------------------|---------------|---------------
XX    | PO/00XXX  | purchase | LGMEC  | Kiosk lấy số DTX-A17 | 2             | outgoing,incoming
```

- `outgoing` = Resupply (gửi linh kiện)
- `incoming` = Receipt (nhận Kiosk)

**Nếu `picking_count = 1` và `picking_types = incoming`:**
→ BOM subcontractor không được config đúng

---

## 🎓 TECHNICAL NOTES

### Odoo Subcontracting Architecture

**Tables involved:**

1. **`mrp_bom`**: Bill of Materials
   - `id`: BOM ID
   - `type`: `'normal'` hoặc `'subcontract'`
   - `product_tmpl_id`: Finished product

2. **`mrp_bom_subcontractor`**: Many-to-many relationship
   - `mrp_bom_id`: FK to `mrp_bom.id`
   - `res_partner_id`: FK to `res_partner.id` (vendor)

3. **`purchase_order`**: Purchase Order
   - Odoo checks: `product_id.bom_ids` filtered by `type='subcontract'`
   - If match found: Creates 2 pickings (Resupply + Receipt)
   - If no match: Creates 1 picking (Receipt only)

### Why UI didn't save relationship?

**Possible causes:**

1. **Form save issue:** One2many/Many2many field không trigger save event
2. **Access rights:** User không có quyền write vào `mrp_bom_subcontractor`
3. **Constraint violation:** (Unlikely, no unique constraints)
4. **Odoo bug:** Known issue trong Odoo 16 Community?

**Workaround:** Direct SQL insert (như đã làm)

---

## ✅ STATUS

**Fixed on:** 2025-12-29 15:37 (Vietnam Time)

**Method:** Direct SQL insert into `mrp_bom_subcontractor` table

**Verification:** ✓ BOM now shows LGMEC in subcontractor relationship

**Next step:** User cần test lại PO workflow

---

## 📞 NEXT STEPS FOR USER

1. ✅ Xóa PO cũ (nếu có)
2. ✅ Tạo PO mới: Vendor=LGMEC, Product=Kiosk, Qty=3, Price=2M
3. ✅ Confirm Order
4. ✅ Kiểm tra 2 smart buttons: Receipt + Resupply
5. ✅ Click Resupply → Gửi 15 linh kiện
6. ✅ Click Receipt → Nhận 3 Kiosk
7. ✅ Tiếp tục test flow từ Phase 5 (Sales)

---

**Created:** 2025-12-29
**Author:** Claude (DTX Project Assistant)
**Status:** ✅ Fixed & Ready for testing
