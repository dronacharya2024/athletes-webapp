
#import necessary packages
from flask import Flask, render_template, request, redirect, url_for, make_response
#from datetime import date
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

#validate login
@app.route('/login', methods=['POST'])
def validate_login():
    """
    Route for POST requests to the login page
    Validates login attempt
    """
    username = request.form['username']
    password = request.form['password']


    # check if username and password are in the users table
    if db.login_data.count_documents({'username': username, 'password': password}) != 0:
        #allow login and redirect
        return redirect(url_for('home')) # tell the browser to make a request for the /home route
        #but logged in version
    else:
        #return error message in login page
        return redirect(url_for('login'))

#sign up page
@app.route("/sign_up")
def sign_up():
    """
    Route for GET request to sign_up page
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

#sign_up_athletecoach
@app.route("/sign_up_athlete")
def sign_up_athlete():
    """
    Route for GET request to sign_up_athlete page
    Displays form for user
    """
    return render_template('sign_up_athletecoach.html')

#sign_up_athletecoach
@app.route("/sign_up_coach")
def sign_up_coach():
    """
    Route for GET request to sign_up_coach page
    Displays form for user
    """
    return render_template('sign_up_athletecoach.html')

#sign_up_sponsor
@app.route("/sign_up_sponsor")
def sign_up_sponsor():
    """
    Route for GET request to sign_up_sponsor page
    Displays form for user
    """
    return render_template('sign_up_sponsor.html')

@app.route('/sign_up_sponsor', methods=['POST'])
def add_sponsor():
    """
    Route for POST requests to the sign up pages.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user_type = 'sponsor'

    # create a new document with the data the user entered
    doc = {
        "username": username,
        "password": password,
        "email": email, 
        "user_type": user_type,
        #"created_at": date.today()
    }
    db.login_data.insert_one(doc) # insert a new document for user
    return redirect(url_for('home')) # tell the browser to make a request for the /home route

@app.route('/sign_up_athlete', methods=['POST'])
def add_athlete():
    """
    Route for POST requests to the sign up pages.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user_type = 'athlete'

    # create a new document with the data the user entered
    doc = {
        "username": username,
        "password": password,
        "email": email, 
        "user_type": user_type,
        #"created_at": date.today()
    }
    db.login_data.insert_one(doc) # insert a new document for user
    return redirect(url_for('home')) # tell the browser to make a request for the /home route

# Rishi, add post method for /sign_up_coach route

#athleteprofile
@app.route("/athleteprofile")
def athleteprofile():
    """
    Route for GET request to athleteprofile page
    Displays form for user
    """
    return render_template('athleteprofile.html')

if __name__ == '__main__':
    app.run(debug = True, port=8000)