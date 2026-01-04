# UAT Test Case: PAKD Excel Formulas

**Module**: dtx_sales_pakd_contract
**Version**: v1.2.0
**Test Date**: 2026-01-04
**Purpose**: Verify tất cả công thức tính toán PAKD khớp 100% với logic Excel

---

## TEST DATA

### Test Case: 2 dòng sản phẩm với VAT 10%

| STT | Sản phẩm | SL | Đơn giá HĐ | Đơn giá nhập | VAT |
|-----|----------|----|-----------:|------------:|----:|
| 1   | Product A | 7 | 27,500,000 | 22,000,000 | 10% |
| 2   | Product B | 1 | 30,000,000 | 18,000,000 | 10% |

---

## EXPECTED RESULTS

### Line Level Calculations

**Line 1 (Product A):**
```
qty = 7
contract_unit_price = 27,500,000
purchase_unit_price = 22,000,000
vat_percent = 10

1) contract_total_excl_vat = 7 × 27,500,000 = 192,500,000 ✓
2) contract_tax_amount = 192,500,000 × 10% = 19,250,000 ✓
3) contract_total_incl_vat = 192,500,000 + 19,250,000 = 211,750,000 ✓
4) purchase_total = 7 × 22,000,000 = 154,000,000 ✓ (NO VAT)
5) line_profit = 192,500,000 - 154,000,000 = 38,500,000 ✓
6) line_margin_percent = (38,500,000 / 154,000,000) × 100 = 25.00% ✓
```

**Line 2 (Product B):**
```
qty = 1
contract_unit_price = 30,000,000
purchase_unit_price = 18,000,000
vat_percent = 10

1) contract_total_excl_vat = 1 × 30,000,000 = 30,000,000 ✓
2) contract_tax_amount = 30,000,000 × 10% = 3,000,000 ✓
3) contract_total_incl_vat = 30,000,000 + 3,000,000 = 33,000,000 ✓
4) purchase_total = 1 × 18,000,000 = 18,000,000 ✓ (NO VAT)
5) line_profit = 30,000,000 - 18,000,000 = 12,000,000 ✓
6) line_margin_percent = (12,000,000 / 18,000,000) × 100 = 66.67% ✓
```

### Header Level Calculations

**Totals from Lines:**
```
total_purchase = 154,000,000 + 18,000,000 = 172,000,000 ✓
total_contract_untaxed = 192,500,000 + 30,000,000 = 222,500,000 ✓
total_contract_tax = 19,250,000 + 3,000,000 = 22,250,000 ✓
total_contract_total = 222,500,000 + 22,250,000 = 244,750,000 ✓
```

**Business Costs (với giả định tax_withheld_percent = 0, no support cost, no commission):**
```
tax_withheld_percent = 0%
tax_withheld_amount = 222,500,000 × 0% = 0 ✓
customer_support_cost = 0 ✓
referral_commission = 0 ✓
business_cost_total = 0 + 0 + 0 = 0 ✓

expected_profit = 222,500,000 - 172,000,000 - 0 = 50,500,000 ✓
expected_margin_percent = (50,500,000 / 222,500,000) × 100 = 22.70% ✓
```

---

## UAT EXECUTION STEPS

### Step 1: Create PAKD
1. Tạo Sale Order mới
2. Tạo PAKD từ Sales > PAKD > Create
3. Select Sale Order vừa tạo

### Step 2: Add Line 1
1. Click "Add a product"
2. Nhập data:
   - Product: Product A
   - Qty: 7
   - Contract Unit Price: 27,500,000
   - Purchase Unit Price: 22,000,000
   - VAT: 10%
3. **Verify computed fields**:
   - Tổng HĐ (chưa VAT): 192,500,000
   - Tổng VAT: 19,250,000
   - Tổng HĐ (có VAT): 211,750,000
   - Tổng nhập: 154,000,000
   - Lãi dòng: 38,500,000
   - Tỷ lệ lãi: 25.00%

