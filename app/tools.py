import decimal, datetime
from flask import jsonify
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