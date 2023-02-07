# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _, SUPERUSER_ID


_logger = logging.getLogger(__name__)


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    code = fields.Char(required=True)
    display = fields.Boolean(default=False)
