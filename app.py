from datetime import datetime
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, success, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///life.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Display all mood entries"""

    # Select all entries from 'mood' table for current user
    rows = db.execute("SELECT * FROM mood WHERE user_id = ? ORDER BY date DESC", session["user_id"])

    # Add the day of each entry as a key-value pair to each entry
    for row in rows:

        # Convert date into datetime object
        dt = datetime.strptime(row["date"], "%Y-%m-%d")

        # Get day of the entry
        day = dt.strftime("%a")

        # Add day to the entry as a key-value pair
        row["day"] = day

    return render_template("index.html", rows=rows)

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Add new mood entry"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Validate user input
        for key in request.form.keys():

            # Ensure all fields in the HTML form except 'remarks' are filled up
            if key != "remarks" and not request.form.get(key):
                return apology("All fields apart from the 'remarks' field must be filled up.", 400)

            # Ensure date is in the correct format
            try:
                datetime.strptime(request.form.get("date"), "%Y-%m-%d")

            except ValueError:
                return apology("You have invalid input(s).", 400)

            # Ensure that mood_1, mood_2, mood_3, sleep, health, and work are digits between 0 and 5 (inclusive)
            if key in ["mood_1", "mood_2", "mood_3", "sleep", "health", "work"] and request.form.get(key) not in ("0", "1", "2", "3", "4", "5"):
                    return apology("You have invalid input(s).", 400)

            # Ensure that remarks is a string
            if type(request.form.get("remarks")) != str:
                return apology("You have invalid input(s).", 400)

        # Ensure that there are no records in the 'mood' table with the date provided
        rows = db.execute("SELECT * FROM mood WHERE user_id = ? AND date = ?", session["user_id"], request.form.get("date"))
        if len(rows):
            return apology(f"You have an existing entry for {request.form.get('date')}. Try editing this entry instead!", 400)

        # Add new record to 'mood' table
        db.execute("INSERT INTO mood VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   session["user_id"], request.form.get("date"), request.form.get("mood_1"), request.form.get("mood_2"),
                   request.form.get("mood_3"), request.form.get("sleep"), request.form.get("health"), request.form.get("work"),
                   request.form.get("remarks"))

        return success("A new entry has been created.")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("new.html")


@app.route("/edit_select", methods=["GET", "POST"])
@login_required
def edit_select():
    """Select mood entry to be edited"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for data of selected entry
        rows = db.execute("SELECT * FROM mood WHERE user_id = ? AND date = ?", session["user_id"], request.form.get("date"))

        # Ensure entry with selected date exists
        if len(rows) == 0:
            return apology("Entry does not exist.", 400)

        # Display form to update data in selected entry
        return render_template("edit_update.html", row=rows[0])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Query database for dates of all entries
        rows = db.execute("SELECT date FROM mood WHERE user_id = ?", session["user_id"])

        return render_template("edit_select.html", rows=rows)

@app.route("/edit_update", methods=["GET", "POST"])
def edit_update():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Validate user input
        for key in request.form.keys():

            # Ensure all fields in the HTML form except 'remarks' are filled up
            if key != "remarks" and not request.form.get(key):
                return apology("All fields apart from the 'remarks' field must be filled up.", 400)

            # Ensure date is in the correct format
            try:
                datetime.strptime(request.form.get("date"), "%Y-%m-%d")

            except ValueError:
                return apology("There are invalid input(s).", 400)

            # Ensure that mood_1, mood_2, mood_3, sleep, health, and work are digits between 0 and 5 (inclusive)
            if key in ["mood_1", "mood_2", "mood_3", "sleep", "health", "work"] and request.form.get(key) not in ("0", "1", "2", "3", "4", "5"):
                    return apology("You have invalid input(s).", 400)

            # Ensure that remarks is a string
            if type(request.form.get("remarks")) != str:
                return apology("There are invalid input(s).", 400)

        # Update entry with data in update form
        db.execute('''UPDATE mood
                      SET mood_1 = ?, mood_2 = ?, mood_3 = ?, sleep = ?, health = ?, work = ?, remarks = ?
                      WHERE user_id = ? AND date = ?''',
                      request.form.get("mood_1"), request.form.get("mood_2"), request.form.get("mood_3"),
                      request.form.get("sleep"), request.form.get("health"), request.form.get("work"),
                      request.form.get("remarks"), session["user_id"], request.form.get("date")
                      )

        return success("The entry has been updated.")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return apology("You cannot access this webpage.", 403)


@app.route("/delete_select", methods=["GET", "POST"])
@login_required
def delete_select():
    """Select mood entry to be deleted"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for data of selected entry
        rows = db.execute("SELECT * FROM mood WHERE user_id = ? AND date = ?", session["user_id"], request.form.get("date"))

        # Ensure entry with selected date exists
        if len(rows) == 0:
            return apology("Entry does not exist.", 400)

        # Display form to update data in selected entry
        return render_template("delete_confirm.html", row=rows[0])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Query database for dates of all entries
        rows = db.execute("SELECT date FROM mood WHERE user_id = ?", session["user_id"])

        return render_template("delete_select.html", rows=rows)


@app.route("/delete_confirm", methods=["GET", "POST"])
def delete_confirm():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Delete entry with selected date
        db.execute('''DELETE FROM mood
                      WHERE date = ?''', request.form.get("date"))

        return success("The entry has been deleted.")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return apology("You cannot access this webpage.", 403)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("You must provide a username.", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return apology("The username you provided is already taken.", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("You must provide a password.", 400)

        # Ensure password confirmation was submitted
        if not request.form.get("confirmation"):
            return apology("You must confirm your password.", 400)

        # Ensure that password and password confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("The password and password confirmation that you provided do not match.", 400)

        # Insert new user into users table
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)",
                   request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("You must provide a username.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("You must provide a password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("The username and/or password you entered is invalid.", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")