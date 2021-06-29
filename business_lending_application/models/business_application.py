# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import fields, models,api,_
from odoo.tools.translate import html_translate

_logger = logging.getLogger(__name__)


class BusinessApplication(models.Model):
    '''Business.application model represent Business Application entity'''
    _name = 'business.application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '''Business Application'''

    name = fields.Char(string='Application Reference',required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    enquire_date = fields.Datetime('Enquire Date',default=fields.Date.today,help='Creation Date of application.')
    business_borrower = fields.Many2one('res.partner',string='Borrower name',domain="[('is_borrower', '=', True)]",help="Choose the business borrower.")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('lending_sent', 'Lending pack'),
        ('internal_meet', 'Internal Meeting'),
        ('info_received', 'Info Received'),
        ('due_diligence','Due Diligence'),
        ('financial_account','Financial Account'),
        ('cover_note','Cover Note'),
        ('approved','Approved'),
        ('close', 'Closed'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    company_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Company Currency",default=lambda self: self.env.company.currency_id,related='business_borrower.company_currency_id',store=True)

    entity = fields.Char('Type of Entity',)
    contact_person = fields.Char('Contact Person',help='Contact Person')
    business_sector = fields.Char('Business Section')
    no_employees = fields.Integer('Number of employees',default=0)
    business_year = fields.Float('Years in business',default=0.0,digits='Product Price')
    business_premises = fields.Char('Business Premised')
    company_reg_no = fields.Char('Company Registration Number')
    member_number = fields.Integer('Member Number')
    main_branch = fields.Text('Main branch')
    accountant_details = fields.Text('Accountant Details')
    tax_confirmation = fields.Char('Tax Confirmation Received')
    solicitor_details = fields.Text('Solicitor Details')
    business_drawing = fields.Monetary(string="Bussiness Drawing",currency_field='company_currency_id')

    business_relationship = fields.Many2many('res.partner',string='Business Relationship',help='Select the Business relationship')

    interest_rate = fields.Many2one('business.interest.rate',string='Interest Rate',domain="[('active', '=', True)]",help="Select the interest rate.")
    loan_amount = fields.Integer('Loan Amount',default=1)
    loan_term = fields.Float('Loan Term',related='interest_rate.loan_term',help='Enter the loan term.')
    repayment_frequency = fields.Integer('Repayment Frequency',default=1,related='interest_rate.repayment_frequency') 
    start_date = fields.Date('Start Date',default=fields.Date.today)
    repayment_amount =fields.Float(string="Repayment Amount",)
    stressed_repayment = fields.Float(string="Stressed Repayment",)

    lending_date = fields.Date('Lending Pack Date',copy=False,help='This field is set automatically when application enters into lending state',readonly=True)
    is_lending_return = fields.Boolean('Is lending pack return', default=False,copy=False,)

    meeting_date = fields.Datetime('Meeting Date',copy=False,help='After the user moves the application to the initial meeting stage,the user needs to specify the date on which the Initial Meeting will take place.',default=fields.Date.today)

    business_asset_ids = fields.One2many('business.assets','business_application_id',string="Add Business Assets",copy=False,help='Add the business assets for the selected business borrower.')

    new_loan_Balance = fields.Float('New Loan Balance',default=0)
    new_loan_limit = fields.Float('New Loan Limit',default=0)
    new_loan_repayment = fields.Float('New Loan Repayment',default=0)

    existing_loans_Balance = fields.Float('Existing Loans Balance',default=0)
    existing_loans_limit = fields.Float('Existing Loans Limit',default=0)
    existing_loans_repayment = fields.Float('Existing Loans Repayment',default=0)

    non_credit_union_Balance = fields.Float('Non Credit Union Balance',default=0)
    non_credit_union_limit = fields.Float('Non Credit Union Limit',default=0)
    non_credit_union_repayment = fields.Float('Non Credit Union Repayment',default=0)

    connected_Balance = fields.Float('Connected Balance',default=0)
    connected_limit = fields.Float('Connected Limit',default=0)
    connected_repayment = fields.Float('Connected Repayment',default=0)

    guarantors_Balance = fields.Float('Guarantors Balance',default=0)
    guarantors_limit = fields.Float('Guarantors Limit',default=0)
    guarantors_repayment = fields.Float('Guarantors Repayment',default=0)

    total_Balance = fields.Float('Total Balance',readonly=True,compute='_compute_borrow_total')
    total_limit = fields.Float('Total Limit',readonly=True,compute='_compute_borrow_total')
    total_repayment = fields.Float('Total Repayment',readonly=True,compute='_compute_borrow_total')

    cost_property = fields.Float('Costs of Property',default=0)
    legal_fees = fields.Float('Legal Fees',default=0)
    stamp_duty = fields.Float('Stamp Duty',default=0)
    other_costs = fields.Float('Other Costs',default=0)

    loan = fields.Float('Loan',default=0)
    own_funds = fields.Float('Own Funds',default=0)
    gift = fields.Float('Gift',default=0)
    other_funding = fields.Float('Other Funding',default=0)

    total_costs = fields.Float('Total Costs',readonly=True,compute='_compute_costs')
    total_funding = fields.Float('Total Funding',readonly=True,compute='_compute_costs')


    # profile_borrower = fields.Text('Profile of borrower',help='Profile of Borrower')
    background_business  = fields.Text('Background/lenght of time in business',help='Background/lenght of time in business')
    qualication_experience = fields.Text('Qualication/Experience',help='Qualication/Experience.')
    reference_connection = fields.Text('Make reference to connections/relation',help='Make reference to connections/relation.')
    long_borrower = fields.Text('How long borrower is a member',help='How long borrower is a member')

    # proposal = fields.Text('Proposal',help='Proposal')
    amount_purpose  = fields.Text('Amount sought for which purpose',help='Amount sought for which purpose')
    illustration_loan = fields.Text('illustration of loan,including term.',help='illustration of loan,including term.')
    connected_borrowing = fields.Text('Total connected borrowing',help='Total connected borrowing.')


    # Highlight exceptions to policy
    rule_1_boolean = fields.Boolean('Financial Information',default=False)
    rule_1_text = fields.Text('Financial Information details',help='Enter about the Financial Information.')

    rule_2_boolean = fields.Boolean('Tax',default=False)
    rule_2_text = fields.Text('Tax details',help='Enter about the Tax.')

    rule_3_boolean = fields.Boolean('Repayment Capacity',default=False)
    rule_3_text = fields.Text('Repayment Capacity details',help='Enter about the Repayment Capacity.')

    rule_4_boolean = fields.Boolean('Stress Testing',default=False)
    rule_4_text = fields.Text('Stress Testing details',help='Enter about the Stress Testing.')

    rule_5_boolean = fields.Boolean('Credit Check',default=False)
    rule_5_text = fields.Text('Credit Check details',help='Enter about the Credit Check.')

    rule_6_boolean = fields.Boolean('Experience',default=False)
    rule_6_text = fields.Text('Experience details',help='Enter about the Experience.')

    rule_7_boolean = fields.Boolean('Term',default=False)
    rule_7_text = fields.Text('Term details',help='Enter about the Term.')

    rule_8_boolean = fields.Boolean('To Purchase & refurbish/extend a business premises for own use',default=False)
    rule_8_text = fields.Text('To Purchase & refurbish/extend a business premises for own use details',help='Enter about the To Purchase & refurbish/extend a business premises for own use.')

    rule_9_boolean = fields.Boolean('Security',default=False)
    rule_9_text = fields.Text('Security details',help='Enter about the Security.')

    rule_10_boolean = fields.Boolean('Status of Member',default=False)
    rule_10_text = fields.Text('Status of Member details',help='Enter about the Status of Member.')

    rule_11_boolean = fields.Boolean('Conditions/Covenants',default=False)
    rule_11_text = fields.Text('Conditions/Covenants details',help='Enter about the Conditions/Covenants.')

    info_received_date = fields.Date('Info Received Date',copy=False,help='This field is set automatically when application enters into Info Received State',readonly=True)

    application_checklist_ids = fields.One2many('business.application.checklist','business_application_id',copy=False,string='Application Checklist',help='Add the checklist for the application.')

    acknowledgment_letter_send = fields.Boolean('Is Acknowledgment Template Letter sent',default=False,help='Please Check this field true when ')

    business_account_ids = fields.One2many('business.account','business_application_id',copy=False,string='Business Account Info',help='Add the business account info for the application.')

    uploaded_business_document = fields.One2many('business.related.document','business_application_id', string="Document Business Related Upload", copy=False)

    uploaded_relationship_document = fields.One2many('relationship.related.document','business_application_id', string="Document Relationship Related Upload", copy=False)


    assessor_id = fields.Many2one('res.partner','Responsible Assessor',copy=False,help='The user who is handling the application currently',domain=[('is_borrower','=',False),('is_relationship','=',False)],tracking=1)

    assessor_cover_note = fields.Html('Cover Note',translate=html_translate,help='Cover note')

    decision_group_id = fields.Many2one('decision.group',string='Decision-Making Group',copy=False,)
    decision_cover_note = fields.Html('Decision Note',translate=html_translate,help='Decision note')


    @api.constrains('decision_group_id')
    def _on_change_decision_group(self):
        if self.decision_group_id:
            for user in self.decision_group_id.user_ids:

                template = user.env.ref('business_lending_application.email_template_edi_decision_group_notify')
                assert template._name == 'mail.template'

                if not user.email:
                    raise UserError(_("Cannot send email: user %s has no email address.", user.name))
                if template:
                    email_values = {'email_to': user.email,}
                    template.sudo().with_context(user= user).send_mail(self.id, email_values=email_values,force_send=True, raise_exception=True,notif_layout='mail.mail_notification_light')


    @api.depends('new_loan_Balance','new_loan_limit','new_loan_repayment','existing_loans_Balance','existing_loans_limit','existing_loans_repayment','non_credit_union_Balance','non_credit_union_limit','non_credit_union_repayment','connected_Balance','connected_limit','connected_repayment','guarantors_Balance','guarantors_limit','guarantors_repayment')
    def _compute_borrow_total(self):
        self.total_Balance = self.new_loan_Balance + self.existing_loans_Balance + self.non_credit_union_Balance + self.guarantors_Balance + self.connected_Balance
        self.total_limit = self.new_loan_limit + self.existing_loans_limit + self.non_credit_union_limit + self.guarantors_limit + self.connected_limit
        self.total_repayment = self.new_loan_repayment + self.existing_loans_repayment + self.non_credit_union_repayment + self.guarantors_repayment + self.connected_repayment


    @api.depends('cost_property','legal_fees','stamp_duty','other_costs','loan','own_funds','gift','other_funding')
    def _compute_costs(self):
        self.total_costs = self.cost_property + self.legal_fees + self.stamp_duty + self.other_costs
        self.total_funding = self.loan + self.own_funds + self.gift + self.other_funding


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'enquire_date' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['enquire_date']))
            vals['name'] = self.env['ir.sequence'].next_by_code('business.application',sequence_date=seq_date) or _('New')

        result = super(BusinessApplication, self).create(vals)
        return result


    def action_lending_pack(self):
        self.write({
            'state': 'lending_sent',
            'lending_date': fields.Date.context_today(self),
        })
        return True


    def action_initial_meeting(self):
        self.write({
            'state':'internal_meet',
            'meeting_date': fields.Date.context_today(self),
        })
        return True


    def action_info_received(self):
        self.write({
            'state': 'info_received',
            'info_received_date': fields.Date.context_today(self),
        })
        return True


    def action_close(self):
        view = self.env.ref('business_lending_application.view_business_close')
        return {
            'name': _('Business Application Closing Reason'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'business.application.close',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': dict(self.env.context,default_bussiness_application_id= self.id),
        }
    

    def action_finanical_account(self):
        self.write({
            'state': 'financial_account',
        })
        return True


    def action_approve(self):
        view = self.env.ref('business_lending_application.view_business_message')
        message_id = self.env['business.message'].create({'message': _("Are you sure want to move in approve state.")})
        return {
            'name': _('Business Application Confirmation Message'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'business.message',
            'res_id': message_id.id,
            'target': 'new',
            'context': dict(self.env.context),
        }
        

    def _send_lending_pack_followup(self):
        '''
            If the Lending Pack has not been returned within seven days from the time the application has moved to the Lending Pack stage we need to send an email to the owner of the application to follow up.
        '''
        self = self.search([('is_lending_return','=',False)])
        for record in self:
            if record.lending_date:
                days_diff = fields.Date.context_today(record) - record.lending_date
                if not record.is_lending_return and days_diff.days>=7:    
                    # code for send email followup
                    template = record.env.ref('business_lending_application.email_template_edi_lending_pack')
                    assert template._name == 'mail.template'

                    user = record.create_uid
                    if not user.email:
                        raise UserError(_("Cannot send email: user %s has no email address.", user.name))
                    template.send_mail(record.id, force_send=True, raise_exception=True,notif_layout='mail.mail_notification_light')
                    _logger.info("Lending pack follow up email sent for user <%s> to <%s>", user.login, user.email)


    def _send_approval_pending_notify(self):
        '''
        if 14 days have passed from the time the application reached the Info Received stage and the application is still not Approved (or declined), notify by an email notification the owner(user) that the application requires approval, and it’s late.
        '''
        self = self.search([('state','in',['approved'])])
        for record in self:
            if record.info_received_date:
                days_diff = fields.Date.context_today(record) - record.info_received_date
                if days_diff.days>=14:
                    template = record.env.ref('business_lending_application.email_template_edi_approval_pending_notify')
                    assert template._name == 'mail.template'

                    user = record.create_uid
                    if not user.email:
                        raise UserError(_("Cannot send email: user %s has no email address.", user.name))
                    template.send_mail(record.id, force_send=True, raise_exception=True,notif_layout='mail.mail_notification_light')
                    _logger.info("All Info Received follow up email sent for user <%s> to <%s>", user.login, user.email)


    def _send_info_received_followup(self):
        '''
        Measure 7 days from the date of the initial meeting and send an email notification to the user to contact the business borrower if there was no decision either to close the application or to move forward.
        '''
        self = self.search([('state','in',['info_received'])])
        for record in self:
            if record.meeting_date:
                days_diff = fields.Date.context_today(record) - record.meeting_date
                if days_diff.days>=7:
                    template = record.env.ref('business_lending_application.email_template_edi_info_received')
                    assert template._name == 'mail.template'

                    user = record.create_uid
                    if not user.email:
                        raise UserError(_("Cannot send email: user %s has no email address.", user.name))
                    template.send_mail(record.id, force_send=True, raise_exception=True,notif_layout='mail.mail_notification_light')
                    _logger.info("All Info Received follow up email sent for user <%s> to <%s>", user.login, user.email)

        self._send_approval_pending_notify()


    def _send_acknowledging_application(self):
        '''
        An email will be sent four days after info received to the user to prompt him to print the Template Letter of Acknowledging Application.
        '''
        self = self.search([('state','in',['info_received']),('acknowledgment_letter_send','=',False)])
        for record in self:
            if record.info_received_date:
                days_diff = fields.Date.context_today(record) - record.info_received_date
                if days_diff.days>=4:
                    template = record.env.ref('business_lending_application.email_template_edi_acknowledging_application')
                    assert template._name == 'mail.template'

                    user = record.create_uid
                    if not user.email:
                        raise UserError(_("Cannot send email: user %s has no email address.", user.name))
                    template.send_mail(record.id, force_send=True, raise_exception=True,notif_layout='mail.mail_notification_light')
                    _logger.info("Acknowledge Application follow up email sent for user <%s> to <%s>", user.login, user.email)


    def copy_assets(self):
        records = self.search([('business_borrower','=',self.business_borrower.id),('id','!=',self.id),('create_date','<=',self.create_date)],order='write_date')
        if records:
            for asset in records[0].business_asset_ids:
                vals = asset.read()[0]
                vals.update({
                    'business_application_id': self.id,
                    'business_borrower': self.business_borrower.id,
                })
                self.business_asset_ids = [(0, 0, vals)]
        return True

    
    def copy_business_account(self):
        records = self.search([('business_borrower','=',self.business_borrower.id),('id','!=',self.id),('create_date','<=',self.create_date)],order='write_date')
        if records:
            for business_account in records[0].business_account_ids:
                vals = business_account.read()[0]
                vals.update({
                    'business_application_id': self.id,
                })
                self.business_asset_ids = [(0, 0, vals)]
        return True

    
    def print_financial_account(self):
        for rec in self:
            # _logger.critical(f'======11111111========={rec.business_account_ids._fields["period_end"].read()}')
            # asdasd
            return rec.env.ref('business_lending_application.business_application_accounting_detail').report_action(rec)

    @api.onchange('business_borrower')
    def _on_change_business_borrower(self):
        for application in self:
            application.entity = application.business_borrower.entity
            application.contact_person = application.business_borrower.contact_person
            application.business_sector = application.business_borrower.business_sector
            application.no_employees = application.business_borrower.no_employees
            application.business_year = application.business_borrower.business_year
            application.business_premises = application.business_borrower.business_premises
            application.company_reg_no = application.business_borrower.company_reg_no
            application.member_number = application.business_borrower.member_number
            application.main_branch = application.business_borrower.main_branch
            application.accountant_details = application.business_borrower.accountant_details
            application.tax_confirmation = application.business_borrower.tax_confirmation
            application.solicitor_details = application.business_borrower.solicitor_details
            application.business_drawing = application.business_borrower.business_drawing


    def action_cover_note(self):
        pass


    def action_assign_assessor(self):
        self.ensure_one()
        template_id = self.env.ref('business_lending_application.email_template_edi_assessor_notify').id
        ctx = {
            'default_model': 'business.application',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': 'mail.mail_notification_light',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }