
#import necessary packages
from flask import Flask
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

#log in page
def log_in():
    """
    Route for log in page
    """
    return

if __name__ == '__main__':
    app.run(debug = True, port=8000)