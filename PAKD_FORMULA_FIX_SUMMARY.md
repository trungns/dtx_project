# PAKD Formula Fix Summary

**Date**: 2026-01-04
**Version**: 16.0.1.3.0
**Issue**: PAKD summary totals không khớp với Excel template

---

## Changes Made

### 1. New Fields Added to `dtx.pakd`

#### `cushion_amount` (Tổng gối thêm)
- **Type**: Monetary (computed, stored)
- **Formula**: `price_diff - tax_withheld_amount`
- **Purpose**: Số tiền còn lại sau khi trừ thu thuế từ chênh lệch giá

#### `referral_commission_percent` (Tỷ lệ hoa hồng %)
- **Type**: Float (manual input)
- **Default**: 0.0
- **Purpose**: Tỷ lệ % hoa hồng tính trên tổng tiền HĐ chưa VAT (thường 3%)

### 2. Modified Fields

#### `tax_withheld_amount` (Thu thuế)
- **OLD Formula**: `total_contract_untaxed × (tax_withheld_percent/100)`
- **NEW Formula**: `price_diff × (tax_withheld_percent/100)` ✅
- **Fix**: Base changed from total contract to price difference

#### `referral_commission` (Hoa hồng người giới thiệu)
- **OLD**: Manual input field
- **NEW**: Computed field ✅
- **Formula**: `total_contract_untaxed × (referral_commission_percent/100)`

#### `customer_support_cost` (Tổng chi phí cho khách)
- **OLD**: Manual input field
- **NEW**: Computed field ✅
- **Formula**: `cushion_amount + referral_commission`
- **Meaning**: Row 8 in Excel = Row 6 + Row 7

#### `business_cost_total` (Tổng chi phí KD)
- **OLD Formula**: `tax_withheld_amount + customer_support_cost + referral_commission`
- **NEW Formula**: `tax_withheld_amount + customer_support_cost` ✅
- **Fix**: Removed double-counting of referral_commission

#### `expected_profit` (Lợi nhuận)
- **OLD Formula**: `total_contract_untaxed - total_purchase - business_cost_total`
- **NEW Formula**: `price_diff - tax_withheld_amount - referral_commission` ✅
- **Fix**: Simplified formula matching Excel logic

### 3. Updated `_compute_business_costs` Method

