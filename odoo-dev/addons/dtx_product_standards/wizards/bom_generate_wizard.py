# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class DtxBomGenerateWizard(models.TransientModel):
    _name = 'dtx.bom.generate.wizard'
    _description = 'Wizard to generate/update BOM from template'

    # ==========================================
    # FIELDS
    # ==========================================

    template_id = fields.Many2one(
        'dtx.bom.template',
        string='BOM Template',
        required=True,
        readonly=True,
    )

    finished_product_tmpl_id = fields.Many2one(
        'product.template',
        string='Sản phẩm Kiosk',
        related='template_id.finished_product_tmpl_id',
        readonly=True,
    )

    component_count = fields.Integer(
        string='Số lượng linh kiện',
        related='template_id.total_components',
        readonly=True,
    )

    bom_exists = fields.Boolean(
        string='BOM đã tồn tại',
        related='template_id.bom_exists',
        readonly=True,
    )

    existing_bom_id = fields.Many2one(
        'mrp.bom',
        string='BOM hiện tại',
        related='template_id.bom_id',
        readonly=True,
    )

    subcontractor_id = fields.Many2one(
        'res.partner',
        string='Đối tác gia công',
        related='template_id.subcontractor_id',
        readonly=True,
    )

    mode = fields.Selection([
        ('create', 'Tạo BOM mới'),
        ('update', 'Cập nhật BOM hiện tại'),
    ], string='Chế độ', compute='_compute_mode', readonly=True)

    # Result fields
    state = fields.Selection([
        ('draft', 'Chưa thực hiện'),
        ('done', 'Hoàn tất'),
    ], default='draft')

    result_message = fields.Text(
        string='Kết quả',
        readonly=True,
    )

    created_bom_id = fields.Many2one(
        'mrp.bom',
        string='BOM đã tạo',
        readonly=True,
    )

    # ==========================================
    # COMPUTED
    # ==========================================

    @api.depends('bom_exists')
    def _compute_mode(self):
        """Determine if creating new or updating existing BOM"""
        for wizard in self:
            wizard.mode = 'update' if wizard.bom_exists else 'create'

    # ==========================================
    # ACTIONS
    # ==========================================

    def action_generate_bom(self):
        """Generate or update mrp.bom from template"""
        self.ensure_one()

        template = self.template_id

        # Validation
        if not template.component_line_ids:
            raise UserError('BOM template không có linh kiện nào!\n\nVui lòng thêm linh kiện trước.')

        # Check if BOM exists
        existing_bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', template.finished_product_tmpl_id.id),
        ], limit=1)

        if existing_bom:
            # Update existing BOM
            bom = self._update_bom(existing_bom, template)
            action_text = 'Cập nhật'
        else:
            # Create new BOM
            bom = self._create_bom(template)
            action_text = 'Tạo mới'

        # Update template reference
        template.bom_id = bom.id

        # Build result message
        result_lines = [
            f'=== KẾT QUẢ {action_text.upper()} BOM ===\n',
            f'BOM: {bom.display_name}',
            f'Sản phẩm: {template.finished_product_tmpl_id.name}',
            f'Số lượng linh kiện: {len(template.component_line_ids)}\n',
            'Danh sách linh kiện:',
        ]

        for line in template.component_line_ids:
            result_lines.append(
                f'  • {line.component_product_id.name}: {line.quantity} {line.product_uom_id.name}'
            )

        if template.subcontractor_id:
            result_lines.append(f'\nĐối tác gia công: {template.subcontractor_id.name}')
            result_lines.append('(BOM đã được cấu hình cho subcontracting)')

        # Update wizard state
        self.write({
            'state': 'done',
            'result_message': '\n'.join(result_lines),
            'created_bom_id': bom.id,
        })

        # Return wizard to show results
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dtx.bom.generate.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_view_bom(self):
        """Open the created/updated BOM"""
        self.ensure_one()

        if not self.created_bom_id:
            raise UserError('Không có BOM nào được tạo!')

        return {
            'type': 'ir.actions.act_window',
            'name': 'BOM',
            'res_model': 'mrp.bom',
            'view_mode': 'form',
            'res_id': self.created_bom_id.id,
            'target': 'current',
        }

    def action_close(self):
        """Close wizard"""
        return {'type': 'ir.actions.act_window_close'}

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _create_bom(self, template):
        """Create new mrp.bom from template"""
        bom_vals = {
            'product_tmpl_id': template.finished_product_tmpl_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'code': f'BOM-{template.name}',
        }

        # Configure for subcontracting if subcontractor is set
        if template.subcontractor_id:
            bom_vals.update({
                'type': 'subcontract',
                # In Odoo 16 Community, subcontracting is basic
                # Just set type - components will still be consumed from stock
            })

        # Create BOM
        bom = self.env['mrp.bom'].create(bom_vals)

        # Add component lines
        self._add_bom_lines(bom, template)

        return bom

    def _update_bom(self, bom, template):
        """Update existing mrp.bom from template"""
        # Update BOM header
        bom_vals = {
            'code': f'BOM-{template.name}',
        }

        if template.subcontractor_id:
            bom_vals['type'] = 'subcontract'
        else:
            bom_vals['type'] = 'normal'

        bom.write(bom_vals)

        # Remove old component lines
        bom.bom_line_ids.unlink()

        # Add new component lines
        self._add_bom_lines(bom, template)

        return bom

    def _add_bom_lines(self, bom, template):
        """Add component lines to BOM"""
        for line in template.component_line_ids:
            self.env['mrp.bom.line'].create({
                'bom_id': bom.id,
                'product_id': line.component_product_id.id,
                'product_qty': line.quantity,
                'product_uom_id': line.product_uom_id.id,
                'sequence': line.sequence,
            })
