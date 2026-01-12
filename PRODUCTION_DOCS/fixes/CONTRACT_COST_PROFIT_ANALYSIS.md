# Contract Cost - Detailed Profit Analysis Enhancement

## Overview

Enhanced Contract Cost sheet to provide detailed line-by-line profit tracking with auto-populated prices from Purchase Orders and Sales Orders, similar to PAKD but showing **actual** costs and revenues.

## Problem Statement

**Original Contract Cost sheet** was too simple:
- Only tracked: planned cost vs actual cost
- No visibility into sales price or profit
- All costs required manual entry
- No automated data from PO/SO

**User request:**
> "Tôi muốn ở sheet này giống y như PAKD nhưng Đơn giá nhập được lấy tự động từ giá mua các sản phẩm. Giá bán lấy thực tế thì lấy tự động từ báo giá nhưng cho phép sửa và thêm line"

**Professional management perspective:**
- Need complete cost visibility per line
- Auto-populate from PO (trustworthy, readonly)
- Allow manual input for non-PO costs (license, services, misc)
- Show profit/margin for decision making
- Visual indicators (colors) for quick assessment

## Solution

### New Fields

#### Purchase Cost Fields
```python
purchase_unit_price          # Auto from PO (readonly, blue background)
purchase_unit_price_manual   # Manual input for lines without PO
has_purchase_order          # Boolean flag (auto-computed)
```

#### Sale Price Fields
```python
sale_unit_price  # Auto from SO, but editable
```

#### Profit Fields
```python
total_purchase    # Qty × Purchase price
total_sale        # Qty × Sale price
profit            # Total sale - Total purchase
margin_percent    # (Profit / Total sale) × 100%
```

### Auto-Population Logic

#### 1. Purchase Price (from Purchase Orders)

**Path:** `sale.order → procurement.group → stock.move → purchase.order.line`

```python
@api.depends('product_id', 'qty', 'sale_order_id.order_line...')
def _compute_purchase_price(self):
    # Find procurement group for this SO
    procurement_group = env['procurement.group'].search([
        ('sale_id', '=', self.sale_order_id.id)
    ])

    # Find stock moves for this product
    stock_moves = env['stock.move'].search([
        ('group_id', '=', procurement_group.id),
        ('product_id', '=', self.product_id.id),
    ])

    # Get PO lines
    po_lines = stock_moves.mapped('purchase_line_id')

    if po_lines:
        # Use latest PO price
        self.purchase_unit_price = po_lines[-1].price_unit
        self.has_purchase_order = True
```

**Result:**
- Lines WITH PO: Auto-fill `purchase_unit_price` (readonly, blue)
- Lines WITHOUT PO: Use `purchase_unit_price_manual` (editable)

#### 2. Sale Price (from Sale Orders)

**Path:** `sale.order.line → price_unit`

```python
@api.depends('product_id', 'sale_order_id.order_line...')
def _compute_sale_price(self):
    # Find SO line with matching product
    so_line = self.sale_order_id.order_line.filtered(
        lambda l: l.product_id == self.product_id
    )

    if so_line:
        self.sale_unit_price = so_line[0].price_unit
```

**Result:**
- Auto-filled from SO
- **Editable** (readonly=False) for manual adjustments

#### 3. Profit Calculation

```python
@api.depends('qty', 'purchase_unit_price', 'purchase_unit_price_manual',
             'sale_unit_price', 'has_purchase_order')
def _compute_profit(self):
    # Effective purchase price
    if self.has_purchase_order:
        effective_purchase = self.purchase_unit_price
    else:
        effective_purchase = self.purchase_unit_price_manual

    # Totals
    self.total_purchase = self.qty * effective_purchase
    self.total_sale = self.qty * self.sale_unit_price

    # Profit
    self.profit = self.total_sale - self.total_purchase

    # Margin%
    if self.total_sale != 0:
        self.margin_percent = (self.profit / self.total_sale) * 100
```

## UI Changes

### Tree View (Contract Cost Lines)

**Before:**
```
| Product | Qty | Planned Cost | Actual Cost | Total | Variance |
```

**After:**
```
| Product | Qty | Purchase Price (PO) | Purchase Manual | Sale Price | Total Purchase | Total Sale | Profit | Margin% |
```

**Column Details:**

| Column | Auto/Manual | Readonly | Color | Purpose |
|--------|-------------|----------|-------|---------|
| Purchase Price (PO) | Auto from PO | Yes | 🔵 Blue | Trustworthy cost from PO |
| Purchase Manual | Manual | No* | White | For license, misc costs |
| Sale Price | Auto from SO | No | White | Revenue per unit (editable) |
| Total Purchase | Computed | Yes | White | Total cost |
| Total Sale | Computed | Yes | White | Total revenue |
| Profit | Computed | Yes | 🟢 Green / 🔴 Red | Net profit |
| Margin% | Computed | Yes | White | Profitability ratio |

