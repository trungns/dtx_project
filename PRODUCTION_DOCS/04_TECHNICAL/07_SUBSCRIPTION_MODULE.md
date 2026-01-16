# Subscription Module - Technical Documentation

**Modules:** dtx_product_standards v1.3.0, dtx_sales_pakd_contract v1.6.0
**Date:** 2026-01-14
**For:** Developers, System Architects

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Model](#data-model)
4. [Business Logic](#business-logic)
5. [Views and UI](#views-and-ui)
6. [Security](#security)
7. [Wizards](#wizards)
8. [Integration Points](#integration-points)
9. [Database Schema](#database-schema)
10. [API Reference](#api-reference)
11. [Testing](#testing)
12. [Migration](#migration)
13. [Performance](#performance)
14. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose

Implement prepaid subscription contract management for SaaS products (DiHub, SeQMS) with:
- Product type: `subscription` (separate from `service`)
- Common product metadata: Part Number, Country of Origin (ALL products)
- Subscription fields on SO lines: Device Count, Months, Start/End dates
- Auto-calculation: Quantity = Devices × Months, End Date = Start + Months
- Renewal wizard for easy contract renewal

### Design Principles

1. **Hybrid Approach**: Custom fields only for subscriptions, existing products unchanged
2. **Zero Database Migration**: New fields with NULL defaults, backward compatible
3. **Odoo Standards**: Use standard Odoo patterns (related fields, computed fields, onchange)
4. **User-Friendly**: Auto-calculations reduce manual work and errors
5. **Extensible**: Easy to add new subscription types or features

### Modules Modified

**1. dtx_product_standards (v1.2.0 → v1.3.0)**
- Add 'subscription' to x_dtx_type selection
- Add common product metadata (Part Number, Country of Origin)
- Add subscription-specific fields (base price, default months)

**2. dtx_sales_pakd_contract (v1.5.0 → v1.6.0)**
- Extend sale.order.line with subscription fields
- Add x_has_subscription_lines to sale.order
- Create renew subscription wizard
- Update views and security

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    dtx_product_standards v1.3.0                 │
├─────────────────────────────────────────────────────────────────┤
│ product.template                                                │
│  ├── x_dtx_type (+ 'subscription' option)                      │
│  ├── x_part_number (common for ALL products)                   │
│  ├── x_country_of_origin (common for ALL products)             │
│  ├── x_subscription_base_price (subscription only)             │
│  └── x_subscription_default_months (subscription only)         │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ depends
                              │
┌─────────────────────────────────────────────────────────────────┐
│                 dtx_sales_pakd_contract v1.6.0                  │
├─────────────────────────────────────────────────────────────────┤
│ sale.order                                                      │
│  └── x_has_subscription_lines (compute)                        │
│                                                                 │
│ sale.order.line                                                 │
│  ├── x_part_number (related)                                   │
│  ├── x_country_of_origin (related)                             │
│  ├── x_is_subscription (compute)                               │
│  ├── x_device_count (subscription only)                        │
│  ├── x_months (subscription only)                              │
│  ├── x_subscription_start (subscription only)                  │
│  └── x_subscription_end (subscription only)                    │
│                                                                 │
│ dtx.renew.subscription.wizard                                   │
│  ├── order_id (original SO)                                    │
│  ├── original_start_date (compute)                             │
│  ├── original_end_date (compute)                               │
│  ├── new_start_date                                            │
│  ├── new_months                                                │
│  ├── new_end_date (compute)                                    │
│  └── action_renew() (creates new SO)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Product Setup Flow:
1. User creates product with DTX Type = 'subscription'
2. Fills Part Number, Country of Origin (common fields)
3. Fills Base Price, Default Months (subscription fields)
4. Saves → Ready for quotation

Quotation Creation Flow:
1. User creates Sale Order
2. Adds subscription product line
3. @api.onchange('product_id') → Auto-fills price, default months
4. User enters Device Count, Months, Start Date
5. @api.onchange('x_device_count', 'x_months') → Auto-calc Quantity
6. @api.onchange('x_subscription_start', 'x_months') → Auto-calc End Date
7. User confirms SO → Standard invoice workflow

Renewal Flow:
1. User opens confirmed SO with subscription lines
2. Clicks "Renew Contract" button
3. Wizard opens with original dates (compute from SO lines)
4. new_start_date defaults to original_end + 1 day
5. User adjusts new_months if needed
6. new_end_date auto-calculates
7. Clicks "Create Renewal" → Wizard.action_renew()
8. System copies SO, updates dates, recalcs quantity
9. Links original and new SO via chatter
10. Returns to new SO in draft state
```

---

## Data Model

### Module: dtx_product_standards

#### Model: product.template

**File:** `odoo-dev/addons/dtx_product_standards/models/product_template.py`

**New/Modified Fields:**

```python
# Modified: Added 'subscription' option
x_dtx_type = fields.Selection(
    selection=[
        ('device_serialized', 'Thiết bị quản lý theo Serial'),
        ('component_untracked', 'Linh kiện / vật tư tiêu hao (không quản lý Serial)'),
        ('finished_kiosk', 'Kiosk / Thiết bị hoàn chỉnh'),
        ('service', 'Dịch vụ (không quản lý kho)'),
        ('subscription', 'Subscription / License theo tháng'),  # NEW
    ],
    string='DTX Product Type',
    required=True,
    default='device_serialized',
    tracking=True,
    help='Loại sản phẩm theo chuẩn DTX. Quyết định workflow quản lý (serial, kho, subscription).',
)

# NEW: Common product metadata (ALL products)
x_part_number = fields.Char(
    string='Part Number / Mã sản phẩm',
    help='Mã sản phẩm theo nhà cung cấp hoặc mã nội bộ DTX. Hiển thị trên quotation/invoice.',
    tracking=True,
)

x_country_of_origin = fields.Char(
    string='Country of Origin / Xuất xứ',
    help='Nước sản xuất (China, USA, Vietnam, etc.). Dùng cho customs và báo cáo.',
    tracking=True,
)

# NEW: Subscription-specific metadata
x_subscription_base_price = fields.Float(
    string='Base Price / Device / Month',
    help='Giá cơ bản cho 1 thiết bị trong 1 tháng (VNĐ, trước VAT). '
         'Chỉ áp dụng cho subscription products. '
         'Total = Device Count × Months × Base Price.',
    digits='Product Price',
)

x_subscription_default_months = fields.Integer(
    string='Default Duration (Months)',
    default=12,
    help='Số tháng mặc định khi tạo quotation. User có thể thay đổi trên SO line.',
)
```

**Field Characteristics:**

| Field | Type | Stored | Computed | Tracking | Required |
|-------|------|--------|----------|----------|----------|
| x_dtx_type | Selection | ✅ | ❌ | ✅ | ✅ |
| x_part_number | Char | ✅ | ❌ | ✅ | ❌ |
| x_country_of_origin | Char | ✅ | ❌ | ✅ | ❌ |
| x_subscription_base_price | Float | ✅ | ❌ | ❌ | ❌ |
| x_subscription_default_months | Integer | ✅ | ❌ | ❌ | ❌ |

**Database Columns:**

```sql
ALTER TABLE product_template
ADD COLUMN x_part_number VARCHAR,
ADD COLUMN x_country_of_origin VARCHAR,
ADD COLUMN x_subscription_base_price NUMERIC,
ADD COLUMN x_subscription_default_months INTEGER DEFAULT 12;

-- Note: Odoo ORM handles this automatically during module upgrade
-- No manual migration needed (NULL defaults are safe)
```

---

### Module: dtx_sales_pakd_contract

#### Model: sale.order

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/models/sale_order.py`

**New Fields:**

```python
x_has_subscription_lines = fields.Boolean(
    string='Has Subscription Lines',
    compute='_compute_has_subscription_lines',
    help='Check if this SO has any subscription product lines. '
         'Used to control "Renew Contract" button visibility.',
)

@api.depends('order_line.x_is_subscription')
def _compute_has_subscription_lines(self):
    """Check if SO has any subscription product lines"""
    for order in self:
        order.x_has_subscription_lines = any(order.order_line.mapped('x_is_subscription'))
```

**Field Characteristics:**

| Field | Type | Stored | Computed | Depends |
|-------|------|--------|----------|---------|
| x_has_subscription_lines | Boolean | ❌ | ✅ | order_line.x_is_subscription |

**Purpose:**
- Controls visibility of "Renew Contract" button
- Button shows only when: `state='sale' AND x_has_subscription_lines=True`

---

#### Model: sale.order.line

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/models/sale_order_line.py` (NEW)

**All Fields:**

```python
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # ==========================================
    # PRODUCT METADATA (visible for ALL products)
    # ==========================================
    x_part_number = fields.Char(
        related='product_id.product_tmpl_id.x_part_number',
        string='Part Number',
        readonly=True,
        store=False,  # Not stored - read from product on demand
    )

    x_country_of_origin = fields.Char(
        related='product_id.product_tmpl_id.x_country_of_origin',
        string='Country of Origin',
        readonly=True,
        store=False,
    )

    # ==========================================
    # SUBSCRIPTION FIELDS (only for subscription products)
    # ==========================================
    x_is_subscription = fields.Boolean(
        compute='_compute_is_subscription',
        store=True,
        string='Is Subscription Line',
        help='Auto-set to True if product DTX Type = subscription',
    )

    x_device_count = fields.Integer(
        string='Số thiết bị / Device Count',
        help='Number of devices for subscription. Used to calculate Quantity = Devices × Months.',
    )

    x_months = fields.Integer(
        string='Thời gian (Tháng) / Months',
        help='Subscription duration in months. Used to calculate Quantity and End Date.',
    )

    x_subscription_start = fields.Date(
        string='Ngày bắt đầu / Start Date',
        help='Subscription start date. Used to calculate End Date = Start + Months.',
    )

    x_subscription_end = fields.Date(
        string='Ngày kết thúc / End Date',
        help='Subscription end date. Auto-calculated from Start + Months.',
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('product_id', 'product_id.product_tmpl_id.x_dtx_type')
    def _compute_is_subscription(self):
        """Check if this line is a subscription product"""
        for line in self:
            line.x_is_subscription = (
                line.product_id
                and line.product_id.product_tmpl_id.x_dtx_type == 'subscription'
            )

    @api.onchange('product_id')
    def _onchange_product_subscription(self):
        """Auto-fill subscription defaults from product"""
        if self.product_id and self.product_id.product_tmpl_id.x_dtx_type == 'subscription':
            # Set default months from product
            self.x_months = self.product_id.product_tmpl_id.x_subscription_default_months or 12
            # Set price_unit from subscription_base_price if available
            if self.product_id.product_tmpl_id.x_subscription_base_price:
                self.price_unit = self.product_id.product_tmpl_id.x_subscription_base_price

    @api.onchange('x_device_count', 'x_months')
    def _onchange_subscription_quantity(self):
        """Auto-calculate quantity = devices × months"""
        if self.x_is_subscription and self.x_device_count and self.x_months:
            self.product_uom_qty = self.x_device_count * self.x_months

    @api.onchange('x_subscription_start', 'x_months')
    def _onchange_subscription_dates(self):
        """Auto-calculate end date from start + months"""
        if self.x_subscription_start and self.x_months:
            # relativedelta handles month-end dates correctly
            # e.g., 2025-12-01 + 9 months = 2026-08-31 (not 2026-09-01)
            self.x_subscription_end = self.x_subscription_start + relativedelta(months=self.x_months)
```

**Field Characteristics:**

| Field | Type | Stored | Computed | Related | Readonly |
|-------|------|--------|----------|---------|----------|
| x_part_number | Char | ❌ | ❌ | ✅ | ✅ |
| x_country_of_origin | Char | ❌ | ❌ | ✅ | ✅ |
| x_is_subscription | Boolean | ✅ | ✅ | ❌ | ✅ |
| x_device_count | Integer | ✅ | ❌ | ❌ | ❌ |
| x_months | Integer | ✅ | ❌ | ❌ | ❌ |
| x_subscription_start | Date | ✅ | ❌ | ❌ | ❌ |
| x_subscription_end | Date | ✅ | ❌ | ❌ | ❌ |

**Database Columns:**

```sql
ALTER TABLE sale_order_line
ADD COLUMN x_is_subscription BOOLEAN,
ADD COLUMN x_device_count INTEGER,
ADD COLUMN x_months INTEGER,
ADD COLUMN x_subscription_start DATE,
ADD COLUMN x_subscription_end DATE;

-- Note: Odoo ORM handles this automatically
-- NULL defaults are safe (backward compatible)
```

---

#### Model: dtx.renew.subscription.wizard

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/wizards/renew_subscription_wizard.py` (NEW)

**Complete Code:**

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class RenewSubscriptionWizard(models.TransientModel):
    _name = 'dtx.renew.subscription.wizard'
    _description = 'Renew Subscription Contract'

    # ==========================================
    # FIELDS
    # ==========================================
    order_id = fields.Many2one(
        'sale.order',
        string='Original SO',
        required=True,
        readonly=True,
        help='The original sale order to renew',
    )

    original_start_date = fields.Date(
        string='Original Start Date',
        compute='_compute_original_dates',
        readonly=True,
        help='Start date from original subscription',
    )

    original_end_date = fields.Date(
        string='Original End Date',
        compute='_compute_original_dates',
        readonly=True,
        help='End date from original subscription',
    )

    new_start_date = fields.Date(
        string='New Start Date',
        required=True,
        help='Start date for renewal period. Defaults to original end + 1 day.',
    )

    new_months = fields.Integer(
        string='New Duration (Months)',
        default=12,
        required=True,
        help='Duration in months for renewal. Can be different from original.',
    )

    new_end_date = fields.Date(
        string='New End Date',
        compute='_compute_new_end_date',
        store=True,
        readonly=True,
        help='Auto-calculated: New Start + New Months',
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('order_id')
    def _compute_original_dates(self):
        """Get start/end dates from original SO subscription lines"""
        for wizard in self:
            if wizard.order_id:
                subscription_lines = wizard.order_id.order_line.filtered('x_is_subscription')
                if subscription_lines:
                    # Use first subscription line as reference
                    first_line = subscription_lines[0]
                    wizard.original_start_date = first_line.x_subscription_start
                    wizard.original_end_date = first_line.x_subscription_end

                    # Auto-set new_start_date to day after original end
                    if first_line.x_subscription_end:
                        wizard.new_start_date = first_line.x_subscription_end + relativedelta(days=1)
                else:
                    wizard.original_start_date = False
                    wizard.original_end_date = False
            else:
                wizard.original_start_date = False
                wizard.original_end_date = False

    @api.depends('new_start_date', 'new_months')
    def _compute_new_end_date(self):
        """Calculate new end date from start + months"""
        for wizard in self:
            if wizard.new_start_date and wizard.new_months:
                wizard.new_end_date = wizard.new_start_date + relativedelta(months=wizard.new_months)
            else:
                wizard.new_end_date = False

    # ==========================================
    # ACTION METHODS
    # ==========================================
    def action_renew(self):
        """Create new SO with updated subscription dates"""
        self.ensure_one()

        # Copy original SO
        new_order = self.order_id.copy({
            'date_order': fields.Datetime.now(),
            'state': 'draft',
            # Clear contract fields
            'x_contract_no': False,
            'x_signed_date': False,
            'x_advance_amount': 0,
            'x_contract_scan': False,
            # Keep customer, pricelist, payment terms, etc.
        })

        # Update subscription lines with new dates
        for new_line in new_order.order_line.filtered('x_is_subscription'):
            new_line.write({
                'x_subscription_start': self.new_start_date,
                'x_months': self.new_months,
                'x_subscription_end': self.new_end_date,
                # Recalculate quantity if device count exists
                'product_uom_qty': (
                    new_line.x_device_count * self.new_months
                    if new_line.x_device_count
                    else new_line.product_uom_qty
                ),
            })

        # Link original and new SO via chatter
        self.order_id.message_post(
            body=f"Renewal quotation created: <a href='/web#id={new_order.id}&model=sale.order'>{new_order.name}</a>"
        )
        new_order.message_post(
            body=f"Renews contract: <a href='/web#id={self.order_id.id}&model=sale.order'>{self.order_id.name}</a>"
        )

        # Return action to open new SO
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': new_order.id,
            'view_mode': 'form',
            'target': 'current',
        }
```

**Field Characteristics:**

| Field | Type | Stored | Computed | Default |
|-------|------|--------|----------|---------|
| order_id | Many2one | ✅ | ❌ | (context) |
| original_start_date | Date | ❌ | ✅ | - |
| original_end_date | Date | ❌ | ✅ | - |
| new_start_date | Date | ✅ | ❌ | original_end + 1 day |
| new_months | Integer | ✅ | ❌ | 12 |
| new_end_date | Date | ✅ | ✅ | new_start + new_months |

**Note:** TransientModel - Data not persisted long-term (auto-deleted after action)

---

## Business Logic

### Auto-calculation Logic

#### 1. Quantity Calculation

**Formula:** `Quantity = Device Count × Months`

**Implementation:**
```python
@api.onchange('x_device_count', 'x_months')
def _onchange_subscription_quantity(self):
    if self.x_is_subscription and self.x_device_count and self.x_months:
        self.product_uom_qty = self.x_device_count * self.x_months
```

**Trigger:** When user changes device count OR months
**Condition:** Both fields must have values
**Result:** Updates product_uom_qty (Quantity field on SO line)

**Example:**
```
Device Count: 10
Months: 9
Quantity: 10 × 9 = 90
```

#### 2. End Date Calculation

**Formula:** `End Date = Start Date + Months`

**Implementation:**
```python
from dateutil.relativedelta import relativedelta

@api.onchange('x_subscription_start', 'x_months')
def _onchange_subscription_dates(self):
    if self.x_subscription_start and self.x_months:
        self.x_subscription_end = self.x_subscription_start + relativedelta(months=self.x_months)
```

**Trigger:** When user changes start date OR months
**Condition:** Both fields must have values
**Result:** Updates x_subscription_end

**Why relativedelta?**
- Handles month-end dates correctly
- Accounts for varying month lengths

**Example:**
```
Start: 2025-12-01
Months: 9
End: 2025-12-01 + 9 months = 2026-08-31 ✅
(Not 2026-09-01 - relativedelta handles month boundary correctly)
```

#### 3. Product Selection Auto-fill

**Implementation:**
```python
@api.onchange('product_id')
def _onchange_product_subscription(self):
    if self.product_id and self.product_id.product_tmpl_id.x_dtx_type == 'subscription':
        # Auto-fill default months
        self.x_months = self.product_id.product_tmpl_id.x_subscription_default_months or 12
        # Auto-fill price
        if self.product_id.product_tmpl_id.x_subscription_base_price:
            self.price_unit = self.product_id.product_tmpl_id.x_subscription_base_price
```

**Trigger:** When user selects subscription product
**Condition:** Product DTX Type = 'subscription'
**Result:**
- x_months ← product.x_subscription_default_months (default: 12)
- price_unit ← product.x_subscription_base_price

### Renewal Logic

**Workflow:**

1. User clicks "Renew Contract" on confirmed SO
2. Wizard opens with context: `default_order_id` = current SO
3. Wizard computes original dates from SO lines
4. Wizard defaults new_start_date = original_end + 1 day
5. User adjusts new_months if needed
6. User clicks "Create Renewal"
7. Wizard.action_renew():
   a. Copies original SO (draft state)
   b. Clears contract fields (no contract number, signed date)
   c. Updates subscription line dates and months
   d. Recalculates quantity = device_count × new_months
   e. Links both SOs via chatter messages
   f. Opens new SO

**Key Design Decisions:**

- **Copy SO:** Preserves customer, pricelist, payment terms
- **Draft state:** New SO needs customer approval
- **Clear contract fields:** New SO is a new contract (different number)
- **Recalculate quantity:** Device count same, but months may change
- **Chatter links:** Easy to track renewal chain

---

## Views and UI

### Product Form View

**File:** `odoo-dev/addons/dtx_product_standards/views/product_template_views.xml`

**Modifications:**

1. **Add common fields** (visible for ALL products):
```xml
<xpath expr="//group[@name='group_general']" position="inside">
    <group string="DTX - Chuẩn hóa sản phẩm" name="dtx_standards_group">
        <field name="x_dtx_type"/>
        <field name="x_dtx_requires_vendor_bill"/>
        <field name="x_part_number" placeholder="e.g., DTX-K32-001"/>
        <field name="x_country_of_origin" placeholder="e.g., China, Vietnam, USA"/>
        <field name="x_dtx_notes" placeholder="Ghi chú đặc điểm, yêu cầu đặc biệt..."/>
    </group>
</xpath>
```

2. **Add subscription-specific group** (visible only when type=subscription):
```xml
<xpath expr="//group[@name='group_general']" position="inside">
    <group string="Subscription Settings" name="dtx_subscription_group"
           attrs="{'invisible': [('x_dtx_type', '!=', 'subscription')]}">
        <field name="x_subscription_base_price"
               widget="monetary"
               options="{'currency_field': 'currency_id'}"/>
        <field name="x_subscription_default_months"/>
    </group>
</xpath>
```

3. **Add columns to tree view**:
```xml
<xpath expr="//field[@name='detailed_type']" position="after">
    <field name="x_dtx_type" optional="show"/>
    <field name="x_part_number" optional="show"/>
    <field name="x_country_of_origin" optional="show"/>
</xpath>
```

**Visibility Logic:**

| DTX Type | Subscription Settings Group Visible? |
|----------|-------------------------------------|
| device_serialized | ❌ No |
| component_untracked | ❌ No |
| finished_kiosk | ❌ No |
| service | ❌ No |
| **subscription** | **✅ Yes** |

---

### Sale Order Form View

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/views/sale_order_views.xml`

**Modification 1: Add "Renew Contract" button**

```xml
<record id="view_order_form_renew_button" model="ir.ui.view">
    <field name="name">sale.order.form.renew.button</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="priority">99</field>
    <field name="arch" type="xml">
        <!-- Add button after Confirm button -->
        <xpath expr="//button[@name='action_confirm']" position="after">
            <button name="%(action_renew_subscription_wizard)d"
                    string="Renew Contract"
                    type="action"
                    class="btn-primary"
                    attrs="{'invisible': ['|', ('state', '!=', 'sale'), ('x_has_subscription_lines', '=', False)]}"/>
            <!-- Hidden field to control button visibility -->
            <field name="x_has_subscription_lines" invisible="1"/>
        </xpath>
    </field>
</record>
```

**Button Visibility Logic:**

| State | Has Subscription Lines | Button Visible? |
|-------|------------------------|----------------|
| draft | Yes | ❌ No |
| sent | Yes | ❌ No |
| **sale** | **Yes** | **✅ Yes** |
| sale | No | ❌ No |
| done | Yes | ✅ Yes |
| cancel | Yes | ❌ No |

**Formula:** `visible = (state == 'sale' OR state == 'done') AND x_has_subscription_lines`

---

### Sale Order Line Tree View

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/views/sale_order_views.xml`

**Modification: Extend SO line tree**

```xml
<record id="view_order_line_tree_subscription" model="ir.ui.view">
    <field name="name">sale.order.line.tree.subscription</field>
    <field name="model">sale.order.line</field>
    <field name="inherit_id" ref="sale.view_order_line_tree"/>
    <field name="arch" type="xml">
        <!-- Add Part Number and Country of Origin after product_id -->
        <xpath expr="//field[@name='product_id']" position="after">
            <field name="x_part_number" optional="show"/>
            <field name="x_country_of_origin" optional="show"/>
        </xpath>

        <!-- Add subscription fields after quantity -->
        <xpath expr="//field[@name='product_uom_qty']" position="after">
            <!-- Hidden field to control visibility of subscription fields -->
            <field name="x_is_subscription" invisible="1"/>

            <!-- Subscription fields (visible only for subscription lines) -->
            <field name="x_device_count" optional="show"
                   attrs="{'invisible': [('x_is_subscription', '=', False)]}"/>
            <field name="x_months" optional="show"
                   attrs="{'invisible': [('x_is_subscription', '=', False)]}"/>
            <field name="x_subscription_start" optional="show"
                   attrs="{'invisible': [('x_is_subscription', '=', False)]}"/>
            <field name="x_subscription_end" optional="show"
                   attrs="{'invisible': [('x_is_subscription', '=', False)]}"/>
        </xpath>
    </field>
</record>
```

**Column Visibility:**

| Column | Hardware Line | Service Line | Subscription Line |
|--------|--------------|--------------|-------------------|
| Product | ✅ | ✅ | ✅ |
| Part Number | ✅ | ✅ | ✅ |
| Country of Origin | ✅ | ✅ | ✅ |
| Quantity | ✅ | ✅ | ✅ (auto-calc) |
| Device Count | ❌ Hidden | ❌ Hidden | ✅ Visible |
| Months | ❌ Hidden | ❌ Hidden | ✅ Visible |
| Start Date | ❌ Hidden | ❌ Hidden | ✅ Visible |
| End Date | ❌ Hidden | ❌ Hidden | ✅ Visible |

---

### Renew Subscription Wizard View

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/wizards/renew_subscription_wizard_views.xml`

**Complete View:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View -->
    <record id="view_renew_subscription_wizard_form" model="ir.ui.view">
        <field name="name">dtx.renew.subscription.wizard.form</field>
        <field name="model">dtx.renew.subscription.wizard</field>
        <field name="arch" type="xml">
            <form string="Renew Subscription Contract">
                <group>
                    <group string="Original Contract">
                        <field name="order_id" invisible="1"/>
                        <field name="original_start_date" readonly="1"/>
                        <field name="original_end_date" readonly="1"/>
                    </group>
                    <group string="New Contract Period">
                        <field name="new_start_date"/>
                        <field name="new_months"/>
                        <field name="new_end_date" readonly="1"/>
                    </group>
                </group>
                <footer>
                    <button name="action_renew"
                            string="Create Renewal Quotation"
                            type="object"
                            class="btn-primary"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record id="action_renew_subscription_wizard" model="ir.actions.act_window">
        <field name="name">Renew Subscription</field>
        <field name="res_model">dtx.renew.subscription.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="binding_model_id" ref="sale.model_sale_order"/>
    </record>
</odoo>
```

**UI Behavior:**

1. Opens as modal dialog (target=new)
2. Original dates readonly (computed from SO)
3. new_start_date defaults to original_end + 1 day (editable)
4. new_months defaults to 12 (editable)
5. new_end_date auto-calculates (readonly)
6. Primary button: "Create Renewal Quotation"
7. Secondary button: "Cancel" (closes wizard without action)

---

## Security

### Access Rights

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/security/ir.model.access.csv`

**New Lines:**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_dtx_renew_subscription_wizard_sales_user,dtx.renew.subscription.wizard sales user,model_dtx_renew_subscription_wizard,sales_team.group_sale_salesman,1,1,1,1
access_dtx_renew_subscription_wizard_sales_manager,dtx.renew.subscription.wizard sales manager,model_dtx_renew_subscription_wizard,sales_team.group_sale_manager,1,1,1,1
```

**Permissions:**

| Group | Model | Read | Write | Create | Unlink |
|-------|-------|------|-------|--------|--------|
| Sales User | dtx.renew.subscription.wizard | ✅ | ✅ | ✅ | ✅ |
| Sales Manager | dtx.renew.subscription.wizard | ✅ | ✅ | ✅ | ✅ |

**Note:** No record rules needed for wizard (transient model, user-specific)

### Field-Level Security

**Product Fields (product.template):**
- All users can READ Part Number, Country of Origin
- Only Sales Manager/Admin can WRITE product fields
- Standard Odoo product security applies

**SO Line Fields (sale.order.line):**
- Sales User can read/write on draft/sent quotations
- Sales Manager can modify confirmed orders (if needed)
- Standard Odoo SO security applies

**No custom field-level security needed** - Odoo's standard model security is sufficient.

---

## Wizards

### dtx.renew.subscription.wizard

#### Wizard Lifecycle

1. **Invocation:**
   - User clicks "Renew Contract" button on SO form
   - Context: `{'default_order_id': <SO ID>}`

2. **Initialization:**
   - order_id set from context
   - _compute_original_dates() runs → fills original start/end
   - new_start_date defaults to original_end + 1 day
   - new_months defaults to 12

3. **User Interaction:**
   - User can adjust new_start_date (if gap needed)
   - User can change new_months (e.g., 6 instead of 12)
   - new_end_date updates automatically via @api.depends

4. **Execution:**
   - User clicks "Create Renewal Quotation"
   - action_renew() method runs:
     - Copies SO
     - Updates dates
     - Links via chatter
   - Returns ir.actions.act_window → opens new SO

5. **Cleanup:**
   - Wizard data auto-deleted (transient model)

#### Context Passing

**Button in SO form:**
```xml
<button name="%(action_renew_subscription_wizard)d" .../>
```

**Action definition:**
```xml
<record id="action_renew_subscription_wizard" model="ir.actions.act_window">
    <field name="binding_model_id" ref="sale.model_sale_order"/>
    ...
</record>
```

**Automatic context injection:**
- `binding_model_id` tells Odoo: "This action is called FROM sale.order"
- Odoo automatically passes: `default_order_id = current_record_id`

**Wizard receives:**
```python
order_id = fields.Many2one('sale.order', default=lambda self: self._context.get('default_order_id'))
```

#### Error Handling

**Validation in action_renew():**

```python
def action_renew(self):
    self.ensure_one()  # Ensure single wizard record

    if not self.order_id:
        raise UserError("Original order not found")

    if not self.new_start_date:
        raise UserError("New start date is required")

    if not self.new_months or self.new_months <= 0:
        raise UserError("New duration must be positive")

    # ... rest of logic
```

**Potential Issues:**

| Issue | Cause | Prevention |
|-------|-------|------------|
| No subscription lines | User clicked button on wrong SO | Button visibility logic (attrs) |
| Invalid dates | User entered bad date | Odoo date widget validation |
| Copy failed | Insufficient permissions | Security access check |
| Chatter link broken | SO deleted during wizard | Transaction rollback on error |

---

## Integration Points

### Standard Odoo Models

**product.template:**
- Extended with x_dtx_type selection
- Extended with common metadata fields
- Extended with subscription fields
- No override of core methods

**sale.order:**
- Extended with x_has_subscription_lines computed field
- No override of core methods (confirm, invoice, etc.)

**sale.order.line:**
- Extended with metadata (related) and subscription fields
- Overrides @api.onchange for product_id (calls super)
- No override of create/write methods

### DTX Modules

**dtx_product_standards:**
- Provides x_dtx_type field (extended with 'subscription')
- Provides base for product metadata

**dtx_sales_pakd_contract:**
- Builds on product_standards
- Subscription features are ADDITIONAL (not replacing PAKD)
- PAKD workflow still works for non-subscription products

### External Dependencies

**Python Libraries:**

```python
from dateutil.relativedelta import relativedelta
```

- Used for date calculations (month addition)
- Standard Python library (included in Odoo)

**No external API calls** - All logic is internal

---

## Database Schema

### Table: product_template

**New Columns:**

```sql
-- Common product metadata (ALL products)
x_part_number VARCHAR NULL
x_country_of_origin VARCHAR NULL

-- Subscription-specific (only for subscription products)
x_subscription_base_price NUMERIC NULL
x_subscription_default_months INTEGER DEFAULT 12
```

**Indexes:**

None required - These fields are:
- Rarely searched (no filtering on base price)
- Part Number could benefit from index if searching frequently

**Optional Index (if needed):**
```sql
CREATE INDEX idx_product_template_part_number
ON product_template(x_part_number)
WHERE x_part_number IS NOT NULL;
```

---

### Table: sale_order_line

**New Columns:**

```sql
-- Related fields (NOT stored in DB - computed on read)
-- x_part_number (related, store=False)
-- x_country_of_origin (related, store=False)

-- Computed field (stored)
x_is_subscription BOOLEAN NULL

-- Subscription data fields
x_device_count INTEGER NULL
x_months INTEGER NULL
x_subscription_start DATE NULL
x_subscription_end DATE NULL
```

**Indexes:**

Useful for reporting/filtering:

```sql
-- Index for filtering subscription lines
CREATE INDEX idx_sol_is_subscription
ON sale_order_line(x_is_subscription)
WHERE x_is_subscription = TRUE;

-- Index for expiry date filtering
CREATE INDEX idx_sol_subscription_end
ON sale_order_line(x_subscription_end)
WHERE x_subscription_end IS NOT NULL;
```

---

### View: Active Subscriptions (Optional)

**Create SQL view for reporting:**

```sql
CREATE OR REPLACE VIEW v_dtx_active_subscriptions AS
SELECT
    so.id AS order_id,
    so.name AS order_name,
    so.partner_id,
    rp.name AS customer_name,
    sol.id AS line_id,
    sol.product_id,
    pt.name AS product_name,
    sol.x_device_count AS device_count,
    sol.x_months AS months,
    sol.x_subscription_start AS start_date,
    sol.x_subscription_end AS end_date,
    sol.product_uom_qty AS quantity,
    sol.price_unit,
    sol.price_subtotal,
    sol.price_total,
    CURRENT_DATE - sol.x_subscription_end AS days_until_expiry,
    CASE
        WHEN sol.x_subscription_end < CURRENT_DATE THEN 'Expired'
        WHEN sol.x_subscription_end <= CURRENT_DATE + INTERVAL '30 days' THEN 'Expiring Soon'
        ELSE 'Active'
    END AS subscription_status
FROM
    sale_order so
    JOIN sale_order_line sol ON sol.order_id = so.id
    JOIN product_product pp ON pp.id = sol.product_id
    JOIN product_template pt ON pt.id = pp.product_tmpl_id
    JOIN res_partner rp ON rp.id = so.partner_id
WHERE
    so.state IN ('sale', 'done')
    AND sol.x_is_subscription = TRUE
    AND sol.x_subscription_end IS NOT NULL
ORDER BY
    sol.x_subscription_end ASC;
```

**Usage:**
```sql
-- Active subscriptions
SELECT * FROM v_dtx_active_subscriptions WHERE subscription_status = 'Active';

-- Expiring in 30 days
SELECT * FROM v_dtx_active_subscriptions WHERE subscription_status = 'Expiring Soon';

-- Expired subscriptions
SELECT * FROM v_dtx_active_subscriptions WHERE subscription_status = 'Expired';
```

---

## API Reference

### Python API

#### Check if Product is Subscription

```python
product = self.env['product.template'].browse(product_id)
is_subscription = (product.x_dtx_type == 'subscription')
```

#### Get Subscription Lines from SO

```python
order = self.env['sale.order'].browse(order_id)
subscription_lines = order.order_line.filtered('x_is_subscription')

for line in subscription_lines:
    print(f"Product: {line.product_id.name}")
    print(f"Devices: {line.x_device_count}")
    print(f"Months: {line.x_months}")
    print(f"Period: {line.x_subscription_start} to {line.x_subscription_end}")
```

#### Create Subscription Product Programmatically

```python
product = self.env['product.template'].create({
    'name': 'DiHub Cloud License (Device-Month)',
    'type': 'service',
    'x_dtx_type': 'subscription',
    'x_part_number': 'DIHUB-LIC-001',
    'x_country_of_origin': 'Vietnam',
    'x_subscription_base_price': 80000.0,
    'x_subscription_default_months': 12,
    'list_price': 80000.0,
    'taxes_id': [(6, 0, [self.env.ref('account.tax_sale_10').id])],
})
```

#### Create SO with Subscription Line

```python
from dateutil.relativedelta import relativedelta

order = self.env['sale.order'].create({
    'partner_id': customer_id,
})

line = self.env['sale.order.line'].create({
    'order_id': order.id,
    'product_id': subscription_product_id,
    'product_uom_qty': 120,  # Will be recalculated
    'price_unit': 80000,
    'x_device_count': 10,
    'x_months': 12,
    'x_subscription_start': fields.Date.today(),
    # x_subscription_end will be auto-calculated
})
```

---

### ORM Queries

#### Find All Subscription Products

```python
subscriptions = self.env['product.template'].search([
    ('x_dtx_type', '=', 'subscription')
])
```

#### Find SOs with Subscription Lines

```python
orders = self.env['sale.order'].search([
    ('state', 'in', ['sale', 'done']),
    ('order_line.x_is_subscription', '=', True),
])
```

#### Find Subscriptions Expiring in 30 Days

```python
from datetime import date, timedelta

end_date = date.today() + timedelta(days=30)

lines = self.env['sale.order.line'].search([
    ('x_is_subscription', '=', True),
    ('order_id.state', 'in', ['sale', 'done']),
    ('x_subscription_end', '<=', end_date),
    ('x_subscription_end', '>=', date.today()),
])
```

#### Aggregate Subscription Revenue

```python
from odoo import fields
from dateutil.relativedelta import relativedelta

# Last 12 months
start_date = fields.Date.today() - relativedelta(months=12)

domain = [
    ('x_is_subscription', '=', True),
    ('order_id.state', 'in', ['sale', 'done']),
    ('x_subscription_start', '>=', start_date),
]

lines = self.env['sale.order.line'].read_group(
    domain,
    ['price_total:sum'],
    ['product_id'],
)

for group in lines:
    product_id = group['product_id'][0]
    total = group['price_total']
    print(f"Product {product_id}: {total} VND")
```

---

## Testing

### Unit Tests

**File:** `odoo-dev/addons/dtx_sales_pakd_contract/tests/test_subscription.py` (CREATE)

```python
from odoo.tests import TransactionCase
from dateutil.relativedelta import relativedelta
from odoo import fields


class TestSubscription(TransactionCase):

    def setUp(self):
        super().setUp()

        # Create subscription product
        self.subscription_product = self.env['product.template'].create({
            'name': 'Test Subscription',
            'type': 'service',
            'x_dtx_type': 'subscription',
            'x_part_number': 'TEST-SUB-001',
            'x_country_of_origin': 'Vietnam',
            'x_subscription_base_price': 80000.0,
            'x_subscription_default_months': 12,
            'list_price': 80000.0,
        })

        # Create customer
        self.customer = self.env['res.partner'].create({
            'name': 'Test Customer',
        })

    def test_product_is_subscription(self):
        """Test product type detection"""
        self.assertEqual(self.subscription_product.x_dtx_type, 'subscription')

    def test_quantity_auto_calculation(self):
        """Test Quantity = Devices × Months"""
        order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
        })

        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.subscription_product.product_variant_id.id,
            'x_device_count': 10,
            'x_months': 9,
        })

        # Trigger onchange
        line._onchange_subscription_quantity()

        self.assertEqual(line.product_uom_qty, 90)

    def test_end_date_calculation(self):
        """Test End Date = Start + Months"""
        order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
        })

        start_date = fields.Date.from_string('2025-12-01')

        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.subscription_product.product_variant_id.id,
            'x_subscription_start': start_date,
            'x_months': 9,
        })

        # Trigger onchange
        line._onchange_subscription_dates()

        expected_end = start_date + relativedelta(months=9)
        self.assertEqual(line.x_subscription_end, expected_end)

    def test_renew_contract(self):
        """Test renewal wizard creates new SO with updated dates"""
        # Create original SO
        original_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'x_contract_no': 'HĐ-TEST-001',
        })

        line = self.env['sale.order.line'].create({
            'order_id': original_order.id,
            'product_id': self.subscription_product.product_variant_id.id,
            'x_device_count': 10,
            'x_months': 12,
            'x_subscription_start': fields.Date.from_string('2025-12-01'),
            'x_subscription_end': fields.Date.from_string('2026-11-30'),
        })

        # Confirm order
        original_order.action_confirm()

        # Create wizard
        wizard = self.env['dtx.renew.subscription.wizard'].create({
            'order_id': original_order.id,
            'new_start_date': fields.Date.from_string('2026-12-01'),
            'new_months': 12,
        })

        # Execute renewal
        result = wizard.action_renew()

        # Get new order
        new_order = self.env['sale.order'].browse(result['res_id'])

        # Assertions
        self.assertEqual(new_order.state, 'draft')
        self.assertFalse(new_order.x_contract_no)  # Contract cleared

        new_line = new_order.order_line.filtered('x_is_subscription')[0]
        self.assertEqual(new_line.x_device_count, 10)  # Same devices
        self.assertEqual(new_line.x_months, 12)  # New duration
        self.assertEqual(new_line.x_subscription_start, fields.Date.from_string('2026-12-01'))
        self.assertEqual(new_line.x_subscription_end, fields.Date.from_string('2027-11-30'))
        self.assertEqual(new_line.product_uom_qty, 120)  # Recalculated
```

**Run Tests:**
```bash
docker-compose run --rm odoo odoo -u dtx_sales_pakd_contract --test-enable --stop-after-init -d dtx_odoo16_test
```

---

### Manual Testing

See [TESTING.md](../../TESTING.md) for comprehensive manual test cases.

---

## Migration

### Database Migration

**No migration script needed** because:

1. New fields have NULL defaults → safe to add
2. No data transformation required
3. Existing data unaffected

**Automatic Schema Update:**

Odoo ORM automatically creates columns during module upgrade:

```bash
docker-compose run --rm odoo odoo -u dtx_product_standards,dtx_sales_pakd_contract -d dtx_odoo16 --stop-after-init
```

### Version Upgrade Path

**From:** dtx_product_standards v1.2.0, dtx_sales_pakd_contract v1.5.0
**To:** dtx_product_standards v1.3.0, dtx_sales_pakd_contract v1.6.0

**Steps:**

1. Backup database
2. Update module code (git pull or copy files)
3. Restart Odoo
4. Upgrade modules (UI or CLI)
5. Verify (check logs for errors)

**Rollback Plan:**

If issues occur:
1. Stop Odoo
2. Restore database backup
3. Revert code changes (git checkout previous version)
4. Restart Odoo

---

## Performance

### Query Performance

**Expected Load:**
- ~100 subscription products
- ~500-1000 active subscription contracts
- ~100 new subscriptions per month

**Critical Queries:**

1. **SO Line Tree View** (most frequent):
```sql
SELECT * FROM sale_order_line WHERE order_id = ?
```
- Uses existing index on order_id
- No performance impact (related fields not stored)

2. **Expiring Subscriptions Report**:
```sql
SELECT * FROM sale_order_line
WHERE x_is_subscription = TRUE
AND x_subscription_end BETWEEN ? AND ?
```
- Benefits from index on x_subscription_end (if created)
- Expected: <100ms for 1000 records

3. **Renewal Wizard Data Load**:
```sql
SELECT * FROM sale_order_line WHERE order_id = ? AND x_is_subscription = TRUE
```
- Uses existing order_id index
- Expected: <10ms (1-20 lines per order)

**Optimization Tips:**

- Create index on x_subscription_end if expiry reports are frequent
- Use SQL view (v_dtx_active_subscriptions) for complex reports
- Archive old/expired SOs to keep active dataset small

### Compute Field Performance

**x_is_subscription (stored):**
- Computed on create/write of SO line
- Stored in DB → no recomputation on read
- Fast: O(1)

**x_has_subscription_lines (not stored):**
- Computed on each SO form load
- Requires reading all SO lines
- Fast: O(n) where n = number of lines (typically <50)

**x_part_number, x_country_of_origin (related, not stored):**
- Computed on each SO line read
- Requires reading product.template
- Fast: O(1) per line (cached by ORM)

**Onchange Methods:**
- Run only in UI (not on create/write)
- No performance impact on backend operations

---

## Troubleshooting

### Common Issues

#### Issue 1: Quantity Not Auto-calculating

**Symptoms:**
- User enters device count and months
- Quantity stays at 1 or doesn't update

**Debug Steps:**

1. Check product type:
```python
line.product_id.product_tmpl_id.x_dtx_type
# Should be 'subscription'
```

2. Check x_is_subscription:
```python
line.x_is_subscription
# Should be True
```

3. Check both fields have values:
```python
line.x_device_count  # Should not be None or 0
line.x_months  # Should not be None or 0
```

4. Check onchange is triggered:
   - Only works in UI form view
   - Does NOT trigger on create/write in code
   - If creating lines programmatically, must set quantity manually

**Solution:**

If creating lines via code:
```python
line.write({
    'x_device_count': 10,
    'x_months': 9,
    'product_uom_qty': 10 * 9,  # Must calculate manually
})
```

---

#### Issue 2: End Date Calculation Wrong

**Symptoms:**
- End date is off by 1 day
- End date doesn't account for month-end

**Debug:**

```python
from dateutil.relativedelta import relativedelta

start = fields.Date.from_string('2025-12-01')
months = 9
end = start + relativedelta(months=months)
# Should be: 2026-08-31

# WRONG approach:
from datetime import timedelta
end_wrong = start + timedelta(days=30*months)
# Would be: 2026-08-30 or incorrect
```

**Root Cause:**
- Using timedelta instead of relativedelta
- Not accounting for varying month lengths

**Solution:**
- Always use `relativedelta(months=N)` for month addition
- Do NOT use `timedelta(days=30*N)`

---

#### Issue 3: "Renew Contract" Button Not Appearing

**Symptoms:**
- Button not visible on confirmed SO

**Debug Steps:**

1. Check SO state:
```python
order.state
# Must be 'sale' or 'done'
```

2. Check x_has_subscription_lines:
```python
order.x_has_subscription_lines
# Should be True
```

3. Check subscription lines exist:
```python
order.order_line.filtered('x_is_subscription')
# Should return at least one line
```

4. Check product type:
```python
for line in order.order_line:
    print(line.product_id.name, line.product_id.product_tmpl_id.x_dtx_type)
# At least one should have 'subscription'
```

**Solution:**

If x_has_subscription_lines is False but lines exist:
- Recompute field:
```python
order._compute_has_subscription_lines()
```

If button still not visible:
- Check view inheritance is applied:
```bash
docker-compose logs odoo | grep "view_order_form_renew_button"
```

---

#### Issue 4: Wizard Crashes on Renewal

**Symptoms:**
- Error when clicking "Create Renewal Quotation"
- Traceback in logs

**Common Errors:**

**Error 1: "order_id is required"**
```python
# Check context:
wizard._context.get('default_order_id')
# Should be set by button action
```

**Error 2: "AccessError: You cannot modify a confirmed sale order"**
```python
# Check copy preserves state:
new_order.state
# Should be 'draft', not 'sale'
```

**Error 3: "RecordSet is empty"**
```python
# Check subscription lines exist:
new_order.order_line.filtered('x_is_subscription')
# Should return lines
```

**Debug Wizard:**

```python
# In Odoo shell:
order = self.env['sale.order'].browse(123)
wizard = self.env['dtx.renew.subscription.wizard'].create({
    'order_id': order.id,
    'new_start_date': '2026-12-01',
    'new_months': 12,
})
wizard.action_renew()  # Run and check error
```

---

### Logging

**Enable Debug Logging:**

`odoo-dev/addons/dtx_sales_pakd_contract/__init__.py`:
```python
import logging
_logger = logging.getLogger(__name__)
```

`models/sale_order_line.py`:
```python
@api.onchange('x_device_count', 'x_months')
def _onchange_subscription_quantity(self):
    _logger.debug(f"Subscription quantity recalc: devices={self.x_device_count}, months={self.x_months}")
    if self.x_is_subscription and self.x_device_count and self.x_months:
        new_qty = self.x_device_count * self.x_months
        _logger.info(f"Auto-calculated quantity: {new_qty}")
        self.product_uom_qty = new_qty
```

**View Logs:**
```bash
docker-compose logs -f odoo | grep "dtx_sales_pakd_contract"
```

---

## Appendix

### Complete File List

**dtx_product_standards:**
- `models/product_template.py` (modified)
- `views/product_template_views.xml` (modified)
- `__manifest__.py` (modified)

**dtx_sales_pakd_contract:**
- `models/__init__.py` (modified - add import)
- `models/sale_order.py` (modified - add x_has_subscription_lines)
- `models/sale_order_line.py` (NEW)
- `views/sale_order_views.xml` (modified - add button and SO line fields)
- `wizards/__init__.py` (modified - add import)
- `wizards/renew_subscription_wizard.py` (NEW)
- `wizards/renew_subscription_wizard_views.xml` (NEW)
- `security/ir.model.access.csv` (modified - add wizard access)
- `__manifest__.py` (modified - version, data files, depends)

**Total:** 12 files (3 new, 9 modified)

### Code Statistics

```
Language: Python
New lines: ~240
Modified lines: ~100

Language: XML
New lines: ~100
Modified lines: ~50

Total new code: ~340 lines
```

---

**Version:** 1.0
**Last Updated:** 2026-01-14
**Module Versions:** dtx_product_standards v1.3.0, dtx_sales_pakd_contract v1.6.0
