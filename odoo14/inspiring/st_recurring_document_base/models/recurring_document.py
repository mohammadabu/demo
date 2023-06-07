from odoo import models, fields, api, _
from odoo.tools import safe_eval
from dateutil.relativedelta import relativedelta
from lxml import etree
from ast import literal_eval


class RecurringDocument(models.AbstractModel):
    _name = 'recurring.document'
    _description = 'Recurring Documents'
    
    subscription_ids = fields.One2many(
        'recurring.document.subscription',
        'res_id',
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True
        )
    history_subscription_id = fields.Many2one('recurring.document.subscription','Triggering Subscription',compute='_compute_history_subscription_id')
    
    def _compute_history_subscription_id(self):
        for record in self:
            document_ref = '%s,%s' % (record._name, record.id or 0),
            history = self.env['recurring.document.history'].search([('document_ref','=',document_ref)],limit=1)
            subscription_id = history.subscription_id.id
            record.history_subscription_id=subscription_id
            
    def unlink(self):
        history_obj = self.env['recurring.document.history']
        history_lines = self.env['recurring.document.history']
        for record in self.filtered(lambda r:r.subscription_ids or r.history_subscription_id):
            document_ref = '%s,%s' % (record._name, record.id or 0),
            history_lines |= history_obj.search([('document_ref','=',document_ref)])
        result = super().unlink()
        if history_lines:
            history_lines.write({
                'document_ref':None,
                'document_deleted':True,
                })
        return result
        
        
    
    def button_recurring_document(self):
        self.ensure_one()
        action = self.env.ref('st_recurring_document_base.act_open_recurring_document_subscription_view').read()[0]
        action['context'] = {
            'default_res_id':self.id,
            'default_model': self._name,
            'default_name': '%s - %s' % (self._name, self.display_name),
            'default_date_init': self._get_default_recurring_date_init(),
            'search_default_res_id': self.id,
            'search_default_model': self._name,
            }
        return action
        
    def _get_default_recurring_date_init(self):
#         if hasattr(self.env[self._name], '_get_default_recurring_date_init'):
#             return self.env[self._name]._get_default_recurring_date_init()
        return fields.Date.today()+relativedelta(month=1)
    
    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(RecurringDocument, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            form = doc.xpath('//form')[0]
            sheet = form.find('sheet')
            button_box = form.xpath("//div[@name='button_box']")
            button_box = button_box and button_box[0]
            fa_icon = 'fa-repeat'
            smart_button = '''
                <button class="oe_stat_button" name="button_recurring_document"
                        type="object" icon="%s" help="Recurring Subscription">
                        <div class="o_field_widget o_stat_info">
                            <span class="o_stat_value">
                            </span>
                            <span class="o_stat_text">%s</span>
                        </div>
                    </button>
                ''' % (fa_icon,_('Recurring'))
            if not button_box:
                smart_button = '''<div class="oe_button_box" name="button_box">%s</div>''' % smart_button
                sheet.insert(0,etree.fromstring(smart_button))
            else:
                button_box.insert(0,etree.fromstring(smart_button))
            res['arch'] = etree.tostring(doc, encoding='unicode')
            config = self.env['recurring.document.config'].search([('model_id.model', '=', self._name)], limit=1)
            button_filter_domain = config and literal_eval(config.button_filter_domain) or None
            if button_filter_domain:
                doc = etree.XML(res['arch'])
                recurring_button = doc.xpath("//div[@name='button_box']")
                recurring_button = recurring_button and recurring_button[0]
                if recurring_button:
                    recurring_button.set('attrs', "{'invisible':%s}" % button_filter_domain)
                res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    
