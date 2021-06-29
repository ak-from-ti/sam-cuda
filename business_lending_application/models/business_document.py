# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _,api

_logger = logging.getLogger(__name__)


TYPE_OF_DOCUMENT = [
    ('balance_sheet','Balance Sheet'),
    ('profit_loss','Profit and Loss'),
    ('five_yr_tax_report','Five years of Tax reports'),
    ('other','Other'),
]


class BusinessRelatedDocument(models.Model):
    _name = 'business.related.document'
    _description = '''Business Related document'''


    name = fields.Char("Name", required=True,default=lambda self: _("New"))
    sequence = fields.Integer(default=10, index=True)
    data_file = fields.Binary("File", required=True)
    data_file_name = fields.Char("File Name")
    business_application_id = fields.Many2one('business.application', "Business Application Id", index=True, ondelete='cascade')
    document_type = fields.Selection(TYPE_OF_DOCUMENT,string='Document Type',required=True)
    document_info = fields.Text('Description about the document')

    @api.onchange("data_file_name")
    def _onchange_data_filename(self):
        self.ensure_one()
        if self.data_file_name:
            filename = str(self.data_file_name)
            self.name = '.'.join(filename.split('.')[:-1])
        else:
            self.name = "New"


    def action_show_document(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        end_string = f"/web/content/{self.id}?model={self._name}&field=data_file&filename_field=data_file_name&download=true" 

        attachment_extension = self.data_file_name[-3:]     
        attachment_title = self.data_file_name
        url = f"{base_url}/attachment_preview/static/lib/ViewerJS/index.html?type={attachment_extension}&title={attachment_title}#{end_string}"

        return {
            'name': _("Attachment View"),
            'res_model': "ir.actions.act_url",
            'type': "ir.actions.act_url",
            'target': 'new',
            'url': url
        }


class RelationshipRelatedDocument(models.Model):
    _name = 'relationship.related.document'
    _description = '''Relationship Related document'''


    name = fields.Char("Name", required=True,default=lambda self: _("New"))
    sequence = fields.Integer(default=10, index=True)
    data_file = fields.Binary("File", required=True)
    data_file_name = fields.Char("File Name")
    business_application_id = fields.Many2one('business.application', "Business Application Id", index=True, ondelete='cascade')
    business_relationship_id = fields.Many2one('res.partner', "Business Relationship", index=True, ondelete='cascade')
    document_type = fields.Selection(TYPE_OF_DOCUMENT,string='Document Type',required=True)
    document_info = fields.Text('Description about the document')

    @api.onchange("data_file_name")
    def _onchange_data_filename(self):
        self.ensure_one()
        if self.data_file_name:
            filename = str(self.data_file_name)
            self.name = '.'.join(filename.split('.')[:-1])
        else:
            self.name = "New"

            
    def action_show_document(self):
        pass
