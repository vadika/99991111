from flask import Flask, render_template, request, url_for
from flask_table import Table, Col
from pymongo import MongoClient, ASCENDING, DESCENDING

from datetime import date, timedelta, datetime

app = Flask(__name__)
dbclient = MongoClient()
db = dbclient.request911


# coordinate conversion

def DecimaltoDMLa(Decimal):
    d = int(float(Decimal))
    m = round((float(Decimal) - d) * 60, 3)
    if d >= 0:
        return "N" + str(abs(d)) + "º" + str(abs(m)) + "'"
    else:
        return "S" + str(abs(d)) + "º" + str(abs(m)) + "'"


def DecimaltoDMLo(Decimal):
    d = int(float(Decimal))
    m = round((float(Decimal) - d) * 60, 3)
    if d >= 0:
        return "E" + str(abs(d)) + "º" + str(abs(m)) + "'"
    else:
        return "W" + str(abs(d)) + "º" + str(abs(m)) + "'"


class RawCol(Col):
    """Class that will just output whatever it is given and will not
    escape it.
    """

    def td_format(self, content):
        return content


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
    url = RawCol('Map Link', allow_sort=False)
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'

        return url_for('display', sort=col_key, direction=direction)


@app.route('/d')
def display():
    field = request.args.get('sort')
    order = request.args.get('direction')
    direction = True

    if not field:
        field = "timestamp"

    if order == 'asc':
        direction = False

    yesterday = datetime.utcnow() - timedelta(days=1)

    items = []
    for loc in db.coords.find({"timestamp": {"$lt": yesterday}}).sort(field, ASCENDING if direction else DESCENDING):
        loc.update({'url': '<a href="https://www.google.com/maps/?q=' + loc['lat'] + ',' + loc['lon'] + '">Google</a>'})
        items.append(loc)

    table = LocationTable(items, sort_by=field, sort_reverse=direction)

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
           "acc": accuracy,
           "uas": uas,
           "ip": ip,
           "timestamp": datetime.utcnow()
           }
    res = db.coords.insert_one(req).inserted_id
    print("res = " + format(res))
    return ""


@app.route('/')
def mainpage():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
