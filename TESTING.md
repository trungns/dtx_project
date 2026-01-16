# Testing Guide: Subscription Management Module

**Version:** 1.6.0
**Date:** 2026-01-14
**Modules:** dtx_product_standards v1.3.0, dtx_sales_pakd_contract v1.6.0

---

## Pre-Testing Checklist

- [ ] Database backed up
- [ ] Modules upgraded successfully
- [ ] Odoo running without errors
- [ ] No errors in logs: `docker-compose logs -f odoo`

---

## Test Case 1: Create Subscription Product ✅

**Objective:** Verify new product type and fields work correctly

### Steps:

1. **Navigate to Products**
   ```
   Menu: Inventory > Products > Products > Create
   ```

2. **Fill Product Details**
   ```
   Product Name: DiHub Cloud License
   Product Type: Service
   Can be Sold: ✓ Yes
   Can be Purchased: ✗ No
   ```

3. **Set DTX Type**
   ```
   DTX Type: Subscription / License theo tháng
   ```

   **Expected:** "Subscription Settings" group appears below

4. **Fill Common Metadata**
   ```
   Part Number: DIHUB-LIC-001
   Country of Origin: Vietnam
   ```

5. **Fill Subscription Settings**
   ```
   Base Price / Device / Month: 80,000
   Default Duration (Months): 12
   ```

6. **Set Sales Price & Tax**
   ```
   Sales Tab:
   - Sales Price: 80,000
   - Unit of Measure: Unit
   - Customer Taxes: VAT 10%
   ```

7. **Save Product**

### Verification:

- [ ] Product saved successfully
- [ ] DTX Type shows "Subscription / License theo tháng"
- [ ] Part Number displays: DIHUB-LIC-001
- [ ] Country of Origin displays: Vietnam
- [ ] Subscription settings saved correctly
- [ ] In product list view:
  - [ ] Part Number column shows DIHUB-LIC-001
  - [ ] Country of Origin column shows Vietnam
  - [ ] Can filter by "Subscription / License"

---

## Test Case 2: Create Subscription Quotation ✅

**Objective:** Verify subscription fields on SO lines work correctly

### Steps:

1. **Create Sale Order**
   ```
   Menu: Sales > Quotations > Create
   Customer: [Select or create test customer]
   ```

2. **Add Subscription Product**
   ```
   Add a line > Product: DiHub Cloud License
   ```

3. **Verify Auto-fill**
   ```
   Expected auto-filled values:
   - Unit Price: 80,000 (from product)
   - Months: 12 (from product default)
   ```

4. **Fill Subscription Fields**
   ```
   Device Count: 10
   Months: 9 (change from default 12)
   Subscription Start: 2025-12-01
   ```

5. **Verify Auto-calculations**
   ```
   Expected:
   - Quantity: 90 (10 × 9) ← Auto-calculated
   - Subscription End: 2026-08-31 ← Auto-calculated
   - Subtotal: 7,200,000 (90 × 80,000)
   - VAT 10%: 720,000
   - Total: 7,920,000
   ```

6. **Verify Display Fields**
   ```
   In SO line tree view, check visible:
   - Part Number: DIHUB-LIC-001
   - Country of Origin: Vietnam
   - Device Count: 10
   - Months: 9
   - Subscription Start: 2025-12-01
   - Subscription End: 2026-08-31
   ```

7. **Save Quotation**

### Verification:

- [ ] Quantity auto-calculates to 90 when entering device count & months
- [ ] End date auto-calculates correctly (2026-08-31)
- [ ] Total amount = 7,920,000 VNĐ (matches Excel calculation)
- [ ] Part Number displays in SO line
- [ ] Country of Origin displays in SO line
- [ ] Subscription fields only visible for subscription products
- [ ] No errors in console/logs

---

## Test Case 3: Renew Contract ✅

**Objective:** Verify renewal wizard works correctly

### Setup:
Use quotation from Test Case 2, confirm it first

### Steps:

1. **Confirm Quotation**
   ```
   Button: Confirm
   Fill:
   - Contract Number: HĐ-TEST-001
   - Signed Date: 2025-12-01
   ```

2. **Verify "Renew Contract" Button Appears**
   ```
   Expected: Button visible at top (next to Create Invoice button)
   State: sale (confirmed)
   Has subscription lines: Yes
   ```

3. **Click "Renew Contract"**
   ```
   Button: Renew Contract
   ```

4. **Wizard Form Verification**
   ```
   Expected pre-filled:
   - Original Start Date: 2025-12-01 (readonly)
   - Original End Date: 2026-08-31 (readonly)
   - New Start Date: 2026-09-01 (auto = old end + 1 day)
   - New Duration: 12 months (editable)
   - New End Date: 2027-08-31 (auto-calculated)
   ```

5. **Modify Duration** (Optional)
   ```
   Change: New Duration = 6 months
   Expected: New End Date = 2027-02-28

   Change back: New Duration = 12 months
   ```

