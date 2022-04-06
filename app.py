from flask import Flask, render_template, request
import sqlite3
from sqlite3 import Error

DATABASE = "website.db"

app = Flask(__name__)

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None

@app.route('/')
def web_main_page():

    con = create_connection(DATABASE)

    query = "SELECT category FROM dictionary"

    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()

    return render_template('home.html', category = category_list)

@app.route('/login')
def web_login():
    return render_template('login.html')


app.run(host='0.0.0.0')
