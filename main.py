from flask import Flask,render_template,redirect,url_for, request, flash
from static import weather_api_endpoint,geocoder_api_endpoint, timezone_api_endpoint
from flask_bootstrap import Bootstrap
import os
import requests
import datetime
import pytz



app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# default loc
default_location = "Gdynia"

def get_weather(location):

    response = requests.get(url=geocoder_api_endpoint,params={"q":location,"limit":1,"appid": os.environ.get("APP_ID")})
  
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
    utc_timezone= pytz.timezone("Europe/London")

    response = requests.get(url=timezone_api_endpoint,params={"apiKey":os.environ.get("TIME_ZONE_API_KEY"),"lat":lat,"long":lon})
    timezone_data = response.json()

    time = datetime.datetime.fromtimestamp(current['dt'],utc_timezone)

    offset = timezone_data['timezone_offset_with_dst'] - int(str(time).split(" ")[1].split(":")[2][3:])


    for i in ["sunrise","sunset","dt"]:
        time = datetime.datetime.fromtimestamp(current[i],utc_timezone)
        if offset < 0:
            time = time - datetime.timedelta(hours=abs(offset))
        elif offset > 0:
            time = time + datetime.timedelta(hours=offset)
        
        time= str(time).split(" ")[1].split(":")[:2]
        time = ":".join(time)

        current[i] = time

    current['weather'][0]['description'] = current['weather'][0]['description'].capitalize()
    current['visibility'] = int(current['visibility']/1000)
    current['wind_speed'] = int(current['wind_speed'])
    current['temp'] = int(current['temp'])
    
    hourly = data['hourly'][:24]

    for hour in hourly:
        time = datetime.datetime.fromtimestamp(hour['dt'],utc_timezone)
        if offset < 0:
            time = time - datetime.timedelta(hours=abs(offset))
        elif offset > 0:
            time = time + datetime.timedelta(hours=offset)
        
        time= str(time).split(" ")[1].split(":")[:2]
        time = ":".join(time)
        
        hour['temp'] = round(hour['temp'])
        hour['dt'] = time

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
        flash(f"Our service does not provide services in {location}")
        return redirect(url_for("weather"))

    
    return render_template('index.html',location=location,weather_current=weather_current,weather_hourly=weather_hourly)


# Run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)