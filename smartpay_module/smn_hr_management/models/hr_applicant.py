# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')])
    nid = fields.Char('National ID')
    nid_issue_date = fields.Date()
    nid_issue_place_id = fields.Many2one('res.country.province')
    birthday = fields.Date()
    address = fields.Char()
    ward_id = fields.Many2one('res.country.ward')
    district_id = fields.Many2one('res.country.district')
    province_id = fields.Many2one('res.country.province')
    create_code_user_id = fields.Many2one('res.users', string='Create code by')
    # responsible_user_id = fields.Many2one('res.users')
    bank_account = fields.Char()
    bank_id = fields.Many2one('res.bank')
    bank_branch_id = fields.Many2one('res.bank', domain="[('parent_id', '=', bank_id)]")
    current_address = fields.Char()
    current_ward_id = fields.Many2one('res.country.ward')
    current_district_id = fields.Many2one('res.country.district')
    current_province_id = fields.Many2one('res.country.province')
    is_same_address = fields.Boolean(default=False)
    applicant_user_id = fields.Many2one('res.users', string='Applicant User')
    applicant_user_code = fields.Char(related='applicant_user_id.login')
    confirm_user_id = fields.Many2one('res.users', string='Confirm User')
    status_code = fields.Char(related='stage_id.code')
    description = fields.Text(tracking=True)
    created_contract = fields.Boolean()
    team_id = fields.Many2one('crm.team')

    @api.onchange('is_same_address')
    def onchange_activity_id(self):
        if self.is_same_address:
            self.current_province_id = self.province_id.id if self.province_id else False
            self.current_district_id = self.district_id.id if self.district_id else False
            self.current_ward_id = self.ward_id.id if self.ward_id else False
            self.current_address = self.address
        else:
            self.current_province_id = False
            self.current_district_id = False
            self.current_ward_id = False
            self.current_address = False

    # @api.onchange('job_id')
    # def _onchange_job_id(self):
    #     for rcs in self:
    #         rcs.create_code_user_id = False
    #         lines = []
    #         rcs.attachment_ids.unlink()
    #         print('------1: ', rcs._origin.id)
    #         if rcs.job_id and rcs.job_id.line_ids:
    #             for line in rcs.job_id.line_ids:
    #                 rcs.attachment_ids.create( {
    #                     'res_id': self._origin.id,
    #                     'res_model': 'hr.applicant',
    #                     'hr_document_type_id': line.hr_document_type_id.id,
    #                     'name': "No attachment",
    #                     'type': 'binary',
    #                     'public': True
    #                 })
    #                 print('------2: ', self.document_line_ids)
    #             rcs.create_code_user_id = rcs.job_id.create_code_user_id
    #
    #     return

    def act_submit(self):
        self.ensure_one()
        if not self.job_id:
            raise UserError("Please select Applied Job")
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'submit')])
        if not stage_id:
            raise UserError("Not found stage name Submit, contact Admin")
        self.check_require_documents()
        self.stage_id = stage_id.id
        return

    def act_send_to_hr(self):
        self.ensure_one()
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'review')])
        if not stage_id:
            raise UserError("Not found stage name Review, please contact Admin")
        self.stage_id = stage_id.id
        return

    def act_interview(self):
        # next action create code stage draft
        self.ensure_one()
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'interview')])
        if not stage_id:
            raise UserError("Not found stage name Interview, please contact Admin")
        self.stage_id = stage_id.id
        return

    def act_update_profile(self):
        self.ensure_one()
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'update_profile')])
        if not stage_id:
            raise UserError("Not found stage name Update Profile, please contact Admin")
        self.stage_id = stage_id.id
        return

    def act_send_to_create_code(self):
        self.ensure_one()
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'create_code')])
        if not stage_id:
            raise UserError("Not found stage name Create Code, please contact Admin")
        self.stage_id = stage_id.id
        return

    def act_create_code(self):
        self.ensure_one()
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'done')])
        if not stage_id:
            raise UserError("Not found stage name Done, please contact Admin")
        if not self.create_code_user_id:
            raise UserError("Not found Create Code User, please contact Admin")
        if self.create_code_user_id and self.env.user.id != self.create_code_user_id.id:
            raise UserError("Only %s can Create Code for User" %  self.create_code_user_id.name)
        self.stage_id = stage_id.id
        self.act_create_user_applicant()
        return

    def act_reject(self):
        self.ensure_one()
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'reject')])
        if not stage_id:
            raise UserError("Not found stage name Reject, please contact Admin")
        self.stage_id = stage_id.id
        return

    def act_save_applicant(self):
        self.ensure_one()
        stage_id = self.env['hr.recruitment.stage'].search([('code', '=', 'save')])
        if not stage_id:
            raise UserError("Not found stage name Save, please contact Admin")
        self.stage_id = stage_id.id
        return

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            stage_new_id = self.env['hr.recruitment.stage'].search([('code', '=', 'new')])
            values['stage_id'] = stage_new_id.id if stage_new_id else False
            # values['responsible_user_id'] = self.env.user.id

            if values.get('job_id'):
                new_job = self.env['hr.job'].browse(values.get('job_id'))
                if new_job and not new_job.line_ids:
                    raise UserError("Not found Document checklist, please contact HR")
                line_ids = []
                for doc in new_job.line_ids:
                    line_ids.append((0, 0, {
                        'res_model': 'hr.applicant',
                        'hr_document_type_id': doc.hr_document_type_id.id,
                        'name': "No attachment",
                        'type': 'binary',
                        'public': True
                    }))
                values['attachment_ids'] = line_ids
                values['create_code_user_id'] = new_job.create_code_user_id.id
                if self.env.user.partner_id.team_id and self.env.user.partner_id.team_id.user_id:
                    values['confirm_user_id'] = self.env.user.partner_id.team_id.user_id
        return super(HrApplicant, self).create(values)

    def write(self, vals):
        for app in self:
            if 'stage_id' in vals and vals.get('job_id') is False and vals.get('stage_id') is False:
                stage_new_id = self.env['hr.recruitment.stage'].search([('code', '=', 'new')])
                vals['stage_id'] = stage_new_id.id if stage_new_id else False
            if 'job_id' in vals and vals.get('job_id') is False:
                app.attachment_ids.unlink()
            if 'job_id' in vals and vals.get('job_id'):
                app.attachment_ids.unlink()
                new_job = self.env['hr.job'].browse(vals.get('job_id'))
                if new_job and not new_job.line_ids:
                    raise UserError("Not found Document checklist, please contact HR")
                line_ids = []
                for doc in new_job.line_ids:
                    line_ids.append((0, 0, {
                        'res_id': app.id,
                        'res_model': 'hr.applicant',
                        'hr_document_type_id': doc.hr_document_type_id.id,
                        'name': "No attachment",
                        'type': 'binary',
                        'public': True
                    }))
                vals['attachment_ids'] = line_ids
                vals['create_code_user_id'] = new_job.create_code_user_id.id
                if self.env.user.partner_id.team_id and self.env.user.partner_id.team_id.user_id:
                    vals['confirm_user_id'] = self.env.user.partner_id.team_id.user_id
        return super(HrApplicant, self).write(vals)

    def act_create_user_applicant(self):
        self.ensure_one()
        if self.env.user.login != 'admin' and self.create_code_user_id and self.env.user.id != self.create_code_user_id.id:
            raise UserError(_('Just %s can create User' % self.create_code_user_id.name ))
        ex_user = self.env['res.users'].sudo().search([('active', 'in', [False, True])])
        ex_user_login = [x.login for x in ex_user]
        while True:
            sequence_code = self.env['ir.sequence'].next_by_code('create.user.from.hr.applicant')
            if sequence_code == 'SA999999':
                raise UserError('Sequence code is maximum, please contact Admin')
            if sequence_code not in ex_user_login:
                break
        if not sequence_code:
            raise UserError('Not found sequence Login, please contact Admin')
        group_id = self.env['res.groups'].sudo().search([('name', '=', 'Sales Agent')])
        if not group_id:
            raise UserError('Not found group name Sale Agent, please contact Admin')
        user_vals = {
            'name': self.partner_name,
            'login': sequence_code,
            'new_password': self.nid,
            'password': self.nid,
            'create_employee': True,
            'email': self.email_from or 'missemail@mail',
            'group_profile_id': group_id.id,
            # 'groups_id': [(6, 0, [group_id.id])],
            'image_1920': False
        }
        place_of_birth = "%s, %s, %s, %s" % (self.address, self.ward_id.name, self.district_id.name, self.province_id.name)
        parent_id = self.env['hr.employee'].search([('user_id', '=', self.create_uid.id)])
        emp_vals = {
            'department_id': self.department_id.id if self.department_id else False,
            'mobile_phone': self.partner_phone,
            'identification_id': self.nid,
            'birthday': self.birthday and self.birthday,
            'gender': self.gender if self.gender else False,
            'place_of_birth': place_of_birth,
            'job_id': self.job_id.id if self.job_id else False,
            'work_email': self.email_from,
            'work_phone': self.partner_phone,
            'parent_id': parent_id.id if parent_id else False,
        }
        new_user = self.env['res.users'].with_user(SUPERUSER_ID).create(user_vals)
        self.applicant_user_id = new_user.id
        new_user.partner_id.phone = self.partner_phone
        new_user.partner_id.email = self.email_from
        new_user.partner_id.team_id = self.team_id.id
        new_user.partner_id.code = self.applicant_user_code
        employee_id = self.env['hr.employee'].search([('user_id', '=', new_user.id)])
        employee_id.write(emp_vals)
        if self.bank_id and self.bank_account and self.partner_name:
            bank_account_id = self.env['res.partner.bank'].create({
                'acc_number': self.bank_account,
                'partner_id': new_user.partner_id.id,
                'acc_holder_name': self.partner_name,
                'bank_id': self.bank_id.id,
            })
            employee_id.bank_account_id = bank_account_id.id
        template_xml_id = self.env.ref('smn_hr_management.hr_applicant_create_user_mail_template')
        self.send_mail_to_user(template_xml_id)

    def unlink(self):
        error = []
        for rcs in self:
            if rcs.active and rcs.stage_id.code != 'new':
                error.append(rcs.partner_name)
        if error:
            raise UserError("You have to archive %s before delete" % ', '.join(error))
        return super(HrApplicant, self).unlink()

    def act_create_contract(self):
        self.ensure_one()

    def action_open_contract_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.hr_contract_history_view_form_action')
        action['res_id'] = self.id
        return action

    def check_require_documents(self):
        if self.attachment_ids and self.job_id.line_ids and len(self.attachment_ids.ids) != len(self.job_id.line_ids):
            raise UserError("Document error: Your attach %s record, Job Position required attach %s record" % (len(self.attachment_ids.ids), len(self.job_id.line_ids)))
        exit_doc_type = []
        for attach in self.attachment_ids:
            if attach.hr_document_type_id:
                exit_doc_type.append(attach.hr_document_type_id.id)
        job_line_ids = self.job_id.line_ids.search([('hr_document_type_id', 'not in', exit_doc_type), ('job_id', '=', self.job_id.id)])
        if job_line_ids:
            raise UserError("Missing Document type: %s" % ', '.join([job.hr_document_type_id.name for job in job_line_ids]))
        is_required_doc_ids = []
        for doc in self.job_id.line_ids:
            if doc.is_required:
                is_required_doc_ids.append(doc.hr_document_type_id.id)
        missing_attach = []
        for attach in self.attachment_ids:
            if not attach.datas and attach.hr_document_type_id.id in is_required_doc_ids:
                missing_attach.append(attach.hr_document_type_id)
        msgs_required = ""
        for miss_id in missing_attach:
            msgs_required += "%s: attachment is required\n" % miss_id.name
        if missing_attach:
            raise UserError(_(msgs_required))
        return

    def send_mail_to_user(self, template_xml_id):
        ir_config_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_config_param.get_param('web.base.url')
        base_url = base_url.replace("https://", "")
        base_url = base_url.replace("http://", "")
        applicant_url = base_url + "/web#id=" + str(self.id) + "&view_type=form&model=hr.applicant"
        context = {
            'applicant_url': applicant_url,
        }
        email_values = {
            'email_to': self.email_from,
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }
        template_xml_id.with_context(**context).send_mail(
            self.id, force_send=True,
            email_values=email_values,
            email_layout_xmlid='mail.mail_notification_light')
        return
