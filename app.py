from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import datetime
#importing required modules

app = Flask(__name__)
bcrypt = Bcrypt(app)
DATABASE = "website.db"
app.secret_key = "srugy8rthy8gyrsuaisgbi89ujdf" #secret key that bcrypt uses for hashing passwords, good for privacy and to prevent hacking
#different secret key will hash passwords differently

#create a function used everytime a connection to the database is required
def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None

#function which has a list of categories
def get_category_list():
    con = create_connection(DATABASE)

    query = "SELECT category, id FROM categories ORDER BY category ASC "
    cur = con.cursor()
    cur.execute(query)
    #puts all the data into a list sorted by alphabetical order
    category_list = cur.fetchall()
    con.close()
    return category_list

@app.route('/', methods=['POST', 'GET']) #home route, used everytime a user is on the home page. uses home.html
def web_main_page():
    if request.method == 'POST':
        print(request.form)
        category = request.form.get('category').title() #collecting information from the form

        con = create_connection(DATABASE) #create connection to the database
        query = "INSERT INTO categories (category) VALUES(?)" #query to insert information into database
        cur = con.cursor()
        cur.execute(query, (category,)) #information is inserted and new category is added
        con.commit()
        con.close()

        return redirect('/')

    return render_template('home.html', categories=get_category_list(), logged_in=is_logged_in(), teacher=is_teacher())

@app.route('/category/<catID>',methods=['POST', 'GET']) #category route, used everytime a user is on a category page, used category.html
def web_categories_page(catID):

    query = "SELECT maori_word, english_word, catID, userid, id, description, image FROM words WHERE catID IS ? ORDER BY maori_word ASC"
    #collecting all words in a category and sorting them by maori word alphabetical order
    con = create_connection(DATABASE) #create connection to the database
    cur = con.cursor()
    cur.execute(query,(catID,))

    word_list = cur.fetchall() #puts all the words into a list
    con.close()


    if request.method == 'POST':
        maori_word = request.form.get('maori_word').strip().lower()
        english_word = request.form.get('english_word').strip().lower()
        level = int(request.form.get('level').strip())
        definition = request.form.get('definition').strip()
        timestamp = datetime.datetime.now() #information collected from form, also gets the time the user submitted the form

        query = "SELECT first_name, last_name FROM user"
        con = create_connection(DATABASE) #create connection to the database
        cur = con.cursor()
        cur.execute(query)
        user_data = cur.fetchall()
        con.close() #collects users data for userid

        first_name = user_data[0][0]
        last_name = user_data[0][1]
        userid = first_name + ' ' + last_name #creating the userid

        if level > 10 or level < 1:
            return redirect('/category/{0}?Error=Level+is+invalid'.format(catID)) #if level is not between 1 and 10, user is given an error message

        query = "INSERT INTO words(maori_word, english_word, catID, level, userid, id, description, timestamp) VALUES (?, ?, ?, ?, ?, NULL, ?, ?)"
        #query to insert information into database
        con = create_connection(DATABASE) #create connection to the database
        cur = con.cursor()
        cur.execute(query, (maori_word, english_word, catID, level, userid, definition, timestamp, )) #information is inserted and category is added
        con.commit()
        con.close()

        return redirect('/category/{0}'.format(catID))

    return render_template('category.html', categories=get_category_list(), logged_in=is_logged_in(), words=word_list, category=catID, teacher=is_teacher())

@app.route('/word/<wordid>') #word route, used everytime a user is on a word page. uses word.html
def web_words_page(wordid):
    try:
        int(wordid)
    except ValueError:
        return redirect('/') #if the wordid is not a number, redirects user to the home page

    query = "SELECT maori_word, english_word, userid, id, description, level, timestamp, image FROM words WHERE id IS ?"
    #selects data to display on the website
    con = create_connection(DATABASE) #create connection to the database
    cur = con.cursor()
    cur.execute(query, (wordid,))

    word_list = cur.fetchall() # puts data into a list
    con.close()

    return render_template('words.html', categories=get_category_list(), logged_in=is_logged_in(), words=word_list, teacher=is_teacher())

