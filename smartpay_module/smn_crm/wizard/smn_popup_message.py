# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SmnPopupMessage(models.TransientModel):
    _name = 'smn.popup.message'
    _description = 'Popup Message'

    name = fields.Char()
