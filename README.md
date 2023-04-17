# QuickScores.com League WebScrapper

This is a simple script to scrape QuickScores.com's website and export team schedules to a csv file.  The csv is formatted for direct import into Google Calendar.

QuickScores' does have an API available for their platform, but the documentation seems to imply it's only available for the organizations that are utilizing (paying for) the platform; i.e. not for public consumption.  So I did not ask if they'd be willing to grant me a personal token.

QuickScores' also provides WebCals that you can subscribe to, but I don't particularly like how they appear -- only one game shows for a double header, etc.  So the csv displays the events how I'd prefer, e.g. individual events per game, proper visitor versus home team, including the Field Number in the event name:  `Visitor vs Home (F#)`.


# Why

I play in several adult softball leagues and previous to writing this script, I used an Excel doc that I would enter the team's schedule into.  Eventually, I added some formulas and automation logic to the Excel doc, but it still took a bit of time to transpose the schedule.  I used this as an opportunity to utilize some Python libraries I had not yet used (mainly Beautiful Soup and Inquirer).


# How to use

If anyone wants to utilize this, you should just need to simply change the `quickscores_org` variable to your league's organization name within the `main` function.

You'll need Python3 and follow the steps below.

Note:  I only tested this on macOS, but I did notice mentionings that Inquirer may or may not work reliably on Windows.


# Setup

```shell

# Create a directory to clone project into
mkdir "QuickScores.com League WebScrapper" && cd "QuickScores.com League WebScrapper"

# Clone this repository
git clone https://github.com/MLBZ521/QuickScores.com-League-WebScrapper.git .

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the required packages:
pip install -r ./requirements.txt
```


# Example usage

```

$ python3 ./get_schedule.py
[?] Select the league to lookup: Tuesday Men's D1
   Sunday Co-Rec D
   Monday Co-Rec D1
   Monday Co-Rec D2
 > Tuesday Men's D1
   Tuesday Men's D2
   Thursday Men's D1
   Thursday Men's D2
   Friday D1 - Single
   Friday D2 - Single
   Friday Co-Rec D - Double
   Exit

[?] Select the team to lookup: No Talent
   Molossers
   Diablos
   Warriors
   Cactus Foot & Ankle
   Fat Chance
   Swingers
 > No Talent
   Inglorious Batters
```
