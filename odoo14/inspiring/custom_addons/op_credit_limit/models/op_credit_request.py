# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.
#      Copying is not allowed.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class CreditRequest(models.Model):
    _name = 'credit.request'
    _description = 'Credit Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='الكود', required=True,
                       copy=False, readonly=True, default='New')
    date_request = fields.Date(
        string='التاريخ', default=fields.Date.context_today, required=True)
    partner_id = fields.Many2one(
        'res.partner', string='العميل', required=True, tracking=True)
    partner_cr = fields.Char(related='partner_id.cr', string='السجل التجاري', )
    partner_phone = fields.Char(
        related='partner_id.phone', string='التليفون', )
    partner_vat = fields.Char(related='partner_id.vat',
                              string='الرقم الضريبي', )
    partner_address_1 = fields.Char(
        related='partner_id.street', string='العنوان', )
    partner_new_old = fields.Selection(
        [('new', 'عميل جديد'), ('old', 'عميل سابق')], string='عمل سابق ام جديد؟', default='new')
    partner_type = fields.Selection([('individual', 'مؤسسة فردية'), ('jv', 'شركة تضامن'), (
        'lc', 'ذات مسؤولية محدودة'), ('sh', 'مساهمة')], string='نوع الشركة',)
    partner_official_location = fields.Char(string='مركز الشركة التجاري', )
    partner_official_activity = fields.Char(string='نشاط الشركة التجاري', )

    # for company use
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", default=lambda self: self.env.user.company_id.id,
        readonly=True)
    user_id = fields.Many2one(
        'res.users', 'المستخدم', default=lambda self: self.env.user, readonly= True)
    # for employee use
    employee_id = fields.Many2one(
        'hr.employee', string='المندوب', required=True, tracking=True)
    employee_no = fields.Char(
        related='employee_id.employee_no', string='الرقم الوظيفي',)
    employee_department = fields.Many2one(
        related='employee_id.department_id', string='فرع', readonly=True)
    # country
    country_id = fields.Many2one('res.country', string='الدولة', required=True,
                                 tracking=True, default=lambda self: self.env.user.company_id.country_id.id)
    # state
    state_id = fields.Many2one('res.country.state', string='المنطقة', required=True,
                               tracking=True, domain="[('country_id', '=', country_id)]")
    # emp

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id:
            self.state_id = False
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}

    credit_limit = fields.Float(
        string='قيمة التسهيلات المطلوبة', tracking=True, required=True,)
    credit_payment_method=fields.Char(
        string='طريقة السداد المسموح بها', required=True, tracking=True)

    credit_payment_method_other=fields.Char(
        string='طريقة السداد في حالة سحب الائتمان او توقف / تصفية الشركة', tracking=True, required=True,)

    credit_attachment_ids=fields.One2many(
        'credit.attachment', 'credit_attachment_id', string='المرفقات')

    state=fields.Selection([('draft', 'مسودة'), ('request_approval', 'ارسال الطلب للموافقة'), ('sales_m_approval', 'معتمد من مدير المبيعات'), (
        'accounting_m_approval', 'معتمد من المدير المالي'), ('legal_affairs_approval', 'معتمد من الشئون القانونية'), ('exe_m_approval', 'معتمد من المدير التنفيذي'), ('done', 'تم')], string='Status', default='draft', tracking=True)

    payment_term_id = fields.Many2one(
        'account.payment.term', string='شروط الدفع', )

    # serial
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'credit.request') or 'New'
        if vals['credit_limit'] < 1:
            raise ValidationError("Credit should be more than 0.")
        return super(CreditRequest, self).create(vals)

    def write(self, vals):
        if 'credit_limit' in vals:
            if vals['credit_limit'] < 1:
                raise ValidationError("Credit should be more than 0.")
        return super(CreditRequest, self).write(vals)

    def action_request_approval(self):
        self.state='request_approval'
        group_id = self.env.ref(
            'op_credit_limit.group_crdit_request_sales_approval').id
        summary = 'Credit request for %s needs your approval ' % self.partner_id.name
        note = 'Credit request for %s needs your approval ' % self.partner_id.name
        # self.create_activity(self, group_id, summary, note)


    def action_sales_m_approval(self):
        self.state='sales_m_approval'
        group_id = self.env.ref(
            'op_credit_limit.group_credit_request_accounting_approval').id
        summary = 'Credit request for %s needs your approval ' % self.partner_id.name
        note = 'Credit request for %s needs your approval ' % self.partner_id.name
        # self.create_activity(self, group_id, summary, note)

    def action_accounting_m_approval(self):
        self.state='accounting_m_approval'
        group_id = self.env.ref(
            'op_credit_limit.group_credit_request_legal_approval').id
        summary = 'Credit request for %s needs your approval ' % self.partner_id.name
        note = 'Credit request for %s needs your approval ' % self.partner_id.name
        # self.create_activity(self, group_id, summary, note)

    def action_legal_affairs_approval(self):
        if self.credit_limit < 100000:
            self.state='legal_affairs_approval'
            # self.state='exe_m_approval'
            self.done()
        else:
            self.state='legal_affairs_approval'
            group_id = self.env.ref(
                'op_credit_limit.group_credit_request_gm_approval').id
            summary = 'Credit request for %s needs your approval ' % self.partner_id.name
            note = 'Credit request for %s needs your approval ' % self.partner_id.name
            # self.create_activity(self, group_id, summary, note)

    def action_exe_m_approval(self):

        if self.credit_limit > 100000:
            self.state='exe_m_approval'
            self.done()

        else:
            self.done()


    def done(self):
        self.state='done'
        res=self.env['res.partner'].search(
            [('id', '=', self.partner_id.id)])
        res['set_credit_limit'] = True
        res['credit_limit']=self.credit_limit
        self.make_activity_done(self)


    @api.model
    def create_activity(self, res_model, group_id, summary, note):
       activity_to_do = self.env.ref('mail.mail_activity_data_todo').id
       res_group = self.env['res.groups'].search([('id', 'in', [group_id])])
       model_id = self.env['ir.model']._get('credit.request').id
       summary = summary
       note = note
       for group in res_group:
           for user in group.users:
               values = {
                   'activity_type_id': activity_to_do,
                   'user_id': user.id,
                   'res_id': res_model,
                   'res_model_id': model_id,
                   'summary': summary,
                   'automated': True,
                   'note': note,
               }
               self.env['mail.activity'].create(values)

    def make_activity_done(self, res_id):
        res = self.env['mail.activity'].search(
            [('res_id', 'in', res_id.ids), ('res_model', '=', self._name), ])
        for act in res:
            act.sudo()._action_done()

    def print_credit_request_report(self):
        data = {}
        data['atids'] = self.ids
        _logger.info('self.ids %s', self.ids)
        return self.env.ref('op_credit_limit.credit_request_action_2').report_action(self, data=data)

    owner_ids=fields.One2many(
        'company_owner', 'owner_id', string='اسم وعنوان المالك / الشركاء')
    bank_ids=fields.One2many(
        'banks', 'bank_id', string='تفاصيل البنوك المتعامل معها')

    comref_ids=fields.One2many(
        'com_ref', 'comref_id', string='المراجع التجارية')
    mofawad_ids=fields.One2many(
        'mofawad', 'mofawad_id', string='الاشخاص المفوضين لطلب واستلام البضاعة')

    is_another_person_in_company=fields.Boolean(
        string='أو أي شخص تحت الكفالة', default=False)

    other_gurantees=fields.Selection(
        [('checks', 'شيكات'), ('rec', 'ايصالات')], string='ضمانات اخري')


