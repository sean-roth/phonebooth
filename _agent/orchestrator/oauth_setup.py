"""One-time Google OAuth bootstrap for the Sheets sync.

Run this ONCE, interactively (it opens a browser):

    python oauth_setup.py

Sign in as yourself and approve. The token is cached under ~/.config/phonebooth/
and reused on every future run -- including headless/scheduled ones. No
service-account key on disk, no sharing the Sheet with a robot account.

Prereq: save the OAuth *client* JSON you downloaded from Google Cloud
(APIs & Services -> Credentials -> Create credentials -> OAuth client ID,
application type "Desktop app") to:

    C:\\Users\\seanr\\.config\\phonebooth\\oauth-client.json
"""
from config import SHEETS_SPREADSHEET_ID, SHEETS_WORKSHEET
from sink import _gspread_client

if __name__ == "__main__":
    gc = _gspread_client()
    print("OAuth OK -- token cached under ~/.config/phonebooth/.")
    if SHEETS_SPREADSHEET_ID:
        sh = gc.open_by_key(SHEETS_SPREADSHEET_ID)
        titles = [ws.title for ws in sh.worksheets()]
        print(f"Opened spreadsheet: {sh.title!r}")
        print(f"Worksheets found:   {titles}")
        print(f"Target worksheet {SHEETS_WORKSHEET!r} present:",
              SHEETS_WORKSHEET in titles)
    else:
        print("SHEETS_SPREADSHEET_ID is not set yet -- skipping the open test.")
        print("Fill it into .env, then re-run to confirm access end-to-end.")