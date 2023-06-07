# -*- coding: utf-8 -*-
# from odoo import http


# class OpCreditLimit(http.Controller):
#     @http.route('/op_credit_limit/op_credit_limit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/op_credit_limit/op_credit_limit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('op_credit_limit.listing', {
#             'root': '/op_credit_limit/op_credit_limit',
#             'objects': http.request.env['op_credit_limit.op_credit_limit'].search([]),
#         })

#     @http.route('/op_credit_limit/op_credit_limit/objects/<model("op_credit_limit.op_credit_limit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('op_credit_limit.object', {
#             'object': obj
#         })
