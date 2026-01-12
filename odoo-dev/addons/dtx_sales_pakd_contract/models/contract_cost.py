# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ContractCost(models.Model):
    _name = 'dtx.contract.cost'
    _description = 'Chi phí hợp đồng thực tế'
    _order = 'sequence, id'

    # ==========================================
    # FIELDS
    # ==========================================
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Hợp đồng',
        required=True,
        ondelete='cascade',
        index=True,
    )

    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
    )

    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True,
    )

    name = fields.Text(
        string='Mô tả',
        required=True,
    )

    qty = fields.Float(
        string='Số lượng',
        default=1.0,
        required=True,
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='ĐVT',
        required=True,
    )

    # ==========================================
    # PURCHASE COST FIELDS
    # ==========================================
    planned_unit_cost = fields.Monetary(
        string='Đơn giá mua dự kiến (PAKD)',
        help='Đơn giá mua từ PAKD (chỉ đọc)',
        readonly=True,
    )

    purchase_unit_price = fields.Monetary(
        string='Đơn giá mua thực tế',
        compute='_compute_purchase_price',
        store=True,
        help='Đơn giá mua từ Purchase Order (tự động, chỉ đọc)',
    )

    purchase_unit_price_manual = fields.Monetary(
        string='Đơn giá mua thủ công',
        help='Đơn giá mua nhập thủ công cho line không có PO (license, misc)',
    )

    has_purchase_order = fields.Boolean(
        string='Có PO',
        compute='_compute_purchase_price',
        store=True,
        help='Line này có Purchase Order hay không',
    )

    # ==========================================
    # SALE PRICE FIELDS
    # ==========================================
    sale_unit_price = fields.Monetary(
        string='Đơn giá bán',
        compute='_compute_sale_price',
        store=True,
        readonly=False,
        help='Đơn giá bán từ Sale Order (tự động nhưng có thể sửa)',
    )

    # ==========================================
    # PROFIT FIELDS
    # ==========================================
    total_purchase = fields.Monetary(
        string='Tổng mua',
        compute='_compute_profit',
        store=True,
        help='Tổng chi phí mua = Số lượng × Đơn giá mua',
    )

    total_sale = fields.Monetary(
        string='Tổng bán',
        compute='_compute_profit',
        store=True,
        help='Tổng doanh thu = Số lượng × Đơn giá bán',
    )

    profit = fields.Monetary(
        string='Lợi nhuận',
        compute='_compute_profit',
        store=True,
        help='Lợi nhuận = Tổng bán - Tổng mua',
    )

    margin_percent = fields.Float(
        string='Tỷ suất (%)',
        compute='_compute_profit',
        store=True,
        help='Tỷ suất lợi nhuận = (Lợi nhuận / Tổng bán) × 100%',
    )

    # ==========================================
    # LEGACY FIELDS (keep for backward compatibility)
    # ==========================================
    actual_unit_cost = fields.Monetary(
        string='Đơn giá thực tế (deprecated)',
        help='Field cũ, dùng purchase_unit_price thay thế',
    )

    planned_total = fields.Monetary(
        string='Tổng dự kiến',
        compute='_compute_totals',
        store=True,
    )

    actual_total = fields.Monetary(
        string='Tổng thực tế',
        compute='_compute_totals',
        store=True,
    )

    variance = fields.Monetary(
        string='Chênh lệch',
        compute='_compute_totals',
        store=True,
        help='Chênh lệch = Thực tế - Dự kiến (âm là tốt, dương là vượt dự kiến)',
    )

    cost_type = fields.Selection([
        ('planned', 'Từ PAKD'),
        ('additional', 'Phát sinh'),
    ], string='Loại chi phí', default='planned', required=True)

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='sale_order_id.currency_id',
        readonly=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        related='sale_order_id.company_id',
        readonly=True,
    )

    notes = fields.Text(
        string='Ghi chú',
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('product_id', 'qty', 'sale_order_id.order_line.product_id', 'sale_order_id.order_line.price_unit')
    def _compute_purchase_price(self):
        """
        Auto-populate purchase price from Purchase Orders linked to Sale Order

        Logic:
        1. Find PO lines via stock moves (sale_order → procurement → purchase_order)
        2. If PO exists: use PO price (readonly, blue background)
        3. If no PO: use manual price (editable for license, misc costs)
        """
        for cost in self:
            purchase_price = 0.0
            has_po = False

            if cost.product_id and cost.sale_order_id:
                # Find purchase order lines for this product in this sale order
                # Path: sale.order → stock.move → purchase.order.line

                # Get procurement group for this sale order
                procurement_group = self.env['procurement.group'].search([
                    ('sale_id', '=', cost.sale_order_id.id)
                ], limit=1)

                if procurement_group:
                    # Find stock moves for this product in this procurement group
                    stock_moves = self.env['stock.move'].search([
                        ('group_id', '=', procurement_group.id),
                        ('product_id', '=', cost.product_id.id),
                    ])

                    # Get purchase order lines from these moves
                    po_lines = stock_moves.mapped('purchase_line_id')

                    if po_lines:
                        # Use the latest PO line price
                        latest_po_line = po_lines.sorted(key=lambda l: l.id, reverse=True)[0]
                        purchase_price = latest_po_line.price_unit
                        has_po = True
                        _logger.info(f"Contract Cost: Found PO price {purchase_price} for product {cost.product_id.name}")

            cost.purchase_unit_price = purchase_price
            cost.has_purchase_order = has_po

    @api.depends('product_id', 'sale_order_id.order_line.product_id', 'sale_order_id.order_line.price_unit')
    def _compute_sale_price(self):
        """
        Auto-populate sale price from Sale Order lines

        Logic:
        1. Find SO line with matching product
        2. Use price_unit from SO line
        3. Allow manual edit (readonly=False)
        """
        for cost in self:
            sale_price = 0.0

            if cost.product_id and cost.sale_order_id:
                # Find sale order line for this product
                so_line = cost.sale_order_id.order_line.filtered(
                    lambda l: l.product_id == cost.product_id and not l.display_type
                )

                if so_line:
                    # Use first matching line
                    sale_price = so_line[0].price_unit
                    _logger.info(f"Contract Cost: Found sale price {sale_price} for product {cost.product_id.name}")

            cost.sale_unit_price = sale_price

    @api.depends('qty', 'purchase_unit_price', 'purchase_unit_price_manual', 'sale_unit_price', 'has_purchase_order')
    def _compute_profit(self):
        """
        Compute profit and margin

        Logic:
        - If has PO: use purchase_unit_price (auto from PO)
        - If no PO: use purchase_unit_price_manual (manual input)
        - Profit = Total sale - Total purchase
        - Margin = (Profit / Total sale) × 100%
        """
        for cost in self:
            # Determine effective purchase price
            if cost.has_purchase_order:
                effective_purchase_price = cost.purchase_unit_price
            else:
                effective_purchase_price = cost.purchase_unit_price_manual or 0.0

            # Calculate totals
            cost.total_purchase = cost.qty * effective_purchase_price
            cost.total_sale = cost.qty * cost.sale_unit_price

            # Calculate profit
            cost.profit = cost.total_sale - cost.total_purchase

            # Calculate margin percentage
            if cost.total_sale != 0:
                cost.margin_percent = (cost.profit / cost.total_sale) * 100
            else:
                cost.margin_percent = 0.0

    @api.depends('qty', 'planned_unit_cost', 'actual_unit_cost')
    def _compute_totals(self):
        """Legacy compute for backward compatibility"""
        for cost in self:
            cost.planned_total = cost.qty * cost.planned_unit_cost
            cost.actual_total = cost.qty * cost.actual_unit_cost
            cost.variance = cost.actual_total - cost.planned_total

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.uom_id = self.product_id.uom_id.id
            # Trigger recompute of prices
            self._compute_purchase_price()
            self._compute_sale_price()
