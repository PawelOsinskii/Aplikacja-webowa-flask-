import uuid
import datetime
from flask import Flask, render_template, redirect, jsonify
from flask import request, make_response, session
from flask import flash, url_for
from flask_session import Session
from redis import Redis, StrictRedis
from bcrypt import hashpw, gensalt, checkpw
from os import getenv
from dotenv import load_dotenv

# from jwt import encode, decode

load_dotenv()  # zaczytuje .env
REDIS_LOKAL = getenv('REDIS_LOKAL')
REDIS_HOST = getenv('REDIS_HOST')
REDIS_PASS = getenv('REDIS_PASS')
db = StrictRedis(REDIS_HOST, db=12, password=REDIS_PASS)  # wczytywać połączenie z env
SESSION_TYPE = 'redis'  # trzymanie danych sesyjnych w redisie
SESSION_REDIS = db  # obiekt reprezentujacy połączene
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_HTTPONLY = True
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
ses = Session(app)
app.debug = False





def is_user(username):
    return db.hexists(f"user:{username}", "password")


def save_user(email, username, password, address):
    salt = gensalt(5)
    password = password.encode()
    hashed = hashpw(password, salt)
    if not is_redis_available(db):
        return render_template("sender/wrong_connection.html")
    db.hset(f"user:{username}", "password", hashed)
    db.hset(f"user:{username}", "email", email)
    db.hset(f"user:{username}", "address", address)
    return True


def verify_user(username, password):
    password = password.encode()
    if not is_redis_available(db):
        return render_template("sender/wrong_connection.html")
    hashed = db.hget(f"user:{username}", "password")
    if not hashed:
        print(f"Wrong password or username!")
        return False

    return checkpw(password, hashed)


def error(msg, status=400):
    resp = make_response({"status": "error", "message": msg}, status)
    return resp


def redirect(url, status=301):
    res = make_response('', status)
    res.headers['Location'] = url
    return res


@app.route('/')
def index():
    if "username" not in session:
        return render_template("index.html")
    return render_template("index_after_login.html")


@app.route('/sender/register', methods=['GET'])
def register_form():
    return render_template("sender/register.html")


@app.route('/sender/register', methods=['POST'])
def register():
    firstname = request.form.get('firstname')
    if not firstname:
        flash("No firstname provided")

    lastname = request.form.get('lastname')
    if not lastname:
        flash("No lastname provided")

    username = request.form.get('login')
    if not username:
        flash("No username provided")

    email = request.form.get('email')
    if not email:
        flash("No email provided")

    address = request.form.get('address')
    if not address:
        flash("no address provided")

    password = request.form.get('password')
    if not password:
        flash("No password provided")

    password2 = request.form.get('password2')
    if password != password2:
        flash("paswords dont match")
        return redirect(url_for("register_form"))

    if email and username and password and address:
        if is_user(username):
            flash(f"User {username} already registered")
            return redirect(url_for("register_form"))
        success = save_user(email, username, password, address)
        if not success:
            flash("error in during saving, please try again")
            return redirect(url_for("register_form"))
    else:
        return redirect(url_for("register_form"))
    flash("Account has been created")
    return redirect(url_for("login_form"))


@app.route('/sender/login', methods=['GET'])
def login_form():
    if "username" not in session:
        return render_template("sender/login.html")
    flash(f'Welcome {session["username"]} in our website, now you can send the parcel. Do you know our offer?')
    return render_template("sender/login_after_login.html")


@app.route('/sender/isLogin/<user>', methods=['GET'])
def is_available(user):
    if is_user(user):
        return jsonify(
            user='taken',
        )
    else:
        return jsonify(
            user='available',
        )


@app.route('/sender/login', methods=['POST'])
def login():
    username = request.form.get('login')
    password = request.form.get('password')
    app.logger.warning(username + '+' + password)
    if not username and not password:
        flash("You need fill in username AND password")
        return redirect(url_for('login_form'))
    if not verify_user(username, password):
        flash("Wrong password or login")
        return redirect(url_for('login_form'))

    flash(f"Welcome {username} in our website, now you can send the parcel. Do you know our offer?")
    session["username"] = username
    now = datetime.datetime.now()
    session['logged-at'] = now.strftime("%m/%d/%Y, %H:%M:%S")
    return render_template("sender/login_after_login.html")


@app.route('/sender/logout', methods=['GET'])
def logout():
    if "username" not in session:
        flash("the first you need log on")
        return redirect(url_for("login_form"))
    session.clear()
    flash("Logout success")
    return redirect(url_for('login_form'))


@app.route('/sender/dashboard', methods=['GET'])
def dashboard():
    if not is_redis_available(db):
        return render_template("sender/wrong_connection.html")
    if "username" not in session:
        flash("the first you need log on")
        return redirect(url_for("login_form"))
    list_of_packages = db.hgetall(f'package:{session["username"]}')
    if list_of_packages:
        for key in list_of_packages:
            position = list_of_packages[key]
            flash(str(position).split('|'))
    return render_template("sender/dashboard.html")


@app.route('/sender/createpackage', methods=['POST'])
def create_package():
    addressee = request.form.get('addressee')
    if not addressee:
        flash("No addressee provided")

    id_postbox = request.form.get('id-postbox')
    if not id_postbox:
        flash("No id-postbox provided")

    size = request.form.get('size')
    if not size:
        flash("No size provided")
    now = datetime.datetime.now()

    date = now.strftime("%m/%d/%Y, %H:%M:%S")

    uid = str(uuid.uuid4())
    if "username" not in session:
        flash("the first you need log on")
        return redirect(url_for("dashboard"))
    username = session["username"]

    if addressee and id_postbox and size:
        success = save_package(addressee, id_postbox, size, date, uid, username)
        if not success:
            flash("error in during saving, please try again")
            return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("dashboard"))
    return redirect(url_for("dashboard"))


def save_package(addressee, id_postbox, size, date, uid, username):
    if not is_redis_available(db):
        return render_template("sender/wrong_connection.html")
    db.hset(f"package:{username}", uid,
            ('cos |' + addressee + '|' + id_postbox + "|" + size + "|" + date + "|" + uid))
    return True


@app.route('/sender/deletepackage/<package>', methods=['GET'])
def delete_package(package):
    if not is_redis_available(db):
        return render_template("sender/wrong_connection.html")
    result =  str(package).replace("'", '')
    result = str(result).replace('"', '')
    wynik = db.hdel(f'package:{session["username"]}', result)
    print(wynik)
    return redirect(url_for("dashboard"))


def is_redis_available(r):
    try:
        r.ping()
        print("Successfully connected to redis")
    except (Redis.exceptions.ConnectionError, ConnectionRefusedError):
        print("Redis connection error!")
        return False
    return True


if __name__ == '__main__':
    app.run()
