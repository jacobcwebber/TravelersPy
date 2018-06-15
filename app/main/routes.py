from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy import desc, text
from app import db
from app.main.forms import DestinationForm
from app.models import User, Destination, Country, Region, Continent, Dest_Location, Dest_Image, Tag
from app.utils import execute, get_dests_by_tag
from app.decorators import admin_required
from app.main import bp

@bp.route('/home')
@login_required
def home():
    if current_user.is_anonymous:
        return redirect(url_for('auth.index'))

    recent_query = text('SELECT d.id, d.name, d.update_date, i.img_url '
                        'FROM destinations d JOIN dest_images i on d.id = i.dest_id '
                        'ORDER BY d.update_date DESC')
    popular_query = text('SELECT d.id, d.name, i.img_url, count(f.dest_id) as favorites '
                        'FROM destinations d JOIN dest_images i ON d.id = i.dest_id '
                                            'JOIN favorites f ON d.id = f.dest_id '
                        'GROUP BY d.id, i.img_url '
                        'ORDER BY favorites DESC')
    recent = execute(recent_query)
    popular = execute(popular_query)
    explored = [dest.id for dest in current_user.explored_dests.all()]
    favorites = [dest.id for dest in current_user.favorited_dests.all()]
    dest_count = Destination.query.count()

    return render_template('main/home.html', recent=recent, popular=popular, explored=explored,
                            favorites=favorites, dest_count=dest_count)

@bp.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()

    favorites = [dest.id for dest in user.favorited_dests.all()]
    explored = [dest.id for dest in user.explored_dests.all()]
    dests = Destination.query.all()

    unesco = get_dests_by_tag(id=id, tag="UNESCO")

    #TODO: this query is easy enough for ORM -- change it
    query = text('SELECT l.lat, l.lng, d.name '
                 'FROM dest_locations l JOIN destinations d on l.dest_id = d.id ')
    locations = execute(query)    

    ## FINDING TOP TAGS BY USER:
    """select t.name, count(dt.tag_id) from tags t join dest_tags dt on t.
id = dt.tag_id join destinations d on dt.dest_id = d.id join explored e on e.des
t_id = d.id join users u on u.id = e.user_id where u.id=1 group by t.id order by
 count(dt.tag_id) desc;"""

    return render_template('main/user.html', title=user.full_name() + ' | Wanderlist', user=user,
                            explored=explored, favorites=favorites, locations=locations)

@bp.route('/change-map', methods=['POST'])
def change_map(where=None):
    view = request.form['view']
    base = 'SELECT l.lat, l.lng, d.name '\
           'FROM dest_locations l JOIN destinations d on l.dest_id = d.id '
    if view == "favorites":
        where = "WHERE l.dest_id IN "\
                    "(SELECT f.dest_id "\
                    "FROM favorites f "\
                    "WHERE f.user_id = {})"\
                    .format(current_user.id)
    elif view == "explored":
        where = "WHERE l.dest_id IN "\
                    "(SELECT e.dest_id "\
                    "FROM explored e "\
                    "WHERE e.user_id = {})"\
                    .format(current_user.id)
    query = text(base + (where if where else ''))
    locations = execute(query)

    return jsonify(locations)

