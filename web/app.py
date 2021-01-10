import uuid
import datetime
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import jwt
from flask import Flask, render_template, redirect, jsonify
from flask import request, make_response, session
from flask import flash, url_for
from flask_session import Session
from redis import Redis, StrictRedis
from bcrypt import hashpw, gensalt, checkpw
from os import getenv, environ
from dotenv import load_dotenv
import requests
from jwt import encode, decode
from six import wraps

load_dotenv()  # zaczytuje .env
REDIS_LOKAL = getenv('REDIS_LOKAL')
REDIS_HOST =  environ.get('REDIS_HOST')#'ec2-3-121-188-229.eu-central-1.compute.amazonaws.com'
REDIS_PASS = environ.get('REDIS_PASS')#'V&2asU5aDYCFuuvacpSodx8DFjdj$'
db = StrictRedis(REDIS_HOST, db=23, password=REDIS_PASS)  # wczytywać połączenie z env
SESSION_TYPE = 'redis'  # trzymanie danych sesyjnych w redisie
SESSION_REDIS = db  # obiekt reprezentujacy połączene
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

app = Flask(__name__)

AUTH0_CALLBACK_URL = environ.get('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = environ.get('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = environ.get('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = environ.get('AUTH0_DOMAIN')
AUTH0_BASE_URL = 'https://' + str(environ.get('AUTH0_BASE_URL'))



oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
app.config.from_object(__name__)
app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ'
ses = Session(app)
app.debug = False


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=5)


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


@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    if userinfo['name'] is not None:
        flash(f"Welcome {userinfo['name']} in our website, now you can send the parcel. Do you know our offer?")
        session["username"] = userinfo['name']
        now = datetime.datetime.now()
        session['logged-at'] = now.strftime("%m/%d/%Y, %H:%M:%S")
        if not is_user(session["username"]):
            success = save_user(session["username"], session["username"], session["username"], session["username"])
        return render_template("sender/login_after_login.html")
    flash(f"login failed")
    return render_template("sender/login.html")




@app.route('/loginoauth')
def loginouath():
    return auth0.authorize_redirect(redirect_uri='https://pawelosinski123.herokuapp.com/callback')



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
        flash("logout")
        return redirect(url_for("login_form"))
    if "profile" in session:
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        session.pop('profile')
        session.pop('username')
        session["__invalidate__"] = True
        params = {'returnTo': url_for('https://pawelosinski123.herokuapp.com/', _external=True), 'client_id': 'VQS2zf4jPI4JJgXY4elqLcOYxFF4LUo7'}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    session.pop('username')
    session.clear()
    session["__invalidate__"] = True
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
    username = session["username"]
    encoded_jwt = jwt.encode({'username': username}, app.secret_key, algorithm='HS256')
    print(str(encoded_jwt))
    _jwt = str(encoded_jwt).split("'")
    jwt_ = _jwt[1]
    headers = {"Authorization": "Bearer " + jwt_}
    r = requests.get(f'https://pawelosinskiprzesylkiprojekt.herokuapp.com/labels/' + username, headers=headers)
    if r.status_code != 200:
        flash("Brak połączenia z web service")
        return render_template("sender/login_after_login.html")
    json = r.json()
    for table in json['_embedded']['items']:
        uid = table['uid']
        size = table['size']
        address = table['address']
        id_post_office = table['id_post_office']
        date = table['date']
        status = table['status']
        position = f'cos|{address} | {id_post_office} | {size} | {date} | {uid} |{status}'
        flash(str(position).split('|'))
    return render_template("sender/dashboard.html")


@app.route('/sender/createpackage', methods=['POST'])
def create_package():
    addressee = request.form.get('addressee')
    id_postbox = request.form.get('id-postbox')
    size = request.form.get('size')
    now = datetime.datetime.now()


    date = now.strftime("%m/%d/%Y, %H:%M:%S")
    uid = str(uuid.uuid4())
    if "username" not in session:
        flash("the first you need log on")
        return redirect(url_for("dashboard"))
    username = session["username"]
    encoded_jwt = jwt.encode({'username': username}, app.secret_key, algorithm='HS256')
    _jwt = str(encoded_jwt).split("'")
    jwt_ = _jwt[1]
    headers = {"Authorization": "Bearer "+ jwt_}

    app.logger.warning(headers)
    if addressee and id_postbox and size:
        res = requests.post(f'https://pawelosinskiprzesylkiprojekt.herokuapp.com/labels/{username}', json={"address": addressee,
                                                                              "id_post_office": id_postbox,
                                                                              "date": date,
                                                                              "uid": uid,
                                                                              "size": size}, headers=headers)
        app.logger.warning(res.text)
        if res.status_code == 500:
            flash('Błąd połączenia z web service, spróbuj później')
            return render_template("sender/login_after_login.html")

        if not res:
            return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("dashboard"))
    return redirect(url_for("dashboard"))



@app.route('/sender/deletepackage/<package>', methods=['GET'])
def delete_package(package):
    username = session["username"]
    result = str(package).replace("'", '').strip()
    result = str(result).replace('"', '')
    res = requests.delete(f'https://pawelosinskiprzesylkiprojekt.herokuapp.com/labels/{username}/{result}')
    if res.status_code == 500:
        flash('Błąd połączenia z web service, spróbuj później')
        return render_template("sender/login_after_login.html")
    app.logger.warning(res.text)

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
