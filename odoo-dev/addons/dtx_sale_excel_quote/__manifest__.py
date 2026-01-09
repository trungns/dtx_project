# -*- coding: utf-8 -*-
{
    'name': 'DTX Sale Excel Quotation',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Export/Import Sale Quotations using DTX Excel Template',
    'description': """
DTX Sale Excel Quotation
=========================
Export and Import Sale Quotations using standardized Excel template.

Features:
- Export quotation to Excel matching DTX template format
- Import quotation from Excel with validation
- Support for sections, notes, and product lines
- VAT calculation with 0%, 8%, 10% rates
- Template-based export preserving format and formulas
- Replace or Append mode for import

Template Structure:
- Header: Company info, Customer info, Sales info
- Product table: STT | MÔ TẢ | MÃ SP | XUẤT XỨ | ĐVT | SL | ĐƠN GIÁ | VAT | TỔNG GIÁ | THÀNH TIỀN
- Footer: Totals with formulas

Version 1.0.0:
- Initial release
- Export quotation to Excel
- Import quotation from Excel
- VAT mapping (0%, 8%, 10%)
- Section/Note/Product line support
    """,
    'author': 'DTX',
    'website': 'https://www.dtx.com',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_management',
        'product',
    ],
    'external_dependencies': {
        'python': ['openpyxl'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizards/sale_excel_import_wizard_views.xml',
    ],
    'assets': {},
    'installable': True,
    'auto_install': False,
    'application': False,
}
