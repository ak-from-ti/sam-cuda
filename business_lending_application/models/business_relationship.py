# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class BusinessRelationship(models.Model):
    ''' Business.relationship model description'''
    _inherit = 'res.partner'

    nature_of_business = fields.Char('Nature of Business Relationship')
    business_borrower = fields.Many2one('res.partner', string='Business Entity',domain="[('is_borrower', '=', True)]",help="Choose the business borrower from which contact belongs." )
    is_relationship = fields.Boolean('does this partner is in business relationship',default=False)

    martial_status = fields.Selection([
        ('married','Married'),
        ('single','Single'),
    ],default='single')
    home_owner  = fields.Char('Home Owner')
    dob = fields.Date('Date of birth')
    date_joined = fields.Datetime('Date Joined',tracking=True, default=fields.Date.today)
    dependent_children = fields.Integer('Dependent Children',default=0)
    account_number = fields.Integer('Account Number')
    employment_status = fields.Char('Employment status')
    employment_year = fields.Integer('Years in employment')
    experience_year = fields.Integer('Years Experience')
    salary = fields.Float('Salary')

    # Discussion about values
    # frequency = fields.Selection([
    #     ('weekly','Weekly'),
    #     ('mon')
    # ])
    member_number = fields.Integer('Member Number')