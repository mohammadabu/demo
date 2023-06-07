odoo.define('oi_workflow.ActionMenus', function (require) {
    "use strict";

    const ActionMenus = require('web.ActionMenus');
    const DropdownMenuItem = require('web.DropdownMenuItem');
    const Dialog = require('web.Dialog');

    const core = require('web.core');
    const session = require('web.session');

    const _t = core._t;
    const qweb = core.qweb;
    
    
    class WorkflowMenu extends DropdownMenuItem {
    	
    	 async _onApprovalInfo() {
    		 const activeId = this.props.activeIds[0];
    		 const approval_info = await this.rpc({
    			 route : '/oi_workflow/approval_info', 
    			 params : {
    				 model : this.env.action.res_model, 
        			 record_id : activeId, 
    			 },    			 
    			 context : this.props.context
    		 });
	        var buttons = [
	        	{
	        		text: _t("Ok"), 
	        		close: true,
	        		classes: 'btn-primary',
	        	}
	        ];
	        		        				
			new Dialog(self, {
                title: _t("Approval Info"),
                size: 'medium',
                buttons : buttons,
                $content: qweb.render('oi_workflow.approval_info', {
                	data : approval_info,
                	session : session,
                	odoo : odoo
                })
            }).open();    		 
    		 
    	 }
    	 
    	 async _onApprove() {
    		 const self = this;
    		 Dialog.confirm(this, (_t("Are you sure you want to approve selected documents?")), {
    			 confirm_callback: function () {
    				 var prom;
    				 if (self.props.isDomainSelected) {
    					 prom = session.rpc('/web/dataset/call_kw', {
        	    			 args: [self.props.domain],
                             method : 'search',
                             model : self.env.action.res_model,
                             kwargs : {},    			 
        	    			 context : self.props.context
        	    		 });
    				 }
    				 else {
    					 prom = new Promise(function (resolve, reject) {
    						 resolve(self.props.activeIds);
    					 });
    				 }
    				 prom.then(function(active_ids) {
        	    		 var def = session.rpc('/web/dataset/call_button', {
        	    			 args: [active_ids],
                             method : 'action_approve',
                             model : self.env.action.res_model,
                             kwargs : {},    			 
        	    			 context : self.props.context
        	    		 });
        	    		 def.then(function(result){
        	    			 self.env.searchModel.trigger('search');
        	    		 });    					 
    				 });
    				     	    		 
    			 }
    		 });
    	 }
    	 async _onUpdateStatus() {
			 const action = {
			    name: _t('Change Document Status'),
                res_model: 'approval.state.update',
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                view_type: 'form',
                view_mode: 'form',
                target : 'new',
                context : _.extend({}, this.props.context, {
                	active_model : this.env.action.res_model,
                	active_ids : this.props.activeIds,
                	active_domain : this.props.isDomainSelected && this.props.domain
                })
			 };
			 if (action.context.active_domain === undefined)
				delete action.context.active_domain;
			 this.trigger('do-action', {action: action});
    	 }
    		
    }
    
    WorkflowMenu.template = 'WorkflowMenu';
    
    ActionMenus.registry.add('workflow-menu', {
        Component: WorkflowMenu,
        getProps(parentProps) {
            return {
                activeIds: parentProps.activeIds,
                context: parentProps.context,
                approval_models : core.approval_models,
                state_models : core.state_models,
                is_system : session.is_system,
                domain : parentProps.domain,
                isDomainSelected : parentProps.isDomainSelected
            };
        },
        
    });

    return WorkflowMenu;
    
    
});