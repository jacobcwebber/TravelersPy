#####################################################
#####            DESTINATIONS PAGES              ####
#####################################################

@app.route('/destinations-user')
@is_logged_in
def destinations_user():
    cur = connection.cursor()
    cur.execute("SELECT d.DestID, d.DestName, i.ImgURL "
                "FROM destinations d JOIN dest_images i on d.destID = i.DestID "
                "GROUP BY d.DestID "
                "ORDER BY d.UpdateDate DESC")
    recommended = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT d.DestID, d.DestName, i.ImgURL "
                "FROM destinations d "
                "JOIN dest_images i on d.DestID = i.DestID "
                "JOIN dest_tags dt on d.DestID = dt.DestID "
                "JOIN tags t ON dt.TagID = t.TagID "
                "WHERE t.TagName = 'Adventure' "
                "GROUP BY d.DestID "
                "ORDER BY RAND()")
    topTag = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT d.DestID, d.DestName, i.ImgURL "
                "FROM destinations d "
                "JOIN dest_images i on d.DestID = i.DestID "
                "JOIN dest_tags dt on d.DestID = dt.DestID "
                "JOIN tags t ON dt.TagID = t.TagID "
                "WHERE t.TagName = 'UNESCO' "
                "GROUP BY d.DestID "
                "ORDER BY RAND()")
    secondTag = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT DestID "
                "FROM favorites "
                "WHERE UserID = %s"
                , session['user'])
    favs = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT DestID "
                "FROM explored "
                "WHERE UserID = %s"
                , session['user'])
    exp = cur.fetchall()
    cur.close()

    # Convert dictionaries for favorites and explored into lists so they can easier be iterated through in jinja 
    favorites = []
    for dest in favs:
        favorites.append(dest['DestID'])

    explored = []
    for dest in exp:
        explored.append(dest['DestID'])

    cur = connection.cursor()
    cur.execute("SELECT COUNT(*) AS Count "
                "FROM Destinations")
    count = cur.fetchone()
    return render_template('destinations_user.html', count=count, favorites=favorites, explored=explored, recommended=recommended)

@app.route('/destinations')
@is_logged_in
def destinations():
    cur = connection.cursor()
    cur.execute("SELECT * "
                "FROM destinations d JOIN countries c ON d.CountryID = c.CountryID "
                "ORDER BY d.DestName")

    destinations = cur.fetchall()
    cur.close() 

    return render_template('destinations.html', destinations=destinations)


class DestinationForm(Form):
    cur = connection.cursor()

    cur.execute("SELECT CountryID, CountryName "
                "FROM countries")

    countries = cur.fetchall()
    cur.close()

    countriesList = [(0, "")]
    for country in countries:
        countriesList.append((country['CountryID'], country['CountryName']))

    name = StringField('Name')
    countryId = SelectField('Country', choices=countriesList, coerce=int)
    category = SelectField('Category', choices=[
        (0, ""),
        (1, "Natural Site"),
        (2, "Cultural Site"),
        (3, "Activity")], coerce=int)
    description = TextAreaField('Description')
    imgUrl = StringField('Image Upload', [validators.URL(message="Not a valid url")])
    tags = StringField('Tags')

class DestImageForm(Form):
    imgUrl = StringField('Image URL', [validators.URL(message="Not a valid url")])

