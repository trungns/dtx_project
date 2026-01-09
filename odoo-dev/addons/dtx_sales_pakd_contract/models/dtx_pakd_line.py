# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DtxPakdLine(models.Model):
    _name = 'dtx.pakd.line'
    _description = 'Chi tiết PAKD'
    _order = 'pakd_id, sequence, id'

    # ==========================================
    # BASIC FIELDS
    # ==========================================
    pakd_id = fields.Many2one(
        'dtx.pakd',
        string='PAKD',
        required=True,
        ondelete='cascade',
        index=True,
    )

    sequence = fields.Integer(string='STT', default=10)

    company_id = fields.Many2one(
        'res.company',
        related='pakd_id.company_id',
        store=True,
        readonly=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='pakd_id.currency_id',
        store=True,
        readonly=True,
    )

    # ==========================================
    # DISPLAY TYPE (for section/note lines)
    # ==========================================
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], string='Display Type', help='Section or note line for grouping, excluded from totals')

    # ==========================================
    # PRODUCT FIELDS
    # ==========================================
    section_type = fields.Selection([
        ('license', 'Phần mềm/License'),
        ('hardware', 'Phần cứng/Hardware'),
        ('deployment', 'Triển khai/Deployment'),
        ('other', 'Khác'),
    ], string='Loại hạng mục', help='Nhóm giống A/B trong Excel PAKD')

    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        domain=[('sale_ok', '=', True)],
    )

    product_code = fields.Char(
        string='Mã SP',
        related='product_id.default_code',
        store=True,
        readonly=True,
    )

    name = fields.Text(
        string='Mô tả',
    )

    # ==========================================
    # QUANTITY & UOM
    # ==========================================
    qty = fields.Float(
        string='Số lượng',
        required=True,
        default=1.0,
        digits='Product Unit of Measure',
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='Đơn vị',
        required=True,
        domain="[('category_id', '=', product_uom_category_id)]",
        default=lambda self: self.env.ref('uom.product_uom_unit', raise_if_not_found=False),
    )

    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id',
        readonly=True,
    )

    # ==========================================
    # PRICE FIELDS (matching Excel PAKD structure)
    # ==========================================
    estimate_unit_excl_vat = fields.Monetary(
        string='Dự toán trước thuế',
        currency_field='currency_id',
        help='Đơn giá dự toán ban đầu (chưa VAT)',
    )

    vendor_list_price = fields.Monetary(
        string='Đơn giá list hãng/NPP',
        currency_field='currency_id',
        help='Giá niêm yết từ nhà cung cấp',
    )

    discount_percent = fields.Float(
        string='Discount (%)',
        digits='Discount',
        help='Tỷ lệ chiết khấu từ giá list, 0-100',
    )

    purchase_unit_price = fields.Monetary(
        string='Đơn giá nhập',
        currency_field='currency_id',
        help='Đơn giá nhập hàng thực tế',
    )

    sale_unit_price = fields.Monetary(
        string='Đơn giá bán',
        currency_field='currency_id',
        help='Đơn giá bán dự kiến cho khách hàng',
    )

    contract_unit_price = fields.Monetary(
        string='Đơn giá hợp đồng',
        currency_field='currency_id',
        help='Đơn giá chính thức trong hợp đồng. Nếu = 0, sẽ dùng đơn giá bán.',
    )

    # ==========================================
    # TAX FIELDS
    # ==========================================
    vat_percent = fields.Float(
        string='VAT (%)',
        digits=(16, 2),
        help='Tỷ lệ VAT. Hệ thống sẽ tự động map sang thuế chuẩn.',
    )

    tax_id = fields.Many2one(
        'account.tax',
        string='Thuế',
        domain=[('type_tax_use', '=', 'sale')],
        help='Thuế bán hàng chuẩn của Odoo',
    )

    # ==========================================
    # COMPUTED TOTALS (matching Excel PAKD formulas)
    # ==========================================
    # 1) Tổng dự toán trước thuế
    estimate_total_excl_vat = fields.Monetary(
        string='Tổng dự toán trước thuế',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= qty × estimate_unit_excl_vat',
    )

    # 2) Tổng dự toán có thuế
    estimate_total_incl_vat = fields.Monetary(
        string='Tổng dự toán có thuế',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= estimate_total_excl_vat × (1 + vat_percent/100)',
    )

    # 3) Tổng tiền nhập
    purchase_total = fields.Monetary(
        string='Tổng tiền nhập',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= qty × purchase_unit_price',
    )

    # 4) Tổng giá bán
    sale_total = fields.Monetary(
        string='Tổng giá bán',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= qty × sale_unit_price',
    )

    # 5) Tổng giá HĐ (chưa VAT)
    contract_total_excl_vat = fields.Monetary(
        string='Tổng giá HĐ (chưa VAT)',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= qty × (contract_unit_price if > 0 else sale_unit_price)',
    )

    # 6) Giá trị HĐ (có VAT)
    contract_total_incl_vat = fields.Monetary(
        string='Giá trị HĐ (có VAT)',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= contract_total_excl_vat × (1 + vat_percent/100)',
    )

    # 7) Helper: purchase_unit_price from list + discount
    purchase_unit_price_from_list = fields.Monetary(
        string='Đơn giá nhập (từ list)',
        compute='_compute_purchase_from_list',
        store=True,
        currency_field='currency_id',
        help='= vendor_list_price × (1 - discount_percent/100)',
    )

    # Additional computed fields for backward compatibility
    contract_tax_amount = fields.Monetary(
        string='Tiền VAT HĐ',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= contract_total_excl_vat × vat_percent/100',
    )

    line_profit = fields.Monetary(
        string='Lãi dòng',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='= contract_total_excl_vat - purchase_total',
    )

    line_margin_percent = fields.Float(
        string='Tỷ lệ lãi dòng (%)',
        compute='_compute_totals',
        store=True,
        help='= (line_profit / purchase_total) × 100',
    )

    # ==========================================
    # ONCHANGE METHODS
    # ==========================================
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        Auto-fill fields when product is selected.
        IMPORTANT: Only for NEW lines (no self.id yet) or when fields are empty.
        This prevents overwriting user-entered data when reopening saved records.
        """
        if not self.product_id:
            return

        # Set default description if empty
        if not self.name:
            self.name = self.product_id.get_product_multiline_description_sale()

        # Set default UOM if not set
        if not self.uom_id:
            self.uom_id = self.product_id.uom_id.id

        # Set default prices ONLY if they are 0 (not yet set by user)
        # This prevents overwriting saved data when form is reloaded
        if not self.estimate_unit_excl_vat:
            self.estimate_unit_excl_vat = self.product_id.list_price
        if not self.sale_unit_price:
            self.sale_unit_price = self.product_id.list_price
        if not self.purchase_unit_price:
            self.purchase_unit_price = self.product_id.standard_price
        if not self.vendor_list_price:
            self.vendor_list_price = self.product_id.list_price

        # Set default tax from product if not set
        if self.product_id.taxes_id and not self.tax_id:
            first_tax = self.product_id.taxes_id[0]
            self.tax_id = first_tax.id
            if first_tax.amount_type == 'percent' and not self.vat_percent:
                self.vat_percent = first_tax.amount

    @api.onchange('vendor_list_price', 'discount_percent')
    def _onchange_vendor_list_price(self):
        """Auto-fill purchase_unit_price from vendor_list_price and discount"""
        if self.vendor_list_price and self.discount_percent:
            # Only auto-fill if purchase_unit_price is empty or 0
            if not self.purchase_unit_price:
                self.purchase_unit_price = self.vendor_list_price * (1 - self.discount_percent / 100)

    @api.onchange('vat_percent')
    def _onchange_vat_percent(self):
        """Auto-map VAT% to account.tax"""
        # Normalize to 0 if empty
        if not self.vat_percent:
            self.vat_percent = 0
            self.tax_id = False
            return

        tax = self._find_tax_by_percent(self.vat_percent)
        if tax:
            self.tax_id = tax.id
        else:
            self.tax_id = False
            return {
                'warning': {
                    'title': 'Chưa có thuế VAT',
                    'message': f'Chưa có thuế VAT {self.vat_percent}% trong cấu hình. '
                              f'Hãy tạo account.tax VAT {self.vat_percent}%.'
                }
            }

    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        """Update vat_percent when tax_id changes"""
        if self.tax_id and self.tax_id.amount_type == 'percent':
            self.vat_percent = self.tax_id.amount

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('vendor_list_price', 'discount_percent')
    def _compute_purchase_from_list(self):
        """Helper: Compute purchase_unit_price from vendor_list_price and discount"""
        for line in self:
            if line.display_type:
                line.purchase_unit_price_from_list = 0.0
            else:
                if line.vendor_list_price and line.discount_percent:
                    line.purchase_unit_price_from_list = line.vendor_list_price * (1 - line.discount_percent / 100)
                else:
                    line.purchase_unit_price_from_list = line.vendor_list_price or 0.0

    @api.depends('qty', 'estimate_unit_excl_vat', 'purchase_unit_price', 'sale_unit_price',
                 'contract_unit_price', 'vat_percent', 'display_type')
    def _compute_totals(self):
        """
        Compute all totals matching Excel PAKD formulas.
        Section/note lines (display_type != False) are excluded from totals.
        """
        for line in self:
            # Section/note lines have zero totals
            if line.display_type:
                line.estimate_total_excl_vat = 0.0
                line.estimate_total_incl_vat = 0.0
                line.purchase_total = 0.0
                line.sale_total = 0.0
                line.contract_total_excl_vat = 0.0
                line.contract_total_incl_vat = 0.0
                line.contract_tax_amount = 0.0
                line.line_profit = 0.0
                line.line_margin_percent = 0.0
                continue

            # Get currency for rounding
            currency = line.currency_id or line.company_id.currency_id

            # 1) Tổng dự toán trước thuế = qty × estimate_unit_excl_vat
            line.estimate_total_excl_vat = currency.round(line.qty * line.estimate_unit_excl_vat)

            # 2) Tổng dự toán có thuế = estimate_total_excl_vat × (1 + vat_percent/100)
            line.estimate_total_incl_vat = currency.round(
                line.estimate_total_excl_vat * (1 + line.vat_percent / 100)
            )

            # 3) Tổng tiền nhập = qty × purchase_unit_price (NO VAT)
            line.purchase_total = currency.round(line.qty * line.purchase_unit_price)

            # 4) Tổng giá bán = qty × sale_unit_price
            line.sale_total = currency.round(line.qty * line.sale_unit_price)

            # 5) Tổng giá HĐ (chưa VAT) = qty × effective_contract_unit
            # effective_contract_unit = contract_unit_price if > 0 else sale_unit_price
            effective_contract_unit = line.contract_unit_price if line.contract_unit_price > 0 else line.sale_unit_price
            line.contract_total_excl_vat = currency.round(line.qty * effective_contract_unit)

            # 6) Giá trị HĐ (có VAT) = contract_total_excl_vat × (1 + vat_percent/100)
            # Simple Excel formula, không dùng tax engine phức tạp
            line.contract_tax_amount = currency.round(
                line.contract_total_excl_vat * (line.vat_percent / 100)
            )
            line.contract_total_incl_vat = currency.round(
                line.contract_total_excl_vat + line.contract_tax_amount
            )

            # Line profit = Doanh thu (chưa VAT) - Chi phí (chưa VAT)
            line.line_profit = currency.round(line.contract_total_excl_vat - line.purchase_total)

            # Margin % = (Profit / Purchase) × 100
            if line.purchase_total:
                line.line_margin_percent = (line.line_profit / line.purchase_total) * 100
            else:
                line.line_margin_percent = 0.0

    # ==========================================
    # ORM METHODS
    # ==========================================
    @api.model
    def create(self, vals):
        """
        Override create to ensure uom_id is always set.
        If not provided and product_id exists, use product's UOM.
        If still not set, use default Unit UOM.
        """
        # If uom_id not provided, try to get from product
        if not vals.get('uom_id') and vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            if product.uom_id:
                vals['uom_id'] = product.uom_id.id

        # If still no uom_id, use default Unit
        if not vals.get('uom_id'):
            default_uom = self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
            if default_uom:
                vals['uom_id'] = default_uom.id

        return super(DtxPakdLine, self).create(vals)

    # ==========================================
    # HELPER METHODS
    # ==========================================
    def _find_tax_by_percent(self, vat_percent):
        """Find account.tax by VAT percent"""
        tax = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('amount_type', '=', 'percent'),
            ('amount', '=', vat_percent),
            ('company_id', 'in', [self.company_id.id, False]),
        ], limit=1)

        return tax
