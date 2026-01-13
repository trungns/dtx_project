# Serial Number Lifecycle State Recompute Issue

**Date:** 2026-01-12
**Module:** `dtx_serial_ext` v2.4.0
**Issue:** Old serial numbers (created before v2.4.0) not updating to correct lifecycle state

---

## Problem Description

User reported that Cam1 serial number still shows "In Production" (`in_production`) instead of "Delivered to Customer" (`delivered`), even though the component was consumed in a kiosk that has been delivered to the customer.

The new component state inheritance logic (Issue #2 fix from 2026-01-12) works correctly for **NEW** stock moves, but does NOT automatically update **OLD** data that existed before the module update.

---

## Root Cause Analysis

### Why Old Data Doesn't Update Automatically

The `x_lifecycle_state` field in `stock.lot` model has:
```python
x_lifecycle_state = fields.Selection(
    ...
    compute='_compute_x_lifecycle_state',
    store=True,  # Stored in database
    help='Automatically computed based on current location',
)
```

**The Problem:** The `_compute_x_lifecycle_state()` method has **NO `@api.depends()` decorator**.

This means:
1. The field is stored in the database
2. The compute method only runs when explicitly called or when the record is created/written
3. There's no dependency tracking to automatically trigger recomputation
4. `write({})` (empty write) does NOT trigger the compute

### Why write({}) Doesn't Work

In stock_lot.py:177, the method signature is:
```python
def _compute_x_lifecycle_state(self):
```

**No decorator like:**
```python
@api.depends('stock.quant', 'stock.move.line')  # This doesn't exist!
```

So when we call `Serial.write([sid], {})`, Odoo doesn't know it needs to recompute this field.

---

## Solution Attempts

### Attempt 1: Trigger via write({}) - FAILED ❌
```python
for sid in serial_ids:
    Serial.write([sid], {})  # Does nothing!
```

**Result:** 0 updates out of 44 serials

**Why it failed:** No @api.depends() means write({}) doesn't trigger compute

### Attempt 2: Direct method call via Odoo Shell - IN PROGRESS ⏳
```python
for serial in serials:
    serial._compute_x_lifecycle_state()  # Call directly
env.cr.commit()
```

**Status:** Script created but output verification pending

---

## Recommended Solutions

### Option 1: Manual Recompute Script (Immediate Fix)

Run the script that directly calls `_compute_x_lifecycle_state()`:

```bash
bash /Users/trungns/dtx_project/scripts/recompute_serials_fixed.sh
```

This will:
- Loop through ALL serial numbers
- Directly call the compute method on each
- Commit changes to database
- Show which serials were updated

### Option 2: Add Dependency Tracking (Long-term Fix)

Modify [stock_lot.py:177](odoo-dev/addons/dtx_serial_ext/models/stock_lot.py#L177) to add dependencies:

```python
@api.depends('quant_ids', 'quant_ids.quantity', 'quant_ids.location_id')
def _compute_x_lifecycle_state(self):
    """
    Compute lifecycle state based on current location of the serial number.
    ...
    """
```

**Benefits:**
- Automatic recomputation when stock moves happen
- No manual scripts needed
- Real-time updates

**Risks:**
- May cause performance issues if quants change frequently
- Need thorough testing

### Option 3: Add Scheduled Action (Hybrid Approach)

Create a cron job that runs daily/weekly to recompute all serials:

```xml
<record id="ir_cron_recompute_serial_states" model="ir.cron">
    <field name="name">Recompute Serial Lifecycle States</field>
    <field name="model_id" ref="stock.model_stock_lot"/>
    <field name="state">code</field>
    <field name="code">
model.search([])._compute_x_lifecycle_state()
env.cr.commit()
    </field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
</record>
```

---

## Testing Steps

### 1. Identify Affected Serials

Look for serials where:
- No stock quants (consumed in production)
- Current state is `in_production`
- Finished product has been delivered (state should be `delivered`)

Example: Cam1

### 2. Check Finished Product State

For consumed components:
1. Find the manufacturing order where consumed
2. Find the finished product serial number
3. Check the finished product's lifecycle state
4. Component should inherit this state

### 3. Verify Recompute

After running recompute script:
1. Check Cam1 serial lifecycle state
2. Should show `delivered` not `in_production`
3. Verify it matches the kiosk's state

---

## Next Steps

1. **Immediate:** Run `recompute_serials_fixed.sh` script to fix old data
2. **Verify:** Check Cam1 and other consumed components show correct state
3. **Document:** Record which serials were updated
4. **Decide:** Choose one of the long-term fix options above
5. **Test:** Create test case for future regressions

---

## Files Created

- `/Users/trungns/dtx_project/scripts/recompute_serials.sh` - Original script (doesn't work)
- `/Users/trungns/dtx_project/scripts/recompute_serials_fixed.sh` - Fixed script (direct method call)
- `/tmp/recompute_serials.py` - Python version via odoorpc
- `/tmp/recompute_serials_fixed.py` - Fixed Python version

---

## Technical Notes

### Why This Happened

1. Module v2.4.0 added component state inheritance logic
2. Logic only runs on `_compute_x_lifecycle_state()` calls
3. Old serials never had this compute method called with new logic
4. No automatic trigger mechanism exists

### How the Inheritance Works

From [stock_lot.py:199-224](odoo-dev/addons/dtx_serial_ext/models/stock_lot.py#L199-L224):

```python
if not quants:  # Consumed component (no stock)
    # Find stock moves where this serial was consumed
    consumed_move_lines = self.env['stock.move.line'].search([
        ('lot_id', '=', lot.id),
        ('state', '=', 'done'),
    ])

    # Filter for manufacturing order consumption
    consumed_moves = consumed_move_lines.mapped('move_id').filtered(
        lambda m: m.raw_material_production_id
    )

    if consumed_moves:
        # Get the production order
        production = consumed_moves[0].raw_material_production_id
        finished_lot = production.lot_producing_id

        if finished_lot:
            # Recursively compute finished product state
            finished_lot._compute_x_lifecycle_state()

            # Inherit the state
            lot.x_lifecycle_state = finished_lot.x_lifecycle_state
```

This logic EXISTS and is CORRECT. It just needs to be EXECUTED on old data.

---

## Status

- ✅ Issue identified and root cause understood
- ✅ Scripts created to fix old data
- ⏳ Waiting for script execution verification
- ⏳ Waiting for user confirmation that Cam1 is fixed
- ❌ Long-term solution not yet implemented

---

## References

- [Issue #2 Fix Documentation](COMPONENT_STATE_INHERITANCE_FIX.md)
- [dtx_serial_ext Module](../../odoo-dev/addons/dtx_serial_ext/)
- [stock_lot.py](../../odoo-dev/addons/dtx_serial_ext/models/stock_lot.py)