@bp.route('/search')
@login_required
def search():
    location = request.args.get('location')
    keyword = request.args.get('keywords')

    base = 'SELECT d.id, d.name as name, c.name as country, i.img_url, co.name as cont '\
           'FROM destinations d JOIN dest_images i ON d.id = i.dest_id '\
                               'JOIN countries c ON d.country_id = c.id '\
                               'JOIN regions r ON c.region_id = r.id '\
                               'JOIN continents co ON r.cont_id = co.id '
    if location:
        if keyword:
            where = "JOIN dest_tags dt ON dt.dest_id = d.id "\
                    "JOIN tags t ON dt.tag_id = t.id "\
                    "WHERE (c.name = '{}' OR co.name = '{}' OR r.name = '{}') AND t.name = '{}'"\
                    .format(location, location, location, keyword)
        else:
            where = "WHERE (c.name = '{}' or co.name = '{}' OR r.name = '{}')"\
                    .format(location, location, location)
    elif keyword:
        where = "JOIN dest_tags dt ON dt.dest_id = d.id "\
                "JOIN tags t ON dt.tag_id = t.id "\
                "WHERE t.name = '{}'".format(keyword)
    else:
        where = 'ORDER BY random() LIMIT 5'
    query = text(base + where)
    dests = execute(query)

    for dest in dests:
        d = Destination.query.get(dest['id'])
        dest['Tags'] = [tag.name for tag in d.tags.all()]

    explored = [dest.id for dest in current_user.explored_dests.all()]
    favorites = [dest.id for dest in current_user.favorited_dests.all()]

    countries = [country.name for country in Country.query.all()]
    continents = [continent.name for continent in Continent.query.all()]
    regions = [region.name for region in Region.query.all()]
    locations = list(set(countries).union(set(list(set(continents).union(set(regions))))))

    tags = [tag.name for tag in Tag.query.all()]

    return render_template('main/search.html', title="Explore | Wanderlist", dests=dests, locations=locations, tags=tags,  
                            explored=explored, favorites=favorites, keyword=keyword, location=location)    

@bp.route('/alter-featured-dest', methods=['POST'])
@login_required
def alter_featured_dest():
    id = request.form['id']
    query = "SELECT d.name as dest_name, c.name as country_name, d.id, c.id, d.description, i.img_url "\
            "FROM destinations d JOIN countries c ON d.country_id = c.id "\
                                "JOIN dest_images i ON d.id = i.dest_id "\
            "WHERE d.id = {}".format(id)
    dest = execute(query)
    tags = [tag.name for tag in Destination.query.get(id).tags.all()]

    return jsonify(dest, tags)

@bp.route('/create-destination', methods=['POST', 'GET'])
@login_required
def create_destination():
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

@bp.route('/edit-destination/<string:id>', methods=['POST', 'GET'])
@login_required
def edit_destination(id):
    form = DestinationForm()
    dest = Destination.query.get(id) 

    if request.method == 'POST':
        dest_img = Dest_Image.query.get(id)
        dest_location = Dest_Location.query.get(id)

        dest.name = form.name.data
        dest.description = form.description.data
        dest.country_id = form.country_id.data
        dest_img.img_url = form.img_url.data
        dest_location.lat = form.lat.data
        dest_location.lng = form.lng.data

        dest.tags = []
        tags = (form.tags.data).split(',')
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            dest.add_tag(tag)
        db.session.commit()   

        return redirect(url_for('main.home'))

    tags = [tag.name for tag in Tag.query.all()]
    form.country_id.choices = [(0, '')] + ([(country.id, country.name) for country in Country.query.all()])
    dest_image = Dest_Image.query.get(id)

    form.name.data = dest.name
    form.country_id.data = dest.country_id
    form.tags.data = ','.join([tag.name for tag in dest.tags.all()])
    form.description.data = dest.description
    form.img_url.data = dest_image.img_url

    return render_template('main/edit_destination.html', form=form, tags=tags)

@bp.route('/user/<id>/<string:tag>')
def user_destinations(id, tag):
    user = User.query.get(id)
    dests = get_dests_by_tag(id=id, tag=tag)
    explored = [dest.id for dest in user.explored_dests.all()]
    favorites = [dest.id for dest in user.favorited_dests.all()]

    return render_template('main/user_destinations.html', user=user, tag=tag, 
                            dests=dests, explored=explored, favorites=favorites)


@bp.route('/alter-explored', methods=['POST'])
def alter_explored():
    dest = Destination.query.get(request.form['id'])
    action = request.form['action']
    
    current_user.add_explored(dest) if action == "add" else current_user.remove_explored(dest)
    db.session.commit()

    return "success"

@bp.route('/alter-favorite', methods=['POST'])
def alter_favorite():
    dest = Destination.query.get(request.form['id'])
    action = request.form['action']
    
    current_user.add_favorite(dest) if action == "add" else current_user.remove_favorite(dest)
    db.session.commit()

    return "success"