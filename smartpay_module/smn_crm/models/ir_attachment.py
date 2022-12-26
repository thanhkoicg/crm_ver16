# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        for rcs in self:
            if rcs.res_id and rcs.res_model == 'crm.lead' and self.env.user.id != 1 and self.env.user.login != 'admin':
                lead_id = self.env['crm.lead'].sudo().browse(int(rcs.res_id))
                if lead_id and lead_id.stage_id.code not in ('NEW', 'CG', 'G1', 'G2', 'G3'):
                    raise UserError(_("You can't delete attachment"))
        return super(IrAttachment, self).unlink()
