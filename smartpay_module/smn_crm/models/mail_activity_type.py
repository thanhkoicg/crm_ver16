# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    stage_id = fields.Many2one('crm.stage')
    line_ids = fields.One2many('mail.activity.type.line', 'activity_type_id')


class MailActivityTypeLine(models.Model):
    _name = "mail.activity.type.line"
    _description = "Mail Activity Type Line"

    sequence = fields.Integer()
    result_id = fields.Many2one('crm.activity.result', required=True)
    stage_id = fields.Many2one('crm.stage', required=True, string="Next Stage")
    activity_type_id = fields.Many2one('mail.activity.type', ondelete='cascade')
