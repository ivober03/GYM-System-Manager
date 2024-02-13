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


@app.route('/plans', methods=['GET'])
def plans():
    """Show plans"""

    # Select plans and user data

    plans = db.execute("SELECT * FROM plans WHERE user_id = :id", id=session["user_id"])
    user = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
    
    return render_template("plans.html", user=user, plans=plans)


@app.route('/delete_plan/<int:plan_id>', methods=['POST'])
def delete_habit(plan_id):
    """Delete plan"""

    # get element ID
    plan = db.execute("SELECT * FROM plans WHERE id = :plan_id", plan_id=plan_id)

    if len(plan) == 1:
        db.execute("DELETE FROM plans WHERE id = :plan_id", plan_id=plan_id)

    # Redirect user to index page
    return redirect(url_for('plans'))



@app.route('/create_new_plan', methods=['POST'])
def create_new_plan():
    """Create new plan """

    # Get form data
    plan_name = request.form['planName']
    plan_price = int(request.form['planPrice'])
    plan_days = int(request.form['days'])
    plan_description = request.form['planDescription']

    # Insertar datos del nuevo plan en la base de datos
    db.execute("INSERT INTO plans (name, days, price, description, user_id) "
               "VALUES (:plan_name, :plan_days, :plan_price,  :plan_description, :user_id)",
                plan_name=plan_name, plan_days=plan_days, plan_price=plan_price,
                plan_description=plan_description, user_id=session["user_id"])

    # Redirigir al usuario a la página de índice
    return redirect(url_for('plans'))


@app.route('/create_new_routine', methods=['POST'])
def create_new_routine():
    """Create new routine """

    # Get form data
    routine_name = request.form['routineName']
    routine_description = request.form['routineDescription']
    pdf_link = 'a'

    # Upload data to database
    db.execute("INSERT INTO routines (name, description, pdf_link, user_id) "
            "VALUES (:routine_name, :routine_description, :pdf_link, :user_id)",
            routine_name=routine_name, routine_description=routine_description, pdf_link=pdf_link, user_id=session["user_id"])

    # Redirigir al usuario a la página de índice
    return redirect(url_for('routines'))


@app.route('/create_new_membership', methods=['POST'])
def create_new_membership():
    """Create new membership """

    # Get form data
    m_name = request.form['membershipName']
    m_plan_id = int(request.form['membershipPlan'])
    m_routine_id = int(request.form['membershipRoutine'])
    m_payment = request.form['membershipPayment'] # make function to store payment in payments table
    m_email = request.form['membershipEmail']
    m_description = request.form['planDescription'] # modify db
    
    # Save date and time
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    # Upload data to database
    db.execute("INSERT INTO members (name, gym_id, plan_id, routine_id, email, start_date) "
           "VALUES (:m_name, :user_id, :m_plan_id, :m_routine_id, :m_email, :formatted_datetime)",
           m_name=m_name, user_id=session["user_id"], m_plan_id=m_plan_id, m_routine_id=m_routine_id,
           m_email=m_email, formatted_datetime=formatted_datetime)

    
    # Return to memberships page
    return redirect(url_for('plans'))


@app.route('/memberships', methods=['GET'])
def memberships():
    """Show memberships"""
    
    user_id = session.get("user_id")
    
    routines = db.execute("SELECT * FROM routines WHERE user_id = :user_id", user_id=user_id)
    plans = db.execute("SELECT * FROM plans WHERE user_id = :user_id", user_id=user_id)
    users = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)

    return render_template("memberships.html", users=users, plans=plans)


@app.route('/routines', methods=['GET'])
def routines():
    """Show routines"""
    
    user_id = session.get("user_id")
    
    routines = db.execute("SELECT * FROM routines WHERE user_id = :user_id", user_id=user_id)
    users = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)

    return render_template("routines.html", users=users, routines=routines)



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
