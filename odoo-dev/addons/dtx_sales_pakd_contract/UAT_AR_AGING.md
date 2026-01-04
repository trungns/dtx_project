# UAT Test Case: AR Aging (Tuổi Nợ Phải Thu)

**Module**: dtx_sales_pakd_contract v1.3.0 (B4)
**Feature**: AR Aging + Cảnh báo công nợ
**Test Date**: 2026-01-04
**Purpose**: Verify AR aging report và cảnh báo công nợ theo đúng yêu cầu

---

## PREREQUISITES

### Test Data Setup

**Customer**: Viettel Hà Nội (hoặc tạo partner test mới)
**Sale Order**: SO-001 (hoặc tạo mới)

### Create Test Invoices

**Invoice A - Quá hạn 10 ngày:**
- Customer: Viettel HN
- Invoice Date: Today - 15 days
- Due Date: Today - 10 days
- Amount Total: 100,000,000 VND
- State: Posted
- Payment: Chưa thanh toán (amount_residual = 100,000,000)

**Invoice B - Sắp đến hạn (5 ngày nữa):**
- Customer: Viettel HN
- Invoice Date: Today
- Due Date: Today + 5 days
- Amount Total: 50,000,000 VND
- State: Posted
- Payment: Chưa thanh toán (amount_residual = 50,000,000)

---

## TEST CASE 1: Cấu hình tuổi nợ

### Steps:
1. Login as Sales Manager hoặc CEO
2. Navigate: **Sales → Công nợ → Cấu hình tuổi nợ**
3. Verify default config exists
4. Check default values:
   - Bucket 1: 7 ngày
   - Bucket 2: 15 ngày
   - Bucket 3: 30 ngày
   - Bucket 4: 60 ngày
   - Bucket 5: 90 ngày

### Expected Results:
- ✅ Form hiển thị config singleton
- ✅ Default values correct
- ✅ Labels hiển thị đúng: "1-7 ngày", "8-15 ngày", ...
- ✅ Có validation: không cho phép bucket_1 >= bucket_2

### Test Change Config:
1. Try changing Bucket 1 to 10 days
2. Save
3. Verify labels update: "1-10 ngày", "11-15 ngày", ...

---

## TEST CASE 2: Tổng hợp tuổi nợ

### Steps:
1. Navigate: **Sales → Công nợ → Tổng hợp tuổi nợ**
2. Find row for "Viettel HN"

### Expected Results:

| Field | Expected Value | Actual | Pass/Fail |
|-------|---------------|--------|-----------|
| Khách hàng | Viettel HN | _______ | ☐ |
| Tổng công nợ | 150,000,000 | _______ | ☐ |
| Chưa đến hạn (Bucket Current) | 50,000,000 | _______ | ☐ |
| Bucket 1 (1-7 ngày) | 0 | _______ | ☐ |
| Bucket 2 (8-15 ngày) | 100,000,000 | _______ | ☐ |
| Bucket 3 (16-30 ngày) | 0 | _______ | ☐ |
| > 90 ngày | 0 | _______ | ☐ |
| Quá hạn tối đa (ngày) | 10 | _______ | ☐ |
| Số hóa đơn | 2 | _______ | ☐ |

**Calculation Logic:**
```
Invoice A:
- Due date = Today - 10 days
- Days overdue = (Today - (Today - 10)) = 10 days
- Falls into Bucket 2 (8-15 ngày) → 100,000,000

Invoice B:
- Due date = Today + 5 days
- Days overdue = (Today - (Today + 5)) = -5 days (negative = not overdue)
- Falls into Bucket Current → 50,000,000

Total = 150,000,000
Max overdue = 10 days
```

### UI Tests:
- ✅ Row decoration: Orange/Yellow if max_days_overdue > 0
- ✅ Row decoration: Red if max_days_overdue > 30
- ✅ Sum totals display correctly at bottom
- ✅ Filter "Quá hạn" shows only partners with overdue invoices
- ✅ Filter "Quá hạn > 30 ngày" works correctly

---

## TEST CASE 3: Drilldown to Invoices

### Steps:
1. On Viettel HN row in AR Aging Summary
2. Double-click or click "Xem hóa đơn" button (if available)
3. Should open list of 2 invoices

### Expected Results:

**Invoice List View:**
| Invoice | Date | Due Date | Amount Total | Amount Residual | Days Overdue | Pass/Fail |
|---------|------|----------|--------------|-----------------|--------------|-----------|
| INV-A | Today-15 | Today-10 | 100,000,000 | 100,000,000 | 10 | ☐ |
| INV-B | Today | Today+5 | 50,000,000 | 50,000,000 | -5 (or 0) | ☐ |

### UI Tests:
- ✅ Field `x_days_overdue` hiển thị đúng
- ✅ Không cho phép create invoice từ đây (create=False)
- ✅ Domain filter chỉ show invoices của Viettel HN với residual > 0

---

## TEST CASE 4: Sale Order AR Alerts

