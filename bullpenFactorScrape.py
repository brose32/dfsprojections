import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl

my_url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=0&season=2021&month=0&season1=2021&ind=0&team=0,ts&rost=0&age=0&filter=&players=0"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")

table_body = page_soup.find("table", {"id" : "LeaderBoard1_dg1_ctl00"}).tbody
rows = table_body.findAll("tr")

bullpenDict = {}

for row in rows:
    bullpen_data = row.findAll("td")
    #rank, team, w, l, era, g, gs, cg, sho, sv, hld, bs, ip, tbf, h, r, er, hr, bb, ibb, hbp, wp, bk, so
    bullpenDict[bullpen_data[1].text] = {
        "ip" : float(bullpen_data[12].text),
        "h" : float(bullpen_data[14].text),
        "r" : float(bullpen_data[15].text),
        "hr" : float(bullpen_data[17].text),
        "bb" : float(bullpen_data[18].text),
        "ibb" : float(bullpen_data[19].text),
        "hbp" : float(bullpen_data[20].text)
    }

for key in bullpenDict:
    bullpenDict[key]["FDpoints/ip"] = ((bullpenDict[key]["h"] * 3) + (bullpenDict[key]["hr"] * 12) + \
                                      (bullpenDict[key]["r"] * 3.2) + (bullpenDict[key]["bb"] * 3) + \
                                      (bullpenDict[key]["ibb"] * 3) + (bullpenDict[key]["hbp"] * 3)) / (bullpenDict[key]["ip"])

FDbullpen_pts_sum = 0
for key in bullpenDict:
    FDbullpen_pts_sum += bullpenDict[key]["FDpoints/ip"]
FDbullpen_avg = FDbullpen_pts_sum / len(bullpenDict)

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
bullpen_rating_sheet = wb.create_sheet("BULLPEN RATING")
bullpen_rating_sheet.append(("TEAM", "FD RATING"))
for key in bullpenDict:
    bullpen_rating_sheet.append((key, bullpenDict[key]["FDpoints/ip"] / FDbullpen_avg))

wb.save(my_file)