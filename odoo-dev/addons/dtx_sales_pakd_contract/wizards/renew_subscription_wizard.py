# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class RenewSubscriptionWizard(models.TransientModel):
    _name = 'dtx.renew.subscription.wizard'
    _description = 'Renew Subscription Contract'

    order_id = fields.Many2one(
        'sale.order',
        string='Original SO',
        required=True,
        readonly=True,
    )

    original_start_date = fields.Date(
        string='Original Start Date',
        compute='_compute_original_dates',
        readonly=True,
    )

    original_end_date = fields.Date(
        string='Original End Date',
        compute='_compute_original_dates',
        readonly=True,
    )

    new_start_date = fields.Date(
        string='New Start Date',
        required=True,
    )

    new_months = fields.Integer(
        string='New Duration (Months)',
        default=12,
        required=True,
    )

    new_end_date = fields.Date(
        string='New End Date',
        compute='_compute_new_end_date',
        store=True,
        readonly=True,
    )

    @api.depends('order_id')
    def _compute_original_dates(self):
        """Get start/end dates from original SO subscription lines"""
        for wizard in self:
            if wizard.order_id:
                subscription_lines = wizard.order_id.order_line.filtered('x_is_subscription')
                if subscription_lines:
                    # Get dates from first subscription line
                    first_line = subscription_lines[0]
                    wizard.original_start_date = first_line.x_subscription_start
                    wizard.original_end_date = first_line.x_subscription_end

                    # Auto-set new_start_date to day after original end
                    if first_line.x_subscription_end:
                        wizard.new_start_date = first_line.x_subscription_end + relativedelta(days=1)
                else:
                    wizard.original_start_date = False
                    wizard.original_end_date = False
                    wizard.new_start_date = False
            else:
                wizard.original_start_date = False
                wizard.original_end_date = False
                wizard.new_start_date = False

    @api.depends('new_start_date', 'new_months')
    def _compute_new_end_date(self):
        """Calculate new end date from start + months"""
        for wizard in self:
            if wizard.new_start_date and wizard.new_months:
                wizard.new_end_date = wizard.new_start_date + relativedelta(months=wizard.new_months)
            else:
                wizard.new_end_date = False

    def action_renew(self):
        """Create new SO with updated subscription dates and formal renewal relationship"""
        self.ensure_one()

        # Copy original SO with renewal relationship
        new_order = self.order_id.copy({
            'date_order': fields.Datetime.now(),
            'state': 'draft',
            'x_contract_no': False,  # Clear contract info
            'x_signed_date': False,
            'x_contract_end_date': False,
            'x_advance_amount': 0,
            'x_advance_date': False,
            'x_advance_note': False,
            'x_customer_commission': 0,
            'x_referrer_commission': 0,
            'x_renewal_of_id': self.order_id.id,  # NEW: Formal renewal link
        })

        # Update subscription lines
        for new_line in new_order.order_line.filtered('x_is_subscription'):
            new_line.write({
                'x_subscription_start': self.new_start_date,
                'x_months': self.new_months,
                'x_subscription_end': self.new_end_date,
                'x_deployment_date': False,  # Clear deployment date (will be set when deployed)
                'x_subscription_status_manual': False,  # Clear manual status override
                # Recalculate quantity = device_count × new_months
                'product_uom_qty': new_line.x_device_count * self.new_months if new_line.x_device_count else new_line.product_uom_qty,
            })

        # Link in chatter (keep for backward compatibility)
        self.order_id.message_post(
            body=f"Renewal quotation created: <a href='/web#id={new_order.id}&model=sale.order&view_type=form'>{new_order.name}</a>"
        )
        new_order.message_post(
            body=f"Renews contract: <a href='/web#id={self.order_id.id}&model=sale.order&view_type=form'>{self.order_id.name}</a>"
        )

        # Trigger status recompute on original SO lines (will set to 'renewed')
        self.order_id.order_line.filtered('x_is_subscription')._compute_subscription_status()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': new_order.id,
            'view_mode': 'form',
            'target': 'current',
        }
