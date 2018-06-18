from functools import wraps
from flask import current_app, abort, flash, request, redirect, url_for
from flask_login import current_user, login_url, user_unauthorized

def admin_required(func):
    """
        Extend Flask-Login to support @admin_required decorator
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_admin:
            return func(*args, **kwargs)
        flash("This page requires Administrator access.", 'danger')
        return redirect(url_for('main.home'))
    return decorated_view