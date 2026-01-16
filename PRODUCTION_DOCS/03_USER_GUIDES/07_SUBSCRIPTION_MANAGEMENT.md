# Subscription Management - User Guide

**Module:** dtx_sales_pakd_contract v1.6.0
**Date:** 2026-01-14
**For:** Sales Team, Sales Manager

---

## Overview

This guide explains how to manage prepaid subscription contracts for:
- **DiHub Digital Signage**: Cloud-based digital signage license
- **SeQMS Online Ticket**: Online queue management license

### Key Features

- ✅ Prepaid model: Single invoice per period (not monthly recurring)
- ✅ Auto-calculate Quantity = Devices × Months
- ✅ Track subscription period (start/end dates)
- ✅ Easy renewal with "Renew Contract" wizard
- ✅ Display Part Number and Country of Origin on quotations

---

## Prerequisites

Before creating subscription quotations, ensure:

1. Subscription products are configured (see [Configuration Guide](../02_CONFIGURATION/05_SUBSCRIPTION_PRODUCTS.md))
2. Products have DTX Type = "Subscription / License theo tháng"
3. Base price per device per month is set
4. Customer record exists in system

---

## Part 1: Create Subscription Quotation

### Step 1: Create New Quotation

Navigate to: **Sales > Quotations > Create**

Fill basic information:
- **Customer**: Select customer
- **Expiration**: Set quotation validity date
- **Pricelist**: Select appropriate pricelist
- **Payment Terms**: Prepaid (100% before delivery)

### Step 2: Add Section Header (Optional but Recommended)

Add a line > **Section**

Example section names:
```
A. Chi phí thuê license DiHub (Device-Month)
B. Chi phí SeQMS Online Ticket
```

### Step 3: Add Subscription Product

Click **Add a line** > Select subscription product

Example: **DiHub Cloud License**

**Fields Auto-filled from Product:**
- **Unit Price**: 80,000 VND (from product base price)
- **Months**: 12 (from product default duration)
- **Part Number**: DIHUB-LIC-001 (displayed in column)
- **Country of Origin**: Vietnam (displayed in column)

### Step 4: Fill Subscription Details

**Required Fields:**
- **Device Count**: Enter number of devices (e.g., 10)
- **Months**: Adjust if different from default (e.g., 9)
- **Subscription Start**: Select start date (e.g., 2025-12-01)

**Auto-calculated Fields:**
- **Quantity**: Automatically calculates = 10 × 9 = **90**
- **Subscription End**: Automatically calculates = 2026-08-31

**Price Calculation:**
```
Device Count: 10
Months: 9
Unit Price: 80,000 VND

Quantity: 10 × 9 = 90
Subtotal: 90 × 80,000 = 7,200,000 VND
VAT 10%: 720,000 VND
Total: 7,920,000 VND
```

### Step 5: Add Description (Optional)

In the **Description** field, add human-readable details:

```
Chi phí thuê DiHub Cloud License cho 10 thiết bị
Thời hạn: 9 tháng (từ 01/12/2025 đến 31/08/2026)

Bao gồm:
- Quản lý nội dung từ xa qua Cloud
- Hỗ trợ kỹ thuật trong thời gian thuê
- Cập nhật phần mềm miễn phí
```

### Step 6: Save and Send Quotation

1. Click **Save**
2. Review total amount
3. Click **Send by Email** or **Print**
4. Wait for customer approval

---

## Part 2: Confirm Subscription Order

### Step 1: Confirm Sale Order

When customer approves:

1. Click **Confirm** button
2. Enter contract details:
   - **Contract Number**: e.g., HĐ-2025-DIHUB-001
   - **Signed Date**: Date customer signed
   - **Advance Amount**: If any prepayment received
3. State changes to **Sale Order** (confirmed)

### Step 2: Create Invoice

1. Click **Create Invoice** button
2. Select **Regular Invoice**
3. Click **Create and View Invoice**
4. Review invoice details
5. Click **Confirm** (Post invoice)

### Step 3: Register Payment

1. Click **Register Payment** button
2. Fill payment details:
   - **Journal**: Cash / Bank
   - **Payment Method**: Transfer / Cash / Check
   - **Amount**: Full amount
   - **Payment Date**: Date received
3. Click **Create Payment**

Invoice status changes to **Paid** ✅

---

## Part 3: Renew Subscription Contract

### When to Renew

Renew subscription before expiry date. Example:
- Original period: 2025-12-01 to 2026-08-31
- Remind customer 30 days before expiry (2026-08-01)
- Create renewal quotation

### Step 1: Open Original Sale Order

Navigate to: **Sales > Orders**

Find and open the original confirmed order (e.g., S00123)

**Check:**
- State = **Sale Order** (confirmed)
- Has subscription lines (Device Count, Months visible)

### Step 2: Click "Renew Contract" Button

Button location: Top of form, next to **Create Invoice** button

