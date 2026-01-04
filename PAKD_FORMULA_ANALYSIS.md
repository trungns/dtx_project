# PAKD Formula Analysis - Excel vs Current Code

**Date**: 2026-01-04
**Issue**: PAKD summary totals don't match Excel PAKD template

---

## Excel Screenshot Analysis

From the Excel screenshot provided, the "Phần chi phí cho khách hàng/người giới thiệu" section shows:

### Current Issues Identified:

| Row # | Label (Excel) | Current Value | Expected Value | Status |
|-------|---------------|---------------|----------------|--------|
| 1 | Tổng tiền nhập (chi phí đầu vào) | ? | ? | Need data |
| 2 | Tổng tiền bán (chi phí thứ vỡ) | 148,000,000 | 156,000,000 | ❌ Wrong |
| 3 | Tổng tiền Hợp đồng (bao gồm chi phí ghi nêu cả) | 188,028,000 | 197,500,000 | ❌ Wrong |
| 4 | Chênh lệch giá | 40,028,000 | 41,500,000 | ❌ Wrong |
| 5 | Thu thuế 17% | 6,804,760 | 7,055,000.00 | ❌ Wrong |
| 6 | Tổng gối thêm | 33,223,240 | 31,145,000 | ❌ Wrong |
| 7 | Hoa hồng của VT Nghệ An 3% | ? | ? | ❌ Wrong |
| 8 | Tổng chi phí cho khách (6+7) | 40,623,240 (22%) | 41,845,000 | ❌ Wrong |
| 9 | Lợi nhuận | 65,718,519 | 35% = 41,845,000 | ❌ Wrong |

---

## Current Code Formula Implementation

### File: `models/dtx_pakd.py`

#### Header Totals (Lines 215-247):

```python
@api.depends('line_ids.purchase_total', 'line_ids.sale_total',
             'line_ids.contract_total_excl_vat', 'line_ids.contract_tax_amount',
             'line_ids.contract_total_incl_vat', 'line_ids.display_type')
def _compute_totals(self):
    for pakd in self:
        normal_lines = pakd.line_ids.filtered(lambda l: not l.display_type)

        # 1) Tổng giá nhập
        pakd.total_purchase = sum(normal_lines.mapped('purchase_total'))

        # 2) Tổng giá bán
        pakd.total_sale = sum(normal_lines.mapped('sale_total'))

        # 3) Tổng giá HĐ (chưa VAT)
        pakd.total_contract_untaxed = sum(normal_lines.mapped('contract_total_excl_vat'))

        # 4) Tổng VAT HĐ
        pakd.total_contract_tax = sum(normal_lines.mapped('contract_tax_amount'))

        # 5) Tổng giá HĐ (có VAT)
        pakd.total_contract_total = pakd.total_contract_untaxed + pakd.total_contract_tax

        # 6) Chênh lệch giá
        pakd.price_diff = pakd.total_sale - pakd.total_purchase
```

**Issues**:
- Line 2 calculation appears wrong based on screenshot
- Line 3 calculation appears wrong based on screenshot
- Need to verify what "Tổng tiền bán" means in Excel vs code

#### Business Costs (Lines 248-276):

```python
@api.depends('total_contract_untaxed', 'total_purchase',
             'tax_withheld_percent', 'customer_support_cost', 'referral_commission')
def _compute_business_costs(self):
    for pakd in self:
        currency = pakd.currency_id or pakd.company_id.currency_id

        # Thu thuế = total_contract_untaxed × (tax_withheld_percent/100)
        pakd.tax_withheld_amount = currency.round(
            pakd.total_contract_untaxed * (pakd.tax_withheld_percent / 100)
        )

        # Tổng chi phí KD
        pakd.business_cost_total = currency.round(
            pakd.tax_withheld_amount + pakd.customer_support_cost + pakd.referral_commission
        )

        # Lợi nhuận = Doanh thu - Chi phí mua - Chi phí KD
        pakd.expected_profit = currency.round(
            pakd.total_contract_untaxed - pakd.total_purchase - pakd.business_cost_total
        )

        # Tỷ lệ lãi %
        if pakd.total_contract_untaxed:
            pakd.expected_margin_percent = (pakd.expected_profit / pakd.total_contract_untaxed) * 100
        else:
            pakd.expected_margin_percent = 0.0
```

