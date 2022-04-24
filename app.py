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
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

#Initialize PyMongo
mongo = PyMongo(app)

app.secret_key = secrets.token_urlsafe(16)
#mongo.db.create_collection("user_profile")

# -- Routes section --
# INDEX Route
@app.route('/')
@app.route('/index')
def index():
    if (os.path.exists("./templates/map.html")):
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
    is_nearby = False    
    for z in zcdb.get_zipcodes_around_radius(zip_code, 5):
        # print(z.zip)
        for user in db_user:
            # print(user)
            user_info = f"Name: {user['name']}\nEmail: {user['email']}\nAddress: {user['address']}\nCompany: {user['company']}\n+Hobbies/Interests: {user['interests']}"
            if z.zip == user['zip_code'] and z.zip != session['zip_code']:
                for interest in split_session:
                    # print("interest",user_split)
                    if interest in user['interests']:
                        # print("interest user",user_split)
                        if session['company'] == user['company']:
                            is_nearby = True
                            #if zipcode,company,interest matches -- red color
                            a = nom.geocode(z.zip)
                            folium.Marker(
                                location=[a[1][0], a[1][1]],
                                popup=user_info,
                                tooltip=user['name'],
                                icon=folium.Icon(color="red", icon="info-sign"),
                            ).add_to(map)
                        else:
                            #if zipcode,interest matches -- black color
                            # print(user['name'],user['company'],session['company'])
                            is_nearby = True
                            a = nom.geocode(z.zip)
                            folium.Marker(
                                location=[a[1][0], a[1][1]],
                                popup=user_info,
                                tooltip=user['name'],
                                icon=folium.Icon(color="black", icon="info-sign"),
                            ).add_to(map)
                    elif session['company'] == user['company']:
                        is_nearby = True
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
                        is_nearby = True
                        # print("found", z.zip)
                        a = nom.geocode(z.zip)
                        folium.Marker(
                            location=[a[1][0], a[1][1]],
                            popup=user_info,
                            tooltip=user['name'],
                        ).add_to(map)
    map.save('templates/map.html')
    
    return(render_template('nearby.html', zip_code=zip_code, distance=distance, is_nearby=is_nearby))

@app.route('/map')
def map():
    return render_template('map.html')
    
@app.route('/howItWorks')
def how_it_works():
    return render_template('howItWorks.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile(): # allow user to add a picture, view and update data, and input their roommate preference
    users = mongo.db.users
    if session:
        email = session['email']
        user = users.find_one({"email":email})
        name = user['name']
        address = user['address']
        zip_code = user['zip_code']
        company = user['company']
        interests = user['interests']
    else:
        email = None
    if request.method == "POST":

        interests = user['interests']
        users.update_one({"email":email}, { "$set": {"interests": interests } })

        url = request.form['url']
        pic = { "$set": {"pic": url } }
        users.update_one({"email":email}, pic)

        roomates = request.form['roomates']
        rm = { "$set": {"roomates": str(roomates) } }
        users.update_one({"email":email}, rm)
        
        print("piccccc",url)
        return render_template('profile.html', name = name, email = email, address = address, zip_code = zip_code, company = company, interests = interests, pic = url, roomates=roomates)
    return render_template('profile.html', name = name, email = email, address = address, zip_code = zip_code, company = company, interests = interests)
@app.route('/profile_picture')
def profile_picture():
    users = mongo.db.users
    if request.method == "GET":
        
        if session:
            email = session['email']
            user = users.find_one({"email":email})

            return render_template('profile_pciture.html', user = user)
        else:
            email = None
    else:
        url = request.form['url']
        user = users.find_one({"email":email})
        pic = { "$set": {"img": url } }

        users.update_one(user, pic)
        

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

            pic = "360_F_346839683_6nAPzbhpSkIpb8pmAwufkC7c5eD7wYws.jpg"

            #encode password
            password = (request.form['password']).encode("utf-8")

            #hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)

            # add new user to database

            users.insert_one({'email': email, 'password': hashed, 'name':name, 'address':address, 'zip_code':zip_code, 'company': company, 'interests':interests, 'pic': pic})

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


@app.route('/logout')
def logout():
    #clear email from session data
    session.clear()
    return redirect(url_for('index'))