from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/d')
def display():
    return render_template("display.html")

@app.route('/p')
def post():
    latitude = request.args.get('la')
    longitude = request.args.get('lo')
    accuracy = request.args.get('acc')
    uas = request.user_agent.string
    ip = request.remote_addr
    print(latitude, longitude, accuracy, uas, ip)
    return ""


@app.route('/')
def mainpage():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
