# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DtxArAgingConfig(models.Model):
    _name = 'dtx.ar.aging.config'
    _description = 'Cấu hình tuổi nợ (AR Aging Configuration)'
    _rec_name = 'company_id'

    # ==========================================
    # FIELDS
    # ==========================================
    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade',
    )

    # Aging buckets (days)
    bucket_1_days = fields.Integer(
        string='Bucket 1 (ngày)',
        default=7,
        required=True,
        help='Nợ từ 1 đến N ngày (ví dụ: 1-7 ngày)',
    )

    bucket_2_days = fields.Integer(
        string='Bucket 2 (ngày)',
        default=15,
        required=True,
        help='Nợ từ Bucket 1+1 đến N ngày (ví dụ: 8-15 ngày)',
    )

    bucket_3_days = fields.Integer(
        string='Bucket 3 (ngày)',
        default=30,
        required=True,
        help='Nợ từ Bucket 2+1 đến N ngày (ví dụ: 16-30 ngày)',
    )

    bucket_4_days = fields.Integer(
        string='Bucket 4 (ngày)',
        default=60,
        required=True,
        help='Nợ từ Bucket 3+1 đến N ngày (ví dụ: 31-60 ngày)',
    )

    bucket_5_days = fields.Integer(
        string='Bucket 5 (ngày)',
        default=90,
        required=True,
        help='Nợ từ Bucket 4+1 đến N ngày (ví dụ: 61-90 ngày)',
    )

    # Computed labels for display
    bucket_1_label = fields.Char(
        string='Label Bucket 1',
        compute='_compute_bucket_labels',
        store=True,
    )

    bucket_2_label = fields.Char(
        string='Label Bucket 2',
        compute='_compute_bucket_labels',
        store=True,
    )

    bucket_3_label = fields.Char(
        string='Label Bucket 3',
        compute='_compute_bucket_labels',
        store=True,
    )

    bucket_4_label = fields.Char(
        string='Label Bucket 4',
        compute='_compute_bucket_labels',
        store=True,
    )

    bucket_5_label = fields.Char(
        string='Label Bucket 5',
        compute='_compute_bucket_labels',
        store=True,
    )

    # ==========================================
    # SQL CONSTRAINTS
    # ==========================================
    _sql_constraints = [
        ('company_unique', 'UNIQUE(company_id)',
         'Chỉ được có một cấu hình tuổi nợ cho mỗi công ty!'),
    ]

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('bucket_1_days', 'bucket_2_days', 'bucket_3_days',
                 'bucket_4_days', 'bucket_5_days')
    def _compute_bucket_labels(self):
        """Compute display labels for each bucket"""
        for config in self:
            config.bucket_1_label = f'1-{config.bucket_1_days} ngày'
            config.bucket_2_label = f'{config.bucket_1_days + 1}-{config.bucket_2_days} ngày'
            config.bucket_3_label = f'{config.bucket_2_days + 1}-{config.bucket_3_days} ngày'
            config.bucket_4_label = f'{config.bucket_3_days + 1}-{config.bucket_4_days} ngày'
            config.bucket_5_label = f'> {config.bucket_5_days} ngày'

    # ==========================================
    # CONSTRAINTS
    # ==========================================
    @api.constrains('bucket_1_days', 'bucket_2_days', 'bucket_3_days',
                    'bucket_4_days', 'bucket_5_days')
    def _check_bucket_sequence(self):
        """Ensure buckets are in ascending order"""
        for config in self:
            if not (config.bucket_1_days < config.bucket_2_days <
                    config.bucket_3_days < config.bucket_4_days <
                    config.bucket_5_days):
                raise ValidationError(_(
                    'Các ngưỡng tuổi nợ phải tăng dần: '
                    'Bucket 1 < Bucket 2 < Bucket 3 < Bucket 4 < Bucket 5'
                ))

            if config.bucket_1_days < 1:
                raise ValidationError(_('Bucket 1 phải >= 1 ngày'))

    # ==========================================
    # HELPER METHODS
    # ==========================================
    @api.model
    def get_company_config(self, company_id=None):
        """Get AR aging config for company (create default if not exists)"""
        if not company_id:
            company_id = self.env.company.id

        config = self.search([('company_id', '=', company_id)], limit=1)
        if not config:
            config = self.create({'company_id': company_id})
        return config

    def get_bucket_for_days(self, days_overdue):
        """
        Return bucket number (0-5) for given days_overdue.
        0 = current (not overdue or <=0)
        1-5 = bucket 1-5
        """
        self.ensure_one()

        if days_overdue <= 0:
            return 0  # Current

        if days_overdue <= self.bucket_1_days:
            return 1
        elif days_overdue <= self.bucket_2_days:
            return 2
        elif days_overdue <= self.bucket_3_days:
            return 3
        elif days_overdue <= self.bucket_4_days:
            return 4
        elif days_overdue <= self.bucket_5_days:
            return 5
        else:
            return 6  # Over bucket 5
