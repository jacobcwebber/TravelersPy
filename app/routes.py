from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