*Purchase Manual is readonly when PO exists (has_purchase_order=True)

### Row Color Coding

```xml
<tree decoration-success="profit > 0 and cost_type=='planned'"
      decoration-warning="profit < 0">
```

- 🟢 **Green row**: Profitable lines (profit > 0)
- 🟠 **Orange row**: Loss lines (profit < 0)
- 🔴 **Red row**: Additional costs (cost_type='additional')

### Form View

**Grouped sections:**

1. **Giá mua (Purchase)**
   - Từ PAKD: `planned_unit_cost` (readonly)
   - Thực tế: `purchase_unit_price` (readonly, blue) OR `purchase_unit_price_manual` (editable)

2. **Giá bán & Lợi nhuận**
   - Doanh thu: `sale_unit_price`, `total_sale`
   - Chi phí & Lợi nhuận: `total_purchase`, `profit`, `margin_percent`

3. **Legacy (backward compatibility)** - Hidden by default
   - Old fields for data migration

## Use Cases

### Case 1: Hardware Product with PO

**Product:** Touch Screen DTX-10

**Flow:**
1. Create SO (SO0158) with Touch Screen × 2 @ 5,000,000 VND
2. Create PO (PO0089) to purchase Touch Screen × 2 @ 3,500,000 VND
3. Import PAKD costs → Contract Cost created

**Contract Cost Line:**
```
Product: Touch Screen DTX-10
Qty: 2
Purchase Price (PO): 3,500,000 (auto, blue, readonly)
Purchase Manual: - (readonly because has_purchase_order=True)
Sale Price: 5,000,000 (auto from SO, editable)

Total Purchase: 7,000,000
Total Sale: 10,000,000
Profit: 3,000,000 (green)
Margin%: 30%
```

**Visual:** Green row, blue background on purchase price

### Case 2: Software License (No PO)

**Product:** Microsoft Office 365 License

**Flow:**
1. Create SO with Office 365 × 10 @ 200,000 VND
2. No PO created (purchased via credit card, misc expense)
3. Manually add contract cost line

**Contract Cost Line:**
```
Product: Office 365 License
Qty: 10
Purchase Price (PO): - (no PO)
Purchase Manual: 150,000 (manual entry, editable)
Sale Price: 200,000 (auto from SO, editable)

Total Purchase: 1,500,000
Total Sale: 2,000,000
Profit: 500,000 (green)
Margin%: 25%
```

**Visual:** Green row, white background on purchase manual

### Case 3: Misc Cost (Additional Line)

**Product:** Installation Service

**Flow:**
1. Not in PAKD, manually add as additional cost
2. No PO, no SO line
3. Full manual entry

**Contract Cost Line:**
```
Product: Installation Service
Qty: 1
Purchase Price (PO): - (no PO)
Purchase Manual: 2,000,000 (manual entry)
Sale Price: 3,000,000 (manual entry)
Cost Type: Phát sinh (additional)

Total Purchase: 2,000,000
Total Sale: 3,000,000
Profit: 1,000,000 (green)
Margin%: 33.3%
```

**Visual:** Red row (additional cost), all fields manual

## Files Changed

### 1. [models/contract_cost.py](odoo-dev/addons/dtx_sales_pakd_contract/models/contract_cost.py)

**New fields:** Lines 52-120
- Purchase cost fields (55-78)
- Sale price fields (80-89)
- Profit fields (91-120)

**Compute methods:** Lines 175-273
- `_compute_purchase_price()` - Auto from PO
- `_compute_sale_price()` - Auto from SO
- `_compute_profit()` - Profit & margin calculation

### 2. [views/contract_cost_views.xml](odoo-dev/addons/dtx_sales_pakd_contract/views/contract_cost_views.xml)

**Tree view:** Lines 3-52
- New columns with profit analysis
- Color decorations
- Optional legacy fields

**Form view:** Lines 54-119
- Grouped sections for purchase/sale/profit
- Conditional visibility based on has_purchase_order

### 3. [static/src/css/pakd_view.css](odoo-dev/addons/dtx_sales_pakd_contract/static/src/css/pakd_view.css)

**Added:** Lines 53-67
- Blue background for readonly PO price
- Bold font for profit fields

### 4. [__manifest__.py](odoo-dev/addons/dtx_sales_pakd_contract/__manifest__.py)

**Version:** 1.4.0 → 1.5.0

