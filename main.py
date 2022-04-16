
from urllib import response
from flask import Flask,render_template,redirect,url_for,request
from static import current_weather_endpoint
from flask_bootstrap import Bootstrap
import os
import requests
import datetime


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# default loc
default_location = "Gdynia"

def get_weather(location):

    response = requests.get(url="http://api.openweathermap.org/geo/1.0/direct?",params={"q":location,"limit":1,"appid": os.environ.get("APP_ID")})
    lon = response.json()[0]["lon"]
    lat = response.json()[0]["lat"]


    params= {
        "lat" : lat,
        "lon" : lon,
        "exclude" : ["minutely","daily","alerts"],
        'appid' : os.environ.get("APP_ID"),
        "units" : "metric"

    }
    response = requests.get("https://api.openweathermap.org/data/2.5/onecall?",params=params)
    data = response.json()
    print(response.url)
    current = data['current']
    current['sunrise'] = str(datetime.datetime.fromtimestamp(current['sunrise'])).split(" ")[1].split(":")[:2]
    current['sunset'] = str(datetime.datetime.fromtimestamp(current['sunset'])).split(" ")[1].split(":")[:2]

    hourly = data['hourly'][:24]
    for hour in hourly:
        date = str(datetime.datetime.fromtimestamp(hour['dt'])).split(" ")[1]
        
        hour['dt'] = date

    return current,hourly

Bootstrap(app)

@app.route('/')
def home():
    return redirect(url_for('weather'))

@app.route("/weather",methods=["GET","POST"])
def weather():
    location = default_location
    if request.method == "POST":
        location = request.form['location']

    weather_current =get_weather(location=location)[0]


    return render_template('index.html',location=location,weather=str(weather_current))


# Run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)