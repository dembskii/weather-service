from flask import Flask
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

Bootstrap(app)

@app.route('/')
def home():
    return "Working"


# Run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)