# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """
        Override to trigger recomputation of vendor_invoice_state
        when vendor bills are posted or reset to draft
        """
        res = super().action_post()

        # Find affected serials when vendor bills are posted
        for move in self:
            if move.move_type == 'in_invoice' and move.invoice_origin:
                _logger.info("DTX Serial: Vendor bill %s posted for PO %s, triggering serial recompute",
                             move.name, move.invoice_origin)

                # Find all serials from this PO
                lots = self.env['stock.lot'].search([
                    ('purchase_order_ids.name', '=', move.invoice_origin),
                ])

                if lots:
                    _logger.info("DTX Serial: Found %d serials to recompute for PO %s",
                                 len(lots), move.invoice_origin)

                    # Trigger recomputation by invalidating cache
                    lots.invalidate_cache(['vendor_invoice_state'])

                    # Force recompute
                    for lot in lots:
                        lot._compute_vendor_invoice_state()

                    _logger.info("DTX Serial: Recomputed vendor_invoice_state for serials: %s",
                                 ', '.join(lots.mapped('name')))

        return res

    def button_draft(self):
        """
        Override to trigger recomputation when bills are reset to draft
        """
        # Store PO references before state change
        po_refs = [(move.invoice_origin, move.move_type) for move in self
                   if move.move_type == 'in_invoice' and move.invoice_origin]

        res = super().button_draft()

        # Trigger recompute for affected serials
        for po_ref, move_type in po_refs:
            if move_type == 'in_invoice':
                lots = self.env['stock.lot'].search([
                    ('purchase_order_ids.name', '=', po_ref),
                ])

                if lots:
                    _logger.info("DTX Serial: Bill for PO %s set to draft, recomputing %d serials",
                                 po_ref, len(lots))

                    lots.invalidate_cache(['vendor_invoice_state'])
                    for lot in lots:
                        lot._compute_vendor_invoice_state()

        return res

    def button_cancel(self):
        """
        Override to trigger recomputation when bills are cancelled
        """
        # Store PO references before cancellation
        po_refs = [(move.invoice_origin, move.move_type) for move in self
                   if move.move_type == 'in_invoice' and move.invoice_origin]

        res = super().button_cancel()

        # Trigger recompute for affected serials
        for po_ref, move_type in po_refs:
            if move_type == 'in_invoice':
                lots = self.env['stock.lot'].search([
                    ('purchase_order_ids.name', '=', po_ref),
                ])

                if lots:
                    _logger.info("DTX Serial: Bill for PO %s cancelled, recomputing %d serials",
                                 po_ref, len(lots))

                    lots.invalidate_cache(['vendor_invoice_state'])
                    for lot in lots:
                        lot._compute_vendor_invoice_state()

        return res
