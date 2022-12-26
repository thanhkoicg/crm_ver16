# -*- coding: utf-8 -*-

from odoo import api, fields, models

class District(models.Model):
    _description = 'District'
    _name = 'res.country.district'
    _order = 'code'

    province_id = fields.Many2one('res.country.province', string='Province', required=True)
    active = fields.Boolean(default=True)
    name = fields.Char(string='District Name', required=True)
    code = fields.Char(string='District Code', required=True)

    def get_ward(self):
        if len(self) == 1:
            ward_ids = self.env['res.country.ward'].search([('district_id', '=', self.id)])
            return ward_ids
        return False