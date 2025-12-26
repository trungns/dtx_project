# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class ApplyDTXStandardsWizard(models.TransientModel):
    _name = 'dtx.apply.standards.wizard'
    _description = 'Wizard to apply DTX standards to products'

    # ==========================================
    # FIELDS
    # ==========================================

    apply_tracking = fields.Boolean(
        string='Áp dụng quản lý Serial',
        default=True,
        help='Tự động bật/tắt serial tracking theo loại sản phẩm DTX',
    )

    apply_purchase_sale = fields.Boolean(
        string='Áp dụng cấu hình mua/bán',
        default=True,
        help='Tự động cấu hình cho phép mua/bán theo loại sản phẩm DTX',
    )

    product_ids = fields.Many2many(
        'product.template',
        string='Sản phẩm',
        help='Sản phẩm được chọn từ danh sách. Nếu để trống sẽ áp dụng cho TẤT CẢ sản phẩm có loại DTX.',
    )

    # Stats fields (after execution)
    total_products = fields.Integer(
        string='Tổng số sản phẩm',
        readonly=True,
    )

    updated_count = fields.Integer(
        string='Số sản phẩm đã cập nhật',
        readonly=True,
    )

    skipped_count = fields.Integer(
        string='Số sản phẩm bỏ qua',
        readonly=True,
    )

    summary_message = fields.Text(
        string='Kết quả',
        readonly=True,
    )

    state = fields.Selection([
        ('draft', 'Chưa thực hiện'),
        ('done', 'Hoàn tất'),
    ], default='draft')

    # ==========================================
    # ACTIONS
    # ==========================================

    @api.model
    def default_get(self, fields_list):
        """Pre-fill product_ids from context (selected products in tree view)"""
        res = super().default_get(fields_list)

        # Get selected products from context
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['product_ids'] = [(6, 0, active_ids)]

        return res

    def action_apply_standards(self):
        """Apply DTX standards to selected products"""
        self.ensure_one()

        # Get products to process
        if self.product_ids:
            products = self.product_ids
        else:
            # Apply to ALL products with DTX type set
            products = self.env['product.template'].search([
                ('x_dtx_type', '!=', False),
            ])

        if not products:
            raise UserError('Không tìm thấy sản phẩm nào có loại DTX để áp dụng chuẩn!')

        updated_count = 0
        skipped_count = 0
        update_details = []

        for product in products:
            product_updated = False
            changes = []

            # Apply tracking configuration
            if self.apply_tracking:
                if product.x_dtx_type == 'device_serialized':
                    # Device should have serial tracking
                    if product.tracking != 'serial':
                        # Check if product has stock moves (cannot change tracking if has moves)
                        if self._can_change_tracking(product):
                            product.tracking = 'serial'
                            changes.append('Serial tracking: BẬT')
                            product_updated = True
                        else:
                            changes.append('Serial tracking: BỎ QUA (đã có giao dịch kho)')

                elif product.x_dtx_type == 'component_untracked':
                    # Component should NOT have tracking
                    if product.tracking != 'none':
                        if self._can_change_tracking(product):
                            product.tracking = 'none'
                            changes.append('Serial tracking: TẮT')
                            product_updated = True
                        else:
                            changes.append('Serial tracking: BỎ QUA (đã có giao dịch kho)')

                elif product.x_dtx_type == 'service':
                    # Service should be type='service'
                    if product.type != 'service':
                        product.type = 'service'
                        changes.append('Product type: DỊCH VỤ')
                        product_updated = True

            # Apply purchase/sale configuration
            if self.apply_purchase_sale:
                if product.x_dtx_type in ['device_serialized', 'component_untracked', 'finished_kiosk']:
                    # Hardware products should be purchasable
                    if not product.purchase_ok:
                        product.purchase_ok = True
                        changes.append('Cho phép mua: BẬT')
                        product_updated = True

                if product.x_dtx_type in ['device_serialized', 'finished_kiosk']:
                    # Devices and Kiosks should be sellable
                    if not product.sale_ok:
                        product.sale_ok = True
                        changes.append('Cho phép bán: BẬT')
                        product_updated = True

                if product.x_dtx_type == 'service':
                    # Services should be sellable but not purchasable (usually)
                    if not product.sale_ok:
                        product.sale_ok = True
                        changes.append('Cho phép bán: BẬT')
                        product_updated = True

            # Track results
            if product_updated:
                updated_count += 1
                update_details.append(f"✓ {product.display_name}: {', '.join(changes)}")
            else:
                skipped_count += 1

        # Build summary message
        summary_lines = [
            f"=== KẾT QUẢ ÁP DỤNG CHUẨN DTX ===\n",
            f"Tổng số sản phẩm: {len(products)}",
            f"Đã cập nhật: {updated_count}",
            f"Bỏ qua: {skipped_count}\n",
        ]

        if update_details:
            summary_lines.append("Chi tiết cập nhật:")
            summary_lines.extend(update_details[:20])  # Show first 20
            if len(update_details) > 20:
                summary_lines.append(f"... và {len(update_details) - 20} sản phẩm khác")

        # Update wizard state
        self.write({
            'state': 'done',
            'total_products': len(products),
            'updated_count': updated_count,
            'skipped_count': skipped_count,
            'summary_message': '\n'.join(summary_lines),
        })

        # Return wizard view to show results
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.apply.standards.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_close(self):
        """Close wizard"""
        return {'type': 'ir.actions.act_window_close'}

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _can_change_tracking(self, product):
        """
        Check if product tracking can be changed
        Cannot change if product has stock moves
        """
        # Check for stock moves
        move_count = self.env['stock.move'].search_count([
            '|',
            ('product_id.product_tmpl_id', '=', product.id),
            ('product_tmpl_id', '=', product.id),
        ])

        return move_count == 0
