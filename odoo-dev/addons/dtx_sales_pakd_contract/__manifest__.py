# -*- coding: utf-8 -*-
{
    'name': 'DTX Sales PAKD Contract',
    'version': '16.0.1.5.0',
    'category': 'Sales',
    'summary': 'Phương Án Kinh Doanh (PAKD) và quản lý hợp đồng cho Sales Order',
    'description': """
DTX Sales PAKD Contract
=======================
Quản lý Phương Án Kinh Doanh (PAKD) và Hợp đồng tích hợp với Sales Order.

Tính năng chính:
- Extend sale.order với các field hợp đồng (số HĐ, ngày ký, file scan...)
- Model PAKD riêng biệt: nhiều PAKD cho 1 quotation
- PAKD line với giá nhập/giá bán/giá hợp đồng/VAT/profit
- Map VAT% tự động sang account.tax
- Wizard Apply PAKD → cập nhật sale.order.line
- **Chi phí hợp đồng thực tế** (v1.1.0): Import từ PAKD + chi phí phát sinh
- **Danh sách hợp đồng** (v1.1.0): Theo dõi lãi/lỗ theo từng hợp đồng
- **AR Aging** (v1.2.0): Tổng hợp tuổi nợ phải thu theo bucket
- **PAKD Excel formulas** (v1.3.0): Công thức chính xác theo file Excel template
- Security groups: CEO, Sales Director, Chief Accountant, Sales User
- Record rules phân quyền theo owner
- UI gọn nhẹ, ẩn field không dùng cho DTX
- Upload file scan hợp đồng (PDF/JPG)
- Tương thích data cũ, không phá workflow core

Version 1.5.0:
- **FEATURE**: Contract Cost detailed profit analysis per line
- **NEW**: Auto-populate purchase price from Purchase Orders (readonly, blue background)
- **NEW**: Auto-populate sale price from Sale Orders (editable)
- **NEW**: Manual price entry for lines without PO (license, misc costs)
- **NEW**: Profit and margin calculation per line
- **NEW**: Color coding - green for profit, red for loss
- **IMPROVE**: Professional management view with full cost visibility

Version 1.4.0:
- **FIX**: Allow CEO and GDKD to edit approved PAKD (remove view readonly attrs)
- **FIX**: Skip section/note lines in import_pakd_costs (prevent errors)
- **FIX**: Better validation in action_create_pakd (check for product lines)
- **FEATURE**: Add commission tracking (x_customer_commission, x_referrer_commission)
- **FEATURE**: Add net profit fields (x_net_profit, x_net_profit_margin)

Version 1.3.0:
- **CRITICAL FIX**: PAKD formulas now match Excel template exactly
- Add new fields: cushion_amount, referral_commission_percent
- Fix tax_withheld_amount: base is price_diff (not total_contract_untaxed)
- Fix customer_support_cost: computed as cushion + commission
- Fix referral_commission: computed from percentage
- Update field labels to match Excel PAKD template
- Restructure "Tổng kết" tab with numbered rows matching Excel

Version 1.2.0:
- Add AR Aging report with bucket classification
- Add x_ar_* fields on sale.order (residual, days overdue, status)
- SQL view for performance with 10K+ invoices
- Configurable aging buckets (default: 7/15/30/60/90 days)

Version 1.1.0:
- Add dtx.contract.cost model for actual cost tracking
- Add contract list view with financial analysis
- Import costs from approved PAKD
- Track planned vs actual costs with variance
- Support additional costs outside PAKD
- Compute profit and margin per contract

Version 1.0.0:
- Initial release
- Multi-PAKD per quotation
- Contract fields on sale.order
- Auto VAT mapping
- Apply wizard with price override
- Security groups and record rules
    """,
    'author': 'DTX',
    'website': 'https://www.dtx.com',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_management',
        'sale_stock',
        'stock',
        'purchase',
        'purchase_stock',
        'account',
        'product',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/sale_order_views.xml',
        'views/sale_order_stock_views.xml',
        'views/dtx_pakd_views.xml',
        'views/contract_cost_views.xml',
        'views/contract_list_views.xml',
        'views/dtx_ar_aging_views.xml',
        'wizards/pakd_apply_wizard_views.xml',
        'wizards/create_purchase_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dtx_sales_pakd_contract/static/src/css/pakd_view.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
