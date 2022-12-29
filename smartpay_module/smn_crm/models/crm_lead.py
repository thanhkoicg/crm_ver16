# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    status_code = fields.Char(related='stage_id.code')
    nic_number = fields.Char('National ID', help="""Số CMND/CCCD""", tracking=True)
    nic_number_date = fields.Date('Date of NIC', help="""Ngày cấp CMND""", tracking=True)
    nic_number_place = fields.Char('Place of  NIC', help="""Nơi cấp CMND""", tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')], tracking=True, help="""Giới tính""")
    birthday = fields.Date('Date of Birth', tracking=True, help="""Ngày sinh""")
    # Địa chỉ nơi ở (Chi tiết, tỉnh, huyện, xã)
    province_id = fields.Many2one('res.country.province', tracking=True)
    district_id = fields.Many2one('res.country.district', domain="[('province_id', '=', province_id)]", tracking=True)
    ward_id = fields.Many2one('res.country.ward', domain="[('district_id', '=', district_id)]", tracking=True)
    # Địa chỉ hộ khẩu (Chi tiết, tỉnh, huyện, xã)
    household_province_id = fields.Many2one('res.country.province', tracking=True)
    household_district_id = fields.Many2one('res.country.district', domain="[('province_id', '=', household_province_id)]", tracking=True)
    household_ward_id = fields.Many2one('res.country.ward', domain="[('district_id', '=', household_district_id)]", tracking=True)
    household_street = fields.Char(help="""Đường""", tracking=True)

    # Activity model
    assign_user_id = fields.Many2one('res.users', default=lambda self: self.env.user, tracking=True)
    activity_id = fields.Many2one('mail.activity.type', domain="[('stage_id', '=', stage_id)]", string="Todo Activity", tracking=True)
    assign_date = fields.Datetime(tracking=True)
    comp_activity_result_ids = fields.Many2many('crm.activity.result', compute="_compute_result")
    activity_result_id = fields.Many2one('crm.activity.result', domain="[('id', 'in', comp_activity_result_ids)]", tracking=True)
    remark = fields.Char()
    next_assign_user_id = fields.Many2one('res.users', tracking=True)
    comp_next_activity_ids = fields.Many2many('mail.activity.type', compute="_compute_result")
    next_activity_id = fields.Many2one('mail.activity.type', domain="[('id', 'in', comp_next_activity_ids)]", tracking=True)
    next_assign_date = fields.Datetime(tracking=True)
    history_count = fields.Integer(compute="_compute_history_count")

    sale_person_code = fields.Char(related='user_id.login')
    is_same_address = fields.Boolean(default=False, string='Same as Address')
    # campaign_id = fields.Char()

    @api.depends('stage_id', 'activity_id', 'activity_result_id')
    def _compute_history_count(self):
        act_his_ids = self.env['crm.activity.history'].search([('lead_id', '=', self.id)])
        self.history_count = len(act_his_ids) if act_his_ids else 0
        return

    @api.onchange('is_same_address')
    def onchange_activity_id(self):
        if self.is_same_address:
            self.household_province_id = self.province_id.id if self.province_id else False
            self.household_district_id = self.district_id.id if self.district_id else False
            self.household_ward_id = self.ward_id.id if self.ward_id else False
            self.household_street = self.street
        else:
            self.household_province_id = False
            self.household_district_id = False
            self.household_ward_id = False
            self.household_street = False

    @api.depends('activity_id', 'activity_result_id')
    def _compute_result(self):
        activity_result_ids = []
        list_next_activity = []
        if self.activity_id and self.activity_id.line_ids:
            for ac_line in self.activity_id.line_ids:
                activity_result_ids.append(ac_line.result_id.id)
        self.comp_activity_result_ids = activity_result_ids
        if self.activity_id and self.activity_result_id:
            activity_line_id = self.env['mail.activity.type.line'].search([
                ('activity_type_id', '=', self.activity_id.id),
                ('result_id', '=', self.activity_result_id.id)])
            next_activity_id = self.env['mail.activity.type'].search([('stage_id', '=', activity_line_id.stage_id.id)])
            if next_activity_id:
                if len(next_activity_id) > 1:
                    list_next_activity += next_activity_id.ids
                else:
                    list_next_activity.append(next_activity_id.id)
        self.comp_next_activity_ids = list_next_activity
        return

    @api.onchange('activity_id')
    def onchange_activity_id(self):
        if self.activity_id:
            self.activity_result_id = False
            self.next_activity_id = False

    @api.onchange('activity_result_id')
    def onchange_activity_result_id(self):
        if self.activity_result_id:
            self.next_activity_id = False

    def action_view_lead_history(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('smn_crm.action_crm_activity_history')
        action['context'] = {}
        action['domain'] = [('lead_id', '=', self.id)]
        return action

    @api.model_create_multi
    def create(self, values):
        res = super(CrmLead, self).create(values)
        if res.activity_id:
            self.create_activity_history(res.id, res.activity_id, res.assign_user_id, res.assign_date, res.activity_result_id)
        return res

    def write(self, vals):
        for lead in self:
            act_his_id = self.env['crm.activity.history'].search([
                ('activity_type_id', '=', lead.activity_id.id),
                ('lead_id', '=', lead.id),
                ('status', '=', 'new')
            ])
            if act_his_id:
                if vals.get('activity_id') and lead.activity_id.id != vals.get('activity_id'):
                    act_his_id.activity_type_id = vals.get('activity_id')
                if vals.get('activity_result_id') != lead.activity_result_id.id:
                    act_his_id.activity_result_id = vals.get('activity_result_id')
                if vals.get('assign_date') != lead.assign_date:
                    act_his_id.date_assign = vals.get('assign_date')
        return super(CrmLead, self).write(vals)

    def act_done_activity(self):
        for rcs in self:
            if rcs.stage_id.code in ('NEW', 'CG', 'G1', 'G2', 'G3', 'KTDK') and not rcs.next_activity_id:
                raise UserError("Please input Next activity before done Current activity")
            act_his_id = self.env['crm.activity.history'].search([
                ('activity_type_id', '=', rcs.activity_id.id),
                ('lead_id', '=', rcs.id),
                ('status', '=', 'new')
            ])
            if not act_his_id or (act_his_id and len(act_his_id) > 1):
                raise UserError("Exists History greater than 1 or not exists activity, please contact Admin")
            act_his_id.status = 'done'
            act_his_id.date_done = datetime.now()
            rcs.act_change_activity()
        return

    def act_auto_done_activity(self):
        act_his_id = self.env['crm.activity.history'].search([
            ('activity_type_id', '=', self.activity_id.id),
            ('lead_id', '=', self.id),
            ('status', '=', 'new')
        ])
        if not act_his_id or (act_his_id and len(act_his_id) > 1):
            return
            # raise UserError("Exists History greater than 1 or not exists activity, please contact Admin")
        act_his_id.status = 'done'
        act_his_id.date_done = datetime.now()
        self.env['mail.message'].create({
            'author_id': self.env.user.partner_id.id,
            'message_type': 'notification',
            'subtype_id': 2,
            'model': 'crm.activity.history',
            'res_id': act_his_id.id,
            'body': 'Auto done activity when check CIC'
        })
        self.activity_id = False
        self.assign_user_id = False
        self.assign_date = False
        self.next_assign_user_id = False
        self.next_activity_id = False
        self.next_assign_date = False
        self.activity_result_id = False
        return

    def act_change_activity(self):
        create_history = None
        self.activity_id = self.next_activity_id.id
        self.assign_user_id = self.next_assign_user_id.id if self.next_assign_user_id else False
        self.assign_date = self.next_assign_date
        if self.activity_id and self.assign_user_id:
            create_history = self.create_activity_history(self.id, self.activity_id, self.assign_user_id, self.assign_date, self.activity_result_id)
        if not create_history:
            raise UserError("Something wrong when change activity, please contact Admin")
        self.next_assign_user_id = False
        self.next_activity_id = False
        self.next_assign_date = False
        self.activity_result_id = False
        self.stage_id = self.activity_id.stage_id.id
        return

    def create_activity_history(self, lead, activity_id, user_id, assign_date, activity_result_id):
        self.env['crm.activity.history'].create({
            'activity_type_id': activity_id.id,
            'lead_id': lead,
            'responsible_user_id': user_id.id,
            'date_assign': assign_date,
            'activity_result_id': activity_result_id.id,
            'status': 'new'
        })
        return True


    def act_reject_lead(self):
        stage_id = self._get_stage_id('TC')
        self.stage_id = stage_id.id
        return

    def _get_stage_id(self, code):
        status_map_id = self.env['crm.stage'].search([('code', '=', code)], limit=1)
        return status_map_id

    def unlink(self):
        for rcs in self:
            if self.env.user.id != 1 and self.env.user.login != 'admin':
                if self.stage_id.code != 'NEW':
                    raise UserError(_("You can delete when status is New, please cancel Lead"))
        return super(CrmLead, self).unlink()

    def button_click_to_call_mobile(self):
        self.ensure_one()
        if not self.phone:
            raise UserError(_('Please make sure field Mobile is NOT empty.'))

        url = 'cisp:action=click2call&phoneNumber=%s&appId=%s' % (self.phone, self.id)
        return {
            'name': 'Click-to-Call',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'call',
            'url': url
        }

    def add_img_business(self):
        return self.action_open_img_attachment('Business Image', 'business')

    def add_img_cmnd(self):
        return self.action_open_img_attachment('CMND Image', 'cmnd')

    def action_open_img_attachment(self, name, type_img):
        self.ensure_one()
        return {
            'name': name,
            'res_model': 'lead.input.image',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': "{'lead_id': '%s', 'name_input': '%s'}" % (self.id, type_img),
            'target': 'new'
        }

    def check_exists_img(self):
        list_name = ['cmnd_1', 'cmnd_2', 'business_img']
        imgs = self.env['ir.attachment'].search([('res_id', '=', self.id)])
        if not imgs:
            raise UserError('Please input CMND and Business Image')
        num = 0
        for img in imgs:
            if img.name in list_name:
                num += 1
        if num != 3:
            raise UserError('Image not enough for Lead (fontside, backside CMND, Business image')
        return

    def get_full_path_file(self, filename):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        img_id = self.env['ir.attachment'].search([('res_id', '=', self.id), ('name', '=', filename)])
        filename_fullpath = base_url + "/web/content?model=ir.attachment&field=datas&id=%s" % img_id.id
        return filename_fullpath

    def act_cancel_lead(self):
        stage_id = self._get_stage_id('HSH')
        self.stage_id = stage_id.id
        return

    def _cron_import_lead_sftp(self):
        return

    def _cron_export_lead_following_campaign(self):
        return

    @api.model
    def _cron_start_campaign(self):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        marketing_campaign_obj = self.env['crm.marketing.campaign']
        campaigns = marketing_campaign_obj.search([
            ('state', '=', 'approved'),
            ('start_date', '<=', current_date), '|',
            ('end_date', '>=', current_date),
            ('end_date', '=', False)])
        if campaigns:
            campaigns.write({'state': 'running'})

    @api.model
    def _cron_stop_campaign(self):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        marketing_campaign_obj = self.env['crm.marketing.campaign']
        campaigns = marketing_campaign_obj.search([
            ('state', '=', 'running'),
            ('end_date', '<', current_date)])
        if campaigns:
            for campaign in campaigns:
                segments = campaign.mapped('segment_ids').filtered(
                    lambda segment: segment.state == 'running')
                if segments:
                    segments.write({'state': 'done'})
            campaigns.write({'state': 'done'})
