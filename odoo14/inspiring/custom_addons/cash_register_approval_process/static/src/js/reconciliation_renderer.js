odoo.define('cash_register_approval_process.ReconciliationRenderer', function (require) {
"use strict";

var ReconciliationRenderer = require('account.ReconciliationRenderer');
var Widget = require('web.Widget');
var FieldManagerMixin = require('web.FieldManagerMixin');
var relational_fields = require('web.relational_fields');
var basic_fields = require('web.basic_fields');
var core = require('web.core');
var time = require('web.time');
var session = require('web.session');
var qweb = core.qweb;
var _t = core._t;


var LineRenderer = ReconciliationRenderer.LineRenderer;
LineRenderer.include ({
    events: _.extend({}, LineRenderer.prototype.events, {
    	'click .o_return ': '_onReturnToBankStatement',
    }),
    
    _onReturnToBankStatement: function (event) {
        event.stopPropagation();
        event.preventDefault();
        var self = this;
        var bank_statement_id = this.model.bank_statement_id || false;
        var journal_id = this.model.context.journal_id || false
        if (journal_id) {
        	journal_id = parseInt(journal_id);
        }
        
        self._rpc({
                model: 'account.bank.statement',
                method: 'return_to_bank_statement',
                args: [[bank_statement_id]],
            }).then(function () {
            	
            	self.do_action({
                    name: 'Bank Statements',
                    res_model: 'account.bank.statement',
                    views: [[false, 'list'], [false, 'form']],
                    type: 'ir.actions.act_window',
                    context: {search_default_journal_id: journal_id, 'journal_type':'bank'},
                    view_mode: 'form',
                });
            });
    },
});

});
