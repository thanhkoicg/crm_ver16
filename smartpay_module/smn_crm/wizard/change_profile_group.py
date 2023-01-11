# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class ChangeProfileGroup(models.TransientModel):
    _name = 'change.profile.group'
    _description = 'Change Profile Group'

    group_profile_id = fields.Many2one('res.groups', string="Profile Group")

    def act_approve(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            user_ids = self.env['res.users'].sudo().browse(active_ids)
            for us_id in user_ids:
                us_id.group_profile_id = self.group_profile_id.id if self.group_profile_id else False
        return