# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class BusinessPersonalRepaymentCapacity(models.Model):
    _name = 'business.personal.repayment.capactiy'
    _description = ''' Business.personal.repayment.capacity model description'''