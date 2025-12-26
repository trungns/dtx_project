# -*- coding: utf-8 -*-
{
    'name': 'DTX Serial Extension',
    'version': '16.0.2.2.0',
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
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
