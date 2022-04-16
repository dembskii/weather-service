
from urllib import response
from flask import Flask,render_template,redirect,url_for,request
from static import current_weather_endpoint
from flask_bootstrap import Bootstrap
import os
import requests
import datetime




weather_symbols = {
    "Clouds" : '<i style="color: white; padding-top:20px;" class="fa-solid fa-cloud fa-5x"></i>',
    "Clear" : '<i style="color: orange;" class="fa-solid fa-sun fa-5x"></i>',
    "Mist" : '<i style="color: blue;" class="fa-solid fa-smog fa-5x"></i>',
    "Haze" : '<i style="color: blue;" class="fa-solid fa-smog fa-5x"></i>',
    "Dust" : '<i style="color: blue;" class="fa-solid fa-smog fa-5x"></i>',
    "Fog" : '<i style="color: blue;" class="fa-solid fa-smog fa-5x"></i>',
    "Sand" : '<i style="color: blue;" class="fa-solid fa-wind fa-5x"></i>',
    "Squall" : '<i style="color: blue;" class="fa-solid fa-wind fa-5x"></i>',
    "Tornado" : '<i style="color: blue;" class="fa-solid fa-tornado fa-5x"></i>',
    "Snow" : '<i style="color: blue;" class="fa-solid fa-snowflake fa-5x"></i>',
    "Rain" : '<i style="color: blue;" class="fa-solid fa-cloud-rain fa-5x"></i>',
    "Drizzle" : '<i style="color: blue;" class="fa-solid fa-cloud-rain fa-5x"></i>',
    "Thunderstorm" : '<i style="color: blue;" class="fa-solid fa-cloud-bolt fa-5x"></i>'
}


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
    current['dt'] = str(datetime.datetime.fromtimestamp(current['dt'])).split(" ")[0]
    current['sunrise'] = str(datetime.datetime.fromtimestamp(current['sunrise'])).split(" ")[1].split(":")[:2]
    current['sunrise'] = ":".join(current['sunrise'])
    current['weather'][0]['description'] = current['weather'][0]['description'].capitalize()
    current['visibility'] = int(current['visibility']/1000)
   
    
    current['sunset'] = str(datetime.datetime.fromtimestamp(current['sunset'])).split(" ")[1].split(":")[:2]
    current['sunset'] = ":".join(current['sunset'])
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
        location = request.form['location'].capitalize()
    weather = get_weather(location=location)
    weather_current = weather[0]
    weather_hourly = weather[1]

    print(weather_current)
    return render_template('index.html',location=location,weather_current=weather_current,weather_hourly=weather_hourly,symbols=weather_symbols)


# Run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)