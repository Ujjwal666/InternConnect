import os
import requests
import bcrypt
import secrets
import folium
from flask import Flask
from flask import render_template
from flask import request, redirect, session, url_for
from flask_pymongo import PyMongo
import folium
from geopy.geocoders import ArcGIS
from pyzipcode import ZipCodeDatabase
import requests

# -- Initialization section --
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'database'

secret_key = os.environ.get('MONGO_URI')
app.config['MONGO_URI'] = "mongodb+srv://admin:WSeGRxmWVLbiFBpR@cluster0.oa59d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

#Initialize PyMongo
mongo = PyMongo(app)

app.secret_key = secrets.token_urlsafe(16)
# mongo.db.create_collection("user_profile")

# -- Routes section --
# INDEX Route
@app.route('/')
@app.route('/index')
def index():
    if (os.path.exists("./templates/map.html")):
        print("DONEEEEEEEE")
        os.remove("./templates/map.html")
    return (render_template('index.html'))


@app.route('/nearby',methods=['GET', 'POST'])
def nearby():
    zip_code = None
    distance = 3   
    if request.method == "POST":
        zip_code = request.form['zipcode']
    else:
        zip_code = session['zip_code']    
    # users = mongo.db.user_profile
    # if session:
    #     email = session['email']
    # else:
    #     email = None 
    # user = users.find_one({'email': email})
    # zip_code = user['zip_code']
    # distance = request.form['distance']
    nom = ArcGIS()

    main = nom.geocode(zip_code)

    map = folium.Map(
        location=[main[1][0], main[1][1]]
    )
    # api_url = f"https://www.zipcodeapi.com/rest/wGb42N8fhmmLTspUBSjLwaxNaZrL6YL59kCJ2Yu38P75IDJ5F8NlNhlzywJQlreg/radius.json/{zip_code}/{distance}/mile"
    # response = requests.get(api_url)
    # for item in response.json()['zip_codes']:
    #     if item['zip_code'] != str(zip_code):
    #         print(f"{item['zip_code']} is {item['distance']} miles away from {zip_code}")
    zcdb = ZipCodeDatabase()
    db_user = list(mongo.db.users.find({}))
    # print(list(db_user))
    split_session = session['interests'].split(',')
    # print(split_session)
    for z in zcdb.get_zipcodes_around_radius(zip_code, 5):
        # print(z.zip)
        for user in db_user:
            user_info = f"Name: {user['name']}\nEmail: {user['email']}\nAddress: {user['address']}\nCompany: {user['company']}\n+Hobbies/Interests: {user['interests']}"
            if z.zip == user['zip_code'] and z.zip != session['zip_code']:
                for interest in split_session:
                    # print("interest",user_split)
                    if interest in user['interests']:
                        # print("interest user",user_split)
                        if session['company'] == user['company']:
                            #if zipcode,company,interest matches -- red color
                            a = nom.geocode(z.zip)
                            folium.Marker(
                                location=[a[1][0], a[1][1]],
                                popup=user_info,
                                tooltip=user['name'],
                                icon=folium.Icon(color="red", icon="info-sign"),
                            ).add_to(map)
                        else:
                            #if zipcode,interest matches -- yellow color
                            # print(user['name'],user['company'],session['company'])
                            a = nom.geocode(z.zip)
                            folium.Marker(
                                location=[a[1][0], a[1][1]],
                                popup=user_info,
                                tooltip=user['name'],
                                icon=folium.Icon(color="yellow", icon="info-sign"),
                            ).add_to(map)
                    elif session['company'] == user['company']:
                        #if zipcode,company matches -- green color
                        # print(user['name'],user['company'],session['company'])                            
                        a = nom.geocode(z.zip)
                        folium.Marker(
                            location=[a[1][0], a[1][1]],
                            popup=user_info,
                            tooltip=user['name'],
                            icon=folium.Icon(color="green", icon="info-sign"),
                        ).add_to(map)
    
                    else:
                        # print("found", z.zip)
                        a = nom.geocode(z.zip)
                        folium.Marker(
                            location=[a[1][0], a[1][1]],
                            popup=user_info,
                            tooltip=user['name'],
                        ).add_to(map)

    map.save('templates/map.html')
    
    return(render_template('nearby.html', zip_code=zip_code, distance=distance))

@app.route('/map')
def map():
    return render_template('map.html')
    
@app.route('/howItWorks')
def how_it_works():
    return render_template('howItWorks.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        users = mongo.db.users
        #search for email in database
        login_user = users.find_one({'email': request.form['email']})

        #if email in database
        if login_user:
            db_password = login_user['password']
            password = request.form['password'].encode("utf-8")
            #compare email in database to email submitted in form
            if bcrypt.checkpw(password, db_password):
                #store email in session
                session['email'] = request.form['email']
                session['zip_code'] = login_user['zip_code']
                session['interests'] = login_user['interests']
                session['company'] = login_user['company']
                return redirect(url_for('index'))
            else:
                return render_template('login.html',error="Invalid email/password combination")
        else:
            return render_template('login.html',error="User not found")
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        users = mongo.db.users
        #search for email in database
        existing_user = users.find_one({'email': request.form['email']})

        #if user not in database
        if not existing_user:
            email = request.form['email']
            name = request.form['name']
            address = request.form['address']
            zip_code = request.form['zip_code']
            company = request.form['company']
            interests = request.form['interests']
            #encode password
            password = (request.form['password']).encode("utf-8")

            #hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)

            # add new user to database

            users.insert_one({'email': email, 'password': hashed, 'name':name, 'address':address, 'zip_code':zip_code, 'company': company, 'interests':interests})

            #store email in session
            session['email'] = request.form['email']
            session['zip_code'] = request.form['zip_code']
            session['interests'] = request.form['interests']
            session['company'] = request.form['company']
            return redirect(url_for('index'))

        else:
            return 'Useremail already registered.  Try logging in.'
    
    else:
        return render_template('signup.html')