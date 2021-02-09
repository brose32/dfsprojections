import datetime
import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl

#this scrape collects nba season avg team ppg, home ppg, and away ppg

today = datetime.datetime.today()
formatted_date = today.strftime('%Y-%m-%d')

my_url = "https://www.teamrankings.com/nba/stat/points-per-game?date=" + formatted_date

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

#print(team_list)

#adding excel sheet

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
team_ppg_sheet = wb.create_sheet("TEAMPPG")
team_ppg_sheet.append(("Team Name", "Season", "Home", "Away"))

def nameToAbbr(name):
    if name == 'New York':
        return 'NYK'
    if name == 'New Orleans':
        return 'NOR'
    abbr_new = name.replace(" ", "")[:3].upper()
    #print(abbr_new)
    #checking special cases
    if abbr_new == 'BRO':
        abbr_new = 'BKN'
    if abbr_new == 'GOL':
        abbr_new = 'GSW'
    if abbr_new == 'SAN':
        abbr_new = 'SAS'
    if abbr_new == 'OKL':
        abbr_new = 'OKC'
    return abbr_new

#print(team_list[0])
#nameToLogo(team_list[0]['teamName'])
#print(team_list[0])
for team in team_list:
    abbr_team_name = nameToAbbr(team['teamName'])
    team['teamName'] = abbr_team_name
    team_ppg_sheet.append((team['teamName'], team['seasonppg'], team['homeppg'], team['awayppg']))

print(team_list[0])
wb.save(my_file)

print('team ppg scrape complete')


