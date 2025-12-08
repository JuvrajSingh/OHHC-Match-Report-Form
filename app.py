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
matches_sheet = sh.worksheet("Matches")
appearances_sheet = sh.worksheet("Appearances")


@app.route("/", methods=["GET", "POST"])
def index():
    # If user submits form
    if request.method == "POST":
        match_id = 1 # match_id TO DO
        match_date = request.form.get("match_date")
        team = request.form.get("team")
        opponent = request.form.get("opponent")
        venue = request.form.get("venue")
        season = "" # left empty so that arrayformula in this column works
        goals_for = request.form.get("goals_scored")
        goals_against = request.form.get("goals_conceded")

        matches_new_row = [match_id, match_date, team, opponent, venue, season, goals_for, goals_against]

        for column in matches_new_row:
            if not column:
                return render_template("index.html") # TO CHANGE
        
        matches_sheet.append_row(matches_new_row)

        return render_template("index.html") # TO CHANGE
    
    # If user opens form
    return render_template("index.html")

@app.route("/autocomplete")
def autocomplete():
    """Autocomplete for when user starts typing in name in players section"""
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