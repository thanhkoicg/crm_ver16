# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import pysftp


class SftpConfig(models.Model):
    _name = "sftp.config"
    _description = "SFTP Config"
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(required=True)
    host = fields.Char(required=True, tracking=True)
    port = fields.Integer(required=True, tracking=True)
    sftp_user = fields.Char(required=True, tracking=True)
    sftp_password = fields.Char(required=True, tracking=True)
    root_folder = fields.Char(required=True,  tracking=True)
    is_encrypted_file = fields.Boolean()
    encryption_key = fields.Char()
    decryption_key = fields.Char()
    config_model_ids = fields.One2many('sftp.model','config_id', string='Models')
    active = fields.Boolean(default=True)

    def sftp_connection(self, test=True):
        conn = None
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        params = {
            'host': self.host.strip(),
            'username': self.sftp_user.strip(),
            'password': self.sftp_password,
            'port': self.port,
            'cnopts': cnopts
        }
        try:
            conn = pysftp.Connection(**params)
            if test:
                raise UserError('Connection Test Succeeded!')
        except (pysftp.CredentialException,
                pysftp.ConnectionException,
                pysftp.SSHException):
            if test:
                raise UserError('Connection Test Failed!')
        return conn


class SftpModel(models.Model):
    _name = "sftp.model"
    _description = "SFTP Model"
    _inherit = ['mail.thread']
    _order = "id desc"

    model_id = fields.Many2one('ir.model')
    child_folder = fields.Char()
    config_id = fields.Many2one('sftp.config', ondelete='cascade')

