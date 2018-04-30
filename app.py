from flask import Flask, render_template, request, url_for
from flask_table import Table, Col
from pymongo import MongoClient
import datetime

app = Flask(__name__)
dbclient = MongoClient()
db = dbclient.request911


# coordinate conversion

def DecimaltoDMLa(Decimal):
    d = int(float(Decimal))
    m = round((float(Decimal) - d) * 60, 3)
    if d >= 0:
        return "N" +str(abs(d)) + "º" + str(abs(m)) + "'"
    else:
        return "S" + str(abs(d)) + "º" + str(abs(m)) + "'"


def DecimaltoDMLo(Decimal):
    d = int(float(Decimal))
    m = round((float(Decimal) - d) * 60, 3)
    if d >= 0:
        return "E" + str(abs(d)) + "º" + str(abs(m)) + "'"
    else:
        return "W" + str(abs(d)) + "º" + str(abs(m)) + "'"


class LatCol(Col):
    def td_format(self, coords):
       return DecimaltoDMLa(coords)

class LonCol(Col):
    def td_format(self, coords):
       return DecimaltoDMLo(coords)


# data class to display a table
class LocationTable(Table):
    timestamp = Col('timestamp')
    uas = Col('Browser')
    ip = Col('IP address')
    lon = LatCol('Longitude')
    lat = LonCol('Latitude')
    acc = Col('Accuracy')
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction =  'desc'
        else:
            direction = 'asc'
        return url_for('display', sort=col_key, direction=direction)



@app.route('/d')
def display():
    items = []
    for loc in db.coords.find().sort("timestamp"):
        items.append(loc)

    table = LocationTable(items)

    return render_template("display.html", table=table)


@app.route('/p')
def post():
    latitude = request.args.get('la')
    longitude = request.args.get('lo')
    accuracy = request.args.get('acc')
    uas = request.user_agent.string
    ip = request.remote_addr
    print(latitude, longitude, accuracy, uas, ip)
    print(DecimaltoDMLa(latitude), DecimaltoDMLo(longitude))
    req = {"lat": latitude,
           "lon": longitude,
           "coord": DecimaltoDMLa(latitude) + " " + DecimaltoDMLo(longitude),
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
