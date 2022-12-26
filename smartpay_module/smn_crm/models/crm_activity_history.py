# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class CrmActivityHistory(models.Model):
    _name = "crm.activity.history"
    _description = "Crm Activity History"
    _inherit = ['mail.thread']
    _rec_name = 'activity_type_id'
    _order = "id desc"

    activity_type_id = fields.Many2one('mail.activity.type', 'Activity Type', index=True, ondelete='set null', tracking=True)
    lead_id = fields.Many2one("crm.lead", ondelete='cascade', tracking=True)
    responsible_user_id = fields.Many2one("res.users")
    date_assign = fields.Datetime()
    activity_result_id = fields.Many2one('crm.activity.result', ondelete='set null', tracking=True)
    date_done = fields.Datetime(tracking=True)
    active = fields.Boolean(default=True)
    status = fields.Selection(selection=[
        ("new", "New"),
        ("wip", "WIP"),
        ("done", "Done"),
        ("cancel", "Cancel")], default='new', tracking=True)
