import json
import re

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl
import sys

my_url = 'https://www.covers.com/sports/nba/matchups'

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
#matchups = page_soup.findAll("div", {"class": "cmg_game_container"})
away_teams = page_soup.findAll("div", {"class": "cmg_matchup_list_column_1"})
home_teams = page_soup.findAll("div", {"class": "cmg_matchup_list_column_3"})
lines_table = page_soup.findAll("div", {"class": "cmg_team_live_odds"})
with open('teamAbbrs.json') as f:
    team_abbrs = json.load(f)
away_teams_list = []
home_teams_list = []
lines = []
#cleaning team abbreviations and adding to list
for team in away_teams:
    away_teams_list.append(team_abbrs[team.div.text.strip()[:3].rstrip()])
for team in home_teams:
    home_teams_list.append(team_abbrs[team.div.text.strip()[3:].lstrip()])

for game in lines_table:
    temp = re.findall(r'-?\d*\.?\d+', game.text)
    if len(temp) == 1 :
        temp.append(0)
    if len(temp) > 0 :
        lines.append({'total' : float(temp[0]), 'homespread': float(temp[1])})
    else:
        lines.append({'total' : 0, 'homespread': 0})
#print(lines)
#adding excel sheet to workbook

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
lines_sheet = wb.create_sheet("VEGAS_LINES")
lines_sheet.append(("HOME TEAM LINE", "O/U", "HOME TEAM", "HOME TOTAL", "AWAY TEAM", "AWAY TOTAL"))

for i in range(0, len(lines)):
    home_total = (lines[i]['total']/2) - (lines[i]['homespread'] / 2)
    lines_sheet.append((lines[i]['homespread'], lines[i]['total'], home_teams_list[i], home_total, away_teams_list[i],
                        (lines[i]['total'] - home_total)))

wb.save(my_file)