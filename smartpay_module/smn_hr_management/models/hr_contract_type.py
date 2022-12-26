# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID


class HrContractType(models.Model):
    _inherit = 'hr.contract.type'

    content = fields.Html()
