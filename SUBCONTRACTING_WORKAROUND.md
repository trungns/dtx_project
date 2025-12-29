# 🔧 ODOO 16 SUBCONTRACTING WORKAROUND

**Ngày:** 2025-12-29
**Vấn đề:** Odoo 16 Community không tự động tạo Resupply picking cho subcontracting PO
**Status:** Cần workaround manual

---

## ❌ VẤN ĐỀ

### Mọi thứ đã config đúng:

✅ **BOM Configuration:**
```sql
bom_id: 1
type: subcontract
product_id: 9 (Kiosk)
subcontractor: LGMEC
components: 3 (Touch Screen, Printer, Mini PC)
```

✅ **Stock Availability:**
```
Touch Screen 17":     1.00 ✓
Thermal Printer:      1.00 ✓
Mini PC Intel i5:     1.00 ✓
```

✅ **Purchase Order:**
```
PO: P00024
Vendor: LGMEC
Product: Kiosk (ID: 9)
Quantity: 1
State: purchase (confirmed)
```

✅ **Modules Installed:**
```
mrp: installed
mrp_subcontracting: installed
mrp_subcontracting_purchase: installed (loaded)
```

---

### Nhưng Resupply picking KHÔNG được tạo tự động!

**Expected behavior:**
- Khi confirm PO → Tạo 2 pickings:
  - Incoming (Receipt): Nhận Kiosk từ LGMEC
  - Outgoing (Resupply): Gửi components cho LGMEC

**Actual behavior:**
- Chỉ tạo 1 picking: Incoming (Receipt)
- Không có Resupply picking
- `subcontracting_resupply_picking_count = 0`

---

## 🔍 ROOT CAUSE

### Investigation Results:

1. **BOM Find:** ✓ Works correctly
   ```python
   bom = env['mrp.bom']._bom_find(product, bom_type='subcontract')
   # Returns: BOM(1) with type='subcontract', subcontractor=LGMEC
   ```

2. **Partner Check:** ✓ Matches
   ```python
   po.partner_id in bom.subcontractor_ids  # True
   ```

3. **Stock Check:** ✓ Available
   ```python
   # All components have qty >= 1.00
   ```

4. **Picking Creation:** ✗ Only creates incoming
   ```python
   po._create_picking()  # Only creates WH/IN/XXXXX
   # Does NOT create WH/OUT/XXXXX
   ```

### Possible Causes:

1. **Odoo 16 Community Limitation:**
   - Subcontracting resupply may require Odoo Enterprise
   - Or specific module configuration not documented

2. **Missing Trigger:**
   - `_create_picking()` doesn't check for subcontracting
   - May need separate method call after PO confirm

3. **Module Hook Missing:**
   - `mrp_subcontracting_purchase` may not be hooking into `button_confirm` properly

---

## ✅ WORKAROUND: Manual Resupply Creation

### Script để tạo Resupply picking manually:

```bash
cd /Users/trungns/dtx_project/odoo-dev
docker-compose exec -T odoo python3 << 'EOF'
import odoo
from odoo.api import Environment

registry = odoo.registry('dtx_dev')
with registry.cursor() as cr:
    env = Environment(cr, 1, {})

    # Get PO (thay 24 bằng PO ID của bạn)
    po_id = 24
    po = env['purchase.order'].browse(po_id)

    if po.state != 'purchase':
        print(f"Error: PO {po.name} must be confirmed first!")
        exit(1)

    # Get product and BOM
    product = po.order_line[0].product_id
    bom_dict = env['mrp.bom']._bom_find(
        product,
        company_id=po.company_id.id,
        bom_type='subcontract'
    )

    if product not in bom_dict:
        print(f"Error: No subcontracting BOM found for {product.name}")
        exit(1)

    bom = bom_dict[product]

    # Check if resupply already exists
    existing_resupply = po.picking_ids.filtered(
        lambda p: p.picking_type_id.code == 'outgoing'
    )

    if existing_resupply:
        print(f"Resupply picking already exists: {existing_resupply.name}")
        exit(0)

    print(f"Creating Resupply picking for PO {po.name}...")

    # Get outgoing picking type
    picking_type = env['stock.picking.type'].search([
        ('code', '=', 'outgoing'),
        ('warehouse_id.company_id', '=', po.company_id.id)
    ], limit=1)

    if not picking_type:
        print("Error: No outgoing picking type found!")
        exit(1)

    # Use supplier location
    supplier_loc = env.ref('stock.stock_location_suppliers')

    # Create Resupply picking
    picking_vals = {
        'partner_id': po.partner_id.id,
        'picking_type_id': picking_type.id,
        'location_id': picking_type.default_location_src_id.id,
        'location_dest_id': supplier_loc.id,
        'origin': po.name,
    }

    resupply_picking = env['stock.picking'].create(picking_vals)

    # Link to PO
    po.write({'picking_ids': [(4, resupply_picking.id)]})

    # Create stock moves for each BOM component
    for bom_line in bom.bom_line_ids:
        qty = bom_line.product_qty * po.order_line[0].product_qty

        env['stock.move'].create({
            'name': bom_line.product_id.name,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': qty,
            'product_uom': bom_line.product_uom_id.id,
            'picking_id': resupply_picking.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': supplier_loc.id,
        })

    # Confirm and assign
    resupply_picking.action_confirm()
    resupply_picking.action_assign()

    print(f"\n✅ Created Resupply picking: {resupply_picking.name}")
    print(f"   Components to send: {len(bom.bom_line_ids)}")

    # Verify
    po._compute_picking_ids()
    print(f"\nPO {po.name} now has {len(po.picking_ids)} pickings:")
    for pick in po.picking_ids:
        print(f"  - {pick.name}: {pick.picking_type_id.name}")

    cr.commit()
    print("\n✅ Done! Refresh browser to see updated PO.")
EOF
```

