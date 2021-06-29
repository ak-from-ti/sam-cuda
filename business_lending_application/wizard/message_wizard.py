# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from logging import getLogger
_logger = getLogger(__name__)



class MessageWizard(models.TransientModel):
    _name = 'business.message'
    _description = 'Business Messages'


    message = fields.Text('Message')

    def process(self):
        active_id = self.env.context.get('active_id',None)
        if active_id:
            business_application_id = self.env['business.application'].sudo().browse([int(active_id)])[0]
            _logger.critical(f"=========111111==========  {business_application_id}")
            business_application_id.write({
                'state':'approved',
            })
            return  True