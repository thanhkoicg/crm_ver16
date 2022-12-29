# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


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
