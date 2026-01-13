# External Invoice Number Tracking for MISA Integration (2026-01-13)

**Module:** `dtx_serial_ext` v2.5.0
**Feature:** External invoice number tracking for MISA accounting system integration
**Status:** ✅ IMPLEMENTED & DEPLOYED

---

## Problem

User requirement: Track external invoice numbers from MISA accounting system in Device Serials.

**Context:**
- Company uses MISA external accounting software for actual invoice generation
- Odoo manages operational workflow (PO, SO, inventory)
- Need to link MISA invoice numbers to serials for complete traceability
- Users want to see both Odoo internal records AND external invoice numbers

**User's request:**
> "Tôi cũng muốn thay đổi trường Linked Invoice PO và SO nếu đã có thì hãy điền số hoá đơn PO (là số hoá đơn khách hàng xuất thực tế từ phần mềm bên ngoài) và số SO là số HĐ tôi đã điền vào. NGoài ra, bán hàng xong tôi cũng sẽ xuất hoá đơn từ phần mềm bên ngoài như MISA nên cũng muốn lưu lại đề truy vết sau này."

---

## Solution

### Design Decision: Leverage Odoo Standard Fields

Instead of creating custom fields, we leveraged Odoo's standard `account.move.ref` field:

**Why this approach:**
- `ref` field is Odoo's standard field for external invoice references
- Already used by accounting teams for vendor invoice numbers
- No custom database schema changes required
- Single source of truth
- Follows Odoo best practices

**Implementation:**
1. Added computed display fields on `stock.lot` model
2. Extract invoice numbers from related `account.move` records
3. Display in both tree and form views
4. Read-only (computed automatically)

---

## How It Works

### Data Flow

```
User enters invoice in Accounting module
         ↓
Enters MISA invoice number in 'ref' field
         ↓
Invoice linked to PO/SO via Odoo's standard mechanism
         ↓
Serial auto-linked to PO/SO (existing logic)
         ↓
New computed fields extract 'ref' from invoices
         ↓
Display in Device Serials views
```

### For Vendor Bills

1. **User enters invoice number:**
   - Go to **Accounting > Vendors > Bills**
   - Open vendor bill (or create new)
   - Enter MISA invoice number in **"Vendor Reference"** field (`ref`)
   - Example: "INV-2026-001"
   - Post the bill

2. **Automatic display:**
   - Bill automatically links to PO via `invoice_origin`
   - Serial already linked to PO (existing logic)
   - Computed field extracts `ref` from vendor bills
   - Displays in Device Serials as "Vendor Invoice #"

### For Customer Invoices

1. **User enters invoice number:**
   - Go to **Accounting > Customers > Invoices**
   - Open customer invoice (created from SO)
   - Enter MISA invoice number in **"Reference/Description"** field (`ref`)
   - Example: "S-INV-2026-100"
   - Post the invoice

2. **Automatic display:**
   - Invoice automatically links to SO via `sale_line_ids`
   - Serial already linked to SO (v2.4.2 logic)
   - Computed field extracts `ref` from customer invoices
   - Displays in Device Serials as "Customer Invoice #"

---

## Technical Implementation

### 1. Model Changes (stock_lot.py)

**Added fields:**
```python
# Lines 149-159
vendor_bill_numbers = fields.Char(
    compute='_compute_vendor_bill_numbers',
    string='Vendor Invoice Numbers',
    help='External invoice numbers from vendor bills (from MISA accounting system)',
)

customer_invoice_numbers = fields.Char(
    compute='_compute_customer_invoice_numbers',
    string='Customer Invoice Numbers',
    help='External invoice numbers for customer invoices (from MISA accounting system)',
)
```

**Added compute methods:**
```python
# Lines 516-546
def _compute_vendor_bill_numbers(self):
    """Extract external invoice numbers from vendor bills"""
    for lot in self:
        if lot.vendor_bill_ids:
            bills = lot.vendor_bill_ids.filtered(lambda b: b.state == 'posted')
            numbers = bills.mapped('ref')
            lot.vendor_bill_numbers = ', '.join(filter(None, numbers)) or 'N/A'
        else:
            lot.vendor_bill_numbers = 'N/A'

def _compute_customer_invoice_numbers(self):
    """Extract external invoice numbers from customer invoices"""
    for lot in self:
        if lot.customer_invoice_ids:
            invoices = lot.customer_invoice_ids.filtered(lambda i: i.state == 'posted')
            numbers = invoices.mapped('ref')
            lot.customer_invoice_numbers = ', '.join(filter(None, numbers)) or 'N/A'
        else:
            lot.customer_invoice_numbers = 'N/A'
```

