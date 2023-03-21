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
    if(current_user.is_authenticated):
        if(current_user.user_type == 'A'):
            itemdata = getItems('A', -1)
        else:
            itemdata = getItems('U', current_user.id)
    else:
        itemdata = getItems('U', -1)
    print(itemdata)
    return render_template('home.html', items = itemdata) # todo: get database info for each item and format properly

@app.route('/account/')
@login_required
def account():
    if(current_user.user_type == 'U'):
        orderid = getOrder(current_user.id)
        itemids = getItemIdsFromOrder(orderid)
        itemlist1 = []
        for x in itemids:
            for id in x:
                itemlist1.append(getItem(id))
        print(itemlist1)
        return render_template("account.html", methods=("GET","POST"),itemlist=itemlist1)
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
        session['selectedattlist']=[]
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
        selectedattlist = session['selectedattlist']
    except:
        session['selectedattlist'] = selectedattlist=[]
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
                name = form.name.data
                image = form.image.data
                price = form.price.data
                description = form.description.data
                if image == "":
                    image = "None"
                if description  == "":
                    description  = "None"
                id=createItems(name,image,price,description)
                if(len(session['attributevalue']) > 0 and len(session['selectedattlist']) > 0):
                    createAttributeValue(session['attributevalue'], session['selectedattlist'],id)
                    session['attributevalue'] = []
                    session['selectedattlist'] = []
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
                selectedattlist = data
            session['selectedattlist']=selectedattlist
        else:
            selectedattlist=session['selectedattlist']
    attlist = getAttributes()
    print(session['selectedattlist'],selectedattlist)
    print(session['attributevalue'],attributevalue)
    return render_template("addItem.html", form=form, attform=attform, attlist=attlist, attvalform=attvalform, selectedattlist=selectedattlist, attributevalue=attributevalue)

@app.route('/item/<id>', methods=["GET"])
def item(id):
    print()
    details = getItem(id)
    reviews = getComments(id)
    visibility = getVisibility(id)
    rating = sum(i for _,_,_,i,_,_ in reviews)                  # Sum up the review numbers
    rating = len(reviews) and rating/len(reviews) or '-'          # Get the average number or 0 if no reviews exist
    attributes=[]
    values=[]
    for x in details:
        if x[9]!=None:
            attributes.append(x[9])
        if x[6] != None:
            values.append(x[7])
    return render_template('item.html', title=details[0][1], image=details[0][2], price = details[0][3], description = details[0][4], attributes = attributes, values=values, comments = reviews, rating = rating, visibility = visibility)

@app.route('/delist/<id>', methods=['POST'])
@login_required
def delist(id):
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))
    itemid = id
    toggleVisibility(id)
    return redirect(request.referrer)

@app.route('/deleteAttribute/<id>/<attribute>', methods=['POST'])
@login_required
def deleteAttribute(id, attribute):
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(request.referrer)
    deleteAtt(id, attribute)
    return redirect(request.referrer)

@app.route('/deleteComment/<id>', methods=['POST'])
@login_required
def deleteComment(id):
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(request.referrer)
    deleteReview(id)
    return redirect(request.referrer)    

@app.route('/updateAttribute/<id>/<attribute>', methods=['POST'])
@login_required
def updateAttribute(id, attribute):
    if(current_user.user_type != 'A'):
        flash("Unauthorized access", "danger")
        return redirect(request.referrer)
    updateAtt(id, attribute, request.form['val'])
    return redirect(request.referrer)

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

@app.route('/cart_add/<itemid>', methods=["POST"])
@login_required
def cartAdd(itemid):
    addToCart(current_user.id, itemid)
    return redirect(url_for('home'))

@app.route('/cart_remove/<itemid>', methods=["POST"])
@login_required
def cartRemove(itemid):
    removeFromCart(current_user.id, itemid)
    return redirect(url_for('home'))

@app.route('/cart/', methods=("GET", "POST"))
@login_required
def cart():
    itemlist=[]
    itemidlist=getCart(current_user.id)
    sum=0
    for x in itemidlist:
        data=getItem(x)
        itemlist.append(data)
        sum = sum + int(data[0][3])
    return render_template("cart.html", itemlist=itemlist, sum=sum)

@app.route('/checkout/<sum>', methods=["POST"])
@login_required
def checkout(sum):
    form=cardCredential_form()
    if form.validate_on_submit():
        banknr=form.banknr
        expdate=form.expdate
        cvs=form.cvs
        itemidlist = getCart(current_user.id)
        orderid = userToOrder(current_user.id, sum)
        for itemid in itemidlist:
            orderToItem(orderid,itemid)
            toggleVisibility(itemid)
            removeFromCart(current_user.id,itemid)
        return redirect(url_for('home'))
    return render_template("checkout.html",form=form,sum=sum)

@app.route('/item/<itemId>/comment', methods=["GET", "POST"])
@login_required
def addComment(itemId):
    form = comment_form()
    if form.validate_on_submit():
        try:
            userId = current_user.id
            text = form.text.data
            rating = form.rating.data
            postComment(itemId, userId, rating, text)
            return redirect(url_for('item', id=itemId))
        except Exception as e:
            flash(e, "danger")
    return render_template("comment.html", form=form, text='Add comment')




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