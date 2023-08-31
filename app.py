
# import necessary packages
from flask import Flask, render_template, request, redirect, url_for, make_response
# from datetime import date
import db
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# instantiate the app
app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = 'static/uploads/'
app.config['MAX_CONTANT_LENGTH'] = 16*500*500
app.config['ALLOWED_EXTENSION'] = ['.jpg', '.jpeg', '.png', '.gif']

'''
# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mode
'''

# home


@app.route("/")
def initial():
    """
    Route for GET request to home page
    Displays form for user
    """
    return redirect('/home')

# home


@app.route("/home")
def home():
    """
    Route for GET request to home page
    Displays form for user
    """
    return render_template('home.html')

# login page


@app.route("/login")
def login():
    """
    Route for GET request to login page
    Displays form for user
    """
    title = 'Login'
    return render_template('login.html', title=title)

# validate login


@app.route('/login', methods=['POST'])
def validate_login():
    """
    Route for POST requests to the login page
    Validates login attempt
    """
    global username
    username = request.form['username']
    password = request.form['password']

# Check if username and password are in the users table
    user_data = db.login_data.find_one(
        {'username': username, 'password': password})

    if user_data:
        global user_type
        user_type = user_data.get('user_type')
        user_id = user_data.get('_id')
        if user_type == 'athlete':
            # Redirect athletes to their profile
            athlete_data = db.athletes_data.find_one({user_id})
            return redirect(url_for('athleteprofile', athlete_data=athlete_data))
        elif user_type == 'coach' and username == 'superuser':
            # Redirect coaches to viewplayerspage
            return redirect(url_for('admintemplate'))
        elif user_type == 'coach':
            # Redirect coaches to viewplayerspage
            return redirect(url_for('requests'))
        elif user_type == 'sponsor':
            # Redirect sponsors to requests page
            return redirect(url_for('requests'))

    else:
        # return error message in login page
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)


# login page
@app.route("/admintemplate")
def admintemplate():
    """
    Route for GET request to login page
    Displays form for user
    """
    title = 'Admin Template'
    type = int(request.args.get('type'))

    if type == 1:
        docs = db.login_data.find({'user_type': 'coach', 'status': 0})
        return render_template('admintemplate.html', title=title, docs=docs)


@ app.route('/admintemplate', methods=['GET'])
def process_admintemplate():
    """
    Route for GET request to login page
    Displays form for user
    """
    title = 'Admin Template'
    type = str(request.args.get('type'))
    if type == 1:
        docs = db.coach_data.aggregate([
            {
                '$lookup': {
                    'from': 'login_data',  # You can directly specify on which collection you want to lookup
                    'localField': '_id',
                    'foreignField': '_id',
                    'as': 'coachdata',
                }
            },
            {
                '$unwind': '$coachdata'
            },
            {
                '$project': {
                    'firstname': '$firstname',
                    'surame': '$surname',
                    'status': 0,
                    'phoneno': '$phoneno',
                    '_id': 0
                }
            }
        ])

        return type


# sign_up_athletecoach


@ app.route("/sign_up_athlete")
def sign_up_athlete():
    """
    Route for GET request to sign_up_athlete page
    Displays form for user
    """
    return render_template('sign_up_athletecoach.html')

# sign_up_athletecoach


@ app.route("/sign_up_coach")
def sign_up_coach():
    """
    Route for GET request to sign_up_coach page
    Displays form for user
    """
    return render_template('sign_up_athletecoach.html')