**Changelog:** Lines 28-35

## Migration Notes

**Existing contract costs:**

After upgrade:
- `actual_unit_cost` → `purchase_unit_price_manual` (for backward compatibility)
- `sale_unit_price` will be auto-computed from SO
- Profit fields will auto-compute

**No data loss:** Legacy fields retained for reference

## Professional Management Benefits

### 1. Complete Cost Visibility

**Before:**
- "What's our actual profit on this contract?"
- Answer: Unknown, need manual calculation

**After:**
- See profit per line + total
- Margin% for each product
- Instant overview of profitability

### 2. Trustworthy Data

**Problem:** Manual entry = human error

**Solution:**
- Purchase price auto from PO (blue, readonly) = trustworthy
- Sale price auto from SO = accurate
- Only non-PO costs need manual entry

### 3. Decision Support

**Use case:** Customer requests discount

**Analysis:**
```
Current margin: 25%
Requested discount: 10%
New margin: 15% (still acceptable)
Decision: APPROVED
```

**Without this feature:** Need to calculate manually, slow response

### 4. Cost Control

**Identify issues:**
- Red rows = losing money
- Low margin% = review pricing
- High manual costs = investigate

**Example:**
```
Touch Screen: Profit = -500,000 (RED)
→ Investigation: PO price increased, SO price not updated
→ Action: Request change order or accept loss
```

## How to Test

### 1. Restart & Upgrade
```bash
docker exec dtx_odoo16 odoo -u dtx_sales_pakd_contract -d dtx_dev --stop-after-init
docker restart dtx_odoo16
```

### 2. Test Scenario: SO0158 (Xã Vân Hà)

**Step 1:** Open SO0158
- Sales > Orders > SO0158

**Step 2:** Check existing POs
- Procurement > View linked Purchase Orders
- Note products and prices

**Step 3:** Import PAKD costs
- Click "Import chi phí từ PAKD"
- Go to "Chi phí hợp đồng" tab

**Expected result:**
- Products with PO: `purchase_unit_price` filled (blue background)
- `sale_unit_price` auto from SO
- Profit & margin calculated
- Green rows for profitable items

**Step 4:** Add manual line
- Click "Add a line"
- Product: Office 365 (no PO)
- Fill `purchase_unit_price_manual`: 150,000
- `sale_unit_price` auto-fills or manual: 200,000
- Check profit calculation

**Step 5:** Verify totals
- Sum of "Tổng mua"
- Sum of "Tổng bán"
- Sum of "Lợi nhuận"
- Overall margin%

## Technical Details

### Why Procurement Group?

**Question:** Why not directly link SO to PO?

**Answer:** Odoo standard flow:
```
Sale Order
  └─ Procurement Group (delivery)
     └─ Stock Move (product movement)
        └─ Purchase Order Line (auto-created by reordering rules)
```

**Benefit:**
- Works with Odoo's automated procurement
- Handles MTO (Make to Order) scenarios
- Supports subcontracting

### Why store=True?

**Performance:**
```python
purchase_unit_price = fields.Monetary(
    compute='_compute_purchase_price',
    store=True,  # ← Important!
)
```

**Reason:**
- Avoid recomputing on every read
- Enable searching/grouping
- Performance with 1000+ lines

### Why readonly=False on sale_unit_price?

**Flexibility:**
- Auto-fill from SO = convenience
- Editable = handle special cases
- Example: "Give 5% discount on this item only"

## Comparison with PAKD

| Feature | PAKD | Contract Cost |
|---------|------|---------------|
| **Purpose** | Planning | Actual tracking |
| **Purchase Price** | Estimated | Auto from PO |
| **Sale Price** | Quoted | Auto from SO |
| **Profit** | Planned | Actual |
| **When** | Before sale | After PO created |
| **Editable** | Pre-approval | Always (for manual costs) |

**Workflow:**
1. Create PAKD → Plan profit
2. Get approval → Convert to SO
3. Create POs → Actual costs known
4. Import Contract Costs → Track actual profit
5. Compare PAKD vs Contract Cost → Variance analysis

## Summary

✅ **Enhanced:** Contract Cost with detailed profit analysis per line
✅ **Auto:** Purchase price from PO (blue, readonly)
✅ **Auto:** Sale price from SO (editable)
✅ **Manual:** Support for non-PO costs (license, misc)
✅ **Profit:** Calculation and margin% per line
✅ **Visual:** Color coding for quick assessment
✅ **Professional:** Management-grade cost visibility
✅ **Version:** 1.4.0 → 1.5.0

Now managers can make data-driven decisions with complete cost visibility! 📊
