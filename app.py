import os
from flask import Flask
from flask import render_template
from flask import request, redirect
from flask_pymongo import PyMongo


# -- Initialization section --
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'database'

secret_key = os.environ.get('MONGO_URI')
app.config['MONGO_URI'] = "mongodb+srv://project3:MZntQQBGfwYCMd9W@cluster0.ioc2g.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

#Initialize PyMongo
mongo = PyMongo(app)

# mongo.db.create_collection("library")

# -- Routes section --
# INDEX Route
@app.route('/')
@app.route('/index')
def index():
    return (render_template('index.html'))

@app.route('/how_it_works')
def how_it_works():
    return (render_template('howItWorks.html'))

@app.route('/login')
def login():
    return (render_template('login.html'))

@app.route('/signup')
def signup():
    return (render_template('signup.html'))