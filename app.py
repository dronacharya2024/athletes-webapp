
#import necessary packages
from flask import Flask, render_template, request, redirect, url_for, make_response
import db

# instantiate the app
app = Flask(__name__)

'''
# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mode
'''

#home page
@app.route('/')
def home():
    """
    Route for the home page
    """
    return "this is the home page!"

#test to insert data to the data base
@app.route("/test")
def test():
    db.collection.insert_one({"name": "John"})
    return "Connected to the data base!"

#login page
@app.route("/login")
def login():
    """
    Route for GET request to login page
    Displays form for user
    """
    return render_template('login.html')

#sign up page
@app.route("/sign_up")
def sign_up():
    """
    Route for GET request to login page
    Displays form for user
    """
    return render_template('sign_up.html')

#index
@app.route("/index")
def index():
    """
    Route for GET request to index page
    Displays form for user
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug = True, port=8000)