@ app.route('/sign_up_coach', methods=['POST'])
def add_coach():
    """
    Route for POST requests to the sign up pages.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    surname = request.form['surname']
    email = request.form['email']
    phoneno = request.form['phoneno']
    additional_info = request.form['additional_info']
    user_type = 'coach'

    # return error if their account already exists
    if db.login_data.count_documents({'email': email}) != 0:
        error = "An account with this email already exists."
        return render_template('sign_up_coach.html', error=error)

    # create a new document with the data the user entered
    doc = {
        "username": username,
        "password": password,
        "user_type": user_type,
        "status": 0,
        "created_at":  datetime.now()
    }

    insert_result = db.login_data.insert_one(
        doc)  # insert a new document for user
    # tell the browser to make a request for the /home route

    doc1 = {
        '_id': insert_result.inserted_id,
        'firstname': firstname,
        'surname': surname,
        "email": email,
        "phoneno": phoneno,
        "additional_info": additional_info,
    }

    db.coach_data.insert_one(doc1)

    docs = db.athletes_data.find()
    title = 'Athletes'
    athlete_class = 'current'
    return render_template('viewathletes.html', title=title, docs=list(docs))


# sign_up_sponsor
@ app.route("/sign_up_sponsor")
def sign_up_sponsor():
    """
    Route for GET request to sign_up_sponsor page
    Displays form for user
    """
    return render_template('sign_up_sponsor.html')


@ app.route('/sign_up_sponsor', methods=['POST'])
def add_sponsor():
    """
    Route for POST requests to the sign up pages.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user_type = 'sponsor'
    companyname = request.form['companyname']
    phoneno = request.form['phoneno']
    address = request.form['address']

    # return error if their account already exists
    if db.login_data.count_documents({'email': email}) != 0:
        error = "An account with this email already exists."
        return render_template('sign_up_sponsor.html', error=error)

    # create a new document with the data the user entered
    doc = {
        "username": username,
        "password": password,
        "email": email,
        "user_type": user_type,
        # "created_at": date.today()
    }
    db.login_data.insert_one(doc)  # insert a new document for user

    docsponsor = {
        "companyname": companyname,
        "email": email,
        "phoneno": phoneno,
        "address": address,
        # "created_at": date.today()
    }
    db.sponsor_data.insert_one(docsponsor)  # insert a new document for user

    # tell the browser to make a request for the /home route
    return redirect(url_for('requests'))


