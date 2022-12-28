# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    content = fields.Html()
    status = fields.Selection([
        ('draft', 'Draft'),
        ('unsigned', 'Unsigned'),
        ('signed', 'Signed'),
        ('expired', 'Expired')
    ], default='draft', tracking=True)
    deadline_sign_date = fields.Date()
    remind_datetime = fields.Date()
    sign_date = fields.Datetime(string='Sign Date', tracking=True, copy=False)

    @api.onchange('contract_type_id')
    def onchange_contract_type_id(self):
        if self.contract_type_id:
            self.content = self.contract_type_id.content
        else:
            self.content = ''
        return

    def act_send(self):
        self.ensure_one()
        if not self.employee_id:
            raise UserError("Please input Employee")
        if not self.contract_type_id:
            raise UserError("Please input Contract Type")
        self.send_email_contract_notify('smn_hr_management.hr_contract_send_to_sign')
        self.update_content_unsigned()
        self.status = 'unsigned'
        return

    def act_sign(self):
        self.ensure_one()
        if self.employee_id and self.employee_id.user_id.id != self.env.user.id:
            raise UserError("Only %s have the right to sign" % self.employee_id.name)
        self.update_content_signed()
        self.status = 'signed'
        return

    def act_expired(self):
        self.ensure_one()
        self.status = 'expired'
        return

    def update_content_unsigned(self):
        if self.content:
            employee = self.employee_id
            applicant_id = self.env['hr.applicant'].search([('applicant_user_id', '=', self.employee_id.user_id.id)])
            if not applicant_id:
                raise UserError("This employee don't have Applicant")
            employee_data = {
                'employee_name': employee.name,
                'contract_number': self.name,
                'birthday': employee.birthday and datetime.strptime(str(employee.birthday), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
                'identification_id': employee.identification_id or '',
                'issue_date': datetime.strptime(str(applicant_id.nid_issue_date), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
                'issue_place': applicant_id.nid_issue_place_id and applicant_id.nid_issue_place_id.name or '',
                'address': employee.place_of_birth,
                'mobile_phone': employee.mobile_phone,
                'email': employee.work_email or '',
                'date_start': self.date_start and datetime.strptime(str(self.date_start), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
                'date_end': self.date_end and datetime.strptime(str(self.date_end), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
                'signed_crm': '',
                'signed_date': '',
                'employee_name_footer': '',
            }
            if self.contract_type_id and self.contract_type_id.content:
                content = self.contract_type_id.content.format(**employee_data)
                self.content = content
        return

    def update_content_signed(self):
        signed_crm = ''
        employee = self.employee_id
        if self.status == 'unsigned':
            signed_crm = u"Đã ký"
        applicant_id = self.env['hr.applicant'].search([('applicant_user_id', '=', self.employee_id.user_id.id)])
        if not applicant_id:
            raise UserError("This employee don't have Applicant")
        employee_data = {
            'employee_name': employee.name,
            'contract_number': self.name,
            'birthday': employee.birthday and datetime.strptime(str(employee.birthday), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
            'identification_id': employee.identification_id or '',
            'issue_date': datetime.strptime(str(applicant_id.nid_issue_date), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
            'issue_place': applicant_id.nid_issue_place_id and applicant_id.nid_issue_place_id.name or '',
            'address': employee.place_of_birth,
            'mobile_phone': employee.mobile_phone,
            'email': employee.work_email or '',
            'date_start': self.date_start and datetime.strptime(str(self.date_start), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
            'date_end': self.date_end and datetime.strptime(str(self.date_end), '%Y-%m-%d').strftime("%d/%m/%Y") or '',
            'signed_crm': signed_crm,
            'signed_date': datetime.now().strftime("%d/%m/%Y"),
            'employee_name_footer': employee.name.upper(),
        }
        if self.contract_type_id and self.contract_type_id.content:
            content = self.contract_type_id.content.format(**employee_data)
            self.content = content
        return

    def cron_set_expired_contract(self):
        today = fields.date.today()
        contracts = self.search([('status', '=', 'signed'), ('date_end', '=', today)])
        for contract in contracts:
            contract.status = 'expired'
        return

    def cron_contract_notify_deadline_need_to_sign(self):
        today = fields.date.today()
        contracts = self.search([('status', '=', 'unsigned')])
        for contract in contracts:
            if contract.deadline_sign_date:
                if not contract.remind_datetime:
                    contract.send_email_contract_notify('smn_hr_management.hr_contract_send_to_sign')
                    if contract.deadline_sign_date < today.strftime('%Y-%m-%d'):
                        contract.remind_datetime = today + timedelta(days=3)
                    else:
                        contract.remind_datetime = datetime.strptime(contract.deadline_sign_date, "%Y-%m-%d") + timedelta(days=3)
                else:
                    if contract.remind_datetime == today.strftime('%Y-%m-%d'):
                        contract.send_email_contract_notify('smn_hr_management.hr_contract_send_to_sign')
                        contract.remind_datetime = today + timedelta(days=3)
        return

    def cron_contract_notify_about_expire(self):
        today = fields.date.today() - timedelta(days=15)
        contracts = self.search([('status', '=', 'signed'), ('date_end', '=', today)])
        ctr_name = []
        hr_cb_email = self.env['ir.config_parameter'].sudo().get_param('smn_email_hr')
        for contract in contracts:
            ctr_name.append(u"[ID-%s] %s" % (contract.id, contract.name))
        if ctr_name:
            email_contract_notify = self.env['ir.config_parameter'].sudo().get_param('smn_hr_management.contract_notify_about_expire')
            template = self.env.ref('smn_hr_management.email_notify_duration_contract')
            template.with_context({
                'email_from': email_contract_notify,
                'email_to': hr_cb_email,
                'list_contract_name': ', '.join(ctr_name),
            }).send_mail(self.id, force_send=True)
        return

    def send_email_contract_notify(self, template_id):
        email_to = []
        ir_config_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_config_param.get_param('web.base.url')
        base_url = base_url.replace("https://", "")
        base_url = base_url.replace("http://", "")
        template = self.env.ref(template_id)
        if self.employee_id:
            if self.employee_id.user_id and self.employee_id.user_id.email:
                email_to.append(self.employee_id.user_id.email)
            if self.employee_id.parent_id and self.employee_id.parent_id.work_email:
                email_to.append(self.employee_id.parent_id.work_email)
        contract_link = base_url + "/web#id=" + str(self.id)+ "&view_type=form&model=hr.contract"
        # email_from = ir_config_param.get_param('smn_email_system_for_notify')
        hr_cb_email = ir_config_param.get_param('smn_email_hr')
        if hr_cb_email:
            email_to.append(hr_cb_email)
        context = {
            'contract_link': contract_link,
            # 'email_from': email_from,
            # 'email_to': ','.join(email_to),
            'smn_email_hr': hr_cb_email
            }
        email_values = {
            'email_to': ','.join(email_to),
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }
        template.with_context(**context).send_mail(
            self.id, force_send=True,
            email_values=email_values,
            email_layout_xmlid='mail.mail_notification_light')