@app.route('/removeword/<wordid>') #removeword route, used everytime a user confirms to remove a word
def web_remove_word(wordid):
    if not is_teacher():
        return redirect("/") #if user is not a teacher, they're redirected to the homepage

    try:
        int(wordid)
    except ValueError:
        return redirect('/') #if the wordid is not a number, redirects user to the home page

    query = "SELECT catID FROM words WHERE id IS ?" #query to get the catID, used for the redirect
    con = create_connection(DATABASE) #if the wordid is not a number, redirects user to the home page
    cur = con.cursor()
    cur.execute(query, (wordid,))
    catID = cur.fetchone() #collects the catID
    con.close()

    query = "DELETE FROM words WHERE id IS ?" #query deletes the word from teh category based on the id
    con = create_connection(DATABASE) #creates connection to teh database
    cur = con.cursor()
    cur.execute(query, (wordid,)) #executes query to delete the word
    con.commit()
    con.close()
    return redirect ('/category/{0}'.format(catID[0])) #redirects user to the category of the word they just deleted

@app.route('/confirmremoveword/<wordid>')#confirmation to delete a word route, used everytime a user wants to remove a word. uses removeword.html
def web_confirm_remove_word(wordid):
    if not is_teacher():
        return redirect("/") #if the user is not a teacher, they're redirect

    query = "SELECT maori_word, english_word, userid, id, description, level, timestamp, image FROM words WHERE id IS ?"
    # query to collect information to display on the page
    con = create_connection(DATABASE) #creates connection the database
    cur = con.cursor()
    cur.execute(query, (wordid,)) #collects information for a certain word

    word_list = cur.fetchall() #puts information into a list
    con.close()

    return render_template ('removeword.html', categories=get_category_list(), logged_in=is_logged_in(), words=word_list, teacher=is_teacher())

@app.route('/editword/<wordid>',methods=['POST', 'GET']) #edit word route, used everytime a user wants to edit the data of a word, uses editword.html
def web_edit_word(wordid):
    if not is_teacher():
        return redirect("/") #if user is not a teacher, they're redirected to the homepage

    try:
        int(wordid)
    except ValueError:
        return redirect('/') #if wordid isn't a number, user is redirected to the homepage

    query = "SELECT maori_word, english_word, userid, id, description, level, timestamp, image FROM words WHERE id IS ?"
    # selects data to display on the page
    con = create_connection(DATABASE)#creates connection to the database
    cur = con.cursor()
    cur.execute(query, (wordid,)) # selects data for a certain word

    word_list = cur.fetchall() #puts data into a list
    con.close()

    if request.method == 'POST':
        new_maori_word = request.form.get('new_maori_word').strip().lower()
        new_english_word = request.form.get('new_english_word').strip().lower()
        new_level = int(request.form.get('new_level').strip())
        new_definition = request.form.get('new_definition').strip()
        new_timestamp = datetime.datetime.now() #information collected from form, also gets the time the user submitted the form

        if new_level > 10 or new_level < 1:
            return redirect('/editword/{0}?Error=Level+is+invalid'.format(wordid))
            #if level isn't between 1 and 10, user is redirect to a fresh edit word page

        query = "SELECT first_name, last_name FROM user"
        con = create_connection(DATABASE) #create connection to the database
        cur = con.cursor()
        cur.execute(query)
        user_data = cur.fetchall()
        con.close() #collects users data for userid

        first_name = user_data[0][0]
        last_name = user_data[0][1]
        new_userid = first_name + ' ' + last_name #creates a new userid

        query = "UPDATE words SET maori_word = ?, english_word = ?, userid = ?, id = ?, description = ?, level = ?, timestamp = ? WHERE id IS ?"
        #query to update the data for a word in teh database
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (new_maori_word, new_english_word, new_userid, wordid, new_definition, new_level, new_timestamp, wordid))
        #updates all the data in the database
        con.commit()
        con.close()

        return redirect ('/word/{0}'.format(wordid)) #redircts user to the word they just updated

    return render_template('editword.html', categories=get_category_list(), logged_in=is_logged_in(), words=word_list, teacher=is_teacher())

