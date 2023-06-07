# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today  Technaureus Info Solutions(<http://technaureus.com/>).
from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'

    #name_arabic = fields.Char(string="Partner Arabic Name")
    street_arabic = fields.Char("Street in Arabic")
    street2_arabic = fields.Char("Street2 in Arabic")
    city_arabic = fields.Char("City in Arabic")
    state_arabic = fields.Char(string="State Arabic Name")
    zip_arabic = fields.Char("Postal Code in Arabic")
    country_arabic = fields.Char(string="Country Name Arabic")
    partner_place_supply = fields.Selection(
        [('abu_dhabi', 'Abu Dhabi'), ('ajman', 'Ajman'), ('dubai', 'Dubai'), ('fujairah', 'Fujairah'),
         ('ras_al_khaimah', 'Ras al-Khaimah'), ('sharjah', 'Sharjah'), ('umm_al_quwain', 'Umm al-Quwain')],
        string="Place of Supply")
    partner_vat_accounting = fields.Selection(related='company_id.vat_accounting')
    building_number = fields.Char("Building Number")
    district_id = fields.Many2one('res.district', "District")
    building_number_arabic = fields.Char("Building Number")
    district_id_arabic = fields.Char("District")
    additional_no = fields.Char("Additional Number")
    other_seller_id = fields.Char("Other Seller ID")
    additional_no_arabic = fields.Char("Additional Number in Arabic")
    other_seller_id_arabic = fields.Char("Other Seller ID in Arabic")
    #vat_in_arabic = fields.Char("Vat Number in Arabic")

    