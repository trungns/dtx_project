# 🔍 DEBUG: Tại sao Resupply button vẫn không xuất hiện?

**Ngày:** 2025-12-29
**Status:** Troubleshooting

---

## ✅ ĐÃ LÀM

1. ✅ Verified Manufacturing module installed
2. ✅ Verified mrp_subcontracting module installed
3. ✅ Fixed BOM subcontractor relationship in database
4. ✅ Verified BOM type = 'subcontract'
5. ✅ Restarted Odoo container
6. ✅ Verified fix persists after restart

**Database confirms:**
```
bom_id | product              | type        | subcontractor | components
-------|----------------------|-------------|---------------|------------
1      | Kiosk lấy số DTX-A17 | subcontract | LGMEC         | 3
```

---

## 🔍 NEXT DEBUGGING STEPS

### Step 1: Enable Developer Mode

**Navigation:** `Settings > Activate the developer mode`

Hoặc thêm `?debug=1` vào URL:
```
http://localhost:8069/web?debug=1
```

---

### Step 2: Check BOM in Developer Mode

**Navigation:** `Manufacturing > Products > Bills of Materials`

**Click:** `Kiosk lấy số DTX-A17` BOM

**Kiểm tra các field sau (trong developer mode sẽ thấy technical fields):**

| Field | Expected Value | Check |
|-------|----------------|-------|
| **Type** | Subcontract | ☐ |
| **Subcontractors** | LGMEC | ☐ |
| **Product** | Kiosk lấy số DTX-A17 | ☐ |
| **Product Variant** | Kiosk lấy số DTX-A17 (ID: X) | ☐ |
| **Components** | 5 lines | ☐ |

**Screenshot này và gửi cho tôi nếu cần.**

---

### Step 3: Create PO with Debug Info

**Sau khi bật Developer Mode, tạo PO mới:**

1. `Purchase > Orders > Create`
2. Vendor: **LGMEC**
3. Order Line:
   - Product: **Kiosk lấy số DTX-A17**
   - Quantity: **3**
   - Unit Price: **2,000,000**
4. **Save** (đừng confirm ngay)

**Click vào tab "Other Info"** (hoặc "Thông tin khác")

**Kiểm tra field:**
- **Picking Type:** Nên là "Receipts" hoặc "WH: Receipts"

**Bây giờ click "Confirm Order"**

---

### Step 4: Check Purchase Order Details (Developer Mode)

**Sau khi Confirm, click vào menu Debug (bug icon) ở góc phải:**

**View Metadata > Technical Information:**

Check:
- `id`: Purchase Order ID
- `state`: 'purchase' (confirmed)

**Click vào tab "Other Info" hoặc debug menu > View Fields:**

Tìm field `picking_ids` - Nên thấy **2 IDs** (Resupply + Receipt)

Nếu chỉ thấy **1 ID** → BOM không được trigger

---

### Step 5: SQL Debug - Check Purchase Order

**Thay `XX` bằng PO ID của bạn:**

```bash
docker-compose exec -T db psql -U odoo -d dtx_dev -c "
SELECT
    po.id,
    po.name,
    po.state,
    pol.product_id,
    pp.product_tmpl_id,
    pt.name->>'en_US' as product_name,
    (SELECT COUNT(*) FROM stock_picking WHERE purchase_id = po.id) as picking_count,
    (SELECT string_agg(sp.picking_type_code || ':' || sp.name, ' | ')
     FROM stock_picking sp
     WHERE sp.purchase_id = po.id) as pickings
FROM purchase_order po
JOIN purchase_order_line pol ON pol.order_id = po.id
JOIN product_product pp ON pol.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE po.id = XX;
"
```

**Expected:**
```
id | name     | state    | product_id | product_tmpl_id | product_name         | picking_count | pickings
---|----------|----------|------------|-----------------|----------------------|---------------|------------------
XX | PO/00XXX | purchase | YY         | ZZ              | Kiosk lấy số DTX-A17 | 2             | outgoing:WH/OUT/XXX | incoming:WH/IN/XXX
```

**Nếu `picking_count = 1` và chỉ có `incoming`:**
→ Subcontracting không được trigger

---

### Step 6: Check if BOM is linked to Product Variant

**Vấn đề có thể là BOM link với Product Template nhưng PO dùng Product Variant!**

