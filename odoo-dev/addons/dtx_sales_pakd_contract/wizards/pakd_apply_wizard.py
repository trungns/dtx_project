# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PakdApplyWizard(models.TransientModel):
    _name = 'dtx.pakd.apply.wizard'
    _description = 'Wizard Apply PAKD to Sales Order'

    # ==========================================
    # FIELDS
    # ==========================================
    pakd_id = fields.Many2one(
        'dtx.pakd',
        string='PAKD',
        required=True,
        readonly=True,
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Báo giá/Đơn hàng',
        related='pakd_id.sale_order_id',
        readonly=True,
    )

    sale_order_state = fields.Selection(
        related='sale_order_id.state',
        readonly=True,
    )

    replace_lines = fields.Boolean(
        string='Thay thế toàn bộ dòng hiện tại',
        default=True,
        help='Nếu tick: xóa tất cả dòng hiện tại và tạo mới từ PAKD. '
             'Nếu không: thêm dòng mới từ PAKD vào cuối.',
    )

    price_source = fields.Selection([
        ('contract', 'Ưu tiên đơn giá HĐ'),
        ('sale', 'Chỉ dùng đơn giá báo giá'),
    ], string='Nguồn giá', default='contract', required=True,
        help='contract: Dùng contract_unit_price, nếu trống thì dùng sale_unit_price\n'
             'sale: Chỉ dùng sale_unit_price')

    warning_message = fields.Text(
        string='Cảnh báo',
        compute='_compute_warning_message',
        readonly=True,
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('sale_order_id.state', 'replace_lines')
    def _compute_warning_message(self):
        for wizard in self:
            warnings = []

            # Warning if SO is confirmed
            if wizard.sale_order_state not in ['draft', 'sent', 'cancel']:
                warnings.append(
                    '⚠️ Đơn hàng đã được xác nhận (state = sale). '
                    'Việc apply PAKD có thể ảnh hưởng đến quy trình đã chạy. '
                    'Hãy cân nhắc kỹ trước khi thực hiện.'
                )

            # Warning if replace_lines and SO has many lines
            if wizard.replace_lines:
                line_count = len(wizard.sale_order_id.order_line)
                if line_count > 0:
                    warnings.append(
                        f'⚠️ Sẽ xóa {line_count} dòng hiện tại trong đơn hàng.'
                    )

            wizard.warning_message = '\n\n'.join(warnings) if warnings else ''

    # ==========================================
    # ACTION METHODS
    # ==========================================
    def action_apply(self):
        """Apply PAKD to Sales Order"""
        self.ensure_one()

        if not self.pakd_id.line_ids:
            raise UserError('PAKD không có dòng nào để apply.')

        sale_order = self.sale_order_id

        # Log start
        _logger.info(
            f"Applying PAKD {self.pakd_id.name} to SO {sale_order.name}. "
            f"Replace lines: {self.replace_lines}, Price source: {self.price_source}"
        )

        # Step 1: Delete existing lines if replace_lines
        if self.replace_lines:
            existing_lines = sale_order.order_line.filtered(lambda l: not l.display_type)
            if existing_lines:
                _logger.info(f"Deleting {len(existing_lines)} existing lines")
                existing_lines.unlink()

        # Step 2: Create new lines from PAKD
        new_lines_count = 0
        skipped_lines_count = 0
        for pakd_line in self.pakd_id.line_ids:
            # Skip section/note lines
            if pakd_line.display_type:
                continue

            # Skip lines without product or uom
            if not pakd_line.product_id:
                _logger.warning(f"Skipping PAKD line {pakd_line.id}: no product_id")
                skipped_lines_count += 1
                continue

            # Get UOM from pakd_line or fallback to product UOM
            uom_id = pakd_line.uom_id.id if pakd_line.uom_id else pakd_line.product_id.uom_id.id
            if not uom_id:
                _logger.warning(f"Skipping PAKD line {pakd_line.id}: no uom_id for product {pakd_line.product_id.name}")
                skipped_lines_count += 1
                continue

            # Determine price_unit
            if self.price_source == 'contract':
                price_unit = pakd_line.contract_unit_price or pakd_line.sale_unit_price
            else:
                price_unit = pakd_line.sale_unit_price

            # Create sale.order.line
            line_vals = {
                'order_id': sale_order.id,
                'product_id': pakd_line.product_id.id,
                'name': pakd_line.name or pakd_line.product_id.get_product_multiline_description_sale(),
                'product_uom_qty': pakd_line.qty,
                'product_uom': uom_id,
                'price_unit': price_unit,
                'tax_id': [(6, 0, [pakd_line.tax_id.id])] if pakd_line.tax_id else [(5, 0, 0)],
                'sequence': pakd_line.sequence,
            }

            self.env['sale.order.line'].create(line_vals)
            new_lines_count += 1

        # Step 3: Log message on sale_order
        body_msg = (
            f'✅ Đã apply PAKD <a href="#" data-oe-model="dtx.pakd" data-oe-id="{self.pakd_id.id}">{self.pakd_id.name}</a><br/>'
            f'- Thay thế dòng: {"Có" if self.replace_lines else "Không"}<br/>'
            f'- Nguồn giá: {dict(self._fields["price_source"].selection).get(self.price_source)}<br/>'
            f'- Số dòng mới: {new_lines_count}'
        )
        if skipped_lines_count > 0:
            body_msg += f'<br/>⚠️ Bỏ qua {skipped_lines_count} dòng (thiếu sản phẩm hoặc đơn vị tính)'

        sale_order.message_post(
            body=body_msg,
            subject='Apply PAKD',
        )

        # Step 4: Log on PAKD
        self.pakd_id.message_post(
            body=f'✅ Đã apply vào <a href="#" data-oe-model="sale.order" data-oe-id="{sale_order.id}">{sale_order.name}</a>',
            subject='Applied to Sales Order',
        )

        _logger.info(f"Successfully applied PAKD {self.pakd_id.name} to SO {sale_order.name}. Created {new_lines_count} lines.")

        # Return to sales order
        return {
            'name': sale_order.name,
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }

    def action_cancel(self):
        """Close wizard without applying"""
        return {'type': 'ir.actions.act_window_close'}
