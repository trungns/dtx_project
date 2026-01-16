# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # ==========================================
    # PRODUCT METADATA (visible for ALL products)
    # ==========================================
    x_part_number = fields.Char(
        related='product_id.product_tmpl_id.x_part_number',
        string='Part Number',
        readonly=True,
        store=False,
    )

    x_country_of_origin = fields.Char(
        related='product_id.product_tmpl_id.x_country_of_origin',
        string='Country of Origin',
        readonly=True,
        store=False,
    )

    # ==========================================
    # SUBSCRIPTION FIELDS (only for subscription products)
    # ==========================================
    x_is_subscription = fields.Boolean(
        compute='_compute_is_subscription',
        store=True,
        string='Is Subscription Line',
    )

    x_device_count = fields.Integer(
        string='Số thiết bị / Device Count',
        help='Number of devices for subscription',
    )

    x_months = fields.Integer(
        string='Thời gian (Tháng) / Months',
        help='Subscription duration in months',
    )

    x_subscription_start = fields.Date(
        string='Ngày bắt đầu / Start Date',
        help='Subscription start date',
    )

    x_subscription_end = fields.Date(
        string='Ngày kết thúc / End Date',
        help='Subscription end date',
    )

    # ==========================================
    # SUBSCRIPTION LIFECYCLE MANAGEMENT (v1.7.0)
    # ==========================================
    x_deployment_date = fields.Date(
        string='Ngày triển khai / Deployment Date',
        help='Ngày triển khai thực tế. Nếu để trống, mặc định = Start Date. '
             'Subscription chỉ active khi đã đến ngày triển khai.',
    )

    x_subscription_status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('expiring_soon', 'Expiring Soon'),
            ('expired', 'Expired'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
            ('renewed', 'Renewed'),
        ],
        string='Subscription Status',
        compute='_compute_subscription_status',
        store=True,
        help='Auto-computed status:\n'
             '- Draft: SO not confirmed or before deployment\n'
             '- Active: Deployed and running\n'
             '- Expiring Soon: Less than 30 days to expiry\n'
             '- Expired: Past end date\n'
             '- Suspended/Cancelled: Manual override\n'
             '- Renewed: Renewal SO created',
    )

    x_subscription_status_manual = fields.Selection(
        selection=[
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
        ],
        string='Manual Status Override',
        help='Set manual status to override auto-computed status (Suspended/Cancelled only)',
        tracking=True,
    )

    x_days_to_expiry = fields.Integer(
        string='Days to Expiry',
        compute='_compute_subscription_status',
        store=True,
        help='Number of days until subscription expires (negative = already expired)',
    )

    x_effective_deployment_date = fields.Date(
        string='Effective Deployment Date',
        compute='_compute_subscription_status',
        store=True,
        help='Deployment date if set, otherwise subscription start date',
    )

    # ==========================================
    # COMPUTE METHODS
    # ==========================================
    @api.depends('product_id', 'product_id.product_tmpl_id.x_dtx_type')
    def _compute_is_subscription(self):
        """Check if this line is a subscription product"""
        for line in self:
            line.x_is_subscription = (
                line.product_id
                and line.product_id.product_tmpl_id.x_dtx_type == 'subscription'
            )

    @api.onchange('product_id')
    def _onchange_product_subscription(self):
        """Auto-fill subscription defaults from product"""
        if self.product_id and self.product_id.product_tmpl_id.x_dtx_type == 'subscription':
            self.x_months = self.product_id.product_tmpl_id.x_subscription_default_months or 12
            # Set price_unit from subscription_base_price if available
            if self.product_id.product_tmpl_id.x_subscription_base_price:
                self.price_unit = self.product_id.product_tmpl_id.x_subscription_base_price

    @api.onchange('x_device_count', 'x_months')
    def _onchange_subscription_quantity(self):
        """Auto-calculate quantity = devices × months"""
        if self.x_is_subscription and self.x_device_count and self.x_months:
            self.product_uom_qty = self.x_device_count * self.x_months

    @api.onchange('x_subscription_start', 'x_months')
    def _onchange_subscription_dates(self):
        """Auto-calculate end date from start + months"""
        if self.x_subscription_start and self.x_months:
            self.x_subscription_end = self.x_subscription_start + relativedelta(months=self.x_months)

    @api.depends(
        'order_id.state',
        'x_subscription_start',
        'x_subscription_end',
        'x_deployment_date',
        'x_subscription_status_manual',
        'order_id.x_renewed_by_ids',
    )
    def _compute_subscription_status(self):
        """
        Auto-compute subscription status based on dates and SO state

        Logic:
        1. Manual override (suspended/cancelled) takes precedence
        2. If renewed (has renewal SO) → renewed
        3. If SO not confirmed → draft
        4. If before deployment date → draft
        5. If after end date → expired
        6. If within 30 days of expiry → expiring_soon
        7. Otherwise → active
        """
        from datetime import date

        today = date.today()
        EXPIRY_WARNING_DAYS = 30

        for line in self:
            # Skip non-subscription lines
            if not line.x_is_subscription:
                line.x_subscription_status = False
                line.x_days_to_expiry = 0
                line.x_effective_deployment_date = False
                continue

            # Compute effective deployment date
            line.x_effective_deployment_date = line.x_deployment_date or line.x_subscription_start

            # Compute days to expiry
            if line.x_subscription_end:
                line.x_days_to_expiry = (line.x_subscription_end - today).days
            else:
                line.x_days_to_expiry = 0

            # RULE 1: Manual override (suspended/cancelled)
            if line.x_subscription_status_manual:
                line.x_subscription_status = line.x_subscription_status_manual
                continue

            # RULE 2: Check if renewed (has renewal SO)
            if line.order_id.x_renewed_by_ids:
                line.x_subscription_status = 'renewed'
                continue

            # RULE 3: Check SO state - not confirmed
            if line.order_id.state not in ('sale', 'done'):
                line.x_subscription_status = 'draft'
                continue

            # RULE 4: Before deployment date
            if line.x_effective_deployment_date and today < line.x_effective_deployment_date:
                line.x_subscription_status = 'draft'
                continue

            # RULE 5: Check if expired (past end date)
            if line.x_subscription_end and today > line.x_subscription_end:
                line.x_subscription_status = 'expired'
                continue

            # RULE 6: Check if expiring soon (within 30 days)
            if line.x_subscription_end and line.x_days_to_expiry <= EXPIRY_WARNING_DAYS:
                line.x_subscription_status = 'expiring_soon'
                continue

            # RULE 7: Otherwise, active
            line.x_subscription_status = 'active'

    @api.model
    def cron_update_subscription_status_and_alerts(self):
        """
        Daily cron job to:
        1. Recompute all subscription statuses
        2. Create activities for newly expiring subscriptions
        3. Send email notifications

        Runs once per day at 8:00 AM
        """
        import logging

        _logger = logging.getLogger(__name__)
        _logger.info("Starting subscription status update cron job...")

        # Find all subscription lines in confirmed SOs
        subscription_lines = self.search([
            ('x_is_subscription', '=', True),
            ('order_id.state', 'in', ('sale', 'done')),
        ])

        _logger.info(f"Found {len(subscription_lines)} subscription lines to process")

        # Force recompute status
        subscription_lines._compute_subscription_status()

        # Find lines that just entered "expiring_soon" status
        expiring_lines = subscription_lines.filtered(
            lambda l: l.x_subscription_status == 'expiring_soon'
        )

        activity_created_count = 0
        email_sent_count = 0

        for line in expiring_lines:
            # Check if activity already exists for this line
            existing_activity = self.env['mail.activity'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', line.order_id.id),
                ('summary', 'ilike', f'Subscription expiring: {line.product_id.name}'),
            ], limit=1)

            if existing_activity:
                continue  # Skip if activity already exists

            # Create activity for salesperson
            try:
                line.order_id.activity_schedule(
                    activity_type_xmlid='mail.mail_activity_data_todo',
                    summary=f'Subscription expiring: {line.product_id.name}',
                    note=f"""
                        <p><strong>Subscription Expiry Alert</strong></p>
                        <ul>
                            <li><strong>Customer:</strong> {line.order_id.partner_id.name}</li>
                            <li><strong>Product:</strong> {line.product_id.name}</li>
                            <li><strong>Devices:</strong> {line.x_device_count}</li>
                            <li><strong>End Date:</strong> {line.x_subscription_end}</li>
                            <li><strong>Days to Expiry:</strong> {line.x_days_to_expiry} days</li>
                        </ul>
                        <p>Please contact customer to arrange renewal.</p>
                    """,
                    user_id=line.order_id.user_id.id or self.env.user.id,
                )
                activity_created_count += 1
            except Exception as e:
                _logger.error(f"Failed to create activity for SO {line.order_id.name}: {e}")

            # Send email notification (if template exists)
            try:
                email_template = self.env.ref(
                    'dtx_sales_pakd_contract.mail_template_subscription_expiry',
                    raise_if_not_found=False
                )
                if email_template:
                    email_template.send_mail(
                        line.order_id.id,
                        force_send=False,
                    )
                    email_sent_count += 1
            except Exception as e:
                _logger.error(f"Failed to send email for SO {line.order_id.name}: {e}")

        _logger.info(
            f"Subscription cron job completed: "
            f"{activity_created_count} activities created, "
            f"{email_sent_count} emails sent"
        )

        return True
