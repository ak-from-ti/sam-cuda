# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from typing import DefaultDict

from odoo import fields, models,api,_

_logger = logging.getLogger(__name__)


class BusinessAssets(models.Model):
    _name = 'business.assets'
    _description = ''' Business.assets model represent assets and liabilities of the business borrower'''

    business_borrower = fields.Many2one('res.partner',string='Borrower name',domain="[('is_borrower', '=', True)]",help="Choose the business borrower.")
    name = fields.Char('Asset name',help='Define the asset name.')
    liability = fields.Char('Liability',help='Define the Liability.')
    financial_institute = fields.Char('Financial Institute',help='Define the Financial Institute.')
    repayment = fields.Char('Repayment',help='Define the Repayment.')
    term = fields.Char('Term',help='Define the Term.')
    income = fields.Char('Income',help='Define the income.')
    value = fields.Char('Value',help='Define the value.')
    business_application_id = fields.Many2one('business.application',string='Business Application',)
