# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class BusinessInterestRate(models.Model):
    _name = 'business.interest.rate'
    _description = ''' Business.interest.rate model description'''


    active = fields.Boolean('Active', default=True)
    name = fields.Char('Name')
    interest_rate = fields.Float('Interest Rate',help='Enter the interest rate.')
    loan_term = fields.Float('Loan Term',help='Enter the loan term.')

    # Discussion about type
    repayment_frequency = fields.Integer('Repayment Frequency',default=1) 

    