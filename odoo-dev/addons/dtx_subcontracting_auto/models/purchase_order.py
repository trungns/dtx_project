import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        """Override button_confirm to auto-create Resupply pickings for subcontracting"""
        res = super().button_confirm()

        for order in self:
            order._create_subcontracting_resupply()

        return res

    def _create_subcontracting_resupply(self):
        """Create Resupply picking for subcontracting orders"""
        self.ensure_one()

        if self.state != 'purchase':
            return

        # Check if resupply already exists
        existing_resupply = self.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing' and p.state != 'cancel'
        )
        if existing_resupply:
            _logger.info(f"Resupply picking already exists for PO {self.name}: {existing_resupply.name}")
            return

        # Process each order line
        for line in self.order_line:
            product = line.product_id

            # Find subcontracting BOM
            bom_dict = self.env['mrp.bom']._bom_find(
                product,
                company_id=self.company_id.id,
                bom_type='subcontract'
            )

            if product not in bom_dict:
                continue

            bom = bom_dict[product]

            # Verify vendor is subcontractor
            if self.partner_id not in bom.subcontractor_ids:
                _logger.warning(
                    f"PO {self.name}: Vendor {self.partner_id.name} is not in BOM subcontractors"
                )
                continue

            # Create Resupply picking
            _logger.info(
                f"Creating Resupply picking for PO {self.name}, "
                f"Product: {product.name}, Vendor: {self.partner_id.name}"
            )

            picking = self._create_resupply_picking(bom, line)
            if picking:
                _logger.info(f"Created Resupply picking: {picking.name}")

    def _create_resupply_picking(self, bom, po_line):
        """Create the actual Resupply picking with components"""
        # Get outgoing picking type
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id.company_id', '=', self.company_id.id)
        ], limit=1)

        if not picking_type:
            _logger.error(f"No outgoing picking type found for company {self.company_id.name}")
            return False

        # Get supplier location
        supplier_loc = self.env.ref('stock.stock_location_suppliers')

        # Create picking
        picking_vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': supplier_loc.id,
            'origin': self.name,
        }

        picking = self.env['stock.picking'].create(picking_vals)

        # Link to PO
        self.write({'picking_ids': [(4, picking.id)]})

        # Create moves for each BOM component
        for bom_line in bom.bom_line_ids:
            qty = bom_line.product_qty * po_line.product_qty

            self.env['stock.move'].create({
                'name': bom_line.product_id.name,
                'product_id': bom_line.product_id.id,
                'product_uom_qty': qty,
                'product_uom': bom_line.product_uom_id.id,
                'picking_id': picking.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': supplier_loc.id,
            })

            _logger.debug(
                f"Added component {bom_line.product_id.name} x {qty} to Resupply picking"
            )

        # Confirm and assign
        picking.action_confirm()
        picking.action_assign()

        return picking