**Button Visibility:**
- ✅ Visible: SO confirmed + has subscription lines
- ❌ Hidden: SO in draft or no subscription lines

### Step 3: Fill Renewal Wizard

Wizard form shows:

**Original Contract (Readonly):**
- Original Start Date: 2025-12-01
- Original End Date: 2026-08-31

**New Contract Period:**
- **New Start Date**: 2026-09-01 (auto-fills to old end + 1 day)
- **New Duration**: 12 months (editable - change if customer wants different duration)
- **New End Date**: 2027-08-31 (auto-calculated)

**Example: Customer wants 6 months instead:**
- Change **New Duration** to: 6
- **New End Date** recalculates to: 2027-02-28

### Step 4: Create Renewal Quotation

Click **Create Renewal Quotation** button

**System Actions:**
1. Copies original SO to new quotation (state = draft)
2. Updates subscription lines:
   - Start Date: 2026-09-01
   - End Date: 2027-08-31
   - Months: 12 (or your adjusted value)
   - Quantity: Recalculates (e.g., 10 devices × 12 = 120)
3. Clears contract fields (no contract number, signed date, etc.)
4. Links both orders in Chatter:
   - Original SO: "Renewal quotation created: S00456"
   - New SO: "Renews contract: S00123"

### Step 5: Review and Send to Customer

New quotation opens automatically.

**Review:**
- ✅ Device Count same as original
- ✅ Months updated to new duration
- ✅ Start/End dates updated
- ✅ Quantity recalculated
- ✅ Price same (unless price changed)

**Send to customer:**
1. Update **Expiration** date if needed
2. Click **Send by Email**
3. Wait for customer approval
4. Confirm and invoice (same as Part 2)

---

## Part 4: Mixed Quotation (Hardware + Subscription)

### Use Case

Customer buys both hardware and subscription. Example:
- 5× DTX Kiosk 32" (CAPEX hardware)
- DiHub Cloud License for 10 devices × 12 months (Subscription)

### Step 1: Create Quotation with Sections

**Structure:**

```
[Section] A. Phần cứng / Hardware
  [Product] DTX Kiosk 32"
    - Quantity: 5
    - Unit Price: 25,000,000 VND
    - Part Number: DTX-K32-001
    - Country of Origin: China
    - VAT: 8%
    - Subtotal: 135,000,000 VND (with VAT)

[Section] B. Chi phí thuê license / Subscription
  [Product] DiHub Cloud License
    - Device Count: 10
    - Months: 12
    - Start: 2025-12-01
    - End: 2026-11-30
    - Quantity: 120 (auto-calculated)
    - Unit Price: 80,000 VND
    - Part Number: DIHUB-LIC-001
    - Country of Origin: Vietnam
    - VAT: 10%
    - Subtotal: 10,560,000 VND (with VAT)

TOTAL: 145,560,000 VND
```

### Step 2: Field Visibility

**Hardware Line (DTX Kiosk):**
- ✅ Visible: Quantity, Price, Part Number, CO
- ❌ Hidden: Device Count, Months, Subscription Start/End

**Subscription Line (DiHub):**
- ✅ Visible: Quantity, Price, Part Number, CO, Device Count, Months, Start/End
- ✅ Subscription fields only visible for subscription products

### Step 3: Confirm and Invoice

Standard workflow:
1. Confirm order
2. Create invoice (covers both hardware and subscription)
3. Register payment

**Note:** "Renew Contract" button still appears because order has subscription lines. When clicking, wizard will only renew subscription lines (not hardware).

---

## Part 5: Reports and Tracking

### Active Subscriptions Report

**Navigate:** Sales > Orders

**Filter:**
1. State = **Sale Order**
2. Click **Filters** > **Add Custom Filter**
   - Field: **Has Subscription Lines**
   - Operator: **is set**

**Result:** List of all confirmed orders with subscription products

**Optional Columns (click column header > + icon):**
- Subscription Start Date
- Subscription End Date
- Device Count
- Months

### Expiring Contracts

**Method 1: Manual Filter**

Navigate: **Sales > Orders**

Filter:
- State = Sale Order
- Subscription End Date **<=** [Today + 30 days]

**Method 2: Using Activities**

Create activity on SO:
1. Open subscription SO
2. Click **Schedule Activity**
3. Activity Type: **To Do**
4. Summary: "Nhắc gia hạn hợp đồng DiHub"
5. Due Date: [End Date - 30 days]
6. Assigned to: Salesperson

**View activities:** Sales > My Activities

### Revenue by Subscription Product

**Navigate:** Sales > Reporting > Sales

**Group by:**
1. Product
2. Filter by Product Type = Subscription

**Show:**
- Total Revenue
- Number of orders
- Average order value

---

## Common Questions

### Q1: Can I change device count after confirming?

**A:** No, once SO is confirmed, you cannot change subscription fields. Instead:
1. Cancel original SO (if no invoice posted)
2. Create new SO with correct device count

