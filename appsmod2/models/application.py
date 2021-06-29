# -*-coding: utf-8 -*-

import base64
import logging
import numpy as np
import numpy_financial as npf

from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource

ADDRESS_FORMAT_CLASSES = {
    '%(city)s %(state_code)s\n%(zip)s': 'o_city_state',
    '%(zip)s %(city)s': 'o_zip_city'
}

STANDARD_GIFT_TO_DEPOSIT = 50.0

STANDARD_MORTGAGE_SERVICE_RATIO = 50.0

STANDARD_TOTAL_DEBT_SERVICE_RATIO = 50.0

STANDARD_STRESSED_MORTGAGE_SERVICE_RATIO = 40.0

_logger = logging.getLogger(__name__)

#TODO: Check this classs
class format_address(object):
    @api.model
    def fields_view_get_address(self, arch):
        address_format = self.env.user.company_id.country_id.address_format or ''
        for format_pattern, format_class in ADDRESS_FORMAT_CLASSES.items():
            if format_pattern in address_format:
                doc = etree.fromstring(arch)
                for address_node in doc.xpath("//div[@class='o_address_format']"):
                    # add address format class to address block
                    address_node.attrib['class'] += ' ' + format_class
                    if format_class.startswith('o_zip'):
                        zip_fields = address_node.xpath("//field[@name='zip']")
                        city_fields = address_node.xpath("//field[@name='city']")
                        if zip_fields and city_fields:
                            # move zip field before city field
                            city_fields[0].addprevious(zip_fields[0])
                arch = etree.tostring(doc)
                break
        return arch


