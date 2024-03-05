
# import necessary packages
from flask import Flask, render_template, request, redirect, url_for, make_response, session, jsonify
from flask_session import Session
# from datetime import date
import db
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import smtplib
import imghdr
from email.message import EmailMessage

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import tempfile

# instantiate the app
app = Flask(__name__)

app.config['SECRET_KEY'] = "super_secret_key"
app.config['SESSION_TYPE'] = 'filesystem'

EMAIL_ADDRESS = "dronacharyaramesh@gmail.com"
EMAIL_PASSWORD = "fqnwskuchpsqjrax"

GENERIC_PASSWORD = "dronacharya"

Session(app)


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
    return render_template('Login.html', title=title)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

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
        {'username': username, 'password': password, 'status': 1})

    if user_data:
        user_type = user_data.get('user_type')
        user_id = user_data.get('_id')

        if user_type == 'athlete':
            session['id'] = user_id
            session['role'] = user_type
            session['username'] = username
            # Redirect athletes to their profile
            return redirect(url_for('athletetemplate'))
        elif user_type == 'coach' and username == 'superuser':
            session['role'] = user_type
            session['username'] = username
            return redirect(url_for('admintemplate', type=1))
        elif user_type == 'coach':
            # Redirect coaches to coachtemplate page
            session['id'] = user_id
            session['role'] = user_type
            session['username'] = username
            return redirect(url_for('coachtemplate'))

    else:
        # return error message in login page
        error = "Invalid username or password. Please try again."
        return render_template('Login.html', error=error)



@ app.route("/admintemplate")
def admintemplate():
    """
    Route for GET request to login page
    Displays form for user
    """
    title = 'Admin Template'
    type = str(request.args.get('type'))

    if type == "1":

        logins_with_status_zero = db.login_data.find(
            {"status": 0, "user_type": 'coach'})
        docs = []

        for login in logins_with_status_zero:
            coach_id = login.get("_id", None)
            if coach_id:
                coach = db.coach_data.find_one({"_id": ObjectId(coach_id)})
                if coach:
                    docs.append({
                        "firstname": coach.get("firstname", None),
                        "surname": coach.get("surname", None),
                        "_id": coach.get("_id", None),
                        "email": coach.get("email", None),
                        "profilepic": coach.get("profilepic", None),
                    })

        return render_template('admintemplate.html', title=title, docs=docs)
    elif type == "2":
        coachData = db.coach_data.find()
        athleteData = db.athletes_data.find()
        return render_template('admintemplate.html', coachData=coachData, athleteData=athleteData)
    elif type == "3":
        requestData = db.request_data.find({'status': 0})
        return render_template('admintemplate.html', requestData=list(requestData))
    else:
        return render_template('admintemplate.html')


