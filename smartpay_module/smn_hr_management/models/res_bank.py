# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID


class ResBank(models.Model):
    _inherit = 'res.bank'

    parent_id = fields.Many2one('res.bank')
