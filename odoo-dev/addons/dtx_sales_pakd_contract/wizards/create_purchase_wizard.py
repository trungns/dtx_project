# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CreatePurchaseWizard(models.TransientModel):
    _name = 'dtx.create.purchase.wizard'
    _description = 'Wizard to create PO from SO'

    # ==========================================
    # FIELDS
    # ==========================================
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Đơn hàng',
        required=True,
        readonly=True,
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string='Nhà cung cấp',
        domain="[('supplier_rank', '>', 0)]",
        help='Chọn nhà cung cấp để tạo đơn mua hàng',
    )

    line_ids = fields.One2many(
        'dtx.create.purchase.wizard.line',
        'wizard_id',
        string='Sản phẩm cần mua',
    )

    company_id = fields.Many2one(
        'res.company',
        related='sale_order_id.company_id',
        store=True,
        readonly=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='sale_order_id.currency_id',
        store=True,
        readonly=True,
    )

    note = fields.Text(
        string='Ghi chú',
        help='Ghi chú thêm cho đơn mua hàng',
    )

    # ==========================================
    # ACTION METHODS
    # ==========================================
    def action_create_purchase(self):
        """Create PO from wizard data"""
        self.ensure_one()

        # Validate: must have vendor
        if not self.vendor_id:
            raise UserError('Vui lòng chọn nhà cung cấp.')

        # Validate: must have at least one selected line
        selected_lines = self.line_ids.filtered(lambda l: l.selected)
        if not selected_lines:
            raise UserError('Vui lòng chọn ít nhất một sản phẩm để tạo đơn mua hàng.')

        # Prepare PO lines
        po_lines = []
        for line in selected_lines:
            if line.qty_to_order <= 0:
                continue

            # Get purchase UOM (default to product's purchase UOM or standard UOM)
            uom_id = line.product_id.uom_po_id.id if line.product_id.uom_po_id else line.product_id.uom_id.id

            # Get price from vendor pricelist or use standard price
            price_unit = self._get_purchase_price(line.product_id, self.vendor_id)

            po_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.display_name,
                'product_qty': line.qty_to_order,
                'product_uom': uom_id,
                'price_unit': price_unit,
                'date_planned': fields.Datetime.now(),
            }))

        if not po_lines:
            raise UserError('Không có sản phẩm nào có số lượng cần mua hợp lệ.')

        # Create PO
        po_vals = {
            'partner_id': self.vendor_id.id,
            'origin': self.sale_order_id.name,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'order_line': po_lines,
        }

        if self.note:
            po_vals['notes'] = self.note

        po = self.env['purchase.order'].create(po_vals)

        # Log message on SO
        product_names = ', '.join(selected_lines.mapped('product_id.name'))
        self.sale_order_id.message_post(
            body=f'Đã tạo đơn mua hàng <a href="#" data-oe-model="purchase.order" data-oe-id="{po.id}">{po.name}</a><br/>'
                 f'Nhà cung cấp: {self.vendor_id.name}<br/>'
                 f'Sản phẩm: {product_names}',
            subject='Tạo PO từ SO',
        )

        # Log message on PO
        po.message_post(
            body=f'Đơn mua hàng được tạo từ <a href="#" data-oe-model="sale.order" data-oe-id="{self.sale_order_id.id}">{self.sale_order_id.name}</a>',
            subject='Nguồn gốc từ SO',
        )

        _logger.info(f"Created PO {po.name} from SO {self.sale_order_id.name} with {len(selected_lines)} lines")

        # Return action to open created PO
        return {
            'name': po.name,
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
            'target': 'current',
        }

    def action_cancel(self):
        """Close wizard without creating PO"""
        return {'type': 'ir.actions.act_window_close'}

    # ==========================================
    # HELPER METHODS
    # ==========================================
    def _get_purchase_price(self, product, vendor):
        """Get purchase price for product from vendor pricelist or standard price"""
        # Try to get price from vendor's pricelist
        supplierinfo = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('partner_id', '=', vendor.id),
        ], limit=1, order='min_qty asc')

        if supplierinfo:
            return supplierinfo.price

        # Fallback to product standard price
        return product.standard_price


class CreatePurchaseWizardLine(models.TransientModel):
    _name = 'dtx.create.purchase.wizard.line'
    _description = 'Wizard line to create PO from SO'
    _order = 'product_id'

    # ==========================================
    # FIELDS
    # ==========================================
    wizard_id = fields.Many2one(
        'dtx.create.purchase.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True,
        readonly=True,
    )

    product_code = fields.Char(
        string='Mã SP',
        related='product_id.default_code',
        readonly=True,
    )

    qty_needed = fields.Float(
        string='Cần',
        required=True,
        readonly=True,
        digits='Product Unit of Measure',
        help='Số lượng cần thiết từ đơn hàng',
    )

    qty_available = fields.Float(
        string='Có sẵn',
        required=True,
        readonly=True,
        digits='Product Unit of Measure',
        help='Số lượng hiện có trong kho',
    )

    qty_to_order = fields.Float(
        string='Cần mua',
        required=True,
        digits='Product Unit of Measure',
        help='Số lượng cần mua = Cần - Có sẵn',
    )

    selected = fields.Boolean(
        string='Chọn',
        default=True,
        help='Chọn sản phẩm này để thêm vào đơn mua hàng',
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='Đơn vị',
        related='product_id.uom_id',
        readonly=True,
    )

    # ==========================================
    # CONSTRAINTS
    # ==========================================
    @api.constrains('qty_to_order')
    def _check_qty_to_order(self):
        """Validate qty_to_order is positive"""
        for line in self:
            if line.qty_to_order < 0:
                raise ValidationError(
                    f'Số lượng cần mua cho sản phẩm {line.product_id.name} '
                    f'không thể âm.'
                )
