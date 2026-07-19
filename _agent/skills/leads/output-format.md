# Output format — tracker rows

Leads are written in the same 13-column format as the live SNR-Cold-Call-Tracker
Google Sheet, so a batch appends cleanly.

## Columns (in order)
1. Source — "Places (mfg)"
2. Segment — "Manufacturer"
3. Company
4. Phone — formatted (XXX) XXX-XXXX, from the Maps listing only
5. Region — "City, ST"
6. Contact — blank at sourcing time
7. Status — "Not called"
8. Last Touch — blank
9. Next Touch — blank
10. Hiring Cadence # — blank
11. Info Sent — blank
12. 60-Day Re-dial — blank
13. Notes — "[H|M|L] <category> · <one-line size/fit signal>"

## Status vocabulary (for the human, once calling)
Not called · No answer · Left VM · Callback · Interested · Email only ·
Disqualified · Refused · Booked · Pilot

## Status colors (conditional formatting on the sheet)
Not called F3F3F3 · No answer FCE5CD · Left VM FFF2CC · Callback FFE599 ·
Interested D9EAD3 · Email only CFE2F3 · Disqualified D9D9D9 · Refused F4CCCC ·
Booked B6D7A8 · Pilot 93C47D
Overdue "Next Touch" (date in the past) -> F4CCCC.

## Delivery
- Clean keepers -> main lead sheet, H-tier first.
- Ambiguous (model unsure) -> a short "review" tab, for the human to judge.
- Never overwrite existing rows; append only.
