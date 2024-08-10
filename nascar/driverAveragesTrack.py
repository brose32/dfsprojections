import json
import sys
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import openpyxl

my_url = "https://www.driveraverages.com/nascar/track_avg.php?trk_id=19"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")

table = page_soup.find('table', {'class': 'tabledata-nascar'})

rows = table.findAll('tr')
driver_data = []
for i in range(1, len(rows)):
    row_data = rows[i].findAll('td')
    driver_data.append({
        "driverName": row_data[1].text,
        "avgFinish": float(row_data[2].text),
        "races": float(row_data[3].text),
        "avgStart": float(row_data[9].text),
        "rating": float(row_data[13].text)
    })

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)

avg_track_sheet = wb.create_sheet("AVGTRACK")
avg_track_sheet.append(("DRIVER", "AVGFINISH", "RACES", "AVGSTART", "RATING"))

for driver in driver_data:
    avg_track_sheet.append((driver['driverName'], driver['avgFinish'], driver['races'], driver['avgStart'], driver['rating']))

wb.save(my_file)


