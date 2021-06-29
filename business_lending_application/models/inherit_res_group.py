# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)



class Users(models.Model):
    _inherit = 'res.users'

    # decision_group_id = fields.Many2one('decision.group',string='Decision Group',copy=False,readonly=True,help='User belongs to which decision Group.')
    decision_maker = fields.Boolean('Is decision-maker',default=False,copy=False)



class DecisionGroup(models.Model):
    _name = 'decision.group'
    _description = 'Decision Group'

    name = fields.Char('Group Name',required=True,copy=False,help='Give the name of the Group.')
    user_ids = fields.Many2many('res.users',string='User belongs to this group')

    business_application_ids = fields.One2many('business.application','decision_group_id',string='Business Application Ids',help='All the assigned business application to this group.',copy=False,)

    _sql_constraints = [
        ('group_name_uniq', 'unique (name)', 'The name of the group must be unique !')
    ]

