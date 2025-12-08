def get_next_id(sheet, prefix: str, column: int=1, min_digits: int=4) -> str:
    """Given a google worksheet with a unique ID column, generates the next auto-incrementing ID"""
    
    col_values = sheet.col_values(column) # Gets all values in specified column

    if len(col_values) <= 1:
        # ie if only a header exists
        num = 1
    else:
        last_id = col_values[-1]

        # Remove prefix and convert to integer
        try:
            num = int(last_id[len(prefix):]) + 1
        except ValueError:
            # If last_id doesn't match expected format, show an error
            # TO DO - return apology message
            return None
        
    next_id = f"{prefix}{num:0{min_digits}d}"
    return next_id