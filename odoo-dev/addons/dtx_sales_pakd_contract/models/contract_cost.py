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

    # Cost fields
    planned_unit_cost = fields.Monetary(
        string='Đơn giá dự kiến (PAKD)',
        help='Đơn giá mua từ PAKD (chỉ đọc)',
        readonly=True,
    )

    actual_unit_cost = fields.Monetary(
        string='Đơn giá thực tế',
        help='Đơn giá mua thực tế (có thể chỉnh sửa)',
        required=True,
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
    @api.depends('qty', 'planned_unit_cost', 'actual_unit_cost')
    def _compute_totals(self):
        for cost in self:
            cost.planned_total = cost.qty * cost.planned_unit_cost
            cost.actual_total = cost.qty * cost.actual_unit_cost
            cost.variance = cost.actual_total - cost.planned_total

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.uom_id = self.product_id.uom_id.id
            # Set actual cost from product standard price
            self.actual_unit_cost = self.product_id.standard_price
