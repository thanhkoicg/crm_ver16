# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class SmnPopupMessage(models.TransientModel):
    _name = 'lead.input.image'
    _description = 'Image'

    def name_default(self):
        if self._context.get('name_input'):
            return self._context.get('name_input')

    name = fields.Char(default=name_default)
    lead_id = fields.Many2one('crm.lead')
    img_cmnd_1 = fields.Binary(string='CMND Truoc')
    img_cmnd_2 = fields.Binary(string='CMND Sau')
    img_business = fields.Binary(string='Business Image')

    def add_upload_im(self):
        attachment_obj = self.env['ir.attachment']
        lead = int(self._context.get('lead_id'))
        if self.name == 'cmnd':
            if not self.img_cmnd_1 or not self.img_cmnd_2:
                raise UserError('You must input fontside and backside of Identification Image')
            exist_img_1 = attachment_obj.search([
                ('name', '=', 'cmnd_1'), ('res_id', '=', lead), ('res_model', '=', 'crm.lead')])
            exist_img_2 = attachment_obj.search([
                ('name', '=', 'cmnd_2'), ('res_id', '=', lead), ('res_model', '=', 'crm.lead')])
            if exist_img_1:
                exist_img_1.unlink()
            if exist_img_2:
                exist_img_2.unlink()
            attachment_obj.create({
                'name': 'cmnd_1',
                'datas': self.img_cmnd_1,
                'res_id': lead,
                'res_model': 'crm.lead',
            })
            attachment_obj.create({
                'name': 'cmnd_2',
                'datas': self.img_cmnd_2,
                'res_id': lead,
                'res_model': 'crm.lead',
            })
        else:
            if not self.img_business:
                raise UserError('You must input Business image')
            exist_img_business = attachment_obj.search([
                ('name', '=', 'business_img'), ('res_id', '=', lead), ('res_model', '=', 'crm.lead')])
            if exist_img_business:
                exist_img_business.unlink()
            attachment_obj.create({
                'name': 'business_img',
                'datas': self.img_business,
                'res_id': lead,
                'res_model': 'crm.lead',
            })
        return
