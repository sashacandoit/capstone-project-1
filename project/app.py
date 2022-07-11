from flask import Flask, render_template, request, flash, redirect, session
from forms import AddUserForm, LoginForm, UpdateUserForm
from models import db, connect_db, User, APIFontStyle
from sqlalchemy.exc import IntegrityError
# from api_keys import GOOGLE_API_KEY

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone_1_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'somethingsecret'

connect_db(app)
# db.create_all()



#############################################################
# USER ROUTES
#############################################################

@app.route('/')
def home_page():
    """Render home page"""
    
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register_user():

    if "username" in session:
        return redirect(f"users/{session['username']}")


    form = AddUserForm()

    if form.validate_on_submit():
        full_name = form.full_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        new_user = User.register(full_name, username, email,  password)

        db.session.add(new_user)
        
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already in use')
            return render_template('register.html', form=form)

        try:
            db.session.commit()
        except IntegrityError:
            form.email.errors.append('Email address already taken')
            return render_template('register.html', form=form)

        session['username'] = new_user.username
        flash('Welcome to the party! Successfully created your account!')
        return redirect(f"users/{session['username']}")
        
    else:
        return render_template('register.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login_user():

    if "username" in session:
        return redirect(f"users/{session['username']}")


    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        
        #Check if use passes authentication:
        if user:
            flash(f"Welcome Back, {user.full_name}!", "primary")
            session['username'] = user.username
            return redirect('/')
          
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)



@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("See you soon!", "info")
    return redirect('/login')



@app.route('/users/<username>')
def show_user(username):
    
    if username != session['username'] or "username" not in session:
        flash("Please login first!")
        return redirect('/login')
        
    user = User.query.get(username)
    #Need to change all of these to user.id

    return render_template('user_profile.html', user=user)