# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class SmnApiHistory(models.Model):
    _name = 'smn.api.history'
    _description = "Api History"
    _order = 'id desc'
    _inherit = ["mail.thread"]

    name = fields.Char()
    link_action = fields.Char()
    send_data = fields.Char()
    receive_data = fields.Char()
    status = fields.Char()
    note = fields.Char()
    partner_id = fields.Many2one('res.partner')
    lead_info = fields.Char()
