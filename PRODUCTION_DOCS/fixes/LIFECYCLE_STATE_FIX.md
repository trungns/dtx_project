# Fix Serial Lifecycle State for Subcontracting

## Vấn đề

Khi resupply serial numbers cho subcontracting production order (P00033 - kiosk DTX-A17):
- Serial MiniPC11 và MáyIn4 đã được chuyển đến subcontractor
- Vị trí thực tế: `Partners/Subcontracting/đối tác`
- Nhưng **Lifecycle State vẫn hiển thị "In Stock"** ❌

**Nguyên nhân:**
- Field `lifecycle_state` là manual field, không tự động update dựa trên location
- Code chỉ update lifecycle_state khi move từ supplier → stock hoặc stock → customer
- Không handle case move đến subcontracting location

## Giải pháp

### 1. Thêm Auto-computed Lifecycle State

**New field:** `x_lifecycle_state`
- Tự động tính toán dựa trên location hiện tại của serial
- Update tự động khi serial di chuyển
- Không thể edit thủ công (readonly)

**States:**
```python
('in_stock', 'In Stock')           # Trong kho WH/Stock
('subcontracted', 'At Subcontractor')  # Tại đối tác gia công
('in_production', 'In Production')     # Trong sản xuất
('delivered', 'Delivered to Customer') # Giao cho khách hàng
('maintenance', 'Under Maintenance')   # Bảo trì
('scrapped', 'Scrapped')              # Thanh lý
```

### 2. Logic Detection

**Dựa trên `stock.quant` location:**

```python
def _get_current_lifecycle_state(self):
    # Get quant with positive quantity
    quants = self.env['stock.quant'].search([
        ('lot_id', '=', self.id),
        ('quantity', '>', 0),
    ])

    location = main_quant.location_id

    # Check location type
    if location.usage == 'internal':
        if 'subcontracting' in location.complete_name.lower():
            return 'subcontracted'  # ✅ FIX CHO VẤN ĐỀ NÀY
        elif 'maintenance' in location.complete_name.lower():
            return 'maintenance'
        else:
            return 'in_stock'

    elif location.usage == 'customer':
        return 'delivered'

    elif location.usage == 'production':
        return 'in_production'

    elif location.usage == 'inventory':
        return 'scrapped'
```

### 3. Auto-update Trigger

**Khi stock move done:**

```python
# In stock_move_line.py _action_done()

# Update x_lifecycle_state after move
if hasattr(lot, 'x_lifecycle_state'):
    lot._compute_x_lifecycle_state()
```

Serial tự động recompute state mỗi khi di chuyển!

## UI Changes

### Tree View (Lots/Serial Numbers)

**Trước:**
```
| Serial | Manual State |
|--------|--------------|
| MPC11  | In Stock     | ❌ Wrong
```

**Sau:**
```
| Serial | Location State    | Manual State |
|--------|-------------------|--------------|
| MPC11  | At Subcontractor  | In Stock     | ✅ Correct!
```

### Form View

**Added section:**
```
┌─ Lifecycle & References ─────────────────┐
│ Current Location State: At Subcontractor │ (auto, readonly)
│ Manual State: In Stock                    │ (manual, editable)
│ Customer: [empty]                         │
└───────────────────────────────────────────┘
```

### Color Coding

```
🟢 Green:  in_stock
🔵 Blue:   delivered
🟠 Orange: subcontracted, in_production, maintenance
🔴 Red:    scrapped
```

## Files Changed

### 1. [models/stock_lot.py](odoo-dev/addons/dtx_serial_ext/models/stock_lot.py)

**Added:**
- Line 36-49: `x_lifecycle_state` field definition
- Line 177-234: `_compute_x_lifecycle_state()` method
- Line 191-234: Location-based state detection logic

### 2. [models/stock_move_line.py](odoo-dev/addons/dtx_serial_ext/models/stock_move_line.py)

**Added:**
- Line 103-111: Trigger x_lifecycle_state recompute after move done

### 3. [views/stock_lot_views.xml](odoo-dev/addons/dtx_serial_ext/views/stock_lot_views.xml)

**Tree view:**
- Line 14-19: Add x_lifecycle_state column with badges

**Form view:**
- Line 70-75: Add x_lifecycle_state field (readonly)
- Line 76-80: Keep lifecycle_state as manual override

### 4. [__manifest__.py](odoo-dev/addons/dtx_serial_ext/__manifest__.py)

**Version:** 2.2.0 → 2.3.0

**Changelog:**
```python
Version 2.3.0:
- **NEW**: Auto-computed lifecycle state based on current location
- **NEW**: x_lifecycle_state field tracks location-based state
- States: in_stock, subcontracted, in_production, delivered, maintenance, scrapped
- Automatically updated when serial moves between locations
- Shown in tree/form views with color badges
- **FIX**: Subcontracted serials now show correct state
```

