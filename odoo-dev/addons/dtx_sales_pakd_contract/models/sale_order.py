# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ==========================================
    # DTX BUSINESS FIELDS
    # ==========================================
    x_end_customer_id = fields.Many2one(
        'res.partner',
        string='Khách hàng cuối (End User)',
        help='Khách hàng cuối cùng sử dụng sản phẩm/dịch vụ. '
             'Trường hợp bán qua đại lý: Customer = Đại lý, End User = Khách hàng thực tế.',
        tracking=True,
    )

    x_agent_id = fields.Many2one(
        'res.partner',
        string='Đại lý cấp 2 (nếu có)',
        help='Đại lý cấp 2 hoặc đối tác giới thiệu (nếu có chuỗi phân phối nhiều tầng)',
        tracking=True,
    )

    # ==========================================
    # CONTRACT FIELDS
    # ==========================================
    x_contract_no = fields.Char(
        string='Số hợp đồng',
        help='Số hợp đồng chính thức (khi Sales Order được confirm)',
        tracking=True,
        copy=False,
    )

    x_signed_date = fields.Date(
        string='Ngày ký HĐ',
        help='Ngày ký hợp đồng chính thức',
        tracking=True,
        copy=False,
    )

    x_contract_end_date = fields.Date(
        string='Ngày hết hạn HĐ',
        help='Ngày hết hạn hợp đồng',
        tracking=True,
        copy=False,
    )

    x_contract_scan_attachment_ids = fields.Many2many(
        'ir.attachment',
        'sale_order_contract_scan_rel',
        'order_id',
        'attachment_id',
        string='File scan hợp đồng',
        help='Upload file scan hợp đồng đã ký (PDF/JPG/PNG)',
        domain="[('res_model', '=', 'sale.order'), ('res_id', '=', id)]",
    )

    x_contract_scan_count = fields.Integer(
        string='Số file scan',
        compute='_compute_contract_scan_count',
    )

    # ==========================================
    # PAKD RELATIONSHIP
    # ==========================================
    pakd_ids = fields.One2many(
        'dtx.pakd',
        'sale_order_id',
        string='Phương án kinh doanh (PAKD)',
        help='Danh sách các phương án kinh doanh cho đơn hàng này',
    )

    pakd_count = fields.Integer(
        string='Số PAKD',
        compute='_compute_pakd_count',
    )

    # ==========================================
    # CONTRACT COSTS
    # ==========================================
    contract_cost_ids = fields.One2many(
        'dtx.contract.cost',
        'sale_order_id',
        string='Chi phí hợp đồng',
        help='Chi phí thực tế của hợp đồng (từ PAKD + phát sinh)',
    )

    contract_cost_count = fields.Integer(
        string='Số dòng chi phí',
        compute='_compute_contract_cost_count',
    )

    # ==========================================
    # CONTRACT COMPUTED FIELDS (for list view)
    # ==========================================
    x_revenue_expected = fields.Monetary(
        string='Doanh thu dự kiến',
        compute='_compute_contract_financials',
        store=True,
        help='Tổng doanh thu dự kiến từ sale order (amount_untaxed)',
    )

    x_revenue_actual = fields.Monetary(
        string='Doanh thu thực tế',
        compute='_compute_contract_financials',
        store=True,
        help='Tổng doanh thu thực tế từ invoices đã thanh toán',
    )

    x_payment_date = fields.Date(
        string='Ngày thanh toán',
        compute='_compute_contract_financials',
        store=True,
        help='Ngày thanh toán gần nhất',
    )

    x_total_cost = fields.Monetary(
        string='Chi phí',
        compute='_compute_contract_financials',
        store=True,
        help='Tổng chi phí từ purchase orders',
    )

    x_profit = fields.Monetary(
        string='Lãi',
        compute='_compute_contract_financials',
        store=True,
        help='Lãi = Doanh thu thực tế - Chi phí',
    )

    x_profit_margin = fields.Float(
        string='Lãi (%)',
        compute='_compute_contract_financials',
        store=True,
        help='Tỷ lệ lãi = (Lãi / Doanh thu thực tế) * 100',
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('x_contract_scan_attachment_ids')
    def _compute_contract_scan_count(self):
        for order in self:
            order.x_contract_scan_count = len(order.x_contract_scan_attachment_ids)

    @api.depends('pakd_ids')
    def _compute_pakd_count(self):
        for order in self:
            order.pakd_count = len(order.pakd_ids)

    @api.depends('contract_cost_ids')
    def _compute_contract_cost_count(self):
        for order in self:
            order.contract_cost_count = len(order.contract_cost_ids)

    @api.depends('amount_untaxed', 'invoice_ids.payment_state', 'invoice_ids.amount_untaxed', 'invoice_ids.date', 'contract_cost_ids.actual_total')
    def _compute_contract_financials(self):
        """Compute contract financial fields"""
        for order in self:
            # Revenue expected = SO amount_untaxed
            order.x_revenue_expected = order.amount_untaxed

            # Revenue actual = sum of paid invoices
            paid_invoices = order.invoice_ids.filtered(
                lambda inv: inv.payment_state == 'paid' and inv.move_type == 'out_invoice'
            )
            order.x_revenue_actual = sum(paid_invoices.mapped('amount_untaxed'))

            # Payment date = latest payment date
            if paid_invoices:
                order.x_payment_date = max(paid_invoices.mapped('date'))
            else:
                order.x_payment_date = False

            # Total cost = sum of actual costs from contract_cost_ids
            order.x_total_cost = sum(order.contract_cost_ids.mapped('actual_total'))

            # Profit = Revenue actual - Total cost
            order.x_profit = order.x_revenue_actual - order.x_total_cost

            # Profit margin % = (Profit / Revenue actual) * 100
            if order.x_revenue_actual:
                order.x_profit_margin = (order.x_profit / order.x_revenue_actual) * 100
            else:
                order.x_profit_margin = 0.0

    # ==========================================
    # ACTION METHODS
    # ==========================================
    def action_view_pakd(self):
        """Open PAKD list view for this sales order"""
        self.ensure_one()
        return {
            'name': f'PAKD - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.pakd',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_end_customer_id': self.x_end_customer_id.id if self.x_end_customer_id else False,
            },
        }

    def action_create_pakd(self):
        """Create new PAKD from Sales Order lines"""
        self.ensure_one()

        # Create PAKD
        pakd = self.env['dtx.pakd'].create({
            'sale_order_id': self.id,
            'partner_id': self.partner_id.id,
            'end_customer_id': self.x_end_customer_id.id if self.x_end_customer_id else False,
        })

        # Create PAKD lines from sale.order.line
        sequence = 10
        for line in self.order_line:
            if line.display_type:
                # Skip section/note lines
                continue

            # Map tax_id to vat_percent
            vat_percent = 0.0
            tax_id = False
            if line.tax_id:
                # Take first tax if multiple
                first_tax = line.tax_id[0] if line.tax_id else False
                if first_tax and first_tax.amount_type == 'percent':
                    vat_percent = first_tax.amount
                    tax_id = first_tax.id

            pakd_line_vals = {
                'pakd_id': pakd.id,
                'sequence': sequence,
                'product_id': line.product_id.id,
                'name': line.name,
                'qty': line.product_uom_qty,
                'uom_id': line.product_uom.id,
                'sale_unit_price': line.price_unit,
                'contract_unit_price': 0.0,  # User will fill later
                'purchase_unit_price': 0.0,  # User will fill later
                'vat_percent': vat_percent,
                'tax_id': tax_id,
            }

            self.env['dtx.pakd.line'].create(pakd_line_vals)
            sequence += 10

        # Log message
        self.message_post(
            body=f'Đã tạo PAKD mới: <a href="#" data-oe-model="dtx.pakd" data-oe-id="{pakd.id}">{pakd.name}</a>',
            subject='Tạo PAKD mới',
        )

        # Open created PAKD
        return {
            'name': f'PAKD - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.pakd',
            'view_mode': 'form',
            'res_id': pakd.id,
            'target': 'current',
        }

    def action_view_contract_scans(self):
        """View contract scan attachments"""
        self.ensure_one()
        return {
            'name': f'File scan HĐ - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.x_contract_scan_attachment_ids.ids)],
            'context': {
                'default_res_model': 'sale.order',
                'default_res_id': self.id,
            },
        }

    def action_import_pakd_costs(self):
        """Import costs from approved PAKD to contract costs"""
        self.ensure_one()

        # Find approved PAKD
        approved_pakd = self.pakd_ids.filtered(lambda p: p.state == 'approved')
        if not approved_pakd:
            raise UserError('Không tìm thấy PAKD đã duyệt để import chi phí.')

        # Use the latest approved PAKD
        pakd = approved_pakd.sorted(key=lambda p: p.create_date, reverse=True)[0]

        # Clear existing costs from PAKD (keep additional costs)
        self.contract_cost_ids.filtered(lambda c: c.cost_type == 'planned').unlink()

        # Create contract costs from PAKD lines
        sequence = 10
        for pakd_line in pakd.line_ids:
            self.env['dtx.contract.cost'].create({
                'sale_order_id': self.id,
                'sequence': sequence,
                'product_id': pakd_line.product_id.id,
                'name': pakd_line.name,
                'qty': pakd_line.qty,
                'uom_id': pakd_line.uom_id.id,
                'planned_unit_cost': pakd_line.purchase_unit_price,
                'actual_unit_cost': pakd_line.purchase_unit_price,  # Initial value
                'cost_type': 'planned',
            })
            sequence += 10

        self.message_post(
            body=f'✅ Đã import {len(pakd.line_ids)} dòng chi phí từ PAKD <a href="#" data-oe-model="dtx.pakd" data-oe-id="{pakd.id}">{pakd.name}</a>',
            subject='Import chi phí từ PAKD',
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã import {len(pakd.line_ids)} dòng chi phí từ PAKD {pakd.name}',
                'type': 'success',
                'sticky': False,
            }
        }

    # ==========================================
    # AR (ACCOUNTS RECEIVABLE) FIELDS
    # ==========================================
    x_ar_residual_total = fields.Monetary(
        string='Còn phải thu',
        compute='_compute_ar_fields',
        store=True,
        help='Tổng số tiền còn phải thu từ các invoice liên quan',
    )

    x_ar_max_days_overdue = fields.Integer(
        string='Quá hạn tối đa (ngày)',
        compute='_compute_ar_fields',
        store=True,
        help='Số ngày quá hạn tối đa của các invoice liên quan',
    )

    x_ar_status = fields.Selection([
        ('ok', 'OK'),
        ('due_soon', 'Sắp đến hạn'),
        ('overdue', 'Quá hạn'),
    ], string='Trạng thái công nợ',
        compute='_compute_ar_fields',
        store=True,
        help='Trạng thái công nợ: OK (đã thanh toán hết), Sắp đến hạn (7 ngày tới), Quá hạn',
    )

    @api.depends('invoice_ids.amount_residual', 'invoice_ids.invoice_date_due',
                 'invoice_ids.invoice_date', 'invoice_ids.state')
    def _compute_ar_fields(self):
        """Compute AR (Accounts Receivable) fields"""
        from datetime import date

        for order in self:
            # Get posted invoices with residual > 0
            ar_invoices = order.invoice_ids.filtered(
                lambda inv: inv.move_type == 'out_invoice' and
                           inv.state == 'posted' and
                           inv.amount_residual > 0
            )

            if not ar_invoices:
                order.x_ar_residual_total = 0.0
                order.x_ar_max_days_overdue = 0
                order.x_ar_status = 'ok'
                continue

            # Total residual
            order.x_ar_residual_total = sum(ar_invoices.mapped('amount_residual'))

            # Max days overdue
            today = date.today()
            max_days = 0
            min_days_to_due = 999999

            for inv in ar_invoices:
                due_date = inv.invoice_date_due or inv.invoice_date
                if due_date:
                    days_overdue = (today - due_date).days
                    max_days = max(max_days, days_overdue)
                    min_days_to_due = min(min_days_to_due, days_overdue)

            order.x_ar_max_days_overdue = max_days

            # AR Status
            if max_days > 0:
                order.x_ar_status = 'overdue'
            elif min_days_to_due >= -7:  # Due within 7 days
                order.x_ar_status = 'due_soon'
            else:
                order.x_ar_status = 'ok'

    def action_view_ar_invoices(self):
        """View AR invoices (unpaid/partially paid)"""
        self.ensure_one()

        return {
            'name': f'Hóa đơn công nợ - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('amount_residual', '>', 0),
                ('id', 'in', self.invoice_ids.ids),
            ],
            'context': {
                'create': False,
            },
        }
