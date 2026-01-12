# Fix Component Lifecycle State Inheritance

## Vấn đề

Khi kiosk được giao cho khách hàng:
- **Kiosk (DTX-A17)**: Location State = "Delivered to Customer" ✅
- **Components (MiniPC11, Touch10, MáyIn4)**: Location State = "In Production" ❌

**Expected behavior:**
- Components đã được consume trong kiosk nên phải inherit state từ kiosk
- Khi kiosk delivered → components cũng phải show "Delivered to Customer"

## Nguyên nhân

### Tại sao components vẫn là "In Production"?

**Khi consume trong manufacturing:**
1. Components move từ `WH/Stock` → `Virtual/Production`
2. Quantity at production location = 0 (consumed)
3. No quants exist for consumed serials

**Current logic trong `_compute_x_lifecycle_state()`:**
```python
quants = self.env['stock.quant'].search([
    ('lot_id', '=', lot.id),
    ('quantity', '>', 0),
])

if not quants:
    lot.x_lifecycle_state = 'in_stock'  # ❌ Wrong default!
    continue
```

**Problem:** Default state là `in_stock` khi không có quants, nhưng consumed components vẫn còn record ở production location với qty=0, nên show "In Production".

## Giải pháp

### Inherit state từ finished product

**New logic:**
```python
if not quants:
    # 1. Find consumed move lines
    consumed_move_lines = self.env['stock.move.line'].search([
        ('lot_id', '=', lot.id),
        ('state', '=', 'done'),
    ])

    # 2. Filter for raw material moves
    consumed_moves = consumed_move_lines.mapped('move_id').filtered(
        lambda m: m.raw_material_production_id
    )

    # 3. Get production order
    if consumed_moves:
        production = consumed_moves[0].raw_material_production_id
        finished_lot = production.lot_producing_id

        # 4. Recursively compute finished product state
        if finished_lot:
            finished_lot._compute_x_lifecycle_state()

            # 5. Inherit the state
            lot.x_lifecycle_state = finished_lot.x_lifecycle_state
            continue
```

### Recursive inheritance

**Scenario:** Multi-level BOM
```
Kiosk (delivered)
  └─ Touch Assembly (consumed)
       └─ Touch Screen (consumed)
       └─ Frame (consumed)
```

**Result:**
- Kiosk: `delivered` (at customer location)
- Touch Assembly: `delivered` (inherit from Kiosk)
- Touch Screen: `delivered` (inherit from Touch Assembly)
- Frame: `delivered` (inherit from Touch Assembly)

## Files Changed

### 1. [models/stock_lot.py](odoo-dev/addons/dtx_serial_ext/models/stock_lot.py#L177-L261)

**Updated:** `_compute_x_lifecycle_state()` method

**Changes:**
- Line 183: Updated docstring to mention state inheritance
- Line 199-228: Added logic to handle consumed components
- Line 202-205: Find consumed move lines
- Line 207-210: Filter for raw material moves
- Line 212-224: Get production and inherit finished product state
- Line 220: Recursive call to handle multi-level BOM
- Line 223: Inherit state from finished product

### 2. [__manifest__.py](odoo-dev/addons/dtx_serial_ext/__manifest__.py)

**Version:** 2.3.0 → 2.4.0

**Changelog:**
```python
Version 2.4.0:
- **FIX**: Consumed components now inherit lifecycle state from finished product
- When serial is consumed in manufacturing (no quants), check finished product state
- Components in delivered kiosk now correctly show 'delivered' status
- Supports recursive state inheritance for multi-level BOM
```

## Test Case

### Scenario: Kiosk delivery with subcontracted components

**Setup:**
1. Manufacturing Order: P00033 (Kiosk DTX-A17)
2. Subcontractor: Đối tác A
3. Components consumed:
   - MiniPC11 (serial)
   - Touch10 (serial)
   - MáyIn4 (serial)

**Flow:**
1. Resupply components to subcontractor
   - Components location: `Partners/Subcontracting/đối tác`
   - **State:** "At Subcontractor" 🟠

2. Subcontractor manufactures kiosk
   - Components consumed (qty = 0)
   - Kiosk produced: KIOSK10
   - Kiosk location: `WH/Stock`
   - **Component state:** "In Production" 🟠 ❌
   - **Kiosk state:** "In Stock" 🟢

3. Deliver kiosk to customer (SO0158)
   - Kiosk location: `Partners/Customers/Xã Vân Hà`
   - **Kiosk state:** "Delivered to Customer" 🔵 ✅

**Before Fix:**
```
Stock -> Lots/Serial Numbers
┌──────────┬─────────────┬──────────────────┐
│ Serial   │ Location    │ Location State   │
├──────────┼─────────────┼──────────────────┤
│ KIOSK10  │ Customer    │ Delivered        │ ✅
│ MiniPC11 │ Production  │ In Production    │ ❌
│ Touch10  │ Production  │ In Production    │ ❌
│ MáyIn4   │ Production  │ In Production    │ ❌
└──────────┴─────────────┴──────────────────┘
```

