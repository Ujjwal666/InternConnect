import os
import requests
import bcrypt
import secrets
import folium
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
        if item['zip_code'] != str(zip_code):
            print(f"{item['zip_code']} is {item['distance']} miles away from {zip_code}")
    return(render_template('nearby.html', zip_code=zip_code, distance=distance))

@app.route('/how_it_works')
def how_it_works():
    return (render_template('howItWorks.html'))

@app.route('/login')
def login():
    return (render_template('login.html'))

# @app.route('/signup')
# def signup():
#     return (render_template('signup.html'))