**Logic:**
- Only show numbers from posted invoices (not drafts)
- Multiple invoices: comma-separated list
- No invoices or missing ref: display "N/A"

### 2. View Changes (stock_lot_views.xml)

**Tree View (List):**
```xml
<!-- Lines 34-35 -->
<field name="vendor_bill_numbers" string="Vendor Invoice #" optional="show"/>
<field name="customer_invoice_numbers" string="Customer Invoice #" optional="show"/>
```

**Form View (Detail) - Vendor Section:**
```xml
<!-- Line 95 -->
<field name="vendor_bill_numbers" readonly="1" string="Số hoá đơn NCC (MISA)"/>
```

**Form View (Detail) - Customer Section:**
```xml
<!-- Line 117 -->
<field name="customer_invoice_numbers" readonly="1" string="Số hoá đơn KH (MISA)"/>
```

### 3. Module Version

**Updated __manifest__.py:**
- Version: `16.0.2.4.2` → `16.0.2.5.0`
- Added version 2.5.0 description

---

## User Workflow

### Scenario 1: Vendor Bill

1. **Receive goods with serial:** TOUCHSCREEN10
2. **Vendor sends invoice:** INV-VN-2026-001
3. **User enters in Odoo:**
   - Open vendor bill for PO
   - "Vendor Reference" field: `INV-VN-2026-001`
   - Post bill
4. **Check Device Serials:**
   - List view shows: Vendor Invoice # = "INV-VN-2026-001"
   - Detail view shows: Số hoá đơn NCC (MISA) = "INV-VN-2026-001"

### Scenario 2: Customer Invoice

1. **Sell device:** KIOSK11 in SO S00160
2. **Generate MISA invoice:** S-INV-160-2026
3. **User enters in Odoo:**
   - Open customer invoice for S00160
   - "Reference/Description" field: `S-INV-160-2026`
   - Post invoice
4. **Check Device Serials:**
   - KIOSK11 shows: Customer Invoice # = "S-INV-160-2026"
   - Components (MiniPC12, touchscreen11) also show: Customer Invoice # = "S-INV-160-2026"

### Scenario 3: Multiple Invoices

1. **Serial received in 2 POs with different bills:**
   - PO1 Bill: "INV-001"
   - PO2 Bill: "INV-002"
2. **Device Serials shows:**
   - Vendor Invoice #: "INV-001, INV-002"

---

## Benefits

### For Users

1. **Single View:** See both Odoo invoices and MISA invoice numbers in one place
2. **Traceability:** Complete audit trail from serial → PO/SO → Odoo invoice → MISA invoice
3. **No Duplication:** Invoice numbers stored once in standard Odoo field
4. **Easy Entry:** Use familiar accounting workflow (same fields they already use)
5. **Automatic Display:** No manual linking required, updates automatically

### For Business

1. **MISA Integration:** Bridge between Odoo operations and MISA accounting
2. **Compliance:** Complete invoice tracking for audits and tax compliance
3. **Reconciliation:** Easy to match Odoo records with MISA invoices
4. **Reporting:** Can export Device Serials with external invoice numbers
5. **Cross-System Traceability:** Link operations to financial records

### Technical

1. **Standard Fields:** Uses Odoo's `account.move.ref` field (no custom schema)
2. **Zero Maintenance:** Computed fields always up-to-date
3. **Backward Compatible:** Works with existing invoices that already have ref populated
4. **Minimal Code:** Simple compute methods, low complexity
5. **Scalable:** Works for single or multiple invoices per serial
6. **Performance:** Computed fields, no additional queries

---

## Testing

### Test Case 1: Vendor Bill with MISA Number ✅

**Steps:**
1. Create vendor bill for PO with serial
2. Enter "TEST-INV-001" in Vendor Reference field
3. Post bill
4. Open Device Serials list

