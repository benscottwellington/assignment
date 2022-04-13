from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
DATABASE = "website.db"
app.secret_key = "srugy8rthy8gyrsuaisgbi89ujdf"

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None

def get_category_list():
    con = create_connection(DATABASE)

    query = "SELECT category, id FROM categories ORDER BY category ASC "

    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close
    return category_list

@app.route('/', methods=['POST', 'GET'])
def web_main_page():
    if request.method == 'POST':
        category = request.form.get('category').lower().strip()

    return render_template('home.html', categories=get_category_list())

@app.route('/category')
def web_category_page():
    con = create_connection(DATABASE)
    query = "SELECT maori_word, english_word, decription, level, id FROM words"
    cur = con.cursor()
    cur.execute(query)

    words_list = cur.fetchall()
    cur.close()


    return render_template('category.html', categories=get_category_list(), words=words_list)



@app.route('/category/<catID>')
def web_categories_page(catID):

    con = create_connection(DATABASE)

    query = "SELECT maori_word, english_word, description, level, id " \
            "FROM words WHERE catID=? ORDER BY maori_word ASC"

    cur = con.cursor()
    cur.execute(query,(catID,))
    words_list = cur.fetchall
    con.close

    return render_template('category.html', words_list=words_list, categories=get_category_list())

@app.route('/login', methods=['POST', 'GET'])
def web_login():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')

        query = "SELECT id, first_name, password FROM user WHERE email =?"
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, ))
        user_data = cur.fetchall()
        con.close()

        try:
            user_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]

        except IndexError:
            return redirect("/login?error=Email+or+password+incorrect")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+or+password+incorrect")

        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name
        print(session)
        return redirect("/")

    return render_template('login.html', categories=get_category_list())

@app.route('/signup', methods=['POST', 'GET'])
def web_signup():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+characters")

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DATABASE)

        query = "INSERT INTO user (first_name, last_name, email, password) " \
                "VALUES (?, ?, ?, ?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=email+is+already+in+use')

    return render_template('signup.html')

def is_logged_in():
    if session.get("email") is None:
        print("Not logged in")
        return False
    else:
        print("Logged in")
        return True


app.run(host='0.0.0.0')
