from flask_pymongo import pymongo
import certifi

#connect to mongodb database
connection_string = "mongodb+srv://anikaroy:8DTDLlwCsv7R9bTC@cluster0.gelqpzw.mongodb.net/?retryWrites=true&w=majority"

cluster = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
db = cluster["athletes_web_app"]
collection = db["athletes_data"]