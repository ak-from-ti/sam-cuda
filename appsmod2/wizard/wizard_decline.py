# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)

DECLINATION_REASON = [
    ('reason_1', "Member Does not Attend Meeting -> Not Interested in Proceeding"),
    ('reason_2', "Metrics Outside Risk Tolerance in Affordability Calculator"),
    ('reason_3', "Character"),
    ('reason_4', "Secure Employment"),
    ('reason_5', "Affordability"),
    ('reason_6', "Property Overvalued -> Member Unable to Bridge Gap"),
    ('reason_7', "Member Did not Proceed")
]

class WizardDecline(models.TransientModel):
    _name = "wizard.decline"

    reason = fields.Selection(DECLINATION_REASON, default="reason_1")
    message = fields.Text("Add The Declination Reason")

    def decline_save(self):
        self.ensure_one()
        active_id = self.env.context.get("active_id")
        application = self.env['application'].browse(active_id)
        REASONS = dict(DECLINATION_REASON)
        decline_message = f"Declination Reason <br/> - {REASONS[self.reason]} <br/> - {self.message}"
        application.message_post(body=_(decline_message))
        application.sudo().write({'state': 'decline', 'decline_message': self.message, 'decline_reason': REASONS[self.reason]})