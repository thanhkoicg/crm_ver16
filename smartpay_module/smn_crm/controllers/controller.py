import json
from odoo import http
from odoo.http import request
from odoo import api, SUPERUSER_ID


class PartnerApiController(http.Controller):

    @http.route('/loan/updatestatus', auth='none', csrf=False,  type='http', website=True)
    def api_kiman_update_stage(self):
        try:
            lead_id = False
            # make sure partner kiman alway exists
            partner_id = request.env['res.partner'].sudo().search([('code', '=', 'kiman')], limit=1)
            if request.httprequest.method != 'POST':
                messages = {
                    'status': 'failed',
                    'code': "ERR_REQUEST_DATA"
                }
                self.create_api_history(messages, 'api_kiman_update_stage', request.httprequest.method, partner_id, lead_id)
                return json.dumps(messages)
            status_text = request.params.get('statusText')
            contract_no = request.params.get('contractNo')
            reason = request.params.get('reason') if request.params.get('reason') else ''
            if status_text and contract_no:
                status_maping_id = request.env['crm.lead.status.mapping'].sudo().search([('code', '=', status_text)])
                if status_maping_id:
                    lead_id = request.env['crm.lead'].sudo().search([('contract_code', '=', contract_no)])
                    if lead_id:
                        lead_id.stage_id = status_maping_id.stage_id.id
                        lead_id.reason = reason
                        messages = {
                            'status': 'success',
                            'code': "OK",
                        }
                        self.create_api_history(messages, 'api_kiman_update_stage', "%s - %s" % (lead_id.stage_id.name, lead_id.reason), partner_id, lead_id)
                        return json.dumps(messages)
                    else:
                        messages = {
                            'status': 'error',
                            'code': "ERR_REQUEST_DATA",
                        }
                        self.create_api_history(messages, 'api_kiman_update_stage', "Not found lead: %s" % contract_no, partner_id,
                                                lead_id)
                        return json.dumps(messages)
                else:
                    messages = {
                        'status': 'error',
                        'code': "ERR_REQUEST_DATA",
                    }
                    self.create_api_history(messages, 'api_kiman_update_stage', "Not found status mapping: %s" % status_text, partner_id, lead_id)
                    return json.dumps(messages)
            else:
                messages = {
                    'status': 'error',
                    'code': "ERR_FORMAT",
                }
                self.create_api_history(messages, 'api_kiman_update_stage', "%s - %s" % (status_text, contract_no), partner_id, lead_id)
                return json.dumps(messages)
        except Exception as e:
            messages = {
                'status': 'error',
                'code': "ERR_SYSTEM",
            }
            self.create_api_history(messages, 'api_kiman_update_stage', str(e), False, False)
            return json.dumps(messages)

    def create_api_history(self, value, name, receive_data, partner_id, lead_id):
        lead = False
        lead_name = ''
        if lead_id:
            lead = lead_id.id
            lead_name = lead_id.name
        request.env['smn.api.history'].sudo().create({
            'name': name if name else '/',
            'link_action': '',
            'send_data': '',
            'receive_data': receive_data if receive_data else '',
            'status': value['status'],
            'note': '',
            'partner_id': partner_id.id if partner_id else '',
            'lead_info': "[ID: %s] %s" % (lead, lead_name),
        })
