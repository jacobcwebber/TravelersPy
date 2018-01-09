#####################################################
#####          USER FUNCTIONALITY                ####
#####################################################

#Forms
class RegisterForm(Form):
    username = StringField('', [
        validators.Length(min=4, max=25, message='Username must be 4 to 25 characters long')
        ], render_kw={"placeholder": "username"})
    email = StringField('', [
        validators.Email(message = "Please submit a valid email"),
        validators.Length(min=4, max=50, message='Email must be 5 to 50 character long')
        ], render_kw={"placeholder": "email"})
    firstName = StringField('', [
        validators.InputRequired()
    ], render_kw={"placeholder": "first name"})
    lastName = StringField('', [
        validators.InputRequired()
    ], render_kw={"placeholder": "last name"}) 
    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ], render_kw={"placeholder": "password"})
    confirm = PasswordField('', render_kw={"placeholder": "confirm password"})

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        first = form.firstName.data
        last = form.lastName.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = connection.cursor()
        cur.execute("INSERT INTO users(Username, FirstName, LastName, Password, Email) "
                    "VALUES (%s, %s, %s, %s, %s)"
                    , (username, first, last, password, email))

        connection.commit()
        cur.close()

        flash('Congratulations! You are now registered.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_attempt = request.form['password']

        cur = connection.cursor()

        result = cur.execute("SELECT * "
                             "FROM users "
                             "WHERE Username = %s"
                             , [username])


        if result > 0:
            user = cur.fetchone()
            password = user['Password']
            userId = user['UserID']
            firstname = user['FirstName']

            #checks if passwords match and logs you in if they do
            if sha256_crypt.verify(password_attempt, password):
                session['logged_in'] = True
                session['user'] = userId

                #sets admin session status from db query
                cur.execute("SELECT IsAdmin "
                            "FROM users "
                            "WHERE UserID = %s"
                            , [userId])

                if cur.fetchone()['IsAdmin'] == 1:
                    session['admin'] = True
                else:
                    session['admin'] = False

                cur.close()
                flash('Welcome, ' + firstname + '. You are now logged in.', 'success')
                return redirect(url_for('index'))

            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()

        else:
            error = "Username not found."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/account')
@is_logged_in
def account():
    cur = connection.cursor()
    cur.execute("SELECT f.DestID "
                "FROM favorites f JOIN destinations d ON d.DestID = f.DestID JOIN users u on u.UserID = f.UserID "
                "WHERE f.UserID = %s"
                , [session['user']])
    favorites = cur.fetchall()
    
    cur.execute("SELECT DestID "
                "FROM explored "
                "WHERE UserID = %s"
                , session['user'])
    explored = cur.fetchall()

    cur.execute("SELECT c.CountryID "
                "FROM explored e JOIN destinations d ON e.DestID = d.DestID JOIN countries c ON d.CountryID = c.CountryID "
                "WHERE e.UserID = %s "
                "GROUP BY c.CountryID"
                , session['user'])
    countries = cur.fetchall()
    cur.close()

    counts = [len(explored), len(favorites), len(countries)]
    captions = ['Destinations Explored', 'Favorites', 'Countries Visited']

    return render_template('account.html', favorites=favorites, explored = explored, captions=captions, counts=counts)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))