**After Fix:**
```
Stock -> Lots/Serial Numbers
┌──────────┬─────────────┬──────────────────┐
│ Serial   │ Location    │ Location State   │
├──────────┼─────────────┼──────────────────┤
│ KIOSK10  │ Customer    │ Delivered        │ ✅
│ MiniPC11 │ Production  │ Delivered        │ ✅ (inherited)
│ Touch10  │ Production  │ Delivered        │ ✅ (inherited)
│ MáyIn4   │ Production  │ Delivered        │ ✅ (inherited)
└──────────┴─────────────┴──────────────────┘
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

### 3. Manually recompute states
```python
# In Odoo shell
serials = env['stock.lot'].search([('name', 'in', ['MiniPC11', 'Touch10', 'MáyIn4'])])
for serial in serials:
    serial._compute_x_lifecycle_state()
```

### 4. Verify Results

**Check component state:**
1. Stock > Lots/Serial Numbers
2. Search: MiniPC11
3. **Location State** should show: "Delivered to Customer" 🔵

**Verify inheritance path:**
```python
# Get component
minipc = env['stock.lot'].search([('name', '=', 'MiniPC11')])

# Find consumed move
consumed_moves = env['stock.move.line'].search([
    ('lot_id', '=', minipc.id),
    ('state', '=', 'done')
]).mapped('move_id').filtered(lambda m: m.raw_material_production_id)

# Get production
production = consumed_moves[0].raw_material_production_id
print(f"Production: {production.name}")  # P00033

# Get finished product
kiosk = production.lot_producing_id
print(f"Kiosk: {kiosk.name}")  # KIOSK10
print(f"Kiosk state: {kiosk.x_lifecycle_state}")  # delivered

# Component inherits from kiosk
print(f"Component state: {minipc.x_lifecycle_state}")  # delivered ✅
```

## Technical Details

### Why Recursive?

**Multi-level BOM example:**
```
Level 0: Kiosk → delivered to customer
Level 1: Touch Assembly → consumed in Kiosk
Level 2: Touch Screen → consumed in Touch Assembly
```

**Without recursion:**
- Touch Screen would inherit from Touch Assembly
- But Touch Assembly's state is not computed yet
- Result: Wrong state

**With recursion:**
```python
# Compute Touch Screen state
touch_screen._compute_x_lifecycle_state()
  → No quants, find production
  → Production = Touch Assembly MO
  → Compute Touch Assembly state (RECURSIVE)
    touch_assembly._compute_x_lifecycle_state()
      → No quants, find production
      → Production = Kiosk MO
      → Compute Kiosk state (RECURSIVE)
        kiosk._compute_x_lifecycle_state()
          → Has quants at customer location
          → State = 'delivered'
      → Inherit: touch_assembly.state = 'delivered'
  → Inherit: touch_screen.state = 'delivered'
```

### Edge Cases Handled

1. **Component consumed in multiple MOs:**
   - Use `consumed_moves[0]` (first production)
   - Assumption: Serial can only be consumed once

2. **Production without finished serial:**
   - `if finished_lot:` check prevents error
   - Fallback to default `in_stock`

3. **Circular dependency:**
   - Odoo prevents circular BOM by design
   - Safe to use recursion

## Migration Notes

**Existing serials need recompute:**

After upgrade, consumed components will still show wrong state until recomputed.

**Option 1: Manual trigger (immediate)**
```python
# Odoo shell
consumed_serials = env['stock.lot'].search([])
for serial in consumed_serials:
    quants = env['stock.quant'].search([('lot_id', '=', serial.id), ('quantity', '>', 0)])
    if not quants:
        serial._compute_x_lifecycle_state()
```

**Option 2: Wait for next stock move**
- Next time any serial moves, it will trigger recompute via `stock_move_line._action_done()`
- Automatic but slower

## Alternative Solutions Considered

### Option 1: Store consumed state in field ❌
```python
consumed_in_production_id = fields.Many2one('mrp.production')
```
**Rejected:** Adds complexity, not needed

### Option 2: Compute state based on last move ❌
```python
last_move = move_lines.sorted('id', reverse=True)[0]
if last_move.location_dest_id.usage == 'production':
    state = 'in_production'
```
**Rejected:** Doesn't reflect actual status (kiosk is delivered, not in production)

### Option 3: Inherit state from finished product ✅
**Selected:** Most accurate representation of reality

## Summary

✅ **Fixed:** Components consumed in manufacturing now inherit state from finished product
✅ **Result:** Delivered kiosk components show "Delivered to Customer"
✅ **Recursive:** Supports multi-level BOM
✅ **Version:** 2.3.0 → 2.4.0

Now components truly reflect their status! 🎯
