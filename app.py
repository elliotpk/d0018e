from flask import Flask, render_template, redirect, url_for, flash ,request
from flask_bcrypt import Bcrypt
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from db import *
from forms import *

app = Flask(__name__)
app.secret_key = '#kF$jdH$L&eYOe'
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

bcrypt = Bcrypt()
bcrypt.init_app(app)

@app.route('/')
def home():
    itemdata = getItems()
    return render_template('home.html', items = itemdata) # todo: get database info for each item and format properly

@app.route('/account/')
@login_required
def account():
    if(current_user.user_type == 'U'):
        return render_template("account.html")
    else:
        return redirect(url_for('admin'))
    
@app.route('/admin/', methods=("GET", "POST"))
@login_required
def admin():
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))
    form = addItem_form()
    if form.validate_on_submit():
        try:
            name = form.name.data
            image = form.image.data
            price = form.price.data
            description = form.description.data
            attid="hej"
            createItems(name,image,price,description,attid)
        except Exception as e:
            flash(e)
    return render_template("admin.html", form=form) #Här är error vet inte vad som saknas

@app.route('/admin/addItem/', methods=("GET","POST"))
@login_required
def addItem():
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))
    form = addItem_form()
    if form.validate_on_submit():
        try:
            name = form.name
            image = form.image
            price = form.price
            description = form.description
            createItems(name,image,price,description)
        except Exception as e:
            flash(e)
    return render_template("admin.html", form=form)

@app.route('/login/', methods=("GET", "POST"))
def login():
    form = login_form()
    if form.validate_on_submit():
        try:
            user = get_user(form.email.data)
            if bcrypt.check_password_hash(user.password, form.pwd.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Invalid username or password", "danger")
        except Exception as e:        
                flash(e)

    return render_template("login.html", form=form, text='Login', btn_action='Login')

@app.route('/register/', methods=("GET", "POST"))
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            if(validate_email(email) != 0):
                raise Exception("Email already exists")
            newUser = User(None, email, bcrypt.generate_password_hash(pwd), 'U')
            add_user(newUser)
            flash("Account Created!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(e, "danger")

    return render_template('login.html', form=form, text='Register', btn_action='Submit')

@app.route('/logout/', methods=("GET", "POST"))
@login_required
def logout():
    logout_user()
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)


if __name__=='__main__':
    app.run()