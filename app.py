
#import necessary packages
from flask import Flask, render_template, request, redirect, url_for, make_response
import pymongo

# instantiate the app
app = Flask(__name__)

'''
# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mode
'''

#connect to mongodb database
CONNECTION_STRING = "mongodb+srv://anikaroy:<8DTDLlwCsv7R9bTC>@cluster0.gelqpzw.mongodb.net/"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('flask_mongodb_atlas')
user_collection = pymongo.collection.Collection(db, 'user_collection')