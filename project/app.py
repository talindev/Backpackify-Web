# Importing everything needed for app.py (Python-Flask backend)
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime, timedelta

import string
import secrets

from helpers import login_required, apology, token_required

# Initializing Flask
app = Flask(__name__)

# Reads enviroment variable email and password used to send token emails to user
with open('.env/apppass.txt', 'r') as file:
    PASSWORD = file.read().strip()

with open('.env/email.txt', 'r') as file:
    EMAIL = file.read().strip()

# Flask_mail configuration using GMAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = EMAIL

# Initializes flask_mail (Mail)
mail = Mail(app)

# Recovery email function outside of any route to be used later
def send_recovery_email(user_email, token):
    with app.app_context():
        # Mail structure
        subject = "Backpackify account recovery"
        body = f"""
        Dear backpackify user,

        You have requested a password recovery. This is your randomized token.

        {token}

        The token will expire 5 minutes from now.
        """

        # Building the message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=EMAIL
        )

        # Attempts to send email, if there is a error, displays it for debugging
        try:
            mail.send(msg)
            print("E-mail sent successfully!")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

# Flask app configuration => Session and SQL database initialization, and after_request
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///backpackify.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Login route from problem set 9 "Finance"
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash(f"Successfully logged in as {request.form.get("username")}", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("landing.html")

# Log out route from problem set 9 "Finance"
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/landing")

# Default route, sends which bags the currently logged user has
@app.route("/")
@login_required
def index():
    bags = db.execute("SELECT * FROM backpacks WHERE user_id = ?", session["user_id"])
    return render_template("index.html", bags=bags)

# Landing page route that only renders the html page
@app.route("/landing")
def landing():
    return render_template("landing.html")

# Register route, implemented
@app.route("/register", methods=["GET", "POST"])
def register():
    # Checks for the type of method
    if request.method == "POST":
        # Gather the data that was sent in the <form>
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Empty/incorrect input error handling
        if not username or not password or not confirmation or not email:
            return apology("empty/incorrect email/username/password/confirmation input", 400)
        if password != confirmation:
            return apology("password different from confirmation", 400)

        # Hashing user's password to store it in database (way more secure)
        hash = generate_password_hash(password)

        # Attempts to register the user in the database and renders an apology html with message and error code if registration is not possible
        try:
            db.execute("INSERT INTO users (email, username, hash) VALUES (?, ?, ?)", email, username, hash)
        except ValueError:
            return apology("user already exists", 400)

        # Feedback for the user
        flash("Successfully created account", "success")
        return redirect("/landing")
    else:
        # GET method rendering
        return render_template("register.html")

# Bag creation route, implemented
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Checks type of method
    if request.method == "POST":
        # Gather the data that was sent by the <form>
        storage_name = request.form.get("storage_name")
        storage_type = request.form.get("storage_type")
        location = request.form.get("location")
        use = request.form.get("use")
        content = request.form.get("content")

        # Since location and use input fields are optional, no error checking + handling for those
        if not storage_name or not storage_type or not content:
            return apology("empty/incorrect storage name/type/content input", 403)

        # Like /register, attempts to register the storage in the database, attached to the currently logged user
        try:
            db.execute("INSERT INTO backpacks (user_id, storage_name, storage_type, location, use, content) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], storage_name, storage_type, location, use, content)
        except ValueError:
            return apology("do not create storages with the same name", 403)

        # Feedback for the user
        flash(f"Successfully created storage named {storage_name}", "success")
        return redirect("/")
    else:
        # GET method rendering
        return render_template("create.html")

# Storage deletion route, implemented, only supports POST requests
@app.route("/delete", methods=["POST"])
@login_required
def delete():
    # Gather data from the attached storage
    name = request.form.get("storage_name")

    # Attempts to delete the storage with the storage's name and the currently logged user attached to it, in cases of error, renders apology
    try:
        db.execute("DELETE FROM backpacks WHERE user_id = ? AND storage_name = ?", session["user_id"], name)
    except Exception:
        return apology("could not delete storage", 500)

    # Feedback for the user
    flash(f"Successfully deleted storage named {name}", "success")
    return redirect("/")

# Search AJAX route, recommended
@app.route("/search")
@login_required
def search():
    # Gathers the query typed in the <input>
    query = request.args.get('q', '')

    # Searchs for it in the database
    bags = db.execute("""
        SELECT * FROM backpacks
        WHERE user_id = ? AND
        (storage_name LIKE ? OR location LIKE ? OR use LIKE ?)
    """, session["user_id"], f"%{query}%", f"%{query}%", f"%{query}%")

    # In case nothing is found, an empty list is returned
    if not bags:
        return jsonify([])

    # Jsonfies the result
    return jsonify(bags)

# Password change/recovery route, implemented
@app.route("/recover", methods=["GET", "POST"])
def recover():
    # Checks for the request method
    if request.method == "POST":
        # Gathers data from the <input>
        username = request.form.get("username")

        # Searches for the user's email and id
        user_email = db.execute("SELECT email FROM users WHERE username = ?", username)[0]["email"]
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

        # Generates a random token using the secrets method for security
        token = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)) # stackoverflow

        # Queries for the user's info in the database
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Stores the current timestamp in a variable
        created_at = datetime.now()

        # Remembers the users's username and the randomly generated token
        session["username"] = rows[0]["username"]
        session["token"] = token

        # Removes any previous tokens generated for this user before moving on
        db.execute("DELETE FROM recoveries WHERE username = ?", session["username"])

        # Attempts to register the token for the desired user, attaching together username, the token itself, id and creation timestamp
        try:
            db.execute("INSERT INTO recoveries (username, token, user_id, created_at) VALUES (?, ?, ?, ?)", username, str(token), user_id, created_at)
        except Exception:
            flash("A error occurred", "danger")

        # If no errors occur, attempts to send an email to the user, informing the token for later verification
        send_recovery_email(user_email, token)
        if not send_recovery_email:
            # Forgets the previously remembered data from the user and 'restarts' the process
            session.clear()
            flash("Failed to send email", "danger")
            return redirect("/recover")

        # Feedback for the user
        flash(f"Email sent to user {username}", "success")
        return redirect("/validatetoken")
    else:
        # GET method rendering
        return render_template("recover.html")