6. **Create Renewal**
   ```
   Button: Create Renewal Quotation
   ```

7. **Verify New Quotation Created**
   ```
   Expected:
   - New SO created (state=draft)
   - Same product lines as original
   - Subscription dates updated:
     - Start: 2026-09-01
     - End: 2027-08-31
     - Months: 12
   - Quantity recalculated: 10 × 12 = 120
   - Contract fields cleared (no contract number, etc.)
   ```

8. **Verify Chatter Links**
   ```
   Original SO (HĐ-TEST-001):
   - Message: "Renewal quotation created: S00XXX"

   New SO (S00XXX):
   - Message: "Renews contract: S00YYY"
   ```

### Verification:

- [ ] "Renew Contract" button only visible when SO confirmed + has subscription
- [ ] Wizard pre-fills original dates correctly
- [ ] New start date defaults to old end + 1 day
- [ ] New end date auto-calculates correctly
- [ ] New SO created with updated dates
- [ ] Quantity recalculated (device count × new months)
- [ ] Chatter messages link both SOs
- [ ] Can open new SO directly from result

---

## Test Case 4: Mixed Quotation (Hardware + Subscription) ✅

**Objective:** Verify subscription works alongside normal products

### Steps:

1. **Create Sale Order**
   ```
   Customer: Test Customer
   ```

2. **Add Section: Hardware**
   ```
   Add a line > Section
   Name: A. Phần cứng
   ```

3. **Add Normal Product** (Create if needed)
   ```
   Product: DTX Kiosk 32" (or any hardware product)
   - DTX Type: device_serialized or finished_kiosk
   - Part Number: DTX-K32-001
   - Country of Origin: China
   - Quantity: 5
   - Unit Price: 25,000,000
   - VAT: 8%
   ```

4. **Add Section: Subscription**
   ```
   Add a line > Section
   Name: B. Chi phí thuê license
   ```

5. **Add Subscription Product**
   ```
   Product: DiHub Cloud License
   - Device Count: 10
   - Months: 12
   - Start: 2025-12-01
   - Expected Quantity: 120
   - Unit Price: 80,000
   - VAT: 10%
   ```

6. **Verify Display**
   ```
   Line 1 (Section): A. Phần cứng
   Line 2 (Product): DTX Kiosk 32"
     - Part Number: DTX-K32-001
     - Country of Origin: China
     - Quantity: 5
     - NO subscription fields visible ✓

   Line 3 (Section): B. Chi phí thuê license
   Line 4 (Product): DiHub Cloud License
     - Part Number: DIHUB-LIC-001
     - Country of Origin: Vietnam
     - Device Count: 10
     - Months: 12
     - Subscription fields visible ✓
     - Quantity: 120 (auto)
   ```

7. **Verify Totals**
   ```
   Hardware: 5 × 25,000,000 × 1.08 = 135,000,000
   Subscription: 120 × 80,000 × 1.10 = 10,560,000
   Total: 145,560,000
   ```

### Verification:

- [ ] Both product types display Part Number + Country of Origin
- [ ] Subscription fields only visible for subscription lines
- [ ] Normal product lines don't show subscription fields
- [ ] Both VAT rates applied correctly (8% vs 10%)
- [ ] Total calculation correct
- [ ] Can confirm and invoice normally
- [ ] "Renew Contract" button appears (has subscription lines)

---

## Test Case 5: Backward Compatibility ✅

**Objective:** Verify existing products/SOs still work after upgrade

### Steps:

1. **Check Existing Products**
   ```
   Menu: Inventory > Products > Products
   Filter: [Existing products before upgrade]
   ```

2. **Open Hardware Product** (e.g., Touch Screen)
   ```
   Expected:
   - DTX Type: device_serialized (unchanged)
   - Part Number: (empty - OK, optional field)
   - Country of Origin: (empty - OK, optional field)
   - NO "Subscription Settings" group visible ✓
   - NO errors when opening ✓
   ```

3. **Open Service Product** (e.g., Installation Service)
   ```
   Expected:
   - DTX Type: service (unchanged)
   - Part Number: (empty - OK)
   - Country of Origin: (empty - OK)
   - NO "Subscription Settings" group visible ✓
   ```

4. **Open Existing Sales Order**
   ```
   Menu: Sales > Orders
   Select: Any confirmed SO from before upgrade
   ```

5. **Verify SO Still Works**
   ```
   Expected:
   - Opens without errors ✓
   - SO lines display correctly ✓
   - Part Number column shows (empty for old lines - OK) ✓
   - Country of Origin column shows (empty for old lines - OK) ✓
   - NO subscription fields visible on old lines ✓
   - Can still create invoice ✓
   - No "Renew Contract" button (no subscription lines) ✓
   ```

