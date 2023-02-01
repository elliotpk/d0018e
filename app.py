from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)
mydb = mysql.connector.connect(
    host="localhost",
    user="elliot",
    password="6626",
    database="test"
)

@app.route('/')
def home():
    cursor = mydb.cursor()
    cursor.execute("SELECT name FROM object WHERE id=1;")
    res = cursor.fetchone()
    print(res)
    return render_template('home.html', name=(res[0]))

if __name__=='__main__':
    app.run()