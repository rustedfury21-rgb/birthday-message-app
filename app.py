
import os
from datetime import datetime

import gspread
from flask import Flask, render_template, request, redirect, url_for
from google.oauth2.service_account import Credentials


app = Flask(__name__)


# ============================================================
# GOOGLE SHEETS SETTINGS
# ============================================================

# You can paste your Google Sheet ID here.
# Example:
# https://docs.google.com/spreadsheets/d/ABC123XYZ/edit
#
# Your ID would be:
# ABC123XYZ

SPREADSHEET_ID = "1ZS-CtvFJj_LAV5hR4q4niZPoDTJXW9FO6fflt5zTpvI"

# Name of the tab inside your Google Sheet
SHEET_NAME = "DataSheet"


# Google Sheets permissions
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================

def get_sheet():
    """
    Connects to your Google Sheet using credentials.json.
    """

    if SPREADSHEET_ID == "PASTE_YOUR_GOOGLE_SHEET_ID_HERE":
        raise RuntimeError(
            "You haven't entered your Google Sheet ID yet."
        )

    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(SHEET_NAME)

    except gspread.WorksheetNotFound:

        # Automatically create the Messages tab
        worksheet = spreadsheet.add_worksheet(
            title=SHEET_NAME,
            rows=1000,
            cols=3
        )

        worksheet.append_row([
            "Name",
            "Message",
            "Submitted At"
        ])

    return worksheet


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def home():

    error = None

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()

        # -------------------------
        # Basic validation
        # -------------------------

        if not name:
            error = "Please enter your name."

        elif not message:
            error = "Please write a message."

        elif len(name) > 80:
            error = "Your name is too long."

        elif len(message) > 2000:
            error = "Your message is too long."

        else:

            try:

                sheet = get_sheet()

                # Add a new row to Google Sheets
                sheet.append_row([
                    name,
                    message,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ])

                # Send them to the thank-you page
                return redirect(url_for("thanks"))

            except Exception as e:

                print("ERROR:", e)

                error = (
                    "Something went wrong while saving "
                    "your message. Please try again."
                )

    return render_template(
        "index.html",
        error=error
    )


# ============================================================
# THANK YOU PAGE
# ============================================================

@app.route("/thanks")
def thanks():

    return render_template("thanks.html")


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
