# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class DtxBomTemplate(models.Model):
    _name = 'dtx.bom.template'
    _description = 'DTX BOM Template for Kiosk Manufacturing'
    _order = 'name'

    # ==========================================
    # FIELDS
    # ==========================================

    name = fields.Char(
        string='Tên mẫu BOM',
        required=True,
        help='Ví dụ: "BOM Kiosk Model A", "BOM Check-in Station Standard"',
    )

    finished_product_tmpl_id = fields.Many2one(
        'product.template',
        string='Sản phẩm hoàn chỉnh (Kiosk)',
        required=True,
        domain="[('x_dtx_type', '=', 'finished_kiosk')]",
        help='Sản phẩm Kiosk sẽ được sản xuất từ BOM này',
    )

    component_line_ids = fields.One2many(
        'dtx.bom.template.line',
        'template_id',
        string='Linh kiện',
        help='Danh sách linh kiện cần thiết để lắp ráp Kiosk',
    )

    subcontractor_id = fields.Many2one(
        'res.partner',
        string='Đối tác gia công',
        domain="[('supplier_rank', '>', 0)]",
        help='Nếu có: BOM sẽ được cấu hình cho gia công thuê ngoài (subcontracting)',
    )

    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về quy trình lắp ráp, yêu cầu đặc biệt, v.v.',
    )

    # Related fields (readonly)
    bom_id = fields.Many2one(
        'mrp.bom',
        string='BOM đã tạo',
        readonly=True,
        help='BOM thực tế trong hệ thống Manufacturing',
    )

    bom_exists = fields.Boolean(
        string='BOM đã tồn tại?',
        compute='_compute_bom_exists',
        store=True,
        help='Kiểm tra xem BOM cho sản phẩm này đã được tạo chưa',
    )

    total_components = fields.Integer(
        string='Số lượng linh kiện',
        compute='_compute_total_components',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # ==========================================
    # COMPUTED FIELDS
    # ==========================================

    @api.depends('finished_product_tmpl_id')
    def _compute_bom_exists(self):
        """Check if BOM already exists for the finished product"""
        for template in self:
            if template.finished_product_tmpl_id:
                bom = self.env['mrp.bom'].search([
                    ('product_tmpl_id', '=', template.finished_product_tmpl_id.id),
                ], limit=1)
                template.bom_exists = bool(bom)
                template.bom_id = bom.id if bom else False
            else:
                template.bom_exists = False
                template.bom_id = False

    @api.depends('component_line_ids')
    def _compute_total_components(self):
        """Count total component lines"""
        for template in self:
            template.total_components = len(template.component_line_ids)

    # ==========================================
    # CONSTRAINTS
    # ==========================================

    @api.constrains('finished_product_tmpl_id')
    def _check_finished_product_type(self):
        """Ensure finished product is a Kiosk type"""
        for template in self:
            if template.finished_product_tmpl_id:
                if template.finished_product_tmpl_id.x_dtx_type != 'finished_kiosk':
                    raise ValidationError(
                        f'Sản phẩm "{template.finished_product_tmpl_id.name}" '
                        f'không phải loại "Kiosk / Thiết bị hoàn chỉnh"!\n\n'
                        f'Vui lòng chọn sản phẩm có Loại DTX = "Kiosk / Thiết bị hoàn chỉnh".'
                    )

    @api.constrains('component_line_ids')
    def _check_has_components(self):
        """Ensure at least one component exists"""
        for template in self:
            if not template.component_line_ids:
                raise ValidationError(
                    'BOM template phải có ít nhất 1 linh kiện!\n\n'
                    'Thêm linh kiện vào tab "Linh kiện".'
                )

    # ==========================================
    # ACTIONS
    # ==========================================

    def action_generate_bom(self):
        """
        Generate or update mrp.bom from this template
        Launch wizard for confirmation
        """
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tạo / Cập nhật BOM',
            'res_model': 'dtx.bom.generate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
            },
        }

    def action_view_bom(self):
        """Open the generated BOM"""
        self.ensure_one()

        if not self.bom_id:
            raise UserError('Chưa có BOM được tạo cho template này!\n\nVui lòng click "Tạo BOM" trước.')

        return {
            'type': 'ir.actions.act_window',
            'name': 'BOM',
            'res_model': 'mrp.bom',
            'view_mode': 'form',
            'res_id': self.bom_id.id,
            'target': 'current',
        }

    # ==========================================
    # DISPLAY NAME
    # ==========================================

    def name_get(self):
        """Enhanced display name"""
        result = []
        for template in self:
            if template.finished_product_tmpl_id:
                name = f"{template.name} ({template.finished_product_tmpl_id.name})"
            else:
                name = template.name
            result.append((template.id, name))
        return result


class DtxBomTemplateLine(models.Model):
    _name = 'dtx.bom.template.line'
    _description = 'DTX BOM Template Line - Component'
    _order = 'sequence, id'

    # ==========================================
    # FIELDS
    # ==========================================

    template_id = fields.Many2one(
        'dtx.bom.template',
        string='BOM Template',
        required=True,
        ondelete='cascade',
    )

    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
    )

    component_product_id = fields.Many2one(
        'product.product',
        string='Linh kiện',
        required=True,
        domain="[('type', '=', 'product')]",
        help='Linh kiện cần thiết (thiết bị hoặc vật tư)',
    )

    component_template_id = fields.Many2one(
        'product.template',
        string='Product Template',
        related='component_product_id.product_tmpl_id',
        readonly=True,
    )

    quantity = fields.Float(
        string='Số lượng',
        required=True,
        default=1.0,
        digits='Product Unit of Measure',
        help='Số lượng linh kiện cần thiết cho 1 Kiosk',
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Đơn vị',
        related='component_product_id.uom_id',
        readonly=True,
    )

    notes = fields.Char(
        string='Ghi chú',
        help='Ghi chú về linh kiện này (vị trí lắp, màu sắc, v.v.)',
    )

    # ==========================================
    # CONSTRAINTS
    # ==========================================

    @api.constrains('quantity')
    def _check_quantity(self):
        """Ensure quantity is positive"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError('Số lượng phải lớn hơn 0!')

    @api.constrains('component_product_id', 'template_id')
    def _check_no_duplicate_component(self):
        """Prevent duplicate components in same template"""
        for line in self:
            if line.component_product_id and line.template_id:
                duplicate = self.search([
                    ('id', '!=', line.id),
                    ('template_id', '=', line.template_id.id),
                    ('component_product_id', '=', line.component_product_id.id),
                ])
                if duplicate:
                    raise ValidationError(
                        f'Linh kiện "{line.component_product_id.name}" đã tồn tại trong BOM template này!\n\n'
                        f'Vui lòng chỉnh sửa số lượng thay vì thêm dòng mới.'
                    )

    # ==========================================
    # ONCHANGE
    # ==========================================

    @api.onchange('component_product_id')
    def _onchange_component_product(self):
        """Auto-fill notes with DTX type if available"""
        if self.component_product_id and self.component_product_id.product_tmpl_id.x_dtx_type:
            dtx_type_label = self.component_product_id.product_tmpl_id.get_dtx_type_label()
            if not self.notes and dtx_type_label:
                self.notes = f'Loại: {dtx_type_label}'
