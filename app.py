from flask import Flask
app = Flask(__name__)

@app.route('/')
def main_page():
    return '<h1> Welcome </h1>'

app.run(host='0.0.0.0')
