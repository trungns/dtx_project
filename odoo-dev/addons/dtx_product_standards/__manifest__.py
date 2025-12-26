# -*- coding: utf-8 -*-
{
    'name': 'DTX Product Standards',
    'version': '16.0.1.1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Chuẩn hóa danh mục sản phẩm DTX & nền tảng sản xuất kiosk',
    'description': """
DTX Product Standards
=====================
Chuẩn hóa dữ liệu sản phẩm để:
- Giảm sai sót khi nhập liệu
- Phân loại rõ ràng: Thiết bị Serial, Linh kiện, Kiosk, Dịch vụ
- Chuẩn bị nền tảng cho sản xuất & gia công thuê ngoài
- Thay thế tư duy Excel bằng quy trình chuẩn hóa

Tính năng chính:
- Phân loại sản phẩm DTX (4 loại)
- Tab kiểm tra nhanh cấu hình sản phẩm
- Wizard áp dụng chuẩn hàng loạt
- BOM Template cho Kiosk (Excel-style, không ERP hóa)
- Hỗ trợ subcontracting cơ bản
- Không ép buộc workflow, chỉ hỗ trợ

Version 1.1.0:
- NEW: BOM Template for Kiosk manufacturing
- Simple component list management
- Generate/update real mrp.bom from template
- Subcontracting support (basic)

Designed for DTX smart queue management system operations.
    """,
    'author': 'DTX',
    'website': 'https://www.dtx.com',
    'license': 'LGPL-3',
    'depends': [
        'product',
        'stock',
        'purchase',
        'sale',
        'mrp',  # For BOM management
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/dtx_bom_template_views.xml',
        'wizards/apply_dtx_standards_wizard_views.xml',
        'wizards/bom_generate_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
