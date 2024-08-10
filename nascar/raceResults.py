import json
import sys
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import re
import openpyxl
import pymongo
from datetime import datetime

for year in range(2024, 2025):
    for race in range(22, 23):
        if race < 10:
            my_url = f"https://www.driveraverages.com/nascar/race.php?sked_id={year}00{race}"
        else:
            my_url = f"https://www.driveraverages.com/nascar/race.php?sked_id={year}0{race}"
        print(my_url)
        uClient = urlopen(my_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        race_info = page_soup.find('div', {'id': 'BreadcrumbDiv'})
        race_info_list = race_info.findAll('li')
        track = race_info_list[3].text
        date_text = race_info_list[4].text
        date = re.search('^.*(?=(\sRace Results))', date_text).group(0)
        timestamp = datetime.strptime(date, "%b %d, %Y")

        with open('trackTypes.json') as f:
            track_types = json.load(f)
        track_type = track_types[track]
        track_data = {
            "track": track,
            "date": timestamp,
            "type": track_type,
        }

        table = page_soup.find('table', {'class': 'tabledata-nascar'})

        rows = table.findAll('tr')
        driver_data = []
        for i in range(1, len(rows)):
            row_data = rows[i].findAll('td')
            if row_data[13].text == '':
                driver_data.append({
                    "driverName": row_data[3].text,
                    "finish": float(row_data[0].text),
                    "laps": float(row_data[6].text),
                    "lapsLed": float(row_data[7].text),
                    "lapsLedPercentage": float(row_data[7].text) / float(row_data[6].text),
                    "start": float(row_data[1].text),
                    "completeRace": row_data[8].text == 'running',
                    "rating": 50.0,
                })
            else:
                driver_data.append({
                    "driverName": row_data[3].text,
                    "finish": float(row_data[0].text),
                    "laps": float(row_data[6].text),
                    "lapsLed": float(row_data[7].text),
                    "lapsLedPercentage": float(row_data[7].text) / float(row_data[6].text),
                    "start": float(row_data[1].text),
                    "completeRace": row_data[8].text == 'running',
                    "rating": float(row_data[13].text)
                })
        track_data['laps'] = driver_data[0]['laps']
        uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        client = pymongo.MongoClient(uri,
                             tls=True,
                             tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
        db = client.nascar
        races_collection = db.races
        res = races_collection.insert_one({
            "track": track_data['track'],
            "date": track_data['date'],
            "type": track_data['type'],
            "laps": track_data['laps'],
            "results": driver_data,
        })

        print(res.inserted_id)


# my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
# wb = openpyxl.load_workbook(my_file)
#
# avg_track_sheet = wb.create_sheet("ALLY400")
# avg_track_sheet.append(("DRIVER", "FINISH", "LAPS", "LAPSLED", "START", "RATING"))
#
# for driver in driver_data:
#     avg_track_sheet.append((driver['driverName'], driver['finish'], driver['laps'], driver['lapsLed'], driver['start'], driver['rating']))
#
# wb.save(my_file)


