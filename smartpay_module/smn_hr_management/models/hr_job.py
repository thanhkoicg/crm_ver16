# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID


class HrJob(models.Model):
    _inherit = 'hr.job'

    # recruitment_id = fields.Many2one('res.users')
    create_code_user_id = fields.Many2one('res.users', string='Create code by')
    line_ids = fields.One2many('hr.job.line', 'job_id')


class HrJobLine(models.Model):
    _name = 'hr.job.line'

    job_id = fields.Many2one('hr.job', ondelete='cascade')
    hr_document_type_id = fields.Many2one('hr.document.type', required=True)
    name =fields.Char('Description')
    is_required = fields.Boolean('Required')