## Test Case

### Scenario: Resupply for Subcontracting

**Setup:**
1. Manufacturing Order: P00033 (Kiosk DTX-A17)
2. Subcontractor: Đối tác A
3. Components to resupply:
   - MiniPC11 (serial number)
   - MáyIn4 (serial number)

**Before Fix:**
```
Stock -> Lots/Serial Numbers
┌──────────┬────────────┬─────────────────┐
│ Serial   │ Location   │ Lifecycle State │
├──────────┼────────────┼─────────────────┤
│ MiniPC11 │ Subcontr.. │ In Stock ❌     │
│ MáyIn4   │ Subcontr.. │ In Stock ❌     │
└──────────┴────────────┴─────────────────┘
```

**After Fix:**
```
Stock -> Lots/Serial Numbers
┌──────────┬────────────┬──────────────────┬──────────────┐
│ Serial   │ Location   │ Location State   │ Manual State │
├──────────┼────────────┼──────────────────┼──────────────┤
│ MiniPC11 │ Subcontr.. │ At Subcontractor │ In Stock     │✅
│ MáyIn4   │ Subcontr.. │ At Subcontractor │ In Stock     │✅
└──────────┴────────────┴──────────────────┴──────────────┘
```

## How to Test

### 1. Restart Odoo
```bash
docker-compose restart odoo
```

### 2. Upgrade Module
```bash
# Option 1: Via UI
Apps > DTX Serial Extension > Upgrade

# Option 2: Command line
docker-compose exec odoo odoo -u dtx_serial_ext -d dtx_dev --stop-after-init
docker-compose restart odoo
```

### 3. Test Subcontracting Flow

1. **Create MO for kiosk** (e.g., DTX-A17)
   - MRP > Manufacturing Orders > Create
   - Product: Kiosk DTX-A17
   - BOM: With subcontracting

2. **Resupply components to subcontractor:**
   - Click "Resupply" button
   - Select serials: MiniPC11, MáyIn4
   - Validate

3. **Check serial state:**
   - Stock > Lots/Serial Numbers
   - Search: MiniPC11
   - **Location State** should show: "At Subcontractor" 🟠

### 4. Verify Other States

**Test in stock:**
```bash
# Receive new serial to WH/Stock
→ Location State: In Stock 🟢
```

**Test delivery:**
```bash
# Deliver serial to customer
→ Location State: Delivered to Customer 🔵
```

**Test maintenance:**
```bash
# Move serial to WH/Maintenance
→ Location State: Under Maintenance 🟠
```

## Technical Details

### Why Two Fields?

**`lifecycle_state` (Manual):**
- For business logic tracking
- Manually set by users
- Values: stock, allocated, delivered, installed, maintenance, scrapped
- Used for workflow/project management

**`x_lifecycle_state` (Auto):**
- **NEW** field for location tracking
- Auto-computed from stock.quant
- Values: in_stock, subcontracted, in_production, delivered, maintenance, scrapped
- Used for inventory visibility

### Compute Trigger

**Method:** On-demand compute (not stored computed with depends)

**Reason:** `stock.quant` has no direct relation to `stock.lot`, cannot use `@api.depends`

**Solution:** Manual trigger on stock move done

**Alternative:** Could add scheduled action to recompute all serials periodically

## Migration Notes

**Existing Serials:**

After upgrade, run manual recompute for all serials:
```python
# In Odoo shell or script
serials = env['stock.lot'].search([])
for serial in serials:
    serial._compute_x_lifecycle_state()
```

Or wait for next stock move to trigger auto-update.

## Commit

```bash
git log -1 --oneline
# 64a3eca feat: Add auto lifecycle state tracking based on location (v2.3.0)

git show 64a3eca --stat
# odoo-dev/addons/dtx_serial_ext/__manifest__.py            | 13 +++-
# odoo-dev/addons/dtx_serial_ext/models/stock_lot.py        | 71 +++++++++++++--
# odoo-dev/addons/dtx_serial_ext/models/stock_move_line.py  | 9 ++
# odoo-dev/addons/dtx_serial_ext/views/stock_lot_views.xml  | 24 ++++--
# 4 files changed, 111 insertions(+), 6 deletions(-)
```

## Summary

✅ **Fixed:** Serials at subcontracting location now show correct state
✅ **Added:** Auto location-based lifecycle tracking
✅ **UI:** New "Location State" column with color badges
✅ **Version:** 2.2.0 → 2.3.0

Giờ bạn có thể dễ dàng nhìn thấy serial numbers đang ở đâu! 🎯
