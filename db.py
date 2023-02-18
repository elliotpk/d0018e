import mysql.connector
from models import User
# Keep the database functions gathered somewhat in here

#create the connection to the database
mydb = mysql.connector.connect(
    host="192.168.1.209",
    user="elliotRemote",
    password="6626",
    database="E-Commerce"
)

def get_user(username):
    cursor=mydb.cursor()
    query = "SELECT id, hashed_pass FROM user WHERE username=%s"
    result = cursor.execute(query, username)
    return User(str(result[0]), username, result[1]) if result else None