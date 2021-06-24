import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl

my_url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=sta&lg=all&qual=5&type=1&season=2021&month=3&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=2021-01-01&enddate=2021-12-31&page=1_300"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")

table_body = page_soup.find("table", {"id" : "LeaderBoard1_dg1_ctl00"}).tbody
rows = table_body.findAll("tr")

pitcherRatingDict = {}

for row in rows:
    rowData = row.findAll("td")
    pitcherRatingDict[rowData[1].text] = {
        "WHIP" : float(rowData[11].text) + 2
    }
whip_sum = 0
for key in pitcherRatingDict:
    whip_sum += pitcherRatingDict[key]["WHIP"]
whip_avg = whip_sum / len(pitcherRatingDict)

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
pitcher_rating_sheet = wb.create_sheet("PITCHER RATING")
pitcher_rating_sheet.append(("NAME", "RATING"))
for key in pitcherRatingDict:
    pitcher_rating_sheet.append((key, pitcherRatingDict[key]["WHIP"] / whip_avg))

wb.save(my_file)

