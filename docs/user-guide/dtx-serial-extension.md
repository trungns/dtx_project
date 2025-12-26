# DTX Serial Extension

## Overview

Extends Odoo 16 Community `stock.lot` (serial/lot numbers) with device lifecycle management specifically designed for DTX smart queue management system operations.

## Features

### 1. Dual Serial Number Tracking
- **Supplier Serial** (stock.lot.name): Primary key, used for supplier warranty
- **DTX Internal Serial** (dtx_serial_internal): Optional customer-facing serial
- Both serials searchable and displayed together in views

### 2. Device Lifecycle State Tracking
Automatic state transitions based on stock moves:
- **In Stock**: Device in warehouse
- **Allocated to Project**: Reserved for specific project
- **Delivered**: Shipped to customer
- **Installed**: Deployed at customer site
- **Under Maintenance**: In repair/maintenance
- **Scrapped**: Disposed/written off

### 3. Vendor Invoice Tracking
Solves the real-world problem of receiving goods before invoices:
- **Invoice State**: Missing / Linked / Replaced
- Auto-updates when invoice reference is entered
- Stores invoice number, date, and notes
- Enables warning system for deliveries without vendor invoice

### 4. Warranty Management
- Start and end dates
- Active/inactive indicator
- Visible in serial form view

### 5. Documentation Links
- Google Drive link field for device documentation
- Easy access from serial record

## Technical Details

### Models Extended
- `stock.lot`: Main extension with new fields
- `stock.move.line`: Auto-update logic on stock moves

### Automatic Behaviors

#### Lifecycle State Updates
Triggered on stock move validation (`_action_done`):
- Receiving from supplier → `stock`
- Delivery to customer → `delivered`
- Transfer to maintenance location → `maintenance`
- Scrap location → `scrapped`
- Return from customer → `stock`

#### Vendor Invoice Auto-Link
When a purchase order bill is posted, serials from that PO are automatically linked to the invoice.

#### Vendor Invoice State Auto-Update
When `vendor_invoice_ref` is filled, state changes from `missing` to `linked` automatically (can be overridden manually).

### Views

#### Tree View
Displays key fields with color-coded badges:
- Lifecycle state (green=stock/installed, blue=allocated, yellow=maintenance, red=scrapped)
- Vendor invoice state (red=missing, green=linked, yellow=replaced)

#### Form View
Mobile-friendly layout with sections:
- Serial Numbers & Basic Info
- Lifecycle & References
- Vendor Invoice Information
- Warranty Information
- Documentation

#### Search View
Filters:
- By lifecycle state
- By invoice state
- Warranty active
- Group by lifecycle/invoice state/customer

### Menu
New menu item: **Inventory > Products > Device Serials**

## Installation

1. Copy `dtx_serial_ext` folder to your Odoo addons directory
2. Update apps list: Settings > Apps > Update Apps List
3. Install: Search "DTX Serial Extension" and click Install

## Configuration

No configuration needed. The module works immediately after installation.

### Recommended Product Setup
For devices you want to track:
1. Go to product form
2. Set **Product Type**: Storable Product
3. Set **Tracking**: By Unique Serial Number
4. Set **Product Category** with:
   - **Costing Method**: Average Cost (AVCO)
   - **Inventory Valuation**: Automated

## Usage

### Creating Serial Numbers
Serial numbers are created automatically when:
1. Receiving devices via Purchase Order
2. Manufacturing finished goods
3. Manual creation via Inventory > Products > Device Serials

### Tracking Lifecycle
States update automatically based on stock moves. Manual override available anytime by editing the serial record.

### Vendor Invoice Tracking
1. When receiving device without invoice: state = `missing`
2. When vendor bill arrives, enter invoice reference in serial form
3. State auto-updates to `linked`
4. If invoice is replaced/corrected, manually change state to `replaced` and add notes

### Search & Filter
Use search bar to find serials by:
- Supplier serial number
- DTX internal serial number
- Customer name
- Invoice reference

Use filters to view:
- All devices in specific lifecycle state
- Devices missing vendor invoices
- Devices under active warranty

## Dependencies

- `stock` (Odoo standard)
- `product` (Odoo standard)

## Compatibility

- Odoo 16 Community Edition
- Tested on: 16.0

## License

LGPL-3

## Author

DTX - Smart Queue Management Systems

## Support

For issues or questions, contact DTX development team.