@app.route('/removecategory/<catID>') #remove category route, used everytime a user confirms they want to remove a category
def web_remove_category(catID):
    if not is_teacher():
        return redirect("/") #if user is not a teacher, they're redirected to the home page

    try:
        int(catID)
    except ValueError:
        return redirect('/') # if catID isn't a number, user is redirected to the home page

    query = "DELETE FROM categories WHERE id IS ?" #query to remove the category
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (catID,)) #executes the query, category is deleted
    con.commit()
    con.close()
    return redirect ('/') #redirects user to the home page


@app.route('/confirmremovecategory/<catID>') #confirm remove category route, used everytime a user wants to remove a category, used removecategory.html
def web_confirm_remove_category(catID):
    if not is_teacher():
        return redirect("/") #if user is not a teacher, they're redirected to the home page

    try:
        int(catID)
    except ValueError:
        return redirect('/')  # if catID isn't a number, user is redirected to the home page

    query = "SELECT id, category FROM categories WHERE id IS ?" #selects data to display on the page
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (catID,)) #gets data for a certain catID

    deletecategory = cur.fetchall() #puts data into a list
    con.close()

    return render_template('removecategory.html', categories=get_category_list(), logged_in=is_logged_in(), deletecategory=deletecategory,
                           teacher=is_teacher())

@app.route('/login', methods=['POST', 'GET']) #login page, used everytime someone wants to log in, uses login.html
def web_login():
    if is_logged_in():
        return redirect('/') #if a user is already logged in, they're redirected to the home page

    if request.method == 'POST': #gets the data from the html form
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')

        query = "SELECT id, first_name, password, role FROM user WHERE email =?" #query to get data from the database
        con = create_connection(DATABASE)# create connection to the database
        cur = con.cursor()
        cur.execute(query, (email,)) # executes the query
        user_data = cur.fetchall() # puts data into a list
        con.close()

        try:
            user_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]
            role = user_data[0][3] #if data from the form matches the database, user is logged in
        except IndexError:
            return redirect("/login?error=Email+or+password+incorrect") #if data from form doesn't match, user gets an error message

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+or+password+incorrect")#if data from form doesn't match, user gets an error message

        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name
        session['role'] = role
        print(session)
        return redirect("/")

    return render_template('login.html', categories=get_category_list(), logged_in=is_logged_in(), teacher=is_teacher())


@app.route('/signup', methods=['POST', 'GET']) #sign up route, used everytime a user wants to signup, uses signup.html
def web_signup():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        role = request.form.get('role')
        password = request.form.get('password')
        password2 = request.form.get('password2') #gets information from the signup form

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match') # if password and password2 dont match, user is redirected with an error message

        if len(password) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+characters") # if password isn't long enough, user is redirected

        hashed_password = bcrypt.generate_password_hash(password) #generates a hashed version of the users password

        con = create_connection(DATABASE) # creates connection to the database

        query = "INSERT INTO user (first_name, last_name, email, password, role) " \
                "VALUES (?, ?, ?, ?, ?)" # query to insert the information into the database

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password, role, )) #executes the query
        except sqlite3.IntegrityError:
            return redirect('/signup?error=email+is+already+in+use')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html', categories=get_category_list(), logged_in=is_logged_in(), teacher=is_teacher())


@app.route('/logout') #logout route, used everytime a user wants to logout
def web_logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())] #removes all the data from the users current session
    print(list(session.keys()))
    return redirect('/') #redirects user to the home page once complete

def is_teacher(): #function that checks whether or not a user is a teacher
    if session.get("role") == '1':
        print("Is a teacher")
        return True
    return False

def is_logged_in(): #function that checks whether a user is logged in or not
    if session.get("email") is None:
        print("Not logged in")
        return False
    else:
        print("Logged in")
        return True


app.run(host='0.0.0.0')
