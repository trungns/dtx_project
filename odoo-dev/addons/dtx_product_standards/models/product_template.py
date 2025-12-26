# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ==========================================
    # SECTION A: DATA MODEL - CHUẨN HÓA LOẠI SẢN PHẨM
    # ==========================================

    x_dtx_type = fields.Selection(
        selection=[
            ('device_serialized', 'Thiết bị quản lý theo Serial'),
            ('component_untracked', 'Linh kiện / vật tư tiêu hao (không quản lý Serial)'),
            ('finished_kiosk', 'Kiosk / Thiết bị hoàn chỉnh'),
            ('service', 'Dịch vụ (không quản lý kho)'),
        ],
        string='Loại sản phẩm DTX',
        help='Phân loại sản phẩm theo chuẩn DTX để dễ quản lý và giảm sai sót',
        tracking=True,
    )

    x_dtx_requires_vendor_bill = fields.Boolean(
        string='Bắt buộc có hóa đơn đầu vào',
        default=True,
        help='Thiết bị phần cứng thường cần hóa đơn đầu vào để đảm bảo chứng từ.',
        tracking=True,
    )

    x_dtx_notes = fields.Text(
        string='Ghi chú nghiệp vụ DTX',
        help='Ghi chú về cách sử dụng, đặc điểm, yêu cầu đặc biệt của sản phẩm này',
    )

    # ==========================================
    # SECTION B: CHECKLIST NGHIỆP VỤ (READ-ONLY)
    # ==========================================

    x_dtx_check_serial_enabled = fields.Boolean(
        string='✓ Đã bật quản lý Serial?',
        compute='_compute_dtx_checklist',
        help='Kiểm tra xem sản phẩm đã được cấu hình quản lý theo serial chưa',
    )

    x_dtx_check_avco_costing = fields.Boolean(
        string='✓ Danh mục giá vốn là Bình quân (AVCO)?',
        compute='_compute_dtx_checklist',
        help='Kiểm tra xem danh mục sản phẩm có dùng phương pháp tính giá vốn Bình quân (AVCO) không',
    )

    x_dtx_check_has_bom = fields.Boolean(
        string='✓ Kiosk đã có BOM?',
        compute='_compute_dtx_checklist',
        help='Nếu là Kiosk thì cần có BOM (Bill of Materials) để sản xuất/lắp ráp',
    )

    x_dtx_check_can_purchase = fields.Boolean(
        string='✓ Cho phép mua hàng?',
        compute='_compute_dtx_checklist',
        help='Kiểm tra xem sản phẩm có thể tạo đơn mua hàng không',
    )

    x_dtx_check_can_sell = fields.Boolean(
        string='✓ Cho phép bán?',
        compute='_compute_dtx_checklist',
        help='Kiểm tra xem sản phẩm có thể bán cho khách hàng không',
    )

    @api.depends('tracking', 'categ_id.property_cost_method', 'purchase_ok', 'sale_ok', 'x_dtx_type')
    def _compute_dtx_checklist(self):
        """
        Tính toán các field checklist để hiển thị trạng thái cấu hình sản phẩm
        CHỈ để nhìn - KHÔNG ép buộc
        """
        for product in self:
            # Check 1: Serial tracking enabled?
            product.x_dtx_check_serial_enabled = (product.tracking == 'serial')

            # Check 2: AVCO costing?
            product.x_dtx_check_avco_costing = (
                product.categ_id.property_cost_method == 'average'
            )

            # Check 3: Has BOM? (only relevant for Kiosk)
            if product.x_dtx_type == 'finished_kiosk':
                bom_count = self.env['mrp.bom'].search_count([
                    ('product_tmpl_id', '=', product.id),
                ])
                product.x_dtx_check_has_bom = (bom_count > 0)
            else:
                product.x_dtx_check_has_bom = False

            # Check 4: Can purchase?
            product.x_dtx_check_can_purchase = product.purchase_ok

            # Check 5: Can sell?
            product.x_dtx_check_can_sell = product.sale_ok

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def get_dtx_type_label(self):
        """Get Vietnamese label for DTX type"""
        self.ensure_one()
        type_dict = dict(self._fields['x_dtx_type'].selection)
        return type_dict.get(self.x_dtx_type, '')

    def get_dtx_type_help_text(self):
        """Get help text for current DTX type"""
        self.ensure_one()
        help_texts = {
            'device_serialized': """Mỗi thiết bị quản lý theo từng chiếc (serial riêng).
Ví dụ: Touch screen, Mini PC, Máy in, Tablet, QR reader, CCCD reader.""",
            'component_untracked': """Vật tư dùng chung, không cần theo dõi từng chiếc.
Ví dụ: cáp mạng, vít, dây điện, đầu RJ45.""",
            'finished_kiosk': """Sản phẩm hoàn chỉnh được lắp ráp từ nhiều linh kiện.
Có thể sản xuất nội bộ hoặc thuê đối tác lắp ráp.""",
            'service': """Phí triển khai, vận chuyển, cài đặt, bảo trì… không nhập xuất kho.""",
        }
        return help_texts.get(self.x_dtx_type, '')
