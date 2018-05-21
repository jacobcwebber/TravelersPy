import decimal, datetime
from flask import jsonify
from flask_login import current_user
from sqlalchemy import text
import json
from app import db

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

def execute(query):
    result = db.engine.execute(query)
    return json.loads(json.dumps([dict(r) for r in result], default=alchemyencoder))

def get_dests_by_tag(tag):
    query = text("SELECT d.id "
                "FROM explored e JOIN destinations d ON e.dest_id = d.id "
                                "JOIN dest_tags dt ON  dt.dest_id = d.id "
                                "JOIN tags t ON dt.tag_id = t.id "
                "WHERE e.user_id = {} AND t.name = '{}'".format(current_user.id, tag))
    results = execute(query)
    return results