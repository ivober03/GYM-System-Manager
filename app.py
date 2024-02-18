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

    # select plans, users, and sections data
    #plans = db.execute(
        #"SELECT plans.*, sections.title as section_title "
        #"FROM plans "
        #"JOIN sections ON plans.section_id = sections.id "
        #"WHERE plans.user_id = :id",
        #id=session["user_id"]
    #)

    users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])

    # Retrieve specific plan data
    #plan_id = request.args.get("plan_id")  # Get the plan ID of the request
    #plan = None
    #if plan_id:
        #plan = db.execute("SELECT * FROM plans WHERE id = :id", id=plan_id).fetchone()


    return render_template("index.html", users=users)


@app.route('/plans', methods=['GET'])
def plans():
    """Show plans"""

    # Select plans and user data

    plans = db.execute("SELECT * FROM plans WHERE user_id = :id", id=session["user_id"])
    user = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
    
    return render_template("plans.html", user=user, plans=plans)


@app.route('/delete_plan/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):
    """Delete plan"""

    # get element ID
    plan = db.execute("SELECT * FROM plans WHERE id = :plan_id", plan_id=plan_id)

    if len(plan) == 1:
        db.execute("UPDATE members SET plan_id = NULL WHERE plan_id = :plan_id", plan_id=plan_id)
        
        db.execute("DELETE FROM plans WHERE id = :plan_id", plan_id=plan_id)
        

    # Redirect user to plans page
    return redirect(url_for('plans'))


@app.route('/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    """Delete member"""

    # get element ID
    member = db.execute("SELECT * FROM members WHERE id = :member_id", member_id=member_id)

    if len(member) == 1:
        db.execute("DELETE FROM members WHERE id = :member_id", member_id=member_id)
        

    # Redirect user to members page
    return redirect(url_for('memberships'))


@app.route('/get_plan/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """get plan data"""

    # Get the plan from the database
    result = db.execute("SELECT * FROM plans WHERE id = :plan_id", plan_id=plan_id)
    plan = result[0]
    if plan:
        # Create a dictionary with the plan data
        plan_data = {
            'id': plan['id'],
            'name': plan['name'],
            'days': int(plan['days']),
            'price': float(plan['price']),
            'description': plan['description']
            
        }
        # Return the plan data as a JSON response
        return jsonify(plan_data)
    else:
        return jsonify({'error': 'plan not found'})
    

@app.route('/get_member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    """get member data"""

    # Get the member from the database
    result = db.execute("SELECT * FROM members WHERE id = :member_id", member_id=member_id)
    member = result[0]
    if member:
        # Get plan and routine name
        plan_id = member['plan_id']
        routine_id = member['routine_id']
        plan_name = db.execute("SELECT name FROM plans WHERE id = :plan_id", plan_id=plan_id)
        routine_name = db.execute("SELECT name FROM routines WHERE id = :routine_id", routine_id=routine_id)


        # Create a dictionary with the member data
        member_data = {
            'id': member['id'],
            'name': member['name'],
            'plan_name': plan_name,
            'routine_name': routine_name,
            'status': member['status'],
            'email': member['email']
        }
        # Return the member data as a JSON response
        return jsonify(member_data)
    else:
        return jsonify({'error': 'member not found'})
    

@app.route('/edit_plan/<int:plan_id>', methods=['GET', 'POST'])
def edit_plan(plan_id):
    """Edit plan"""
    plan = db.execute("SELECT * FROM plans WHERE id = :plan_id", plan_id=plan_id)
    if len(plan) == 1:
        # Get the new form data
        plan_name = request.form['editPlanName']
        plan_days = request.form['editDays']
        plan_price = request.form['editPlanPrice']
        plan_description = request.form['editPlanDescription']          

        # Update the plan data in the database
    db.execute("UPDATE plans SET name = :plan_name, days = :plan_days, price = :plan_price, description = :plan_description WHERE id = :plan_id",
                   plan_name=plan_name, plan_days=plan_days, plan_price=plan_price, plan_description=plan_description, plan_id=plan_id)

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
    return redirect(url_for('memberships'))


@app.route('/memberships', methods=['GET'])
def memberships():
    """Show memberships"""
    """ query = request.args.get('query', '')  # Get URL search parameter

    # Select records' data with plans' information and apply the search query, ordered by date descending
    records = db.execute(
        "SELECT records.*, plans.name AS plan_name, plans.type "
        "FROM records "
        "JOIN plans ON records.plan_id = plans.id "
        "WHERE records.user_id = :id AND plans.name LIKE :query "
        "ORDER BY records.date DESC",
        id=session["user_id"],
        query=f"%{query}%"
    )


    # Convert the results to RecordWithplan objects
    records_with_plans = [
        RecordWithplan(
            name=record['plan_name'],
            type=record['type'],
            state=record['state'],
            streak=record['current_streak'],
            date=record['date']
        )
        for record in records
    ]

    return render_template("records.html", records=records_with_plans, query=query)
    """
    
    user_id = session.get("user_id")
    
    routines = db.execute("SELECT * FROM routines WHERE user_id = :user_id", user_id=user_id)
    plans = db.execute("SELECT * FROM plans WHERE user_id = :user_id", user_id=user_id)
    users = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)
    members = db.execute("SELECT * FROM members WHERE gym_id = :gym_id", gym_id=user_id)

    return render_template("memberships.html", users=users, plans=plans, routines=routines, members=members)


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
