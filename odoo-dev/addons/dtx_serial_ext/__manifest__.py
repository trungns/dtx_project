# -*- coding: utf-8 -*-
{
    'name': 'DTX Serial Extension',
    'version': '16.0.2.5.0',
    'category': 'Inventory/Inventory',
    'summary': 'Extended serial/lot tracking for DTX device lifecycle management',
    'description': """
DTX Serial Extension
====================
Extends stock.lot (serial/lot numbers) with:
- DTX internal serial number (optional, searchable)
- Device lifecycle state tracking
- Project and customer references
- Purchase order & vendor bill tracking (automated via stock moves)
- Sales order & customer invoice tracking (automated via stock moves)
- Vendor invoice state tracking (missing/linked/replaced) - FULLY AUTOMATIC
- Manual replacement invoice linking for special cases
- Warranty period tracking
- Google Drive link for device documentation

Version 2.5.0:
- **NEW**: External invoice number tracking for MISA accounting integration
- Display vendor invoice numbers from MISA on Device Serials
- Display customer invoice numbers from MISA on Device Serials
- Uses Odoo standard 'ref' field on account.move for invoice numbers
- Visible in both tree view (list) and form view (detail)
- No custom schema changes - leverages existing Odoo fields

Version 2.4.2:
- **ENHANCEMENT**: Components now auto-link to Sale Orders via finished product
- Hook automatically updates sale_order_ids when stock moves done
- Scheduled action recomputes sale orders daily for production serials
- Components show which SO their finished product was sold in
- Also updates customer invoices and invoice state for components

Version 2.4.1:
- **FIX**: Components stuck in production location now inherit finished product state
- Handles case where components have quants in production location after MO done
- Components with quants in 'production' location check if consumed in MO
- If finished product is delivered, component inherits 'delivered' state
- Fixes MiniPC12, touchscreen11 not showing 'delivered' after KIOSK delivered

Version 2.4.0:
- **FIX**: Consumed components now inherit lifecycle state from finished product
- When serial is consumed in manufacturing (no quants), check finished product state
- Components in delivered kiosk now correctly show 'delivered' status
- Supports recursive state inheritance for multi-level BOM

Version 2.3.0:
- **NEW**: Auto-computed lifecycle state based on current location
- **NEW**: x_lifecycle_state field tracks location-based state
- States: in_stock, subcontracted, in_production, delivered, maintenance, scrapped
- Automatically updated when serial moves between locations
- Shown in tree/form views with color badges
- **FIX**: Subcontracted serials now show correct state

Version 2.2.0:
- NEW: Replacement Invoice field for manual bill linking
- Support for devices purchased without original invoice
- Can link invoice from another PO as replacement
- Auto-compute includes both auto-linked and replacement invoices
- State automatically becomes 'replaced' when replacement invoice is set

Version 2.1.1:
- CRITICAL FIX: Added account.move hooks for TRUE auto-update
- Vendor invoice state now updates when bills posted/cancelled/draft
- Added logging for bill state changes
- Fixed dependency chain issue in computed fields

Version 2.1.0:
- MAJOR: Vendor invoice state now AUTO-COMPUTES from vendor bills
- Automatically updates when bills are posted (no manual trigger needed)
- State changes instantly when bills appear/disappear
- Manual override still possible for 'replaced' state
- Removed manual check logic from stock moves (no longer needed)

Version 2.0.1:
- Added comprehensive error handling and logging
- Fixed "Missing Record" error with exists() checks
- Improved debugging capabilities

Version 2.0.0:
- Refactored to use Many2many relationships to PO/SO/Invoices
- Removed manual invoice reference fields
- Automatic linking via Odoo's stock move system

Designed for DTX smart queue management system operations.
    """,
    'author': 'DTX',
    'website': 'https://www.dtx.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'product',
        'purchase',      # Required for purchase.order and vendor bill tracking
        'sale',          # Required for sale.order tracking
        'account',       # Required for account.move (invoices/bills)
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_lot_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