@ app.route('/admintemplate', methods=['POST'])
def process_admintemplate():
    """
    Route for GET request to login page
    Displays form for user
    """
    title = 'Admin Template'
    type = request.form['type']
    coachID = request.form['coachID']
    if type == "1":
        acceptID = request.form['acceptID']
        if acceptID == "1":
            db.login_data.update_one({'_id': ObjectId(coachID)}, {
                "$set": {'status': 1}}, upsert=False)
            return redirect(url_for('admintemplate', title=title, type=1))
        elif acceptID == "0":
            emailID = request.form['emailID']
            if emailID != "":
                body = 'Your signup request has been rejected. Kindly contact admin'
                msg = EmailMessage()
                msg.set_content(body)
                msg['Subject'] = 'Your Signup Rejected'
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = emailID
    
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(msg)

            result = db.coach_data.delete_one({"_id": ObjectId(coachID)})
            result = db.login_data.delete_one({"_id": ObjectId(coachID)})
            if result.deleted_count > 0:
                return redirect(url_for('admintemplate', title=title, type=1, txtMsg=1))
    elif type == "2":
        coachID = request.form['coachID']
        athleteID = request.form['athleteID']
        db.coach_athlete_data.update_one({'atheleteID': ObjectId(athleteID)}, {
            "$set": {'coachID': coachID}}, upsert=False)
        return redirect(url_for('admintemplate', title=title, type=2, txtMsg=2))
    elif type == "3":
        athleteID = request.form['athleteID']
        requestID = request.form['requestID']
        requestSubject = request.form['requestSubject']
        requestAmt = request.form['requestAmt']
        requestEnddate = request.form['requestEnddate']
        contactName = request.form['contactName']
        contactPhone = request.form['contactPhone']

        athleteData = db.athletes_data.find_one(
            {"_id": ObjectId(athleteID)})
        athleteFirstname = athleteData.get("firstname", None)
        athleteSurname = athleteData.get("surname", None)

        coachData = db.coach_data.find_one(
            {"_id": ObjectId(coachID)})
        coachFirstname = coachData.get("firstname", None)
        coachSurname = coachData.get("surname", None)

        db.request_data.update_one({'_id': ObjectId(requestID)}, {
            "$set": {'status': 1}}, upsert=False)

        sponsors = db.sponsor_data.find({}, {'email': 1, 'companyname': 1})

        for sponsor in sponsors:
            recipient_email = sponsor['email']
            msg = EmailMessage()
            body = f"Hello {sponsor['companyname']}, \n\n Request your kind sponsorship for  {athleteFirstname}  {athleteSurname}. Below are the details- \n\n{requestSubject}\n\n{requestAmt}\n\n Please Contact {contactName}-{contactPhone} for further details.\n\n Thanking You,\n\n  {coachFirstname} {coachSurname}"
            msg.set_content(body)
            msg['Subject'] = requestSubject
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = recipient_email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)

        return redirect(url_for('admintemplate', title=title, type=3, txtMsg=3))
       

@ app.route("/sign_up_coach")
def sign_up_coach():
    """
    Route for GET request to sign_up_coach page
    Displays form for user
    """
    return render_template('sign_up_coach.html')


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
    file = request.files['profileimg']
    additional_info = request.form['additional_info']
    user_type = 'coach'

    profilefilename = secure_filename(file.filename)
    if file:
        fileVar = upload_image_drv(file)

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
        "profilepic": profilefilename,
        "additional_info": additional_info,
    }

    db.coach_data.insert_one(doc1)

    docs = db.athletes_data.find()
    title = 'Athletes'
    athlete_class = 'current'
    return redirect(url_for('login'))


def add_sponsor():
    """
    Route for POST requests to the sponsor pages.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    email = request.form['email']
    companyname = request.form['companyname']
    phoneno = request.form['phoneno']
    address = request.form['address']

    docsponsor = {
        "companyname": companyname,
        "email": email,
        "phoneno": phoneno,
        "address": address,
        # "created_at": date.today()
    }
    result = db.sponsor_data.insert_one(
        docsponsor)  # insert a new document for user

    # tell the browser to make a request for the /home route
    return result


def update_sponsor(sponsorID):
    """
    Route for POST requests to the sign up pages.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    email = request.form['email']
    companyname = request.form['companyname']
    phoneno = request.form['phoneno']
    address = request.form['address']

    docsponsor = {
        "companyname": companyname,
        "email": email,
        "phoneno": phoneno,
        "address": address,
        # "created_at": date.today()
    }
    result = db.sponsor_data.update_one(
        {"_id":  ObjectId(sponsorID)}, {"$set": docsponsor})
    return result


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

    athleteID = request.args.get('id')

    details = getathlete_coachdata(athleteID)
    return render_template('athleteprofile.html', details=details)



# athletejournal
@ app.route("/journal")
def journal():
    """
    Route for GET request to journal page
    Displays form for user
    """
    title = "Athlete Journal"
    athleteID = request.args.get('id')
    journalData = db.journal_data.find({"athleteID": ObjectId(athleteID)})
    return render_template('journal.html', title=title, journalData=journalData)



def getathlete_coachdata(athleteID):
    athlete = db.athletes_data.find_one({'_id': ObjectId(athleteID)})
    coach = get_coach_name(ObjectId(athleteID))
    return {
        "athlete": athlete,
        "coach": coach
    }


