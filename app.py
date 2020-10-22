from flask import Flask, render_template

app = Flask(__name__)

app.debug = False

users = {'posinski': {'firstname': 'Pawel', 'lastname': 'Osinski'
                      }
         }


@app.route('/check/<username>')
def check(username):
    if username in users:
        return {username: 'taken'}
    return {username: 'available'}


@app.route('/')
def hello_world():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
