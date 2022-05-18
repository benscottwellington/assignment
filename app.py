from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import datetime

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
    con.close()
    return category_list

@app.route('/', methods=['POST', 'GET'])
def web_main_page():
    if request.method == 'POST':
        print(request.form)
        category = request.form.get('category').title()
        print(category)

        con = create_connection(DATABASE)  # SUCK MY NUTS !!!
        query = "INSERT INTO categories (category) VALUES(?)"
        cur = con.cursor()
        cur.execute(query, (category,))
        con.commit()
        con.close()

        return redirect('/')

    return render_template('home.html', categories=get_category_list(), logged_in=is_logged_in())

@app.route('/category/<catID>',methods=['POST', 'GET'])
def web_categories_page(catID):

    query = "SELECT maori_word, english_word, catID, userid, id, description, image FROM words WHERE catID IS ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query,(catID,))

    word_list = cur.fetchall()
    con.close()
    print(catID)
    print(word_list)

    if request.method == 'POST':
        maori_word = request.form.get('maori_word').title().strip()
        english_word = request.form.get('english_word').title().strip()
        level = int(request.form.get('level').strip())
        definition = request.form.get('definition').title().strip()
        timestamp = datetime.datetime.now()

        query = "SELECT first_name, last_name FROM user"
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query)
        user_data = cur.fetchall()
        con.close()

        first_name = user_data[0][0]
        last_name = user_data[0][1]
        userid = first_name + ' ' + last_name

        if level > 10 or level < 1:
            return redirect('/category/{0}?Error=Level+is+invalid'.format(catID))

        query = "INSERT INTO words(maori_word, english_word, catID, level, userid, id, description, timestamp) VALUES (?, ?, ?, ?, ?, NULL, ?, ?)"
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (maori_word, english_word, catID, level, userid, definition, timestamp, ))
        con.commit()
        con.close()

        return redirect('/category/{0}'.format(catID))

    return render_template('category.html', categories=get_category_list(), logged_in=is_logged_in(), words=word_list, category=catID)

@app.route('/word/<wordid>')
def web_words_page(wordid):
    try:
        int(wordid)
    except ValueError:
        return redirect('/')

    query = "SELECT maori_word, english_word, userid, id, description, level, timestamp, image FROM words WHERE id IS ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (wordid,))

    word_list = cur.fetchall()
    con.close()
    print(word_list)

    return render_template('words.html', categories=get_category_list(), logged_in=is_logged_in(), words=word_list,)

@app.route('/removeword/<wordid>')
def web_remove_word(wordid):
    try:
        int(wordid)
    except ValueError:
        return redirect('/')

    query = "SELECT catID FROM words WHERE id IS ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (wordid,))
    catID = cur.fetchone()
    con.close()
    print("fhfdh")

    query = "DELETE FROM words WHERE id IS ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (wordid,))
    con.commit()
    con.close()
    print("e")
    return redirect ('/category/{0}'.format(catID[0]))

@app.route('/removecategory/<catID>')
def web_remove_category(catID):
    try:
        int(catID)
    except ValueError:
        return redirect('/')

    query = "DELETE FROM categories WHERE id IS ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (catID,))
    con.commit()
    con.close()
    print("e")
    return redirect ('/')

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
        cur.execute(query, (email,))
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

    return render_template('login.html', categories=get_category_list(), logged_in=is_logged_in())


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

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html', categories=get_category_list(), logged_in=is_logged_in())


@app.route('/logout')
def web_logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/')


def is_logged_in():
    if session.get("email") is None:
        print("Not logged in")
        return False
    else:
        print("Logged in")
        return True


app.run(host='0.0.0.0')
