from bs4 import BeautifulSoup as soup

from urllib.request import urlopen
import openpyxl
import json
import sys

my_url = "https://www.teamrankings.com/nfl/stat/points-per-game?date=2021-02-08"
uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
table = page_soup.find("table", {"class":"datatable"})
tbody = table.tbody
rows = tbody.findAll("tr")
team_ppg = []
with open('CityToAbbr.json') as f:
    city_to_abbr = json.load(f)
for row in rows:
    city = row.find("a").text
    ppg = float(row.find("td", {"class":"text-right"}).text)
    team_ppg.append((city_to_abbr[city],ppg))

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
team_snap_sheet = wb.create_sheet("TEAMPPG")
team_snap_sheet.append(("Team Name", "PPG"))
for team in team_ppg:
    team_snap_sheet.append((team[0],team[1]))
wb.save(my_file)