def athleteprofilesave():
    firstname = request.form['firstname']
    surname = request.form['surname']
    age = request.form['age']
    email = request.form['email']
    phoneno = request.form['phoneno']
    sport = request.form['sport']
    achievements = request.form['achievements']
    bestrecord = request.form['bestrecord']
    file = request.files['profileimg']
    profimg = request.form['profileimg1']
    filenm1 = request.form['filename11']
    filenm2 = request.form['filename12']
    filenm3 = request.form['filename13']
    filenm4 = request.form['filename14']
    filenm5 = request.form['filename15']

    if file:
        profilefilename = secure_filename(file.filename)
    else:
        profilefilename = profimg

    file1 = request.files['filename1']
    if file1:
        filename1 = secure_filename(file1.filename)
    else:
        filename1 = filenm1

    file2 = request.files['filename2']
    if file2:
        filename2 = secure_filename(file2.filename)
    else:
        filename2 = filenm2

    file3 = request.files['filename3']
    if file3:
        filename3 = secure_filename(file3.filename)
    else:
        filename3 = filenm3

    file4 = request.files['filename4']
    if file4:
        filename4 = secure_filename(file4.filename)
    else:
        filename4 = filenm4

    file5 = request.files['filename5']
    if file5:
        filename5 = secure_filename(file5.filename)
    else:
        filename5 = filenm5
    i = 0

    if file:
        fileVar = upload_image_drv(file)

    if file1:
        fileVar1 = upload_image_drv(file1)
        i = 1

    if file2:
        fileVar2 = upload_image_drv(file2)
        i = i+1

    if file3:
        fileVar3 = upload_image_drv(file3)
        i = i+1

    if file4:
        fileVar4 = upload_image_drv(file4)
        i = i+1
    if file5:
        fileVar5 = upload_image_drv(file5)
        i = i+1

    doc = {
        "firstname": firstname,
        "surname": surname,
        "age": age,
        "phoneno": phoneno,
        "email": email,
        "sport": sport,
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

    update_result = db.athletes_data.update_one(
        {"_id":  ObjectId(session['id'])}, {"$set": doc})  
    details = getathlete_coachdata(ObjectId(session['id']))
    return details





@ app.route("/sponsorprofile")
def sponsorprofile():
    """
    Route for GET request to sponsorprofile page
    Displays form for user
    """
    sponsorID = str(request.args.get('sponsorID'))
    sponsorName = str(request.args.get('sponsorName'))
    athlete_info = db.sponsor_request_data.distinct(
        'athleteID', {'sponsorID': sponsorID})
    unique_athlete_info = list(athlete_info)
    docs = []

    for athlete in unique_athlete_info:
        athlete_id = athlete
        if athlete_id:
            athleteData = db.athletes_data.find_one(
                {"_id": ObjectId(athlete_id)})
            if athleteData:
                docs.append({
                    "athleteID": athleteData.get("_id", None),
                    "firstname": athleteData.get("firstname", None),
                    "surname": athleteData.get("surname", None),
                    "profileimg": athleteData.get("profileimg", None),
                })

    return render_template('sponsorprofile.html', sponsorName=sponsorName, docs=docs)

# sponsorprofileedit


@ app.route("/sponsorprofileedit")
def sponsorprofileedit():
    """
    Route for GET request to sponsorprofileedit page
    Displays form for user
    """
    return render_template('sponsorprofileedit.html')

# coach views players list


def get_coach_name(athlete_id):
    # Query the db.coach_athlete collection for coach_id using athlete_id
    relation = db.coach_athlete_data.find_one({"athleteID": athlete_id})
    if not relation:
        return None

    coach_id = relation["coachID"]

    # Query the db.coach collection using coach_id to get coach's name
    coach = db.coach_data.find_one({"_id": ObjectId(coach_id)})
    if not coach:
        return None

    return coach

# coach views players list


@ app.route("/athletetemplate")
def athletetemplate():
    type = str(request.args.get('type'))
    if type == "1":
        title = "Change Password"
        return render_template('athletetemplate.html', title=title, type=1)
    elif type == "2":
        title = " Edit Profile"
        athlete = db.athletes_data.find_one(
            {"_id": ObjectId(session['id'])})
        coach = get_coach_name(ObjectId(session['id']))
        return render_template('athletetemplate.html', title=title, athlete=athlete, coach=coach, type=2)
    else:
        title = "Athlete Page"
        return render_template('athletetemplate.html', title=title)


@ app.route("/athletetemplate", methods=['POST'])
def validate_athletetemplate():
    type = request.form['type']
    athleteID = session['id']

    if type == "1":
        title = "Change Password"
        password = request.form['password']
        db.login_data.update_one({'_id': ObjectId(athleteID)}, {
            "$set": {'password': password}}, upsert=False)
        return redirect(url_for('athletetemplate', title=title, type=1, txtMsg=1))
    elif type == "2":
        details = athleteprofilesave()
        return render_template('athleteprofile.html', details=details)
    elif type == "3":
        subject = request.form['subject']
        journaldate = request.form['journaldate']
        description = request.form['description']
        doc = {
            "subject": subject,
            "journaldate": journaldate,
            "description": description,
            "athleteID": athleteID,
            "created_at":  datetime.now(),
        }
        insert_result = db.journal_data.insert_one(doc)
        return redirect(url_for('athletetemplate', type=3, txtMsg=2))
    



@ app.route("/viewathletes")
def view_athletes():
    """
    Route for GET request to viewathletes page
    Displays page where coach can view all athletes under them; only coach can access
    """

    coachID = request.args.get('coachID')
    page = request.args.get('page', 1, type=int)
    doccount = db.athletes_data.find()
    count = len(list(doccount.clone()))
    if count <= 12:
        docs = db.athletes_data.find()
    else:
        docs = db.athletes_data.find().skip(12 * page).limit(12)

    title = 'Our Athletes'
    return render_template('viewathletes.html', title=title, docs=list(docs), count=count)


@ app.route("/viewsponsors")
def view_sponsors_():
    """
    Route for GET request to viewathletes page
    Displays page where coach can view all athletes under them; only coach can access
    """
    # docs = db.athletes_data.find({"coach_id":username}).sort("athlete_name", -1)
    docs = db.sponsor_data.find()
    title = 'Our Sponsors'
    sponsor_class = 'current'
    return render_template('viewsponsors.html', title=title, docs=list(docs))


@ app.route("/viewcoaches", methods=['GET'])
def view_coaches__():
    """
    Route for GET request to viewathletes page
    Displays page where coach can view all athletes under them; only coach can access
    """
    # docs = db.athletes_data.find({"coach_id":username}).sort("athlete_name", -1)

    coaches = db.coach_data.find()

    # Filter coaches based on the login_data collection
    filtered_coaches = [
        coach for coach in coaches if db.login_data.find_one({'_id': coach['_id'], 'status': 1, 'user_type': 'coach'})
    ]
    title = 'Our Coaches'

    return render_template('viewcoaches.html', title=title, docs=list(filtered_coaches))

# requests


def requestCheckStatus(reqID, coachID, reqAmt):
    requestID = str(reqID)
    coachID = coachID
    requestdoc = db.sponsor_request_data.find({"requestID": requestID, "coachID": coachID})
    total_amount = 0
    reqAmt = int(reqAmt)
    
    for request_data in requestdoc:
        amount_received= int(request_data.get('request_amt_recieved'))
        total_amount += amount_received

    if total_amount >= reqAmt:
        return  "Completed"
    else:
        return  "Incomplete"
    

@ app.route("/coachtemplate")
def coachtemplate():
    type = str(request.args.get('type'))

    actionID = str(request.args.get('actionID'))

    if type == "1":
        title = "Add Athlete"
        return render_template('coachtemplate.html', title=title, type=1)
    elif type == "2":
        title = "Create Request"
        coachID = session['id']
        requestID = request.args.get('requestID')
        actionID = str(request.args.get('actionID'))

        athletes_dt = db.coach_athlete_data.find(
            {"coachID": coachID})
        docs = []

        for dt in athletes_dt:
            athlete_id = dt.get("athleteID", None)
            if athlete_id:
                athlete = db.athletes_data.find_one(
                    {"_id": ObjectId(athlete_id)})
                if athlete:
                    docs.append({
                        "firstname": athlete.get("firstname", None),
                        "surname": athlete.get("surname", None),
                        "_id": athlete.get("_id", None),
                        "email": athlete.get("email", None)
                    })
        if actionID == "2":
            title = " Edit Request"
            reqdoc = db.request_data.find_one({"_id": ObjectId(requestID)})
        else:
            title = "Create Request"
            reqdoc = None

        return render_template('coachtemplate.html', title=title, docs=docs, reqdoc=reqdoc, type=2)
    elif type == "3":
        coachID = session['id']
        title = "Pending Requests"
        docs = db.request_data.find({"coachID": coachID, "status": 0})

        return render_template('coachtemplate.html', title=title, docs=docs)
    elif type == "4":

        if actionID == "2":
            title = " Update Sponsor"
            sponsorID = str(request.args.get('sponsorID'))
            sponsordoc = db.sponsor_data.find_one({"_id": ObjectId(sponsorID)})
            return render_template('coachtemplate.html', title=title, sponsordoc=sponsordoc)
        else:
            title = "Add Sponsor"
            sponsordoc = None
            return render_template('coachtemplate.html', title=title, type=4, sponsordoc=sponsordoc)

    elif type == "5":
        coachID = session['id']
        title = "List of Sponsors"
        docs = db.sponsor_data.find()
        return render_template('coachtemplate.html', title=title, docs=docs)
    elif type == "6":
        coachID = session['id']
        approveddocs = db.request_data.find(
            {"coachID": coachID, "status": 1})
           # Initialize an empty list to store data
        data_list = []

        # Iterate over the documents
        for document in approveddocs:
            # Extract required fields from the document
            request_id = document.get('_id')
            coachID = ObjectId(document.get('coachID'))
            request_amt = document.get('request_amt')
            request_subject = document.get('request_subject')
            request_enddate = document.get('request_enddate')
            
            # Determine the status based on a condition
            status = requestCheckStatus(request_id,coachID,request_amt)

            # Create a dictionary containing the extracted fields and status
            data_item = {
                'request_id': request_id,
                'request_amt': request_amt,
                'request_subject': request_subject,
                'request_enddate': request_enddate,
                'status': status
            }

            # Append the data item to the list
            data_list.append(data_item)
        return render_template('coachtemplate.html', approveddocs=data_list)
    elif type == "7":
        coachID = session['id']
        requestID = request.args.get('requestID')
        actionID = request.args.get('actionID')
        requestdoc = db.request_data.find_one(
            {"_id": ObjectId(requestID), "status": 1})
        athletedoc = db.athletes_data.find_one(
            {'_id': ObjectId(requestdoc["athleteID"])})
        sponsordoc = list(db.sponsor_data.find())
        if actionID == "1":
            sponsorReqdoc = db.sponsor_request_data.find(
                {"requestID": requestID})
            sponsorReqdoc = list(sponsorReqdoc)
            sponsorIDdocs = []
            sponsorAmtdocs = []
            sponsorReqIDdocs = []

            for sponsor in sponsorReqdoc:
                sponsor_id = sponsor.get('sponsorID')
                if sponsor_id:
                    sponsorIDdocs.append(str(sponsor_id))
                    sponsorAmtdocs.append(
                        int(sponsor.get('request_amt_recieved')))
                    sponsorReqIDdocs.append(str(sponsor.get('_id')))
            sponsorAmt = sum(sponsorAmtdocs)
            amtRemaining = int(requestdoc.get("request_amt"))-sponsorAmt
        else:
            sponsorIDdocs = None
            sponsorAmtdocs = None
            sponsorReqIDdocs = None
            amtRemaining = None
        return render_template('coachtemplate.html', requestdoc=requestdoc, athletedoc=athletedoc, sponsordoc=sponsordoc, sponsorIDdocs=sponsorIDdocs, sponsorAmtdocs=sponsorAmtdocs, sponsorReqIDdocs=sponsorReqIDdocs, amtRemaining=amtRemaining)

    else:
        return render_template('coachtemplate.html')


@ app.route("/coachtemplate", methods=['POST'])
def validate_coachtemplate():
    type = request.form['type']
    print(type)
    coachID = session['id']

    if type == "1":
        title = "Add Athlete"
        username = request.form['username']
        password = GENERIC_PASSWORD
        user_type = 'athlete'

        # create a new document with the data the user entered
        doc = {
            "username": username,
            "password": password,
            "user_type": user_type,
            "status": 1,
            "created_at":  datetime.now(),
        }
        insert_result = db.login_data.insert_one(
            doc)  # insert a new document for user

        doc1 = {
            '_id': insert_result.inserted_id,
        }

        db.athletes_data.insert_one(doc1)
        doc2 = {
            'coachID': coachID,
            'athleteID': insert_result.inserted_id,
        }
        db.coach_athlete_data.insert_one(doc2)

        return redirect(url_for('coachtemplate', title=title, type=1, txtMsg=1))
    elif type == "2":
        title = "Create Request"
        athleteID = request.form['athlete_id']
        request_amt = request.form['request_amt']
        request_enddate = request.form['request_enddate']
        request_subject = request.form['request_subject']
        description = request.form['description']
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']
        actionID = request.form['actionID']
        requestID = request.form['requestID']

        doc = {
            "coachID": coachID,
            "athleteID": athleteID,
            "request_amt": request_amt,
            "request_enddate": request_enddate,
            "request_subject": request_subject,
            "description": description,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "status": 0,

        }
        if actionID == "2":
            update_result = db.request_data.update_one({'_id': ObjectId(requestID)}, {
                "$set": doc}, upsert=False)
            return redirect(url_for('coachtemplate', title=title, type=3))
        else:
            insert_result = db.request_data.insert_one(
                doc)  # insert a new document for user
        # tell the browser to make a request for the /home route
            return redirect(url_for('coachtemplate', title=title, type=2, txtMsg=2))
    elif type == "4":
        title = "Add Sponsor"
        actionID = request.form['actionID']
        sponsorID = request.form['sponsorID']
        if actionID == "2":
            result = update_sponsor(sponsorID)
            return redirect(url_for('coachtemplate', title=title, type=5))
        else:
            result = add_sponsor()
            return redirect(url_for('coachtemplate', title=title, type=4, txtMsg=4))
        
    elif type == "6":
        actionID = request.form['actionID']
        requestID = request.form['requestID']
        result = db.request_data.delete_one({"_id":ObjectId(requestID)})
        result1 = db.sponsor_request_data.delete_many({"requestID": requestID})

        if result.deleted_count == 1:
            txtMsg = "1"
        else:
            txtMsg = "0"
        return redirect(url_for('coachtemplate', type=6, txtMsg=txtMsg))

    elif type == "7":
        athleteID = request.form['athleteID']
        requestID = request.form['requestID']
        actionID = request.form['actionID']
        amtRecieved1 = request.form['amtRecieved1']
        if amtRecieved1:
            sponsorID1 = request.form['sponsorID1']
            sponsorReqID1 = request.form['sponsorReqID1']
            i = 1
        amtRecieved2 = request.form['amtRecieved2']
        if amtRecieved2:
            sponsorID2 = request.form['sponsorID2']
            sponsorReqID2 = request.form['sponsorReqID2']
            i = i+1
        amtRecieved3 = request.form['amtRecieved3']
        if amtRecieved3:
            sponsorID3 = request.form['sponsorID3']
            sponsorReqID3 = request.form['sponsorReqID3']
            i = i+1
        amtRecieved4 = request.form['amtRecieved4']
        if amtRecieved4:
            sponsorID4 = request.form['sponsorID4']
            sponsorReqID4 = request.form['sponsorReqID4']
            i = i+1
        amtRecieved5 = request.form['amtRecieved5']
        if amtRecieved5:
            sponsorID5 = request.form['sponsorID5']
            sponsorReqID5 = request.form['sponsorReqID5']
            i = i+1
        n = 1
        for n in range(1, 6):
            request_txt = "amtRecieved" + str(n)
            request_amt = request.form[request_txt]
            sponsor_txt = "sponsorID" + str(n)
            sponsorID = request.form[sponsor_txt]
            sponsorReq_txt = "sponsorReqID" + str(n)
            sponsorReqID = request.form[sponsorReq_txt]

            if request_amt != "":
                doc = {
                    "coachID": coachID,
                    "athleteID": athleteID,
                    "sponsorID": sponsorID,
                    "requestID": requestID,
                    "request_amt_recieved": request_amt,
                }
                if actionID == "1":

                    if sponsorReqID:
                        sponsReqID = sponsorReqID
                        filter = {"_id": ObjectId(sponsReqID)}
                    else:
                        filter = {}
                    update_result = db.sponsor_request_data.update_one(
                        filter, {"$set": doc}, upsert=False)
                else:
                    insert_result = db.sponsor_request_data.insert_one(doc)
                n = n+1

        return redirect(url_for('coachtemplate', type=6))


@ app.route("/requests")
def allrequests():
    """
    Route for GET request to requests page
    Displays page where users can view all athlete requests
    """
    title = "Requests"
    docs = db.request_data.find({"status": 1})
     
    return render_template('requests.html', docs=docs, title=title)

 
 


@ app.route("/requestdetails")
def requestdetails():
    """
    Route for GET request to requests page
    Displays page where users can view all athlete requests
    """
    title = "Requests"
    requestID = request.args.get('requestID')
    requestdata = db.request_data.find_one({"_id": ObjectId(requestID)})
    requestdoc = db.sponsor_request_data.distinct(
        'sponsorID', {"requestID": requestID})
    requestdoc = list(requestdoc)
    docs = []
    if len(requestdata) > 0:
        athleteID = requestdata.get("athleteID")
        athleteData = db.athletes_data.find_one(
            {"_id": ObjectId(athleteID)})
    for sponsor in requestdoc:
        sponsor_id = sponsor
        if sponsor_id:
            sponsorData = db.sponsor_data.find_one(
                {"_id": ObjectId(sponsor_id)})

            if sponsorData:
                docs.append({
                    "sponsorID": sponsorData.get("_id", None),
                    "companyname": sponsorData.get("companyname", None),

                })
    return render_template('requestdetails.html', docs=docs, requestdata=requestdata, athleteData=athleteData)


@ app.route("/createrequest")
def create_request():
    """
    Route for GET request to createrequest page
    Displays page where coach/athlete can create request
    """
    docs = db.athletes_data.find()
    return render_template('createrequest.html', docs=docs)


@app.route('/uploadImage')
def uploadImage():
    image_url = get_image_url('image1.jpg')
    return render_template('uploadImage.html', image_url=image_url)


def create_drive_service():
    credentials_path = 'gdrvcredentials.json'
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service



def get_image_url(imgName):
    drive_service = create_drive_service()
    IMAGE_FILENAME = imgName
    DRIVE_FOLDER_ID = '1O17snc953dQDn_RX_CZvHR6NUFYBkVTj'

    try:
        # Search for the image file by name in the specified folder
        # Define the path to your Google Drive API credentials JSON file

        results = drive_service.files().list(
            q=f"'{DRIVE_FOLDER_ID}' in parents and name = '{IMAGE_FILENAME}'", fields="files(id, webContentLink)").execute()

        image_url = None
        for file in results.get('files', []):
            image_url = file.get('webContentLink')
            if "&export=download" in image_url:
                 image_url = image_url.replace("&export=download", "")
            
            image_url = image_url.replace("uc", "thumbnail")
            break

        return image_url
    except HttpError as e:
        print(f"Google Drive API error: {e}")
        return None


app.jinja_env.globals.update(get_image_url=get_image_url)



def upload_image_drv(imgFile):
    drive_service = create_drive_service()
    temp_dir = tempfile.TemporaryDirectory()
    temp_file = imgFile
    temp_path = os.path.join(temp_dir.name, temp_file.filename)
    temp_file.save(temp_path)

    file_metadata = {
        'name': temp_file.filename,
        'parents': ['1O17snc953dQDn_RX_CZvHR6NUFYBkVTj']
    }

    media = MediaFileUpload(
        temp_path,
        mimetype='image/jpg'
    )
    try:
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return f'Image uploaded with file ID: {uploaded_file.get("id")}'
    except Exception as e:
        # Handle any errors that occur during the upload process
        return jsonify({"error": str(e)})





if __name__ == '__main__':
    app.run(debug=True, port=8000)
