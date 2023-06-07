 # -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReportAccountAgedbalanceNewPrint(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_aged_balance_print'

    # def get_project_info(self, docs):
    #     rec = ''
    #     if len(docs.stages) > 0 :
    #         arr = []
    #         for stage in docs.stages:
    #             arr.append(stage.id)    
    #         rec = self.env['project.project'].sudo().search([('active','=',1),('project_stage','in',arr)])
    #     else:
    #         rec = self.env['project.project'].sudo().search([('active','=',1)])
               

    #     records = []
    #     for r in rec: 
    #         cur = r.parent_opportunity.company_currency.name 
    #         mon = r.parent_opportunity.planned_revenue
    #         value_opportunity = ''
    #         if r.parent_opportunity.name != False:
    #             value_opportunity = str(int(mon)) + " " + str(cur)
    #         else:
    #             value_opportunity = ""
    #         vals = {
    #                 'name_seq': r.name_seq,
    #                 'name': r.name,
    #                 'stage': r.project_stage.name,
    #                 'parent_opportunity': r.parent_opportunity.name,
    #                 'value_opportunity':value_opportunity, 
    #                 'customer_name':r.parent_opportunity.partner_id.name
    #             }
    #         records.append(vals)
    #     return [records]

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.aged.trial.balance.new'].sudo().browse(self.env.context.get('active_id'))
        # project_info = self.get_project_info(docs)
        return {
            'doc_ids': self.ids,
            'docs': docs,
            # 'project_info': project_info[0],
        }