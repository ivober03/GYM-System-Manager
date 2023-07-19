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

# Define a namedtuple class to represent each record in the 'records' table along with the 'habits' fields
RecordWithHabit = namedtuple('RecordWithHabit', ['name', 'type', 'state', 'streak', 'date'])

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6g7h8i9j0'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")


@app.route('/')
def home():
    # check if the user is loged in
    if 'users' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')



@app.route("/records")
def records():
    """Show records"""

    query = request.args.get('query', '')  # Get URL search parameter

    # Select records' data with habits' information and apply the search query, ordered by date descending
    records = db.execute(
        "SELECT records.*, habits.name AS habit_name, habits.type "
        "FROM records "
        "JOIN habits ON records.habit_id = habits.id "
        "WHERE records.user_id = :id AND habits.name LIKE :query "
        "ORDER BY records.date DESC",
        id=session["user_id"],
        query=f"%{query}%"
    )


    # Convert the results to RecordWithHabit objects
    records_with_habits = [
        RecordWithHabit(
            name=record['habit_name'],
            type=record['type'],
            state=record['state'],
            streak=record['current_streak'],
            date=record['date']
        )
        for record in records
    ]

    return render_template("records.html", records=records_with_habits, query=query)


@app.route('/increment_habit/<int:habit_id>', methods=['POST'])
def increment_habit(habit_id):
    """Increment current value of an habit"""

    # get habit
    result = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)
    habit = result[0]

    if (habit['current_value'] + 1) == habit['value']:
            # get completed section id for the user
            section = db.execute("SELECT id FROM sections WHERE title = 'Completed' AND user_id = :id",
                                        id=session["user_id"])
            section_id = section[0]['id']

            # get date and time
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            # get current streak
            result2 = db.execute("SELECT * FROM records WHERE habit_id = :habit_id ORDER BY date DESC LIMIT 1", habit_id=habit_id)
            record = result2[0]
            streak = record['current_streak'] + 1


            # update records table
            db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, :state, :streak, :user_id)",
                                habit_id=habit_id, formatted_datetime=formatted_datetime, state='Completed',streak=streak, user_id=session["user_id"])

            # update on the database
            db.execute("UPDATE habits SET current_value = :value, section_id = :section_id WHERE id = :habit_id",
                            value=habit['value'], section_id=section_id, habit_id=habit_id)

    else:

        # increase value
        value = habit['current_value'] + 1

        # update on the database
        db.execute("UPDATE habits SET current_value = :value WHERE id = :habit_id",
                        value=value, habit_id=habit_id)

    # redirect user to index page
    return redirect(url_for('index'))


@app.route('/complete_habit/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    """Complete habit"""

    # get habit
    result = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)
    habit = result[0]

    # get completed section id for the user
    section = db.execute("SELECT id FROM sections WHERE title = 'Completed' AND user_id = :id",
                                        id=session["user_id"])
    section_id = section[0]['id']

    # update habit table
    db.execute("UPDATE habits SET section_id = :section_id WHERE id = :habit_id",
                section_id=section_id, habit_id=habit_id)

    # get date and time
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # get current streak
    result2 = db.execute("SELECT * FROM records WHERE habit_id = :habit_id ORDER BY date DESC LIMIT 1", habit_id=habit_id)
    streak = result2[0]['current_streak'] + 1


    # update records table
    db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, :state, :streak, :user_id)",
                        habit_id=habit_id, formatted_datetime=formatted_datetime, state='Completed',streak=streak, user_id=session["user_id"])


    # redirect user to index page
    return redirect(url_for('index'))


@app.route('/fail_habit/<int:habit_id>', methods=['POST'])
def fail_habit(habit_id):
    """Fail habit"""


    # get habit
    result = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)
    habit = result[0]

    # get failed section id for the user
    section = db.execute("SELECT id FROM sections WHERE title = 'Failed' AND user_id = :id",
                                        id=session["user_id"])
    section_id = section[0]['id']

    # get date and time
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


    # update records table
    db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, :state, :streak, :user_id)",
                                habit_id=habit_id, formatted_datetime=formatted_datetime, state='Failed',streak=0, user_id=session["user_id"])


    # update database
    db.execute("UPDATE habits SET section_id = :section_id WHERE id = :habit_id",
                            section_id=section_id , habit_id=habit_id)

    # redirect user to index page
    return redirect(url_for('index'))


