# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID


class HrDocumentType(models.Model):
    _name = 'hr.document.type'
    _order = 'id desc'
    _description = 'HR Document Type'
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    code = fields.Char()


