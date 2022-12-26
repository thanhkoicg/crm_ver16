# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    hr_document_type_id = fields.Many2one('hr.document.type')
    # is_required = fields.Boolean('Required')

    def unlink(self):
        for rcs in self:
            if rcs.res_model and rcs.res_model == 'hr.applicant' and rcs.res_id:
                applicant_id = self.env['hr.applicant'].browse(int(rcs.res_id))
                if applicant_id.stage_id.code != 'new' and applicant_id.active:
                    raise UserError("You can delete attach file when Stage of HR Applicant stage is New")
        return super(IrAttachment, self).unlink()

    @api.onchange('datas')
    def onchange_datas(self):
        for rcs in self:
            if rcs.res_model and rcs.res_model == 'hr.applicant' and rcs.res_id and not rcs.datas:
                rcs.name = "No Attachment"
