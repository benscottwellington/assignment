from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def web_main_page():
    return render_template('base.html')

@app.route('/login')
def web_login():
    return render_template('login.html')


app.run(host='0.0.0.0')