class Application(models.Model):
    _name = "application"
    _description = "Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    STATE_SELECTION = [
        ('draft', "Draft"),
        ('limits_eligible', "Limits Eligible"),
        ('limits_not_eligible', "Limits Not Eligible"),
        ('pre_application_complete', "Pre-Application Complete"),
        ('pre_application_not_complete', "Pre-Application Not Complete"),
        ('application_requested', "Application Requested"),
        ('application_pack_returned', "Application Pack Returned"),
        ('consent_signed', "Consent Signed"),
        ('application_form_received', "Application Form Received"),
        ('external_assessor', "External Assessor"),
        ('ready_for_assessment', "Ready For Assessment"),
        ('valuation_report', "Awaiting Valuation Report"),
        ('property_overvalued', "Property Overvalued"),
        ('submit', "Submit For Final Review"),
        ('accepted', "Accepted"),
        ('funds_drawn_down', "Funds Drawn Down"),
        ('decline', "Declined")
    ]

    YES_NO = [
        ('yes', "Yes"),
        ('no', "No")
    ]

    PAYMENT_FREQUENCY = [
        ('weekly', "Weekly"),
        ('fortnightly', "Fortnightly"),
        ('monthly', "Monthly")
    ]

    SINGLE = [
        ('1300', "1300"),
        ('2050', "2050")
    ]

    PURPOSE_OF_MORTGAGE = [
        ('moving', "Moving Home"),
        ('building', "Building"),
        ('switching', "Switching Mortgage Provider"),
        ('topup', "Top Up"),
        ('buy_first_home', "Buy First Home")
    ]

    MONTH_SELECTION = [
        ('0', "0"),
        ('1', "1"),
        ('2', "2"),
        ('3', "3"),
        ('4', "4"),
        ('5', "5"),
        ('6', "6"),
        ('7', "7"),
        ('8', "8"),
        ('9', "9"),
        ('10', "10"),
        ('11', "11"),
        ('12', "12")
    ]

    def _default_company_id(self):
        # return self.env["res.company"]._compute_default_get("application")
        return self.env.user.company_id

    def _default_interest_rate_increase(self):
        company_id = self.env.user.company_id
        return float(company_id.interest_rate_increase)

    def _default_country_id(self):
        country = self.env["res.country"].search([('name', '=', "Ireland")], limit=1)
        return country.id

    def _default_red_image(self):
        img_path = get_module_resource("appsmod2", "static/img", "red.png")
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read())


    def _default_green_image(self):
        img_path = get_module_resource("appsmod2", "static/img", "green.png")
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read())

        
    

    name = fields.Char("Application Reference", readonly=True, tracking=True, copy=False, default=lambda self: _('New'))
    state = fields.Selection(STATE_SELECTION, "Status", tracking=True, readonly=True, default="draft", copy=False, select=True)
    original_assignee = fields.Many2one("res.users", "Indicator - Original Assignee", default=lambda self: self.env.user, copy=False)
    officer_category_id = fields.Integer("Indicator - External Assessor ID", compute="_compute_officer_category_id")
    senior_officer_category_id = fields.Integer("Indicator - Senior Officer Category ID", compute="_compute_senior_officer_category_id")
    field_mry_tab_check = fields.Boolean("Indicator - MRY Tab Visibility", compute="_compute_mry_tab_visibility") 
    field_paye_check = fields.Boolean("Indicator - PAYE Visibility", compute="_compute_pay_visibility")
    field_self_check = fields.Boolean("Indicator - Self Visibility", compute="_compute_self_visibility")

    # Column2
    assignee = fields.Many2one("res.users", "Assignee", copy=False, default=lambda self: self.env.user, tracking=True)
    external_assessor_user = fields.Many2one("res.users", "Indicator - External Assessor", copy=False)
    company_id = fields.Many2one("res.company", "Company", tracking=True, default=_default_company_id)
    
    # New code 2020
    mortgage_product_id = fields.Many2one("mortgage.product", "Mortgage Product", required=True, ondelete="restrict")
    mortgage_type = fields.Selection([
        ('variable_rate', "Variable Rate Mortgage"),
        ('fixed_variable_rate', "Fixed Rate Into Variable Mortgage")
    ], related="mortgage_product_id.mortgage_type", string="Mortgage Type", store=True)

    mortgrage_term_months = fields.Selection(MONTH_SELECTION, string="Mortgage Term Months", default='0', tracking=True, copy=False)
    mortgrage_term_year = fields.Integer("Mortgage Term Years", tracking=True, copy=False)
    monthly_repayment = fields.Float("Monthly Repayment", digits=(16, 2),compute="_compute_repayment", store=True, copy=False, tracking=True)

    loan_to_value = fields.Float("Loan To Value %",compute="_compute_loan_to_value", store=True, tracking=True, copy=False)
    loan_to_income_ratio = fields.Float("Loan To Income Ratio",compute="_compute_loan_to_income_ratio", store=True, tracking=True, copy=False)
    mortgage_service_ratio = fields.Float("Mortgage Service Ratio %", compute="_compute_service_ratio", store=True, tracking=True, copy=False)
    total_debt_service_ratio = fields.Float("Total Debt Service Ratio %", compute="_compute_service_ratio", store=True, tracking=True, copy=False)

    net_disposable_inc = fields.Float("Net Disposable Income", compute="_compute_service_ratio", store=True, tracking=True, copy=False, help="Net Disposable Income")
    gift_to_deposit = fields.Float("Gift to Deposit %",compute="_compute_gift_to_deposit", store=True, tracking=True, copy=False, help="What percentage of deposit can come from Gift.")
    max_lend_facility = fields.Float("Max Lend Facility",compute="_compute_loan_to_income_ratio", store=True, tracking=True, copy=False, help="Maximum amount that can be lended based on given information.")

    # For Stress Test
    monthly_income_reduced = fields.Float("Monthly Income Reduced %",compute="_compute_monthly_income_reduced",store=True, tracking=True, copy=False, help="Monthly Income Reduced % (For Stress Test)")
    interest_rate_increase = fields.Float("Interest Rate Increase %", tracking=True, copy=False, default=_default_interest_rate_increase)
    stressed_income = fields.Float("Stressed Income",compute="_compute_stressed_income", store=True, tracking=True, copy=False)
    stressed_allowable_income = fields.Float("Stressed Allowable Income",compute="_compute_stressed_allowable_income", store=True, tracking=True, copy=False, help="Stressed Allowable Monthly Income")
    stressed_monthly_repayment = fields.Float("Stressed Monthly Repayment", compute="_compute_stressed_monthly_repayment", store=True, tracking=True, copy=False)
    stressed_mortgage_service_ratio = fields.Float("Stressed Mortgage Service Ratio", compute="_compute_stressed_service_ratio", store=True, tracking=True, copy=False)
    stressed_total_debt_service_ratio = fields.Float("Stressed Total Debt Service Ratio", compute="_compute_stressed_service_ratio", store=True, tracking=True, copy=False, help="Total Debt Service Ratio for Stress Test")
    stressed_net_disposable_income = fields.Float("Stressed Net Disposable Income", compute="_compute_stressed_service_ratio", store=True, tracking=True, copy=False)

    # Address fields
    street = fields.Char("Street", copy=False)
    street2 = fields.Char("Street2", copy=False)
    zip = fields.Char("EIRCODE", size=24, change_default=True, copy=False)
    city = fields.Char("City", copy=False)
    state_id = fields.Many2one("res.country.state", "County", ondelete="restrict")
    country_id = fields.Many2one("res.country", "Country", ondelete="restrict", default=_default_country_id)

    purpose_of_mortgage = fields.Selection(PURPOSE_OF_MORTGAGE, "Purpose Of Mortgage", default='moving', tracking=True)

    # ESIS fields
    esis_payment_frequency = fields.Selection(PAYMENT_FREQUENCY, "Payment Frequency", default="monthly", tracking=True)
    esis_weekly_repayment = fields.Float("Weekly Repayment", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_fortnightly_repayment = fields.Float("Fortnightly Repayment", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_no_of_repayment = fields.Integer("No. Of Repayments", compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_total_repaid = fields.Float("Total Repaid", digits=(16, 2), compute="_compute_total_repaid", store=True, tracking=True, copy=False)
    esis_cost_of_credit = fields.Float("Cost of Credit", digits=(16, 2), compute="_compute_total_repaid", store=True, tracking=True, copy=False)
    esis_cost_per_1 = fields.Float("Cost per €1", digits=(16, 2), compute="_compute_total_repaid", store=True, tracking=True, copy=False)
    esis_interest_rate = fields.Float("Interest Rate + 1%", compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_monthly_repayment_1 = fields.Float("Monthly Repayment + 1%", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_fortnightly_repayment_1 = fields.Float("Fortnightly Repayment + 1%", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_weekly_repayment_1 = fields.Float("Weekly Repayment + 1%", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False, help="Fortnightly Weekly + 1%")
    esis_monthly_repayment_2 = fields.Float("Monthly Repayment + 2%", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_fortnightly_repayment_2 = fields.Float("Fortnightly Repayment + 2%", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False)
    esis_weekly_repayment_2 = fields.Float("Weekly Repayment + 2%", digits=(16, 2), compute="_compute_repayment", store=True, tracking=True, copy=False, help="Fortnightly Weekly + 2%")
    esis_aprc = fields.Float("APRC", compute="_compute_aprc", store=True, tracking=True, copy=False, help="Annual Percentage Rate of Charge")
    esis_aprc_1 = fields.Float("APRC + 1%", compute="_compute_aprc", store=True, tracking=True, copy=False, help="Annual Percentage Rate of Charge + 1%")

    # Column 1
    first_time_buyer = fields.Selection(YES_NO, string="First Time Buyer", default="yes", tracking=True, copy=False)
    first_time_buyer_value = fields.Float("First Time Value", default=90.0, copy=False)
    single = fields.Selection(SINGLE, "Single/Couple", default="1300", copy=False, tracking=True)
    applicant_1 = fields.Many2one("res.partner", "Applicant 1", tracking=True, copy=False)
    applicant_1_age = fields.Char("Applicant 1 Age", compute="_compute_applicant_1_age", store=True, tracking=True, copy=False)
    applicant_1_age_end_of_term = fields.Char("Applicant 1 Age: End of Term", compute="_compute_applicant_age_end_of_term", store=True, tracking=True, copy=False)
    no_of_dependents = fields.Integer("No of Dependents", tracking=True, copy=False)
    ndi_monthly = fields.Float("Required NDI Monthly", compute="_compute_ndi_monthly", store=True, tracking=True, copy=False)
    property_value = fields.Float("Property Value", digits=(16, 2), tracking=True, copy=False)
    mortgage_amount = fields.Float("Mortgage Amount", digits=(16, 2), tracking=True, copy=False)
    interest_rate = fields.Float("Interest Rate", digits=(16, 2), compute="_compute_on_mortgage_product", store=True, tracking=True, copy=False)
    total_basic_income_1 = fields.Float("Applicant 1 Total Basic Income", tracking=True, copy=False)
    total_net_basic_income_1 = fields.Float("Applicant 1 Total Net Basic Income", tracking=True, copy=False)
    total_other_income_1 = fields.Float("Applicant 1 Total Other Net Income", tracking=True, copy=False)
    total_income = fields.Float("Total Net Income", compute="_compute_income", store=True, tracking=True, copy=False)
    self_employed_1 = fields.Selection(YES_NO, "Applicant 1 Self Employed?", default="no", tracking=True, copy=False)
    other_income_counted = fields.Float("% Of Other Income Counted", default=100, tracking=True, copy=False)
    nd2_income_counted = fields.Float("% Of 2nd Income Counted", default=100, tracking=True, copy=False)

    total_sustainable_income = fields.Float("Total Sustainable Income",compute="_compute_income", store=True, tracking=True, copy=False)
    allowable_monthly_income = fields.Float("Allowable Monthly Income",compute="_compute_income", store=True, tracking=True, copy=False)

    applicant_1_p60 = fields.Float("Applicant 1 P60 Income For Last Year", tracking=True, copy=False, help="P60 Income For Last Year")
    applicant_1_ann_pen = fields.Float("Applicant 1 Annual Pension Contribution", tracking=True, copy=False)
    applicant_1_exi_mor = fields.Float("Applicant 1 Existing Mortgage Commitments", tracking=True, copy=False)
    applicant_1_rental_income = fields.Float("Applicant 1 Rental Income", tracking=True, copy=False)
    debt_repay = fields.Float("Monthly Debt Repayments", tracking=True, copy=False)
    property_co = fields.Float("Future Property Costs", tracking=True, copy=False)
    maintenance = fields.Float("Maintenance", tracking=True, copy=False)
    childcare = fields.Float("Monthly Childcare Costs", tracking=True, copy=False)
    total_short_term = fields.Float("Total Short Term Debt",compute="_compute_total_short_term", store=True, tracking=True, copy=False)

    gifts_towards_deposit = fields.Selection(YES_NO, "Gifts Towards Deposit", tracking=True, default="no", copy=False)
    values_of_gifts = fields.Float("Values of Gifts", tracking=True, copy=False)
    gifts_letter_received = fields.Selection(YES_NO, "Gift Letter Received", default="yes", tracking=True, copy=False)
    contribution_to_valuation = fields.Float("Contribution to Valuation", tracking=True, copy=False)
    contribution_to_revaluation = fields.Float("Contribution to Revaluation", tracking=True, copy=False)
    once_off_costs = fields.Float("Other Once Off Costs", tracking=True, copy=False)
    applicant_1_eu_citizen = fields.Selection(YES_NO, "Applicant 1 EU Citizen", default="yes", copy=False)
    applicant_1_credit_risk = fields.Selection(YES_NO, "Applicant 1 Are Credit Checks Acceptable?", default="yes", tracking=True, copy=False, help="Is Credit Risk Acceptable?")
    
    # Column 3
    date_of_offer = fields.Date("Date of Offer")
    date_of_offer_plus_1 = fields.Date("Date of Offer + 1", help="Date of Offer")
    date_of_offer_plus_2 = fields.Date("Date of Offer + 2", help="Date Of Offer")

    applicant_2 = fields.Many2one("res.partner", "Applicant 2", tracking=True, copy=False)
    applicant_2_age = fields.Char("Applicant 2 Age", compute="_compute_applicant_2_age", store=True, tracking=True, copy=False)
    applicant_2_age_end_of_term = fields.Char("Applicant 2 Age: End of Term", compute="_compute_applicant_age_end_of_term", store=True, tracking=True, copy=False)
    total_basic_income_2 = fields.Float("Applicant 2 Total Basic Income", tracking=True, copy=False, help="Total Basic Income of Applicant 2")
    total_net_basic_income_2 = fields.Float("Applicant 2 Total Net Basic Income", tracking=True, copy=False)
    total_other_income_2 = fields.Float("Applicant 2 Total Other Net Income", tracking=True, copy=False)
    self_employed_2 = fields.Selection(YES_NO, default="no", string="Applicant 2 Self Employed?", tracking=True, copy=False)
    applicant_2_p60 = fields.Float("Applicant 2 P60 Income For Last Year", tracking=True, copy=False, help="P60 Income For Last Year")
    applicant_2_ann_pen = fields.Float("Applicant 2 Annual Pension Contribution", tracking=True, copy=False)
    applicant_2_exi_mor = fields.Float("Applicant 2 Existing Mortgage Commitments", tracking=True, copy=False)
    applicant_2_rental_income = fields.Float("Applicant 2 Rental Income", tracking=True, copy=False)
    applicant_2_eu_citizen = fields.Selection(YES_NO, default="yes", string="Applicant 2 EU Citizen", tracking=True, copy=False)
    applicant_2_credit_risk = fields.Selection(YES_NO, default="yes", string="Applicant 2 Are Credit Checks Acceptable?", help="Is Credit Risk Acceptable?")

    # Duration of fixed rate term as per product
    term_at_starting_rate = fields.Integer("Term At Starting Rate",compute="_compute_on_mortgage_product", store=True, tracking=True, copy=False)
    fixed_interest_rate = fields.Float("Fixed Interest Rate", compute="_compute_on_mortgage_product", store=True, tracking=True, copy=False)
    fixed_term_payment = fields.Float("Fixed Term Payment",compute="_compute_term_repayment", store=True, tracking=True, copy=False)
    repayment_at_variable = fields.Float("Repayment at Variable",compute="_compute_term_repayment", store=True, tracking=True, copy=False)
    repayment_at_variable_plus1 = fields.Float("Repayment at Variable + 1%", compute="_compute_term_repayment", store=True, tracking=True, copy=False)
    repayment_at_variable_plus2 = fields.Float("Repayment at Variable + 2%", compute="_compute_term_repayment", store=True, tracking=True, copy=False)
    max_possible_repayment = fields.Float("Max Possible Repayment", compute="_compute_term_repayment", store=True, tracking=True, copy=False)
    avg_repayment = fields.Float("Average Repayment", compute="_compute_total_repaid", store=True, tracking=True, copy=False)
    avg_rate = fields.Float("Average Rate", compute="_compute_total_repaid", store=True, tracking=True, copy=False)
    avg_repayment_plus1 = fields.Float("Average Repayment + 1%", compute="_compute_total_repaid", store=True, tracking=True, copy=False)
    is_old_application = fields.Boolean("Old Application", copy=False)

    # Assessment 
    character_demonstrated = fields.Selection(YES_NO, default='no', string="Applicant 1 Is Character Demonstrated?", tracking=True, copy=False, help="- ICB in order\n- All Financial Commitments met\n- Explanation for all DDs and SOs\n- No erratic pattern in statements\n- No unusual movements in accounts")
    affordability_established = fields.Selection(YES_NO, default="no", string="Applicant 1 Is Affordability Established?", tracking=True, copy=False, help="- Income and Expenditure an in application\n- Assessed Finances within policy limits\n- Impending change in circumstances ( eg. child care costs?)")
    secure_employement = fields.Selection(YES_NO, default="no", string="Applicant 1 Secure Employment?", tracking=True, copy=False, help="- Permanency of Employment\n- Low risk sector or skills transferable to another sector\n- Established Employer")
    certified_value = fields.Selection(YES_NO, default="no", string="Do you have a certified value of property?", tracking=True, copy=False)
    certified_property_value = fields.Float("What is the certified value of property?", digits=(16, 2), tracking=True, copy=False)

    character_demonstrated_applicant_2 = fields.Selection(YES_NO, default='no', string="Applicant 2 Is Character Demonstrated?", tracking=True, copy=False, help="- ICB in order\n- All Financial Commitments met\n- Explanation for all DDs and SOs\n- No erratic pattern in statements\n- No unusual movements in accounts")
    affordability_established_applicant_2 = fields.Selection(YES_NO, default="no", string="Applicant 2 Is Affordability Established?", tracking=True, copy=False, help="- Income and Expenditure an in application\n- Assessed Finances within policy limits\n- Impending change in circumstances ( eg. child care costs?)")
    secure_employement_applicant_2 = fields.Selection(YES_NO, default="no", string="Applicant 2 Secure Employment?", tracking=True, copy=False, help="- Permanency of Employment\n- Low risk sector or skills transferable to another sector\n- Established Employer")

    # Decline Letter Text 
    decline_message = fields.Text("Declination Message", copy=False)
    decline_reason = fields.Char("Decline Reason", copy=False)

    # Cover Note Tab 
    body_html = fields.Text("Cover Note", copy=False)

    # Special Conditions Tab 
    body_special_conditions = fields.Text("Special Conditions", copy=False)

    # Documents Tab 
    documents_uniquely_applicable_line = fields.One2many("documents.uniquely.applicable", "application_id", "Documents Uniquely Applicable")
    documents_applicable_applicant1_line = fields.One2many("documents.applicable.applicant1", "application_id", "Applicant 1 Documents")
    documents_applicable_applicant2_line = fields.One2many("documents.applicable.applicant2", "application_id", "Applicant 2 Documents")


    # Checklist Tab 
    jointly_applicable_line = fields.One2many("jointly.applicable", "application_id", "Jointly Applicable")
    checklist_applicable_applicant1_line = fields.One2many("checklist.applicable.applicant1", "application_id", "Applicant 1 Checklist")
    checklist_applicable_applicant2_line = fields.One2many("checklist.applicable.applicant2", "application_id", "Applicant 2 Checklist")
    checklist_self_applicable_applicant1_line = fields.One2many("checklist.self.applicable.applicant1", "application_id", "Applicant 1 Checklist Self")
    checklist_self_applicable_applicant2_line = fields.One2many("checklist.self.applicable.applicant2", "application_id", "Applicant 2 Checklist Self")
    checklist_paye_applicable_applicant1_line = fields.One2many("checklist.paye.applicable.applicant1", "application_id", "Applicant 1 Checklist Paye")
    checklist_paye_applicable_applicant2_line = fields.One2many("checklist.paye.applicable.applicant2", "application_id", "Applicant 2 Checklist Paye")

    # MRY Tab 
    applicant_1_net_profit_1 = fields.Float("Applicant 1 Net Profit - MRY", tracking=True, copy=False, help="Net Profit")
    applicant_1_net_profit_2 = fields.Float("Applicant 1 Net Profit - MRY 1", tracking=True, copy=False, help="Net Profit")
    applicant_1_net_profit_3 = fields.Float("Applicant 1 Net Profit - MRY 2", tracking=True, copy=False, help="Net Profit")

    applicant_1_plus_depreceation_1 = fields.Float("Applicant 1 Plus Depreciation - MRY", tracking=True, copy=False, help="Plus Depreciation")
    applicant_1_plus_depreceation_2 = fields.Float("Applicant 1 Plus Depreciation - MRY 1", tracking=True, copy=False, help="Plus Depreciation")
    applicant_1_plus_depreceation_3 = fields.Float("Applicant 1 Plus Depreciation - MRY 2", tracking=True, copy=False, help="Plus Depreciation")

    applicant_1_plus_interest_paid_1 = fields.Float("Applicant 1 Plus Interest Paid - MRY", tracking=True, copy=False, help="Plus Interest Paid")
    applicant_1_plus_interest_paid_2 = fields.Float("Applicant 1 Plus Interest Paid - MRY 1", tracking=True, copy=False, help="Plus Interest Paid")
    applicant_1_plus_interest_paid_3 = fields.Float("Applicant 1 Plus Interest Paid - MRY 2", tracking=True, copy=False, help="Plus Interest Paid")

    applicant_1_plus_remuneration_1 = fields.Float("Applicant 1 Plus Remuneration - MRY", tracking=True, copy=False, help="Plus Renumeration")
    applicant_1_plus_remuneration_2 = fields.Float("Applicant 1 Plus Remuneration - MRY 1", tracking=True, copy=False, help="Plus Renumeration")
    applicant_1_plus_remuneration_3 = fields.Float("Applicant 1 Plus Remuneration - MRY 2", tracking=True, copy=False, help="Plus Renumeration")

    applicant_1_plus_pension_1 = fields.Float("Applicant 1 Plus Pension - MRY", tracking=True, copy=False, help="Plus Pension")
    applicant_1_plus_pension_2 = fields.Float("Applicant 1 Plus Pension - MRY 1", tracking=True, copy=False, help="Plus Pension")
    applicant_1_plus_pension_3 = fields.Float("Applicant 1 Plus Pension - MRY 2", tracking=True, copy=False, help="Plus Pension")

    applicant_1_trading_profit_1 = fields.Float("Applicant 1 Trading Profit - MRY", compute="_compute_mry", store=True, tracking=True, copy=False, help="Trading Profit")
    applicant_1_trading_profit_2 = fields.Float("Applicant 1 Trading Profit - MRY 2", compute="_compute_mry_1", store=True, tracking=True, copy=False, help="Trading Profit")
    applicant_1_trading_profit_3 = fields.Float("Applicant 1 Trading Profit - MRY 3", compute="_compute_mry_2", store=True, tracking=True, copy=False, help="Trading Profit")

    applicant_1_average_trading_profit = fields.Float("Applicant 1 Average Trading Profit", compute="_compute_avg_trading_profit_1", store=True, tracking=True, copy=False, help="Average Trading Profit")
    applicant_1_less_business_repayments = fields.Float("Applicant 1 Less Business Repayments", tracking=True, copy=False, help="Less Business Repayments")
    applicant_1_surplus = fields.Float("Applicant 1 Surplus", compute="_compute_surplus_1", store=True, tracking=True, copy=False, help="Surplus")

    applicant_1_notice_1 = fields.Float("Applicant 1 Notice of Assessment - MRY", tracking=True, copy=False, help="Notice of Assessment")
    applicant_1_notice_2 = fields.Float("Applicant 1 Notice of Assessment - MRY 1", tracking=True, copy=False, help="Notice of Assessment")
    applicant_1_notice_3 = fields.Float("Applicant 1 Notice of Assessment - MRY 3", tracking=True, copy=False, help="Notice of Assessment")

    applicant_2_net_profit_1 = fields.Float("Applicant 2 Net Profit - MRY", tracking=True, copy=False, help="Net Profit")
    applicant_2_net_profit_2 = fields.Float("Applicant 2 Net Profit - MRY 1", tracking=True, copy=False, help="Net Profit")
    applicant_2_net_profit_3 = fields.Float("Applicant 2 Net Profit - MRY 2", tracking=True, copy=False, help="Net Profit")

    applicant_2_plus_depreceation_1 = fields.Float("Applicant 2 Plus Depreciation - MRY", tracking=True, copy=False, help="Plus Depreciation")
    applicant_2_plus_depreceation_2 = fields.Float("Applicant 2 Plus Depreciation - MRY 1", tracking=True, copy=False, help="Plus Depreciation")
    applicant_2_plus_depreceation_3 = fields.Float("Applicant 2 Plus Depreciation - MRY 2", tracking=True, copy=False, help="Plus Depreciation")

    applicant_2_plus_interest_paid_1 = fields.Float("Applicant 2 Plus Interest Paid - MRY", tracking=True, copy=False, help="Plus Interest Paid")
    applicant_2_plus_interest_paid_2 = fields.Float("Applicant 2 Plus Interest Paid - MRY 1", tracking=True, copy=False, help="Plus Interest Paid")
    applicant_2_plus_interest_paid_3 = fields.Float("Applicant 2 Plus Interest Paid - MRY 2", tracking=True, copy=False, help="Plus Interest Paid")

    applicant_2_plus_remuneration_1 = fields.Float("Applicant 2 Plus Remuneration - MRY", tracking=True, copy=False, help="Plus Renumeration")
    applicant_2_plus_remuneration_2 = fields.Float("Applicant 2 Plus Remuneration - MRY 1", tracking=True, copy=False, help="Plus Renumeration")
    applicant_2_plus_remuneration_3 = fields.Float("Applicant 2 Plus Remuneration - MRY 2", tracking=True, copy=False, help="Plus Renumeration")

    applicant_2_plus_pension_1 = fields.Float("Applicant 2 Plus Pension - MRY", tracking=True, copy=False, help="Plus Pension")
    applicant_2_plus_pension_2 = fields.Float("Applicant 2 Plus Pension - MRY 1", tracking=True, copy=False, help="Plus Pension")
    applicant_2_plus_pension_3 = fields.Float("Applicant 2 Plus Pension - MRY 2", tracking=True, copy=False, help="Plus Pension")

    applicant_2_trading_profit_1 = fields.Float("Applicant 2 Trading Profit - MRY", compute="_compute_mry2", store=True, tracking=True, copy=False, help="Trading Profit")
    applicant_2_trading_profit_2 = fields.Float("Applicant 2 Trading Profit - MRY 2", compute="_compute_mry2_1", store=True, tracking=True, copy=False, help="Trading Profit")
    applicant_2_trading_profit_3 = fields.Float("Applicant 2 Trading Profit - MRY 3", compute="_compute_mry2_2", store=True, tracking=True, copy=False, help="Trading Profit")

    applicant_2_average_trading_profit = fields.Float("Applicant 2 Average Trading Profit", compute="_compute_avg_trading_profit_2", store=True, tracking=True, copy=False, help="Average Trading Profit")
    applicant_2_less_business_repayments = fields.Float("Applicant 2 Less Business Repayments", tracking=True, copy=False, help="Less Business Repayments")
    applicant_2_surplus = fields.Float("Applicant 2 Surplus", compute="_compute_surplus_2", store=True, tracking=True, copy=False, help="Surplus")

    applicant_2_notice_1 = fields.Float("Applicant 2 Notice of Assessment - MRY", tracking=True, copy=False, help="Notice of Assessment")
    applicant_2_notice_2 = fields.Float("Applicant 2 Notice of Assessment - MRY 1", tracking=True, copy=False, help="Notice of Assessment")
    applicant_2_notice_3 = fields.Float("Applicant 2 Notice of Assessment - MRY 3", tracking=True, copy=False, help="Notice of Assessment")


    # Indicators to show tabs
    hide_load_checklist = fields.Boolean("Indicator - Hide Checklist", copy=False)
    show_checklist = fields.Boolean("Indicator - Show Checklist", copy=False)
    show_cover_note = fields.Boolean("Indicator - Show Cover Note", copy=False)
    show_special = fields.Boolean("Indicator - Show Speical Conditions", copy=False)
    show_assessment = fields.Boolean("Indicator - Show Assessment", copy=False)

    image_red_1 = fields.Binary("Red Image 1", default=_default_red_image)
    image_red_2 = fields.Binary("Red Image 2", default=_default_red_image)
    image_red_3 = fields.Binary("Red Image 3", default=_default_red_image)
    image_red_4 = fields.Binary("Red Image 4", default=_default_red_image)
    image_red_5 = fields.Binary("Red Image 5", default=_default_red_image)
    image_red_8 = fields.Binary("Red Image 8", default=_default_red_image)
    image_red_9 = fields.Binary("Red Image 9", default=_default_red_image)

    image_green_1 = fields.Binary("Green Image 1", default=_default_green_image)
    image_green_2 = fields.Binary("Green Image 2", default=_default_green_image)
    image_green_3 = fields.Binary("Green Image 3", default=_default_green_image)
    image_green_4 = fields.Binary("Green Image 4", default=_default_green_image)
    image_green_5 = fields.Binary("Green Image 5", default=_default_green_image)
    image_green_8 = fields.Binary("Green Image 8", default=_default_green_image)
    image_green_9 = fields.Binary("Green Image 9", default=_default_green_image)

    show_image_1 = fields.Boolean("Image Visibility 1", copy=False)
    show_image_2 = fields.Boolean("Image Visibility 2", copy=False)
    show_image_3 = fields.Boolean("Image Visibility 3", copy=False)
    show_image_4 = fields.Boolean("Image Visibility 4", copy=False)
    show_image_5 = fields.Boolean("Image Visibility 5", copy=False)
    show_image_8 = fields.Boolean("Image Visibility 8", copy=False)
    show_image_9 = fields.Boolean("Image Visibility 9", copy=False)


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env["ir.sequence"].with_company(vals.get("company_id")).next_by_code("application.number") or _("New")

        return super(Application, self).create(vals)

    def _compute_officer_category_id(self):
        for application in self:
            application.officer_category_id = self.env.ref("appsmod2.group_appsmod2_external_user").id

    def _compute_senior_officer_category_id(self):
        for application in self:
            application.senior_officer_category_id = self.env.ref("appsmod2.group_appsmod2_loan_officer").id

    @api.depends("self_employed_1", "self_employed_2")
    def _compute_mry_tab_visibility(self):
        for application in self:
            if application.self_employed_1 and application.self_employed_2:
                if application.self_employed_1 == 'no' and application.self_employed_2 == 'no':
                    application.field_mry_tab_check = False
                else:
                    application.field_mry_tab_check = True
            else:
                if application.self_employed_1 and application.self_employed_1 == 'no':
                    application.field_mry_tab_check = False
                else:
                    application.field_mry_tab_check = True

    @api.depends("self_employed_1", "self_employed_2")
    def _compute_pay_visibility(self):
        for application in self:
            application.field_paye_check = not application.field_mry_tab_check

    @api.depends("self_employed_1", "self_employed_2")
    def _compute_self_visibility(self):
        for application in self:
            application.field_self_check = application.field_mry_tab_check

    @api.depends("applicant_1")
    def _compute_applicant_1_age(self):
        for application in self:
            if application.applicant_1:
                if application.applicant_1.DOB:
                    application.applicant_1_age = self._calculate_age(application.applicant_1.DOB)
                else:
                    raise UserError(_("Please maintain Date Of Birth for Applicant."))

    @api.depends("applicant_2")
    def _compute_applicant_2_age(self):
        for application in self:
            if application.applicant_2:
                if application.applicant_2.DOB:
                    application.applicant_2_age = self._calculate_age(application.applicant_2.DOB)
                else:
                    raise UserError(_("Please maintain Date of Birth for Applicant 2."))

    @api.depends("applicant_1_age", "applicant_2_age", "mortgrage_term_year", "mortgrage_term_months")
    def _compute_applicant_age_end_of_term(self):
        for application in self:
            if application.applicant_1_age:
                application.applicant_1_age_end_of_term = self._calculate_age_end_of_term(application.applicant_1_age, application.mortgrage_term_year, application.mortgrage_term_months)
            if application.applicant_2_age:
                application.applicant_2_age_end_of_term = self._calculate_age_end_of_term(application.applicant_2_age, application.mortgrage_term_year, application.mortgrage_term_months)
                
    def _calculate_age_end_of_term(self, age, mortgage_years, mortgage_months):
        end_of_term_age = int(age)
        years = 0
        months = 0
        if mortgage_years:
            years += mortgage_years
        if int(mortgage_months):
            if int(mortgage_months) == 12:
                years += 1
            else:
                months = int(mortgage_months)
        end_of_term_age = f"{end_of_term_age + years} years"
        if months:
            end_of_term_age += f" {months} months"

        return end_of_term_age

    def _calculate_age(self, dob):
        today = fields.Date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @api.depends("total_net_basic_income_1", "total_other_income_1", "total_net_basic_income_2", "total_other_income_2", "other_income_counted", "nd2_income_counted")
    def _compute_income(self):
        """
            compute and assign total_income, total_sustainable_income, and allowable_monthly_income.
        """
        for application in self:
            total_net_basic_income_1 = int(application.total_net_basic_income_1 or 0)
            total_other_income_1 = int(application.total_other_income_1 or 0)
            total_net_basic_income_2 = int(application.total_net_basic_income_2 or 0)
            total_other_income_2 = int(application.total_other_income_2 or 0)
            other_income_counted = int(application.other_income_counted or 0)
            second_income_counted = int(application.nd2_income_counted or 0)

            application.total_income = total_net_basic_income_1 + total_other_income_1 + total_net_basic_income_2 + total_other_income_2
            application.total_sustainable_income = total_net_basic_income_1 + total_other_income_1 * (other_income_counted/100) + total_net_basic_income_2 * (second_income_counted/100) + total_other_income_2 * (other_income_counted/100)
            application.allowable_monthly_income = round(application.total_sustainable_income / 12, 2)

    @api.depends("property_value", "mortgage_amount", "first_time_buyer")
    def _compute_loan_to_value(self):
        """
            compute and assign loan_to_value ratio.
        """
        for application in self:
            if self.property_value:
                self.loan_to_value = round((self.mortgage_amount / self.property_value) * 100, 2)

            if self.first_time_buyer == 'yes':
                self.first_time_buyer_value = 90
            else:
                self.first_time_buyer_value = 80

            if self.company_id and self.company_id.ltv:
                self.show_image_1 = self.loan_to_value < self.company_id.ltv
            else:
                self.show_image_1 = self.loan_to_value < self.first_time_buyer_value

    @api.depends("total_basic_income_1", "total_basic_income_2", "mortgage_amount")
    def _compute_loan_to_income_ratio(self):
        """
            compute and assign loan_to_income_ratio and max_lend_facility 
        """
        for application in self:
            total_basic_income_1 = float(application.total_basic_income_1 or 0)
            total_basic_income_2 = float(application.total_basic_income_2 or 0)

            max_lend_facility = total_basic_income_1 + total_basic_income_2
            application.max_lend_facility = max_lend_facility * 3.5

            if max_lend_facility:
                application.loan_to_income_ratio = round(application.mortgage_amount / max_lend_facility, 2)

                if application.company_id.lti:
                    application.show_image_2 = application.loan_to_income_ratio < application.company_id.lti
                else:
                    application.show_image_2 = application.loan_to_income_ratio < 3.5

    @api.depends("company_id")
    def _compute_monthly_income_reduced(self):
        for application in self:
            application.monthly_income_reduced = application.company_id.monthly_income_reduced

    @api.depends("total_income", "monthly_income_reduced")    
    def _compute_stressed_income(self):
        for application in self:
            application.stressed_income = float(application.total_income - ((application.total_income / 100) * application.monthly_income_reduced))

    @api.depends("allowable_monthly_income", "monthly_income_reduced")
    def _compute_stressed_allowable_income(self):
        for application in self:
            application.stressed_allowable_income = float(application.allowable_monthly_income - ((application.allowable_monthly_income / 100) * application.monthly_income_reduced))

    @api.depends("mortgage_product_id")
    def _compute_on_mortgage_product(self):
        # New Code in 2020
        for application in self:
            if application.mortgage_product_id:
                mortgage = application.mortgage_product_id
                application.interest_rate = mortgage.variable_interest_rate
                application.term_at_starting_rate = mortgage.fixed_term
                application.fixed_interest_rate = mortgage.fixed_interest_rate

    @api.depends("single", "no_of_dependents")
    def _compute_ndi_monthly(self):
        for application in self:
            ndi_monthly = 0
            if application.single:
                ndi_monthly += int(application.single)
            if application.no_of_dependents:
                ndi_monthly += (application.no_of_dependents * 250)

            application.ndi_monthly = ndi_monthly

    @api.depends("values_of_gifts", "property_value", "mortgage_amount")
    def _compute_gift_to_deposit(self):
        for application in self:
            difference = float(application.property_value - application.mortgage_amount)
            if int(difference):
                application.gift_to_deposit = (application.values_of_gifts / difference) * 100

            if application.company_id.gift_to_deposit:
                application.show_image_5 = application.gift_to_deposit < application.company_id.gift_to_deposit
            else:
                application.show_image_5 = application.gift_to_deposit < STANDARD_GIFT_TO_DEPOSIT

    @api.depends("interest_rate", "mortgage_amount", "mortgrage_term_year", "mortgrage_term_months", "esis_payment_frequency")
    def _compute_repayment(self):
        """
        Compute Monthly Repayment from given mortgage_amount and interest rate.

        Parameters:
            interest_rate: Rate of Interst
            mortgage_amount: Principal Amount
            mortgrage_term_year: Duration of mortgage in years
            mortgrage_term_months: Duration of mortgrage in months(if any)
            esis_payment_frequency: Frequency of repayment
        """
        for application in self:
            mortgage_term = int(application.mortgrage_term_year * 12) + int(application.mortgrage_term_months)
            mortgage_term_years = application.mortgrage_term_year + (float(application.mortgrage_term_months) / 12)

            if application.interest_rate and mortgage_term:
                application.monthly_repayment = round(-1 * (npf.pmt((application.interest_rate / 100) / 12, mortgage_term, application.mortgage_amount)), 2)

            if application.esis_payment_frequency == "weekly":
                mortgage_term_2 = (int(application.mortgrage_term_year) * 52) + ((float(application.mortgrage_term_months) / 12) * 52)

                if application.interest_rate and mortgage_term_2:
                    if application.mortgage_type == "fixed_variable_rate":
                        result = self.calculate_outstanding_balance(application.fixed_interest_rate, mortgage_term_2, application.mortgage_amount, application.term_at_starting_rate * 52)
                        application.esis_weekly_repayment = application.get_monthly_payement(
                            annual_interest_rate = float(application.interest_rate),
                            number_of_periods = mortgage_term_2 - application.term_at_starting_rate * 52,
                            amount = result.get("outstanding_amount", 0.0),
                            frequency = "weekly"
                        )
                        application.esis_weekly_repayment_1 = application.get_monthly_payement(
                            annual_interest_rate = float(application.interest_rate) + 1,
                            number_of_periods = mortgage_term_2 - application.term_at_starting_rate * 52,
                            amount = result.get("outstanding_amount", 0.0),
                            frequency = "weekly"
                        )
                        application.esis_weekly_repayment_2 = application.get_monthly_payement(
                            annual_interest_rate = float(application.interest_rate) + 2,
                            number_of_periods = mortgage_term_2 - application.term_at_starting_rate * 52,
                            amount = result.get("outstanding_amount", 0.0),
                            frequency = "weekly"
                        )
                    else:
                        application.esis_weekly_repayment = round(-1 * (npf.pmt((application.interest_rate / 100) / 52, mortgage_term_2, application.mortgage_amount)), 2)
                        application.esis_weekly_repayment_1 = round(-1 * (npf.pmt(((application.interest_rate + 1) / 100) / 52, mortgage_term_2, application.mortgage_amount)), 2)
                        application.esis_weekly_repayment_2 = round(-1 * (npf.pmt(((application.interest_rate + 2) / 100) / 52, mortgage_term_2, application.mortgage_amount)), 2)
                    
                    application.esis_fortnightly_repayment = 0
                    application.esis_no_of_repayment = mortgage_term_years * 52
            elif application.esis_payment_frequency == "fortnightly":
                mortgage_term_3 = (application.mortgrage_term_year * 26) + ((float(application.mortgrage_term_months) / 12) * 26)
                
                application.esis_weekly_repayment = 0
                application.esis_no_of_repayment = mortgage_term_years * 26
                if application.interest_rate and mortgage_term_3:
                    if application.mortgage_type == "fixed_variable_rate":
                        result = self.calculate_outstanding_balance(application.fixed_interest_rate, mortgage_term_3, application.mortgage_amount, application.term_at_starting_rate * 26)

                        application.esis_fortnightly_repayment = self.get_monthly_payement(
                            annual_interest_rate=float(application.interest_rate),
                            number_of_periods=mortgage_term_3 - application.term_at_starting_rate * 26,
                            amount=result.get("outstanding_amount", 0.0),
                            frequency="fortnightly"
                        )
                        application.esis_fortnightly_repayment_1 = self.get_monthly_payement(
                            annual_interest_rate=float(application.interest_rate) + 1,
                            number_of_periods=mortgage_term_3 - application.term_at_starting_rate * 26,
                            amount=result.get("outstanding_amount", 0.0),
                            frequency="fortnightly"
                        )
                        application.esis_fortnightly_repayment_2 = self.get_monthly_payement(
                            annual_interest_rate=float(application.interest_rate) + 2,
                            number_of_periods=mortgage_term_3 - application.term_at_starting_rate * 26,
                            amount=result.get("outstanding_amount", 0.0),
                            frequency="fortnightly"
                        )
                    else:
                        application.esis_fortnightly_repayment = round(-1 * npf.pmt((application.interest_rate / 100) / 26, mortgage_term_3, application.mortgage_amount), 2)
                        application.esis_fortnightly_repayment_1 = round(-1 * npf.pmt(((application.interest_rate + 1) / 100) / 26, mortgage_term_3, application.mortgage_amount), 2)
                        application.esis_fortnightly_repayment_2 = round(-1 * npf.pmt(((application.interest_rate + 2) / 100) / 26, mortgage_term_3, application.mortgage_amount), 2)
            elif application.esis_payment_frequency == "monthly":
                application.esis_weekly_repayment = 0
                application.esis_fortnightly_repayment = 0
                application.esis_no_of_repayment = mortgage_term_years * 12

                if application.interest_rate and mortgage_term:
                    application.esis_monthly_repayment_1 = round(-1 * (npf.pmt(((application.interest_rate + 1) / 100) / 12, mortgage_term, application.mortgage_amount)), 2)
                    application.esis_monthly_repayment_2 = round(-1 * (npf.pmt(((application.interest_rate + 2) / 100) / 12, mortgage_term, application.mortgage_amount)), 2)
            application.esis_interest_rate = application.interest_rate + 1
            
    @api.depends("mortgrage_term_year", "mortgrage_term_months", "mortgage_amount", "fixed_interest_rate", "monthly_repayment", "esis_payment_frequency")
    def _compute_term_repayment(self):
        for application in self:
            mortgage_term_years = application.mortgrage_term_year + (float(application.mortgrage_term_months) / 12)
            mortgage_term = int(application.mortgrage_term_year) * 12 + int(application.mortgrage_term_months)

            if application.esis_payment_frequency == "monthly":
                step = 12
                multiplier = 1
            elif application.esis_payment_frequency == "fortnightly":
                step = 26
                multiplier = 2
            elif application.esis_payment_frequency == "weekly":
                step = 52
                multiplier = 4
            else:
                raise Exception(_(f"Unsupported Payment Frequency: {application.esis_payment_frequency}"))

            total_mortgage_periods = (int(application.mortgrage_term_year) * step) + (int(application.mortgrage_term_months) * multiplier)
            fixed_term_periods = int(application.term_at_starting_rate) * step

            if mortgage_term:
                application.fixed_term_payment = round(-1 * (npf.pmt((application.fixed_interest_rate / 100) / 12, total_mortgage_periods, int(application.mortgage_amount))), 2)

                result = application.calculate_outstanding_balance(
                    annual_interest_rate = application.fixed_interest_rate,
                    number_of_periods = total_mortgage_periods,
                    amount = application.mortgage_amount,
                    specified_period = (application.term_at_starting_rate * step),
                    frequency = application.esis_payment_frequency
                )

                application.repayment_at_variable = application.get_monthly_payement(application.interest_rate, total_mortgage_periods - application.term_at_starting_rate * step, result.get("outstanding_amount", 0.0), application.esis_payment_frequency)
                application.repayment_at_variable_plus1 = application.get_monthly_payement(application.interest_rate + 1.0, total_mortgage_periods - application.term_at_starting_rate * step, result.get("outstanding_amount", 0.0), application.esis_payment_frequency)
                application.repayment_at_variable_plus2 = application.get_monthly_payement(application.interest_rate + 2.0, total_mortgage_periods - application.term_at_starting_rate * step, result.get("outstanding_amount", 0.0), application.esis_payment_frequency)

                if application.mortgage_type == "fixed_variable_rate":
                    application.max_possible_repayment = max(application.fixed_term_payment, application.repayment_at_variable)
                else:
                    application.max_possible_repayment = application.monthly_repayment

                # TODO: Check What is the Use of these two variables?
                total_term_for_fixed_rate = application.term_at_starting_rate * 12
                total_term_for_variable_rate = mortgage_term - (application.term_at_starting_rate * 12)

    def calculate_outstanding_balance(self, annual_interest_rate, number_of_periods, amount, specified_period, frequency="monthly"):
        if frequency == "monthly":
            step = 12
            multiplier = 1
        elif frequency == "fortnightly":
            step = 26
            multiplier = 2
        elif frequency == "weekly":
            step = 52
            multiplier = 4
        else:
            raise Exception(_("Unsupported Payment Frequency"))

        total_installment_amount = 0
        total_installment_interest_amount = 0
        principal_amount = amount
        monthly_payement = self.get_monthly_payement(annual_interest_rate, number_of_periods, amount, frequency)
        for i in range(int(specified_period)):
            interest_at_installment = (annual_interest_rate / 100) / step * principal_amount
            installment_capital = monthly_payement - interest_at_installment

            # Calculate outstanding capital which will be principal amount for the next iteration
            principal_amount = principal_amount - installment_capital
            total_installment_amount += monthly_payement
            total_installment_interest_amount += interest_at_installment

        return {
            'outstanding_amount': principal_amount,
            'total_repayment_amount': total_installment_amount,
            'total_interest_paid_amount': total_installment_interest_amount
        }

    def get_monthly_payement(self, annual_interest_rate, number_of_periods, amount, frequency="monthly"):
        """
        Calculate Payments.
        
        Parameters:
            annual_interest_rate: Interst Rate,
            number_of_periods: Duration,
            amount: Principal Amount,
            frequency: monthly / fortnightly / weekly
        """
        if frequency == "weekly":
            months = 52
        elif frequency == "fortnightly":
            months = 26
        else:
            months = 12

        return round(-1 * (npf.pmt((annual_interest_rate / 100) / months, number_of_periods, float(amount))), 2)

    @api.depends("debt_repay", "property_co", "childcare", "maintenance")
    def _compute_total_short_term(self):
        for application in self:
            application.total_short_term = float(application.debt_repay + application.property_co + application.childcare + application.maintenance)

    @api.depends("allowable_monthly_income", "monthly_repayment", "total_short_term", "max_possible_repayment", "esis_payment_frequency")
    def _compute_service_ratio(self):
        for application in self:
            if application.esis_payment_frequency == "weekly":
                tmp_monthly_repayment = float(application.max_possible_repayment) * 30.4 / 7
            elif application.esis_payment_frequency == "fortnightly":
                tmp_monthly_repayment = float(application.max_possible_repayment) * 30.4 / 14
            elif application.esis_payment_frequency == "monthly":
                tmp_monthly_repayment = float(application.max_possible_repayment)
            else:
                raise Exception(_("Unknown ESIS Payment Frequency"))

            #if the mortage_type is variable rate we should be using the monthly_repayment to calculate all figures as net_disposable_inc, total_debt_service_ratio, mortgage_service ratio
            if application.mortgage_type == "variable_rate":
                tmp_monthly_repayment = application.monthly_repayment

            application.net_disposable_inc = float(application.allowable_monthly_income) - float(tmp_monthly_repayment + application.total_short_term)

            if application.allowable_monthly_income:
                application.mortgage_service_ratio = round((tmp_monthly_repayment / application.allowable_monthly_income) * 100, 2)
                application.total_debt_service_ratio = round(((tmp_monthly_repayment + application.total_short_term) / application.allowable_monthly_income) * 100, 2)

                if application.company_id.mortgage_service_ratio:
                    application.show_image_3 = application.mortgage_service_ratio < float(application.company_id.mortgage_service_ratio)
                else:
                    application.show_image_3 = application.mortgage_service_ratio < STANDARD_MORTGAGE_SERVICE_RATIO
                
                if application.company_id.debt_service_ratio:
                    application.show_image_4 = application.total_debt_service_ratio < float(application.company_id.debt_service_ratio)
                else:
                    application.show_image_4 = application.total_debt_service_ratio < STANDARD_TOTAL_DEBT_SERVICE_RATIO

    @api.depends("interest_rate", "mortgage_amount", "mortgrage_term_year", "mortgrage_term_months", "interest_rate_increase")
    def _compute_stressed_monthly_repayment(self):
        for application in self:
             mortgage_term = (application.mortgrage_term_year * 12) + int(application.mortgrage_term_months)

             if (application.interest_rate + application.interest_rate_increase) and mortgage_term:
                 application.stressed_monthly_repayment = round(-1 * (npf.pmt(((application.interest_rate + application.interest_rate_increase) / 100) / 12, mortgage_term, application.mortgage_amount)), 2)

    @api.depends("stressed_allowable_income", "stressed_monthly_repayment", "total_short_term")
    def _compute_stressed_service_ratio(self):
        """
        Compute and Assign stressed_mortgage_service_ratio, stressed_total_debt_service_ratio, stressed_net_disposable_income.
        """
        for application in self:
            if application.stressed_allowable_income:
                application.stressed_mortgage_service_ratio = round((application.stressed_monthly_repayment / application.stressed_allowable_income) * 100, 2)
                application.stressed_total_debt_service_ratio = round(((application.stressed_monthly_repayment + application.total_short_term) / application.stressed_allowable_income) * 100, 2)
                application.stressed_net_disposable_income = application.stressed_allowable_income - (application.stressed_monthly_repayment + application.total_short_term)

                if application.company_id.stressed_mortgage_service_ratio:
                    application.show_image_8 = application.stressed_mortgage_service_ratio < application.company_id.stressed_mortgage_service_ratio
                else:
                    application.show_image_8 = application.stressed_mortgage_service_ratio < STANDARD_STRESSED_MORTGAGE_SERVICE_RATIO

                if application.company_id.stressed_debt_service_ratio:
                    application.show_image_9 = application.stressed_total_debt_service_ratio < application.company_id.stressed_debt_service_ratio
                else:
                    application.show_image_9 = application.stressed_total_debt_service_ratio < STANDARD_TOTAL_DEBT_SERVICE_RATIO

    @api.depends("monthly_repayment", "mortgrage_term_year", "mortgrage_term_months", "esis_payment_frequency", "mortgage_amount", "repayment_at_variable", "term_at_starting_rate", "fixed_term_payment")
    def _compute_total_repaid(self):
        for application in self:
            if application.esis_payment_frequency == "monthly":
                step = 12
                multiplier = 1
            elif application.esis_payment_frequency == "fortnightly":
                step = 26
                multiplier = 2
            elif application.esis_payment_frequency == "weekly":
                step = 52
                multiplier = 4
            else:
                raise Exception(_(f"Unsupported Payment Frequency: {application.esis_payment_frequency}"))

            mortgage_term = int(application.mortgrage_term_year + (float(application.mortgrage_term_months) / 12))
            
            if application.mortgage_type == "variable_rate":
                if application.esis_payment_frequency == "monthly":
                    application.esis_total_repaid = application.monthly_repayment * ((float(application.mortgrage_term_year) * step) + (float(application.mortgrage_term_months) * multiplier))
                elif application.esis_payment_frequency == "fortnightly":
                    application.esis_total_repaid = application.esis_fortnightly_repayment * ((float(application.mortgrage_term_year) * step) + (float(application.mortgrage_term_months) * multiplier))
                elif application.esis_payment_frequency == "weekly":
                    application.esis_total_repaid = application.esis_weekly_repayment * ((float(application.mortgrage_term_year) * step) + (float(application.mortgrage_term_months) * multiplier))
                else:
                    raise Exception(_(f"Unsupported Payment Frequency: {application.esis_payment_frequency}"))
            else:
                application.esis_total_repaid = (application.fixed_term_payment * application.term_at_starting_rate * step) + (application.repayment_at_variable * ((float(application.mortgrage_term_year) * step) + (float(application.mortgrage_term_months) * multiplier)) - (application.term_at_starting_rate * step))

            application.esis_cost_of_credit = application.esis_total_repaid - application.mortgage_amount

            if int(application.mortgrage_term_year) or int(application.mortgrage_term_months):
                application.avg_repayment = application.esis_total_repaid / ((application.mortgrage_term_year * step) + (float(application.mortgrage_term_months) * multiplier))
            else:
                application.avg_repayment = 0.0

            if application.mortgage_amount and application.avg_repayment:
                if application.esis_payment_frequency == "weekly":
                    tmp_avg_repayment = (application.avg_repayment * 30.4) / 7
                elif application.esis_payment_frequency == "fortnightly":
                    tmp_avg_repayment = (application.avg_repayment * 30.4) / 14
                elif application.esis_payment_frequency == "monthly":
                    tmp_avg_repayment = application.avg_repayment 
                else:
                    raise Exception(_(f"Unsuported Payment Frequency: {application.esis_payment_frequency}"))

                application.avg_rate = (npf.rate((application.mortgrage_term_year * 12) + int(application.mortgrage_term_months), -1 * tmp_avg_repayment, application.mortgage_amount, 0) * 12) * 100
                application.avg_repayment_plus1 = round(-1 * (npf.pmt(((application.avg_rate + 1) / 100) / 12, (application.mortgrage_term_year * 12) + int(application.mortgrage_term_months), application.mortgage_amount)), 2)

                if application.mortgage_amount:
                    application.esis_cost_per_1 = application.esis_total_repaid / application.mortgage_amount

    @api.depends("monthly_repayment", "avg_repayment", "esis_monthly_repayment_1", "avg_repayment_plus1", "mortgage_amount", "mortgrage_term_year", "mortgrage_term_months", "contribution_to_valuation", "contribution_to_revaluation", "once_off_costs")
    def _compute_aprc(self):
        for application in self:
            mortgage_term = int(application.mortgrage_term_year) + (float(application.mortgrage_term_months) / 12)

            if application.esis_payment_frequency == "weekly":
                tmp_monthly_repayment = (float(application.avg_repayment) * 30.4 ) / 7
            elif application.esis_payment_frequency == "fortnightly":
                tmp_monthly_repayment = (float(application.avg_repayment) * 30.4) / 14
            elif application.esis_payment_frequency == "monthly":
                tmp_monthly_repayment = application.avg_repayment
            else:
                raise Exception(_(f"Unsupported Payment Frequency: {application.esis_payment_frequency}"))

            if mortgage_term and application.monthly_repayment:
                esis_aprc_value = npf.rate(mortgage_term * 12, -1 * tmp_monthly_repayment, application.mortgage_amount - (application.contribution_to_valuation + application.contribution_to_revaluation + application.once_off_costs), 0)
                esis_aprc_value = (np.power(esis_aprc_value + 1, 12) - 1) * 100
                application.esis_aprc = round(esis_aprc_value, 1)

            if mortgage_term and application.esis_monthly_repayment_1:
                esis_aprc_value = npf.rate(mortgage_term * 12, -1 * application.avg_repayment_plus1, application.mortgage_amount - (application.contribution_to_valuation + application.contribution_to_revaluation + application.once_off_costs), 0)
                esis_aprc_value = (np.power(esis_aprc_value + 1, 12) - 1) * 100
                application.esis_aprc_1 = round(esis_aprc_value, 1)

    @api.depends("applicant_1_net_profit_1", "applicant_1_plus_depreceation_1", "applicant_1_plus_interest_paid_1", "applicant_1_plus_remuneration_1",  "applicant_1_plus_pension_1")
    def _compute_mry(self):
        for application in self:
            application.applicant_1_trading_profit_1 = int(application.applicant_1_net_profit_1) + int(application.applicant_1_plus_depreceation_1) + int(application.applicant_1_plus_interest_paid_1) + int(application.applicant_1_plus_remuneration_1) +  int(application.applicant_1_plus_pension_1)

    @api.depends("applicant_1_net_profit_2", "applicant_1_plus_depreceation_2", "applicant_1_plus_interest_paid_2", "applicant_1_plus_remuneration_2",  "applicant_1_plus_pension_2")
    def _compute_mry_1(self):
        for application in self:
            application.applicant_1_trading_profit_2 = int(application.applicant_1_net_profit_2) + int(application.applicant_1_plus_depreceation_2) + int(application.applicant_1_plus_interest_paid_2) + int(application.applicant_1_plus_remuneration_2) +  int(application.applicant_1_plus_pension_2)
  
    @api.depends("applicant_1_net_profit_3", "applicant_1_plus_depreceation_3", "applicant_1_plus_interest_paid_3", "applicant_1_plus_remuneration_3",  "applicant_1_plus_pension_3")
    def _compute_mry_2(self):
        for application in self:
            application.applicant_1_trading_profit_3 = int(application.applicant_1_net_profit_3) + int(application.applicant_1_plus_depreceation_3) + int(application.applicant_1_plus_interest_paid_3) + int(application.applicant_1_plus_remuneration_3) +  int(application.applicant_1_plus_pension_3)

    @api.depends("applicant_1_trading_profit_1", "applicant_1_trading_profit_2", "applicant_1_trading_profit_3")
    def _compute_avg_trading_profit_1(self):
        for application in self:
            application.applicant_1_average_trading_profit = round((float(application.applicant_1_trading_profit_1) + float(application.applicant_1_trading_profit_2) + float(application.applicant_1_trading_profit_3)) / 3, 2)

    @api.depends("applicant_1_average_trading_profit", "applicant_1_less_business_repayments")
    def _compute_surplus_1(self):
        for application in self:
            application.applicant_1_surplus = float(application.applicant_1_average_trading_profit) - float(application.applicant_1_less_business_repayments)

    @api.depends("applicant_2_net_profit_1", "applicant_2_plus_depreceation_1", "applicant_2_plus_interest_paid_1", "applicant_2_plus_remuneration_1",  "applicant_2_plus_pension_1")
    def _compute_mry2(self):
        for application in self:
            application.applicant_2_trading_profit_1 = int(application.applicant_2_net_profit_1) + int(application.applicant_2_plus_depreceation_1) + int(application.applicant_2_plus_interest_paid_1) + int(application.applicant_2_plus_remuneration_1) +  int(application.applicant_2_plus_pension_1)

    @api.depends("applicant_2_net_profit_2", "applicant_2_plus_depreceation_2", "applicant_2_plus_interest_paid_2", "applicant_2_plus_remuneration_2",  "applicant_2_plus_pension_2")
    def _compute_mry2_1(self):
        for application in self:
            application.applicant_2_trading_profit_2 = int(application.applicant_2_net_profit_2) + int(application.applicant_2_plus_depreceation_2) + int(application.applicant_2_plus_interest_paid_2) + int(application.applicant_2_plus_remuneration_2) +  int(application.applicant_2_plus_pension_2)
    
    @api.depends("applicant_2_net_profit_3", "applicant_2_plus_depreceation_3", "applicant_2_plus_interest_paid_3", "applicant_2_plus_remuneration_3",  "applicant_2_plus_pension_3")
    def _compute_mry2_2(self):
        for application in self:
            application.applicant_2_trading_profit_3 = int(application.applicant_2_net_profit_3) + int(application.applicant_2_plus_depreceation_3) + int(application.applicant_2_plus_interest_paid_3) + int(application.applicant_2_plus_remuneration_3) +  int(application.applicant_2_plus_pension_3)

    @api.depends("applicant_2_trading_profit_1", "applicant_2_trading_profit_2", "applicant_2_trading_profit_3")
    def _compute_avg_trading_profit_2(self):
        for application in self:
            application.applicant_2_average_trading_profit = round((float(application.applicant_2_trading_profit_1) + float(application.applicant_2_trading_profit_2) + float(application.applicant_2_trading_profit_3)) / 3, 2)

    @api.depends("applicant_2_average_trading_profit", "applicant_2_less_business_repayments")
    def _compute_surplus_2(self):
        for application in self:
            application.applicant_2_surplus = float(application.applicant_2_average_trading_profit) - float(application.applicant_2_less_business_repayments)

    def action_limits_eligible(self):
        self.ensure_one()

        self.check_checklist()
        values = {'state': "limits_eligible"}
        if not self.applicant_2:
            values.update({'applicant_2_age': "", 'applicant_2_age_end_of_term': "", 'total_basic_income_2': "", 'total_net_basic_income_2': "", 'total_other_income_2': "", 'self_employed_2': "no"})
        self.write(values)

        self.load_checklist_items()

    def action_limits_not_eligible(self):
        self.ensure_one()
        self.check_checklist()

        context = dict(self.env.context or {})
        limits_not_eligible_form = self.env.ref("appsmod2.wizard_limits_not_eligible_view_form")
        return {
            'name': _("Limits Not Eligible"),
            'type': "ir.actions.act_window",
            'view_mode': "form",
            'res_model': "wizard.limits.not.eligible",
            'views': [(limits_not_eligible_form.id, "form")],
            'view_id': limits_not_eligible_form.id,
            'target': "new",
            'context': context
        }


    def load_checklist_items(self, state="application_form_received"):
        self.ensure_one()
        application_id = self.env.context.get("active_id", False) or self.id

        all_applicants = self.env["application.checklist"].search([('type', '=', "all_applicants"), ('active', '=', True), ('applicable_for_eu_citizen', '=', False), ('state', '=', state)])
        if all_applicants:
            values = [{'name': checklist.name, 'application_id': application_id, 'sequence': checklist.sequence, 'state': state} for checklist in all_applicants]
            self.env["jointly.applicable"].create(values)

        individually_applicable = self.env["application.checklist"].search([('type', '=', "all_applicants_individual"), ('active', '=', True), ('applicable_for_eu_citizen', '=', False), ('state', '=', state)])
        if individually_applicable:
            values = [{'name': checklist.name, 'application_id': application_id, 'sequence': checklist.sequence, 'state': state} for checklist in individually_applicable]
            self.env["checklist.applicable.applicant1"].create(values)
            if self.applicant_2:
                self.env["checklist.applicable.applicant2"].create(values)
            
        self_applicable = self.env["application.checklist"].search([('type', '=', 'self_employed'), ('active', '=', True), ('applicable_for_eu_citizen', '=', False), ('state', '=', state)])
        if self_applicable:
            values = [{'name': checklist.name, 'application_id': application_id, 'sequence': checklist.sequence, 'state': state} for checklist in self_applicable]
            if self.self_employed_1 == "yes":
                self.env["checklist.self.applicable.applicant1"].create(values)
            if self.applicant_2 and self.self_employed_2 == "yes":
                self.env["checklist.self.applicable.applicant2"].create(values)

        paye_applicable = self.env["application.checklist"].search([('type', '=', 'paye_employees'), ('active', '=', True), ('applicable_for_eu_citizen', '=', False), ('state', '=', state)])
        if paye_applicable:
            values = [{'name': checklist.name, 'application_id': application_id, 'sequence': checklist.sequence, 'state': state} for checklist in paye_applicable]
            if self.self_employed_1 == "no":
                self.env["checklist.paye.applicable.applicant1"].create(values)
            if self.applicant_2 and self.self_employed_2 == "no":
                self.env["checklist.paye.applicable.applicant2"].create(values)

        # Add EU Citizen Checklist Items 
        individually_applicable = self.env['application.checklist'].search([('type', '=', 'all_applicants_individual'), ('active', '=', True), ('applicable_for_eu_citizen', '=', True), ('state', '=', state)])
        if individually_applicable:
            values = [{'name': checklist.name, 'application_id': application_id, 'sequence': checklist.sequence, 'state': state} for checklist in individually_applicable]
            if self.applicant_1_eu_citizen == "yes":
                self.env['checklist.applicable.applicant1'].create(values)
            if self.applicant_2 and self.applicant_2_eu_citizen == "yes":
                self.env['checklist.applicable.applicant2'].create(values)

        self_applicable = self.env['application.checklist'].search([('type', '=', 'self_employeed'), ('active', '=', True), ('applicable_for_eu_citizen', '=', True), ('state', '=', state)])
        if self_applicable:
            values = [{'name': checklist.name, 'application_id': application_id, 'sequence': checklist.sequence, 'state': state} for checklist in self_applicable]
            if self.applicant_1_eu_citizen == "yes" and self.self_employed_1 == "yes":
                self.env['checklist.self.applicable.applicant1'].create(values)
            if self.applicant_2 and self.applicant_2_eu_citizen == "yes" and self.self.self_employed_2 == "yes":
                self.env['checklist.self.applicable.applicant2'].create(values)

        paye_applicable = self.env['application.checklist'].search([('type', '=', 'paye_employees'), ('active', '=', True), ('applicable_for_eu_citizen', '=', True), ('state', '=', state)])
        if paye_applicable:
            values = [{'name': checklist.name, 'application_id': application_id, 'sequence': checklist.sequence, 'state': state} for checklist in paye_applicable]
            if self.applicant_1_eu_citizen == "yes" and self.self_employed_1 == "no":
                self.env['checklist.paye.applicable.applicant1'].create(values)
            if self.applicant_2 and self.applicant_2_eu_citizen == "yes" and self.self_employed_2 == "no":
                    self.env['checklist.paye.applicable.applicant2'].create(values)

    def check_checklist(self):
        self.ensure_one()
        applicant1_passed = True
        applicant2_passed = True
        jointly_passed = True


        message_error = "Following Checklist Items Failed: \n"
        jointly_error = "\nJOINTLY\n"
        applicant1_error = "\nAPPLICANT 1\n"
        applicant2_error = "\nAPPLICANT 2\n"

        all_applicants = self.env["jointly.applicable"].search([('application_id', '=', self.id)])
        for checklist in all_applicants:
            if not checklist.acceptable:
                jointly_error = f"{jointly_error}- {checklist.name}\n"
                jointly_passed = False

        individually_applicable1 = self.env["checklist.applicable.applicant1"].search([('application_id', '=', self.id)])
        for checklist in individually_applicable1:
            if not checklist.acceptable:
                applicant1_error += f"- {checklist.name}\n"
                applicant1_passed = False

        if self.applicant_1_credit_risk == "no":
            applicant1_error += f"- Credit Risk Not Acceptable\n"
            applicant1_passed = False

        individually_applicable2 = self.env["checklist.applicable.applicant2"].search([('application_id', '=', self.id)])
        for checklist in individually_applicable2:
            if not checklist.acceptable:
                applicant2_error += f"- {checklist.name}\n"
                applicant2_passed = False

        if self.applicant_2_credit_risk == "no":
            applicant2_error += f"- Credit Risk Not Acceptable\n"
            applicant2_passed = False

        self_applicable1 = self.env["checklist.self.applicable.applicant1"].search([('application_id', '=', self.id)])
        for checklist in self_applicable1:
            if not checklist.acceptable:
                applicant1_error += f"- {checklist.name}\n"
                applicant1_passed = False

        self_applicable2 = self.env["checklist.self.applicable.applicant2"].search([("application_id", '=', self.id)])
        for checklist in self_applicable2:
            if not checklist.acceptable:
                applicant2_error += f"- {checklist.name}\n"
                applicant2_passed = False

        paye_applicable1 = self.env["checklist.paye.applicable.applicant1"].search([("application_id", '=', self.id)])
        for checklist in paye_applicable1:
            if not checklist.acceptable:
                applicant1_error += f"- {checklist.name}\n"
                applicant1_passed = False
            
        paye_applicable2 = self.env["checklist.paye.applicable.applicant2"].search([('application_id', '=', self.id)])
        for checklist in paye_applicable2:
            if not checklist.acceptable:
                applicant2_error += f"- {checklist.name}\n"
                applicant2_passed = False

        if not jointly_passed:
            message_error += jointly_error
        if not applicant1_passed:
            message_error += applicant1_error
        if not applicant2_passed:
            message_error += applicant2_error

        if jointly_passed and applicant1_passed and applicant2_passed:
            return True
        else:
            raise UserError(_(message_error))

    def action_decline(self):
        self.ensure_one()
        context = dict(self.env.context)
        decline_form = self.env.ref("appsmod2.wizard_decline_view_form")

        return {
            'name': _("Declination Confirmation"),
            'type': "ir.actions.act_window",
            'view_mode': "form",
            'res_model': "wizard.decline",
            'views': [(decline_form.id, "form")],
            'view_id': decline_form.id,
            'target': 'new',
            'context': context
        }
