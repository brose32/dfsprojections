import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl


#last 14 days min 10 PA
my_url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=10&type=0&season=2021&month=2&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=&enddate=&page=1_1500"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")

table_body = page_soup.find("table", {"id" : "LeaderBoard1_dg1_ctl00"}).tbody
rows = table_body.findAll("tr")

hitterLast14Dict = {}

for row in rows:
    batter_data = row.findAll("td")
    hitterLast14Dict[batter_data[1].text] = {
        "NAME": batter_data[1].text,
        "TEAM": batter_data[2].text,
        "GAMES": float(batter_data[3].text),
        "PA": float(batter_data[5].text),
        "PA/G": float(batter_data[5].text) / float(batter_data[3].text),
        "1B": float(batter_data[7].text),
        "2B" : float(batter_data[8].text),
        "3B" : float(batter_data[9].text),
        "HR" : float(batter_data[10].text),
        "SLUG": (float(batter_data[7].text) + (float(batter_data[8].text) * 2) + (float(batter_data[9].text) * 3)
                 + (float(batter_data[10].text) * 4)) / float(batter_data[4].text),
        "BB%": float(batter_data[13].text) / float(batter_data[5].text),
        "SB/PA": float(batter_data[20].text) / float(batter_data[5].text),
        "R/PA": float(batter_data[11].text) / float(batter_data[5].text),
        "RBI/PA": float(batter_data[12].text) / float(batter_data[5].text)
    }
for key in hitterLast14Dict:
    hitterLast14Dict[key]["FDproj/PA"] = (hitterLast14Dict[key]["SLUG"] * 3) + (hitterLast14Dict[key]["BB%"] * 3) + \
                                         (hitterLast14Dict[key]["R/PA"] * 3.2) + (hitterLast14Dict[key]["RBI/PA"] * 3.5) + \
                                         (hitterLast14Dict[key]["SB/PA"] * 6)

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
hitter_last14_sheet = wb.create_sheet("HITTER LAST 14")
hitter_last14_sheet.append(("NAME", "FDproj/PA", "PA/G"))
for key in hitterLast14Dict:
    hitter_last14_sheet.append((hitterLast14Dict[key]["NAME"], hitterLast14Dict[key]["FDproj/PA"], hitterLast14Dict[key]["PA/G"]))
wb.save(my_file)

