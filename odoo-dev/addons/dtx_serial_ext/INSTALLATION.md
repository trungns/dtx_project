# DTX Serial Extension - Installation & Testing Guide

## Module Structure

```
dtx_serial_ext/
├── __init__.py
├── __manifest__.py
├── README.md
├── INSTALLATION.md (this file)
├── models/
│   ├── __init__.py
│   ├── stock_lot.py          # Main serial extension
│   └── stock_move_line.py    # Auto-update logic
├── views/
│   └── stock_lot_views.xml   # Enhanced UI
├── security/
│   └── ir.model.access.csv   # Access rights
└── static/
    └── description/
        └── index.html        # Module description
```

## Installation Steps

### 1. Prerequisites
- Odoo 16 Community Edition installed
- Standard `stock` and `product` modules installed
- Database with admin access

### 2. Copy Module to Addons
```bash
# Option A: Copy to custom addons directory
cp -r dtx_serial_ext /path/to/odoo/custom-addons/

# Option B: Copy to default addons directory
cp -r dtx_serial_ext /path/to/odoo/addons/
```

### 3. Update Odoo Configuration (if using custom addons)
Edit your `odoo.conf`:
```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/odoo/custom-addons
```

### 4. Restart Odoo Server
```bash
# If running as service
sudo systemctl restart odoo

# If running manually
./odoo-bin -c /path/to/odoo.conf
```

### 5. Update Apps List
1. Login as admin
2. Go to: **Settings → Apps**
3. Click: **Update Apps List** (top-right corner, may be in debug mode)
4. Confirm the update

### 6. Install Module
1. Remove "Apps" filter in search box
2. Search: "DTX Serial Extension"
3. Click: **Install**

## Post-Installation Configuration

### 1. Configure Product Category for Devices

1. Go to: **Inventory → Configuration → Product Categories**
2. Create or edit category "DTX Devices":
   - **Category Name**: DTX Devices
   - **Costing Method**: Average Cost (AVCO)
   - **Inventory Valuation**: Automated
   - **Force Removal Strategy**: FIFO

### 2. Configure Device Products

For each device product (kiosk, screen, printer, etc.):

1. Go to: **Inventory → Products → Products**
2. Open product (or create new)
3. Set:
   - **Product Type**: Storable Product
   - **Tracking**: By Unique Serial Number
   - **Product Category**: DTX Devices
   - **Cost**: Will be auto-calculated from purchases

### 3. Configure Warehouse Locations (Optional)

If you want automatic maintenance state detection:

1. Go to: **Inventory → Configuration → Locations**
2. Create location: **WH/Stock/Maintenance**
   - **Location Name**: Maintenance
   - **Parent Location**: WH/Stock
   - **Location Type**: Internal Location

## Testing Guide

### Test 1: Create Serial with Basic Info

1. Go to: **Inventory → Products → Device Serials**
2. Click: **Create**
3. Fill:
   - **Lot/Serial Number**: TEST-SN-001
   - **DTX Internal Serial**: DTX-TEST-001
   - **Product**: Select a device product
   - **Vendor Invoice State**: Missing (default)
   - **Lifecycle State**: In Stock (default)
4. Save

**Expected Result:**
- Serial created successfully
- Display name shows: "TEST-SN-001 [DTX-TEST-001]"
- State badges show correct colors

### Test 2: Search by Both Serials

1. Go to: **Inventory → Products → Device Serials**
2. Search for: "DTX-TEST-001"
3. Should find the serial created in Test 1

**Expected Result:**
- Search works for both supplier serial and DTX internal serial

### Test 3: Vendor Invoice Auto-Update

1. Open serial from Test 1
2. Fill **Vendor Invoice Reference**: "INV-2025-001"
3. Save

**Expected Result:**
- **Vendor Invoice State** auto-changes to "Linked"
- Badge turns green

### Test 4: Warranty Active Indicator

1. Open serial from Test 1
2. Set:
   - **Warranty Start**: 2025-01-01
   - **Warranty End**: 2026-12-31
3. Save

**Expected Result:**
- **Warranty Active** toggle shows as ON (if today is between dates)

### Test 5: Lifecycle Auto-Update on Receipt

1. Create Purchase Order:
   - **Vendor**: Select a supplier
   - **Order Line**: 1x device product
