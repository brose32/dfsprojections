import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl


my_url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=1&season=2021&month=3&season1=2021&ind=0&team=0,ts&rost=0&age=0&filter=&players=0"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")

table_body = page_soup.find("table", {"id" : "LeaderBoard1_dg1_ctl00"}).tbody
rows = table_body.findAll("tr")
#rank, team, pa, bb%, k%, bb/k, avg, obp, slg, ops, iso...
teamDict = {}
for row in rows:
    rowData = row.findAll("td")
    teamDict[rowData[1].text] = {
        "bb%": float(rowData[3].text.replace("%", '')),
        "k%" : float(rowData[4].text.replace("%", '')),
        "avg" : float(rowData[6].text),
        "obp" : float(rowData[7].text),
        "slg" : float(rowData[8].text),
        "ops" : float(rowData[9].text),
        "iso" : float(rowData[10].text)
    }
k_sum = 0
ops_sum = 0
for key in teamDict:
    k_sum += teamDict[key]["k%"]
    ops_sum += teamDict[key]["ops"]
k_avg = k_sum / len(teamDict)
ops_avg = ops_sum / len(teamDict)
for key in teamDict:
    teamDict[key]["kRating"] = teamDict[key]["k%"] / k_avg
    teamDict[key]["opsRating"] = teamDict[key]["ops"] / ops_avg

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
team_rating_sheet = wb.create_sheet("TeamHitRating")
team_rating_sheet.append(("TEAM", "kRating", "PopsRating", "OVR"))

for key in teamDict:
    team_rating_sheet.append((key, teamDict[key]["kRating"], 1 + (1 - teamDict[key]["opsRating"]),
                              (teamDict[key]["kRating"] * .5) + ((1 + (1 - teamDict[key]["opsRating"])) * .5)))

wb.save(my_file)



