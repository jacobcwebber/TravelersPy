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

def get_dests(id, tag):
    tableName = "favorites" if tag == "Favorites" else "explored"
    query = "SELECT d.id, d.name as name, c.name as country, i.img_url, co.name as cont "\
            "FROM {tableName} e JOIN destinations d ON e.dest_id = d.id "\
                                "JOIN dest_images i ON i.dest_id = d.id "\
                                "JOIN countries c ON d.country_id = c.id "\
                                "JOIN regions r ON c.region_id = r.id "\
                                "JOIN continents co ON r.cont_id = co.id "\
                                "JOIN dest_tags dt ON  dt.dest_id = d.id "\
                                "JOIN tags t ON dt.tag_id = t.id "\
            "WHERE e.user_id = {userId}".format(tableName=tableName, userId=id)
    if tag != "Explored" and tag != "Favorites":
        where =  " AND t.name = '{tagName}'".format(tagName=tag)
    else: 
        where = ''
    results = execute(text(query+where))
    return results