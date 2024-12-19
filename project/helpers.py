from functools import wraps
from flask import session, redirect, render_template

# Requires user to be logged in, else redirects to landing.html
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/landing")
        return f(*args, **kwargs)
    return decorated_function

# Requires user to had previously requested a token, else redirects to landing.html
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("token") is None:
            return redirect("/landing")
        return f(*args, **kwargs)
    return decorated_function

# Works along with flash(), renders an apology with message and code arguments displayed
def apology(message, code):
    return render_template("error.html", code=code, message=message)
