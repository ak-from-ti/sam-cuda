# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MortgageProduct(models.Model):
    _name = "mortgage.product"
    _description = "Mortgage Product"
    _inherit = ["mail.thread"]

    name = fields.Char("Name", required=True, tracking=True, copy=False)
    mortgage_type = fields.Selection([
        ('variable_rate', "Variable Rate Mortgage"),
        ('fixed_variable_rate', "Fixed Rate Into Variable Mortgage")
    ], string="Mortgage Type", required=True, default="variable_rate", tracking=True, copy=False)
    variable_interest_rate = fields.Float("Variable Interest Rate", tracking=True, copy=False)
    fixed_interest_rate = fields.Float("Fixed Interest Rate", tracking=True, copy=False, help="Base Interest Rate")
    fixed_term = fields.Integer("Fixed Term", tracking=True, copy=False, help="Duration of Fixed Term")
    company_id = fields.Many2one("res.company", "Company", required=True, index=True, default=lambda self: self.env.user.company_id, tracking=True, copy=False)
    active = fields.Boolean("Active", default=True)