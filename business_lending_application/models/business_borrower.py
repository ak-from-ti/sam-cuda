# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class BusinessBorrower(models.Model):
    '''BusinessBorrower class represent a business entity that applies for a loan,'''
    
    _inherit = 'res.partner'

    company_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Company Currency",default=lambda self: self.env.company.currency_id)

    is_borrower = fields.Boolean('Is partner is borrower',default=False)

    entity = fields.Char('Type of Entity')
    contact_person = fields.Char('Contact Person',help='Contact Person')
    business_sector = fields.Char('Business Section')
    no_employees = fields.Integer('Number of employees',default=0)
    business_year = fields.Float('Years in business',default=0.0,digits='Business Year')
    business_premises = fields.Char('Business Premised')
    company_reg_no = fields.Char('Company Registration Number')
    member_number = fields.Integer('Member Number')
    main_branch = fields.Text('Main branch')
    accountant_details = fields.Text('Accountant Details')
    tax_confirmation = fields.Char('Tax Confirmation Received')
    solicitor_details = fields.Text('Solicitor Details')
    business_drawing = fields.Monetary(string="Bussiness Drawing",currency_field='company_currency_id')