**File**: [models/dtx_pakd.py:264-320](d:/trungns/dtx_project/odoo-dev/addons/dtx_sales_pakd_contract/models/dtx_pakd.py#L264-L320)

New dependency list:
```python
@api.depends('price_diff', 'total_contract_untaxed', 'total_purchase',
             'tax_withheld_percent', 'referral_commission_percent')
```

Formula implementation now matches Excel structure:
```python
# 5) Thu thuế = price_diff × (tax_withheld_percent/100)
pakd.tax_withheld_amount = currency.round(
    pakd.price_diff * (pakd.tax_withheld_percent / 100)
)

# 6) Tổng gối thêm = price_diff - tax_withheld_amount
pakd.cushion_amount = currency.round(
    pakd.price_diff - pakd.tax_withheld_amount
)

# 7) Hoa hồng = total_contract_untaxed × (referral_commission_percent/100)
pakd.referral_commission = currency.round(
    pakd.total_contract_untaxed * (pakd.referral_commission_percent / 100)
)

# 8) Tổng chi phí cho khách = Tổng gối thêm + Hoa hồng
pakd.customer_support_cost = currency.round(
    pakd.cushion_amount + pakd.referral_commission
)

# Tổng chi phí KD = Thu thuế + Tổng chi phí cho khách
pakd.business_cost_total = currency.round(
    pakd.tax_withheld_amount + pakd.customer_support_cost
)

# 9) Lợi nhuận = price_diff - thu thuế - hoa hồng
pakd.expected_profit = currency.round(
    pakd.price_diff - pakd.tax_withheld_amount - pakd.referral_commission
)
```

### 4. Updated View Labels

**File**: [views/dtx_pakd_views.xml:143-203](d:/trungns/dtx_project/odoo-dev/addons/dtx_sales_pakd_contract/views/dtx_pakd_views.xml#L143-L203)

**Tổng kết tab** now shows numbered rows matching Excel:

1. **Tổng tiền nhập (chi phí đầu vào)** = `total_purchase`
2. **Tổng tiền bán (chi phí thứ vỡ)** = `total_sale`
3. **Tổng tiền HĐ (bao gồm chi phí ghi nêu cả)** = `total_contract_total`
   - 3a. Tổng tiền HĐ (chưa VAT) = `total_contract_untaxed`
   - 3b. Tổng VAT = `total_contract_tax`

**Phần chi phí cho khách hàng/người giới thiệu** section:

4. **Chênh lệch giá** = `price_diff`
5. **Thu thuế X%** = `tax_withheld_percent` → `tax_withheld_amount`
6. **Tổng gối thêm** = `cushion_amount` (= 4 - 5)
7. **Hoa hồng Y%** = `referral_commission_percent` → `referral_commission`
8. **Tổng chi phí cho khách** = `customer_support_cost` (= 6 + 7)
9. **Lợi nhuận** = `expected_profit` (= 4 - 5 - 7)

---

## Excel Formula Verification

### Test Case: UAT Quỳ Châu (Expected Values)

Given:
- **Tổng tiền HĐ (chưa VAT)**: 179,545,455 VND
- **Tổng VAT**: 17,954,545 VND
- **Tổng tiền HĐ (có VAT)**: 197,500,000 VND
- **Tổng tiền nhập**: Assume 156,000,000 VND
- **Tổng tiền bán**: 156,000,000 VND (from screenshot)
- **Chênh lệch giá**: 41,500,000 VND (from screenshot estimate)
- **Thu thuế 17%**: 41,500,000 × 17% = **7,055,000 VND** ✅ (matches Excel)
- **Tổng gối thêm**: 41,500,000 - 7,055,000 = **34,445,000 VND**
- **Hoa hồng 3%**: 179,545,455 × 3% = **5,386,364 VND**
- **Tổng chi phí cho khách**: 34,445,000 + 5,386,364 = **39,831,364 VND**
- **Lợi nhuận**: 41,500,000 - 7,055,000 - 5,386,364 = **29,058,636 VND**
- **Tỷ lệ lãi**: 29,058,636 / 179,545,455 = **16.19%**

**Note**: Actual values depend on real purchase prices entered by user.

---

## Breaking Changes

⚠️ **WARNING**: This is a breaking change for existing PAKD records!

### Migration Impact

1. **`referral_commission`**: Changed from manual input to computed
   - Old manual values will be overwritten
   - Users must now use `referral_commission_percent` field

2. **`customer_support_cost`**: Changed from manual input to computed
   - Old manual values will be overwritten
   - Now auto-computed as sum of cushion + commission

3. **Formula changes**: All business cost calculations will recalculate

### Migration Strategy

**Option A - Accept Data Loss** (Recommended for development):
- Upgrade module directly
- Old manual values will be lost
- Formulas will compute correctly based on new logic

**Option B - Data Migration** (For production):
```python
# Before upgrade: save old values
UPDATE dtx_pakd
SET note = CONCAT(note,
    '\nOld referral_commission: ', referral_commission,
    '\nOld customer_support_cost: ', customer_support_cost
);

# After upgrade: restore if needed by creating custom manual fields
```

---

## Upgrade Steps

### 1. Stop Odoo
```bash
cd odoo-dev
docker-compose stop odoo
```

### 2. Upgrade Module
```bash
docker-compose run --rm odoo odoo -d odoo -u dtx_sales_pakd_contract --stop-after-init
```

### 3. Restart Odoo
```bash
docker-compose start odoo
```

### 4. Verify Changes

1. Navigate to existing PAKD (if any)
2. Check that new fields appear:
   - `cushion_amount` (Tổng gối thêm)
   - `referral_commission_percent` (Tỷ lệ hoa hồng %)
3. Verify labels match Excel template
4. Test formulas by creating new PAKD

### 5. Create Test PAKD

Follow [MANUAL_UAT_GUIDE.md](d:/trungns/dtx_project/odoo-dev/addons/dtx_sales_pakd_contract/MANUAL_UAT_GUIDE.md):
1. Create quotation (197.5M total)
2. Create PAKD from quotation
3. Enter purchase prices
4. Enter `tax_withheld_percent` = 17
5. Enter `referral_commission_percent` = 3
6. Verify Row 5: Thu thuế = 7,055,000 (if price_diff = 41,500,000)
7. Verify Row 6: Tổng gối thêm computed correctly
8. Verify Row 7: Hoa hồng computed correctly
9. Verify Row 8: Tổng chi phí = Row 6 + Row 7
10. Verify Row 9: Lợi nhuận computed correctly

---

## Files Changed

1. ✅ [models/dtx_pakd.py](d:/trungns/dtx_project/odoo-dev/addons/dtx_sales_pakd_contract/models/dtx_pakd.py)
   - Added: `cushion_amount`, `referral_commission_percent` fields
   - Modified: `tax_withheld_amount`, `referral_commission`, `customer_support_cost` (now computed)
   - Updated: `_compute_business_costs()` method with correct formulas

2. ✅ [views/dtx_pakd_views.xml](d:/trungns/dtx_project/odoo-dev/addons/dtx_sales_pakd_contract/views/dtx_pakd_views.xml)
   - Restructured "Tổng kết" tab
   - Added numbered labels matching Excel (1-9)
   - Added new fields to form view
   - Improved field descriptions

3. ✅ [__manifest__.py](d:/trungns/dtx_project/odoo-dev/addons/dtx_sales_pakd_contract/__manifest__.py)
   - Version bump: 16.0.1.1.0 → 16.0.1.3.0
   - Added version 1.3.0 changelog

---

## Testing Checklist

- [ ] Module upgrades without errors
- [ ] New fields appear in PAKD form
- [ ] Labels match Excel template
- [ ] Create quotation with 9 lines (197.5M total)
- [ ] Create PAKD from quotation
- [ ] Enter purchase prices
- [ ] Enter tax_withheld_percent (e.g., 17%)
- [ ] Enter referral_commission_percent (e.g., 3%)
- [ ] Verify Row 5: Thu thuế calculation (base = price_diff) ✅
- [ ] Verify Row 6: Tổng gối thêm = price_diff - thu thuế ✅
- [ ] Verify Row 7: Hoa hồng = contract_total × % ✅
- [ ] Verify Row 8: Tổng chi phí = gối thêm + hoa hồng ✅
- [ ] Verify Row 9: Lợi nhuận matches Excel ✅
- [ ] Run automated tests (if available)

---

## Known Issues

### Issue: PAKD Creation Error (uom_id)
**Status**: Under investigation
**Workaround**: Ensure quotation has valid product_uom on all lines

### Issue: Total doesn't match 197.5M
**Possible causes**:
1. Missing VAT configuration (0%, 10%)
2. Wrong product prices
3. Missing lines (should have 9 lines)

**Solution**: Follow [MANUAL_UAT_GUIDE.md](d:/trungns/dtx_project/odoo-dev/addons/dtx_sales_pakd_contract/MANUAL_UAT_GUIDE.md) Step 1-2

---

## Next Steps

1. ✅ Fix formulas (DONE)
2. ✅ Update labels (DONE)
3. ⏳ Upgrade module
4. ⏳ Test with real data
5. ⏳ Verify calculations match Excel
6. ⏳ Update automated tests to reflect new formulas
7. ⏳ Document for users

---

**Status**: Ready for upgrade
**Risk Level**: Medium (breaking changes to formula fields)
**Recommended**: Test in development environment first
