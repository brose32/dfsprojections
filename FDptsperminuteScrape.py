import json
import sys

from bs4 import BeautifulSoup as soup

import requests
import openpyxl

my_url = 'https://rotocurve.com/nba/fantasy-points-per-minute/'
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Dnt": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
  }
#ua = UserAgent()
uClient = requests.get(my_url, headers=headers)
#page_html = uClient.read()

uClient.close()
page_soup = soup(uClient.text, "html.parser")
table = page_soup.find("table", {"class": "table"})
table_body = table.tbody
#print(table_body)
rows = table_body.findAll("tr")

name_list = []
with open('playerNames.json') as f:
    player_names = json.load(f)
for row in rows:
    playerFDpts_min = row.findAll("td", {"class": "bg-blue-lighter"})
    #FD points per minute on 50/50 ratio between last5 games and season average
    #could add ratio with last 10 games
    last5_seasonAvg = (float(playerFDpts_min[0].text.lstrip().rstrip()) * .5) + (float(playerFDpts_min[-1].text.lstrip().rstrip()) * .5)

    name_list.append({'name': player_names[row.td.text.lstrip().rstrip()], 'avg': last5_seasonAvg})
#print(name_list)

#setting excel sheet
my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
fd_pts_min_sheet = wb.create_sheet("FD PTS_MIN")
fd_pts_min_sheet.append(("NAME", "FD PTS/MIN"))
for player in name_list:
    fd_pts_min_sheet.append((player['name'], player['avg']))

wb.save(my_file)
print("FD pts per min scrape complete")


