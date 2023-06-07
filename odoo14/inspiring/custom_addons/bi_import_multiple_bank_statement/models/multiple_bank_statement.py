# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import io
import datetime
import tempfile
import binascii
import logging
import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
_logger = logging.getLogger(__name__)
from io import StringIO

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
try:
    import xlrd
    from xlrd import XLRDError
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class AccountMultipleBankStatementWizard(models.TransientModel):
    _name= "account.multiple.bank.statement.wizard"

    file = fields.Binary('File')
    file_opt = fields.Selection([('excel','Excel'),('csv','CSV')])


   
    def import_multiple_bank_statement(self):
        
        if not self.file:
            raise UserError('Please upload a file to import')

        if self.file_opt == 'csv':
            keys = ['name','date','journal_id','line_date','ref','partner','memo','amount','currency']                    
            data = base64.b64decode(self.file)
            try:
                file_input = io.StringIO(data.decode("utf-8"))
            except UnicodeError:
                raise UserError('File Format is not correct !!!\n Please Select CSV File')

            file_input.seek(0)
            reader_info = []
            csv_reader = csv.reader(file_input, delimiter=',')
 
            try:
                reader_info.extend(csv_reader)
            except Exception:
                raise UserError(_("Invalid file!"))
            values = {}
            for i in range(len(reader_info)):
                field = list(map(str, reader_info[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self.create_bank_statement(values)           
                        
        elif self.file_opt == 'excel':
            fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = ''
            try:
                workbook = xlrd.open_workbook(fp.name)
            except xlrd.XLRDError:
                raise UserError('File Format is not correct !!!\n Please Select XLS File')
            sheet = workbook.sheet_by_index(0)
            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(map(lambda row:isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if not line[1]:
                        raise UserError('Please Provide Date Field Value')


                                            
                    statement_date = int(float(line[1]))
                    data_tuple = xlrd.xldate_as_tuple(statement_date, workbook.datemode)
                    date_string = datetime.date(data_tuple[0], data_tuple[1], data_tuple[2])
                    if not line[3]:
                        raise UserError('Please Provide Line Date Field Value')                            
                    line_date = int(float(line[3]))
                    line_date_as_datetime = xlrd.xldate_as_tuple(line_date, workbook.datemode)
                    line_date_string = datetime.date(line_date_as_datetime[0], line_date_as_datetime[1], line_date_as_datetime[2])
                    
                    values.update({
                                    'name' : line[0],
                                    'date' : date_string,
                                    'journal_id' :  line[2],
                                    'line_date': line_date_string,
                                    'ref': line[4],
                                    'partner': line[5],
                                    'memo': line[6],
                                    'amount': line[7],
                                    'currency' : line[8],
                                    })
                    
                    res = self.create_bank_statement(values)
        else:
            raise UserError('Please Select File Type')

        return res

    
    def create_bank_statement(self,values):
        bank_statement_obj = self.env['account.bank.statement']
       
        journal_id = self._find_journal(values.get('journal_id'))
        journal = self.env['account.journal'].browse(journal_id)
        
        bank_recent_id = bank_statement_obj.search([('journal_id','=',journal.id)],order="id desc", limit=1)
        bank_statement_ids = bank_statement_obj.search([('name', '=', values.get('name'))])

        balance_start = 0.0
        if bank_recent_id:
            new_ = values.get('date')
            new_date = None
            if new_:
                if isinstance(new_,str):
                    if new_.split('/'):
                        if len(new_.split('/')) > 1 or len(new_.split('-')[0]) < 4:
                            raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                        if len(new_) > 10 or len(new_) < 5:
                            raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                    new_date = datetime.datetime.strptime(new_, DEFAULT_SERVER_DATE_FORMAT).date()
                    values.update({'date':new_date})
                    
                else:
                    new_date = values.get('date')
                    values.update({'date':new_date})
            else:
                raise UserError(_('Please Provide Date Field Value.'))

        if bank_statement_ids:    
            if bank_statement_ids.journal_id.name == journal.name:
                b = self.create_bank_statement_lines(values, bank_statement_ids)
                bank_statement_ids.write({
                    'balance_end_real' : bank_statement_ids.balance_end,
                    'date': values.get('date')

                })
                return bank_statement_ids
            else:
                raise UserError(_('Journal is different for "%s" .\n Please define same.') % values.get('journal_id'))
        else:
            if not values.get('date'):
                raise UserError(_('Please Provide Date Field Value for Bank Statement.'))
            if bank_recent_id:
                balance_start = bank_recent_id.balance_end
            new_ = values.get('date')
            new_date = None
            if new_:
                if isinstance(new_,str):
                    if new_.split('/'):
                        if len(new_.split('/')) > 1 or len(new_.split('-')[0]) <4:
                            raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                        if len(new_) > 10 or len(new_) < 5:
                            raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                    
                    new_date = datetime.datetime.strptime(new_, DEFAULT_SERVER_DATE_FORMAT).date()
                                        
                else:
                    new_date = values.get('date')
            else:
                raise UserError(_('Please Provide Date Field Value.'))    
            vals = {
                    'name' : values.get('name'),
                    'journal_id' : journal_id,
                    'date' : new_date,
                    'balance_start' : balance_start,
                }    
            bank_statement_id = bank_statement_obj.create(vals)
            
            self.create_bank_statement_lines(values, bank_statement_id)
            
        return bank_statement_id
    
    
    def create_bank_statement_lines(self,values,bank_statement_id):
        
        account_bank_statement_line_obj = self.env['account.bank.statement.line']
        partner_id = self._find_partner(values.get('partner'))
        if values.get('currency'):
            currency_id = self._find_currency(values.get('currency'))
        else:
            currency_id = False
        if not values.get('memo'):
            raise UserError('Please Provide Memo Field Value')
        if values.get('line_date'):
            new_ = values.get('line_date')
            new_date = None
            if new_:
                if isinstance(new_,str):
                    if new_.split('/'):
                        if len(new_.split('/')) > 1 or len(new_.split('-')[0]) <4:
                            raise ValidationError(_('Wrong Date Format. Line Date Should be in format YYYY-MM-DD.'))
                        if len(new_) > 10 or len(new_) < 5:
                            raise ValidationError(_('Wrong Date Format. Line Date Should be in format YYYY-MM-DD.'))
                    
                    new_date = datetime.datetime.strptime(new_, DEFAULT_SERVER_DATE_FORMAT).date()
                else:
                    new_date = values.get('line_date')
                    
            else:
                raise UserError(_('Please Provide Line Date Field Value.'))
            value = {
                    'date':new_date,
                    'payment_ref':values.get('ref'),
                    'partner_id':partner_id or False,
                    'name':values.get('memo'),
                    'amount':values.get('amount'),
                    'currency_id':currency_id,
                    'statement_id':bank_statement_id.id,
                    }     
            bank_statement_lines = account_bank_statement_line_obj.create(value)
        else:
            raise UserError(_('Please Provide Line Date Field Value'))
        return True

    def _find_partner(self,name):
        partner_id = self.env['res.partner'].search([('name','=',name)])
        if partner_id:
            return partner_id.id
        else:
            return

    def _find_currency(self,currency):
        currency_id = self.env['res.currency'].search([('name','=',currency)])
        if currency_id:
            return currency_id.id
        else:
            raise UserError(_(' "%s" Currency are not available.') % currency)

    def _find_journal(self,name):
        journal_id = self.env['account.journal'].search([('name','=',name)])
        if journal_id:
            return journal_id.id
        else:
            raise UserError(_(' "%s" Journal is not available.') % (name))
            
class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.constrains('currency_id', 'journal_id')
    def _check_currency_id(self):
        for line in self:
            if not line.currency_id:
                continue