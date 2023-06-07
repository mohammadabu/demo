from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class RecurringDocumentSubscription(models.Model):
    _name = 'recurring.document.subscription'
    _description = 'Recurring Document Subscriptions'
    
    name = fields.Char(required=True)
    active = fields.Boolean(help="If the active field is set to False, it will allow you to hide the subscription without removing it.", default=True)
    notes = fields.Text(string='Internal Notes')
    interval_number = fields.Integer(string='Interval Qty', default=1)
    interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], string='Interval Unit', default='months', required=True)
    model = fields.Char('Related Document Model', index=True)
    model_id = fields.Many2one('ir.model', 'Model Ref', compute='_compute_model_id', store=True, compute_sudo=True)
    res_id = fields.Integer('Related Document ID', index=True)
    next_date = fields.Datetime(string='Next Date', default=fields.Datetime.now)
    numbercall = fields.Integer('Number of Calls', help='Zero or lower is always')
    default_field_ids = fields.One2many('recurring.document.field', 'subscription_id', 'Default Values')
    server_action_ids = fields.Many2many('ir.actions.server', string='Server Actions')
    history_line_ids = fields.One2many('recurring.document.history', 'subscription_id', string='Documents created', readonly=True)

    @api.depends('model')
    def _compute_model_id(self):
        models = self.env['ir.model'].search([('model', 'in', self.mapped('model'))])
        for subscription in self:
            subscription.model_id = models.filtered(lambda r:r.model == subscription.model).id
    
    @api.constrains('model', 'res_id')
    def _check_unique_subscription(self):
        if self.search_count([('model', '=', self.model), ('res_id', '=', self.res_id), ('id', '!=', self.id)]):
            raise ValidationError(_('Per Document only 1 Recurring Subscription!'))
    
    @api.model
    def _cron_generate_recurring_documents(self):
        to_handle_subscriptions = self.search([('next_date','<=',fields.Datetime.now())])
        return to_handle_subscriptions._create_recurring_documents()
    
    def _create_recurring_documents(self):
        history_obj = self.env['recurring.document.history']
        server_action_obj = self.env['ir.actions.server']
        for subscription in self:
            record = self.env[subscription.model].browse(subscription.res_id)
            default = subscription._get_default_vals()
            new_record = record.copy(default=default)
            history_obj.create({
                'document_ref':'%s,%s' % (new_record._name, new_record.id or 0),
                'subscription_id':subscription.id,
                })
            message = _("This Document has been created from the Recurring Document Subscription: <a href=# data-oe-model=recurring.document.subscription data-oe-id=%d>%s</a>") % (subscription.id, subscription.name)
            new_record.message_post(body=message)
            server_actions = subscription.server_action_ids
            if server_actions:
                server_actions.with_context(
                    active_model=subscription.model,
                    active_ids=new_record.ids,
                    active_id=new_record.id).run()
            next_date = subscription.next_date + relativedelta(**{subscription.interval_type:subscription.interval_number})
            vals = {
                'next_date':next_date,
                }
            if subscription.numbercall != 0:
                numbercall = subscription.numbercall - 1
                vals['numbercall'] = numbercall
                if not numbercall:
                    vals['active'] = False
            subscription.write(vals)
        
            
    def _get_default_vals(self):
        default = {}
        for field_line in self.default_field_ids.filtered(lambda r:r.value):
            new_value = field_line.value == 'date' and fields.Date.to_string(fields.Date.today()) or False
            default[field_line.field.name] = new_value
        return default
            
            
