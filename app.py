from flask import Flask

app = Flask(__name__)

app.debug = False


@app.route('/check/<username>')
def check(username):
    if username == 'posinski':
        return {username: 'taken'}
    return {username: 'available'}


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
