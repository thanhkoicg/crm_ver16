# -*- coding: utf-8 -*-
{
    'name': 'SMN HR Management',
    'version': '1.1',
    'category': 'Smartnet Own Modules',
    'author': 'SMARTNET',
    'website': 'https://smartnetvn.com.vn/',
    'license': 'AGPL-3',
    'summary': 'CRM API Management',
    'description': """
This module allows you to manage API for Partner.
""",
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'hr_contract'
        'smn_crm'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'views/res_bank_view.xml',
        'views/hr_document_type_view.xml',
        'views/hr_applicant_view.xml',
        'views/hr_job_view.xml',
        'views/hr_recruitment_stage_view.xml',
        'views/hr_contract_type_view.xml',
        'views/hr_contract_view.xml',
        # 'wizard/smn_popup_message_view.xml',
        'views/menu.xml'
    ],
    'application': True,
}