### Step 3: Add Line 2
1. Click "Add a product"
2. Nhập data:
   - Product: Product B
   - Qty: 1
   - Contract Unit Price: 30,000,000
   - Purchase Unit Price: 18,000,000
   - VAT: 10%
3. **Verify computed fields**:
   - Tổng HĐ (chưa VAT): 30,000,000
   - Tổng VAT: 3,000,000
   - Tổng HĐ (có VAT): 33,000,000
   - Tổng nhập: 18,000,000
   - Lãi dòng: 12,000,000
   - Tỷ lệ lãi: 66.67%

### Step 4: Verify Header Totals
1. Chuyển sang tab "Tổng kết"
2. **Verify** các field:
   - Tổng giá nhập: 172,000,000
   - Tổng giá HĐ (chưa VAT): 222,500,000
   - Tổng VAT HĐ: 22,250,000
   - Tổng giá HĐ (có VAT): 244,750,000

### Step 5: Verify Business Costs
1. Trong tab "Tổng kết", section "Chi phí kinh doanh"
2. Nhập tax_withheld_percent = 0% (default)
3. **Verify**:
   - Thu thuế: 0
   - Tổng chi phí cho khách: 0
   - Hoa hồng người giới thiệu: 0
   - Tổng chi phí KD: 0

### Step 6: Verify Final Profit
1. Trong tab "Tổng kết", section "Lợi nhuận"
2. **Verify**:
   - Lợi nhuận dự kiến: 50,500,000
   - Tỷ lệ lãi: 22.70%

---

## TEST WITH BUSINESS COSTS

### Test Case 2: Thêm chi phí kinh doanh

**Input:**
```
tax_withheld_percent = 15%
customer_support_cost = 5,000,000
referral_commission = 2,000,000
```

**Expected:**
```
tax_withheld_amount = 222,500,000 × 15% = 33,375,000
business_cost_total = 33,375,000 + 5,000,000 + 2,000,000 = 40,375,000
expected_profit = 222,500,000 - 172,000,000 - 40,375,000 = 10,125,000
expected_margin_percent = (10,125,000 / 222,500,000) × 100 = 4.55%
```

**UAT Steps:**
1. Trong PAKD tab "Tổng kết"
2. Nhập:
   - Tỷ lệ thu thuế: 15
   - Tổng chi phí cho khách: 5,000,000
   - Hoa hồng người giới thiệu: 2,000,000
3. **Verify auto-computed**:
   - Thu thuế: 33,375,000
   - Tổng chi phí KD: 40,375,000
   - Lợi nhuận dự kiến: 10,125,000
   - Tỷ lệ lãi: 4.55%

---

## SECTION LINES TEST

### Test Case 3: Test Section/Note lines

**Steps:**
1. Tạo PAKD mới
2. Click "Add a section"
3. Nhập: "A. Phần mềm/License"
4. Click "Add a product" → Nhập Line 1 như trên
5. Click "Add a section"
6. Nhập: "B. Phần cứng/Hardware"
7. Click "Add a product" → Nhập Line 2 như trên

**Expected:**
- Section lines hiển thị đậm/bold
- Section lines KHÔNG tính vào totals
- Tổng vẫn đúng: 172M nhập, 222.5M HĐ, 50.5M lãi

---

## FORMULA SUMMARY

### dtx.pakd.line (PAKD Line)

| Field | Formula | Note |
|-------|---------|------|
| `estimate_total_excl_vat` | `qty × estimate_unit_excl_vat` | Tổng dự toán (chưa VAT) |
| `estimate_total_incl_vat` | `estimate_total_excl_vat × (1 + vat_percent/100)` | Tổng dự toán (có VAT) |
| `purchase_total` | `qty × purchase_unit_price` | **NO VAT** (được khấu trừ) |
| `sale_total` | `qty × sale_unit_price` | Tổng giá bán |
| `contract_total_excl_vat` | `qty × (contract_unit_price > 0 ? contract_unit_price : sale_unit_price)` | Tổng HĐ (chưa VAT) |
| `contract_tax_amount` | `contract_total_excl_vat × (vat_percent/100)` | VAT đầu ra |
| `contract_total_incl_vat` | `contract_total_excl_vat + contract_tax_amount` | Tổng HĐ (có VAT) |
| `line_profit` | `contract_total_excl_vat - purchase_total` | Lãi dòng |
| `line_margin_percent` | `(line_profit / purchase_total) × 100` | **Margin = Lãi/Chi phí** |
| `purchase_unit_price_from_list` | `vendor_list_price × (1 - discount_percent/100)` | Helper field |