OR (if invoice already posted):
1. Keep original SO as-is
2. Create credit note for wrong invoice
3. Create new SO with correct details

### Q2: What if customer wants to add more devices mid-period?

**A:** Two options:

**Option 1 - New SO for additional devices:**
```
Existing: 10 devices from 2025-12-01 to 2026-11-30
Add: 5 more devices from 2026-06-01 to 2026-11-30

New SO:
- Device Count: 5
- Months: 6 (Jun to Nov)
- Quantity: 5 × 6 = 30
```

**Option 2 - Prorated invoice (manual calculation):**
- Calculate remaining months
- Create manual quotation with adjusted price

### Q3: Can subscription product be used in PAKD?

**A:** Not required. Subscription products can go directly:
- Quotation > Confirm > Invoice > Payment

PAKD is optional if you need cost analysis (e.g., license resale with cost).

### Q4: How to handle early termination?

**A:** Manual process:
1. Calculate unused months
2. Create credit note for refund amount
3. Update subscription end date in notes
4. Mark SO as terminated in Chatter

### Q5: Part Number not showing on my old products?

**A:** Part Number is optional. To add:
1. Navigate: Inventory > Products > [Product]
2. Scroll to **DTX - Chuẩn hóa sản phẩm**
3. Fill **Part Number / Mã sản phẩm**
4. Fill **Country of Origin / Xuất xứ**
5. Save

---

## Best Practices

### 1. Naming Convention for Subscription Products

Use clear names indicating pricing unit:

✅ Good:
- DiHub Cloud License (Device-Month)
- SeQMS Online Ticket (Device-Month)

❌ Avoid:
- DiHub License
- SeQMS (unclear pricing)

### 2. Product Description Template

Always include in product Notes:
```
[Product Name] - Subscription Model

Pricing:
- Base: [X] VND/device/month (before VAT)
- VAT: 10%
- Total: [Y] VND/device/month

Included:
- [Feature 1]
- [Feature 2]
- Support during subscription period
```

### 3. Quotation Line Description

Be specific about what's included:
```
Chi phí thuê DiHub Cloud License cho [N] thiết bị
Thời hạn: [M] tháng (từ DD/MM/YYYY đến DD/MM/YYYY)

Bao gồm:
- Tính năng A
- Tính năng B
- Hỗ trợ kỹ thuật
```

### 4. Renewal Reminders

Set activities 30 days before expiry:
- **Due Date**: End Date - 30 days
- **Assigned**: Original salesperson
- **Summary**: "Nhắc gia hạn: [Customer] - [Product] - expires [Date]"

### 5. Track Contract Status in Chatter

Use Chatter messages for important events:
- Customer requested renewal
- Price negotiation notes
- Special terms agreed
- Termination requests

---

## Troubleshooting

### Issue 1: Quantity Not Auto-calculating

**Symptom:** Quantity stays at 1 even after entering device count and months

**Causes & Solutions:**

1. **Product type not subscription:**
   - Open product > Check DTX Type = "Subscription / License theo tháng"

2. **One field empty:**
   - Ensure BOTH Device Count AND Months are filled
   - Auto-calculation only works when both have values

3. **Manual quantity override:**
   - If you manually changed quantity, auto-calculation stops
   - Change device count or months to trigger recalculation

### Issue 2: End Date Not Auto-calculating

**Symptom:** End date stays empty

**Causes & Solutions:**

1. **Start date empty:**
   - Fill Subscription Start Date first

2. **Months empty:**
   - Fill Months field

3. **Invalid start date:**
   - Check date format is correct (YYYY-MM-DD)

### Issue 3: "Renew Contract" Button Not Visible

**Symptom:** Button missing on confirmed SO

**Causes & Solutions:**

1. **SO not confirmed:**
   - State must be "Sale Order" (not Draft or Quotation Sent)
   - Click Confirm first

2. **No subscription lines:**
   - SO must have at least one product with DTX Type = Subscription
   - Check product type

3. **Browser cache:**
   - Refresh page (Ctrl+F5 or Cmd+Shift+R)
   - Clear browser cache

### Issue 4: Part Number Not Showing on SO Line

**Symptom:** Part Number column empty on quotation

**Causes & Solutions:**

1. **Product missing Part Number:**
   - Open product > Fill "Part Number / Mã sản phẩm"
   - Save product
   - Refresh quotation

2. **Column hidden:**
   - In SO line tree view, click column header gear icon
   - Enable "Part Number" column

---

## Related Documentation

- [Subscription Product Configuration](../02_CONFIGURATION/05_SUBSCRIPTION_PRODUCTS.md)
- [PAKD User Guide](./04_PAKD_WORKFLOW.md)
- [Contract Cost Tracking](./05_CONTRACT_COST_TRACKING.md)
- [Technical Documentation](../04_TECHNICAL/07_SUBSCRIPTION_MODULE.md)

---

**Version:** 1.0
**Last Updated:** 2026-01-14
**Module Version:** dtx_sales_pakd_contract v1.6.0