2. Confirm PO
3. Click: **Receive Products**
4. In receipt form:
   - Click on product line
   - Enter serial: "TEST-SN-002"
   - Set **Lot/Serial Number**: TEST-SN-002
5. Validate receipt

**Expected Result:**
- New serial "TEST-SN-002" created automatically
- **Lifecycle State**: In Stock
- **Vendor Invoice State**: Missing

### Test 6: Lifecycle Auto-Update on Delivery

1. Create Sales Order for the device
2. Confirm SO
3. Click: **Delivery**
4. Select serial "TEST-SN-002"
5. Validate delivery

**Expected Result:**
- Serial "TEST-SN-002" **Lifecycle State** changes to "Delivered"
- Chatter message logged with state change

### Test 7: Filter and Group

1. Go to: **Inventory → Products → Device Serials**
2. Use filters:
   - Click "Filters"
   - Select "Invoice Missing"

**Expected Result:**
- Shows only serials with missing vendor invoices

3. Group by:
   - Click "Group By"
   - Select "Lifecycle State"

**Expected Result:**
- Serials grouped by their lifecycle state

### Test 8: Vendor Invoice Auto-Link from PO

1. Create Purchase Order with serial tracking product
2. Confirm and receive (create serial during receipt)
3. Go to: **Purchase → Vendor Bills**
4. Create bill for the PO
5. Post the bill

**Expected Result:**
- Serial from that PO automatically links to vendor invoice
- Check serial: **Vendor Invoice Reference** should show bill number

### Test 9: Maintenance Location Transfer

1. Go to: **Inventory → Operations → Transfers**
2. Create internal transfer:
   - **Source**: WH/Stock
   - **Destination**: WH/Stock/Maintenance
   - **Product**: Device with serial "TEST-SN-002"
3. Validate

**Expected Result:**
- Serial "TEST-SN-002" **Lifecycle State** changes to "Under Maintenance"

### Test 10: Mobile View Test

1. Access Odoo from mobile browser or Odoo mobile app
2. Go to: **Device Serials**
3. Open a serial record

**Expected Result:**
- Form displays cleanly without horizontal scrolling
- All sections readable and editable
- Status bar visible at top

## Verification Checklist

After installation, verify:

- [ ] Module appears in Apps list
- [ ] Menu item "Device Serials" appears under Inventory → Products
- [ ] Can create serial with both supplier and DTX serial
- [ ] Search works for both serial fields
- [ ] Vendor invoice state auto-updates when ref is entered
- [ ] Lifecycle state changes automatically on stock moves
- [ ] Warranty active indicator works correctly
- [ ] Filters (lifecycle, invoice state) work
- [ ] Group by works
- [ ] Chatter logs state changes
- [ ] Forms are mobile-friendly

## Troubleshooting

### Module Not Appearing in Apps List
- Check if module is in addons path: `odoo.conf` → `addons_path`
- Restart Odoo server
- Update Apps List with admin user

### Permission Errors
- Check: **Settings → Users & Companies → Users**
- Ensure user has "Inventory / User" or "Inventory / Administrator" rights

### Lifecycle State Not Updating
- Check stock move is validated (done state)
- Check destination location type (internal/customer/etc.)
- Check chatter for error messages

### Vendor Invoice Not Auto-Linking
- Ensure bill is in "Posted" state
- Check bill is linked to correct PO
- Check serial was created from that PO receipt

## Uninstallation

**WARNING: Uninstalling will remove all DTX-specific data (DTX serials, invoice refs, lifecycle states, etc.)**

1. Go to: **Settings → Apps**
2. Search: "DTX Serial Extension"
3. Click: **Uninstall**
4. Confirm

Standard serial/lot records will remain, but extended fields will be removed.

## Support

For issues or questions:
- Check this guide first
- Review module README.md
- Contact DTX development team

## Next Steps

After successful installation and testing:
1. Import/create your device products
2. Configure product categories with AVCO costing
3. Start receiving devices with serial tracking
4. Monitor vendor invoice states
5. Track device lifecycle

When ready, proceed with:
- **dtx_vendorbill_alert** module (warning on delivery without invoice)
- **dtx_ops_project** module (project/contract management)
