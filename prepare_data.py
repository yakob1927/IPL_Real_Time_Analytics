
import json
import zipfile
import requests
import pandas as pd

from pathlib import Path
from io import BytesIO

# Create data folder
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# IPL historical dataset
URL = "https://cricsheet.org/downloads/ipl_json.zip"

print("Downloading IPL dataset...")

response = requests.get(URL, timeout=180)
response.raise_for_status()

print("Download completed!")
print("Extracting IPL matches...")

delivery_rows = []

with zipfile.ZipFile(BytesIO(response.content)) as archive:

    json_files = [
        name for name in archive.namelist()
        if name.lower().endswith(".json")
        and not name.startswith("__MACOSX")
    ]

    for filename in json_files:

        try:
            with archive.open(filename) as file:
                match = json.load(file)

            info = match.get("info", {})
            teams = info.get("teams", [])

            match_id = Path(filename).stem
            outcome = info.get("outcome", {})
            toss = info.get("toss", {})

            dates = info.get("dates", [])
            match_date = str(dates[0]) if dates else ""

            for innings_number, innings in enumerate(
                match.get("innings", []), start=1
            ):

                batting_team = innings.get("team", "Unknown")

                bowling_teams = [
                    team for team in teams
                    if team != batting_team
                ]

                bowling_team = (
                    bowling_teams[0] if bowling_teams else "Unknown"
                )

                for over_data in innings.get("overs", []):

                    over_number = over_data.get("over", 0) + 1

                    for ball_number, delivery in enumerate(
                        over_data.get("deliveries", []), start=1
                    ):

                        runs = delivery.get("runs", {})
                        extras = delivery.get("extras", {})
                        wickets = delivery.get("wickets", [])

                        delivery_rows.append({

                            "match_id": match_id,
                            "season": str(info.get("season", "")),
                            "date": match_date,
                            "venue": info.get("venue", ""),
                            "winner": outcome.get("winner", ""),
                            "toss_winner": toss.get("winner", ""),
                            "toss_decision": toss.get("decision", ""),

                            "innings": innings_number,
                            "over": over_number,
                            "ball": ball_number,

                            "batting_team": batting_team,
                            "bowling_team": bowling_team,

                            "batter": delivery.get("batter", ""),
                            "bowler": delivery.get("bowler", ""),

                            "batter_runs": runs.get("batter", 0),
                            "total_runs": runs.get("total", 0),

                            "wides": extras.get("wides", 0),
                            "noballs": extras.get("noballs", 0),
                            "byes": extras.get("byes", 0),
                            "legbyes": extras.get("legbyes", 0),

                            "is_wicket": len(wickets) > 0,

                            "wicket_types": ", ".join(
                                wicket.get("kind", "")
                                for wicket in wickets
                            )
                        })

        except Exception as error:
            print("Skipping:", filename, error)

# Convert to DataFrame
df = pd.DataFrame(delivery_rows)

if df.empty:
    raise ValueError("No IPL data found!")

# Save CSV
output = DATA_DIR / "ipl_deliveries.csv"

df.to_csv(output, index=False)

print("\nIPL dataset prepared successfully!")
print("Total deliveries:", len(df))
print("Total matches:", df["match_id"].nunique())
print("CSV saved at:", output)
