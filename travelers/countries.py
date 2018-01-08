class CountryForm(Form):
    cur = connection.cursor()

    name = StringField('Name', [validators.Length(min=1, max=300)])
    description = TextAreaField('Description')

@app.route('/countries')
@is_logged_in
def countries():
    cur = connection.cursor()
    result = cur.execute("SELECT c.CountryName, count(d.DestName) AS DestCount, c.CountryID "
                         "FROM Countries c LEFT OUTER JOIN Destinations d ON c.CountryID = d.CountryID "
                         "GROUP BY c.CountryName "
                         "ORDER BY c.CountryName")

    countries = cur.fetchall()
    cur.close()

    return render_template('countries.html', countries=countries)

@app.route('/country/<string:id>')
@is_logged_in
def country(id):
    countryCur = connection.cursor()
    destinationsCur = connection.cursor()
    imagesCur = connection.cursor()

    countryCur.execute("SELECT CountryName, Description, UpdateDate "
                        "FROM countries "
                        "WHERE CountryID = %s"
                        , [id])

    destinationsCur.execute("SELECT CountryName, DestName, DestID, c.Description, c.UpdateDate"
                " FROM countries c JOIN destinations d"
                " WHERE c.CountryID = d.CountryID AND c.CountryID = %s"
                , [id])

    imagesCur.execute("SELECT c.CountryId, d.DestName, i.ImgUrl "
            "FROM countries c JOIN destinations d ON c.CountryID = d.CountryID "
            "JOIN dest_images i on d.DestID = i.DestID "
            "WHERE c.CountryID = %s "
            "ORDER BY RAND()"
            , [id])

    country = countryCur.fetchone()
    destinations = destinationsCur.fetchall()
    images = imagesCur.fetchall()
    countryCur.close()
    destinationsCur.close()
    return render_template('country.html', country=country, destinations=destinations, images=images)


@app.route('/edit_country/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_country(id):
    cur = connection.cursor()
    cur.execute("SELECT CountryName, Description "
                "FROM countries "
                "WHERE CountryID = %s"
                , [id])

    country = cur.fetchone()
    cur.close()

    form = CountryForm(request.form)

    form.name.data = country['CountryName']
    form.description.data = country['Description']

    if request.method == 'POST':
        if request.form['action'] == 'Submit':
            name = request.form['name']
            description = request.form['description']

            cur = connection.cursor()
            cur.execute("UPDATE countries "
                        "SET CountryName=%s, Description=%s "
                        "WHERE CountryID=%s"
                        ,(name, description, id))

            connection.commit()
            cur.close()

            flash('Country updated.', 'success')
            return redirect(url_for('countries'))

        elif request.form['action'] == 'Delete':
            cur = connection.cursor()
            cur.execute("DELETE FROM countries "
                        "WHERE CountryID = %s"
                        , [id])

            connection.commit()
            cur.close()

            flash('Country successfully deleted.', 'success')
            return redirect(url_for('destinations'))

    return render_template('edit_country.html', form=form)
