# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResUsers(models.Model):
    # _inherit = 'res.users'
    _name = 'res.users'
    _inherit = ['res.users', 'mail.thread']

    group_profile_id = fields.Many2one('res.groups', string="Profile Group", tracking=True)
