# -*-coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

APPLICABILITY_SELECTION = [
    ('all_applicants', "For All Applicants Where Applicable"),
    ('all_applicants_individual', "For All Applicants Where Applicable Individually"),
    ('paye_employees', "For PAYE Employees"),
    ('self_employed', "For Self Employed"),
    ('mortgage', "If Mortgage is for Self-Build"),
    ('tenant_or_council', "If Purchasing Property Under Tenant Purchase Of Counsil Buyout")
]

STATE_SELECTION = [
    ('limits_eligible', "Limits Eligible"),
    ('limits_not_eligible', "Limits Not Eligible"),
    ('pre_application_complete', "Pre-Application Complete"),
    ('pre_application_not_complete', "Pre-Application Not Complete"),
    ('application_requested', "Application Requested"),
    ('application_pack_returned', "Application Pack Returned"),
    ('consent_signed', "Consent Signed"),
    ('application_form_received', "Application Form Received"),
    ('ready_for_assessment', "Ready For Assessment"),
    ('valuation_report', "Awaiting Valuation Report"),
    ('property_overvalued', "Property Overvalued"),
    ('submit', "Submit For Final Review")
]

class ApplicationChecklist(models.Model):
    _name = "application.checklist"
    _description = "Application Checklist"

    name = fields.Char("Name", help="Checklist name")
    active = fields.Boolean("Active", default=True)
    applicable_for_eu_citizen = fields.Boolean("Applicable for Non-EU Citizen")
    type = fields.Selection(APPLICABILITY_SELECTION, default="all_applicants", string="Type", help="Type this checklist is applicable to.")
    state = fields.Selection(STATE_SELECTION, string="State", help="Application state at which checklist to check.")
    sequence = fields.Integer("Sequence")

    _sql_constraints = [
        ('unique_name', "unique(name, type)", "The name of the checklist must be unique.")
    ]

    @api.model
    def create(self, vals):
        if vals.get("applicable_for_eu_citizen", False):
            if vals["type"] == "all_applicants":
                vals["applicable_for_eu_citizen"] = False
        return super(ApplicationChecklist, self).create(vals)

    def unlink(self):
        raise UserError('Checklist Items Cannot be Deleted. They Can be De-Activated In Case Not Required.')