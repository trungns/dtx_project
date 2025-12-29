#!/usr/bin/env python3
"""
Auto-create Resupply picking for Subcontracting PO

Usage:
    docker-compose exec odoo python3 /mnt/scripts/auto_create_resupply.py <PO_NUMBER>

Example:
    docker-compose exec odoo python3 /mnt/scripts/auto_create_resupply.py P00026
"""

import sys
import odoo
from odoo.api import Environment

def create_resupply_for_po(po_number):
    """Create resupply picking for a subcontracting PO"""

    registry = odoo.registry('dtx_dev')
    with registry.cursor() as cr:
        env = Environment(cr, 1, {})

        # Find PO by number
        po = env['purchase.order'].search([('name', '=', po_number)], limit=1)

        if not po:
            print(f"❌ Error: PO {po_number} not found!")
            return False

        print(f"📋 Processing PO: {po.name}")
        print(f"   Vendor: {po.partner_id.name}")
        print(f"   State: {po.state}")

        if po.state != 'purchase':
            print(f"❌ Error: PO must be confirmed! Current state: {po.state}")
            return False

        # Check if PO has Kiosk product
        if not po.order_line:
            print("❌ Error: PO has no order lines!")
            return False

        product = po.order_line[0].product_id
        print(f"   Product: {product.name} (ID: {product.id})")

        # Find BOM
        bom_dict = env['mrp.bom']._bom_find(
            product,
            company_id=po.company_id.id,
            bom_type='subcontract'
        )

        if product not in bom_dict:
            print(f"❌ Error: No subcontracting BOM found for {product.name}")
            print(f"   Make sure:")
            print(f"   - BOM exists for this product")
            print(f"   - BOM type = 'subcontract'")
            print(f"   - BOM has subcontractor assigned")
            return False

        bom = bom_dict[product]
        print(f"✓ Found BOM: {bom.id}")
        print(f"   Type: {bom.type}")
        print(f"   Components: {len(bom.bom_line_ids)}")

        if po.partner_id not in bom.subcontractor_ids:
            print(f"❌ Error: Vendor {po.partner_id.name} is not in BOM subcontractors!")
            print(f"   BOM subcontractors: {[s.name for s in bom.subcontractor_ids]}")
            return False

        print(f"✓ Vendor {po.partner_id.name} is BOM subcontractor")

        # Check if resupply already exists
        existing_resupply = po.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing'
        )

        if existing_resupply:
            print(f"ℹ️  Resupply picking already exists: {existing_resupply.name}")
            print(f"   State: {existing_resupply.state}")
            if existing_resupply.state == 'cancel':
                print("   (Picking is cancelled, will create new one)")
            else:
                return True

        print()
        print("🔧 Creating Resupply picking...")

        # Get outgoing picking type
        picking_type = env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id.company_id', '=', po.company_id.id)
        ], limit=1)

        if not picking_type:
            print("❌ Error: No outgoing picking type found!")
            return False

        # Get supplier location
        supplier_loc = env.ref('stock.stock_location_suppliers')

        # Create Resupply picking
        picking_vals = {
            'partner_id': po.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': supplier_loc.id,
            'origin': po.name,
        }

        resupply_picking = env['stock.picking'].create(picking_vals)
        print(f"✓ Created picking: {resupply_picking.name}")

        # Link to PO
        po.write({'picking_ids': [(4, resupply_picking.id)]})

        # Create stock moves for each component
        print()
        print("📦 Adding components:")
        for bom_line in bom.bom_line_ids:
            qty = bom_line.product_qty * po.order_line[0].product_qty

            move = env['stock.move'].create({
                'name': bom_line.product_id.name,
                'product_id': bom_line.product_id.id,
                'product_uom_qty': qty,
                'product_uom': bom_line.product_uom_id.id,
                'picking_id': resupply_picking.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': supplier_loc.id,
            })

            # Check stock availability
            quants = env['stock.quant'].search([
                ('product_id', '=', bom_line.product_id.id),
                ('location_id', '=', picking_type.default_location_src_id.id),
            ])
            available = sum(quants.mapped('quantity'))

            status = "✓" if available >= qty else "⚠️"
            print(f"   {status} {bom_line.product_id.name} x {qty} (available: {available})")

        # Confirm and assign
        resupply_picking.action_confirm()
        resupply_picking.action_assign()

        print()
        print(f"✅ Resupply picking created: {resupply_picking.name}")
        print(f"   State: {resupply_picking.state}")

        cr.commit()

        # Verify
        po = env['purchase.order'].search([('name', '=', po_number)], limit=1)
        print()
        print(f"📊 PO {po.name} now has {len(po.picking_ids)} picking(s):")
        for pick in po.picking_ids:
            print(f"   - {pick.name}: {pick.picking_type_id.name} ({pick.state})")

        print()
        print("✅ Done! Refresh browser to see updated PO.")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: auto_create_resupply.py <PO_NUMBER>")
        print("Example: auto_create_resupply.py P00026")
        sys.exit(1)

    po_number = sys.argv[1]
    success = create_resupply_for_po(po_number)
    sys.exit(0 if success else 1)
