from flask import Flask, render_template, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # TO DO
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)