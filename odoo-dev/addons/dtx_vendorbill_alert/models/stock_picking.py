# -*- coding: utf-8 -*-
import logging
from odoo import models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """Override to check for missing vendor bills on outgoing deliveries"""
        self.ensure_one()

        # Only check for outgoing pickings (deliveries)
        if self.picking_type_id.code != 'outgoing':
            return super(StockPicking, self).button_validate()

        # Check if already confirmed by wizard (context flag)
        if self.env.context.get('vendorbill_alert_confirmed'):
            return super(StockPicking, self).button_validate()

        # Find all lots/serials with missing vendor bills
        missing_bill_lots = self._get_missing_bill_lots()

        if not missing_bill_lots:
            # No issues, proceed with normal validation
            return super(StockPicking, self).button_validate()

        # Show warning wizard
        _logger.info(
            f"Picking {self.name}: Found {len(missing_bill_lots)} serials with missing vendor bills. "
            f"Opening warning wizard."
        )

        return {
            'name': 'Vendor Bill Warning',
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.vendor.bill.warning.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
                'default_missing_lot_ids': [(6, 0, missing_bill_lots.ids)],
            },
        }

    def _get_missing_bill_lots(self):
        """
        Find all lots/serials in this picking that have missing vendor bills.

        Returns:
            stock.lot recordset with vendor_invoice_state in ('missing', False)
        """
        self.ensure_one()

        # Get all move lines with lot/serial numbers
        move_lines = self.move_line_ids.filtered(lambda ml: ml.lot_id)

        if not move_lines:
            return self.env['stock.lot']

        # Get all unique lots
        lots = move_lines.mapped('lot_id')

        # Filter lots with missing bills
        # Note: vendor_invoice_state can be 'missing', 'linked', 'replaced', or False (unknown)
        # We consider False (unknown) and 'missing' as problematic
        missing_bill_lots = lots.filtered(
            lambda lot: lot.vendor_invoice_state in ('missing', False)
        )

        return missing_bill_lots
