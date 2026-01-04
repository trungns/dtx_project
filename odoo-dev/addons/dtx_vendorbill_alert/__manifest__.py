# -*- coding: utf-8 -*-
{
    'name': 'DTX Vendor Bill Alert',
    'version': '16.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Warning alert when delivering products without vendor bills',
    'description': """
DTX Vendor Bill Alert
=====================
Prevents forgetting to create vendor bills for received goods.

Features:
- Detects outgoing deliveries with serials that have missing vendor bills
- Shows warning dialog listing affected products and serials
- Requires user to provide a note explaining the situation
- Saves notes to serial numbers (stock.lot) with timestamp and picking reference
- Posts chatter message on picking for audit trail
- Non-blocking warning - allows validation to proceed after confirmation

Integration with dtx_serial_ext:
- Uses vendor_bill_state field (unknown/missing/linked/replaced)
- Updates vendor_bill_note field on stock.lot
- Tracks which deliveries had missing bill warnings

Version 1.0.0:
- Initial release with warning wizard
- Chatter integration
- Timestamp and picking reference tracking
    """,
    'author': 'DTX',
    'website': 'https://www.dtx.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'dtx_serial_ext',  # Required for vendor_bill_state and vendor_bill_note fields
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/vendor_bill_warning_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
