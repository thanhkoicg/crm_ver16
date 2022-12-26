# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class CrmActivityResult(models.Model):
    _name = "crm.activity.result"
    _description = "Crm Activity Result"
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(tracking=True)
    active = fields.Boolean(default=True)