### dtx.pakd (PAKD Header)

| Field | Formula | Note |
|-------|---------|------|
| `total_purchase` | `sum(line.purchase_total)` | Tổng nhập |
| `total_sale` | `sum(line.sale_total)` | Tổng bán |
| `total_contract_untaxed` | `sum(line.contract_total_excl_vat)` | Tổng HĐ (chưa VAT) |
| `total_contract_tax` | `sum(line.contract_tax_amount)` | Tổng VAT |
| `total_contract_total` | `total_contract_untaxed + total_contract_tax` | Tổng HĐ (có VAT) |
| `price_diff` | `total_sale - total_purchase` | Chênh lệch giá |
| `tax_withheld_amount` | `total_contract_untaxed × (tax_withheld_percent/100)` | Thu thuế |
| `business_cost_total` | `tax_withheld_amount + customer_support_cost + referral_commission` | Chi phí KD |
| `expected_profit` | `total_contract_untaxed - total_purchase - business_cost_total` | Lợi nhuận |
| `expected_margin_percent` | `(expected_profit / total_contract_untaxed) × 100` | Tỷ lệ lãi % |

---

## KEY DIFFERENCES FROM PREVIOUS VERSION

### ✅ Fixed Issues

1. **VAT Calculation**: Purchase total giờ **KHÔNG** bao gồm VAT (VAT đầu vào được khấu trừ)
2. **Margin Formula**: Đổi từ `profit/revenue` sang `profit/cost` theo Excel
3. **Section Lines**: Hỗ trợ section/note lines, excluded from totals
4. **Business Costs**: Thêm tax withheld, support cost, referral commission
5. **Excel Alignment**: Tất cả công thức giờ khớp 100% với Excel PAKD

### ✅ New Fields

**dtx.pakd.line:**
- `display_type`: Section/Note support
- `section_type`: License/Hardware/Deployment/Other grouping
- `estimate_unit_excl_vat`: Đơn giá dự toán
- `estimate_total_excl_vat`, `estimate_total_incl_vat`: Tổng dự toán
- `sale_total`: Tổng giá bán
- `purchase_unit_price_from_list`: Helper from vendor list + discount

**dtx.pakd:**
- `total_sale`: Tổng giá bán
- `price_diff`: Chênh lệch giá
- `tax_withheld_percent`, `tax_withheld_amount`: Thu thuế
- `customer_support_cost`: Chi phí hỗ trợ khách
- `referral_commission`: Hoa hồng
- `business_cost_total`: Tổng chi phí KD

---

## PASS CRITERIA

✅ **PASS** if all expected values match exactly:
- Line 1: 192.5M HĐ, 154M nhập, 38.5M lãi, 25.00% margin
- Line 2: 30M HĐ, 18M nhập, 12M lãi, 66.67% margin
- Header: 222.5M HĐ, 172M nhập, 50.5M lãi, 22.70% margin
- Section lines excluded from totals
- Business costs computed correctly

❌ **FAIL** if any computed value differs by more than 1 VND (rounding tolerance)

---

## NOTES

- Tất cả monetary fields sử dụng currency rounding
- Section/Note lines có display_type != False → all totals = 0
- VAT mapping: Tự động tìm account.tax theo vat_percent
- Onchange vendor_list_price + discount → auto-fill purchase_unit_price nếu trống

---

**Tester**: _______________
**Date**: _______________
**Result**: ☐ PASS  ☐ FAIL
**Notes**: _______________________________________________
