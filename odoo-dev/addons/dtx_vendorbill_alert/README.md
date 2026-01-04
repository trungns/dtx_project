# DTX Vendor Bill Alert

## Overview

**DTX Vendor Bill Alert** prevents forgetting to create vendor bills for received goods by showing a warning dialog when validating outgoing deliveries that contain serial numbers without vendor bills.

## Key Features

- ✅ **Automatic Detection**: Identifies serials with `vendor_bill_state` in ('unknown', 'missing') during delivery validation
- ✅ **Non-blocking Warning**: Shows dialog with details but allows user to proceed after providing justification
- ✅ **Audit Trail**: Saves notes to each serial number's history with timestamp and picking reference
- ✅ **Chatter Integration**: Posts message to picking's chatter for full traceability
- ✅ **Mobile-friendly**: Simple, clean UI that works on tablets and phones
- ✅ **Performance**: Minimal overhead - only checks outgoing pickings with serials

## How It Works

### Workflow

```
┌─────────────────────────────────────────┐
│  User validates OUTGOING delivery       │
│  (Inventory → Operations → Deliveries)  │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  System checks: Any serials with        │
│  vendor_bill_state = 'missing'/False?   │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴────────┐
        │ NO             │ YES
        ▼                ▼
┌──────────────┐   ┌──────────────────────────────┐
│ Proceed      │   │ Show Warning Dialog with:    │
│ normally     │   │ - Product names              │
│              │   │ - Supplier serial numbers    │
│              │   │ - DTX internal serials       │
│              │   │ - Current bill state         │
└──────────────┘   │ - Required note field        │
                   └────────────┬─────────────────┘
                                │
                                ▼
                   ┌─────────────────────────────┐
                   │ User provides justification │
                   │ e.g., "Will obtain invoice  │
                   │ from supplier next week"    │
                   └────────────┬────────────────┘
                                │
                                ▼
                   ┌─────────────────────────────┐
                   │ System actions:             │
                   │ 1. Append note to each      │
                   │    serial's vendor_invoice_ │
                   │    note with timestamp      │
                   │ 2. Post chatter message     │
                   │ 3. Proceed with validation  │
                   └─────────────────────────────┘
```

### Technical Flow

1. **Override `button_validate` in `stock.picking`**:
   - Only checks pickings with `picking_type_id.code == 'outgoing'`
   - Calls `_get_missing_bill_lots()` to find problematic serials
   - If found and not already confirmed, opens wizard
   - If confirmed (context flag), proceeds normally

2. **Wizard collects justification**:
   - Shows HTML table with serial details
   - Requires user to enter a note
   - On confirm:
     - Appends note to each `stock.lot.vendor_invoice_note`
     - Format: `[YYYY-MM-DD HH:MM:SS] [WH/OUT/00123] User's note`
     - Posts chatter message to picking
     - Re-calls `button_validate` with `vendorbill_alert_confirmed=True` flag

3. **Audit trail preserved**:
   - Serial number history: All notes accumulated in `vendor_invoice_note` field
   - Picking history: Chatter message with list of affected serials
   - Logs: INFO level logs in `odoo.log`

## Dependencies

- **Required Modules**:
  - `stock` (Odoo built-in)
  - `dtx_serial_ext` (DTX custom module)

- **Required Fields** (from `dtx_serial_ext`):
  - `stock.lot.vendor_invoice_state` (selection: 'missing'/'linked'/'replaced')
  - `stock.lot.vendor_invoice_note` (text)
  - `stock.lot.dtx_serial_internal` (char, optional)

## Installation

### 1. Install Dependencies

Ensure `dtx_serial_ext` is installed first:

```bash
# Navigate to Odoo directory
cd /path/to/odoo-dev

# Install dtx_serial_ext if not already installed
docker-compose exec odoo odoo -u dtx_serial_ext -d your_database --stop-after-init
```

### 2. Install dtx_vendorbill_alert

```bash
# Upgrade/install the module
docker-compose exec odoo odoo -u dtx_vendorbill_alert -d your_database --stop-after-init

# Restart Odoo
docker-compose restart odoo
```

### 3. Verify Installation

1. Go to **Apps** → Search "DTX Vendor Bill Alert"
2. Should show as "Installed"
3. No additional configuration needed

## How to Test

### Prerequisites

You need test data with:
- Products tracked by serial number
- Stock lots (serials) with `vendor_bill_state = 'missing'` or `False`
- Outgoing picking with these serials

### Test Scenario 1: Basic Warning Flow

**Setup:**