# Token validation route, redirected from /recover, implemented
@app.route("/validatetoken", methods=["GET", "POST"])
@token_required
def validate_token():
    # Method checking
    if request.method == "POST":
        # Checks if the typed in token is correct and matches the previously stored token for the currently 'logged' user
        token = request.form.get("token")
        match = db.execute("SELECT * FROM recoveries WHERE token = ? AND username = ?", token, session["username"])

        # If no matches were found, forgets the data and 'restarts' the process
        if len(match) != 1:
            session.clear()
            flash("Token mismatch/error", "danger")
            return redirect("/landing")

        # Checks if the token has not expired after 5 minutes
        creationDate = match[0]['created_at']
        creationDate = datetime.strptime(creationDate, "%Y-%m-%d %H:%M:%S")
        expirationDate = creationDate + timedelta(minutes=5)

        # If token is expired, deletes all previously created tokens for that user and forgets his information, 'restarting' the process
        if datetime.now() > expirationDate:
            db.execute("DELETE FROM recoveries WHERE username = ?", session["username"])
            session.clear()
            flash("Token expired", "danger")
            return redirect("/recover")

        # In case no errors were reported and the token is correct, moves on to the final step
        return redirect("/passwordchange")
    else:
        # GET method rendering
        return render_template("validatetoken.html")

# Final password change <form> route, implemented
@app.route("/passwordchange", methods=["GET", "POST"])
@token_required
def password_change():
    # Method checking
    if request.method == "POST":
        # Gathers data typed by the user, which is the new desired password
        newPassword = request.form.get("newPassword")
        confirmation = request.form.get("confirmation")

        # Checks password confirmation
        if newPassword != confirmation:
            flash("Password and confirmation did not match", "danger")
            return redirect("/passwordchange")

        # Hashes the new password, for security
        newHash = generate_password_hash(newPassword)

        # Updates the previous password for the new one for the current user
        db.execute("UPDATE users SET hash = ? WHERE username = ?", newHash, session["username"])

        # Deletes every token for that user
        db.execute("DELETE FROM recoveries WHERE username = ?", session["username"])

        # Forgets data from the user, forcing user to log in
        session.clear()

        # Feedback for the user
        flash("Successfully changed password", "success")

        return redirect("/landing")
    else:
        # GET method rendering
        return render_template("passwordchange.html")
