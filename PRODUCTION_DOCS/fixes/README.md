# DTX Odoo Fixes Documentation

This folder contains detailed documentation for all fixes and enhancements applied to the DTX Odoo system.

## Recent Fixes (January 2026)

### 2026-01-12: Issues #1 & #2 Complete

#### Issue #1: Contract Cost Profit Analysis
**Module:** `dtx_sales_pakd_contract` v1.5.0

**Problem:**
- Contract Cost sheet lacked profit visibility
- Manual entry for all costs (no automation)
- No comparison with PAKD

**Solution:**
- Auto-populate purchase price from PO (blue, readonly)
- Auto-populate sale price from SO (editable)
- Manual entry for non-PO items (license, misc)
- Line-by-line profit & margin calculation
- Color coding for quick assessment

**Files:** [CONTRACT_COST_PROFIT_ANALYSIS.md](CONTRACT_COST_PROFIT_ANALYSIS.md)

---

#### Issue #2: Component Lifecycle State Inheritance (v2.4.1)
**Module:** `dtx_serial_ext` v2.4.0 → v2.4.1

**Problem:**
- Components consumed in kiosk manufacturing showed "In Production"
- Even after kiosk delivered to customer
- Issue persisted even with quants in production location

**Solution v2.4.0:**
- Detect consumed components (no quants)
- Find manufacturing order where consumed
- Recursively inherit finished product's state

**Solution v2.4.1 (Extended Fix):**
- Handle components WITH quants in production location
- Check if consumed in MO even when quants exist
- Added daily scheduled action for old data
- Existing hook handles new data automatically

**Files:**
- [COMPONENT_STATE_INHERITANCE_FIX.md](COMPONENT_STATE_INHERITANCE_FIX.md) (v2.4.0)
- [FIX_2026-01-12_COMPONENT_STATE_V2.md](FIX_2026-01-12_COMPONENT_STATE_V2.md) (v2.4.1)

---

### 2026-01-10: Multiple Fixes (SO0158)

**Fixed:**
1. PAKD editing permissions for CEO/GDKD
2. Import PAKD costs (skip section/note lines)
3. Create PAKD validation
4. Excel import product matching

**Files:** [FIXES_2026-01-10.md](FIXES_2026-01-10.md)

---

### Earlier Fixes

#### Excel Import Enhancement
**Module:** `dtx_sale_excel_quote` v1.1.0

**Problem:** Product codes with spaces failed to match

**Solution:** 4-strategy matching (exact, cleaned, case-insensitive, fuzzy)

**Files:** [EXCEL_IMPORT_FIX.md](EXCEL_IMPORT_FIX.md)

---

#### Lifecycle State Auto-Tracking
**Module:** `dtx_serial_ext` v2.3.0

**Problem:** Serial lifecycle states not updated automatically

**Solution:** Auto-compute based on stock location

**Files:** [LIFECYCLE_STATE_FIX.md](LIFECYCLE_STATE_FIX.md)

---

## How to Use

Each fix documentation includes:
- **Problem Statement**: What was broken
- **Root Cause Analysis**: Why it happened
- **Solution**: How we fixed it
- **Test Cases**: How to verify the fix
- **Technical Details**: Code changes and logic

---

#### Issue #3: Component Sale Order Linking (v2.4.2)
**Module:** `dtx_serial_ext` v2.4.1 → v2.4.2

**Problem:**
- Components consumed in manufacturing had no link to Sale Orders
- Couldn't see which SO the components were sold in
- Logic existed but never triggered

**Solution:**
- Enhanced hook to recompute sale_order_ids when stock moves done
- Updated scheduled action to recompute sale orders daily
- Components now auto-link to finished product's Sale Orders
- Also updates customer invoices and invoice state

**Result:**
- MiniPC12 → S00160 ✅
- touchscreen11 → S00160 ✅
- 11 components successfully linked ✅

**Files:** [FIX_2026-01-12_COMPONENT_SALE_ORDERS.md](FIX_2026-01-12_COMPONENT_SALE_ORDERS.md)

---

#### Issue #4: External Invoice Number Tracking (v2.5.0)
**Module:** `dtx_serial_ext` v2.4.2 → v2.5.0

**Problem:**
- Need to track MISA external invoice numbers in Device Serials
- Company uses MISA for actual invoice generation
- No way to see external invoice numbers in Odoo

**Solution:**
- Leverage Odoo's standard `account.move.ref` field
- Added computed display fields on stock.lot
- Extract external invoice numbers from vendor bills and customer invoices
- Display in both tree (list) and form (detail) views

**Result:**
- Users enter MISA invoice numbers in Accounting module
- Automatically displayed in Device Serials ✅
- Complete traceability from operations to accounting ✅
- No custom schema changes ✅

**Files:** [EXTERNAL_INVOICE_TRACKING.md](EXTERNAL_INVOICE_TRACKING.md)

---

## Module Versions

| Module | Current Version | Last Updated |
|--------|----------------|--------------|
| dtx_serial_ext | 2.5.0 | 2026-01-13 |
| dtx_sales_pakd_contract | 1.5.0 | 2026-01-12 |
| dtx_sale_excel_quote | 1.1.0 | 2026-01-10 |

## For Developers

When adding new fixes:
1. Create detailed MD file in this folder
2. Include problem/solution/test cases
3. Update this README with summary
4. Link to detailed documentation
5. Update module version in table

## For Users

To apply these fixes:
```bash
# Restart Odoo
docker restart dtx_odoo16

# Upgrade specific module
docker exec dtx_odoo16 odoo -u <module_name> -d dtx_dev --stop-after-init
docker restart dtx_odoo16
```

Replace `<module_name>` with: `dtx_serial_ext`, `dtx_sales_pakd_contract`, or `dtx_sale_excel_quote`
