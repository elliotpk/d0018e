from flask import Flask, render_template, redirect, url_for, flash ,request, session
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
    try:
        session['attributevalue']=[]
        session['selctedattlist']=[]
    except Exception as e:
        print(e)
    form = addItem_form
    return render_template("admin.html", form=form)


@app.route('/admin/addItem/', methods=("GET","POST"))
@login_required
def addItem():
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))
    form = addItem_form()
    attform = addAttribute_form()
    attvalform = addAttributeValue_form()
    try:
        selctedattlist = session['selctedattlist']
    except:
        session['selctedattlist'] = selctedattlist=[]
    try:
        attributevalue=session['attributevalue']
    except:
        session['attributevalue'] = attributevalue = []
    try:
        action = request.form['button']
    except Exception as e:
        action = None
    if action == 'newitem':
        if form.validate_on_submit():
            try:
                name = form.name.data
                image = form.image.data
                price = form.price.data
                description = form.description.data
                if image == "":
                    image = "None"
                if description  == "":
                    description  = "None"
                id=createItems(name,image,price,description)
                createAttributeValue(session['attributevalue'], session['selctedattlist'],id)
                session['attributevalue'] = []
                session['selctedattlist'] = []
            except Exception as e:
                print(e,"newitem")
    elif action == 'createattribute':
        if attform.validate_on_submit():
            try:
                attributename = attform.attributename.data
                createAttribute(attributename)
            except Exception as e:
                print(e,"createattribute")
    elif action == 'createvalue':
        if attvalform.validate_on_submit():
            try:
                if request.form.getlist('attributevalue') != 0:
                    tre = request.form.getlist('attributevalue')
                    attributevalue=request.form.getlist('attributevalue')
                    session['attributevalue']=attributevalue
                else:
                    attributevalue=session['attributevalue']
            except Exception as e:
                print(e,"createvalue")
    elif action == 'selectattribute':
        if len(request.form.getlist('attribute')) != 0:
            data = request.form.getlist('attribute')
            for x in range(len(data)):
                data[x]=data[x].split("('")[1].split("',)")[0]
                selctedattlist = data
            session['selctedattlist']=selctedattlist
        else:
            selctedattlist=session['selctedattlist']
    attlist = getAttributes()
    print(session['selctedattlist'],selctedattlist)
    print(session['attributevalue'],attributevalue)
    return render_template("addItem.html", form=form, attform=attform, attlist=attlist, attvalform=attvalform, selctedattlist=selctedattlist, attributevalue=attributevalue)

@app.route('/item/<id>', methods=["GET"])
def item(id):
    return id

@app.route('/delist/<id>', methods=['POST'])
@login_required
def delist(id):
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))
    itemid = id
    # TODO Add database connection to delist the item, also make sure to fetch delisted items and display them to the admin
    return redirect(url_for('home'))


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