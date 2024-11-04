from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
import sqlite3
import os
from flask_bcrypt import Bcrypt 
from ml_prediction import predict
from wrapper import get_advice, find_volunteering

app = Flask(__name__)
bcrypt = Bcrypt(app) 
conn = sqlite3.connect('database.db', check_same_thread=False)
db = conn.cursor()
app.config["SECRET_KEY"] = os.urandom(24)
db.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
             )''')
db.execute('''CREATE TABLE IF NOT EXISTS profile (
                id INT NOT NULL,
                numbers TEXT,
                advice TEXT,
                volunteer TEXT,
                profile_id INTEGER PRIMARY KEY AUTOINCREMENT
            );''')

conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/demographics_test', methods = ['GET', 'POST'])
def demographics_test():
    
    if not session.get('loggedin', False):
        return redirect('/login')
    if request.method == "POST":
        age = int(request.form['age'])
        county = request.form['county']
        employment = request.form['employment']
        income = int(request.form['income'])
        education = request.form['education']
        ethnicity = request.form['ethnicity']

        # Check if all fields are filled
        if not age or not county or not employment or not education:
            return render_template('apology.html', message = "Please fill out all fields.")
        #send parameters to ml model
        values = predict(county, ethnicity, income, employment, education, age)
        values = '|'.join(map(str, values))
        #send response to gpt
        advice = get_advice(values)
        #get gpt response
        response = find_volunteering(county, values)
        #log gpt response in database
        db.execute("INSERT INTO profile (id, numbers, advice, volunteer) VALUES (?, ?, ?, ?)", (session['user_id'], values, advice, response))
        conn.commit()
        return redirect('/profile')
    if request.method == 'GET':
        return render_template('demographics_test.html')
    else:
        return redirect('/')
    
@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if not session.get('loggedin', False):
        return redirect('/login')
    profile_data = db.execute("SELECT * FROM profile WHERE id = ? ORDER BY profile_id DESC LIMIT 1", (session['user_id'],)).fetchone()
    if not profile_data:
        return render_template('apology.html', message = "Please take the demographics test first.")
    print(profile_data)
    dictionaries = []
    for event in profile_data[3].split("\n"):
        lon, lat, website, desc = event.split("|")
        dictionaries.append({"coords": [float(lon), float(lat)], "website": website, "description": desc})
    categories = ["Low Life Expectancy", "Expected Building Loss Rate", "Flood Risk", "Wildfire Risk", "Traffic Proximity", "Clean Air Quality", "Waste Water Pollutants"]
    numbers = [max(2, min(98, 100 - int(float(num)))) for num in profile_data[1].split('|')]
    return render_template('profile.html', numbers = numbers, advice = profile_data[2].split('|'), volunteering = dictionaries, categories = categories)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':#user login request
        username = request.form['username']
        password = request.form['password']
        
        if username == "" or password == "":
            return render_template('apology.html', message = "Please fill in all fields")
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and bcrypt.check_password_hash(user[2], password):
            session['loggedin'] = True
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return render_template('apology.html', message = "Invalid username or password")
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session['loggedin'] = False
    session['user_id'] = None
    return redirect('/')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmation = request.form['confirmation']
        if len(username) > 20:
            return render_template('apology.html', message = "Username must be less than 32 characters")
        if len(password) > 64:
            return render_template('apology.html', message = "Password must be less than 128 characters")
        if password != confirmation:
            return render_template('apology.html', message = "Passwords do not match")
        elif db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall():
            return render_template('apology.html', message = "Username is already taken")
        elif username == "" or password == "" or confirmation == "":
            return render_template('apology.html', message = "Please fill in all fields")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            session['loggedin'] = True
            session['user_id'] = user[0]
            return redirect('/')
    else:
        return render_template('register.html')
    
@app.route('/apology')
def apology():
    return render_template('apology.html')

if __name__ == '__main__':
    app.run(debug=True)