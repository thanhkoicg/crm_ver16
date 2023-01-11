# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    group_profile_id = fields.Many2one('res.groups', string="Profile Group")

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'group_profile_id' in vals:
            profile_group_ids = self.env['res.groups'].search([('is_profile_group', '=', True)])
            if vals.get('group_profile_id'):
                for gr_id in profile_group_ids:
                    if gr_id.id == vals['group_profile_id']:
                        gr_id.write({'users': [(4, self.id)]})
                    else:
                        gr_id.write({'users': [(3, self.id)]})
            else:
                for gr_id in profile_group_ids:
                    gr_id.write({'users': [(3, self.id)]})
        return res

    # def write(self, vals):
    #     if 'group_profile_id' in vals:
    #         if vals.get('group_profile_id'):
    #             vals['groups_id'] = [(6, 0, [vals['group_profile_id']])]
    #         else:
    #             vals['groups_id'] = [(6, 0, [self.env.ref('base.group_user').id])]
    #     return super(ResUsers, self).write(vals)
