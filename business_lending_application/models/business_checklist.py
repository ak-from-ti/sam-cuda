# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _

import logging
_logger = logging.getLogger(__name__)

CHECKLIST_CATEGORY = [
    ('business_checklist','Business Checklist'),
    ('entity_checklist','Entity Checklist'),
    ('individual_checklist','Individual Checklist'),
]

class BusinessChecklist(models.Model):
    _name = 'business.checklist'
    _description = ''' Business checklist model description'''


    name = fields.Char('Checklist name',required=True,)



class BusinessApplicationChecklist(models.Model):
    _name = 'business.application.checklist'
    _description = ''' Business application checklist model description'''


    checklist_type = fields.Selection(CHECKLIST_CATEGORY,string='Checklist type',required=True,copy=False,)
    checklist_id = fields.Many2one('business.checklist',string='Checklist',required=True,copy=False)
    checklist_satisfactory = fields.Boolean('Checklist Satisfactory',default=False)
    checklist_comment = fields.Text('Checklist Comment',help='Enter about the Checklist Comment.')
    business_application_id = fields.Many2one('business.application',string='Business Application',copy=False)