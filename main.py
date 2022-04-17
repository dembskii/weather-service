from flask import Flask,render_template,redirect,url_for,request, flash
from static import weather_api_endpoint
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
    response = requests.get(weather_api_endpoint,params=params)
    data = response.json()
    print(response.url)

    current = data['current']
   
    current['dt'] = str(datetime.datetime.fromtimestamp(current['dt'])).split(" ")[0]
    current['sunrise'] = str(datetime.datetime.fromtimestamp(current['sunrise'])).split(" ")[1].split(":")[:2]
    current['sunrise'] = ":".join(current['sunrise'])
    current['weather'][0]['description'] = current['weather'][0]['description'].capitalize()
    current['visibility'] = int(current['visibility']/1000)
    current['wind_speed'] = int(current['wind_speed'])
    current['temp'] = int(current['temp'])
    
    current['sunset'] = str(datetime.datetime.fromtimestamp(current['sunset'])).split(" ")[1].split(":")[:2]
    current['sunset'] = ":".join(current['sunset'])
    hourly = data['hourly'][:24]

    for hour in hourly:
        date = str(datetime.datetime.fromtimestamp(hour['dt'])).split(" ")[1].split(":")[:2]
        date = ":".join(date)
        hour['temp'] = round(hour['temp'])
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
        location = request.form['location'].capitalize()
        if location == "":
            flash("You have to pass any location")
            return redirect(url_for('weather'))
    try:

        weather = get_weather(location=location)
        weather_current = weather[0]
        weather_hourly = weather[1]
    except Exception:
        flash(f"Our service does not provide in {location}")
        return redirect(url_for("weather"))

    print(weather_current)
    return render_template('index.html',location=location,weather_current=weather_current,weather_hourly=weather_hourly)


# Run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)