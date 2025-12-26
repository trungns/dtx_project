# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # ==========================================
    # LIFECYCLE STATE AUTO-UPDATE LOGIC
    # ==========================================
    def _action_done(self):
        """
        Override to auto-update serial lifecycle state based on stock moves

        Logic:
        - Incoming (to stock) -> 'stock'
        - Outgoing (from stock to customer) -> 'delivered'
        - To maintenance location -> 'maintenance'
        - To scrap location -> 'scrapped'
        """
        _logger.info("=== DTX Serial Extension: _action_done called for %d move lines ===", len(self))
        res = super()._action_done()

        for move_line in self:
            try:
                # Check if move_line still exists
                if not move_line.exists():
                    _logger.warning("DTX Serial: Move line %s no longer exists, skipping", move_line.id)
                    continue

                if not move_line.lot_id:
                    _logger.debug("DTX Serial: Move line %s has no lot_id, skipping", move_line.id)
                    continue

                lot = move_line.lot_id
                dest_location = move_line.location_dest_id
                source_location = move_line.location_id

                _logger.info("DTX Serial: Processing move line %s - Lot: %s, From: %s (%s) -> To: %s (%s)",
                             move_line.id, lot.name,
                             source_location.complete_name, source_location.usage,
                             dest_location.complete_name, dest_location.usage)

                # Skip if already in terminal state
                if lot.lifecycle_state == 'scrapped':
                    _logger.debug("DTX Serial: Lot %s already scrapped, skipping", lot.name)
                    continue

                # Determine new state based on location type
                new_state = None
            except Exception as e:
                _logger.error("DTX Serial: Error processing move line %s: %s", move_line.id, str(e), exc_info=True)
                continue

            try:
                # SCRAP: Moving to scrap location
                if dest_location.scrap_location:
                    new_state = 'scrapped'
                    _logger.info("DTX Serial: Lot %s -> SCRAPPED (scrap location)", lot.name)

                # MAINTENANCE: Moving to maintenance location
                elif 'maintenance' in dest_location.complete_name.lower():
                    new_state = 'maintenance'
                    _logger.info("DTX Serial: Lot %s -> MAINTENANCE", lot.name)

                # INCOMING: From supplier/production to internal stock
                elif (source_location.usage in ['supplier', 'production'] and
                      dest_location.usage == 'internal'):
                    new_state = 'stock'
                    _logger.info("DTX Serial: Lot %s -> STOCK (incoming from %s)", lot.name, source_location.usage)

                # OUTGOING: From internal to customer
                elif (source_location.usage == 'internal' and
                      dest_location.usage == 'customer'):
                    new_state = 'delivered'
                    _logger.info("DTX Serial: Lot %s -> DELIVERED (outgoing to customer)", lot.name)

                # RETURN: From customer back to internal
                elif (source_location.usage == 'customer' and
                      dest_location.usage == 'internal'):
                    # Return from customer - set back to stock
                    new_state = 'stock'
                    _logger.info("DTX Serial: Lot %s -> STOCK (return from customer)", lot.name)

                # Update state if determined
                if new_state and lot.lifecycle_state != new_state:
                    _logger.info("DTX Serial: Updating lot %s state from '%s' to '%s'",
                                 lot.name, lot.lifecycle_state, new_state)
                    lot.lifecycle_state = new_state

                    # Log the change in chatter
                    lot.message_post(
                        body=f"Lifecycle state automatically updated to '{dict(lot._fields['lifecycle_state'].selection).get(new_state)}' "
                             f"via stock move {move_line.reference or move_line.picking_id.name or 'N/A'}",
                        subject="Lifecycle State Changed",
                    )
                elif new_state:
                    _logger.debug("DTX Serial: Lot %s already in state '%s', no update needed", lot.name, new_state)
            except Exception as e:
                _logger.error("DTX Serial: Error updating lifecycle state for lot %s: %s",
                             lot.name if lot else 'Unknown', str(e), exc_info=True)
                continue

        _logger.info("=== DTX Serial Extension: Completed processing %d move lines ===", len(self))
        return res
