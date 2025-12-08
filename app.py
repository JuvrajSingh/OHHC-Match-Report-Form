from flask import Flask, render_template, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
import os

app = Flask(__name__)

# Setup for Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    os.path.join("credentials", "service_account.json"),
    scopes=SCOPES)
gc = gspread.authorize(creds)

sh = gc.open_by_key("1XuTyJb0PG8OIEHj-UosEqXW0m8mNu3iQUvJUXM8tw1E")
players_sheet = sh.worksheet("Players")


@app.route("/", methods=["GET", "POST"])
def index():
    # TO DO
    return render_template("index.html")

# Autocomplete for when user starts typing in name in players section
@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("query", "").strip().lower()

    if not query:
        return jsonify([])
    
    # Fetch whole sheet once
    records = players_sheet.get_all_records()

    # Filter on display_name, and return JSON array [{id, name, dob}, ...] as JS is expecting
    matches = []
    for r in records:
        name = r.get("display_name", "")
        if query in name.lower():
            matches.append({
                "id": r.get("player_id"),
                "name": name,
                "dob": r.get("date_of_birth")
            })

    return jsonify(matches[:10]) # limit autocomplete results to 10 names

if __name__ == "__main__":
    app.run(debug=True)