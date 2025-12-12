from flask import Flask, render_template, request, jsonify, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
import os

from models import get_next_id, apology, apology_walkover
from config import TEAMS, MAX_PLAYERS, MIN_PLAYERS, FORFEIT_RESULT

app = Flask(__name__)

# Setup for Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(
    os.path.abspath(os.path.join("credentials", "service_account.json")),
    scopes=SCOPES)
gc = gspread.authorize(creds)

# sh = gc.open_by_key("1XuTyJb0PG8OIEHj-UosEqXW0m8mNu3iQUvJUXM8tw1E") # LIVE SHEET
sh = gc.open_by_key("1lRbopWLaEgtoCLzoTgf5OR78_XK5x5mAA1nXwQYjlC8") # TESTER SHEET

players_sheet = sh.worksheet("Players")
matches_sheet = sh.worksheet("Matches")
appearances_sheet = sh.worksheet("Appearances")

records = players_sheet.get_all_records() # Fetch whole sheet once
players_by_id = {str(record["player_id"]): record["display_name"] for record in records} # build lookup dict


@app.route("/", methods=["GET", "POST"])
def index():
    # If user submits form
    if request.method == "POST":
        match_id = get_next_id(matches_sheet, "M")
        match_date = request.form.get("match_date")
        team = request.form.get("team")
        opponent = request.form.get("opponent", "").strip()
        venue = request.form.get("venue")
        season = "" # left empty so that arrayformula in this column works
        goals_for = request.form.get("goals_scored")
        goals_against = request.form.get("goals_conceded")

        matches_checks = [match_id, match_date, team, opponent, venue, goals_for, goals_against]
        error_texts = ["Match ID", "Match date", "Team", "Opponent", "Venue", "Goals Scored", "Goals Conceded"]

        for column, error_text in zip(matches_checks, error_texts):
            if not column:
                return apology(f"{error_text} is either blank or invalid")
        
        walkover_true = "N"
        matches_new_row = [match_id, match_date, team, opponent, venue, season, goals_for, goals_against, walkover_true]

        # Add a new row to the appearances sheet per player per match
        appearances_new_rows = []
        appearance_counter = 0
        player_ids = []
        goals_tally = 0
        for i in range(1, MAX_PLAYERS + 1):
            player_name = request.form.get(f"player_{i}", "").strip()
            if player_name:
                player_id = request.form.get(f"player_id_{i}")
                if not player_id:
                    return apology(f"Player '{player_name}' is not in the database. Please select from the suggestions")
                db_name = players_by_id.get(player_id)
                if not db_name or db_name != player_name:
                    return apology(f"Invalid player selection in row {i}.")
                
                appearance_id = get_next_id(appearances_sheet, "A", min_digits=6, counter=appearance_counter)
                # I already have match ID
                # I already have player ID
                player_goals = request.form.get(f"goals_{i}")

                appearances_checks = [appearance_id, player_goals]
                error_texts_2 = ["Appearannce ID", "Player Goals"]

                for column, error_text in zip(appearances_checks, error_texts_2):
                    if not column:
                        return apology(f"{error_text} is either blank or invalid")

                appearances_new_rows.append([appearance_id, match_id, player_id, player_goals])
                appearance_counter += 1
                player_ids.append(player_id)
                goals_tally += int(player_goals)

        if len(player_ids) != len(set(player_ids)):
            return apology("A player was selected twice")
        
        if int(goals_for) != goals_tally:
            return apology("Please make sure goals tally up. Sum of goals attributed to each player must equal to goals scored in the match")

        matches_sheet.append_row(matches_new_row, value_input_option="USER_ENTERED")
        for row in appearances_new_rows:
            appearances_sheet.append_row(row, value_input_option="USER_ENTERED")

        return redirect(url_for("thanks"))
    
    # If user opens form
    return render_template("index.html", TEAMS=TEAMS, MAX_PLAYERS=MAX_PLAYERS, MIN_PLAYERS=MIN_PLAYERS, form={})

@app.route("/autocomplete")
def autocomplete():
    """Autocomplete for when user starts typing in name in players section"""
    query = request.args.get("query", "").strip().lower()

    if not query:
        return jsonify([])

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

@app.route("/walkover", methods=["GET", "POST"])
def walkover():
    # If user submits form
    if request.method == "POST":
        match_id = get_next_id(matches_sheet, "M")
        match_date = request.form.get("match_date")
        team = request.form.get("team")
        opponent = request.form.get("opponent", "").strip()
        venue = request.form.get("venue")
        season = "" # left empty so that arrayformula in this column works
        goals_for = str(FORFEIT_RESULT) if request.form.get("forfeited") == "Opponent" else "0"
        goals_against = str(FORFEIT_RESULT) if request.form.get("forfeited") == "OHHC" else "0"

        matches_checks = [match_id, match_date, team, opponent, venue, goals_for, goals_against]
        error_texts = ["Match ID", "Match date", "Team", "Opponent", "Venue", "Goals Scored", "Goals Conceded"]

        for column, error_text in zip(matches_checks, error_texts):
            if not column:
                return apology_walkover(f"{error_text} is either blank or invalid")
            
        walkover_true = "Y"     
        matches_new_row = [match_id, match_date, team, opponent, venue, season, goals_for, goals_against, walkover_true]
        matches_sheet.append_row(matches_new_row, value_input_option="USER_ENTERED")

        return redirect(url_for("thanks"))
    
    # IF user opens form
    return render_template("walkover.html", TEAMS=TEAMS, form={})

@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    # If user clicks "Submit another match report form" button
    if request.method == "POST":
        return redirect("/")
    
    # If user reaches page by submitting match report form
    return render_template("thanks.html")

if __name__ == "__main__":
    app.run(debug=True)