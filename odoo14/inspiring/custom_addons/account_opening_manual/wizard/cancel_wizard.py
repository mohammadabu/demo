# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models



class PartnerAccountCancel(models.TransientModel):
    _name = 'partner.account.cancel'
    _description = 'Partner Account Entry Cancel'


    receivable = fields.Boolean(
        string='Receivable',
    )
    payble = fields.Boolean(
        string='Payable',
    )
    bandc = fields.Boolean(
        string='Bank & Cash',
    )


    def cancel_entry(self):
        partner_id = self.env['partner.account'].search([('id','=',self.env.context.get('active_id'))])
        if partner_id.state == 'posted':
            if self.receivable:
                unlink_account_move_ids = partner_id.account_move_ids.filtered(lambda r : r.account_id.internal_type == 'receivable')
                for unlink_account_move_id in unlink_account_move_ids.ids:
                    # self.env.cr.execute('delete from account_move where id = %(id)s',{'id' : unlink_account_move_id.id})
                    # unlink_account_move_id.unlink()
                    d_id = self.env['account.move'].search([('id', '=', unlink_account_move_id)])
                    d_id.write({'posted_before' : False, 'state' : 'draft'})
                    d_id.unlink()

            if self.payble:
                unlink_account_move_ids = partner_id.account_move_ids.filtered(lambda r : r.account_id.internal_type == 'payable')
                for unlink_account_move_id in unlink_account_move_ids.ids:
                    d_id = self.env['account.move'].search([('id', '=', unlink_account_move_id)])
                    d_id.write({'posted_before' : False, 'state' : 'draft'})
                    d_id.unlink()

            if self.bandc:
                unlink_account_move_ids = partner_id.account_move_ids.filtered(lambda r : r.account_id.internal_type == 'liquidity' and r.account_id.internal_group == 'asset')
                print('----------------------- this is bank account move for test : ',unlink_account_move_ids)
                for unlink_account_move_id in unlink_account_move_ids.ids:
                    d_id = self.env['account.move'].search([('id', '=', unlink_account_move_id)])
                    d_id.write({'posted_before' : False, 'state' : 'draft'})
                    d_id.unlink()

            if not partner_id.account_move_ids:
                partner_id.write({'state' : 'draft'})

        if partner_id.state == 'done':
            if self.receivable:
                unlink_account_move_ids = partner_id.account_move_ids.filtered(lambda r : r.account_id.internal_type == 'receivable')
                for unlink_account_move_id in unlink_account_move_ids.ids:
                    d_id = self.env['account.move'].search([('id', '=', unlink_account_move_id)])
                    d_id.write({'posted_before' : False, 'state' : 'draft'})
                    d_id.unlink()
                    # self.env.cr.execute('delete from account_move where id = %(id)s',{'id' : unlink_account_move_id.id})

            if self.payble:
                unlink_account_move_ids = partner_id.account_move_ids.filtered(lambda r : r.account_id.internal_type == 'payable')
                for unlink_account_move_id in unlink_account_move_ids.ids:
                    d_id = self.env['account.move'].search([('id', '=', unlink_account_move_id)])
                    d_id.write({'posted_before' : False, 'state' : 'draft'})
                    d_id.unlink()

            if self.bandc:
                unlink_account_move_ids = partner_id.account_move_ids.filtered(lambda r : r.account_id.internal_type == 'liquidity' and r.account_id.internal_group == 'asset')
                for unlink_account_move_id in unlink_account_move_ids.ids:
                    d_id = self.env['account.move'].search([('id', '=', unlink_account_move_id)])
                    d_id.write({'posted_before' : False, 'state' : 'draft'})
                    d_id.unlink()

            if not partner_id.account_move_ids:
                partner_id.write({'state' : 'draft'})