# -*- coding: utf-8 -*-
{
    'name': 'SMN CRM API',
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
        'crm',
        'as_vn_address',
        'sale',
        'sales_team',
        'hr',
        'hr_contract',
        'hr_recruitment'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_groups.xml',
        # 'data/mail_template.xml',
        'data/ir_cron.xml',
        'views/res_groups_view.xml',
        'views/res_users_view.xml',
        # 'views/res_partner_view.xml',
        'views/crm_lead_view.xml',
        'views/crm_stage_view.xml',
        'views/crm_activity_history_view.xml',
        'views/crm_activity_result_view.xml',
        'views/mail_activity_type_view.xml',
        'views/mail_activity_type_line_view.xml',
        'views/smn_api_history_view.xml',
        'views/crm_marketing_campaign_view.xml',
        'views/sftp_config_view.xml',
        'wizard/smn_popup_message_view.xml',
        'wizard/lead_input_image_view.xml',
        'views/menu.xml'
    ],
    'application': True,
}
