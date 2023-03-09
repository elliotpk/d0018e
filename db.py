import mysql.connector
from models import User
import json
# Keep the database functions gathered somewhat in here

#create the connection to the database
with open("config.json", "r") as configfile:
    data = json.load(configfile)

mydb = mysql.connector.connect(
    host=data["host"],
    user=data["user"],
    password=data["password"],
    database=data["database"]
)

def get_user(email):
    cursor=mydb.cursor()
    query = "SELECT id, email, hashed_pass, user_type FROM user WHERE email=%s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    if (result == None):
        query = "SELECT id, email, hashed_pass, user_type FROM user WHERE id=%s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
    return User(str(result[0]), result[1], result[2], result[3]) if result else None

def add_user(user):
    cursor = mydb.cursor()
    query = "INSERT INTO user (email, hashed_pass) VALUES (%s, %s)"
    cursor.execute(query, (user.email, user.password))
    mydb.commit()
    query = "SELECT id FROM user WHERE email=%s"
    cursor.execute(query, (user.email,))
    result = cursor.fetchone()
    user.setId = result[0]

def validate_email(email):
    cursor=mydb.cursor()
    query="SELECT EXISTS(SELECT * FROM user WHERE email = %s)"
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    return result[0][0]                                            # Returns 0 if no user exists with that email

def getItems():
    """Get all active listings for items"""
    cursor=mydb.cursor()
    query="SELECT listing.`date`, item.`name`, item.`image`, item.`price` FROM listing JOIN item WHERE item.`id` = `item:id` AND listing.`active` = 1"   # can remove listing.`item:id` from select
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)
    return result

def createItems(name,img,price,description):
    try:
        cursor=mydb.cursor()
        query="INSERT INTO item (name, image, price, description) VALUES (%s, %s, %s, %s)"
        values = (name,img,int(price),description)
        cursor.execute(query,values)
        mydb.commit()
        query="SELECT id FROM item WHERE name = %s"
        cursor.execute(query,name)
        itemid=cursor.fetchone()
        print(itemid)
        return itemid
    except mysql.connector.DatabaseError as e:
        print(e)

def createAttribute(attname):
    try:
        cursor=mydb.cursor()
        query="INSERT INTO attributes (name) VALUES (%s)"
        values = ([attname])
        cursor.execute(query,values)
        mydb.commit()
    except Exception as e:
        print(e,"createa")

def createAttributeValue(attvalue,attid,id):
    try:
        cursor=mydb.cursor()
        query = "SELECT * FROM attributes WHERE name = %s"
        temp = attid
        for x in attid:
            cursor.execute(query,x)
            temp = cursor.fetchone()[0]
        query="INSERT INTO attribute_value (value,item:id,attributes:id) VALUES (%s, %s, %s)"
        for x in attvalue:
            values = (x,id,temp[x])
            cursor.execute(query,values)
            mydb.commit()
    except Exception as e:
        print(e,"creatval")

def getAttributes():
    try:
        cursor=mydb.cursor()
        query="SELECT DISTINCT `name` FROM attributes"
        cursor.execute(query)
        result=cursor.fetchall()
        return result
    except Exception as e:
        print(e,"getatt")
        return []