# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Province(models.Model):
    _description = 'Province'
    _name = 'res.country.province'
    _order = 'code'

    country_id = fields.Many2one('res.country', string='Country', required=True)
    active = fields.Boolean(default=True)
    name = fields.Char(string='Province Name', required=True)
    code = fields.Char(string='Province Code', required=True)

    def get_district(self):
        if len(self) == 1:
            district_ids = self.env['res.country.district'].search([('province_id', '=', self.id)])
            return district_ids
        return False
