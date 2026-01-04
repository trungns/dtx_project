# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, tools

_logger = logging.getLogger(__name__)


class DtxArAgingSummary(models.Model):
    _name = 'dtx.ar.aging.summary'
    _description = 'Tổng hợp tuổi nợ (AR Aging Summary)'
    _auto = False  # SQL view, not a regular table
    _order = 'total_residual desc, max_days_overdue desc'

    # ==========================================
    # FIELDS
    # ==========================================
    partner_id = fields.Many2one(
        'res.partner',
        string='Khách hàng',
        readonly=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        readonly=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        readonly=True,
    )

    salesperson_id = fields.Many2one(
        'res.users',
        string='Nhân viên bán hàng',
        readonly=True,
        help='Sale user từ invoice gần nhất',
    )

    # Total receivables
    total_residual = fields.Monetary(
        string='Tổng công nợ',
        currency_field='currency_id',
        readonly=True,
        help='Tổng số tiền còn phải thu',
    )

    invoice_count = fields.Integer(
        string='Số hóa đơn',
        readonly=True,
        help='Số lượng hóa đơn chưa thanh toán hết',
    )

    # Aging buckets
    bucket_current = fields.Monetary(
        string='Chưa đến hạn',
        currency_field='currency_id',
        readonly=True,
        help='Nợ chưa đến hạn hoặc quá hạn <= 0 ngày',
    )

    bucket_1 = fields.Monetary(
        string='1-7 ngày',
        currency_field='currency_id',
        readonly=True,
    )

    bucket_2 = fields.Monetary(
        string='8-15 ngày',
        currency_field='currency_id',
        readonly=True,
    )

    bucket_3 = fields.Monetary(
        string='16-30 ngày',
        currency_field='currency_id',
        readonly=True,
    )

    bucket_4 = fields.Monetary(
        string='31-60 ngày',
        currency_field='currency_id',
        readonly=True,
    )

    bucket_5 = fields.Monetary(
        string='61-90 ngày',
        currency_field='currency_id',
        readonly=True,
    )

    bucket_over = fields.Monetary(
        string='> 90 ngày',
        currency_field='currency_id',
        readonly=True,
        help='Quá hạn > 90 ngày',
    )

    # Date tracking
    oldest_invoice_date = fields.Date(
        string='HĐ cũ nhất',
        readonly=True,
    )

    last_invoice_date = fields.Date(
        string='HĐ mới nhất',
        readonly=True,
    )

    max_days_overdue = fields.Integer(
        string='Quá hạn tối đa (ngày)',
        readonly=True,
        help='Số ngày quá hạn của hóa đơn lâu nhất',
    )

    # ==========================================
    # SQL VIEW INITIALIZATION
    # ==========================================
    def init(self):
        """Create SQL view for AR aging summary"""
        tools.drop_view_if_exists(self.env.cr, self._table)

        # Get default config values for buckets (will use in SQL)
        # Note: In real deployment, this should be dynamic per company
        query = """
            CREATE OR REPLACE VIEW %s AS (
                WITH aging_config AS (
                    SELECT
                        company_id,
                        COALESCE(bucket_1_days, 7) as bucket_1_days,
                        COALESCE(bucket_2_days, 15) as bucket_2_days,
                        COALESCE(bucket_3_days, 30) as bucket_3_days,
                        COALESCE(bucket_4_days, 60) as bucket_4_days,
                        COALESCE(bucket_5_days, 90) as bucket_5_days
                    FROM dtx_ar_aging_config
                    UNION ALL
                    -- Default config if not exists
                    SELECT
                        rc.id as company_id,
                        7 as bucket_1_days,
                        15 as bucket_2_days,
                        30 as bucket_3_days,
                        60 as bucket_4_days,
                        90 as bucket_5_days
                    FROM res_company rc
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dtx_ar_aging_config
                        WHERE company_id = rc.id
                    )
                ),
                invoice_aging AS (
                    SELECT
                        am.id as move_id,
                        am.partner_id,
                        am.company_id,
                        am.currency_id,
                        am.invoice_user_id as salesperson_id,
                        am.amount_residual,
                        am.invoice_date,
                        COALESCE(am.invoice_date_due, am.invoice_date) as due_date,
                        CURRENT_DATE - COALESCE(am.invoice_date_due, am.invoice_date) as days_overdue,
                        ac.bucket_1_days,
                        ac.bucket_2_days,
                        ac.bucket_3_days,
                        ac.bucket_4_days,
                        ac.bucket_5_days
                    FROM account_move am
                    LEFT JOIN aging_config ac ON ac.company_id = am.company_id
                    WHERE am.move_type = 'out_invoice'
                        AND am.state = 'posted'
                        AND am.amount_residual > 0
                        AND am.payment_state != 'paid'
                )
                SELECT
                    ROW_NUMBER() OVER (ORDER BY partner_id, company_id) as id,
                    partner_id,
                    company_id,
                    currency_id,
                    -- Take salesperson from most recent invoice
                    (array_agg(salesperson_id ORDER BY invoice_date DESC))[1] as salesperson_id,
                    SUM(amount_residual) as total_residual,
                    COUNT(*) as invoice_count,
                    -- Bucket current (not overdue)
                    SUM(CASE WHEN days_overdue <= 0 THEN amount_residual ELSE 0 END) as bucket_current,
                    -- Bucket 1
                    SUM(CASE WHEN days_overdue > 0 AND days_overdue <= bucket_1_days
                        THEN amount_residual ELSE 0 END) as bucket_1,
                    -- Bucket 2
                    SUM(CASE WHEN days_overdue > bucket_1_days AND days_overdue <= bucket_2_days
                        THEN amount_residual ELSE 0 END) as bucket_2,
                    -- Bucket 3
                    SUM(CASE WHEN days_overdue > bucket_2_days AND days_overdue <= bucket_3_days
                        THEN amount_residual ELSE 0 END) as bucket_3,
                    -- Bucket 4
                    SUM(CASE WHEN days_overdue > bucket_3_days AND days_overdue <= bucket_4_days
                        THEN amount_residual ELSE 0 END) as bucket_4,
                    -- Bucket 5
                    SUM(CASE WHEN days_overdue > bucket_4_days AND days_overdue <= bucket_5_days
                        THEN amount_residual ELSE 0 END) as bucket_5,
                    -- Bucket over (> bucket 5)
                    SUM(CASE WHEN days_overdue > bucket_5_days
                        THEN amount_residual ELSE 0 END) as bucket_over,
                    MIN(invoice_date) as oldest_invoice_date,
                    MAX(invoice_date) as last_invoice_date,
                    MAX(days_overdue) as max_days_overdue
                FROM invoice_aging
                GROUP BY partner_id, company_id, currency_id
            )
        """ % (self._table,)

        self.env.cr.execute(query)

    # ==========================================
    # ACTIONS
    # ==========================================
    def action_view_invoices(self):
        """Open list of invoices for this partner"""
        self.ensure_one()

        return {
            'name': f'Hóa đơn: {self.partner_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('amount_residual', '>', 0),
                ('partner_id', '=', self.partner_id.id),
            ],
            'context': {
                'create': False,
                'default_move_type': 'out_invoice',
            },
        }

    def action_view_sale_orders(self):
        """Open list of sale orders for this partner"""
        self.ensure_one()

        return {
            'name': f'Đơn hàng: {self.partner_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [
                ('partner_id', '=', self.partner_id.id),
            ],
            'context': {
                'create': False,
            },
        }
