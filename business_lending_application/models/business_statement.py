# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class BusinessStatement(models.Model):
    _name = 'business.statement'
    _description = ''' Business.statement model description'''