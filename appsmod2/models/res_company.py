# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    lti = fields.Float("LTI", help="Loan to Income")
    ltv = fields.Float("LTV", help="Loan to Value")
    mortgage_service_ratio = fields.Float("Mortgage Service Ratio %", help="Mortgage Service Ratio %")
    debt_service_ratio = fields.Float("Total Debt Service Ratio %", help="Total Debt Service Ratio %")
    gift_to_deposit = fields.Float("Gift to Deposit %", help="Gift to Deposit Ratio")

    monthly_income_reduced = fields.Float("Monthly Income Reduced %", help="Monthly Income Reduced %")
    interest_rate_increase = fields.Float("Interest Rate Increase %", help="Interest Rate Increase %")
    stressed_mortgage_service_ratio = fields.Float("Stressed Mortgage Service Ratio", help="Stressed Mortgage Service Ratio")
    stressed_debt_service_ratio = fields.Float("Stressed Total Debt Service Ratio", help="Stressed Total Debt Service Ratio")

    interest_rate = fields.Float("Interest Rate", help="Interest Rate")

    # New Development in 2020 
    mortgage_product_ids = fields.One2many("mortgage.product", "company_id", "Mortgage Products")
    