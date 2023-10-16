from flask_pymongo import pymongo
import certifi

# connect to mongodb database
connection_string = "mongodb+srv://anikaroy:8DTDLlwCsv7R9bTC@cluster0.gelqpzw.mongodb.net/?retryWrites=true&w=majority"

cluster = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
db = cluster["athletes_web_app"]
athletes_data = db["athletes_data"]
coach_data = db["coach_data"]
sponsor_data = db["sponsor_data"]
login_data = db["login_data"]
request_data = db["request_data"]
coach_athlete_data = db["coach_athlete_data"]
sponsor_request_data = db["sponsor_request_data"]
