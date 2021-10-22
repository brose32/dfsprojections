from bs4 import BeautifulSoup as soup

from urllib.request import urlopen
import openpyxl
import json
import sys

my_url = "https://www.teamrankings.com/nfl/stat/plays-per-game"
uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
table = page_soup.find("table", {"class":"datatable"})
tbody = table.tbody
rows = tbody.findAll("tr")
team_snaps = []
with open('CityToAbbr.json') as f:
    city_to_abbr = json.load(f)
for row in rows:
    city = row.find("a").text
    snaps = float(row.find("td", {"class":"text-right"}).text)
    team_snaps.append((city_to_abbr[city],snaps))

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
team_snap_sheet = wb.create_sheet("TEAMSNAPs")
team_snap_sheet.append(("Team Name", "Snaps/g"))
for team in team_snaps:
    team_snap_sheet.append((team[0],team[1]))
wb.save(my_file)

