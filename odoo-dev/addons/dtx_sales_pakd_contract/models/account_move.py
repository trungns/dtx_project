# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from datetime import date

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ==========================================
    # AR AGING FIELDS
    # ==========================================
    x_days_overdue = fields.Integer(
        string='Quá hạn (ngày)',
        compute='_compute_days_overdue',
        help='Số ngày quá hạn thanh toán (today - invoice_date_due)',
    )

    @api.depends('invoice_date_due', 'invoice_date', 'state', 'amount_residual')
    def _compute_days_overdue(self):
        """Compute days overdue for invoices"""
        today = date.today()

        for move in self:
            if move.move_type != 'out_invoice' or move.state != 'posted' or move.amount_residual <= 0:
                move.x_days_overdue = 0
                continue

            due_date = move.invoice_date_due or move.invoice_date
            if due_date:
                move.x_days_overdue = (today - due_date).days
            else:
                move.x_days_overdue = 0