### Cách sử dụng:

1. **Tạo PO bình thường:**
   - Vendor: LGMEC
   - Product: Kiosk lấy số DTX-A17
   - Quantity: 1
   - Confirm Order

2. **Lấy PO ID** từ URL hoặc PO number

3. **Chạy script trên**, thay `po_id = 24` bằng PO ID của bạn

4. **Refresh browser**

5. **Kiểm tra PO:** Giờ sẽ thấy 2 operations:
   - Trong button "Phiếu nhập kho" sẽ có 2 dòng:
     - WH/IN/XXXXX (Receipt - Nhận Kiosk)
     - WH/OUT/XXXXX (Resupply - Gửi components)

---

## 📋 WORKFLOW SAU KHI TẠO RESUPPLY

### Bước 1: Xử lý Resupply (Gửi components)

**Click vào PO → Click button "Phiếu nhập kho" (hoặc "Receipt")**

**Sẽ thấy 2 dòng:**
- WH/IN/XXXXX: Receipt (đừng làm gì với cái này trước)
- **WH/OUT/XXXXX: Resupply** ← Click vào đây

**Trong WH/OUT/XXXXX:**
1. Tab "Operations"
2. Click "Check Availability" (nếu stock đủ)
3. Với mỗi component, nhập Serial Number:
   - Touch Screen: Chọn từ available serials
   - Thermal Printer: Chọn từ available serials
   - Mini PC: Chọn từ available serials
4. Click "Validate"

**Kết quả:**
- 3 components chuyển từ WH/Stock → Partners/Vendors
- Status: Done ✓

---

### Bước 2: Nhận Kiosk (Receipt)

**Quay lại PO → Click button "Phiếu nhập kho"**

**Click vào WH/IN/XXXXX (Receipt):**

1. Tab "Operations"
2. Nhập Serial Number cho Kiosk:
   - Lot/Serial Number: `KIOSK-A17-001`
   - Quantity: 1
3. Click "Validate"

**Kết quả:**
- 1 Kiosk nhận vào WH/Stock
- On Hand = 1 Unit
- Serial: KIOSK-A17-001
- Status: Done ✓

---

## 🎯 TRACEABILITY

**Sau khi hoàn thành, kiểm tra traceability:**

### Check 1: Product Moves

**Navigation:** `Inventory > Products > Products`

**Mở:** Kiosk lấy số DTX-A17

**Tab:** Traceability (hoặc click vào On Hand)

**Expected:**
- Serial KIOSK-A17-001
- Source: Partners/Vendors (LGMEC)
- Destination: WH/Stock

---

### Check 2: Component Consumption

**Mở từng component (Touch Screen, Printer, Mini PC)**

**Check stock moves:**
- On Hand giảm đi 1
- Serial đã chuyển → Partners/Vendors (LGMEC)

---

## 📝 LIMITATIONS

### Với workaround này:

✅ **Works:**
- Gửi components cho subcontractor
- Nhận finished products
- Traceability đầy đủ
- Serial tracking hoạt động

✗ **Không tự động:**
- Phải chạy script manually sau khi tạo PO
- Không có smart button "Resupply" riêng biệt
- Cả 2 pickings hiển thị trong cùng button "Phiếu nhập kho"

---

## 🔄 FUTURE IMPROVEMENTS

### Option 1: Tạo custom module

Tạo module DTX Subcontracting Auto-create:

```python
# models/purchase_order.py
from odoo import models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super().button_confirm()

        # Auto-create resupply for subcontracting
        for order in self:
            for line in order.order_line:
                bom_dict = self.env['mrp.bom']._bom_find(
                    line.product_id,
                    company_id=order.company_id.id,
                    bom_type='subcontract'
                )

                if line.product_id in bom_dict:
                    bom = bom_dict[line.product_id]
                    if order.partner_id in bom.subcontractor_ids:
                        self._create_resupply_picking(order, bom, line)

        return res

    def _create_resupply_picking(self, order, bom, line):
        # Implementation here...
        pass
```

---

### Option 2: Check Odoo Enterprise

Subcontracting full features có thể chỉ có trong Odoo Enterprise.

**Để verify:**
- Test trên Odoo.sh (trial)
- Hoặc check official docs

---

## ✅ RECOMMENDED WORKFLOW

**Cho production, khuyến nghị:**

1. Tạo script automation (như trên)
2. Chạy script ngay sau khi confirm PO subcontracting
3. Hoặc tạo button custom trong UI để trigger script
4. Train user để nhận biết khi nào cần chạy script

**Hoặc:**

1. Nâng cấp lên Odoo Enterprise (nếu budget cho phép)
2. Verify subcontracting works out-of-box

---

**Created:** 2025-12-29
**Author:** Claude (DTX Project Assistant)
**Status:** Workaround ready, tested với PO 24
