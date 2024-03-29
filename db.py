import mysql.connector
from models import User
import json
from datetime import datetime
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
    query = "SELECT COUNT(*) FROM cart WHERE `user:id` = %s"
    cursor.execute(query, (result[0],))
    cart = cursor.fetchone()
    cursor.close()
    return User(str(result[0]), result[1], result[2], result[3], cart[0]) if result else None

def getAllUsers():
    cursor = mydb.cursor()
    qurey = "SELECT `id`, `email`, `isDeleted` FROM `user`"
    cursor.execute(qurey)
    result = cursor.fetchall()
    return result

def togleUserVisability(id):
    cursor = mydb.cursor()
    query = "UPDATE `user` SET `isDeleted` = NOT `isDeleted` WHERE `id` = %s"
    cursor.execute(query,(id,))
    mydb.commit()
    cursor.close()

def add_user(user):
    cursor = mydb.cursor()
    query = "INSERT INTO user (email, hashed_pass) VALUES (%s, %s)"
    cursor.execute(query, (user.email, user.password))
    mydb.commit()
    query = "SELECT id FROM user WHERE email=%s"
    cursor.execute(query, (user.email,))
    result = cursor.fetchone()
    cursor.close()
    user.setId = result[0]

def validate_email(email):
    cursor=mydb.cursor()
    query="SELECT EXISTS(SELECT * FROM user WHERE email = %s)"
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    cursor.close()
    return result[0][0]                                            # Returns 0 if no user exists with that email

def getItems(usertype, userid):
    """Get all active listings for items"""
    cursor=mydb.cursor()
    if(usertype == 'A'):
        query="SELECT listing.`date`, item.`name`, item.`image`, item.`price`, item.`id`, item.`description`, listing.`active` FROM listing JOIN item WHERE item.`id` = `item:id`"   # can remove listing.`item:id` from select
    else:
        query="SELECT listing.`date`, item.`name`, item.`image`, item.`price`, item.`id`, item.`description` FROM listing JOIN item WHERE item.`id` = `item:id` AND listing.`active` = 1"
    cursor.execute(query)
    result = cursor.fetchall()
    if(userid != -1):
        query = "SELECT `item:id` FROM cart WHERE `user:id` = %s"
        cursor.execute(query, (userid,))
        cartIds = cursor.fetchall()
    cursor.close()
    newResult = []
    for item in result:
        if(userid != -1):
            for itemId in cartIds:
                if(item[4] == itemId[0]):
                    item += (1,)
        if(len(item) != 7): item += (0,)
        newResult.append(item)
    return newResult

def createItems(name,img,price,description):
    try:
        cursor=mydb.cursor(buffered=True)
        query="INSERT INTO item (name, image, price, description) VALUES (%s, %s, %s, %s)"
        values = (name,img,int(price),description)
        cursor.execute(query,(values))
        mydb.commit()
        query="SELECT LAST_INSERT_ID()"
        cursor.execute(query)
        itemid=cursor.fetchone()[0]
        query="INSERT INTO listing (active, `item:id`, date) VALUES (%s, %s, %s)"
        current_time = datetime.now()
        time = current_time.strftime("%Y-%m-%d")
        cursor.execute(query, (1, itemid, time))
        mydb.commit()
        cursor.close()
        return itemid
    except mysql.connector.DatabaseError as e:
        print(e,"create item")

def createAttribute(attname):
    try:
        cursor=mydb.cursor()
        query="INSERT INTO attributes (name) VALUES (%s)"
        values = ([attname])
        cursor.execute(query,values)
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(e,"createa")

def createAttributeValue(attvalue,attid,id):
        cursor=mydb.cursor()
        query = "SELECT id FROM attributes WHERE name = %s LIMIT 1"
        query2 = "INSERT INTO attribute_value (value,`item:id`,`attributes:id`) VALUES (%s, %s, %s)"
        tempid=[]
        while(len(attid)>0):
            cursor.execute(query, (attid.pop(0),))
            res = cursor.fetchall()
            for var in res:
                tempid.append(var[0])
        data = []
        for i in range(len(tempid)):
            data.append((attvalue[i], id, tempid[i]))
        
        cursor.executemany(query2, data)
        mydb.commit()

def getAttributes():
    try:
        cursor=mydb.cursor()
        query="SELECT DISTINCT `name` FROM attributes"
        cursor.execute(query)
        result=cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(e,"getatt")
        return []

def getItem(id):
    cursor = mydb.cursor()
    #query = "SELECT item.*, attribute_value.`value`, attributes.`name` from item JOIN attribute_value JOIN attributes WHERE `item:id` = %s AND attributes.id = `attributes:id`"
    query = "SELECT * FROM item AS t1" \
            " LEFT JOIN `attribute_value` AS t2 ON t1.id = t2.`item:id`" \
            " LEFT JOIN `attributes` AS t3 ON t2.`attributes:id` = t3.id" \
            " WHERE t1.id = %s"
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    cursor.close()
    return result

