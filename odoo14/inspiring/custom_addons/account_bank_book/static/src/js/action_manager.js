odoo.define('account_bank_book.action_manager', function (require) {
"use strict";

/**
 * The purpose of this file is to add the actions of type
 * 'ir.actions.bank.xlsx_download' to the ActionManager.
 */

var ActionManager = require('web.ActionManager');
var framework = require('web.framework');
var session = require('web.session');

ActionManager.include({

    /**
     * Executes actions of type 'ir.actions.bank.xlsx_download'.
     *
     * @private
     * @param {Object} action the description of the action to execute
     * @returns {Deferred} resolved when the report has been downloaded ;
     *   rejected if an error occurred during the report generation
     */
    _executeBankXlsxReportDownloadAction: function (action) {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/bank_xlsx_reports',
            data: action,
            success: def.resolve.bind(def),
            error: (error) => this.call('crash_manager', 'rpc_error', error),
            complete: framework.unblockUI,
        });
        return def;
    },
    /**
     * Overrides to handle the 'ir.actions.bank.xlsx_download' actions.
     *
     * @override
     * @private
     */
    _handleAction: function (action, options) {

        if (action.type === 'ir.actions.bank.xlsx_download') {
            var state = this._super.apply(this, arguments);
            action.output_format = 'xlsx'
            return this._executeBankXlsxReportDownloadAction(action, options);
        }
        return this._super.apply(this, arguments);
    },
});

});
