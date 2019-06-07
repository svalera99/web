import gc
import json
import os
from functools import wraps

from MySQLdb import escape_string as thwart
from flask import Flask, render_template, flash, request, url_for, redirect, session
from flask_wtf.file import FileField
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from wtforms import Form, BooleanField, TextField, PasswordField, validators

from content_management import Content
from dbconnect import connection

TOPIC_DICT = Content()

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("main.html")


@app.route('/centers/')
def dashboard():
    return render_template("centers.html", TOPIC_DICT=TOPIC_DICT)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.route('/knowmore/')
def know():
    return render_template("knowmore.html")


@app.route('/subscribe/')
def subscribe():
    return render_template("subscribe.html")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))


class PostCreationForm(Form):
    name = TextField('Name')
    illness = TextField('Illness')
    status = TextField('Status')
    age = TextField('Age')
    blood = TextField('Blood type')
    location = TextField('Country of current location')
    file = FileField("Upload picture")


@app.route("/make-post/", methods=["GET", "POST"])
def make_post():
    allowed_file = lambda filename: filename[-3:] in set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    try:
        if request.method == "POST":
            picture = "/static/js/nophoto.png"
            uploaded = 0
            if request.files['file'].filename != '':
                file = request.files['file']
                uploaded = 1
            if uploaded:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    picture = os.path.join('/static/images/', filename)
                    file.save("." + picture)
            new_dict = {}
            with open("static/js/posts.json", "r+") as json_file:
                json_data = json.load(json_file)
                index = int(list(json_data.keys())[-1]) + 1
                new_dict["picture"] = ".." + picture
                new_dict["name"] = request.form["name"]
                new_dict["illness"] = request.form["illness"]
                new_dict["status"] = request.form["status"]
                new_dict["age"] = request.form["age"]
                new_dict["blood-group"] = request.form["blood"]
                new_dict["location"] = request.form["location"]
                json_data[str(index)] = new_dict
            with open("static/js/posts.json", "w") as json_file:
                json.dump(json_data, json_file)
            flash("Thank you for creating the post!")
            return redirect("/")
        return render_template("make_post.html")
    except Exception as e:
        return str(e)


@app.route('/login/', methods=["GET", "POST"])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":
            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             thwart(request.form['username']))
            data = c.fetchone()[2]
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are now logged in")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid credentials, try again."
        gc.collect()
        return render_template("login.html", error=error)
    except Exception as e:
        error = "Invalid credentials, try again."
        return render_template("login.html", error=error)


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password',
                             [validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)',
                              [validators.Required()])
    accept_email = BooleanField('I want to get an emails about your news', [validators.Optional()])


@app.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            accept_email = form.accept_email.data
            c, conn = connection()
            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                          (thwart(username),))
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, send_emails) VALUES (%s, %s, %s, %s)",
                          (thwart(username), thwart(password), thwart(email), accept_email))
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('dashboard'))
        return render_template("register.html", form=form)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()