@ app.route('/sign_up_athlete', methods=['POST'])
def add_athlete():
    """
    Route for POST requests to the sign up pages.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user_type = 'athlete'

    # return error if their account already exists
    if db.login_data.count_documents({'email': email}) != 0:
        error = "An account with this email already exists."
        return render_template('sign_up_athletecoach.html', error=error)

    # create a new document with the data the user entered
    doc = {
        "username": username,
        "password": password,
        "email": email,
        "user_type": user_type,
        "status": 0,
        "created_at":  datetime.now(),
    }
    db.login_data.insert_one(doc)  # insert a new document for user
    # tell the browser to make a request for the /home route
    return redirect(url_for('athleteprofileedit', username=username))

# athleteprofile


@ app.route("/athleteprofile")
def athleteprofile():
    """
    Route for GET request to athleteprofile page
    Displays form for user
    """
    id = str(request.args.get('id'))
    docs = db.athletes_data.find({'_id': ObjectId(id)})
    return render_template('athleteprofile.html', docs=docs)

# athleteprofileedit


@ app.route("/athleteprofileedit", methods=['GET'])
def athleteprofileedit():
    """
    Route for GET request to athleteprofileedit page
    Displays form for user
    """
    username = request.args.get('username')
    return render_template('athleteprofileedit.html', username=username)

# sponsorprofile


@ app.route('/athleteprofileedit', methods=['POST'])
def validate_athleteprofileedit():
    fullname = request.form['fullname']
    age = request.form['age']
    email = request.form['email']
    phoneno = request.form['phoneno']
    sport = request.form['sport']
    rank = request.form['rank']
    achievements = request.form['achievements']
    bestrecord = request.form['bestrecord']
    file = request.files['profileimg']
    profilefilename = secure_filename(file.filename)
    file1 = request.files['filename1']
    filename1 = secure_filename(file1.filename)
    file2 = request.files['filename2']
    filename2 = secure_filename(file2.filename)
    file3 = request.files['filename3']
    filename3 = secure_filename(file3.filename)
    file4 = request.files['filename4']
    filename4 = secure_filename(file4.filename)
    file5 = request.files['filename5']
    filename5 = secure_filename(file5.filename)

    if file:
        file.save(os.path.join(
            app.config['UPLOAD_DIRECTORY'], profilefilename))

    if file1:
        file1.save(os.path.join(
            app.config['UPLOAD_DIRECTORY'], filename1))
        i = 1

    if file2:
        file2.save(os.path.join(
            app.config['UPLOAD_DIRECTORY'], filename2))
        i = i+1

    if file3:
        file3.save(os.path.join(
            app.config['UPLOAD_DIRECTORY'], filename3))
        i = i+1

    if file4:
        file4.save(os.path.join(
            app.config['UPLOAD_DIRECTORY'], filename4))
        i = i+1
    if file5:
        file5.save(os.path.join(
            app.config['UPLOAD_DIRECTORY'], filename5))
        i = i+1

    doc = {
        "fullname": fullname,
        "age": age,
        "phoneno": phoneno,
        "email": email,
        "achievements": achievements,
        "bestrecord": bestrecord,
        "profileimg": profilefilename,
        "filename1": filename1,
        "filename2": filename2,
        "filename3": filename3,
        "filename4": filename4,
        "filename5": filename5,
        "counter": i,

    }

    insert_result = db.athletes_data.insert_one(
        doc)  # insert a new document for user
    # tell the browser to make a request for the /home route

    docs = db.athletes_data.find({'_id': insert_result.inserted_id})
    return render_template('athleteprofile.html', docs=docs)


@ app.route("/sponsorprofile")
def sponsorprofile():
    """
    Route for GET request to sponsorprofile page
    Displays form for user
    """
    return render_template('sponsorprofile.html')

# sponsorprofileedit


@ app.route("/sponsorprofileedit")
def sponsorprofileedit():
    """
    Route for GET request to sponsorprofileedit page
    Displays form for user
    """
    return render_template('sponsorprofileedit.html')

# coach views players list


@ app.route("/viewathletes")
def view_athletes():
    """
    Route for GET request to viewathletes page
    Displays page where coach can view all athletes under them; only coach can access
    """
    # docs = db.athletes_data.find({"coach_id":username}).sort("athlete_name", -1)
    title = 'Athletes'
    return render_template('viewathletes.html', title=title)


# coach views players list
@ app.route("/viewplayers")
def view_players():
    """
    Route for GET request to viewathletes page
    Displays page where coach can view all athletes under them; only coach can access
    """
    # docs = db.athletes_data.find({"coach_id":username}).sort("athlete_name", -1)
    page = request.args.get('page', 1, type=int)
    doccount = db.athletes_data.find()
    docs = db.athletes_data.find().skip(12 * page).limit(12)
    count = len(list(doccount.clone()))
    title = 'Athletes'
    athlete_class = 'current'
    return render_template('viewplayers.html', title=title, docs=list(docs), count=count)


@ app.route("/viewsponsors")
def view_sponsors_():
    """
    Route for GET request to viewathletes page
    Displays page where coach can view all athletes under them; only coach can access
    """
    # docs = db.athletes_data.find({"coach_id":username}).sort("athlete_name", -1)
    docs = db.sponsor_data.find()
    title = 'Sponsors'
    sponsor_class = 'current'
    return render_template('viewsponsors.html', title=title, docs=list(docs))


@ app.route("/viewcoaches", methods=['GET'])
def view_coaches__():
    """
    Route for GET request to viewathletes page
    Displays page where coach can view all athletes under them; only coach can access
    """
    # docs = db.athletes_data.find({"coach_id":username}).sort("athlete_name", -1)
    docs = db.login_data.find()
    title = 'Coaches'
    coach_class = 'current'

    return render_template('viewcoaches.html', title=title, docs=list(docs))

# requests


@ app.route("/requests")
def requests():
    """
    Route for GET request to requests page
    Displays page where users can view all athlete requests
    """
    docs = db.request_data.find()
    return render_template('requests.html', docs=docs)


@ app.route("/ca_requests")
def ca_requests():
    """
    Route for GET request to requests page
    Displays page where coach or athletes can view or create athlete requests
    """
    return render_template('ca_requests.html')


'''
@app.route("/requests")
def requests():
    """
    Route for GET request to requests page
    Displays page where users can view all athlete requests
    """
    if user_type == 'athlete':
        return render_template('ca_requests.html')
    elif user_type == 'coach':
        return render_template('ca_requests.html')
    else:
        return render_template('requests.html')
'''


@ app.route("/createrequest")
def create_request():
    """
    Route for GET request to createrequest page
    Displays page where coach/athlete can create request
    """
    docs = db.athletes_data.find()
    return render_template('createrequest.html', docs=docs)


@ app.route("/createrequest", methods=['POST'])
def validate_create_request():
    """
    Route for GET request to createrequest page
    Displays page where coach/athlete can create request
    """
    athlete_id = ObjectId(request.form['athlete_id'])
    request_amt = request.form['request_amt']
    request_enddate = request.form['request_enddate']
    request_subject = request.form['request_subject']
    description = request.form['description']

    doc = {
        "athlete_id": athlete_id,
        "request_amt": request_amt,
        "request_enddate": request_enddate,
        "request_subject": request_subject,
        "description": description,

    }

    insert_result = db.request_data.insert_one(
        doc)  # insert a new document for user
    # tell the browser to make a request for the /home route

    return render_template('ca_requests.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
