# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DtxPakd(models.Model):
    _name = 'dtx.pakd'
    _description = 'Phương án kinh doanh (PAKD)'
    _order = 'create_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==========================================
    # BASIC FIELDS
    # ==========================================
    name = fields.Char(
        string='Mã PAKD',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Báo giá/Đơn hàng',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='company_id.currency_id',
        store=True,
        readonly=True,
    )

    owner_user_id = fields.Many2one(
        'res.users',
        string='Sale phụ trách',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã trình'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ], string='Trạng thái', default='draft', tracking=True, copy=False)

    note = fields.Text(string='Ghi chú')

    # ==========================================
    # RELATED PARTNER FIELDS
    # ==========================================
    partner_id = fields.Many2one(
        'res.partner',
        string='Đại lý/KH ký HĐ',
        related='sale_order_id.partner_id',
        store=True,
        readonly=True,
    )

    end_customer_id = fields.Many2one(
        'res.partner',
        string='Khách hàng cuối',
        related='sale_order_id.x_end_customer_id',
        store=True,
        readonly=True,
    )

    # ==========================================
    # PAKD LINES
    # ==========================================
    line_ids = fields.One2many(
        'dtx.pakd.line',
        'pakd_id',
        string='Chi tiết PAKD',
        copy=True,
    )

    # ==========================================
    # COMPUTED TOTALS (matching Excel PAKD header)
    # ==========================================
    # 1) Tổng giá nhập
    total_purchase = fields.Monetary(
        string='Tổng giá nhập',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= sum(line.purchase_total)',
    )

    # 2) Tổng giá bán
    total_sale = fields.Monetary(
        string='Tổng giá bán',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= sum(line.sale_total)',
    )

    # 3) Tổng giá HĐ (chưa VAT)
    total_contract_untaxed = fields.Monetary(
        string='Tổng giá HĐ (chưa VAT)',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= sum(line.contract_total_excl_vat)',
    )

    # 4) Tổng VAT HĐ (simple sum from lines, không dùng tax engine)
    total_contract_tax = fields.Monetary(
        string='Tổng VAT HĐ',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= sum(line.contract_total_excl_vat × vat_percent/100)',
    )

    # 5) Tổng giá HĐ (có VAT)
    total_contract_total = fields.Monetary(
        string='Tổng giá HĐ (có VAT)',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= total_contract_untaxed + total_contract_tax',
    )

    # 6) Chênh lệch giá
    price_diff = fields.Monetary(
        string='Chênh lệch giá',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= total_sale - total_purchase',
    )

    # ==========================================
    # CHI PHÍ / HOA HỒNG / THUẾ (manual input)
    # ==========================================
    tax_withheld_percent = fields.Float(
        string='Tỷ lệ thu thuế (%)',
        default=0.0,
        help='Tỷ lệ thu thuế từ chênh lệch giá (thường 15-20%), nhập tay',
    )

    tax_withheld_amount = fields.Monetary(
        string='Thu thuế',
        compute='_compute_business_costs',
        store=True,
        currency_field='currency_id',
        help='= price_diff × (tax_withheld_percent/100)',
    )

    cushion_amount = fields.Monetary(
        string='Tổng gối thêm',
        compute='_compute_business_costs',
        store=True,
        currency_field='currency_id',
        help='= price_diff - tax_withheld_amount (Số tiền còn lại sau khi thu thuế)',
    )

    referral_commission_percent = fields.Float(
        string='Tỷ lệ hoa hồng (%)',
        default=0.0,
        help='Tỷ lệ hoa hồng từ tổng tiền HĐ chưa VAT (thường 3%), nhập tay',
    )

    referral_commission = fields.Monetary(
        string='Hoa hồng người giới thiệu',
        compute='_compute_business_costs',
        store=True,
        currency_field='currency_id',
        help='= total_contract_untaxed × (referral_commission_percent/100)',
    )

    customer_support_cost = fields.Monetary(
        string='Tổng chi phí cho khách',
        compute='_compute_business_costs',
        store=True,
        currency_field='currency_id',
        help='= cushion_amount + referral_commission (Tổng gối thêm + Hoa hồng)',
    )

    business_cost_total = fields.Monetary(
        string='Tổng chi phí kinh doanh',
        compute='_compute_business_costs',
        store=True,
        currency_field='currency_id',
        help='= tax_withheld_amount + customer_support_cost',
    )

    # ==========================================
    # LỢI NHUẬN (computed)
    # ==========================================
    expected_profit = fields.Monetary(
        string='Lợi nhuận dự kiến',
        compute='_compute_business_costs',
        store=True,
        currency_field='currency_id',
        help='= total_contract_untaxed - total_purchase - business_cost_total',
    )

    expected_margin_percent = fields.Float(
        string='Tỷ lệ lãi (%)',
        compute='_compute_business_costs',
        store=True,
        help='= (expected_profit / total_contract_untaxed) × 100',
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('line_ids.purchase_total',
                 'line_ids.sale_total',
                 'line_ids.contract_total_excl_vat',
                 'line_ids.contract_tax_amount',
                 'line_ids.contract_total_incl_vat',
                 'line_ids.display_type')
    def _compute_totals(self):
        """
        Compute header totals matching Excel PAKD.
        Exclude section/note lines (display_type != False).
        """
        for pakd in self:
            # Filter out section/note lines
            normal_lines = pakd.line_ids.filtered(lambda l: not l.display_type)

            # 1) Tổng giá nhập
            pakd.total_purchase = sum(normal_lines.mapped('purchase_total'))

            # 2) Tổng giá bán
            pakd.total_sale = sum(normal_lines.mapped('sale_total'))

            # 3) Tổng giá HĐ (chưa VAT)
            pakd.total_contract_untaxed = sum(normal_lines.mapped('contract_total_excl_vat'))

            # 4) Tổng VAT HĐ (simple sum from line computed values)
            pakd.total_contract_tax = sum(normal_lines.mapped('contract_tax_amount'))

            # 5) Tổng giá HĐ (có VAT)
            pakd.total_contract_total = pakd.total_contract_untaxed + pakd.total_contract_tax

            # 6) Chênh lệch giá
            pakd.price_diff = pakd.total_sale - pakd.total_purchase

    @api.depends('price_diff', 'total_contract_untaxed', 'total_purchase',
                 'tax_withheld_percent', 'referral_commission_percent')
    def _compute_business_costs(self):
        """
        Compute business costs and profit matching Excel PAKD formulas.

        Excel PAKD structure:
        1. Tổng tiền nhập (chi phí đầu vào) = total_purchase
        2. Tổng tiền bán (chi phí thứ vỡ) = total_sale
        3. Tổng tiền Hợp đồng = total_contract_total
        4. Chênh lệch giá = price_diff = total_sale - total_purchase
        5. Thu thuế X% = price_diff × tax_withheld_percent
        6. Tổng gối thêm = price_diff - thu thuế
        7. Hoa hồng Y% = total_contract_untaxed × referral_commission_percent
        8. Tổng chi phí cho khách = Tổng gối thêm + Hoa hồng
        9. Lợi nhuận = price_diff - thu thuế - hoa hồng
        """
        for pakd in self:
            currency = pakd.currency_id or pakd.company_id.currency_id

            # 5) Thu thuế = price_diff × (tax_withheld_percent/100)
            # Base is chênh lệch giá (not total_contract_untaxed!)
            pakd.tax_withheld_amount = currency.round(
                pakd.price_diff * (pakd.tax_withheld_percent / 100)
            )

            # 6) Tổng gối thêm = price_diff - tax_withheld_amount
            pakd.cushion_amount = currency.round(
                pakd.price_diff - pakd.tax_withheld_amount
            )

            # 7) Hoa hồng = total_contract_untaxed × (referral_commission_percent/100)
            pakd.referral_commission = currency.round(
                pakd.total_contract_untaxed * (pakd.referral_commission_percent / 100)
            )

            # 8) Tổng chi phí cho khách = Tổng gối thêm + Hoa hồng
            pakd.customer_support_cost = currency.round(
                pakd.cushion_amount + pakd.referral_commission
            )

            # Tổng chi phí KD = Thu thuế + Tổng chi phí cho khách
            pakd.business_cost_total = currency.round(
                pakd.tax_withheld_amount + pakd.customer_support_cost
            )

            # 9) Lợi nhuận = price_diff - thu thuế - hoa hồng
            # Or equivalently: total_contract_untaxed - total_purchase - business_cost_total
            pakd.expected_profit = currency.round(
                pakd.price_diff - pakd.tax_withheld_amount - pakd.referral_commission
            )

            # Tỷ lệ lãi % = (Lợi nhuận / Tổng tiền HĐ chưa VAT) × 100
            if pakd.total_contract_untaxed:
                pakd.expected_margin_percent = (pakd.expected_profit / pakd.total_contract_untaxed) * 100
            else:
                pakd.expected_margin_percent = 0.0

    # ==========================================
    # ORM METHODS
    # ==========================================
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('dtx.pakd') or _('New')
        return super(DtxPakd, self).create(vals)

    # ==========================================
    # ACTION METHODS
    # ==========================================
    def action_submit(self):
        """Submit PAKD for approval"""
        for pakd in self:
            pakd.state = 'submitted'
            pakd.message_post(body='PAKD đã được trình duyệt', subject='Trình PAKD')

    def action_approve(self):
        """Approve PAKD"""
        for pakd in self:
            pakd.state = 'approved'
            pakd.message_post(body='PAKD đã được phê duyệt', subject='Phê duyệt PAKD')

    def action_reject(self):
        """Reject PAKD"""
        for pakd in self:
            pakd.state = 'rejected'
            pakd.message_post(body='PAKD đã bị từ chối', subject='Từ chối PAKD')

    def action_reset_draft(self):
        """Reset to draft"""
        for pakd in self:
            pakd.state = 'draft'

    def action_open_apply_wizard(self):
        """Open wizard to apply PAKD to sale.order"""
        self.ensure_one()

        if not self.line_ids:
            raise UserError('PAKD không có dòng nào để apply.')

        return {
            'name': f'Apply PAKD {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.pakd.apply.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pakd_id': self.id,
                'default_sale_order_id': self.sale_order_id.id,
            },
        }

    def action_view_sale_order(self):
        """View related sales order"""
        self.ensure_one()
        return {
            'name': self.sale_order_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }
