import json
import sys

from bs4 import BeautifulSoup as soup

import requests
import openpyxl
import unicodedata
def strip_accents(text):
    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)
my_url = 'https://rotocurve.com/nba/fantasy-points-per-minute/'
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Dnt": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
  }

uClient = requests.get(my_url, headers=headers)
#page_html = uClient.read()

uClient.close()
page_soup = soup(uClient.text, "html.parser")
table = page_soup.find("table", {"class": "table"})
table_body = table.tbody
#print(table_body)
rows = table_body.findAll("tr")

name_list = []
with open('dkNormalizedPlayerNames.json') as f:
    player_names = json.load(f)
for row in rows:
    playerDKpts_min = row.findAll("td", {"class": "bg-green-light"})
    #DK points per minute on 50/50 ratio between last5 games and season average
    #could add ratio with last 10 games
    dk_last5_seasonAvg = (float(playerDKpts_min[0].text.lstrip().rstrip()) * .5) + (
                float(playerDKpts_min[-1].text.lstrip().rstrip()) * .5)
    if row.td.text.lstrip().rstrip() == "Aleksej Pokuševski":
        name_list.append({'name': "Aleksej Pokusevski",'DKavg': dk_last5_seasonAvg})
        continue
    elif row.td.text.lstrip().rstrip() == "Ömer Yurtseven":
        name_list.append({'name': "Omer Yurtseven", 'DKavg': dk_last5_seasonAvg})
        continue
    elif row.td.text.lstrip().rstrip() == "Vít Krej?í":
        name_list.append({'name': "Vit Krejci", 'DKavg': dk_last5_seasonAvg})
        continue
    elif row.td.text.lstrip().rstrip() == "Moussa Diabaté":
        name_list.append({'name': "Moussa Diabate", 'DKavg': dk_last5_seasonAvg})
        continue
    # name_list.append({'name': row.td.text.lstrip().rstrip(), 'DKavg': dk_last5_seasonAvg})
    name_list.append({'name': player_names[row.td.text.lstrip().rstrip().replace(' Jr.', '').replace(' Jr', '').replace(' Sr', '').replace(' III', '').replace(' II', '').replace(
            ' Sr.', '').replace(' IV', '').replace('.', '').upper().replace("'", '')], 'DKavg': dk_last5_seasonAvg})

#print(name_list)

#setting excel sheet
my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)

dk_pts_min_sheet = wb.create_sheet("DK PTS_MIN")
dk_pts_min_sheet.append(("NAME", "DK PTS/MIN"))
for player in name_list:
    dk_pts_min_sheet.append((player['name'], player['DKavg']))

wb.save(my_file)
print("dk pts per min scrape complete")


