odoo.define('tis_web_arabic', function (require) {
    "use strict";

    var config = require('web.config');
    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');
    FormRenderer.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            console.log("this.applyChatterPosition()")
            this.applyChatterPosition()
        },
        applyChatterPosition: function () {
            var $form = this.$('.o_form_view');
            var $sheet = $form.find('aside.o_chatter');
            // var $chatter = $form.find('aside.o_chatter');
            console.log("test")
            console.log($form)
            console.log($sheet)
            if ($sheet.length == 1) {
                $sheet.css('display', 'none');
                $sheet.hide()
            }
        },
    });
});
