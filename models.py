from flask import render_template, request
from config import TEAMS, MAX_PLAYERS, MIN_PLAYERS

def get_next_id(sheet, prefix: str, column: int=1, min_digits: int=4, counter: int=0) -> str:
    """Given a google worksheet with a unique ID column, generates the next auto-incrementing ID"""
    
    col_values = sheet.col_values(column) # Gets all values in specified column

    if len(col_values) <= 1:
        # ie if only a header exists
        num = 1 + counter
    else:
        last_id = col_values[-1]

        # Remove prefix and convert to integer
        try:
            num = int(last_id[len(prefix):]) + 1 + counter
        except ValueError:
            # If last_id doesn't match expected format, show an error
            message = "Sorry, looks like the most recent entry in the database does not have a valid format in the ID column. Please check the database to make sure that all looks okay, and that nobody has accidently edited anything"
            return apology(message)
        
    next_id = f"{prefix}{num:0{min_digits}d}"
    return next_id

def apology(message):
    return render_template("index.html", TEAMS=TEAMS, MAX_PLAYERS=MAX_PLAYERS, MIN_PLAYERS=MIN_PLAYERS, error=message, form=request.form)

def apology_walkover(message):
    return render_template("walkover.html", TEAMS=TEAMS, error=message, form=request.form)