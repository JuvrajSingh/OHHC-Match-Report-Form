from flask import Flask, render_template, request, jsonify, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
import os

from models import get_next_id, apology

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

MAX_PLAYERS = 18 # the maximum allowed number of players per side in a match
MIN_PLAYERS = 7 # the minimum required number of players per side in a match


@app.route("/", methods=["GET", "POST"])
def index():
    # If user submits form
    if request.method == "POST":
        match_id = get_next_id(matches_sheet, "M")
        match_date = request.form.get("match_date")
        team = request.form.get("team")
        opponent = request.form.get("opponent")
        venue = request.form.get("venue")
        season = "" # left empty so that arrayformula in this column works
        goals_for = request.form.get("goals_scored")
        goals_against = request.form.get("goals_conceded")

        matches_new_row = [match_id, match_date, team, opponent, venue, season, goals_for, goals_against]
        error_texts = ["Match ID", "Match date", "Team", "Opponent", "Venue", "Season", "Goals Scored", "Goals Conceded"]

        for column, error_text in zip(matches_new_row, error_texts):
            if not column:
                return apology(f"{error_text} is either blank or invalid")
        
        matches_sheet.append_row(matches_new_row, value_input_option="USER_ENTERED")

        # Add a new row to the appearances sheet per player per match
        for i in range(1, MAX_PLAYERS + 1):
            player_name = request.form.get(f"player_{i}")
            if player_name.strip():
                appearance_id = get_next_id(appearances_sheet, "A", min_digits=6)
                # I already have match ID
                player_id = request.form.get(f"player_id_{i}")
                player_goals = request.form.get(f"goals_{i}")

                appearances_new_row = [appearance_id, match_id, player_id, player_goals]
                error_texts_2 = ["Appearannce ID", "Match ID", "Player ID", "Player Goals"]

                for column, error_text in zip(appearances_new_row, error_texts_2):
                    if not column:
                        return apology(f"{error_text} is either blank or invalid")
                appearances_sheet.append_row(appearances_new_row, value_input_option="USER_ENTERED")

        return redirect(url_for("thanks"))
    
    # If user opens form
    return render_template("index.html", MAX_PLAYERS=MAX_PLAYERS, MIN_PLAYERS=MIN_PLAYERS)

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

@app.route("/thanks")
def thanks():
    # If user clicks "Submit another match report form" button
    if request.method == "POST":
        return redirect("/")
    
    # If user reaches page by submitting match report form
    return render_template("thanks.html")

if __name__ == "__main__":
    app.run(debug=True)