@app.route('/reset_habit/<int:habit_id>', methods=['POST'])
def reset_habit(habit_id):
    """Reset habit"""


    # get habit
    result = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)
    habit = result[0]

    # determinate if the habit is good or bad
    if habit['type'] == 'Good':
        habit_type = 'Positive habits'
    else:
        habit_type = 'Negative habits'

    # get the original section for the habit
    section = db.execute("SELECT id FROM sections WHERE title = :habit_type AND user_id = :user_id",
                                        habit_type=habit_type, user_id=session["user_id"])
    section_id = section[0]['id']

    # get the most recent record
    result2 = db.execute("SELECT * FROM records WHERE habit_id = :habit_id ORDER BY date DESC LIMIT 1", habit_id=habit_id)
    record = result2[0] if result2 else None

    # update database
    if habit_type == 'Negative habits':
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("UPDATE habits SET start_date = :formatted_datetime, current_value = 0, section_id = :section_id WHERE id = :habit_id",
                                formatted_datetime=formatted_datetime, section_id=section_id, habit_id=habit_id)

        # Save record for habit reset
        if record:
            db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, 'Restarted', :current_streak, :user_id)",
                                habit_id=habit_id, formatted_datetime=formatted_datetime, current_streak=record['current_streak'], user_id=session["user_id"])
        else:
            db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, 'Restarted', 0, :user_id)",
                                habit_id=habit_id, formatted_datetime=formatted_datetime, user_id=session["user_id"])
    else:
        db.execute("UPDATE habits SET current_value = 0, section_id = :section_id WHERE id = :habit_id",
                                section_id=section_id, habit_id=habit_id)

        # Save record for habit reset
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        if record:
            db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, 'Restarted', :current_streak, :user_id)",
                                habit_id=habit_id, formatted_datetime=formatted_datetime, current_streak=record['current_streak'], user_id=session["user_id"])
        else:
            db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, 'Restarted', 0, :user_id)",
                                habit_id=habit_id, formatted_datetime=formatted_datetime, user_id=session["user_id"])

    # redirect user to index page
    return redirect(url_for('index'))



@app.route("/index.html")
def index():
    """Load index page"""


    # select habits, users, and sections data
    habits = db.execute(
        "SELECT habits.*, sections.title as section_title "
        "FROM habits "
        "JOIN sections ON habits.section_id = sections.id "
        "WHERE habits.user_id = :id",
        id=session["user_id"]
    )
    users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    sections = db.execute("SELECT * FROM sections WHERE user_id = :id", id=session["user_id"])

    # Retrieve specific habit data
    habit_id = request.args.get("habit_id")  # Get the habit ID of the request
    habit = None
    if habit_id:
        habit = db.execute("SELECT * FROM habits WHERE id = :id", id=habit_id).fetchone()


    return render_template("index.html", habits=habits, users=users, habit=habit, sections=sections)


@app.route('/create_good_habit', methods=['POST'])
def create_good_habit():
    """Create new good habit """

    # Get form data
    habit_name = request.form['habitName']
    habit_value = int(request.form['habitValue'])
    habit_duration = request.form['habitDuration']
    habit_period = request.form['habitPeriod']
    habit_repeat = request.form['habitRepeatON']
    habit_notes = request.form['habitNotes']
    habit_show_at = request.form['habitShowAt']

    # Save date and time
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Get the section based on habit type (good) and user_id
    section_id_result = db.execute("SELECT id FROM sections WHERE user_id = :user_id AND title = 'Positive habits'",
                                   user_id=session["user_id"])
    section_id = section_id_result[0]['id']

    # Insert good habit data into the database
    db.execute("INSERT INTO habits (user_id, section_id, name, value, duration, period, repeat, notes, type, start_Date, show_at) "
               "VALUES (:id, :section_id, :habit_name, :habit_value, :habit_duration, :habit_period, :habit_repeat, "
               ":habit_notes, :type, :date, :show_at)",
               id=session["user_id"], section_id=section_id, habit_name=habit_name, habit_value=habit_value,
               habit_duration=habit_duration, habit_period=habit_period, habit_repeat=habit_repeat,
               habit_notes=habit_notes, type='Good', date=formatted_datetime, show_at=habit_show_at)

    result = db.execute("SELECT id FROM habits WHERE user_id = :user_id AND name = :habit_name",
                        user_id=session["user_id"], habit_name=habit_name)

    habit_id = result[0]['id']

    # insert first record into the database
    db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, :state, :streak, :user_id)",
                                habit_id=habit_id, formatted_datetime=formatted_datetime, state='Created',streak=0, user_id=session["user_id"])


    # Redirect user to index page
    return redirect(url_for('index'))




