odoo.define('oi_action_trigger_reload.ActionMenus', function (require) {
    "use strict";

    const ActionMenus = require('web.ActionMenus');
    const DropdownMenuItem = require('web.DropdownMenuItem');

    const core = require('web.core');
    const session = require('web.session');

    const _t = core._t;
    const qweb = core.qweb;
    
    
    class RefreshMenu extends DropdownMenuItem {    	
    	 
    	async _onRefreshMenuClick (event) {
			 this.trigger('reload', {
				 onSuccess : () => document.body.click()
			 });
	   }    	 
    }
    
    RefreshMenu.template = 'RefreshMenu';
    
    ActionMenus.registry.add('refresh-menu', {
        Component: RefreshMenu,
        getProps(parentProps) {
            return {
                activeIds: parentProps.activeIds,
                context: parentProps.context,
            };
        },
        
    });    	
    
    return RefreshMenu;
    
    
});