6. **Add Line to Existing SO**
   ```
   Add: Any normal product (not subscription)
   Expected: Works normally, no subscription fields visible ✓
   ```

### Verification:

- [ ] Existing products open without errors
- [ ] Old DTX types still work (device_serialized, service, etc.)
- [ ] New fields (Part Number, CO) are optional (can be empty)
- [ ] Existing SOs open without errors
- [ ] Old SO lines don't show subscription fields
- [ ] Can still perform normal operations (invoice, delivery, etc.)
- [ ] No database migration errors in logs

---

## Test Case 6: Part Number & Country of Origin (All Products) ✅

**Objective:** Verify common metadata fields work for all product types

### Steps:

1. **Update Existing Hardware Product**
   ```
   Product: Touch Screen 21"
   DTX Type: device_serialized
   Fill:
   - Part Number: TS-21-PCAP-001
   - Country of Origin: China
   Save
   ```

2. **Update Service Product**
   ```
   Product: Installation Service
   DTX Type: service
   Fill:
   - Part Number: SVC-INSTALL
   - Country of Origin: Vietnam
   Save
   ```

3. **Create SO with Multiple Product Types**
   ```
   Add lines:
   1. Touch Screen 21" (DTX Type: device_serialized)
   2. Installation Service (DTX Type: service)
   3. DiHub Cloud License (DTX Type: subscription)
   ```

4. **Verify Display in SO Lines**
   ```
   All lines should show:
   - Part Number column
   - Country of Origin column

   Line 1: TS-21-PCAP-001, China
   Line 2: SVC-INSTALL, Vietnam
   Line 3: DIHUB-LIC-001, Vietnam
   ```

### Verification:

- [ ] Part Number & CO work for ALL product types
- [ ] Fields visible in product form for all types
- [ ] Fields visible in SO line tree for all types
- [ ] Fields optional (can be empty)
- [ ] Tracking works (changes logged)

---

## Error Scenarios to Test 🔍

### Error 1: Missing Device Count or Months

**Steps:**
1. Create SO with subscription product
2. Enter Device Count: 10
3. Leave Months: empty
4. Try to save

**Expected:** Quantity should remain manual (not auto-calculated)

---

### Error 2: Button Visibility

**Test "Renew Contract" button logic:**

| SO State | Has Subscription Lines | Button Visible? |
|----------|----------------------|----------------|
| draft | Yes | ❌ No |
| sent | Yes | ❌ No |
| sale | Yes | ✅ Yes |
| sale | No | ❌ No |
| done | Yes | ✅ Yes |
| cancel | Yes | ❌ No |

---

## Performance Test 📊

**Objective:** Verify no performance degradation

### Steps:

1. **Check Load Time**
   ```
   - Product list load time: < 2 seconds
   - SO form load time: < 1 second
   - SO line tree render: < 1 second
   ```

2. **Check Database**
   ```bash
   docker-compose exec db psql -U odoo dtx_odoo16

   -- Count products
   SELECT x_dtx_type, COUNT(*) FROM product_template GROUP BY x_dtx_type;

   -- Check new fields
   SELECT COUNT(*) FROM product_template WHERE x_part_number IS NOT NULL;

   -- Check SO lines
   SELECT COUNT(*) FROM sale_order_line WHERE x_is_subscription = true;
   ```

### Verification:

- [ ] No slowdown in UI
- [ ] Database queries performant
- [ ] No N+1 query issues
- [ ] Logs show no warnings

---

## Post-Testing Checklist ✅

After completing all test cases:

- [ ] All 6 test cases passed
- [ ] No errors in Odoo logs
- [ ] No JavaScript console errors
- [ ] Database backup exists
- [ ] Rollback plan ready (if needed)
- [ ] Ready for production deployment

---

## Rollback Plan 🔄

If issues found:

```bash
# 1. Stop Odoo
docker-compose stop odoo

# 2. Restore backup
./scripts/restore-db.sh dtx_odoo16 [backup_file]

# 3. Downgrade modules (if needed)
# Edit __manifest__.py to revert versions
# Re-run upgrade with old versions

# 4. Start Odoo
docker-compose up -d odoo
```

---

## Test Results Log 📝

**Date:** _________________
**Tester:** _________________
**Environment:** Development / Staging / Production

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC1: Create Product | ⬜ Pass / ⬜ Fail | |
| TC2: Create Quotation | ⬜ Pass / ⬜ Fail | |
| TC3: Renew Contract | ⬜ Pass / ⬜ Fail | |
| TC4: Mixed Quotation | ⬜ Pass / ⬜ Fail | |
| TC5: Backward Compat | ⬜ Pass / ⬜ Fail | |
| TC6: Common Metadata | ⬜ Pass / ⬜ Fail | |

**Overall Result:** ⬜ PASS / ⬜ FAIL

**Issues Found:**
```
[List any issues here]
```

**Sign-off:**
- Tester: _________________
- Date: _________________