@app.route('/edit_good_habit/<int:habit_id>', methods=['POST'])
def edit_good_habit(habit_id):
    """Edit good habit"""


    # Get the habit to edit from the database
    habit = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)
    if len(habit) == 1:
        # Get the new form data
        habit_name = request.form['editHabitName']
        habit_value = int(request.form['editHabitValue'])
        habit_duration = request.form['editHabitDuration']
        habit_period = request.form['editHabitPeriod']
        habit_repeat = request.form['editHabitRepeatON']
        habit_notes = request.form['editHabitNotes']
        habit_showat= request.form['editHabitShowAt']


        # Update the habit data in the database
        db.execute("UPDATE habits SET name = :habit_name, value = :habit_value, duration = :habit_duration, period = :habit_period, repeat = :habit_repeat, notes = :habit_notes, show_at = :habit_showat WHERE id = :habit_id",
                   habit_name=habit_name, habit_value=habit_value, habit_duration=habit_duration, habit_period=habit_period, habit_repeat=habit_repeat, habit_notes=habit_notes, habit_showat=habit_showat, habit_id=habit_id)

    # redirect user to index page
    return redirect(url_for('index'))


@app.route('/delete_habit/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    """Delete habit"""

    # get element ID
    habit = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)


    # delete all records and habit from database
    if len(habit) == 1:
        db.execute("DELETE FROM records WHERE habit_id = :habit_id", habit_id=habit_id)
        db.execute("DELETE FROM habits WHERE id = :habit_id", habit_id=habit_id)

    # Redirect user to index page
    return redirect(url_for('index'))


@app.route('/break_bad_habit', methods=['POST'])
def break_bad_habit():
    """Create new break bad habit"""


    # get habit name
    habit_name = request.form['badHabitName']

    # Get the section based on habit type (bad) and user_id
    section_id_result = db.execute("SELECT id FROM sections WHERE user_id = :user_id AND title = 'Negative habits'",
                                   user_id=session["user_id"])
    section_id = section_id_result[0]['id']

    # get and check the habit type (quit/limit)
    habit_type = request.form.get('habit_type')


    if habit_type == 'quit':
        # get start date
        date_string = request.form['datepickerBreak2']
        if date_string == '':
            date = datetime.now()
            # insert data into the database
            db.execute("INSERT INTO habits (user_id, section_id, name, start_Date, type)"
                        "VALUES (:id, :section_id, :habit_name, :date, :type)",
                        id=session["user_id"], section_id=section_id, habit_name=habit_name, date=date, type='Bad')

            result = db.execute("SELECT id FROM habits WHERE user_id = :user_id AND name = :habit_name",
                                user_id=session["user_id"], habit_name=habit_name)

            habit_id = result[0]['id']

            # insert first record into the database
            db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, :state, :streak, :user_id)",
                                        habit_id=habit_id, formatted_datetime=date, state='Created',streak=0, user_id=session["user_id"])

            return redirect(url_for('index'))

        else:
            # convert date to a datetime object
            date = datetime.strptime(date_string, '%a %b %d %Y')
            if datetime.now().date() == date.date():
                date = datetime.now()
            # get timestamp
            timestamp = date.timestamp()
            # formate timestamp to YYYY-MM-DD HH:MM:SS
            formatted_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


            # insert data into the database
            db.execute("INSERT INTO habits (user_id, section_id, name, start_Date, type)"
                    "VALUES (:id, :section_id, :habit_name, :date, :type)",
                    id=session["user_id"], section_id=section_id, habit_name=habit_name, date=formatted_date, type='Bad')

    elif habit_type == 'limit':
        # get start date
        date_string = request.form['datepickerBreak']
        if date_string == '':
            date = datetime.now()

            # get form data (value, duration, and repeatOn)
            habit_value = int(request.form['badHabitValue'])
            habit_duration = request.form['badHabitDuration']
            habit_period = request.form['badHabitPeriod']

            # insert data into the database

            db.execute("INSERT INTO habits (user_id, section_id, name, value, duration, period, start_Date, type)"
                        "VALUES (:id, :section_id, :habit_name, :habit_value, :habit_duration, :habit_period, :date, :type)",
                        id=session["user_id"], section_id=section_id, habit_name=habit_name, habit_value=habit_value,
                        habit_duration=habit_duration, habit_period=habit_period, date=date, type='Bad')

            result = db.execute("SELECT id FROM habits WHERE user_id = :user_id AND name = :habit_name",
            user_id=session["user_id"], habit_name=habit_name)

            habit_id = result[0]['id']

            # insert first record into the database
            db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, :state, :streak, :user_id)",
                                        habit_id=habit_id, formatted_datetime=date, state='Created',streak=0, user_id=session["user_id"])

            return redirect(url_for('index'))

        else:
            # convert date to a datetime object
            date = datetime.strptime(date_string, '%a %b %d %Y')
            if datetime.now().date() == date.date():
                date = datetime.now()
            # get timestamp
            timestamp = date.timestamp()
            # formate timestamp to YYYY-MM-DD HH:MM:SS
            formatted_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            # get form data (value, duration, and repeatOn)
            habit_value = int(request.form['badHabitValue'])
            habit_duration = request.form['badHabitDuration']
            habit_period = request.form['badHabitPeriod']

            # insert data into the database
            db.execute("INSERT INTO habits (user_id, section_id, name, value, duration, period, start_Date, type)"
                        "VALUES (:id, :section_id, :habit_name, :habit_value, :habit_duration, :habit_period, :date, :type)",
                        id=session["user_id"], section_id=section_id, habit_name=habit_name, habit_value=habit_value,
                        habit_duration=habit_duration, habit_period=habit_period, date=formatted_date, type='Bad')

    result = db.execute("SELECT id FROM habits WHERE user_id = :user_id AND name = :habit_name",
                                user_id=session["user_id"], habit_name=habit_name)

    habit_id = result[0]['id']

    # insert first record into the database
    db.execute("INSERT INTO records (habit_id, date, state, current_streak, user_id) VALUES (:habit_id, :formatted_datetime, :state, :streak, :user_id)",
                            habit_id=habit_id, formatted_datetime=formatted_datetime, state='Created',streak=0, user_id=session["user_id"])


    # redirect user to index page
    return redirect(url_for('index'))


