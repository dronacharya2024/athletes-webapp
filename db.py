from flask import Flask
from flask_pymongo import pymongo
from app import app
import certifi

#connect to mongodb database
CONNECTION_STRING = "mongodb+srv://anikaroy:8DTDLlwCsv7R9bTC@cluster0.gelqpzw.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
db = client.get_database('athletes_web_app')
user_collection = pymongo.collection.Collection(db, 'user_collection')
