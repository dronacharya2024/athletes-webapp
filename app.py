
#import necessary packages
from flask import Flask
#import pymongo
from flask_pymongo import pymongo

# instantiate the app
app = Flask(__name__)

@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"

'''
# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mode
'''
'''
#connect to mongodb database
CONNECTION_STRING = "mongodb+srv://anikaroy:<8DTDLlwCsv7R9bTC>@cluster0.gelqpzw.mongodb.net/"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('flask_mongodb_atlas')
user_collection = pymongo.collection.Collection(db, 'user_collection')
'''

import certifi

cluster = pymongo.MongoClient("mongodb+srv://anikaroy:8DTDLlwCsv7R9bTC@cluster0.gelqpzw.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())
db = cluster["athletes_web_app"]
collection = db["athletes_data"]


#import db

#test to insert data to the data base
@app.route("/test")
def test():
    #db.db.collection.insert_one({"name": "John"})
    collection.insert_one({"name": "John"})
    return "Connected to the data base!"

if __name__ == '__main__':
    app.run(debug = True, port=8000)