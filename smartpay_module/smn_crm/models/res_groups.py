# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResGroups(models.Model):
    _inherit = 'res.groups'

    is_profile_group = fields.Boolean(default=False)

