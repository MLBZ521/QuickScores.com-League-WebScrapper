#!/usr/bin/env python3

import csv
import os
import re

import inquirer
import requests

from datetime import datetime, timedelta

from bs4 import BeautifulSoup


__about__ = "https://github.com/MLBZ521/QuickScores.com-League-WebScrapper"
__updated__ = "1/9/2024"
__version__ = "1.0.1"


def string_to_date_and_time(datetime_string: str, format_string: str = "%Y-%m-%dT%H:%M"):
	"""Convert a datetime formatted string into separate date and time strings

	Args:
		datetime_string (str):  A string of a date time object
		format_string (str, optional):  The format of the incoming string
			Defaults to "%Y-%m-%dT%H:%M"

	Returns:
		tuple:  (date as a string, time as a string)
	"""

	date_time_obj = datetime.strptime(datetime_string, format_string)
	return date_time_obj.strftime("%m/%d/%Y"), date_time_obj.strftime("%I:%M %p")


def game_times(time: str, time_str_format: str = "%I:%M %p"):
	"""Returns the start and end game times from the game one start time

	Args:
		time (str):  Game one start time as a string
		time_str_format (str, optional):  The format of the incoming and going string
			Defaults to "%I:%M %p"

	Returns:
		tuple:  (game one end and game two start time, game two end time)
	"""

	time_obj = datetime.strptime(time, time_str_format)
	g1_end_g2_start_time = (time_obj + timedelta(hours=1)).strftime(time_str_format)
	g2_end_time = (time_obj + timedelta(hours=2)).strftime(time_str_format)

	return g1_end_g2_start_time, g2_end_time


def main():
	"""Create a CSV of the schedule for the selected team
	and league formatted for import in Google Calendar"""

	# User Defined Variables
	save_location = os.path.expanduser("~/Downloads")
	quickscores_org = "chandleraz"

	# Define the address (location) for each field name
	locations = {
		"Snedigar 2": "Snedigar Sports Complex 4500 S Basha Rd Chandler, AZ 85248",
		"Snedigar 3": "Snedigar Sports Complex 4500 S Basha Rd Chandler, AZ 85248",
		"Snedigar 5": "Snedigar Sports Complex West 4001 S Alma School Rd, Chandler, AZ 85248",
		"Snedigar 6": "Snedigar Sports Complex West 4001 S Alma School Rd, Chandler, AZ 85248",
		"Tournament": "Snedigar Sports Park"
	}

	# Static Variables
	quickscores_base_url = "https://www.quickscores.com"
	quickscores_org_base_url = f"{quickscores_base_url}/Orgs"

	# Get the Org's available leagues
	org_leagues = BeautifulSoup(
		requests.get(f"{quickscores_base_url}/{quickscores_org}").text, features="html.parser")

	# Get the _latest_ Softball league
	# 37 = (Adult?) Softball
	season = org_leagues.find(attrs={"data-sport": "37"})

	# Expects different leagues are played on different days; get each day's league
	day_leagues = season.find_all(attrs={"class": "DayGroup"})

	# Get the individual leagues for each day
	available_leagues = {}

	for day in day_leagues:
		leagues = day.find_all("a")

		for league in leagues:
			day_league_name = league.text
			day_league_link = league.get("href")
			available_leagues[day_league_name] = day_league_link

	# add an extra option to allow exiting
	available_leagues["Exit"] = "Quit"

	# Loop the check in case there are multiple leagues that are being played in
	while True:

		# Prompt for which league to lookup
		answer = inquirer.prompt([
			inquirer.List(
				name = 'selected_league',
				message = "Select the league to lookup",
				choices = available_leagues.keys(),
				carousel = True
			),
		])

		selected_league = answer.get("selected_league")

		if selected_league == "Exit":
			break

		# Get the link for the selected league
		league_link = available_leagues.get(selected_league)

		# Get and parse the league's page
		league_page = BeautifulSoup(
			requests.get(f"{quickscores_base_url}{league_link}").text, features="html.parser")

		# Get the individual teams in each league
		league_teams = {}
		for team in league_page.find_all(title="Click for this team's schedule"):
			team_name = team.text
			team_link = team.get("href")
			league_teams[team_name] = team_link

		# Prompt for which team to lookup
		answer = inquirer.prompt([
			inquirer.List(
				name = 'selected_team',
				message = "Select the team to lookup",
				choices = league_teams.keys(),
				carousel = True
			),
		])

		selected_team = answer.get("selected_team")

		# Get the link for the selected team
		league_team_link = league_teams.get(selected_team)

		# Get and parse the team's page
		team_page = BeautifulSoup(
			requests.get(f"{quickscores_org_base_url}/{league_team_link}").text,
			features="html.parser"
		)

		# Get the weeks container(s) for the team plays
		weeks = team_page.find_all(attrs={"class": "week-container"})

		# Parse the weeks to get the team's schedule
		schedule = []

		for week in weeks[:-1]:
		# Get everything, except the fail week as this is typically
		# the tournament night which does list specifics

			date_time = week.find(attrs={"class": "e-time local-info"}).get("datetime")
			date, g1_start_time = string_to_date_and_time(date_time)
			field = week.find(title="Click for directions").string
			g1_end_g2_start_time, g2_end_time = game_times(g1_start_time)

			# Determine which team is home/away for the first game
			for team in week.find_all(attrs={"class": "team-name"}):
				if team_name := re.search(r"\s+H:\s(.+)\s", team.text):
					home_team = team_name[1]
				if team_name := re.search(r"\s+A:\s(.+)\s", team.text):
					away_team = team_name[1]

			schedule.extend((
				# Game 1
				{
					"Subject": f"{away_team} vs {home_team} \
						({re.sub('Snedigar ', 'F', field, flags=re.IGNORECASE)})",
					"Start Date": date,
					"Start Time": g1_start_time,
					"End Date": date,
					"End Time": g1_end_g2_start_time,
					"All Day Event": "FALSE",
					"Description": "",
					"Location": locations.get(field),
					"Private": "default",
				},
				# Game 2
				# Home/away team is reversed in game two
				{
					"Subject": f"{home_team} vs {away_team} \
						({re.sub('Snedigar ', 'F', field, flags=re.IGNORECASE)})",
					"Start Date": date,
					"Start Time": g1_end_g2_start_time,
					"End Date": date,
					"End Time": g2_end_time,
					"All Day Event": "FALSE",
					"Description": "",
					"Location": locations.get(field),
					"Private": "default",
				},
			))

		# Confirm the final week is the Tournament and add it to the schedule
		if re.search(
			r"Tournament.*", 
			weeks[-1].find(attrs={"class": "cell comment-only"}).find("p").string
		):

			game_date = f"{weeks[-1].find(attrs={'class': 'e-date'}).string} {datetime.now().year}"
			date = datetime.strptime(game_date, "%b %d %Y").strftime("%m/%d/%Y")

			schedule.append({
				"Subject": "Tournament",
				"Start Date": f"{date}",
				"Start Time": "06:20 PM",
				"End Date": f"{date}",
				"End Time": "10:20 PM",
				"All Day Event": "FALSE",
				"Description": "Tournament bracket, game times, and fields \
					are determined after conclusion of the regular season.",
				"Location": locations.get("Tournament"),
				"Private": "default",
			})

		# Export schedule to a csv
		with open(f"{save_location}/{selected_league}_{selected_team}.csv", 'w') as csv_file:

			w = csv.DictWriter(csv_file, schedule[0].keys())
			w.writeheader()

			for week in schedule:
				w.writerow(week)


if __name__ == "__main__":
	main()