```bash
docker-compose exec -T db psql -U odoo -d dtx_dev -c "
-- Check BOM product linkage
SELECT
    mb.id as bom_id,
    mb.product_tmpl_id,
    pt.name->>'en_US' as template_name,
    mb.product_id as bom_product_variant_id,
    (SELECT COUNT(*) FROM product_product WHERE product_tmpl_id = mb.product_tmpl_id) as variant_count
FROM mrp_bom mb
JOIN product_template pt ON mb.product_tmpl_id = pt.id
WHERE mb.id = 1;
"
```

**Expected:**
```
bom_id | product_tmpl_id | template_name        | bom_product_variant_id | variant_count
-------|-----------------|----------------------|------------------------|---------------
1      | X               | Kiosk lấy số DTX-A17 | NULL or Y              | 1
```

**Nếu `bom_product_variant_id = NULL` và `variant_count > 1`:**
→ BOM không biết link với variant nào!

**Fix:**
```sql
UPDATE mrp_bom
SET product_id = (
    SELECT id FROM product_product
    WHERE product_tmpl_id = (SELECT product_tmpl_id FROM mrp_bom WHERE id = 1)
    LIMIT 1
)
WHERE id = 1;
```

---

### Step 7: Check Odoo Logs

**Xem logs khi tạo PO:**

```bash
docker-compose logs -f odoo --tail=100
```

**Tìm keyword:**
- `subcontract`
- `resupply`
- `mrp.bom`

**Nếu thấy error hoặc warning liên quan đến BOM → Copy và gửi cho tôi**

---

### Step 8: Manual Trigger (Last Resort)

**Nếu tất cả đều đúng nhưng vẫn không work, có thể trigger manually qua Python:**

```bash
docker-compose exec -T odoo python3 << 'EOF'
import odoo
from odoo.api import Environment

# Connect
registry = odoo.registry('dtx_dev')
with registry.cursor() as cr:
    env = Environment(cr, 1, {})  # uid=1 (admin)

    # Find the PO (replace XX with your PO ID)
    po = env['purchase.order'].browse(XX)

    print(f"PO: {po.name}")
    print(f"Partner: {po.partner_id.name}")
    print(f"State: {po.state}")

    # Check order lines
    for line in po.order_line:
        print(f"\nProduct: {line.product_id.name}")
        print(f"Product Template ID: {line.product_id.product_tmpl_id.id}")

        # Find BOM
        bom = env['mrp.bom']._bom_find(
            product=line.product_id,
            company_id=po.company_id.id,
            bom_type='subcontract'
        )

        print(f"Found BOM: {bom.id if bom else 'NONE'}")
        if bom:
            print(f"BOM Type: {bom.type}")
            print(f"Subcontractors: {[s.name for s in bom.subcontractor_ids]}")

    # Check pickings
    print(f"\nPickings: {len(po.picking_ids)}")
    for pick in po.picking_ids:
        print(f"  - {pick.name}: {pick.picking_type_code}")

    cr.commit()
EOF
```

**Output sẽ cho biết:**
- BOM có được tìm thấy không
- Picking nào được tạo
- Tại sao Resupply không xuất hiện

---

## 🎯 CHECKLIST

Hãy làm theo thứ tự và đánh dấu:

- [ ] Step 1: Enable Developer Mode
- [ ] Step 2: Verify BOM in UI (with developer mode)
- [ ] Step 3: Create new PO and check fields
- [ ] Step 4: Check PO metadata/fields
- [ ] Step 5: Run SQL to check picking_count
- [ ] Step 6: Verify BOM product variant linkage
- [ ] Step 7: Check Odoo logs for errors
- [ ] Step 8: Run Python debug script

**Sau mỗi step, gửi kết quả cho tôi để tôi phân tích!**

---

## 📝 REPORT TEMPLATE

**Hãy điền thông tin sau:**

### PO Information
- PO Number: `___________`
- PO ID: `___________`
- Vendor: `___________`
- Product: `___________`
- State: `___________`

### Smart Buttons Visible
- [ ] Receipt
- [ ] Resupply

### SQL Check Results
```
picking_count: ___________
picking_types: ___________
```

### BOM Verification (Developer Mode)
- BOM Type: `___________`
- Subcontractor: `___________`
- Product Variant ID: `___________`

### Logs (paste any errors here)
```
[paste logs here]
```

---

**Created:** 2025-12-29 15:41
**Status:** Ready for debugging
