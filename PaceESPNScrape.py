import json
import sys
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl

my_url = "http://www.espn.com/nba/hollinger/teamstats/_/sort/paceFactor"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")

table = page_soup.find('table', {'class': 'tablehead'})
#print(table)
rows = table.findAll('tr')
team_pace_list = []
with open('CityToAbbr.json') as f:
    city_to_abbr = json.load(f)
#cleaning abbreviations
for i in range(2, len(rows)):
    team_name = rows[i].find("a").text
    abbr_name = city_to_abbr[team_name]
    pace = rows[i].find("td", {'class': 'sortcell'})
    team_pace_list.append({'PACE': float(pace.text), 'TEAM': abbr_name})

#create excel sheet

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
team_pace_sheet = wb.create_sheet("PACE")
team_pace_sheet.append(("TEAM", "PACE"))
sum = 0
for team in team_pace_list:
    team_pace_sheet.append((team['TEAM'], team['PACE']))
    sum += team['PACE']
team_pace_sheet.append(("League AVG", sum/30))
wb.save(my_file)
