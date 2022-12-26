# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # recruitment_id = fields.Many2one('res.users')
    create_code_user_id = fields.Many2one('res.users', string='Create code by')
    line_ids = fields.One2many('hr.job.line', 'job_id')