```python
# Create a product tracked by serial
product = env['product.product'].create({
    'name': 'Test Touch Screen',
    'type': 'product',
    'tracking': 'serial',
})

# Create a serial with missing vendor bill
lot = env['stock.lot'].create({
    'name': 'TOUCH-TEST-001',
    'product_id': product.id,
    'company_id': 1,
    'vendor_invoice_state': 'missing',  # This triggers the warning
    'dtx_serial_internal': 'DTX-T-001',
})

# Ensure stock exists (add to WH/Stock location)
env['stock.quant']._update_available_quantity(
    product,
    env.ref('stock.stock_location_stock'),
    1.0,
    lot_id=lot
)

# Create outgoing delivery
picking_type_out = env.ref('stock.picking_type_out')
partner = env.ref('base.res_partner_1')

picking = env['stock.picking'].create({
    'picking_type_id': picking_type_out.id,
    'location_id': env.ref('stock.stock_location_stock').id,
    'location_dest_id': env.ref('stock.stock_location_customers').id,
    'partner_id': partner.id,
})

# Add move with serial
move = env['stock.move'].create({
    'name': product.name,
    'product_id': product.id,
    'product_uom_qty': 1.0,
    'product_uom': product.uom_id.id,
    'picking_id': picking.id,
    'location_id': picking.location_id.id,
    'location_dest_id': picking.location_dest_id.id,
})

# Confirm picking
picking.action_confirm()
picking.action_assign()

# Set serial on move line
picking.move_line_ids[0].lot_id = lot.id
```

**Test Steps:**

1. Go to **Inventory → Operations → Deliveries**
2. Open the test delivery `WH/OUT/XXXXX`
3. Click **Validate** button
4. **Expected**: Warning dialog appears with:
   - Title: "Warning: Missing Vendor Bills"
   - Table showing: Product, Supplier Serial (TOUCH-TEST-001), DTX Serial (DTX-T-001), Bill State (Missing)
   - Required note field
5. Enter note: "Test - will obtain invoice later"
6. Click **Confirm & Proceed**
7. **Expected**:
   - Delivery validates successfully
   - Serial `TOUCH-TEST-001` has updated `vendor_invoice_note` with timestamp
   - Picking has chatter message about acknowledged warning

**Verify Results:**

```python
# Check serial note was updated
lot = env['stock.lot'].search([('name', '=', 'TOUCH-TEST-001')])
print(lot.vendor_invoice_note)
# Expected: [2026-01-03 XX:XX:XX] [WH/OUT/XXXXX] Test - will obtain invoice later

# Check picking chatter
picking = env['stock.picking'].search([('name', '=', 'WH/OUT/XXXXX')])
messages = picking.message_ids
print(messages[0].body)  # Should contain warning details
```

### Test Scenario 2: Multiple Serials

**Setup:**

```python
# Create 3 serials with missing bills
serials = []
for i in range(1, 4):
    lot = env['stock.lot'].create({
        'name': f'PRINTER-TEST-00{i}',
        'product_id': product.id,
        'vendor_invoice_state': 'missing',
        'dtx_serial_internal': f'DTX-P-00{i}',
    })
    serials.append(lot)

    # Add stock
    env['stock.quant']._update_available_quantity(
        product,
        env.ref('stock.stock_location_stock'),
        1.0,
        lot_id=lot
    )

# Create delivery with 3 moves (one per serial)
# ... follow similar steps as Test 1
```

**Test Steps:**

1. Validate delivery with 3 serials
2. **Expected**: Warning shows all 3 serials in table
3. Enter note: "Bulk purchase without invoices, replacement bills will be linked"
4. Confirm
5. **Expected**: All 3 serials get the same note appended

### Test Scenario 3: No Warning (Normal Flow)

**Setup:**

```python
# Create serial with LINKED vendor bill
lot = env['stock.lot'].create({
    'name': 'CAMERA-TEST-001',
    'product_id': product.id,
    'vendor_invoice_state': 'linked',  # No warning for 'linked'
})
```

**Test Steps:**

1. Create delivery with this serial
2. Click **Validate**
3. **Expected**: No warning dialog, validates immediately

### Test Scenario 4: Mixed Serials

**Setup:**

```python
# Mix of missing and linked serials in same delivery
lot1 = env['stock.lot'].create({
    'name': 'MINI-PC-001',
    'product_id': product.id,
    'vendor_invoice_state': 'missing',  # This triggers warning
})

lot2 = env['stock.lot'].create({
    'name': 'MINI-PC-002',
    'product_id': product.id,
    'vendor_invoice_state': 'linked',  # This is OK
})
```

**Test Steps:**

