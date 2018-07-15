from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc, func, text
from app import db
from app.admin import bp
from app.decorators import admin_required
from app.models import User

@bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')

@bp.route('/registered-users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.order_by(User.id).all()
    return render_template(
        'admin/registered_users.html', users=users)

@bp.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()), 'success')
    return render_template('admin/new_user.html', form=form)

@bp.route('/create-destination', methods=['POST', 'GET'])
@login_required
@admin_required
def new_destination():
    form = DestinationForm()

    if request.method == 'POST':
        dest = Destination(name=form.name.data, country_id=form.country_id.data, description=form.description.data)
        tags = (form.tags.data).split(',')
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            dest.add_tag(tag)
        db.session.add(dest)
        db.session.commit()

        dest_img = Dest_Image(dest_id=dest.id, img_url=form.img_url.data)
        dest_location = Dest_Location(dest_id=dest.id, lat=form.lat.data, lng=form.lng.data)

        db.session.add_all([dest_img, dest_location])
        db.session.commit()
        
        return redirect(url_for('main.home'))

    tags = [tag.name for tag in Tag.query.all()]
    form.country_id.choices = [(0, '')] + ([(country.id, country.name) for country in Country.query.all()])

    return render_template('main/create_destination.html', form=form, tags=tags)
