# -*- coding: utf-8 -*-
from dis import show_code
from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import json
import logging
_logger = logging.getLogger(__name__)


class Edit_Contacts(models.Model):
      _inherit = 'res.partner'
      title_ar = fields.Char(string='Arabic Title')
      cr_number = fields.Char(string='Company Registration Number')
      google_maps_coordinates = fields.Char()
      cr_file = fields.Binary(
          string='Company Registration File', attachment=True)
      tax_cert = fields.Binary(string='Tax Certificate', attachment=True)
      contact_company_type = fields.Selection(
          [('vendor', 'Vendor'), ('contact', 'Contact'), ('customer', 'Customer')], string='Company Type')
      bank_reference = fields.Char(string='Bank Reference', store=True)
      hide_bank_reference = fields.Boolean(default=False, company_dependent=True)
      creating_owner_id = fields.Many2one('res.users', 'Owner', default=lambda self: self.env.user)

      # give the sales manager the access to modify the payment terms
      @api.model
      def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
            context = self._context or {}
            res = super(Edit_Contacts, self).fields_view_get(
                view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)     
            if not self.env.user.has_group('sales_team.group_sale_manager'):
                doc = etree.XML(res['arch'])
                _logger.info('view_type %s', view_type)
                if view_type == 'tree':
                    for node in doc.xpath("//tree[@string='Contacts']"):
                        node.set('create', '0')
                elif view_type == 'kanban':
                    for node in doc.xpath("//kanban[@class='o_res_partner_kanban']"):
                        node.set('create', '0')
                elif view_type == 'form':
                    for node in doc.xpath("//form[@string='Partners']"):
                        node.set('create', '0')
                        node.set('edit', '0')
                for node in doc.xpath("//field[@name='property_payment_term_id']"):
                    node.set("readonly", "1")
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='property_supplier_payment_term_id']"):
                    node.set("readonly", "1")
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
                res['arch'] = etree.tostring(doc)
            return res   

      @api.onchange('title_ar')
      def on_change_title_ar(self):
            if self.title_ar:
                return {'value': {'name_arabic': self.title_ar}}
            else:
                return  

      @api.onchange('property_payment_method_id')
      def on_change_property_payment_method_id(self):
            if self.property_payment_method_id.name == 'Wired Transfer':
                self.hide_bank_reference = True
                # return {'value': {'hide_bank_reference': True}}
            else:
                self.hide_bank_reference = False  

      @api.constrains('name')
      def _check_user_permissions(self):
            employee = self.env['hr.employee'].sudo().search(
              [('user_id', '=', self.env.user.id)], limit=1)
            position = self.env['hr.job'].sudo().search(
              [('id', '=', employee.job_id.id)], limit=1)
            user = self.env['res.users'].sudo().search(
              [('id', '=', self.env.user.id)], limit=1)
            # _logger.info('self_creating_owner_id %s', self.creating_owner_id)
            # _logger.info('self_env_id %s', self.env.user.id)
            # _logger.info('position internal_id %s', position.internal_id)
            # _logger.info('has_group group_sale_manager %s', user.has_group('sales_team.group_sale_manager'))
            # _logger.info('has_group group_user %s', user.has_group('base.group_user'))

            if self.creating_owner_id.id != self.env.user.id and not user.has_group('sales_team.group_sale_manager'):
                raise ValidationError(
                    _('Creating or Editng contact is limited to managers or administrators')
                )   
            else:
                return