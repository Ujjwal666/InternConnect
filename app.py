import os
from flask import Flask
from flask import render_template
from flask import request, redirect
import requests
import folium

# -- Initialization section --
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'database'

secret_key = os.environ.get('MONGO_URI')
app.config['MONGO_URI'] = "mongodb+srv://project3:MZntQQBGfwYCMd9W@cluster0.ioc2g.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

# -- Routes section --
zip_code = 11412
distance = 3
units = "mile"

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

@app.route('/nearby', methods=['GET', 'POST'])
def nearby():
    if request.method == "POST":
        zip_code = request.form['zipcode']
        api_url = "https://www.zipcodeapi.com/rest/DemoOnly008LKWfhqkCgkxq2SYsKmXAOk8Y1Ww4TdEqeHjNj4XaDEegU73V9FAf9/radius.json/{{zip_code}}/{{distance}}/{{units}}"
        response = requests.get(api_url)
        nearby_zip = response.json()
    
        return (render_template('nearby.html'))