# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID


class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    code = fields.Char()
