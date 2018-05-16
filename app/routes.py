from flask import render_template, redirect, url_for
from app import app
from app.forms import LoginForm, RegisterForm

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    login_form = LoginForm()
    register_form = RegisterForm()

    if request.method == 'POST':
        if request.form['submit'] == "Create account":
            email = register_form.email.data
            first = register_form.firstName.data
            last = register_form.lastName.data
            password = sha256_crypt.encrypt(str(register_form.password.data))

            cur = connection.cursor()
            cur.execute("INSERT INTO users(FirstName, LastName, Password, Email) "
                        "VALUES (%s, %s, %s, %s, %s)"
                        , (first, last, password, email))

            connection.commit()
            cur.close()

            flash('Congratulations! You are now registered.', 'success')

            return redirect(url_for('login'))
        elif request.form['submit'] == "Login":
            email = login_form.email
            password_attempt = login_form.password
            remember_me = login_form.remember_me

            cur = connection.cursor()
            result = cur.execute("SELECT * "
                                "FROM users "
                                "WHERE Email = %s"
                                , email)
            user = cur.fetchone()
            cur.close()

            if result > 0:
                password = user['Password']
                userId = user['UserID'] 
                firstname = user['FirstName']
                isAdmin = user['IsAdmin']

                if sha256_crypt.verify(password_attempt, password):
                    
                    session['user'] = userId
                    session['logged_in'] = True
                    session['is_admin'] = isAdmin

                    return redirect(url_for('destinations'))

                else:
                    error = 'Invalid login. Please try again.'
                    return render_template('login.html', error=error)
                cur.close()

            else:
                error = "User not found."
                return render_template('login.html', error=error)

    return render_template('index.html', login_form=login_form, register_form=register_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')

    password_attempt = form.password

    cur = connection.cursor()

    result = cur.execute("SELECT * "
                            "FROM users "
                            "WHERE Username = %s"
                            , [username])
    user = cur.fetchone()
    cur.close()

    if result > 0:
        password = user['Password']
        userId = user['UserID'] 
        firstname = user['FirstName']

        if sha256_crypt.verify(password_attempt, password):
            
            # set session variables
            session['logged_in'] = True
            session['user'] = userId

            if user['IsAdmin'] == 1:
                session['is_admin'] = True
            else:
                session['is_admin'] = False

            return redirect(url_for('index'))

        else:
            error = 'Invalid login'
            return render_template('login.html', error=error)
        cur.close()

    else:
        error = "Username not found."
        return render_template('login.html', error=error)
