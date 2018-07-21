from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc, func, text
from app import db
from app.admin import bp
from app.admin.forms import ChangeUserEmailForm, NewUserForm, DestinationForm
from app.decorators import admin_required
from app.models import User, Destination, Country, Region, Continent, Dest_Location, Dest_Image, Tag

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

@bp.route('/user/<int:user_id>')
@bp.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@bp.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))

@bp.route('/destinations')
@login_required
@admin_required
def destinations():
    """View all destinations."""
    destinations = Destination.query.join(Country).order_by(Destination.name).all()
    return render_template(
        'admin/destinations.html', destinations=destinations)


@bp.route('/new-destination', methods=['POST', 'GET'])
@login_required
@admin_required
def new_destination():
    """Create a new destination."""
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

    return render_template('admin/new_destination.html', form=form, tags=tags)