### Steps:
1. Find Sale Order linked to Invoice A + B (or create link manually)
2. Open Sale Order form
3. Check AR fields

### Expected Results:

| Field | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Còn phải thu (x_ar_residual_total) | 150,000,000 | _______ | ☐ |
| Quá hạn tối đa (x_ar_max_days_overdue) | 10 ngày | _______ | ☐ |
| Trạng thái công nợ (x_ar_status) | Quá hạn | _______ | ☐ |

**Status Logic:**
- `overdue` if max_days_overdue > 0 → ✅ Expected: "Quá hạn"
- `due_soon` if invoice due within 7 days and residual > 0
- `ok` if residual = 0

### UI Tests:
1. Add notebook page "Công nợ" on sale.order form (if not exists)
2. Display AR fields in group
3. Add button "Mở hóa đơn liên quan" → action_view_ar_invoices

**Button Test:**
- Click button
- Should show 2 invoices (Invoice A + B)
- Domain: out_invoice, posted, residual > 0, invoice_id in sale.order.invoice_ids

---

## TEST CASE 5: Phân quyền Sales Team

### Setup:
- User A: Sales User, owns Sale Order SO-001 → Invoice A + B
- User B: Sales User, owns different orders
- User C: Sales Manager

### Test Access:

**User A (Owner):**
1. Login as User A
2. Navigate: Sales → Công nợ → Tổng hợp tuổi nợ
3. **Expected**: See Viettel HN (if linked to SO-001 with user_id=User A)

**User B (Not owner):**
1. Login as User B
2. Navigate: Sales → Công nợ → Tổng hợp tuổi nợ
3. **Expected**: Do NOT see Viettel HN (if no sale orders for this customer)

**User C (Manager):**
1. Login as User C
2. Navigate: Sales → Công nợ → Tổng hợp tuổi nợ
3. **Expected**: See ALL customers (no restriction)

### Implementation Note:
Record rule on `dtx.ar.aging.summary`:
```python
domain = [
    '|',
    ('salesperson_id', '=', user.id),
    ('salesperson_id', '=', False),
]
# OR user has group_sale_manager
```

---

## TEST CASE 6: Pivot Analysis

### Steps:
1. Navigate: Sales → Công nợ → Tổng hợp tuổi nợ
2. Switch to Pivot view
3. Group by "Nhân viên bán hàng" (row)
4. Measures: Tổng công nợ, Bucket 1-3, > 90 ngày

### Expected Results:
- ✅ Pivot table shows salesperson rows
- ✅ Each bucket shows correct totals
- ✅ Can drill down to see partners per salesperson
- ✅ Export to Excel works

---

## TEST CASE 7: Edge Cases

### A) Invoice fully paid
1. Create payment for Invoice A → residual = 0
2. Refresh AR Aging Summary
3. **Expected**:
   - Total residual = 50,000,000 (only Invoice B)
   - Bucket 2 = 0
   - Bucket Current = 50,000,000

### B) No invoices
1. Check partner with no unpaid invoices
2. **Expected**: Partner NOT in AR Aging Summary (filtered out)

### C) Multiple companies
1. If multi-company setup
2. **Expected**: AR Aging Config per company
3. **Expected**: Summary filtered by company_id

---

## SQL VIEW VERIFICATION

### Manual Query Test:
```sql
-- Check if SQL view created
SELECT * FROM dtx_ar_aging_summary
WHERE partner_id = [Viettel HN partner_id];

-- Should return 1 row with correct buckets
```

### Expected Columns:
- id (ROW_NUMBER)
- partner_id
- company_id
- currency_id
- salesperson_id
- total_residual = 150,000,000
- invoice_count = 2
- bucket_current = 50,000,000
- bucket_1 = 0
- bucket_2 = 100,000,000
- bucket_3..5 = 0
- bucket_over = 0
- oldest_invoice_date = (Invoice A date)
- last_invoice_date = (Invoice B date)
- max_days_overdue = 10

---

## PASS CRITERIA

✅ **PASS** if:
1. Config form works, validates bucket sequence
2. SQL view returns correct data for test invoices
3. AR Aging Summary shows correct buckets
4. Drilldown to invoices works
5. Sale Order AR fields compute correctly
6. Sale Order AR status badge displays
7. Record rules enforce proper access control
8. Pivot view works
9. All UI decorations (colors) correct

❌ **FAIL** if:
- Incorrect bucket classification
- Wrong days_overdue calculation
- SQL view errors
- Record rules don't work
- Any computed field shows wrong value

---

## NOTES

- **Performance**: SQL view should be fast (<1s for 10k invoices)
- **Currency**: All amounts in company currency (VND)
- **Rounding**: Use currency rounding for amounts
- **Refresh**: Summary updates automatically when invoice state/residual changes (via SQL view)
- **Due Date**: If `invoice_date_due` is NULL, use `invoice_date`

---

**Tester**: _______________
**Date**: _______________
**Result**: ☐ PASS  ☐ FAIL
**Issues Found**: _______________________________________________
