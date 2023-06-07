from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

# -----------------------------------------------
# Clean old view if user came from old version
# -----------------------------------------------


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cronjob = env.ref('st_recurring_document_base.generate_recurring_documents_cron')
    cr.execute("UPDATE ir_cron set interval_type = 'minutes' where id = %i" % cronjob.id)
        
    
