# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class VendorBillWarningWizard(models.TransientModel):
    _name = 'dtx.vendor.bill.warning.wizard'
    _description = 'Vendor Bill Warning Wizard'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Delivery Order',
        required=True,
        readonly=True,
    )

    missing_lot_ids = fields.Many2many(
        'stock.lot',
        string='Serials with Missing Bills',
        readonly=True,
        help='List of serial numbers that have missing vendor bills',
    )

    missing_lot_count = fields.Integer(
        string='Count',
        compute='_compute_missing_lot_count',
    )

    missing_lot_details = fields.Html(
        string='Details',
        compute='_compute_missing_lot_details',
        help='Formatted list of products and serials with missing bills',
    )

    note = fields.Text(
        string='Justification Note',
        required=True,
        help='Explain why you are proceeding without vendor bills. '
             'Example: "Will obtain replacement invoice later" or '
             '"Purchased without invoice, replacement bill to be linked"',
    )

    @api.depends('missing_lot_ids')
    def _compute_missing_lot_count(self):
        for wizard in self:
            wizard.missing_lot_count = len(wizard.missing_lot_ids)

    @api.depends('missing_lot_ids')
    def _compute_missing_lot_details(self):
        """Generate HTML table with serial details"""
        for wizard in self:
            if not wizard.missing_lot_ids:
                wizard.missing_lot_details = '<p>No missing bills found.</p>'
                continue

            html = '''
                <table class="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Supplier Serial</th>
                            <th>DTX Serial</th>
                            <th>Bill State</th>
                        </tr>
                    </thead>
                    <tbody>
            '''

            for lot in wizard.missing_lot_ids:
                # Get product name
                product_name = lot.product_id.name or 'N/A'

                # Get supplier serial (primary key)
                supplier_serial = lot.name or 'N/A'

                # Get DTX internal serial
                dtx_serial = lot.dtx_serial_internal or 'N/A'

                # Get bill state
                bill_state = dict(
                    lot._fields['vendor_invoice_state'].selection
                ).get(lot.vendor_invoice_state, 'Unknown')

                html += f'''
                    <tr>
                        <td>{product_name}</td>
                        <td>{supplier_serial}</td>
                        <td>{dtx_serial}</td>
                        <td><span class="badge badge-warning">{bill_state}</span></td>
                    </tr>
                '''

            html += '''
                    </tbody>
                </table>
            '''

            wizard.missing_lot_details = html

    def action_confirm(self):
        """
        User confirmed - save notes and proceed with validation.

        Actions:
        1. Append note to each lot's vendor_invoice_note with timestamp and picking ref
        2. Post chatter message on picking
        3. Re-call button_validate with confirmation flag
        """
        self.ensure_one()

        if not self.note:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Note Required',
                    'message': 'Please provide a justification note before proceeding.',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Prepare timestamp and picking reference
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        picking_ref = self.picking_id.name or 'Unknown'

        # Format note with metadata
        formatted_note = f"[{timestamp}] [{picking_ref}] {self.note}"

        # Update each lot's vendor_invoice_note
        for lot in self.missing_lot_ids:
            existing_note = lot.vendor_invoice_note or ''
            if existing_note:
                updated_note = f"{existing_note}\n{formatted_note}"
            else:
                updated_note = formatted_note

            lot.write({'vendor_invoice_note': updated_note})

            _logger.info(
                f"Updated vendor_invoice_note for serial {lot.name} (Product: {lot.product_id.name})"
            )

        # Post chatter message on picking
        chatter_message = f"""
            <p><strong>Vendor Bill Warning Acknowledged</strong></p>
            <p><strong>Serials with missing vendor bills:</strong> {self.missing_lot_count}</p>
            <ul>
                {''.join([f'<li>{lot.name} ({lot.product_id.name})</li>' for lot in self.missing_lot_ids])}
            </ul>
            <p><strong>Justification:</strong> {self.note}</p>
        """

        self.picking_id.message_post(
            body=chatter_message,
            subject='Vendor Bill Warning Acknowledged',
            message_type='notification',
        )

        _logger.info(
            f"Picking {picking_ref}: User acknowledged {self.missing_lot_count} missing vendor bills. "
            f"Note: {self.note[:100]}..."
        )

        # Re-call button_validate with confirmation flag
        return self.picking_id.with_context(
            vendorbill_alert_confirmed=True
        ).button_validate()

    def action_cancel(self):
        """User cancelled - close wizard without validating"""
        return {'type': 'ir.actions.act_window_close'}