**Expected:**
- Vendor Invoice # column shows "TEST-INV-001"
- Click into serial detail
- "Số hoá đơn NCC (MISA)" shows "TEST-INV-001"

### Test Case 2: Customer Invoice with MISA Number ✅

**Steps:**
1. Create customer invoice from SO with serial
2. Enter "CUST-INV-100" in Reference/Description field
3. Post invoice
4. Open Device Serials list

**Expected:**
- Customer Invoice # column shows "CUST-INV-100"
- Click into serial detail
- "Số hoá đơn KH (MISA)" shows "CUST-INV-100"

### Test Case 3: Multiple Invoices ✅

**Steps:**
1. Create 2 vendor bills for same serial with different refs
2. Post both bills

**Expected:**
- Shows comma-separated: "INV-001, INV-002"

### Test Case 4: No Invoice Numbers ✅

**Steps:**
1. Create bill/invoice without entering ref field
2. Post invoice

**Expected:**
- Field shows "N/A"

### Test Case 5: Draft Invoices ✅

**Steps:**
1. Create bill with ref but keep in draft state

**Expected:**
- Field shows "N/A" (only posted invoices counted)

---

## Files Modified

| File | Change | Lines |
|------|--------|-------|
| [models/stock_lot.py](../../odoo-dev/addons/dtx_serial_ext/models/stock_lot.py) | Added 2 fields (149-159) + 2 methods (516-546) | +33 |
| [views/stock_lot_views.xml](../../odoo-dev/addons/dtx_serial_ext/views/stock_lot_views.xml) | Added fields to tree (34-35) and form (95, 117) | +4 |
| [__manifest__.py](../../odoo-dev/addons/dtx_serial_ext/__manifest__.py) | Version bump + description (4, 21-27) | +7 |

**Total:** 44 lines added across 3 files

---

## Deployment

### Completed Steps

1. ✅ Added computed fields to stock_lot.py
2. ✅ Added compute methods for extracting ref from invoices
3. ✅ Updated tree view with new columns
4. ✅ Updated form view with new fields (Vietnamese labels)
5. ✅ Bumped version to 2.5.0
6. ✅ Module upgraded successfully
7. ✅ Odoo restarted
8. ✅ Feature ready for production use

### Deployment Commands Used

```bash
# Restart Odoo
docker restart dtx_odoo16

# Upgrade module
docker exec dtx_odoo16 odoo -u dtx_serial_ext -d dtx_dev --stop-after-init

# Restart Odoo again
docker restart dtx_odoo16
```

---

## Future Considerations

### Potential Enhancements

1. **Search by Invoice Number:**
   - Add to search view to filter by external invoice numbers
   - Would require changing from Char to stored computed field

2. **Invoice Date Display:**
   - Show MISA invoice date alongside number
   - Extract from `invoice_date` field

3. **Bulk Update:**
   - Tool to bulk update ref fields from CSV
   - For historical data migration

4. **Validation:**
   - Check invoice number format
   - Warn on duplicates

5. **Export:**
   - Add to Excel export templates
   - Include in reports

---

## Comparison with Previous Features

This feature follows the same pattern as recent enhancements:

| Feature | Version | Pattern | Status |
|---------|---------|---------|--------|
| Lifecycle State Inheritance | 2.4.1 | Computed + Hook + Cron | ✅ |
| Component Sale Order Linking | 2.4.2 | Computed + Hook + Cron | ✅ |
| External Invoice Tracking | 2.5.0 | Computed (no hook needed) | ✅ |

**Consistent architecture!** ✅

---

## Summary

**Problem:** Need to track MISA external invoice numbers in Device Serials

**Solution:** Leverage Odoo's standard `account.move.ref` field with computed display fields

**Implementation:**
- Added 2 computed Char fields on stock.lot
- Extract ref from related vendor bills and customer invoices
- Display in tree and form views
- Read-only, automatically updated

**Result:**
- ✅ Users can see MISA invoice numbers in Device Serials
- ✅ Single source of truth (account.move.ref)
- ✅ Standard Odoo workflow for data entry
- ✅ Complete traceability from operations to accounting
- ✅ No custom schema changes
- ✅ Zero maintenance overhead

**Version:** dtx_serial_ext v2.5.0

**Date:** 2026-01-13

**Status:** ✅ PRODUCTION READY
