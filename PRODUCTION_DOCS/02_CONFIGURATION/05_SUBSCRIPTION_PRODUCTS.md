# Subscription Product Configuration Guide

**Module:** dtx_product_standards v1.3.0, dtx_sales_pakd_contract v1.6.0
**Date:** 2026-01-14
**For:** System Administrator, Sales Manager

---

## Overview

This guide explains how to configure subscription products for prepaid license sales (DiHub Digital Signage, SeQMS Online Ticket, etc.).

### What You'll Learn

- How to create subscription products
- Configure pricing per device per month
- Set default subscription duration
- Add Part Number and Country of Origin (for ALL products)
- Configure taxes for subscription services

---

## Prerequisites

Before configuring subscription products, ensure:

1. Module `dtx_product_standards` v1.3.0+ installed
2. Module `dtx_sales_pakd_contract` v1.6.0+ installed
3. Admin or Sales Manager access
4. VAT tax rates configured (typically 10% for services)

---

## Part 1: Create Subscription Product

### Step 1: Navigate to Products

**Menu:** Inventory > Products > Products > Create

### Step 2: Fill Basic Information

**General Information Tab:**

| Field | Value | Example |
|-------|-------|---------|
| Product Name | Descriptive name with pricing unit | DiHub Cloud License (Device-Month) |
| Product Type | **Service** | Service ⚠️ Important |
| Can be Sold | ✅ Yes | Checked |
| Can be Purchased | ❌ No | Unchecked (it's a license) |

**Why Service Type?**
- Subscriptions don't have inventory/stock
- No delivery order needed
- Direct invoice after confirmation

### Step 3: Set DTX Type to Subscription

**DTX - Chuẩn hóa sản phẩm section:**

| Field | Value | Notes |
|-------|-------|-------|
| DTX Type | **Subscription / License theo tháng** | ⚠️ Critical - enables subscription fields |
| Requires Vendor Bill | Unchecked | Unless you resell licenses |

**Important:** Once you select "Subscription / License theo tháng", the **Subscription Settings** section will appear below.

### Step 4: Fill Common Product Metadata

**These fields are available for ALL product types (not just subscriptions):**

| Field | Example | Notes |
|-------|---------|-------|
| Part Number / Mã sản phẩm | DIHUB-LIC-001 | Internal or vendor code |
| Country of Origin / Xuất xứ | Vietnam | Manufacturing country |
| DTX Notes | Special requirements | Optional |

**Naming Convention for Part Numbers:**

Recommended format: `[PRODUCT]-[TYPE]-[VARIANT]`

Examples:
```
DIHUB-LIC-001      DiHub Cloud License
SEQMS-TICKET-001   SeQMS Online Ticket
DIHUB-LIC-ENT      DiHub Enterprise License
SEQMS-TICKET-PRO   SeQMS Professional Ticket
```

### Step 5: Configure Subscription Settings

**Subscription Settings section (only visible when DTX Type = Subscription):**

| Field | Example | Purpose |
|-------|---------|---------|
| Base Price / Device / Month | 80,000 | Price per device per month (VND, before VAT) |
| Default Duration (Months) | 12 | Auto-fills when adding to quotation |

**Pricing Example:**
```
Base Price: 80,000 VND/device/month (before VAT)
VAT 10%: 8,000 VND
Total: 88,000 VND/device/month

Customer wants: 10 devices × 9 months
Quantity: 10 × 9 = 90 device-months
Subtotal: 90 × 80,000 = 7,200,000 VND
VAT: 720,000 VND
Total: 7,920,000 VND
```

### Step 6: Configure Sales Tab

**Sales Tab Settings:**

| Field | Value | Notes |
|-------|-------|-------|
| Sales Price | 80,000 | Same as Base Price ⚠️ |
| Unit of Measure | Unit | Standard UoM |
| Customer Taxes | VAT 10% | Select from dropdown |
| Sales Description | Full description | What customer sees on invoice |

**⚠️ Important - Price Consistency:**
- **Sales Price** = **Base Price / Device / Month**
- Both should be the same value (80,000 in example)
- Sales Price is what Odoo uses for quotation lines

**Sales Description Template:**
```
DiHub Cloud License - Monthly Subscription

Pricing: 80,000 VND/device/month (before VAT 10%)

Features included:
- Cloud-based content management
- Remote monitoring and control
- Automatic software updates
- Technical support during subscription period
- 99.9% uptime SLA

Billing: Prepaid per period
Minimum: 1 device × 1 month
Payment: 100% advance before activation
```

### Step 7: Configure Purchase Tab (Optional)

**Only if you resell licenses from a vendor:**

| Field | Example | Notes |
|-------|---------|-------|
| Can be Purchased | ✅ Yes | Check if you buy licenses |
| Vendor | [Select vendor] | License provider |
| Vendor Price | 60,000 | Your cost price |
| Vendor Taxes | No tax | Usually tax-exempt for resale |

**Cost Tracking:**
- If you develop the software: Cost = 0 or minimal (server costs)
- If you resell licenses: Cost = vendor price

### Step 8: Add Product Image (Recommended)

Upload product image:
1. Click camera icon in top-left
2. Upload logo or product screenshot
3. Image appears on quotations and invoices

### Step 9: Save Product

Click **Save**

**Verification Checklist:**
- [ ] DTX Type = "Subscription / License theo tháng"
- [ ] Part Number filled
- [ ] Country of Origin filled
- [ ] Base Price / Device / Month = Sales Price
- [ ] Default Duration set (e.g., 12 months)
- [ ] Customer Tax = VAT 10%
- [ ] Unit of Measure = Unit

---

## Part 2: Add Metadata to Existing Products

### When to Add Part Number and Country of Origin

The new fields **Part Number** and **Country of Origin** are available for ALL product types:
- Hardware products (Kiosk, Touch Screen, etc.)
- Component parts (cables, brackets, etc.)
- Services (installation, maintenance)
- Subscriptions (DiHub, SeQMS)

### How to Update Existing Products

**Step 1:** Navigate to product
- Menu: Inventory > Products > Products
- Find product (e.g., "Touch Screen 21 inch")
- Click to open

**Step 2:** Scroll to DTX - Chuẩn hóa sản phẩm section

**Step 3:** Fill metadata
```
Part Number: TS-21-PCAP-001
Country of Origin: China
```

**Step 4:** Save

**Note:** These fields are **optional**. You can leave them empty if:
- Product doesn't have a specific part number
- Origin is not relevant
- Legacy products not yet cataloged

---

## Part 3: Common Product Configurations

### Configuration 1: DiHub Digital Signage

**Use Case:** Cloud-based digital signage license

**Product Setup:**
```
Name: DiHub Cloud License (Device-Month)
Type: Service
DTX Type: Subscription / License theo tháng

Metadata:
- Part Number: DIHUB-LIC-001
- Country of Origin: Vietnam
- Notes: DiHub Digital Signage - Cloud Content Management

Subscription:
- Base Price: 80,000 VND/device/month
- Default Duration: 12 months

Sales:
- Sales Price: 80,000 VND
- UoM: Unit
- Customer Tax: VAT 10%
```

**Quotation Example:**
```
Customer: ABC Company
Product: DiHub Cloud License
Device Count: 15
Months: 12
Start: 2025-12-01

Calculation:
- Quantity: 15 × 12 = 180 device-months
- Subtotal: 180 × 80,000 = 14,400,000 VND
- VAT 10%: 1,440,000 VND
- Total: 15,840,000 VND
```

---

### Configuration 2: SeQMS Online Ticket

**Use Case:** Online queue management subscription

**Product Setup:**
```
Name: SeQMS Online Ticket License (Device-Month)
Type: Service
DTX Type: Subscription / License theo tháng

Metadata:
- Part Number: SEQMS-TICKET-001
- Country of Origin: Vietnam
- Notes: SeQMS Online Queue Management System

Subscription:
- Base Price: 100,000 VND/device/month
- Default Duration: 12 months

Sales:
- Sales Price: 100,000 VND
- UoM: Unit
- Customer Tax: VAT 10%
```

**Quotation Example:**
```
Customer: XYZ Hospital
Product: SeQMS Online Ticket License
Device Count: 20
Months: 6
Start: 2026-01-01

Calculation:
- Quantity: 20 × 6 = 120 device-months
- Subtotal: 120 × 100,000 = 12,000,000 VND
- VAT 10%: 1,200,000 VND
- Total: 13,200,000 VND
```

---

### Configuration 3: DiHub Enterprise (Higher Tier)

**Use Case:** Enterprise version with more features

**Product Setup:**
```
Name: DiHub Enterprise License (Device-Month)
Type: Service
DTX Type: Subscription / License theo tháng

Metadata:
- Part Number: DIHUB-LIC-ENT
- Country of Origin: Vietnam
- Notes: DiHub Enterprise with advanced analytics

Subscription:
- Base Price: 150,000 VND/device/month
- Default Duration: 12 months

Sales:
- Sales Price: 150,000 VND
- UoM: Unit
- Customer Tax: VAT 10%
```

**When to Use:**
- Customer needs advanced features (analytics, API access, etc.)
- Larger deployments (50+ devices)
- SLA requirements (faster support response)

---

## Part 4: Pricing Strategies

### Strategy 1: Flat Rate (Current Implementation)

**Model:** Same price per device regardless of quantity

```
1-10 devices: 80,000 VND/device/month
11-50 devices: 80,000 VND/device/month
51+ devices: 80,000 VND/device/month
```

**Pros:**
- Simple to understand
- Easy to calculate
- No special configuration needed

**Cons:**
- No volume discount incentive
- May lose large deals to competitors

### Strategy 2: Volume Discounts (Manual Adjustment)

**Model:** Adjust price manually based on device count

```
1-10 devices: 80,000 VND/device/month (create quote with this price)
11-50 devices: 70,000 VND/device/month (manually change price_unit)
51+ devices: 60,000 VND/device/month (manually change price_unit)
```

**Implementation:**
1. Create quotation with default price (80,000)
2. Check device count on line
3. Manually adjust Unit Price if in higher tier
4. Add note in description: "Giá ưu đãi cho gói 50+ thiết bị"

**Pros:**
- Flexible for negotiations
- Can adjust per customer

**Cons:**
- Manual work
- Risk of inconsistent pricing

### Strategy 3: Different Products per Tier (Recommended for Scale)

**Model:** Create separate products for each tier

```
Product 1: DiHub License - Starter (1-10 devices)
- Part Number: DIHUB-LIC-START
- Price: 80,000 VND/device/month

Product 2: DiHub License - Business (11-50 devices)
- Part Number: DIHUB-LIC-BUS
- Price: 70,000 VND/device/month

Product 3: DiHub License - Enterprise (51+ devices)
- Part Number: DIHUB-LIC-ENT
- Price: 60,000 VND/device/month
```

**Pros:**
- Clear product catalog
- Accurate reporting by tier
- Can add tier-specific features

**Cons:**
- More products to manage
- Need to choose correct product when creating quote

---

## Part 5: Tax Configuration

### Standard Subscription Tax: VAT 10%

**Navigate:** Accounting > Configuration > Taxes

**Verify Tax Exists:**
- **Name:** VAT 10%
- **Tax Type:** Sales
- **Tax Computation:** Percentage of Price
- **Amount:** 10%
- **Tax Scope:** Services

**If tax doesn't exist, create it:**
1. Click Create
2. Name: VAT 10%
3. Tax Computation: Percentage of Price
4. Amount: 10.00
5. Tax Scope: Services
6. Save

### Apply Tax to Product

In product form (Sales tab):
- **Customer Taxes:** Select "VAT 10%"

### Special Cases

**Tax-exempt customers (e.g., government, export):**

Option 1 - Use tax-exempt pricelist:
1. Create pricelist "Government - Tax Exempt"
2. Remove taxes from pricelist
3. Assign to customer

Option 2 - Manual tax removal:
1. Create quotation normally
2. In SO line, remove tax manually
3. Add note in description: "Miễn VAT - Đơn vị Nhà nước"

---

## Part 6: Unit of Measure (UoM)

### Standard UoM: Unit

**Current setup:**
- Use Odoo standard UoM: **Unit**
- Represents "device-month" in context
- No custom UoM needed

**Why not create custom "Device-Month" UoM?**

❌ **Not Recommended:**
- Adds complexity
- Doesn't improve functionality
- Quantity already calculated correctly (devices × months)

✅ **Current approach (Unit) works because:**
- Quantity field holds total device-months
- Price per Unit = Price per device-month
- Calculation is transparent on quotation

### If You Must Create Custom UoM

**Only if required for reporting/clarity:**

1. Navigate: Inventory > Configuration > UoM > Create
2. **UoM Name:** Device-Month
3. **Category:** Unit (same as "Unit")
4. **Type:** Reference Unit of Measure
5. **Rounding Precision:** 0.01
6. Save

Then in product:
- **Unit of Measure:** Device-Month
- **Purchase Unit of Measure:** Device-Month

---

## Part 7: Product Variants (Advanced)

### When to Use Variants

**Use variants if you have multiple options for same subscription:**

Example: DiHub with different support levels
```
Base Product: DiHub Cloud License
Variants:
- Standard Support (8x5)
- Premium Support (24x7)
- Enterprise Support (24x7 + Dedicated Account Manager)
```

### How to Configure

**Step 1:** Enable variants on product

Product form > Attributes & Variants tab

**Step 2:** Create attribute

Navigate: Inventory > Configuration > Product Attributes > Create
```
Attribute: Support Level
Values:
- Standard (8x5)
- Premium (24x7)
- Enterprise (24x7 + AM)
```

**Step 3:** Add attribute to product

Product > Attributes & Variants > Add a line
- Attribute: Support Level
- Values: All (Standard, Premium, Enterprise)

**Step 4:** Configure variant prices

Product > Variants > Edit each variant
```
DiHub Cloud License - Standard
- Base Price: 80,000 VND/device/month

DiHub Cloud License - Premium
- Base Price: 100,000 VND/device/month
- Extra: +20,000 for 24x7 support

DiHub Cloud License - Enterprise
- Base Price: 150,000 VND/device/month
- Extra: +70,000 for 24x7 + AM
```

### Simplified Approach (Recommended)

**Instead of variants, create separate products:**
- DiHub License - Standard Support
- DiHub License - Premium Support
- DiHub License - Enterprise Support

This is simpler and more flexible for DTX's use case.

---

## Part 8: Product Categories

### Recommended Category Structure

**Navigate:** Inventory > Configuration > Product Categories

**Create hierarchy:**
```
All Products
├── Hardware
│   ├── Kiosk
│   ├── Touch Screen
│   └── Components
├── Services
│   ├── Installation
│   ├── Maintenance
│   └── Subscription Licenses ← NEW
│       ├── DiHub
│       └── SeQMS
```

### Create Subscription Licenses Category

1. Navigate: Inventory > Configuration > Product Categories > Create
2. **Category Name:** Subscription Licenses
3. **Parent Category:** Services
4. **Costing Method:** Standard Price (or FIFO)
5. **Inventory Valuation:** Manual (no inventory for services)
6. Save

### Assign Category to Products

Product form > General Information tab:
- **Product Category:** Services / Subscription Licenses / DiHub

**Benefits:**
- Easy filtering in reports
- Clear product organization
- Can apply category-specific settings (e.g., default taxes)

---

## Part 9: Product Checklist Template

Use this checklist when creating new subscription products:

```
Product Information:
□ Name includes pricing unit (e.g., "Device-Month")
□ Product Type = Service
□ Can be Sold = Yes
□ Can be Purchased = No (unless reselling)

DTX Configuration:
□ DTX Type = "Subscription / License theo tháng"
□ Part Number filled (e.g., DIHUB-LIC-001)
□ Country of Origin filled (e.g., Vietnam)
□ Notes describe the product clearly

Subscription Settings:
□ Base Price / Device / Month set (e.g., 80,000)
□ Default Duration set (typically 12 months)

Sales Configuration:
□ Sales Price = Base Price (must match!)
□ Unit of Measure = Unit
□ Customer Taxes = VAT 10%
□ Sales Description written (clear, detailed)

Optional:
□ Product image uploaded
□ Product category assigned
□ Vendor configured (if reselling)
□ Cost price set (for profit tracking)

Verification:
□ Create test quotation
□ Check auto-calculation works (Quantity = Devices × Months)
□ Check End Date auto-calculates
□ Check Part Number displays on SO line
□ Save test quotation (don't confirm)
```

---

## Part 10: Migration Guide - Updating Existing Products

### Scenario: Adding Metadata to Current Products

**Goal:** Add Part Number and Country of Origin to all existing DTX products

### Hardware Products Example

**Touch Screen 21 inch:**
```
Navigate: Inventory > Products > Products > Touch Screen 21"

Current state:
- DTX Type: device_serialized
- Part Number: (empty)
- Country of Origin: (empty)

Update to:
- DTX Type: device_serialized (no change)
- Part Number: TS-21-PCAP-001
- Country of Origin: China
```

**DTX Kiosk 32 inch:**
```
Current state:
- DTX Type: finished_kiosk
- Part Number: (empty)
- Country of Origin: (empty)

Update to:
- DTX Type: finished_kiosk (no change)
- Part Number: DTX-K32-001
- Country of Origin: Vietnam
```

### Service Products Example

**Installation Service:**
```
Current state:
- DTX Type: service
- Part Number: (empty)
- Country of Origin: (empty)

Update to:
- DTX Type: service (no change)
- Part Number: SVC-INSTALL
- Country of Origin: Vietnam (service location)
```

### Bulk Update (Optional)

If you have many products to update:

1. Export product list: Inventory > Products > Products > ⚙️ > Export
2. Update Excel: Fill Part Number and CO columns
3. Import: ⚙️ > Import > Map columns > Validate > Import

**Note:** Be careful with bulk import - test with a few products first.

---

## Troubleshooting

### Issue 1: Subscription Settings Section Not Appearing

**Symptom:** Can't see "Base Price / Device / Month" field

**Solution:**
1. Check DTX Type = "Subscription / License theo tháng"
2. Save product
3. Refresh page (F5)
4. Section should appear below DTX fields

### Issue 2: Sales Price and Base Price Out of Sync

**Symptom:** Quotation shows wrong price

**Solution:**
- Both fields must have same value
- Update Sales Price to match Base Price
- Save product
- Existing quotations won't update (need manual adjustment)

### Issue 3: Part Number Not Showing on Quotation

**Symptom:** SO line doesn't display Part Number column

**Solution 1 - Enable column:**
1. Open quotation
2. In SO line tree view, click column header (⚙️ icon)
3. Check "Part Number" checkbox

**Solution 2 - Product missing Part Number:**
1. Check product has Part Number filled
2. Save product
3. Remove and re-add line to quotation

### Issue 4: Wrong Tax Applied

**Symptom:** VAT showing as 8% instead of 10%

**Solution:**
1. Open product > Sales tab
2. Check **Customer Taxes** = VAT 10%
3. Save product
4. In quotation, remove and re-add line
5. Or manually change tax on SO line

---

## Best Practices

### 1. Product Naming

✅ **Good:**
- DiHub Cloud License (Device-Month)
- SeQMS Online Ticket License (Device-Month)

❌ **Avoid:**
- DiHub License (unclear pricing unit)
- Digital Signage (too generic)

### 2. Part Number Format

**Consistent structure:**
```
[PRODUCT]-[TYPE]-[VARIANT]

Examples:
DIHUB-LIC-001       Base DiHub license
DIHUB-LIC-ENT       Enterprise version
SEQMS-TICKET-001    Base SeQMS
TS-21-PCAP-001      Touch screen 21" capacitive
```

### 3. Description Quality

**Include in Sales Description:**
- What the product is
- Pricing model
- What's included
- Support terms
- SLA if applicable
- Payment terms

### 4. Price Consistency

**Always ensure:**
- Sales Price = Base Price / Device / Month
- Same value in both fields
- Update both when changing price

### 5. Regular Review

**Quarterly tasks:**
- Review pricing (adjust for cost changes)
- Update product descriptions
- Add new variants as needed
- Archive obsolete products

---

## Related Documentation

- [Subscription Management User Guide](../03_USER_GUIDES/07_SUBSCRIPTION_MANAGEMENT.md)
- [Product Standards Module](../04_TECHNICAL/05_PRODUCT_STANDARDS.md)
- [Technical Documentation](../04_TECHNICAL/07_SUBSCRIPTION_MODULE.md)

---

**Version:** 1.0
**Last Updated:** 2026-01-14
**Module Version:** dtx_product_standards v1.3.0, dtx_sales_pakd_contract v1.6.0
