from flask import Flask, render_template, request, session, redirect
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

@app.route('/', methods=['POST', 'GET'])
def web_main_page():
    if request.method == 'POST':
        category = request.form.get('category').lower().strip()

    con = create_connection(DATABASE)

    query = "SELECT category, id FROM categories ORDER BY category ASC "

    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close

    return render_template('home.html', categories=category_list)

@app.route('/category/<catID>')
def web_categories_page(catID):

    con = create_connection(DATABASE)

    query = "SELECT category, id FROM categories ORDER BY category ASC "

    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()

    query = "SELECT maori_word, english_word, description, level, id " \
            "FROM words WHERE catID=? ORDER BY maori_word ASC"

    cur = con.cursor()
    cur.execute(query,(catID,))
    words_list = cur.fetchall
    con.close

    return render_template('home.html', words=words_list, categories=category_list)

@app.route('/login')
def web_login():
    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')

        query = "SELECT id, first_name, password FROM customer WHERE email =?"
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, ))
        user_data = cur.fetchall()
        con.close()

        try:
            customer_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]

        except IndexError:
            return redirect("/login?error=Email+or+password+incorrect")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+or+password+incorrect")

        session['email'] = email
        session['customer_id'] = customer_id
        session['first_name'] = first_name
        print(session)
        return redirect("/")
    return render_template('login.html',logged_in=is_logged_in())

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

        query = "INSERT INTO customer (first_name, last_name, email, password) " \
                "VALUES (?, ?, ?, ?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=email+is+already+in+use')

def is_logged_in():
    if session.get("email") is None:
        print("Not logged in")
        return False
    else:
        print("Logged in")
        return True


app.run(host='0.0.0.0')
