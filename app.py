from flask import Flask, render_template, make_response, request

app = Flask(__name__)

app.debug = False

users = {'posinski': {'firstname': 'Pawel', 'lastname': 'Osinski'
                      }
         }


@app.route('/check/<username>', methods=["GET"])
def check(username):
    origin = request.headers.get('Origin')
    result = {username: 'available'}
    if username in users:
        result = {username: 'taken'}
    response = make_response(result, 200)
    if origin is not None:
        response.headers["Access-Control-Allow-Origin"] = origin


@app.route('/')
def mainPage():
    return render_template("index.html")

@app.route('/sender/sign-up')
def signUp():
    return render_template("sender/sign-up.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5110)
"""formularz z podświetlanymi danymi na bieżąco
wyodrębnić 3 elementy: document.html, arkusz stylów, kod w javascripcie 
czy rzeczywiscie te 3 elementy są odseperowane od siebie będzie to sprawdzał"""