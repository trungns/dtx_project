# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    # ==========================================
    # DTX INTERNAL SERIAL
    # ==========================================
    dtx_serial_internal = fields.Char(
        string='DTX Internal Serial',
        index=True,
        help='Optional DTX internal serial number for customer-facing identification',
    )

    # ==========================================
    # DEVICE LIFECYCLE STATE
    # ==========================================
    lifecycle_state = fields.Selection(
        selection=[
            ('stock', 'In Stock'),
            ('allocated', 'Allocated to Project'),
            ('delivered', 'Delivered'),
            ('installed', 'Installed'),
            ('maintenance', 'Under Maintenance'),
            ('scrapped', 'Scrapped'),
        ],
        string='Lifecycle State (Manual)',
        default='stock',
        required=True,
        tracking=True,
        help='Manual lifecycle status of the device',
    )

    x_lifecycle_state = fields.Selection(
        selection=[
            ('in_stock', 'In Stock'),
            ('subcontracted', 'At Subcontractor'),
            ('in_production', 'In Production'),
            ('delivered', 'Delivered to Customer'),
            ('maintenance', 'Under Maintenance'),
            ('scrapped', 'Scrapped'),
        ],
        string='Lifecycle State (Auto)',
        compute='_compute_x_lifecycle_state',
        store=True,
        help='Automatically computed based on current location',
    )

    # ==========================================
    # PROJECT & CUSTOMER REFERENCES
    # ==========================================
    # Note: project_id will be added when dtx_ops_project module is installed
    # Using related field for now to avoid dependency
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        tracking=True,
        help='Final customer who owns this device',
    )

    # ==========================================
    # PURCHASE ORDER & VENDOR BILL TRACKING
    # ==========================================
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        compute='_compute_purchase_orders',
        string='Purchase Orders',
        help='Purchase orders that supplied this serial number',
    )

    vendor_bill_ids = fields.Many2many(
        'account.move',
        compute='_compute_vendor_bills',
        string='Vendor Bills',
        help='Vendor bills linked to purchase orders for this serial',
    )

    replacement_vendor_bill_id = fields.Many2one(
        'account.move',
        string='Replacement Invoice',
        domain="[('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]",
        tracking=True,
        help='Hoá đơn thay thế cho trường hợp nhập hàng không có hoá đơn gốc. Dùng hoá đơn từ đơn hàng khác để thay thế.',
    )

    vendor_invoice_state = fields.Selection(
        selection=[
            ('missing', 'Invoice Missing'),
            ('linked', 'Invoice Linked'),
            ('replaced', 'Invoice Replaced'),
        ],
        string='Vendor Invoice State',
        compute='_compute_vendor_invoice_state',
        store=True,
        readonly=False,  # Allow manual override when needed
        tracking=True,
        help='Automatically computed based on vendor bills. Auto-set to "linked" when bills exist, "missing" otherwise. Can be manually set to "replaced" for special cases.',
    )

    vendor_invoice_note = fields.Text(
        string='Vendor Invoice Notes',
        help='Notes about invoice replacement, corrections, etc.',
    )

    # ==========================================
    # SALES ORDER & CUSTOMER INVOICE TRACKING
    # ==========================================
    sale_order_ids = fields.Many2many(
        'sale.order',
        'stock_lot_sale_order_rel',
        'lot_id',
        'sale_order_id',
        compute='_compute_sale_orders',
        store=True,
        string='Sales Orders',
        help='Sales orders that shipped this serial number',
    )

    customer_invoice_ids = fields.Many2many(
        'account.move',
        compute='_compute_customer_invoices',
        string='Customer Invoices',
        help='Customer invoices linked to sales orders for this serial',
    )

    customer_invoice_state = fields.Selection(
        selection=[
            ('not_invoiced', 'Not Invoiced'),
            ('invoiced', 'Invoiced'),
            ('paid', 'Paid'),
        ],
        string='Customer Invoice State',
        compute='_compute_customer_invoice_state',
        store=True,
        tracking=True,
        help='Automatically computed based on customer invoices. "not_invoiced" when no invoice exists, "invoiced" when invoice posted but not paid, "paid" when fully paid.',
    )

    customer_invoice_note = fields.Text(
        string='Customer Invoice Notes',
        help='Notes about customer invoice',
    )

    # ==========================================
    # EXTERNAL INVOICE NUMBERS (MISA)
    # ==========================================
    vendor_bill_numbers = fields.Char(
        compute='_compute_vendor_bill_numbers',
        string='Vendor Invoice Numbers',
        help='External invoice numbers from vendor bills (from MISA accounting system)',
    )

    customer_invoice_numbers = fields.Char(
        compute='_compute_customer_invoice_numbers',
        string='Customer Invoice Numbers',
        help='External invoice numbers for customer invoices (from MISA accounting system)',
    )

    # ==========================================
    # WARRANTY TRACKING
    # ==========================================
    warranty_start = fields.Date(
        string='Warranty Start Date',
        help='Supplier warranty start date',
    )

    warranty_end = fields.Date(
        string='Warranty End Date',
        help='Supplier warranty expiration date',
    )

    warranty_active = fields.Boolean(
        string='Warranty Active',
        compute='_compute_warranty_active',
        store=True,
        help='Indicates if warranty is currently active',
    )

    # ==========================================
    # GOOGLE DRIVE LINK
    # ==========================================
    gdrive_link = fields.Char(
        string='Google Drive Link',
        help='Link to device documentation in Google Drive',
    )

    # ==========================================
    # COMPUTED FIELDS
    # ==========================================
    def _compute_x_lifecycle_state(self):
        """
        Compute lifecycle state based on current location of the serial number.

        Logic:
        - Get quants for this serial with qty > 0
        - If no quants (consumed in production), inherit state from finished product
        - Check location type and usage to determine state:
          - Internal (WH/Stock/*) → 'in_stock'
          - Subcontracting location → 'subcontracted'
          - Production location → 'in_production'
          - Customer location → 'delivered'
          - Scrap location → 'scrapped'
          - Maintenance location (custom) → 'maintenance'
        """
        for lot in self:
            # Get stock quants for this serial with positive quantity
            quants = self.env['stock.quant'].search([
                ('lot_id', '=', lot.id),
                ('quantity', '>', 0),
            ])

            if not quants:
                # No stock - check if consumed in production
                # Find stock move lines where this serial was used
                consumed_move_lines = self.env['stock.move.line'].search([
                    ('lot_id', '=', lot.id),
                    ('state', '=', 'done'),
                ])

                # Filter for moves that were consumed in production (raw materials)
                consumed_moves = consumed_move_lines.mapped('move_id').filtered(
                    lambda m: m.raw_material_production_id
                )

                if consumed_moves:
                    # Get the production order where this serial was consumed
                    production = consumed_moves[0].raw_material_production_id
                    finished_lot = production.lot_producing_id

                    if finished_lot:
                        # Recursively compute state of finished product
                        # This handles multi-level BOM scenarios
                        finished_lot._compute_x_lifecycle_state()

                        # Inherit the finished product's state
                        lot.x_lifecycle_state = finished_lot.x_lifecycle_state
                        continue

                # If not consumed or no finished product, default to in_stock
                lot.x_lifecycle_state = 'in_stock'
                continue

            # Get the location with most quantity (in case split across locations)
            main_quant = quants.sorted(key=lambda q: q.quantity, reverse=True)[0]
            location = main_quant.location_id

            # Determine state based on location
            if location.usage == 'internal':
                # Check if it's subcontracting location
                if 'subcontracting' in location.complete_name.lower():
                    lot.x_lifecycle_state = 'subcontracted'
                # Check if it's production location
                elif location.location_id and location.location_id.usage == 'production':
                    lot.x_lifecycle_state = 'in_production'
                # Check if it's maintenance location
                elif 'maintenance' in location.complete_name.lower():
                    lot.x_lifecycle_state = 'maintenance'
                # Regular stock
                else:
                    lot.x_lifecycle_state = 'in_stock'

            elif location.usage == 'customer':
                lot.x_lifecycle_state = 'delivered'

            elif location.usage == 'inventory':
                # Scrap location
                lot.x_lifecycle_state = 'scrapped'

            elif location.usage == 'production':
                # Component in production location - check if consumed in MO with delivered finished product
                consumed_move_lines = self.env['stock.move.line'].search([
                    ('lot_id', '=', lot.id),
                    ('state', '=', 'done'),
                ])

                # Filter for moves that were consumed in production (raw materials)
                consumed_moves = consumed_move_lines.mapped('move_id').filtered(
                    lambda m: m.raw_material_production_id
                )

                if consumed_moves:
                    # Get the production order where this serial was consumed
                    production = consumed_moves[0].raw_material_production_id
                    finished_lot = production.lot_producing_id

                    if finished_lot:
                        # Recursively compute state of finished product
                        finished_lot._compute_x_lifecycle_state()

                        # Inherit the finished product's state
                        # This handles the case where component is "stuck" in production location
                        # but the finished product has been delivered
                        lot.x_lifecycle_state = finished_lot.x_lifecycle_state
                    else:
                        lot.x_lifecycle_state = 'in_production'
                else:
                    lot.x_lifecycle_state = 'in_production'

            else:
                # Default to in_stock for other cases
                lot.x_lifecycle_state = 'in_stock'

    @api.depends('warranty_start', 'warranty_end')
    def _compute_warranty_active(self):
        """Check if warranty is currently active based on dates"""
        today = fields.Date.today()
        for lot in self:
            if lot.warranty_start and lot.warranty_end:
                lot.warranty_active = lot.warranty_start <= today <= lot.warranty_end
            else:
                lot.warranty_active = False

    def _compute_purchase_orders(self):
        """
        Compute purchase orders linked to this serial via stock moves
        Path: stock.lot → stock.move.line → stock.move → purchase.order.line → purchase.order
        """
        for lot in self:
            # Get all stock move lines for this serial
            move_lines = self.env['stock.move.line'].search([('lot_id', '=', lot.id)])
            # Extract purchase orders from moves that have purchase_line_id
            po_lines = move_lines.mapped('move_id.purchase_line_id')
            lot.purchase_order_ids = po_lines.mapped('order_id')

    def _compute_vendor_bills(self):
        """
        Compute vendor bills linked to purchase orders for this serial
        Includes both auto-linked bills from PO and replacement invoice
        Path: stock.lot → purchase.order → account.move (where move_type='in_invoice')
        Note: We use invoice_origin field which stores the PO name
        """
        for lot in self:
            bills = self.env['account.move']

            # Auto-linked bills from PO
            if lot.purchase_order_ids:
                po_names = lot.purchase_order_ids.mapped('name')
                auto_bills = self.env['account.move'].search([
                    ('move_type', '=', 'in_invoice'),
                    ('invoice_origin', 'in', po_names),
                    ('state', '!=', 'cancel'),
                ])
                bills |= auto_bills

            # Add replacement invoice if exists
            if lot.replacement_vendor_bill_id:
                bills |= lot.replacement_vendor_bill_id

            lot.vendor_bill_ids = bills

    @api.depends('purchase_order_ids', 'replacement_vendor_bill_id')
    def _compute_vendor_invoice_state(self):
        """
        Automatically compute vendor invoice state based on vendor bills
        - If replacement invoice exists → 'replaced'
        - If posted bills exist → 'linked'
        - If no bills → 'missing'

        Note: Depends on purchase_order_ids and replacement_vendor_bill_id
        to ensure proper recomputation when bills are created/posted
        """
        for lot in self:
            # Priority 1: Replacement invoice (manual)
            if lot.replacement_vendor_bill_id and lot.replacement_vendor_bill_id.state == 'posted':
                lot.vendor_invoice_state = 'replaced'
                continue

            # Priority 2: Auto-linked bills from PO
            if lot.purchase_order_ids:
                po_names = lot.purchase_order_ids.mapped('name')
                posted_bills = self.env['account.move'].search([
                    ('move_type', '=', 'in_invoice'),
                    ('invoice_origin', 'in', po_names),
                    ('state', '=', 'posted'),
                ], limit=1)

                if posted_bills:
                    lot.vendor_invoice_state = 'linked'
                else:
                    lot.vendor_invoice_state = 'missing'
            else:
                # No POs linked yet
                lot.vendor_invoice_state = 'missing'

    def _compute_sale_orders(self):
        """
        Compute sales orders linked to this serial via stock moves

        Supports THREE paths:
        1. Direct SO line: stock.lot → stock.move.line → stock.move → sale.order.line → sale.order
        2. BoM kit delivery: stock.lot → stock.move.line → stock.picking → sale.order
        3. Consumed in production: stock.lot → mrp.production → finished product serial → sale.order

        Path 2 is for BoM kits where components are delivered together (e.g., kit products)
        Path 3 is for subcontracting/manufacturing where components are consumed in production
        (e.g., KIOSK10 with components TOUCHSCREEN10, MiniPC10)
        """
        for lot in self:
            sale_orders = self.env['sale.order']

            # Get all stock move lines for this serial
            move_lines = self.env['stock.move.line'].search([('lot_id', '=', lot.id)])

            # Path 1: Direct sale line (for products sold directly)
            # Only if sale_stock module is installed
            if 'sale_line_id' in self.env['stock.move']._fields:
                so_lines = move_lines.mapped('move_id.sale_line_id')
                sale_orders |= so_lines.mapped('order_id')

            # Path 2: Via picking sale_id (for BoM kits delivered together)
            # This catches kits where components are delivered in same picking as parent
            # Only if sale_stock module is installed
            if 'sale_id' in self.env['stock.picking']._fields:
                pickings = move_lines.mapped('picking_id')
                sale_orders |= pickings.mapped('sale_id')

            # Path 3: Via production order (for consumed components in manufacturing)
            # Find production orders where this serial was consumed
            consumed_moves = move_lines.mapped('move_id').filtered(
                lambda m: m.raw_material_production_id
            )

            for move in consumed_moves:
                production = move.raw_material_production_id

                # Get the finished product serial from this production
                finished_lot = production.lot_producing_id

                if finished_lot:
                    # Recursively get sale orders for the finished product
                    # This handles multi-level BoMs
                    finished_move_lines = self.env['stock.move.line'].search([
                        ('lot_id', '=', finished_lot.id)
                    ])

                    # Path 3a: Finished product sold directly
                    if 'sale_line_id' in self.env['stock.move']._fields:
                        finished_so_lines = finished_move_lines.mapped('move_id.sale_line_id')
                        sale_orders |= finished_so_lines.mapped('order_id')

                    # Path 3b: Finished product delivered via picking
                    if 'sale_id' in self.env['stock.picking']._fields:
                        finished_pickings = finished_move_lines.mapped('picking_id')
                        sale_orders |= finished_pickings.mapped('sale_id')

            lot.sale_order_ids = sale_orders

    def _compute_customer_invoices(self):
        """
        Compute customer invoices linked to sale orders for this serial
        Path: stock.lot → sale.order → account.move.line → account.move
        Uses the sale_line_ids M2M field on invoice lines to find related invoices
        """
        for lot in self:
            if lot.sale_order_ids:
                # Get all SO lines from the sale orders
                so_lines = lot.sale_order_ids.mapped('order_line')

                # Find invoice lines that reference these SO lines
                invoice_lines = self.env['account.move.line'].search([
                    ('sale_line_ids', 'in', so_lines.ids),
                ])

                # Get the invoices and filter for customer invoices only
                invoices = invoice_lines.mapped('move_id').filtered(
                    lambda m: m.move_type == 'out_invoice' and m.state != 'cancel'
                )
                lot.customer_invoice_ids = invoices
            else:
                lot.customer_invoice_ids = False

    @api.depends('sale_order_ids', 'sale_order_ids.invoice_ids.state', 'sale_order_ids.invoice_ids.payment_state')
    def _compute_customer_invoice_state(self):
        """
        Automatically compute customer invoice state based on customer invoices
        - If all invoices are paid → 'paid'
        - If any invoice posted but not fully paid → 'invoiced'
        - If no invoices → 'not_invoiced'

        Note: Depends on sale_order_ids and related invoice states
        to ensure proper recomputation when invoices are created/posted/paid
        """
        for lot in self:
            if lot.sale_order_ids:
                # Get all SO lines from the sale orders
                so_lines = lot.sale_order_ids.mapped('order_line')

                # Find invoice lines that reference these SO lines
                if 'sale_line_ids' in self.env['account.move.line']._fields:
                    invoice_lines = self.env['account.move.line'].search([
                        ('sale_line_ids', 'in', so_lines.ids),
                    ])

                    # Get posted customer invoices
                    posted_invoices = invoice_lines.mapped('move_id').filtered(
                        lambda m: m.move_type == 'out_invoice' and m.state == 'posted'
                    )

                    if posted_invoices:
                        # Check if all invoices are paid
                        if all(inv.payment_state == 'paid' for inv in posted_invoices):
                            lot.customer_invoice_state = 'paid'
                        else:
                            lot.customer_invoice_state = 'invoiced'
                    else:
                        lot.customer_invoice_state = 'not_invoiced'
                else:
                    # sale_stock module not installed
                    lot.customer_invoice_state = 'not_invoiced'
            else:
                # No sale orders linked
                lot.customer_invoice_state = 'not_invoiced'

    def _compute_vendor_bill_numbers(self):
        """
        Extract external invoice numbers from vendor bills
        Uses the 'ref' field which stores vendor's actual invoice number
        """
        for lot in self:
            if lot.vendor_bill_ids:
                # Get posted bills only
                bills = lot.vendor_bill_ids.filtered(lambda b: b.state == 'posted')
                # Extract ref field (vendor invoice number)
                numbers = bills.mapped('ref')
                # Join with comma, filter out empty values
                lot.vendor_bill_numbers = ', '.join(filter(None, numbers)) or 'N/A'
            else:
                lot.vendor_bill_numbers = 'N/A'

    def _compute_customer_invoice_numbers(self):
        """
        Extract external invoice numbers from customer invoices
        Uses the 'ref' field which stores customer invoice number from MISA
        """
        for lot in self:
            if lot.customer_invoice_ids:
                # Get posted invoices only
                invoices = lot.customer_invoice_ids.filtered(lambda i: i.state == 'posted')
                # Extract ref field (customer invoice number)
                numbers = invoices.mapped('ref')
                # Join with comma, filter out empty values
                lot.customer_invoice_numbers = ', '.join(filter(None, numbers)) or 'N/A'
            else:
                lot.customer_invoice_numbers = 'N/A'

    # ==========================================
    # SEARCH METHODS
    # ==========================================
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """
        Enhanced search to allow searching by both supplier serial (name)
        and DTX internal serial
        """
        args = args or []
        domain = []

        if name:
            domain = [
                '|',
                ('name', operator, name),
                ('dtx_serial_internal', operator, name),
            ]

        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    # ==========================================
    # DISPLAY NAME
    # ==========================================
    def name_get(self):
        """
        Enhanced display name showing both serials if DTX internal exists
        Format: "SUPPLIER_SERIAL [DTX_SERIAL]" or just "SUPPLIER_SERIAL"
        """
        result = []
        for lot in self:
            if lot.dtx_serial_internal:
                name = f"{lot.name} [{lot.dtx_serial_internal}]"
            else:
                name = lot.name
            result.append((lot.id, name))
        return result
