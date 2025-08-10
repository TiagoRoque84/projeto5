
import json
from flask_login import current_user
from extensions import db
from models import AuditLog

def _username():
    try: return current_user.username if current_user.is_authenticated else 'system'
    except Exception: return 'system'

def log_create(entity, entity_id, snapshot:dict):
    db.session.add(AuditLog(entity=entity, entity_id=entity_id, action='create', user=_username(), changes=json.dumps(snapshot, ensure_ascii=False)))

def log_update(entity, entity_id, before:dict, after:dict):
    diff = {}
    for k in set(before.keys()) | set(after.keys()):
        if before.get(k) != after.get(k):
            diff[k] = {'from': before.get(k), 'to': after.get(k)}
    db.session.add(AuditLog(entity=entity, entity_id=entity_id, action='update', user=_username(), changes=json.dumps(diff, ensure_ascii=False)))

def log_delete(entity, entity_id, snapshot:dict):
    db.session.add(AuditLog(entity=entity, entity_id=entity_id, action='delete', user=_username(), changes=json.dumps(snapshot, ensure_ascii=False)))
