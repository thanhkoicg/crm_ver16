# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # customer_of_partner = fields.Char()
    # is_api_partner = fields.Boolean(default=False)
    code = fields.Char() # company_tax_code version 10

    def unlink(self):
        for rcs in self:
            if rcs.code:
                raise UserError(_("Permission denied"))
        return super(ResPartner, self).unlink()