1. Create delivery with both serials
2. Click **Validate**
3. **Expected**: Warning shows only MINI-PC-001 (not MINI-PC-002)

### Test Scenario 5: Incoming Picking (No Warning)

**Setup:**

```python
# Create INCOMING picking (receipt) with missing bill serial
picking_type_in = env.ref('stock.picking_type_in')

picking = env['stock.picking'].create({
    'picking_type_id': picking_type_in.id,  # INCOMING, not outgoing
    'location_id': env.ref('stock.stock_location_suppliers').id,
    'location_dest_id': env.ref('stock.stock_location_stock').id,
})
# ... add moves with missing bill serials
```

**Test Steps:**

1. Validate INCOMING receipt with missing bill serials
2. **Expected**: No warning (only triggers on OUTGOING)

## Configuration

No configuration needed. The module works out-of-the-box once installed.

## User Permissions

- **Stock User** (`stock.group_stock_user`): Can see and confirm warning
- **Stock Manager** (`stock.group_stock_manager`): Full access

No additional groups required.

## Performance Considerations

- **Negligible overhead**: Only runs on outgoing pickings with serials
- **Optimized query**: Single filtered search on `stock.lot`
- **No database locks**: Non-blocking warning
- **Scales well**: Tested with 100+ serials in single picking

## Troubleshooting

### Warning doesn't appear

**Check:**
1. Is picking type = 'outgoing'? (not incoming/internal)
2. Do move lines have `lot_id` set?
3. Is `dtx_serial_ext` installed?
4. Do serials have `vendor_invoice_state` in ('missing', False)?

**Debug:**

```python
# Check picking type
picking.picking_type_id.code  # Should be 'outgoing'

# Check serials
picking.move_line_ids.mapped('lot_id.vendor_invoice_state')
# Should contain 'missing' or False

# Manual check
missing_lots = picking._get_missing_bill_lots()
print(missing_lots)  # Should not be empty
```

### Note not saved to serial

**Check:**
1. Did you click "Confirm & Proceed" (not Cancel)?
2. Check `vendor_invoice_note` field exists on `stock.lot`
3. Check user has write permission on `stock.lot`

**Debug:**

```python
# Check if note was appended
lot = env['stock.lot'].search([('name', '=', 'YOUR-SERIAL')])
print(lot.vendor_invoice_note)
# Should show: [2026-01-03 XX:XX:XX] [WH/OUT/XXXXX] Your note
```

### Chatter message missing

**Check:**
1. Picking exists and is not cancelled
2. User has access to picking's chatter
3. Check `mail` module is installed (should be by default)

**Debug:**

```python
# Check messages
picking.message_ids.filtered(lambda m: 'Vendor Bill Warning' in (m.subject or ''))
```

## Integration with Other Modules

### dtx_serial_ext (Required)

- Uses `vendor_invoice_state` to detect missing bills
- Updates `vendor_invoice_note` with justification
- Reads `dtx_serial_internal` for display

### Future Integrations (Optional)

- **dtx_ops_project**: Could show project name in warning dialog
- **dtx_vendorbill_dashboard**: Aggregate warning statistics
- **Custom reports**: Use `vendor_invoice_note` for audit reports

## API Reference

### Models

#### `stock.picking` (inherited)

**New Methods:**

- `button_validate()`: Overridden to check for missing bills before validation
- `_get_missing_bill_lots()`: Returns recordset of `stock.lot` with missing bills

#### `dtx.vendor.bill.warning.wizard` (transient)

**Fields:**

- `picking_id` (Many2one): Related delivery order
- `missing_lot_ids` (Many2many): Serials with missing bills
- `missing_lot_count` (Integer, computed): Count of missing serials
- `missing_lot_details` (Html, computed): Formatted HTML table
- `note` (Text, required): User's justification

**Methods:**

- `action_confirm()`: Save notes and proceed with validation
- `action_cancel()`: Close wizard without validating

## Changelog

### Version 1.0.0 (2026-01-03)

**Initial Release:**

- ✅ Warning dialog for outgoing deliveries with missing vendor bills
- ✅ Wizard to collect user justification notes
- ✅ Append notes to serial numbers with timestamp and picking reference
- ✅ Chatter integration for audit trail
- ✅ HTML table display of affected serials
- ✅ Non-blocking validation flow
- ✅ Performance optimized (minimal overhead)
- ✅ Mobile-friendly UI

## License

LGPL-3

## Author

DTX Project Team

## Support

For issues or questions:
- GitHub: https://github.com/your-org/dtx-odoo-modules
- Email: support@dtx.com
