# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
from odoo.tools.misc import xlsxwriter
import os

SHEET_LEAD_DETAILS = [
    'Leadid', 'Phone', 'TSA_CODE', 'TSA_name', 'Teamlead', 'Disposition', 'Sub_disposition', 'Salestage',
    'Leadstatus', 'Import_time', 'Last_modified_date', 'Activity', 'Activity - Responsible Name',
    'Activity - Responsible Code', 'Activity Date', 'Remark Done', 'Remark New', 'Campaign']


class CrmMarketingCampaign(models.Model):
    _name = "crm.marketing.campaign"
    _description = "Crm Marketing Campaign"
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(tracking=True)
    start_date = fields.Datetime(string='Validity Period', tracking=True)
    end_date = fields.Datetime(tracking=True)
    partner_ids = fields.Many2many('res.partner')
    product_category_ids = fields.Many2many('product.category', required=True)
    product_template_ids = fields.Many2many('product.template')
    description = fields.Text()
    object_id = fields.Many2one('ir.model', string='Resource', tracking=True)
    partner_field_id = fields.Many2one('ir.model.fields', tracking=True)
    # de_sftp_config_id = fields.Many2one('sftp.config', string='DE Server', tracking=True)
    # de_target_folder = fields.Char('DE Target Folder', tracking=True)
    # qde_target_folder = fields.Char('QDE Target Folder', tracking=True)
    partner_sftp_config_id = fields.Many2one('sftp.config', string='Partner Server', tracking=True, required=True)
    status_target_folder = fields.Char('Status Target Folder', tracking=True, required=True)
    active = fields.Boolean(default=True)
    status = fields.Selection(selection=[
        ("new", "New"),
        ("approved", "Approved to Launch"),
        ("running", "Running"),
        ("done", "Done"),
        ("cancel", "Cancel")], default='new', tracking=True)

    @api.model
    def _cron_export_lead_following_campaign(self):
        marketing_campaigns = self.search([('state', 'in', ['running', 'done']), ('partner_sftp_config_id', '!=', False)])
        xml_id = 'smn_crm.smn_cron_export_lead_following_campaign'
        scheduler_id = self.env.ref(xml_id)
        for campaign in marketing_campaigns:
            lead_sql = """
                SELECT
                    CL.id
                FROM
                    crm_activity_history CAH
                        INNER JOIN crm_lead CL
                            ON CL.id = CAH.lead_id
                        INNER JOIN crm_marketing_campaign MC
                            ON CL.marketing_camp_id = MC.id
                WHERE
                    MC.id = %s AND CAH.state = 'done' AND CAH.date_done > '%s'
                GROUP BY CL.id
                ORDER BY crm_id;""" % (campaign.id, scheduler_id.last_execution_date)
            self._cr.execute(lead_sql)
            list_id_leads = [res[0] for res in self._cr.fetchall()]
            if not list_id_leads:
                continue
            file_name = "%s/%s - %s.xlsx" % (
                os.path.dirname(os.path.abspath(__file__)),
                campaign.name,
                self.convert_to_local_timezone(fields.Datetime.now(), True).strftime("%Y-%m-%d %H-%M-%S"))
            result = self.create_xlsx_file(file_name, list_id_leads)
            if result:
                partner_server = campaign.partner_sftp_config_id
                remote_path = '%s%s' % (
                    partner_server.root_folder,
                    '/' + campaign.status_target_folder if campaign.status_target_folder else '')
                if partner_server.is_encrypted_file:
                    ciphertext = partner_server.encrypt_data_from_file(file_name)
                    with open(file_name, 'wb') as f:
                        f.write(ciphertext)
                self.upload_file_to_sftp_server(file_name, partner_server, remote_path)
        return

    @api.model
    def convert_to_local_timezone(self, str_datetime, return_date=False):
        timestamp = fields.Datetime.from_string(str_datetime)
        local_datetime = fields.Datetime.context_timestamp(self, timestamp)
        if return_date:
            return local_datetime
        return fields.Datetime.to_string(local_datetime)

    @api.model
    def create_xlsx_file(self, file_name, list_id_leads):
        workbook = xlsxwriter.Workbook(file_name)
        if list_id_leads:
            leadsheet = workbook.add_worksheet('Lead Details')
            # Write header for sheet Lead Details
            for col in range(0, len(SHEET_LEAD_DETAILS)):
                leadsheet.write(0, col, SHEET_LEAD_DETAILS[col])
            # Write content for sheet Lead Details
            leads = self.env['crm.lead'].browse(list_id_leads)
            row = 1
            for lead in leads:
                leadsheet.write(row, 0, lead.id)
                leadsheet.write(row, 1, lead.mobile)
                leadsheet.write(row, 2, lead.salesperson_code)
                leadsheet.write(row, 3, lead.user_id and lead.user_id.name or '')
                leadsheet.write(row, 4, lead.team_id and lead.team_id.user_id and lead.team_id.user_id.name or '')
                leadsheet.write(row, 5, lead.stage_id and lead.stage_id.name or '')
                leadsheet.write(row, 9, self.convert_to_local_timezone(lead.create_date))
                leadsheet.write(row, 10, self.convert_to_local_timezone(lead.write_date))
                # Find lastest activity history.
                act_history_sql = """
                    SELECT id
                    FROM crm_activity_history
                    WHERE state='done'
                        AND date_done IS NOT NULL
                        AND lead_id = %s
                    ORDER BY date_done DESC
                    LIMIT 1;
                """ % lead.id
                self._cr.execute(act_history_sql)
                act_history_id = self._cr.fetchone()
                act_history = self.env['crm.activity.history'].browse(act_history_id)
                if not act_history:
                    continue
                act_history_sqlnew = """
                    SELECT id
                    FROM crm_activity_history
                    WHERE state='new' 
                        AND lead_id = %s
                    ORDER BY id DESC
                    LIMIT 1;
                """ % lead.id
                self._cr.execute(act_history_sqlnew)
                act_history_new = self._cr.fetchone()
                act_history_new_id = self.env['crm.activity.history'].browse(act_history_new)
                if not act_history_new_id:
                    continue
                result = act_history.result_id or False
                # leadsheet.write(row, 6, result and result.name or '')
                # leadsheet.write(row, 7,  lead.stage_id and lead.stage_id.name or '')
                leadsheet.write(row, 8, result and result.name or '')
                leadsheet.write(row, 11, act_history.activity_id and act_history.activity_id.name or '')
                leadsheet.write(row, 12, act_history.responsible_user_id and act_history.responsible_user_id.name or '')
                leadsheet.write(row, 13, act_history.responsible_user_id and act_history.responsible_user_id.code or '')
                leadsheet.write(row, 14, act_history.date_done and self.convert_to_local_timezone(act_history.date_done) or '')
                leadsheet.write(row, 15, act_history.note and act_history.note or '')
                leadsheet.write(row, 16, act_history_new_id.note and act_history_new_id.note or '')
                leadsheet.write(row, 17, lead.marketing_camp_id and lead.marketing_camp_id.name or '')
                row += 1
        workbook.close()
        return True

    @api.model
    def upload_file_to_sftp_server(self, file_name, sftp_server, remote_path):
        if not sftp_server:
            self.env['smn.api.history'].sudo().create({
                'name': 'upload_file_to_sftp_server',
                'note': 'Not found SFTP Server',
                'status': 'False'
            })
            return False
        with sftp_server.sftp_connection(test=False) as remote:
            try:
                if not remote.exists(remote_path):
                    remote.makedirs(remote_path)
            except Exception as e:
                self.env['smn.api.history'].sudo().create({
                    'name': 'upload_file_to_sftp_server',
                    'note': 'Error: %s' % e,
                    'status': 'False'
                })

                return False
            try:
                with remote.cd(remote_path):
                    remote.put(file_name)
            except Exception as e:
                self.env['smn.api.history'].sudo().create({
                    'name': 'upload_file_to_sftp_server',
                    'note': 'Error: %s' % e,
                    'status': 'False'
                })
                return False
        return True

    @api.model
    def _cron_start_campaign(self):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        campaigns = self.search([
            ('state', '=', 'approved'),
            ('start_date', '<=', current_date), '|',
            ('end_date', '>=', current_date),
            ('end_date', '=', False)])
        if campaigns:
            campaigns.write({'state': 'running'})

    @api.model
    def _cron_stop_campaign(self):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        campaigns = self.search([('state', '=', 'running'), ('end_date', '<', current_date)])
        if campaigns:
            for campaign in campaigns:
                segments = campaign.mapped('segment_ids').filtered(lambda segment: segment.state == 'running')
                if segments:
                    segments.write({'state': 'done'})
            campaigns.write({'state': 'done'})
