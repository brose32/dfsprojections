import datetime
import json
import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl

#this scrape collects nba season avg team ppg, home ppg, and away ppg

today = datetime.datetime.today()
formatted_date = today.strftime('%Y-%m-%d')

#my_url = "https://www.teamrankings.com/nba/stat/points-per-game?date=" + formatted_date
# my_url = "https://www.teamrankings.com/nba/stat/points-per-game"
my_url = "https://www.teamrankings.com/nba/stat/points-per-game?date=2023-06-13"
uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
table = page_soup.find("table")
table_body = table.tbody
rows = table_body.findAll("tr")
team_list = []

for row in rows:
    team_name = row.find("td", {'class': 'text-left nowrap'})
    team_ppgs = row.findAll('td', {'class': 'text-right'})
    team_list.append({'teamName': team_name.text, 'seasonppg': float(team_ppgs[0].text), 'homeppg': float(team_ppgs[3].text),
                      'awayppg': float(team_ppgs[4].text)})

#adding excel sheet

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
team_ppg_sheet = wb.create_sheet("TEAMPPG")
team_ppg_sheet.append(("Team Name", "Season", "Home", "Away"))

with open('CityToAbbr.json') as f:
    city_to_abbr = json.load(f)
#cleaning abbreviations
for team in team_list:
    abbr_team_name = city_to_abbr[team['teamName']]
    team['teamName'] = abbr_team_name
    team_ppg_sheet.append((team['teamName'], team['seasonppg'], team['homeppg'], team['awayppg']))

#fffprint(team_list[0])
wb.save(my_file)

print('team ppg scrape complete')


