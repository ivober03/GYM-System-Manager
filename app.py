import os

from cs50 import SQL
from datetime import datetime
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, json, jsonify, render_template, request, session, url_for, make_response
from flask_session import Session
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from collections import namedtuple

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6g7h8i9j0'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///manager.db")


@app.route('/')
def home():
    # check if the user is loged in
    if 'users' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')


@app.route("/index")
def index():
    """Load index page"""

    # select habits, users, and sections data
    #habits = db.execute(
        #"SELECT habits.*, sections.title as section_title "
        #"FROM habits "
        #"JOIN sections ON habits.section_id = sections.id "
        #"WHERE habits.user_id = :id",
        #id=session["user_id"]
    #)

    users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])

    # Retrieve specific habit data
    #habit_id = request.args.get("habit_id")  # Get the habit ID of the request
    #habit = None
    #if habit_id:
        #habit = db.execute("SELECT * FROM habits WHERE id = :id", id=habit_id).fetchone()


    return render_template("index.html", users=users)


@app.route('/plans', methods=['GET' ])
def plans():
    """Show plans"""

    users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    return render_template("plans.html", users=users)

@app.route('/create_new_plan', methods=['POST'])
def create_new_plan():
    """Create new plan """

    # Get form data
    plans_name = request.form['planName']
    plans_price = int(request.form['planPrice'])
    plans_days = int(request.form['days'])
    plans_description = request.form['planDescription']

    
    
    

    # Insertar datos del nuevo plan en la base de datos
    db.execute("INSERT INTO plans (name, days, price, description) "
               "VALUES (:plans_name, :plans_days, :plans_price,  :plans_description)",
                plans_name=plans_name, plans_days=plans_days, plans_price=plans_price,
                plans_description=plans_description)

    # Redirigir al usuario a la página de índice
    return redirect(url_for('plans'))

@app.route('/memberships', methods=['GET' ])
def memberships():
    """Show memberships"""

    users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    return render_template("memberships.html", users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """login"""

    # Forget any user_id
    session.clear()

    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate form inputs
        if not email or not password:
            error_message = "Must provide email and password."
            return render_template("login.html", password_error=error_message)

        # Query database for user with the provided email
        row = db.execute('SELECT * FROM users WHERE email = ?', email)

        # Ensure email exists and password is correct
        if len(row) != 1 or not check_password_hash(row[0]["password_hash"], password):
            error_message = "Invalid email and/or password."
            return render_template("login.html", password_error=error_message)

        # Remember which user has logged in
        session["user_id"] = row[0]["id"]

        # Redirect user to home page
        return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    """logout"""


    # Delete the user's session
    session.clear()

    # Redirect the user to the login page
    return redirect(url_for('login'))


@app.route('/check_email', methods=['POST'])
def check_email():
    """check if the email is in the database"""


    email = request.json['email']
    rows = db.execute("SELECT * FROM users WHERE email = :email", email=email)

    return json.dumps({ 'exists': len(rows) > 0 })


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # save user data
        name = request.form.get("name")
        password_hash = generate_password_hash(request.form.get("password"))
        email = request.form.get("email")

        # insert user data into the database
        db.execute("INSERT INTO users (name, password_hash, email) VALUES ( :name, :password_hash, :email)",
                 name=name, password_hash=password_hash, email=email)

        # get the ID of the inserted user
        user_id = db.execute("SELECT id FROM users WHERE email = :email", email=email)[0]["id"]


        # Redirect user to login form
        flash("Registration completed successfully!")
        return redirect(url_for('login'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
