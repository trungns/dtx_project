# UAT Test Case: Component Lifecycle State Inheritance (v2.4.1)

**Date:** 2026-01-12
**Module:** `dtx_serial_ext` v2.4.1
**Feature:** Components in production location inherit finished product state

---

## Background

**Previous Issue (v2.4.0):** Components consumed in production showed incorrect state when they had quants in production location instead of being fully consumed (no quants).

**Fix (v2.4.1):** Logic now handles both cases:
1. Components with NO quants (fully consumed) → inherit state
2. Components with quants in PRODUCTION location → inherit state if consumed in MO

---

## Test Scenario

Test that components stuck in production location inherit the finished product's lifecycle state.

### Prerequisites

- Module `dtx_serial_ext` v2.4.1 installed
- Manufacturing module enabled
- A product with BoM (Bill of Materials)
- At least 2 component serials
- 1 finished product serial

---

## Test Case 1: New Manufacturing Order (Ideal Test)

### Step 1: Create Manufacturing Order
1. Go to **Manufacturing > Operations > Manufacturing Orders**
2. Click **Create**
3. Select a product with BoM (e.g., KIOSK)
4. Set quantity = 1
5. Click **Confirm**

### Step 2: Assign Component Serials
1. Click **Check Availability**
2. In the **Components** tab, assign serial numbers to each component
   - Example: MiniPC13, touchscreen12
3. Note the serial numbers used

### Step 3: Complete Manufacturing
1. Click **Produce**
2. Assign finished product serial (e.g., KIOSK12)
3. Click **Mark as Done**

### Step 4: Verify Component States
1. Go to **Inventory > Products > Lot/Serial Numbers**
2. Search for each component serial (e.g., MiniPC13)
3. Check **Lifecycle State (Auto)** field
4. **Expected:** Should show `In Production` (components in production location)

### Step 5: Deliver Finished Product
1. Find the Sales Order linked to this KIOSK
2. Click **Delivery** smart button
3. Click **Validate** to deliver to customer
4. Wait a few seconds for recompute

### Step 6: Verify Component States Updated
1. Go back to component serials (MiniPC13, touchscreen12)
2. Refresh the page
3. Check **Lifecycle State (Auto)** field
4. **Expected:** Should now show `Delivered to Customer` (inherited from KIOSK12)

**✅ PASS if:** Components show `Delivered to Customer` after finished product delivered

**❌ FAIL if:** Components still show `In Production` after delivery

---

## Test Case 2: Existing Data (MiniPC12, touchscreen11, KIOSK11)

This tests the fix for old data that exists before v2.4.1 deployment.

### Step 1: Check Current State
1. Go to **Inventory > Products > Lot/Serial Numbers**
2. Search for `MiniPC12`
3. Note current **Lifecycle State (Auto)**: _____________
4. Search for `touchscreen11`
5. Note current **Lifecycle State (Auto)**: _____________
6. Search for `KIOSK11`
7. Note current **Lifecycle State (Auto)**: _____________

**Expected:**
- KIOSK11: `Delivered to Customer`
- MiniPC12: `In Production` (WRONG - should be delivered)
- touchscreen11: `In Production` (WRONG - should be delivered)

### Step 2: Wait for Scheduled Action
The system has a scheduled action that runs daily to recompute states.

**Option A: Wait for automatic run (next day)**
- Wait until next day
- Check serials again

**Option B: Manual trigger (immediate)**
1. Go to **Settings > Technical > Automation > Scheduled Actions**
2. Search for "Recompute Serial Lifecycle States"
3. Click on the record
4. Click **Run Manually** button
5. Wait for completion

### Step 3: Verify States Updated
1. Go back to **Lot/Serial Numbers**
2. Search for `MiniPC12`
3. Refresh page
4. Check **Lifecycle State (Auto)**: _____________
5. Repeat for `touchscreen11`

**✅ PASS if:**
- MiniPC12 shows `Delivered to Customer`
- touchscreen11 shows `Delivered to Customer`
- Both match KIOSK11's state

**❌ FAIL if:**
- Components still show `In Production`
- States don't match finished product

---

## Test Case 3: Stock Move Trigger (Real-time Update)

This tests that the hook works for new stock moves.

### Step 1: Create Internal Transfer
1. Go to **Inventory > Operations > Transfers**
2. Create a new transfer
3. Move one component from Production to Stock
   - Example: Move MiniPC12 from Production to WH/Stock
4. Validate the transfer

### Step 2: Verify State Updated
1. Go to the serial number
2. Check **Lifecycle State (Auto)**
3. **Expected:** Should update based on new location

**✅ PASS if:** State updates immediately after stock move

**❌ FAIL if:** State doesn't update

---

## Expected Results Summary

| Serial | Before Fix | After Fix | Notes |
|--------|-----------|-----------|-------|
| KIOSK11 | Delivered | Delivered | Finished product (correct) |
| MiniPC12 | In Production | Delivered | Component (inherited) |
| touchscreen11 | In Production | Delivered | Component (inherited) |

---

## Troubleshooting

### Issue: Components don't update after manual trigger
**Solution:**
1. Check Odoo logs for errors
2. Verify cron job is active
3. Manually run this code in Odoo shell:
```python
production_locs = env['stock.location'].search([('usage', '=', 'production')])
quants = env['stock.quant'].search([
    ('location_id', 'in', production_locs.ids),
    ('quantity', '>', 0),
])
serials = quants.mapped('lot_id')
serials._compute_x_lifecycle_state()
env.cr.commit()
```

### Issue: New manufacturing orders don't trigger update
**Solution:**
1. Check that `stock_move_line.py` hook is active
2. Check logs for DTX Serial Extension messages
3. Verify module version is 2.4.1

---

## Technical Notes

### How It Works

1. **New Stock Moves:** Hook in `_action_done()` calls `_compute_x_lifecycle_state()` automatically
2. **Existing Data:** Scheduled action runs daily to recompute all serials in production location
3. **Logic:**
   ```python
   if location.usage == 'production':
       # Check if consumed in MO
       consumed_moves = self.env['stock.move.line'].search([
           ('lot_id', '=', lot.id),
           ('state', '=', 'done'),
       ]).mapped('move_id').filtered(lambda m: m.raw_material_production_id)

       if consumed_moves:
           production = consumed_moves[0].raw_material_production_id
           finished_lot = production.lot_producing_id
           if finished_lot:
               finished_lot._compute_x_lifecycle_state()
               lot.x_lifecycle_state = finished_lot.x_lifecycle_state
   ```

### Files Changed

- [stock_lot.py:256-284](../../odoo-dev/addons/dtx_serial_ext/models/stock_lot.py#L256-L284) - Added inheritance logic for production location
- [__manifest__.py](../../odoo-dev/addons/dtx_serial_ext/__manifest__.py) - Version bumped to 2.4.1
- [ir_cron.xml](../../odoo-dev/addons/dtx_serial_ext/data/ir_cron.xml) - New scheduled action

---

## Test Results

| Test Case | Date | Tester | Result | Notes |
|-----------|------|--------|--------|-------|
| TC1: New MO | _____ | _____ | ☐ PASS ☐ FAIL | |
| TC2: Existing Data | _____ | _____ | ☐ PASS ☐ FAIL | |
| TC3: Stock Move | _____ | _____ | ☐ PASS ☐ FAIL | |

---

## Sign-off

- [ ] All test cases passed
- [ ] Components inherit correct state from finished products
- [ ] Scheduled action works correctly
- [ ] Stock move hook triggers updates

**Tested by:** _________________
**Date:** _________________
**Approved by:** _________________
