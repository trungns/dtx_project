{
    'name': 'DTX Subcontracting Auto Resupply',
    'version': '16.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Automatically create Resupply pickings for subcontracting Purchase Orders',
    'description': """
Automatically creates Resupply pickings when confirming Purchase Orders
that have products with subcontracting BOMs.

Features:
- Auto-detects subcontracting BOMs
- Creates Resupply picking with components
- Links pickings to Purchase Order
- Validates stock availability
    """,
    'author': 'DTX Project',
    'depends': [
        'purchase',
        'stock',
        'mrp',
        'mrp_subcontracting',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
