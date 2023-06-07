from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

# -----------------------------------------------
# Clean old view if user came from old version
# -----------------------------------------------


def migrate(cr, version):
    """ This will delete old views """
    cr.execute('''SELECT recurring_document_history.id,recurring_document_history.document_ref from recurring_document_history''')
    history = cr.fetchall()
    document_refs = {r[0]: r[1] for r in history}
    to_delete_document_refs = []
    for history_id, document_ref in document_refs.items():
        if not document_ref:
            continue
        model, db_id = document_ref.split(',')
        model= model.replace('.','_')
        cr.execute('SELECT %s.id from %s where id = %s' % (model,model,db_id))
        existing_id = cr.fetchone()
        if existing_id:
            continue
        to_delete_document_refs.append(history_id)
    if to_delete_document_refs:
        cr.execute('UPDATE recurring_document_history set document_ref = NULL, document_deleted=True where id in %s;' % (tuple(to_delete_document_refs),))
    