class Mofawad(models.Model):
    _name='mofawad'

    name=fields.Char(string='الاسم', )
    job=fields.Char(string='المنصب', )
    phone=fields.Char(string=' الهاتف', )
    # signature = fields.Char(string='التوقيع', )

    mofawad_id=fields.Many2one(
        'credit.request',)


class ComRef(models.Model):
    _name='com_ref'

    name=fields.Char(string='اسم المؤسسة / الشركة', )
    phone=fields.Char(string='الهاتف', )
    address=fields.Char(string='العنوان', )

    comref_id=fields.Many2one(
        'credit.request',)


class BankDetails(models.Model):
    _name='banks'

    name=fields.Char(string='البنك', )
    branch=fields.Char(string='الفرع', )
    acc=fields.Char(string='رقم الحساب', )

    bank_id=fields.Many2one(
        'credit.request',)


class CompanyOwner(models.Model):
    _name='company_owner'


    name=fields.Char(string='الاسم', )
    desc=fields.Char(string='الصفة', )
    phone=fields.Char(string='رقم الهاتف', )
    address=fields.Char(string='العنوان', )

    owner_id=fields.Many2one(
        'credit.request',)



class CreditAttachment(models.Model):
    _name='credit.attachment'
    _description='Credit Attachment'
    _inherit=['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name=fields.Many2one('credit.attachment.list',
                         string='الاسم', required=True)
    attachment_id=fields.Binary(string='المرفق', )
    credit_attachment_id=fields.Many2one(
        'credit.request', string='Credit Request', required=True)

class CreditAttachmentList(models.Model):
    _name='credit.attachment.list'
    _description='Credit Attachment List'
    _inherit=['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name=fields.Char(string='Name', )
