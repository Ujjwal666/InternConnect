import os
import requests
import bcrypt
import secrets
from flask import Flask
from flask import render_template
from flask import request, redirect, session, url_for
from flask_pymongo import PyMongo


# -- Initialization section --
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'database'

secret_key = os.environ.get('MONGO_URI')
app.config['MONGO_URI'] = "mongodb+srv://admin:dStKsL8tINe3LD54@cluster0.6ah66.mongodb.net/InternConnect?retryWrites=true&w=majority"

#Initialize PyMongo
mongo = PyMongo(app)

# mongo.db.create_collection("user_profile")

# -- Routes section --
# INDEX Route
@app.route('/')
@app.route('/index')
def index():
    return(render_template('index.html'))


#SIGNUP Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        users = mongo.db.user_profile
        #search for email in database
        existing_user = users.find_one({'email': request.form['email']})

        #if user not in database
        if not existing_user:
            name = request.form['name']
            email = request.form['email']
            #encode password
            password = (request.form['password']).encode("utf-8")
            zip_code = request.form['zip_code']

            #hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)

            # add new user to database

            users.insert_one({'name': name, 'email': email, 'password': hashed, 'zip_code': zip_code})

            #store email in session
            session['email'] = request.form['email']
            return redirect(url_for('index'))

        else:
            return 'Useremail already registered.  Try logging in.'
    
    else:
        return render_template('signup.html')
    

@app.route('/nearby')
def nearby():
    users = mongo.db.user_profile
    if session:
        email = session['email']
    else:
        email = None 
    user = users.find_one({'email': email})
    zip_code = user['zip_code']
    distance = request.form['distance']

 
    api_url = f"https://www.zipcodeapi.com/rest/wGb42N8fhmmLTspUBSjLwaxNaZrL6YL59kCJ2Yu38P75IDJ5F8NlNhlzywJQlreg/radius.json/{zip_code}/{distance}/mile"
    response = requests.get(api_url)

    for item in response.json()['zip_codes']:
        print(item)
    return(render_template('nearby.html', zip_code=zip_code, distance=distance))

# @app.route('/how_it_works')
# def how_it_works():
#     return (render_template('howItWorks.html'))

# @app.route('/login')
# def login():
#     return (render_template('login.html'))

# @app.route('/signup')
# def signup():
#     return (render_template('signup.html'))