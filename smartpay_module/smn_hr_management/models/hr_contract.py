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

    def act_send(self):
        self.ensure_one()
        if not self.employee_id:
            raise UserError("Please input Employee")
        template_xml_id = self.env.ref('smn_hr_management.hr_contract_send_to_sign')
        self.send_mail_to_user(template_xml_id)
        self.status = 'unsigned'
        return

    def act_sign(self):
        self.ensure_one()
        if self.employee_id and self.employee_id.user_id.id != self.env.user.id:
            raise UserError("Only %s have the right to sign" % self.employee_id.name)
        self.status = 'signed'
        return

    def act_expired(self):
        self.ensure_one()
        self.status = 'expired'
        return

    def send_mail_to_user(self, template_xml_id):
        content = {}
        ir_config_param = self.env['ir.config_parameter'].sudo()
        email_from = ir_config_param.get_param('smn_email_system_for_notify')
        content.update({
            'email_from': email_from,
            'email_to': self.employee_id.user_id.email
        })
        template_xml_id.with_user(SUPERUSER_ID).with_context(content).send_mail(self.id, force_send=True)
        return

    def cron_set_expired_contract(self):
        contract_ids = self.search()

        return

    def cron_contract_notify_deadline_need_to_sign(self):
        today = fields.date.today()
        contracts = self.search([('state', '=', 'sign')])
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
        contracts = self.search([('state', '=', 'open'), ('date_end', '=', today)])
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
        date_start = self.date_start and datetime.strptime(self.date_start, '%Y-%m-%d').strftime("%d/%m/%Y") or ''
        date_end = self.date_end and datetime.strptime(self.date_end, '%Y-%m-%d').strftime("%d/%m/%Y") or ''
        email_from = ir_config_param.get_param('smn_email_system_for_notify')
        hr_cb_email = ir_config_param.get_param('smn_email_hr')
        if hr_cb_email:
            email_to.append(hr_cb_email)
        template.with_context({
            'contact_number': self.name,
            'date_start': date_start,
            'date_end': date_end,
            'deadline_sign_date'
            'contract_link': contract_link,
            'email_from': email_from,
            'email_to': ','.join(email_to),
            'smn_email_hr': self.employee_id.name,
            'contract_type': self.contract_type_id.name if self.contract_type_id else '',
            }).send_mail(self.id, force_send=True)

