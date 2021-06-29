# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models,api,_

_logger = logging.getLogger(__name__)

class BusinessAccount(models.Model):
    '''Business account model description'''
    _name = 'business.account'
    _description = '''Business account'''

    company_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Company Currency",default=lambda self: self.env.company.currency_id,)
    period_end = fields.Date('Year/Period End',default=fields.Date.today,help='Specify the financial Year')
    current_assets  = fields.Monetary(string="Bussiness Drawing",currency_field='company_currency_id')
    stock = fields.Float('Stock',default=0.0)
    debtors = fields.Float('Debtors',default=0.0)
    cash_bank_balance = fields.Float('Cash & Bank Balance',default=0.0)
    total_current_assets = fields.Float('TOTAL CURRENT ASSETS',compute='_compute_total_current_assets',copy=False)
    
    current_liabilities = fields.Float('Currennt Liabilities',default=0.0)
    creditors = fields.Float('Creditors [incl. VAT,PAYE,PRSI]',default=0.0)
    taxation = fields.Float('Taxation [Corporation Tax]',default=0.0)
    dividends = fields.Float('Dividends',default=0.0)
    current_borrowings = fields.Float('Current Borrowing',default=0.0)
    director_accounts = fields.Float('Director Accounts',default=0.0)
    total_current_liabilities = fields.Float('TOTAL CURRENT LIABILITIES',compute='_compute_total_current_liabilities',copy=False)
    net_assets_liabilities = fields.Float('NET CURRENT ASSETS/LIABILITIES',compute='_compute_net_current_asset_lia',copy=False)

    current_ratio = fields.Float('Current Ration',compute='_compute_current_ration',copy=False)

    other_assets = fields.Float('FIXED/OTHER ASSETS',default=0.0)
    land_building = fields.Float('Land & Buildings',default=0.0)
    investment_company = fields.Float('Investment in Associate Companies',default=0.0)
    pem_vehicle = fields.Float('Plant,Equipment & Motor Companies',default=0.0)
    total_fixed_assets = fields.Float('TOTAL FIXED ASSETS',compute='_compute_fixed_assets',copy=False)
    total_capital_employed = fields.Float('TOTAL CAPTAL EMPLOYED',compute='_compute_capital_employed',copy=False)

    business_application_id = fields.Many2one('business.application',string='Business Application',copy=False)
    

    @api.depends('stock','current_assets','debtors','cash_bank_balance')
    def _compute_total_current_assets(self):
        for rec in self:
            rec.total_current_assets = rec.current_assets + rec.stock + rec.debtors + rec.cash_bank_balance


    @api.depends('current_liabilities','creditors','taxation','dividends','current_borrowings','director_accounts')
    def _compute_total_current_liabilities(self):
        for rec in self:
            rec.total_current_liabilities = rec.current_liabilities + rec.creditors + rec.taxation + rec.dividends + rec.current_borrowings + rec.director_accounts

    @api.depends('total_current_liabilities','total_current_assets',)
    def _compute_net_current_asset_lia(self):
        for rec in self:
            rec.net_assets_liabilities = rec.total_current_assets - rec.total_current_liabilities


    # Need to discuss the logic of function
    @api.depends('net_assets_liabilities')
    def _compute_current_ration(self):
        for rec in self:
            rec.current_ratio = 0.75

    @api.depends('other_assets','land_building','investment_company','pem_vehicle')
    def _compute_fixed_assets(self):
        for rec in self:
            rec.total_fixed_assets = rec.other_assets + rec.land_building + rec.investment_company + rec.pem_vehicle

    @api.depends('total_fixed_assets','net_assets_liabilities',)
    def _compute_capital_employed(self):
        for rec in self:
            rec.total_capital_employed = rec.total_fixed_assets - rec.net_assets_liabilities

    
    def _valid_fields(self):
        return [
            'current_assets',
            'stock',
            'debtors',
            'cash_bank_balance',
            'total_current_assets',
            'current_liabilities',
            'creditors',
            'taxation',
            'dividends',
            'current_borrowings',
            'director_accounts',
            'total_current_liabilities',
            'net_assets_liabilities',
            'current_ratio',
            'other_assets',
            'land_building',
            'investment_company',
            'pem_vehicle',
            'total_fixed_assets',
            'total_capital_employed',
        ]

    def _get_field_value(self,field):
        return getattr(self,field,None)


    def _get_compute_field(self,):
        return [
            'total_current_assets',
            'total_current_liabilities',
            'net_assets_liabilities',
            'current_ratio',
            'total_fixed_assets',
            'total_capital_employed',
        ]

    


        
