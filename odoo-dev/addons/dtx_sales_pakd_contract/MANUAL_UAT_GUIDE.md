# Manual UAT Testing Guide - Quỳ Châu Project

**Module**: dtx_sales_pakd_contract
**Version**: 16.0.1.2.0
**Test Date**: 2026-01-04
**Odoo URL**: http://localhost:8069

---

## Prerequisites

✅ **Odoo Status**: Running on port 8069
✅ **Module Status**: Installed with automated tests
✅ **Database**: odoo

**Login Credentials** (default):
- **Username**: admin
- **Password**: admin

---

## Test Scenario: Dự án Quỳ Châu - 197.5M VND

### Overview
- **Đại lý**: Viettel Hà Nội
- **End Customer**: UBND Quỳ Châu
- **Total Contract**: 197,500,000 VND
- **Products**: 9 items (software + hardware + services)
- **VAT**: Mixed 0% and 10%

---

## STEP 1: Setup Master Data (Can Skip if Automated Tests Ran)

### 1.1 Create Partners

**Navigate**: Contacts → Create

**Partner 1: Viettel Hà Nội**
- Name: Viettel Hà Nội
- Company Type: Company
- Street: 1 Giang Văn Minh
- City: Hà Nội
- Phone: 0243.943.9999

**Partner 2: UBND Quỳ Châu**
- Name: UBND Quỳ Châu
- Company Type: Company
- Street: Quỳ Châu
- City: Nghệ An

### 1.2 Verify Taxes

**Navigate**: Accounting → Configuration → Taxes

**Required Taxes**:
- ✅ VAT 0% (Type: Sales, Amount: 0%)
- ✅ VAT 10% (Type: Sales, Amount: 10%)

If missing, create them.

### 1.3 Create Products

**Navigate**: Sales → Products → Products → Create

**Create 9 Products**:

| Code | Name | Type | Sale Price | VAT |
|------|------|------|------------|-----|
| SEQMS-BrA | SEQMS-BrA License | Service | 45,628,000 | 0% |
| SEQMS-Counter | SEQMS-Counter Module | Service | 4,000,000 | 0% |
| DTX-A17 | DTX-A17 LED Display | Storable Product | 34,560,000 | 10% |
| DTX-LEDw | DTX-LEDw LED Panel | Storable Product | 4,320,000 | 10% |
| UA98DU9000 | Samsung TV UA98DU9000 | Storable Product | 49,680,000 | 10% |
| X2-2.1 | Speaker X2-2.1 | Storable Product | 2,592,000 | 10% |
| SV-VC | Videoconference Service | Service | 2,160,000 | 10% |
| SV-INSTALL | Installation Service | Service | 1,620,000 | 10% |
| SV-TRAIN | Training Service | Service | 3,240,000 | 10% |

**For each product**:
1. General Information tab:
   - Name: [as above]
   - Internal Reference: [Code]
   - Product Type: [Service or Storable Product]
   - Sales Price: [as above]
2. Invoicing tab:
   - Customer Taxes: [VAT as above]

---

## STEP 2: Create Quotation

**Navigate**: Sales → Orders → Quotations → Create

### 2.1 Quotation Header

- **Customer**: Viettel Hà Nội
- **End Customer**: UBND Quỳ Châu (custom field `x_end_customer_id`)
  - *Note: This field is in "DTX Business" tab*

### 2.2 Order Lines

Click "Add a product" and add 9 lines:

| Product | Qty | Unit Price |
|---------|-----|------------|
| SEQMS-BrA | 1 | 45,628,000 |
| SEQMS-Counter | 6 | 4,000,000 |
| DTX-A17 | 1 | 34,560,000 |
| DTX-LEDw | 6 | 4,320,000 |
| UA98DU9000 | 1 | 49,680,000 |
| X2-2.1 | 1 | 2,592,000 |
| SV-VC | 1 | 2,160,000 |
| SV-INSTALL | 6 | 1,620,000 |
| SV-TRAIN | 1 | 3,240,000 |

### 2.3 Verify Total

