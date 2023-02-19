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

def get_user(email):
    cursor=mydb.cursor()
    query = "SELECT id, hashed_pass FROM user WHERE email=%s"
    cursor.execute(query, email)
    result = cursor.fetchone()
    return User(str(result[0]), email, result[1]) if result else None

def add_user(user):
    cursor = mydb.cursor()
    query = "INSERT INTO user (email, hashed_pass) VALUES (%s, %s)"
    print('hello')
    cursor.execute(query, (user.email, user.password))
    print('executed statment')
    mydb.commit()
    query = "SELECT id FROM user WHERE email=%s"
    cursor.execute(query, (user.email,))
    result = cursor.fetchone()
    print(result[0])
    user.setId = result[0]

def validate_email(email):
    cursor=mydb.cursor()
    query="SELECT EXISTS(SELECT * FROM user WHERE email = %s)"
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    return result[0][0]                                            # Returns 0 if no user exists with that email