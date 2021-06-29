# -*- coding: utf-8 -*-
{
    'name': "SAM - Secure Application Management",
    'author': "Target Integration",
    'summary': "This module implements Application Module of Target Integration",
    'description': """
        This module will create the workflow needed to support the Test & Affordability Calculator's functionality as described in the tickets
        #9844, #9851, #9853, #9854, #9855, #9856
    """,
    'website': "http://www.targetintegration.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': "Uncategorized",
    'version': "0.1",
    # any module necessary for this one to work correctly
    'depends': [
        "base", "mail", "contacts"
    ],
    'data': [
        'security/appsmod2_security.xml',
        'security/ir.model.access.csv',
        'data/default_checklist_data.xml',
        'data/ir_sequence_data.xml',
        'views/mortgage_product_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/application_checklist_views.xml',
        'views/application_views.xml',
        'views/appsmod2_menus.xml',
        'wizard/wizard_decline_views.xml',
        'wizard/wizard_limits_not_eligible_views.xml'
    ],
    'external_dependencies': {
        'python': ['numpy', 'numpy-financial']
    },
    'application': True
}
