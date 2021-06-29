# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class WizardLimitsNotEligible(models.Model):
    _name = "wizard.limits.not.eligible"
    _description = "Wizard Limits Not Eligible"

    message = fields.Text("Non-Eligibility Reason")

    def limits_not_eligible_save(self):
        application_id = self.env.context.get("active_id")
        if application_id:
            application = self.env["application"].browse(application_id)
            message = self.message
            application.message_post(body=message)
            application.write({'state': "limits_not_eligible"})
            application.with_context(self.env.context).load_checklist_items("limits_not_eligible")