@app.route('/destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def destination(id):
    if request.method == 'GET':
        cur = connection.cursor()
        result = cur.execute("SELECT DestName, CountryName, DestID, c.CountryID, d.Description, d.UpdateDate "
                             "FROM destinations d JOIN countries c ON d.CountryID = c.CountryID "
                             "WHERE DestID = %s", [id])
        destination = cur.fetchone()

        cur.execute("SELECT ImgUrl "
                         "FROM dest_images "
                         "WHERE DestID = %s"
                         , [id])
        images = cur.fetchall()

        cur.execute("SELECT * "
                    "FROM vTags "
                    "WHERE DestName  = %s"
                    , [destination['DestName']])
        tags = cur.fetchall()
        cur.close()

        if result > 0:
            return render_template('destination.html', destination=destination, images=images, tags=tags)
        else:
            flash('Destination does not exist.', 'danger')
            return redirect(url_for('destinations'))

    else:
        cur = connection.cursor()
        cur.execute("INSERT INTO favorites "
                    "VALUES (%s, %s)",
                    (session['user'], id))

        connection.commit()
        cur.close()

        flash('Added to favorites', 'success')

        return redirect(url_for('destinations'))

@app.route('/create-destination', methods=['POST', 'GET'])
@is_logged_in
def create_destination():
    form = DestinationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        countryId = form.countryId.data
        category = form.category.data
        description = form.description.data
        imgUrl = form.imgUrl.data
        tags = form.tags.data
        #lat = request.form['lat']
        #lng = request.form['lng']

        cur = connection.cursor()

        cur.execute("INSERT INTO destinations(DestName, CountryID, Category, Description) "
                    " VALUES (%s, %s, %s, %s)"
                    , (name, countryId, category, description))

        connection.commit()
        cur.close()

        cur = connection.cursor()

        cur.execute("SELECT DestID "
                    "FROM destinations "
                    "WHERE DestName = %s"
                    , [name])
        id = cur.fetchone()

        cur.execute("INSERT INTO dest_images "
                    " VALUES (%s, %s)",
                    (id['DestID'], imgUrl))

        #TODO: make it so the latLng is saved in db to avoid geocoding on page load
        # cur.execute("INSERT INTO dest_locations "
        #     " VALUES (%s, %s, %s)"
        #     , (id['DestID'], lat, lng))

        connection.commit()
        cur.close()

        ##TODO: figure out why this if statement isn't working... error is thrown if no tags input
        if tags != None:
            for tag in tags.split(','):
                cur = connection.cursor()

                cur.execute("SELECT TagID "
                            "FROM Tags "
                            "WHERE TagName = %s"
                            , [tag])
                tagId = cur.fetchone()
                
                cur.execute("INSERT INTO dest_tags "
                            "VALUES (%s, %s)"
                            , (id['DestID'], tagId['TagID']))
                connection.commit()
                cur.close()

        flash('Your new destination has been created!', 'success')

        return redirect(url_for('destinations'))
            
    cur = connection.cursor()
    cur.execute("SELECT TagName FROM tags")
    tags = cur.fetchall()
    cur.close()

    tagsList = []
    for tag in tags:
        tagsList.append(tag['TagName'])

    return render_template('create_destination.html', form=form, tags=tagsList)

@app.route('/edit_destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_destination(id):
    cur = connection.cursor()

    cur.execute("SELECT * "
                "FROM destinations d JOIN dest_images i ON d.DestID = i.DestID "
                "WHERE d.DestID = %s"
                , [id])

    destination = cur.fetchone()
    cur.close()

    form = DestinationForm(request.form)

    form.name.data = destination['DestName']
    form.countryId.data = destination['CountryID']
    form.category.data = destination['Category']
    form.description.data = destination['Description']
    form.imgUrl.data = destination['ImgURL']
    # form.tags.data = tags['TagName'] --> gonna need to loop through

    if request.method == 'POST':
        #if request.form['action'] == 'Submit':
        name = request.form['name']
        countryId = request.form['countryId']
        category = request.form['category']
        description = request.form['description']
        tags = request.form['tags']
        imgUrl = request.form['imgUrl']

        print("The tags are: " + tags, file=sys.stderr)

        cur = connection.cursor()
        cur.execute("UPDATE destinations "
                    "SET DestName=%s, CountryID=%s, Category=%s, Description=%s "
                    "WHERE DestID=%s"
                    , (name, countryId, category, description, id))

        cur.execute("UPDATE dest_images "
                    "SET ImgURL = %s "
                    "WHERE DestID=%s"
                    , (imgUrl, id))

        connection.commit()
        cur.close()

        cur = connection.cursor()

        cur.execute("SELECT DestID "
                    "FROM destinations "
                    "WHERE DestName = %s"
                    , [name])
        destId = cur.fetchone()
        try:
            for tag in tags.split(','):
                cur = connection.cursor()       

                cur.execute("SELECT TagID "
                            "FROM Tags "
                            "WHERE TagName = %s"
                            , [tag])
                tagId = cur.fetchone()
                
                cur.execute("INSERT INTO dest_tags "
                            "VALUES (%s, %s)"
                            , (destId['DestID'], tagId['TagID']))
                connection.commit()
                cur.close()
        except TypeError: 
            print("A TypeError occured because you did not submit any new tags. This is a temporary issues.")

        flash('Destination updated.', 'success')
        return redirect(url_for('destinations_user'))

    cur = connection.cursor()
    cur.execute("SELECT TagName FROM tags")
    tags = cur.fetchall()
    cur.close()

    tagsList = []
    for tag in tags:
        tagsList.append(tag['TagName'])

    return render_template('edit_destination.html', form=form, tags=tagsList)


@app.route('/alter-explored', methods=['POST'])
def alter_explored():
    id = request.form['id']
    action = request.form['action']
    
    cur = connection.cursor()

    if action == "add":
        cur.execute("INSERT INTO explored "
                    "VALUES (%s, %s)"
                    , (session['user'], id))
    elif action == "remove":
        cur.execute("DELETE FROM explored "
                    "WHERE UserID = %s AND DestID = %s"
                    , (session['user'], id))  

    connection.commit()
    cur.close()
    return "success"

@app.route('/alter-favorite', methods=['POST'])
def alter_favorite():
    id = request.form['id']
    action = request.form['action']
    
    cur = connection.cursor()

    if action == "add":
        cur.execute("INSERT INTO favorites "
                    "VALUES (%s, %s)"
                    , (session['user'], id))
    elif action == "remove":
        cur.execute("DELETE FROM favorites "
                    "WHERE UserID = %s AND DestID = %s"
                    , (session['user'], id))  

    connection.commit()
    cur.close()
    return "success"

