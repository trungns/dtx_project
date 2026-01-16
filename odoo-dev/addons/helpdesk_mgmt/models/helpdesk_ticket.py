from datetime import timedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError, UserError, ValidationError


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _rec_name = "number"
    _rec_names_search = ["number", "name"]
    _order = "priority desc, sequence, number desc, id desc"
    _mail_post_access = "read"
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "portal.mixin"]

    @api.depends("team_id")
    def _compute_stage_id(self):
        for ticket in self:
            ticket.stage_id = ticket.team_id._get_applicable_stages()[:1]

    @api.depends("team_id")
    def _compute_user_id(self):
        for ticket in self:
            if not ticket.user_id and ticket.team_id:
                ticket.user_id = ticket.team_id.alias_user_id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Show always the stages without team, or stages of the default team."""
        search_domain = [
            "|",
            ("id", "in", stages.ids),
            ("team_ids", "=", False),
        ]
        default_team_id = self.default_get(["team_id"]).get("team_id")
        if default_team_id:
            search_domain = [
                "|",
                ("team_ids", "=", default_team_id),
            ] + search_domain
        return stages.search(search_domain, order=order)

    number = fields.Char(string="Ticket number", default="/", readonly=True)
    name = fields.Char(string="Title", required=True)
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned user",
        tracking=True,
        index=True,
        compute="_compute_user_id",
        store=True,
        readonly=False,
        domain="team_id and [('share', '=', False),('id', 'in', user_ids)] or [('share', '=', False)]",  # noqa: B950
    )
    user_ids = fields.Many2many(
        comodel_name="res.users", related="team_id.user_ids", string="Users"
    )
    stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        string="Stage",
        compute="_compute_stage_id",
        store=True,
        readonly=False,
        ondelete="restrict",
        tracking=True,
        group_expand="_read_group_stage_ids",
        copy=False,
        index=True,
        domain="['|',('team_ids', '=', team_id),('team_ids','=',False)]",
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    commercial_partner_id = fields.Many2one(
        string="Commercial Partner",
        store=True,
        related="partner_id.commercial_partner_id",
    )
    partner_name = fields.Char()
    partner_email = fields.Char(string="Email")
    last_stage_update = fields.Datetime(default=fields.Datetime.now)
    assigned_date = fields.Datetime()
    closed_date = fields.Datetime()
    closed = fields.Boolean(related="stage_id.closed")
    unattended = fields.Boolean(related="stage_id.unattended", store=True)
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag", string="Tags", tracking=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    channel_id = fields.Many2one(
        comodel_name="helpdesk.ticket.channel",
        string="Channel",
        help="Channel indicates where the source of a ticket"
        "comes from (it could be a phone call, an email...)",
    )
    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
    )
    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Team",
        index=True,
    )
    priority = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        default="1",
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        domain=[("res_model", "=", "helpdesk.ticket")],
        string="Media Attachments",
    )
    color = fields.Integer(string="Color Index")
    kanban_state = fields.Selection(
        selection=[
            ("normal", "Default"),
            ("done", "Ready for next stage"),
            ("blocked", "Blocked"),
        ],
    )
    sequence = fields.Integer(
        index=True,
        default=10,
        help="Gives the sequence order when displaying a list of tickets.",
    )
    active = fields.Boolean(default=True)
    approver_id = fields.Many2one(
        comodel_name="res.users",
        string="Người phê duyệt",
        compute="_compute_approver_id",
        store=True,
        tracking=True
    )
    
    @api.depends('team_id')
    def _compute_approver_id(self):
        for ticket in self:
            ticket.approver_id = False
            if ticket.team_id and ticket.team_id.approver_id:
                ticket.approver_id = ticket.team_id.approver_id
                
    # Lưu stage phê duyệt cao nhất đã qua
    approval_stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string="Giai đoạn phê duyệt đã qua",
        store=True,
        compute="_compute_approval_stage_id",
        tracking=True
    )
    
    @api.depends("stage_id")
    def _compute_approval_stage_id(self):
        for ticket in self:
            ticket.approval_stage_id = False
            if ticket.stage_id and ticket.team_id.approval_stage_ids and ticket.stage_id in ticket.team_id.approval_stage_ids:
                ticket.approval_stage_id = ticket.stage_id
            
    is_stage_changed = fields.Boolean(
        string="Stage đã được chuyển",
        default=False,
    )
    
    can_edit = fields.Boolean(
        string="Có thể cập nhật",
        compute="_compute_can_edit_fields",
    )
    
    @api.depends("stage_id", "is_stage_changed", "approver_id")
    def _compute_can_edit_fields(self):
        for ticket in self:
            if not ticket.is_stage_changed:
                ticket.can_edit = True
            else:
                if ticket.approver_id == self.env.user:
                    ticket.can_edit = True
                else:
                    ticket.can_edit = False
    
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.number + " - " + rec.name))
        return res

    def assign_to_me(self):
        self.write({"user_id": self.env.user.id})

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    def _creation_subtype(self):
        return self.env.ref("helpdesk_mgmt.hlp_tck_created")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("number", "/") == "/":
                vals["number"] = self._prepare_ticket_number(vals)
            if vals.get("user_id") and not vals.get("assigned_date"):
                vals["assigned_date"] = fields.Datetime.now()
            if vals.get("team_id"):
                team = self.env["helpdesk.ticket.team"].browse([vals["team_id"]])
                if team.company_id:
                    vals["company_id"] = team.company_id.id
            # Automatically set default e-mail channel when created from the
            # fetchmail cron task
            if self.env.context.get("fetchmail_cron_running") and not vals.get(
                "channel_id"
            ):
                channel_email_id = self.env.ref(
                    "helpdesk_mgmt.helpdesk_ticket_channel_email",
                    raise_if_not_found=False,
                )
                if channel_email_id:
                    vals["channel_id"] = channel_email_id.id
        tickets = super().create(vals_list)

        # Tự động thêm người theo dõi
        for ticket in tickets:

            # Lọc và xóa người theo dõi không mong muốn
            self._filter_followers(ticket)
            
            followers_to_add = []

            # Thêm người tạo
            if ticket.create_uid:
                followers_to_add.append(ticket.create_uid.partner_id.id)

            # Thêm người phụ trách
            if ticket.user_id:
                followers_to_add.append(ticket.user_id.partner_id.id)

            # Thêm người phê duyệt
            if ticket.approver_id:
                followers_to_add.append(ticket.approver_id.partner_id.id)

            # Loại bỏ trùng lặp và đăng ký theo dõi
            followers_to_add = list(set(followers_to_add))
            if followers_to_add:
                ticket.message_subscribe(partner_ids=followers_to_add)

        return tickets

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super().copy(default)
        return res

    def write(self, vals):
        old_stages = {ticket.id: ticket.stage_id for ticket in self}
        old_descriptions = {ticket.id: ticket.description or '' for ticket in self}
        
        for _ticket in self:
            now = fields.Datetime.now()
            if vals.get("stage_id"):
                stage = self.env["helpdesk.ticket.stage"].browse([vals["stage_id"]])
                vals["last_stage_update"] = now
                if stage.closed:
                    vals["closed_date"] = now
                if stage != _ticket.stage_id:
                    vals["is_stage_changed"] = True
                self._validate_stage_transition(_ticket, stage)
            if vals.get("user_id"):
                vals["assigned_date"] = now
        
        result = super().write(vals)
        
        for ticket in self:
            # Log activity sửa mô tả
            if vals.get("description"):
                description = vals["description"]
                old_description = old_descriptions[ticket.id]
                if description != old_description:
                    log_message = f"""<strong>Thay đổi mô tả:</strong>
                                        <ul>
                                            <li><strong>Từ:</strong>{old_description}</li>
                                            <li><strong>Sang:</strong>{description}</li>
                                        </ul>"""
                    self._log_activities(self.id, log_message)
                    
            # Cập nhật trạng thái phê duyệt và gửi thông báo
            if vals.get("stage_id"):
                new_stage = self.env["helpdesk.ticket.stage"].browse([vals["stage_id"]])
                old_stage = old_stages[ticket.id]
                if old_stage != new_stage:
                    self._send_stage_change_notification(ticket, new_stage)
        
            # Cập nhật danh sách người theo dõi
            self._filter_followers(ticket)
        
        return result


    def action_duplicate_tickets(self):
        for ticket in self.browse(self.env.context["active_ids"]):
            ticket.copy()

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_company(values["company_id"])
        return seq.next_by_code("helpdesk.ticket.sequence") or "/"
    
    # Kiểm tra việc chuyển giai đoạn theo quy trình phê duyệt
    def _validate_stage_transition(self, ticket, new_stage):
        current_user = self.env.user
        current_stage = ticket.stage_id
        # Check lùi giai đoạn
        if new_stage.sequence < current_stage.sequence:
            raise UserError(
                _("Bạn chỉ có thể di chuyển ticket theo trình tự tiến của giai đoạn, không được chuyển lùi lại!")
            )
        team = ticket.team_id
        # Nếu không có team hoặc không có gđ cần phê duyệt hoặc không có người phê duyệt thì return
        if not team or not team.approval_stage_ids or not ticket.approver_id:
            return

        approval_stages = team.approval_stage_ids
        approver = team.approver_id
        
        # TH gđ mới là gđ cần phê duyệt thì check người phê duyệt
        if new_stage in approval_stages:
            if approver and current_user != approver:
                raise UserError(
                    _("Chỉ có người phê duyệt mới được quyền chuyển sang giai đoạn này!")
                )
        # TH gđ mới không phải là gđ cần phê duyệt thì check đã qua gđ cần phê duyệt ở giữa gđ mới và cũ chưa
        else:
            approval_stages_between = approval_stages.filtered(
                lambda s: current_stage.sequence < s.sequence < new_stage.sequence
            )
            sequences = approval_stages_between.mapped("sequence")
            if sequences:
                # Kiểm tra xem ticket đã qua giai đoạn phê duyệt nào trong khoảng này chưa
                if not ticket.approval_stage_id or ticket.approval_stage_id.sequence not in sequences:
                    names = approval_stages_between.mapped("name")
                    raise UserError(
                        _("Đội ngũ %s được cấu hình cần phê duyệt tại giai đoạn %s. "
                          "Bạn vui lòng chuyển Ticket qua giai đoạn %s trước khi "
                          "chuyển qua giai đoạn %s") % (
                            team.name, ', '.join(names), ', '.join(names), new_stage.name
                        )
                    )

    def _send_stage_change_notification(self, ticket, new_stage):
        current_user = self.env.user

        # Message thông báo
        message = _("Trung tâm hỗ trợ: %s đã chuyển ticket %s sang giai đoạn %s") % (
            current_user.name, ticket.number, new_stage.name
        )

        # Lấy thông tin của người theo dõi trừ người đang thao tác
        followers = ticket.message_follower_ids.filtered(
            lambda f: f.partner_id != current_user.partner_id
        )
        
        # Tạo mail activity với thời hạn 24h cho người theo dõi
        if followers:
            activity_type = self.env.ref('mail.mail_activity_data_todo')
            user_ids = []
            for follower in followers:
                # Tìm user từ partner_id của follower
                user = self.env['res.users'].search([
                    ('partner_id', '=', follower.partner_id.id),
                    ('active', '=', True)
                ], limit=1)
                
                if user:
                    user_ids.append(user.id)
                    # Tạo mail activity
                    ticket.activity_schedule(
                        activity_type_id=activity_type.id,
                        user_id=user.id,
                        date_deadline=fields.Date.today() + timedelta(days=1),
                        summary=message
                    )
            
            # Gửi notification nổi trên màn hình
            view_id = self.env.ref('helpdesk_mgmt.ticket_view_form').id
        
            url = f"/web#id={ticket.id}&model=helpdesk.ticket&view_type=form&view_id={view_id}"
            
            action = {
                'type': 'ir.actions.act_url',
                'name': 'Thông báo ticket',
                'url': url,
                'target': 'new',
            }
        
            if user_ids:
                self.send_notify(
                    title=message,
                    message='',
                    user_ids=user_ids,
                    type="info",
                    action=action,
                    res_id=ticket.id,
                    res_model=ticket._name
                )

    def _compute_access_url(self):
        res = super()._compute_access_url()
        for item in self:
            item.access_url = "/my/ticket/%s" % (item.id)
        return res

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _track_template(self, tracking):
        res = super()._track_template(tracking)
        ticket = self[0]
        if "stage_id" in tracking and ticket.stage_id.mail_template_id:
            res["stage_id"] = (
                ticket.stage_id.mail_template_id,
                {
                    # Need to set mass_mail so that the email will always be sent
                    "composition_mode": "mass_mail",
                    "auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            "name": msg.get("subject") or _("No Subject"),
            "description": msg.get("body"),
            "partner_email": msg.get("from"),
            "partner_id": msg.get("author_id"),
        }
        defaults.update(custom_values)

        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)

        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=ticket, force_create=False
            )
            if p
        ]
        ticket.message_subscribe(partner_ids)

        return ticket

    def message_update(self, msg, update_vals=None):
        """Override message_update to subscribe partners"""
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=self, force_create=False
            )
            if p
        ]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    def _message_get_suggested_recipients(self):
        recipients = super()._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id:
                    ticket._message_add_suggested_recipient(
                        recipients, partner=ticket.partner_id, reason=_("Customer")
                    )
                elif ticket.partner_email:
                    ticket._message_add_suggested_recipient(
                        recipients,
                        email=ticket.partner_email,
                        reason=_("Customer Email"),
                    )
        except AccessError:
            # no read access rights -> just ignore suggested recipients because this
            # imply modifying followers
            return recipients
        return recipients

    def _filter_followers(self, ticket):
        """Lọc và xóa người theo dõi không thuộc 3 đối tượng được chỉ định:
        1. Người tạo (create_uid)
        2. Người phụ trách (user_id)
        3. Người phê duyệt (approver_id nếu có)
        """
        # Lấy danh sách người theo dõi hiện tại
        followers = ticket.message_follower_ids.mapped('partner_id')
        
        # Lấy danh sách 3 đối tượng được chỉ định
        allowed_partners = self.env['res.partner']
        
        # 1. Người tạo
        if ticket.create_uid and ticket.create_uid.partner_id:
            allowed_partners |= ticket.create_uid.partner_id
            
        # 2. Người phụ trách
        if ticket.user_id and ticket.user_id.partner_id:
            allowed_partners |= ticket.user_id.partner_id
            
        # 3. Người phê duyệt (nếu có)
        if hasattr(ticket, 'approver_id') and ticket.approver_id and ticket.approver_id.partner_id:
            allowed_partners |= ticket.approver_id.partner_id
        
        # Lọc ra những người theo dõi không thuộc 3 đối tượng được chỉ định
        partners_to_remove = followers - allowed_partners
        followers_to_remove = ticket.message_follower_ids.filtered(
            lambda f: f.partner_id in partners_to_remove
        )
        
        # Xóa người theo dõi không mong muốn
        if followers_to_remove:
            followers_to_remove.sudo().unlink()
    
    def _notify_get_reply_to(self, default=None):
        """Override to set alias of tasks to their team if any."""
        aliases = self.sudo().mapped("team_id")._notify_get_reply_to(default=default)
        res = {ticket.id: aliases.get(ticket.team_id.id) for ticket in self}
        leftover = self.filtered(lambda rec: not rec.team_id)
        if leftover:
            res.update(
                super(HelpdeskTicket, leftover)._notify_get_reply_to(default=default)
            )
        return res
        
    def _log_activities(self, ticket_id: int, message):
        # cập nhật log activities
        self.env['mail.message'].create({
            'model': 'helpdesk.ticket',
            'res_id': ticket_id,
            'message_type': 'comment',
            'body': message,
        })