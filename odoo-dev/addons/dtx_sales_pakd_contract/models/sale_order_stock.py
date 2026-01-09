# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # ==========================================
    # INVENTORY STATUS FIELDS
    # ==========================================
    x_qty_available = fields.Float(
        string='Tồn kho',
        compute='_compute_inventory_status',
        help='Số lượng có sẵn trong kho (On Hand)'
    )

    x_qty_forecasted = fields.Float(
        string='Dự báo',
        compute='_compute_inventory_status',
        help='Tồn kho dự báo (bao gồm incoming/outgoing)'
    )

    x_stock_status = fields.Selection([
        ('in_stock', 'Đủ hàng'),
        ('partial', 'Thiếu một phần'),
        ('out_of_stock', 'Hết hàng'),
        ('not_storable', 'Không quản lý kho'),
    ], string='Trạng thái kho', compute='_compute_inventory_status')

    x_stock_status_icon = fields.Char(
        compute='_compute_inventory_status',
        help='Icon để hiển thị trên tree view'
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('product_id', 'product_uom_qty', 'product_id.qty_available', 'product_id.virtual_available')
    def _compute_inventory_status(self):
        """Compute inventory status for each SO line"""
        for line in self:
            # Skip display_type lines (section/note)
            if line.display_type:
                line.x_stock_status = 'not_storable'
                line.x_qty_available = 0.0
                line.x_qty_forecasted = 0.0
                line.x_stock_status_icon = ''
                continue

            # Check if product is storable
            if not line.product_id or line.product_id.type != 'product':
                # Service, consumable → không cần check kho
                line.x_stock_status = 'not_storable'
                line.x_qty_available = 0.0
                line.x_qty_forecasted = 0.0
                line.x_stock_status_icon = ''
                continue

            # Get stock qty from product (use product's warehouse context if available)
            # Use free_qty (qty available to promise) instead of qty_available
            product = line.product_id.with_context(
                warehouse=line.order_id.warehouse_id.id if line.order_id.warehouse_id else False
            )

            line.x_qty_available = product.qty_available
            line.x_qty_forecasted = product.virtual_available

            # Determine status based on available qty vs ordered qty
            if line.x_qty_available >= line.product_uom_qty:
                line.x_stock_status = 'in_stock'
                line.x_stock_status_icon = '✅'
            elif line.x_qty_available > 0:
                line.x_stock_status = 'partial'
                line.x_stock_status_icon = '⚠️'
            else:
                line.x_stock_status = 'out_of_stock'
                line.x_stock_status_icon = '❌'

    # ==========================================
    # ACTION METHODS
    # ==========================================
    def action_create_po_for_line(self):
        """Create PO for a single SO line (called from tree view button)"""
        self.ensure_one()

        if not self.product_id or self.product_id.type != 'product':
            raise UserError('Sản phẩm này không phải là loại quản lý kho.')

        if self.x_stock_status not in ['out_of_stock', 'partial']:
            raise UserError('Sản phẩm này đã có đủ trong kho.')

        # Calculate qty to order
        qty_to_order = self.product_uom_qty - self.x_qty_available
        if qty_to_order <= 0:
            raise UserError('Không cần mua thêm.')

        # Create wizard record with line
        wizard = self.env['dtx.create.purchase.wizard'].create({
            'sale_order_id': self.order_id.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'qty_needed': self.product_uom_qty,
                'qty_available': self.x_qty_available,
                'qty_to_order': qty_to_order,
            })],
        })

        # Open wizard
        return {
            'name': f'Tạo đơn mua - {self.product_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.create.purchase.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ==========================================
    # STOCK STATUS SUMMARY FIELD
    # ==========================================
    x_stock_status_summary = fields.Selection([
        ('all_in_stock', 'Tất cả có sẵn'),
        ('partial_stock', 'Một phần thiếu'),
        ('need_procurement', 'Cần mua hàng'),
    ], string='Trạng thái tồn kho', compute='_compute_stock_status_summary', store=True)

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('order_line.x_stock_status')
    def _compute_stock_status_summary(self):
        """Compute overall stock status for the entire SO"""
        for order in self:
            # Filter only storable product lines (exclude service, consumable, section, note)
            storable_lines = order.order_line.filtered(
                lambda l: l.product_id and l.product_id.type == 'product' and not l.display_type
            )

            # If no storable lines, consider as all in stock
            if not storable_lines:
                order.x_stock_status_summary = 'all_in_stock'
                continue

            # Check if any lines are out of stock or partial
            out_of_stock_lines = storable_lines.filtered(lambda l: l.x_stock_status == 'out_of_stock')
            partial_lines = storable_lines.filtered(lambda l: l.x_stock_status == 'partial')

            if out_of_stock_lines or partial_lines:
                order.x_stock_status_summary = 'need_procurement'
            else:
                order.x_stock_status_summary = 'all_in_stock'

    # ==========================================
    # ACTION METHODS
    # ==========================================
    def action_view_stock_by_product(self):
        """View stock quants for all products in SO"""
        self.ensure_one()

        # Get all storable products from SO lines
        product_ids = self.order_line.filtered(
            lambda l: l.product_id and l.product_id.type == 'product' and not l.display_type
        ).mapped('product_id').ids

        if not product_ids:
            raise UserError('Đơn hàng này không có sản phẩm nào cần quản lý kho.')

        return {
            'name': f'Tồn kho - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'tree,form',
            'domain': [
                ('product_id', 'in', product_ids),
                ('location_id.usage', '=', 'internal')
            ],
            'context': {
                'search_default_internal_loc': 1,
            },
        }

    def action_create_purchase_for_missing(self):
        """Create PO for out-of-stock items"""
        self.ensure_one()

        # Find missing items (out of stock or partial)
        missing_lines = self.order_line.filtered(
            lambda l: l.x_stock_status in ['out_of_stock', 'partial']
                     and l.product_id
                     and l.product_id.type == 'product'
                     and not l.display_type
        )

        if not missing_lines:
            raise UserError('Tất cả sản phẩm đều có sẵn trong kho.')

        # Prepare wizard line data
        wizard_lines = []
        for line in missing_lines:
            qty_to_order = line.product_uom_qty - line.x_qty_available
            if qty_to_order > 0:
                wizard_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'qty_needed': line.product_uom_qty,
                    'qty_available': line.x_qty_available,
                    'qty_to_order': qty_to_order,
                }))

        if not wizard_lines:
            raise UserError('Không có sản phẩm nào cần mua thêm.')

        # Open wizard to create PO
        return {
            'name': 'Tạo đơn mua hàng',
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.create.purchase.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_line_ids': wizard_lines,
            },
        }