def getVisibility(id):
    cursor = mydb.cursor()
    query = "SELECT active FROM listing WHERE `item:id` = %s"
    cursor.execute(query,(id,))
    result = cursor.fetchall()
    cursor.close()
    return result[0][0]

def toggleVisibility(id):
    cursor = mydb.cursor()
    query = "UPDATE listing SET `active` = NOT `active` WHERE `item:id` = %s"  # Will flip the boolean value
    cursor.execute(query, (id,))
    mydb.commit()
    cursor.close()

def addToCart(userId, itemId):
    cursor = mydb.cursor()
    query = "INSERT INTO cart (`user:id`, `item:id`, available) VALUES (%s, %s, %s)"
    cursor.execute(query, (userId, itemId, 1))
    mydb.commit()
    cursor.close()

def removeFromCart(userId, itemId):
    cursor = mydb.cursor()
    query = "DELETE FROM cart WHERE `user:id` = %s AND `item:id` = %s"
    cursor.execute(query, (userId, itemId))
    mydb.commit()
    cursor.close()

def getCart(userId):
    cursor = mydb.cursor()
    query = "SELECT `item:id` FROM cart WHERE `user:id` = %s"
    cursor.execute(query, (userId,))
    itemids=cursor.fetchall()
    for item in range(len(itemids)):
        itemids[item]=itemids[item][0]
    cursor.close()
    return itemids

def userToOrder(userId,sum):
    cursor = mydb.cursor()
    query = "INSERT INTO `order` (`date`, `user:id`, `sum`) VALUES (%s, %s, %s)"
    cursor.execute(query,(datetime.now(),userId,sum))
    mydb.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    result = cursor.fetchone()
    orderid = result[0]
    return orderid

def orderToItem(orderId,itemId):
    cursor = mydb.cursor()
    query = "INSERT INTO `order_items` (`item:id`,`order:id`) VALUES (%s, %s)"
    cursor.execute(query,(itemId,orderId))
    mydb.commit()

def getOrder(userId):
    cursor = mydb.cursor()
    query = "SELECT id FROM `order` WHERE `user:id` = %s AND handeld = 1"
    cursor.execute(query,(userId,))
    result=cursor.fetchall()
    for orderid in range(len(result)):
        result[orderid]=result[orderid][0]
    return result

def getAllOrders():
    cursor = mydb.cursor()
    query = "SELECT * FROM `order` WHERE `handeld` = 0"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def updateOrder(orderid):
    cursor = mydb.cursor()
    query = "update `order` set handeld = 1 where `id` = %s;"
    cursor.execute(query,(orderid,))
    mydb.commit()
    cursor.close()

def getItemIdsFromOrder(orderId):
    cursor = mydb.cursor()
    query = "SELECT `item:id` FROM `order_items` WHERE `order:id` = %s"
    itemids = []
    for id in orderId:
        cursor.execute(query,(id,))
        result=cursor.fetchall()
        for i in range(len(result)):
            itemids.append(result[i][0])
    return itemids

def postComment(itemId, userId, rating, txt):
    cursor = mydb.cursor()
    query = "INSERT INTO comment (`text`, `user:id`, `rating`, `listing:id`) VALUES (%s, %s, %s, (SELECT `id` FROM listing WHERE `item:id` = %s))"
    cursor.execute(query, (txt, userId, rating, itemId))
    mydb.commit()
    cursor.close()

def getComments(itemId):
    cursor = mydb.cursor()
    query = "SELECT * FROM comment WHERE `listing:id` IN (SELECT `id` FROM listing WHERE `item:id` = %s)"
    cursor.execute(query, (itemId,))
    result = cursor.fetchall()
    cursor.close()
    return result

def deleteAtt(itemId, attName):
    cursor = mydb.cursor()
    query = "DELETE FROM attribute_value WHERE `item:id` = %s AND `attributes:id` = (SELECT `id` FROM attributes WHERE attributes.`name` = %s)"
    cursor.execute(query, (itemId, attName))
    mydb.commit()
    cursor.close()

def updateAtt(itemId, attName, value):
    cursor = mydb.cursor()
    query = "UPDATE attribute_value SET `value` = %s WHERE `item:id` = %s AND `attributes:id` = (SELECT `id` FROM attributes WHERE attributes.`name` = %s)"
    cursor.execute(query, (value, itemId, attName))
    mydb.commit()
    cursor.close()

def deleteReview(commentId):
    cursor = mydb.cursor()
    query = "DELETE FROM comment WHERE `id` = %s"
    cursor.execute(query, (commentId,))
    mydb.commit()
    cursor.close()

def updateDesc(itemId, description):
    cursor = mydb.cursor()
    query = "UPDATE item SET `description` = %s WHERE `id` = %s"
    cursor.execute(query,(description, itemId))
    mydb.commit()
    cursor.close()