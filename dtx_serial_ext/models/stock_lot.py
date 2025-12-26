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
        string='Lifecycle State',
        default='stock',
        required=True,
        tracking=True,
        help='Current lifecycle status of the device',
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
        compute='_compute_sale_orders',
        string='Sales Orders',
        help='Sales orders that shipped this serial number',
    )

    customer_invoice_ids = fields.Many2many(
        'account.move',
        compute='_compute_customer_invoices',
        string='Customer Invoices',
        help='Customer invoices linked to sales orders for this serial',
    )

    customer_invoice_note = fields.Text(
        string='Customer Invoice Notes',
        help='Notes about customer invoice',
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
        Path: stock.lot → purchase.order → account.move (where move_type='in_invoice')
        Note: We use invoice_origin field which stores the PO name
        """
        for lot in self:
            if lot.purchase_order_ids:
                # Get all vendor bills that reference these PO names in invoice_origin
                po_names = lot.purchase_order_ids.mapped('name')
                bills = self.env['account.move'].search([
                    ('move_type', '=', 'in_invoice'),
                    ('invoice_origin', 'in', po_names),
                    ('state', '!=', 'cancel'),  # Exclude cancelled bills
                ])
                lot.vendor_bill_ids = bills
            else:
                lot.vendor_bill_ids = False

    @api.depends('purchase_order_ids')
    def _compute_vendor_invoice_state(self):
        """
        Automatically compute vendor invoice state based on vendor bills
        - If posted bills exist → 'linked'
        - If no bills → 'missing'
        - Manual override to 'replaced' is possible (readonly=False)

        Note: Depends on purchase_order_ids instead of vendor_bill_ids
        to ensure proper recomputation when bills are created/posted
        """
        for lot in self:
            # Skip if manually set to 'replaced'
            if lot.vendor_invoice_state == 'replaced':
                continue

            # Find posted vendor bills for this lot's POs
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
        Path: stock.lot → stock.move.line → stock.move → sale.order.line → sale.order
        Note: sale_line_id is only populated on delivery moves (outgoing to customer)
        """
        for lot in self:
            # Get all stock move lines for this serial
            move_lines = self.env['stock.move.line'].search([('lot_id', '=', lot.id)])
            # Extract sale orders from moves that have sale_line_id
            so_lines = move_lines.mapped('move_id.sale_line_id')
            lot.sale_order_ids = so_lines.mapped('order_id')

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
