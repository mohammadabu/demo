# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Product(models.Model):
    _inherit = "product.product"

    sample_qty = fields.Float('Sample Qty', compute='calculate_sample_quants')

    def calculate_sample_quants(self):
        """ This method get sample quantity. """
        samples = self.stock_quant_ids.filtered(lambda stock: stock.location_id.filtered(lambda loc: loc.is_sample_location))
        self.sample_qty = sum(samples.mapped('quantity'))
        
    def action_open_sample_quants(self):
        """ Fetch sample product quantity"""
        samples = self.stock_quant_ids.filtered(lambda stock: stock.location_id.filtered(lambda loc: loc.is_sample_location))
        domain = [('id', 'in', samples.ids)]
        action = self.env['stock.quant']._get_quants_action(domain)
        action['name'] = _('Sample Qty')
        return action


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sample_qty = fields.Float('Sample Qty', compute='calculate_sample_quants')

    def calculate_sample_quants(self):
        """ This method get sample quantity. """
        samples = self.product_variant_ids.stock_quant_ids.filtered(lambda stock: stock.location_id.filtered(lambda loc: loc.is_sample_location))
        self.sample_qty = sum(samples.mapped('quantity'))
        
    def action_open_sample_quants(self):
        """ Fetch sample product quantity"""
        return self.product_variant_ids.action_open_sample_quants()