@app.route('/get_habit/<int:habit_id>', methods=['GET'])
def get_habit(habit_id):
    """get habit data"""

    # Get the habit from the database
    result = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)
    habit = result[0]
    if habit:
        # Create a dictionary with the habit data
        habit_data = {
            'id': habit['id'],
            'user_id': habit['user_id'],
            'section_id': habit['section_id'],
            'name': habit['name'],
            'value': habit['value'],
            'current_value': habit['current_value'],
            'duration': habit['duration'],
            'period': habit['period'],
            'repeat': habit['repeat'],
            'notes': habit['notes'],
            'start_date': habit['start_date'],
            'type': habit['type'],
            'show_at' : habit['show_at']
        }
        # Return the habit data as a JSON response
        return jsonify(habit_data)
    else:
        return jsonify({'error': 'Habit not found'})


@app.route('/get_progress_data/<int:habit_id>', methods=['GET'])
def get_progress_data(habit_id):
    """get habit progress data"""


    # Get the habit and its most recent record
    result = db.execute("SELECT * FROM habits WHERE id = :habit_id", habit_id=habit_id)
    habit = result[0]

    result2 = db.execute("SELECT * FROM records WHERE habit_id = :id", id=habit_id)
    records = result2

    habit_data = {}
    record_data = {}

    if habit:
        # Create a dictionary with the habit data
        habit_data = {
            'id': habit['id'],
            'user_id': habit['user_id'],
            'section_id': habit['section_id'],
            'name': habit['name'],
            'value': habit['value'],
            'current_value': habit['current_value'],
            'duration': habit['duration'],
            'period': habit['period'],
            'repeat': habit['repeat'],
            'notes': habit['notes'],
            'start_date': habit['start_date'],
            'type': habit['type'],
            'failed_count': 0,
            'completed_count': 0,
        }

        # Count the number of 'completed' and 'failed' statuses in logs
        for record in records:
            if record['state'] == 'Completed':
                habit_data['completed_count'] += 1
            elif record['state'] == 'Failed':
                habit_data['failed_count'] += 1

    if records:
        # Get the most recent record
        latest_record = max(records, key=lambda x: x['date'])
        record_data = {
            'current_streak': latest_record['current_streak'],
            'date': latest_record['date'],
            'state': latest_record['state']
        }

    # Return the habit data as a JSON response
    return jsonify(habit_data=habit_data, record_data=record_data)



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
        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        email = request.form.get("email")

        # insert user data into the database
        db.execute("INSERT INTO users (username, name, password_hash, email) VALUES (:username, :name, :password_hash, :email)",
                username=username, name=name, password_hash=password_hash, email=email)

        # get the ID of the inserted user
        user_id = db.execute("SELECT id FROM users WHERE email = :email", email=email)[0]["id"]

        # insert initial sections for habits
        db.execute("INSERT INTO sections (user_id, title) VALUES (:id, 'Positive habits')",
                    id=user_id)
        db.execute("INSERT INTO sections (user_id, title) VALUES (:id, 'Negative habits')",
                    id=user_id)
        db.execute("INSERT INTO sections (user_id, title) VALUES (:id, 'Completed')",
                    id=user_id)
        db.execute("INSERT INTO sections (user_id, title) VALUES (:id, 'Failed')",
                    id=user_id)

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

