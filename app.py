from flask import Flask, render_template, request
from pymongo import MongoClient
import datetime

app = Flask(__name__)
dbclient = MongoClient()
db = dbclient.request911

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
    req = {"lat": latitude,
           "lon": longitude,
           "acc": accuracy,
           "uas": uas,
           "ip": ip,
           "timestamp": datetime.datetime.utcnow()
           }
    res = db.coords.insert_one(req).inserted_id
    print("res = " + format(res))
    return ""


@app.route('/')
def mainpage():
    return render_template("index.html")


if __name__ == '__main__':

    app.run()
