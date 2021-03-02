import json
import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl

my_url = "https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
table = page_soup.find("table", {"class": "table"})
table_body = table.tbody
point_guard_stats = table_body.findAll("tr", {"class": "GC-0 PG"})
shooting_guard_stats = table_body.findAll("tr", {"class": "GC-0 SG"})
small_forward_stats = table_body.findAll("tr", {"class": "GC-0 SF"})
power_forward_stats = table_body.findAll("tr", {"class": "GC-0 PF"})
center_stats = table_body.findAll("tr", {"class": "GC-0 C"})

avgfpg = center_stats[0].findAll("b")
centerRows = []
with open('teamAbbrs.json') as f:
    team_abbrs = json.load(f)
for team in center_stats:
    stats = team.findAll("b")
    stuff = [team_abbrs[team.td.span.text], "C", stats[-1].text]
    centerRows.append(stuff)

##adding new sheet to excel workbook at end of workbook


my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
dvoa_sheet = wb.create_sheet("TEAMOVP")
dvoa_sheet.append(('TEAM', 'POS', 'PTS', 'tOVP'))
sum = 0
for i in range(0, 30):
    dvoa_sheet['A' + str(i + 2)] = centerRows[i][0]
    dvoa_sheet['B' + str(i + 2)] = centerRows[i][1]
    dvoa_sheet['C' + str(i + 2)] = float(centerRows[i][2])
    sum += float(centerRows[i][2])
avgCenter = sum/30
for x in range(2, 32):
    perc = ((float(centerRows[x-2][2]) - avgCenter)/100) + 1
    dvoa_sheet['D' + str(x)] = perc


#adding pointguard dvoa to worksheet
pointGuardRows = []
for team in point_guard_stats:
    data = team.findAll("b")
    pointGuardRows.append([team_abbrs[team.td.span.text], "PG", data[-1].text])
pgSum = 0
for i in range(30, 60):
    dvoa_sheet['A' + str(i + 2)] = pointGuardRows[i-30][0]
    dvoa_sheet['B' + str(i + 2)] = pointGuardRows[i-30][1]
    dvoa_sheet['C' + str(i + 2)] = float(pointGuardRows[i-30][2])
    pgSum += float(pointGuardRows[i-30][2])
avgPG = pgSum/30
for x in range(32,62):
    perc = ((float(pointGuardRows[x - 32][2]) - avgPG) / 100) + 1
    dvoa_sheet['D' + str(x)] = perc

#SG
shootingGuardRows = []
for team in shooting_guard_stats:
    data = team.findAll("b")
    shootingGuardRows.append([team_abbrs[team.td.span.text], "SG", data[-1].text])
sgSum = 0
for i in range(60,90):
    dvoa_sheet['A' + str(i + 2)] = shootingGuardRows[i-60][0]
    dvoa_sheet['B' + str(i + 2)] = shootingGuardRows[i-60][1]
    dvoa_sheet['C' + str(i + 2)] = float(shootingGuardRows[i-60][2])
    sgSum += float(shootingGuardRows[i-60][2])
avgSG = sgSum/30
for x in range(62,92):
    perc = ((float(shootingGuardRows[x - 62][2]) - avgSG) / 100) + 1
    dvoa_sheet['D' + str(x)] = perc
#SF
smallForwardRows = []
for team in small_forward_stats:
    data = team.findAll("b")
    smallForwardRows.append([team_abbrs[team.td.span.text], "SF", data[-1].text])
sfSum = 0
for i in range(90,120):
    dvoa_sheet['A' + str(i + 2)] = smallForwardRows[i-90][0]
    dvoa_sheet['B' + str(i + 2)] = smallForwardRows[i-90][1]
    dvoa_sheet['C' + str(i + 2)] = float(smallForwardRows[i-90][2])
    sfSum += float(smallForwardRows[i-90][2])
sfAvg = sfSum/30
for x in range(92,122):
    perc = ((float(smallForwardRows[x - 92][2]) - sfAvg) / 100) + 1
    dvoa_sheet['D' + str(x)] = perc
#PF
powerForwardRows = []
for team in power_forward_stats:
    data = team.findAll("b")
    powerForwardRows.append([team_abbrs[team.td.span.text], "PF", data[-1].text])
pfSum = 0
for i in range(120,150):
    dvoa_sheet['A' + str(i+2)] = powerForwardRows[i-120][0]
    dvoa_sheet['B' + str(i + 2)] = powerForwardRows[i-120][1]
    dvoa_sheet['C' + str(i + 2)] = float(powerForwardRows[i-120][2])
    pfSum += float(powerForwardRows[i-120][2])
pfAvg = pfSum/30
for x in range(122,152):
    perc = ((float(powerForwardRows[x - 122][2]) - pfAvg) / 100) + 1
    dvoa_sheet['D' + str(x)] = perc
wb.save(my_file)
print("FantasyPros Webscrape Complete")