**Expected Totals**:
- **Untaxed Amount**: ~179,545,455 VND
- **Taxes**: ~17,954,545 VND
- **Total**: **197,500,000 VND** ✅

**Save** quotation (but DON'T confirm yet)

---

## STEP 3: Create PAKD from Quotation

### 3.1 Create PAKD

In the quotation form:
1. Click **"Tạo PAKD"** button (top toolbar)
   - *Or navigate to PAKD tab and click "Create"*
2. System will create a new PAKD with:
   - Name: Auto-generated (PAKD/YYYY/XXXX)
   - 9 lines copied from quotation
   - Partner, End Customer auto-filled

### 3.2 Verify PAKD Lines

**Navigate**: PAKD form view

Check that 9 lines exist with:
- ✅ Product, Quantity, UoM
- ✅ `sale_unit_price` copied from quotation
- ✅ `vat_percent` mapped correctly:
  - SEQMS-BrA, SEQMS-Counter: 0%
  - All others: 10%
- ✅ `tax_id` mapped to correct account.tax

### 3.3 Set Purchase Prices

Edit PAKD lines to add purchase unit prices:

| Product Code | Purchase Unit Price | Contract Unit Price |
|--------------|---------------------|---------------------|
| DTX-A17 | 22,000,000 | (same as sale) |
| DTX-LEDw | 3,100,000 | (same as sale) |
| UA98DU9000 | 45,000,000 | (same as sale) |
| X2-2.1 | 2,000,000 | (same as sale) |
| SV-INSTALL | 18,000,000 | (same as sale) |

*Note: For other products, you can leave purchase price as 0 or set custom values*

**Contract Unit Price**: Set = `sale_unit_price` for all lines
*(Or leave empty - system will use sale_unit_price)*

### 3.4 Verify PAKD Totals

**Expected Header Totals**:
- **Total Purchase** (Tổng giá nhập): Based on your purchase prices
- **Total Sale** (Tổng giá bán): 197,500,000 (same as quotation)
- **Total Contract (excl VAT)**: ~179,545,455
- **Total Contract Tax**: ~17,954,545
- **Total Contract (incl VAT)**: **197,500,000 VND** ✅

### 3.5 Approve PAKD

1. Click **"Trình duyệt"** (Submit) → State = Submitted
2. Click **"Phê duyệt"** (Approve) → State = Approved

---

## STEP 4: Apply PAKD to Quotation

### 4.1 Open Apply Wizard

In PAKD form:
1. Click **"Apply vào SO"** button
2. Wizard opens with options:
   - ✅ Replace existing lines: Yes
   - Price source: "Ưu tiên đơn giá HĐ" (Contract price)

### 4.2 Execute Apply

1. Review warning message (if any)
2. Click **"Apply"**
3. System will:
   - Delete old quotation lines
   - Create new lines from PAKD
   - Use `contract_unit_price` (or `sale_unit_price` if empty)

### 4.3 Verify Quotation Updated

Back in quotation:
- ✅ Lines updated with PAKD data
- ✅ Prices match PAKD `contract_unit_price`
- ✅ Total still **197,500,000 VND**

---

## STEP 5: Confirm Sales Order

### 5.1 Confirm Quotation

In quotation form:
1. Click **"Confirm"** button
2. State changes: Draft → Sales Order
3. Quotation becomes a confirmed Sales Order

### 5.2 Set Contract Fields

In Sales Order form, go to **"Hợp đồng"** tab:

Fill in:
- **Số hợp đồng** (x_contract_no): HĐ-QC-2026-001
- **Ngày ký HĐ** (x_signed_date): Today
- **Ngày hết hạn HĐ** (x_contract_end_date): Today + 365 days

**Save**

---

## STEP 6: Upload Contract Scans

### 6.1 Create Attachments

In Sales Order form:
1. Go to **"Hợp đồng"** tab
2. Field **"File scan hợp đồng"** (x_contract_scan_attachment_ids)
3. Click "Add" → Upload files:
   - Hop_Dong_Quy_Chau_signed.pdf
   - Phu_Luc_Hop_Dong.pdf

### 6.2 Verify Attachment Count

- Field **"Số file scan"** should show: **2**

---

## STEP 7: Create and Post Invoice

### 7.1 Create Invoice from Sales Order

In Sales Order:
1. Click **"Create Invoice"** button
2. Create invoice:
   - Invoice Date: Today
   - Due Date: Today + 30 days
3. **Post** invoice (Confirm)

### 7.2 Verify Invoice

- ✅ State: Posted
- ✅ Amount Total: **197,500,000 VND**
- ✅ Amount Residual: 197,500,000 (unpaid)
- ✅ Field `x_days_overdue`: 0 (not overdue yet)

---

## STEP 8: Test AR Aging Features

### 8.1 Check AR Fields on Sales Order

In Sales Order, check computed fields:
- **Còn phải thu** (x_ar_residual_total): 197,500,000
- **Quá hạn tối đa** (x_ar_max_days_overdue): 0 days
- **Trạng thái công nợ** (x_ar_status):
  - "OK" (if due > 7 days from now)
  - "Sắp đến hạn" (if due within 7 days)

### 8.2 View AR Aging Summary

**Navigate**: Sales → Công nợ → Tổng hợp tuổi nợ

**Find row for**: Viettel Hà Nội

**Verify**:
- ✅ Tổng công nợ: 197,500,000
- ✅ Chưa đến hạn (Bucket Current): 197,500,000
- ✅ Bucket 1-5: 0 (not overdue)
- ✅ Quá hạn tối đa: 0 days
- ✅ Số hóa đơn: 1

**Row decoration**:
- Should be normal (white) - no overdue

### 8.3 Drilldown to Invoices

In AR Aging Summary row:
1. Double-click on "Viettel Hà Nội" row
2. Should open list of invoices for this partner
3. Verify:
   - ✅ 1 invoice shown
   - ✅ Amount Residual: 197,500,000
   - ✅ Days Overdue: 0

### 8.4 Test AR Aging Config

**Navigate**: Sales → Công nợ → Cấu hình tuổi nợ

**Verify default buckets**:
- Bucket 1: 7 days → Label: "1-7 ngày"
- Bucket 2: 15 days → Label: "8-15 ngày"
- Bucket 3: 30 days → Label: "16-30 ngày"
- Bucket 4: 60 days → Label: "31-60 ngày"
- Bucket 5: 90 days → Label: "61-90 ngày"

**Try changing**:
- Change Bucket 1 to 10 days
- Save
- Verify label updates: "1-10 ngày", "11-15 ngày", ...

### 8.5 Pivot Analysis

**Navigate**: Sales → Công nợ → Tổng hợp tuổi nợ → Switch to Pivot view

**Test**:
- Group by: Nhân viên bán hàng (row)
- Measures: Tổng công nợ, Bucket 1-3
- ✅ Data shows correctly
- ✅ Can drill down to partners
- ✅ Export to Excel works

---

## STEP 9: Test Edge Cases

### 9.1 Create Multiple PAKDs

Back in Sales Order:
1. Click **"Tạo PAKD"** again
2. Should create 2nd PAKD for same order
3. ✅ Both PAKDs linked to same Sales Order
4. ✅ Can apply either PAKD

### 9.2 Test PAKD State Workflow

Create new PAKD:
1. State: Draft
2. Click "Trình duyệt" → State: Submitted
3. Click "Phê duyệt" → State: Approved
4. Or click "Từ chối" → State: Rejected
5. Click "Reset về Draft" → State: Draft again

### 9.3 Test Payment and AR Status

**Scenario A: Partial Payment**
1. Create payment for invoice (50% = 98,750,000)
2. Check AR fields on Sales Order:
   - x_ar_residual_total: 98,750,000 (reduced)
   - x_ar_status: Still "OK" or "Sắp đến hạn"

**Scenario B: Full Payment**
1. Create payment for remaining 98,750,000
2. Check AR fields:
   - x_ar_residual_total: 0
   - x_ar_status: "OK"
3. Check AR Aging Summary:
   - Viettel Hà Nội row should disappear (no residual)

**Scenario C: Overdue Invoice**
1. Create new invoice with due date = Today - 15 days
2. Post invoice
3. Check AR Aging Summary:
   - Bucket 2 (8-15 ngày): Shows amount
   - Row decoration: Yellow/Orange (warning)
4. Create invoice due date = Today - 35 days
5. Check:
   - Bucket 3 (16-30 ngày): Shows amount
   - Row decoration: Red (danger)

---

## STEP 10: Test Security & Access Control

### 10.1 Sales User Access

**Setup**:
1. Create user: Sales User A
2. Assign group: Sales / User
3. Assign as salesperson on Sales Order

**Test**:
1. Login as Sales User A
2. Navigate: Sales → Công nợ → Tổng hợp tuổi nợ
3. ✅ See only customers from own sales orders
4. ✅ Cannot see other users' customers

### 10.2 Sales Manager Access

**Setup**:
1. Create user: Sales Manager
2. Assign group: Sales / Manager

**Test**:
1. Login as Sales Manager
2. Navigate: Sales → Công nợ → Tổng hợp tuổi nợ
3. ✅ See ALL customers (no restriction)
4. ✅ Can access config: Cấu hình tuổi nợ

### 10.3 Accountant Access

**Setup**:
1. Create user: Accountant
2. Assign group: Accounting / Billing

**Test**:
1. Login as Accountant
2. Navigate: Sales → Công nợ → Tổng hợp tuổi nợ
3. ✅ See all AR aging data (read-only)

---

## Expected Results Summary

### ✅ PASS Criteria

1. **Quotation Total**: 197,500,000 VND (±1 tolerance)
2. **PAKD Creation**: 9 lines with correct VAT mapping
3. **PAKD Formulas**: Match Excel calculations
4. **Apply Wizard**: Updates quotation lines correctly
5. **Sales Order**: Confirm + contract fields work
6. **Contract Scans**: Upload 2 files, count = 2
7. **Invoice**: Posted, total = 197,500,000
8. **AR Aging Summary**: Shows correct residual and buckets
9. **AR Fields on SO**: Compute correctly (residual, days overdue, status)
10. **Pivot Analysis**: Works correctly
11. **Multiple PAKDs**: Can create multiple PAKDs per SO
12. **State Workflow**: Draft → Submitted → Approved → Rejected
13. **Access Control**: Sales users see only own customers, managers see all

### ❌ FAIL Criteria

- Quotation total ≠ 197,500,000
- PAKD VAT mapping incorrect
- Apply wizard doesn't update lines
- AR aging summary shows wrong residual
- Bucket classification incorrect
- Access control not working (users see all data)

---

## Troubleshooting

### Issue: Module not installed

**Solution**:
```bash
docker-compose run --rm odoo odoo -d odoo -i dtx_sales_pakd_contract --stop-after-init
docker-compose restart odoo
```

### Issue: AR Aging Summary empty

**Cause**: SQL view not refreshed or no unpaid invoices

**Solution**:
1. Post an invoice with residual > 0
2. Refresh view (F5)
3. Or restart Odoo

### Issue: PAKD button not visible

**Cause**: User doesn't have permission

**Solution**:
- Assign user to "Sales / User" group minimum
- Or "CEO" / "Sales Director" / "Chief Accountant" groups

### Issue: Tests not running

**Solution**:
```bash
cd odoo-dev
docker-compose run --rm odoo odoo -d odoo \
  --test-tags=dtx_sales_pakd_contract \
  --stop-after-init
```

---

## Notes

- **Performance**: AR Aging SQL view should be fast (<1s for 10K invoices)
- **Currency**: All amounts in company currency (VND)
- **Rounding**: Uses currency rounding (tolerance ±1)
- **Refresh**: Summary updates automatically via SQL view
- **Due Date**: If NULL, uses invoice_date

---

**Tester**: _______________
**Date**: _______________
**Result**: ☐ PASS  ☐ FAIL
**Issues Found**: _______________________________________________
