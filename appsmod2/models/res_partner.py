# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    def _default_country(self):
        country = self.env["res.country"].search([('name', '=', "Ireland")], limit=1)
        return country

    first_name = fields.Char("First Name")
    last_name = fields.Char("Last Name")
    member_id = fields.Char("Member ID")
    # Used as DOB in v9
    DOB = fields.Date("Date of Birth")

    # Adds default country attribute
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_default_country)

    _sql_constraints = [
        ('member_unique', "unique(member_id, company_id)", "Member ID must be Unique per Company!")
    ]

    @api.model
    def create(self, vals):
        if not vals.get("name", False):
            first_name = vals.get("first_name", '')
            last_name = vals.get("last_name", '')
            vals["name"] = (first_name + " " + last_name).strip()

        return super(ResPartner, self).create(vals)

    def write(self, vals):
        if vals.get("first_name", False) or vals.get("last_name", False):
            first_name = vals.get("first_name", self.first_name)
            last_name = vals.get("last_name", self.last_name)
            vals["name"] = (first_name + " " + last_name).strip()
        return super(ResPartner, self).write(vals)
