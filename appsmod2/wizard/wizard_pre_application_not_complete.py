# -*- coding: utf-8 -*-

from odoo import models, fields, _

class WizardPreApplicationNotComplete(models.TransientModel):
    _name = "wizard.pre.application.not.complete"
    _description = "Wizard Pre-Application Not Complete"

    message = fields.Text("Pre-Application Not Complete Reason")

    def pre_application_not_complete_save(self):
        application_id = self.env.context.get("active_id")
        application = self.env["application"].browse(application_id)
        message = self.message
        application.message_post(body=_(message))
        application.write({'state': "pre_application_not_complete"})
        application.with_context(self.env.context).load_checklist_items("pre_application_not_complete")