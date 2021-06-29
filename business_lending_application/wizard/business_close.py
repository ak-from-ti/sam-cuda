# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from logging import getLogger
_logger = getLogger(__name__)

CLOSE_REASONS = [
                   ('find_another','Find Another'),
                   ('not_interested','Warning'),
                   ('other','Other')
                ]


class BusinessApplicationClose(models.TransientModel):
    _name = 'business.application.close'
    _description = 'Business Application Close'

    bussiness_application_id = fields.Many2one('business.application',string='Business Application',help='Current Business Application')
    closing_reason = fields.Selection(CLOSE_REASONS,string='Closing Reason',default="find_another",required=True)
    reason_text = fields.Text('Closing Comment')

    def process(self):
        key_val_dict = dict(self._fields['closing_reason'].selection) 
    
        reason = self.closing_reason
        msg_body = _('Bussiness Application is closed.<br/>Reason --> %s', key_val_dict.get(reason,None))
        if self.reason_text:
            msg_body+= _('<br/>Comment : %s', self.reason_text)

        self.bussiness_application_id.message_post(body=msg_body)
        self.bussiness_application_id.write({
            'state': 'close',
        })
        return True