**Issues**:
- Row 5: "Thu thuế 17%" calculation wrong (6,804,760 vs 7,055,000)
- Row 6: "Tổng gối thêm" - this field doesn't exist in current code!
- Row 7: "Hoa hồng của VT Nghệ An 3%" - unclear mapping
- Row 8: "Tổng chi phí cho khách" - formula unclear
- Row 9: "Lợi nhuận" - calculation appears wrong

---

## Excel PAKD Template Formula Interpretation

Based on typical PAKD Excel structure and screenshot clues:

### Section: "Phần chi phí cho khách hàng/người giới thiệu"

**Row 1**: Tổng tiền nhập (chi phí đầu vào)
- Formula: `= SUM(purchase_total for all lines)`
- Maps to: `total_purchase` ✅

**Row 2**: Tổng tiền bán (chi phí thứ vỡ)
- **Current interpretation**: Sum of sale prices
- **Suspected issue**: May need to use `total_contract_untaxed` instead?
- Screenshot shows: 148M vs expected 156M
- **Hypothesis**: This might be sale price EXCLUDING certain items?

**Row 3**: Tổng tiền Hợp đồng (bao gồm chi phí ghi nêu cả)
- Formula: Should be `total_contract_total` (with VAT)
- Screenshot shows: 188,028,000 vs expected 197,500,000
- **This is critical**: The expected 197,500,000 matches UAT total!
- **Issue**: Current value 188M is too low

**Row 4**: Chênh lệch giá
- Formula: `= total_sale - total_purchase` ✅
- But if Row 2 is wrong, this will be wrong too

**Row 5**: Thu thuế X%
- Formula: `= price_diff × (tax_percent / 100)`
- Screenshot shows 17%, amount 7,055,000
- Verify: 41,500,000 × 17% = 7,055,000 ✅
- **Issue**: Current uses `total_contract_untaxed` as base, should use `price_diff`!

**Row 6**: Tổng gối thêm
- **Missing field in current code!**
- Formula (suspected): `= price_diff - tax_withheld_amount`
- Verify: 41,500,000 - 7,055,000 = 34,445,000 (close to 31,145,000)
- **Or**: This might be a manual input field for additional costs

**Row 7**: Hoa hồng của VT Nghệ An 3%
- Formula: `= total_contract_untaxed × 3%` or `= price_diff × 3%`?
- **Current mapping**: Might be `referral_commission`?
- Need to verify percentage calculation base

**Row 8**: Tổng chi phí cho khách (6+7)
- Formula: `= row6 + row7`
- Screenshot shows: 40,623,240 (22%) vs 41,845,000
- This is sum of "Tổng gối thêm" + "Hoa hồng"

**Row 9**: Lợi nhuận
- Formula: `= price_diff - total_business_costs`
- Or: `= total_contract_untaxed - total_purchase - total_business_costs`
- Screenshot shows 35% margin
- Verify: If total_contract_untaxed = 179.5M (excl VAT from 197.5M total)
  - Profit% = 35% suggests profit = 179.5M × 35% = 62.8M

---

## Critical Discovery

Looking at UAT data:
- **Expected Quotation Total**: 197,500,000 VND (with VAT)
- **Expected Contract Total (excl VAT)**: ~179,545,455 VND
- **Expected VAT**: ~17,954,545 VND

From Excel screenshot:
- **Row 3 shows**: 188,028,000 (current) vs 197,500,000 (expected)
- **Difference**: 9,472,000 VND

This suggests the `total_contract_total` calculation is WRONG!

### Hypothesis:
The issue is in how we compute contract totals from lines. Need to check `dtx_pakd_line.py`.

---

## Action Items

1. ✅ **Read dtx_pakd_line.py** to verify line-level formula calculations
2. ⚠️ **Verify line totals** match Excel line calculations
3. ⚠️ **Fix Row 5**: Thu thuế base should be `price_diff`, not `total_contract_untaxed`
4. ⚠️ **Add Row 6**: "Tổng gối thêm" field (might need new field)
5. ⚠️ **Clarify Row 7**: Hoa hồng percentage base
6. ⚠️ **Fix Row 8**: Tổng chi phí cho khách formula
7. ⚠️ **Fix Row 9**: Lợi nhuận calculation
8. ⚠️ **Update field labels** to match Excel exactly

---

## Next Steps

1. Ask user for Excel PAKD template file to see exact formulas
2. Or manually verify with user what each row represents
3. Read dtx_pakd_line.py to check line-level calculations
4. Create test case with known values to verify formulas
5. Update dtx_pakd.py formulas based on findings

---

**Status**: Analysis in progress - Need more information about Excel template structure
