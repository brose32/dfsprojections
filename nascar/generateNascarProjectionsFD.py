import sys
import csv
import openpyxl
import pymongo
from datetime import datetime
fpath = "C:\\Users\\brose32\\Downloads\\" + sys.argv[2]

fdf = open(fpath)
csv_fdf = csv.reader(fdf)
next(csv_fdf)
info = {}
for row in csv_fdf:
    info[row[3]] = {'ID': row[0], 'driverName': row[3], 'SAL': row[7], 'start': 0, 'avgDiffTrack': 0, 'avgTrackDriverRating': 0, 'avgFinishTrack': 0, 'avgDiffTrackType3yrType': 0, 'avgTrackTypeDriverRating3yr': 0, 'avgFinishTrackType3yr': 0, 'FDOWN': 0}

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.Workbook()
proj_sheet = wb.create_sheet("PROJECTIONS")
proj_sheet.append(('NAME', 'SAL', 'AVGDIFFTK', 'AVGTKDR', 'AVGFINTK', 'AVGDIFFTY', 'AVGTYDR', 'AVGFINTY', 'START', 'PROJFIN', 'PROJLEAD', 'PROJ', 'VAL', 'ID', 'FDOWN', 'RANK'))

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile="C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem")
mongo_db = client.nascar
race_collection = mongo_db.races

track = sys.argv[3]
laps = sys.argv[4]
track_races = race_collection.find({"track": track, "date": {"$gte": datetime(2013, 1, 1)}, "date": {"$lte": datetime(2024, 7, 1)}}).sort("date", pymongo.ASCENDING)

for race in track_races:
    for driver in race['results']:
        if driver['driverName'] in info:
            if driver.__contains__("avgDiffTrack3yr"):
                info[driver['driverName']]['avgDiffTrack'] = driver['avgDiffTrack3yr']
                info[driver['driverName']]['avgTrackDriverRating'] = driver['avgTrackDriverRating3yr']
                info[driver['driverName']]['avgFinishTrack'] = driver['avgFinishTrack3yr']
            if driver.__contains__("avgDiffTrackType3yrType"):
                info[driver['driverName']]['avgDiffTrackType3yrType'] = driver['avgDiffTrackType3yrType']
                info[driver['driverName']]['avgTrackTypeDriverRating3yr'] = driver['avgTrackTypeDriverRating3yr']
                info[driver['driverName']]['avgFinishTrackType3yr'] = driver['avgFinishTrackType3yr']

for driver in info:
    for key in info[driver]:
        if info[driver][key] == []:
            info[driver][key] = 0
start, avgDiffTrack3yr, avgTrackDriverRating3yr, avgFinishTrack3yr, avgDiffTrackType3yrType, avgTrackTypeDriverRating3yr, avgFinishTrackType3yr = [0.10425413, -0.0306184, -0.14532794, -0.29791075, -0.21624984, -0.10128464, -0.04572672]
laps_start, laps_avgDiffTrack3yr, laps_avgTrackDriverRating3yr, laps_avgFinishTrack3yr, laps_avgDiffTrackType3yrType, laps_avgTrackTypeDriverRating3yr, laps_avgFinishTrackType3yr = [-.00429117742, .00970549934, .000512970074, .00185743433, .00266710589, .00135473835, -.00234777918]
intercept_position = 34.2904966934781
laps_intercept_position = -0.04933787360709413
for i, driver in enumerate(info):
    finish_formula = f"=(I{i+2}*{start}) + (C{i+2}*{avgDiffTrack3yr}) + (D{i+2}*{avgTrackDriverRating3yr}) + (E{i+2}*{avgFinishTrack3yr}) + (F{i+2}*{avgDiffTrackType3yrType}) + (G{i+2}*{avgTrackTypeDriverRating3yr}) + (H{i+2}*{avgFinishTrackType3yr}) + {intercept_position}"
    lap_formula = f"=((I{i+2}*{laps_start}) + (C{i+2}*{laps_avgDiffTrack3yr}) + (D{i+2}*{laps_avgTrackDriverRating3yr}) + (E{i+2}*{laps_avgFinishTrack3yr}) + (F{i+2}*{laps_avgDiffTrackType3yrType}) + (G{i+2}*{laps_avgTrackTypeDriverRating3yr}) + (H{i+2}*{laps_avgFinishTrackType3yr}) + {laps_intercept_position})*{laps}*0.1"
    val_formula = f"=(J{i + 2}/(B{i + 2}/1000))"
    proj_formula = f"=({laps}* 0.1) + (41-P{i+2}) + (0.1 * K{i+2}) + (I{i + 2} - P{i+2} * 0.5)"
    rank_formula = f"=RANK(J{i + 2}, J:J, 1)"
    print(info[driver])
    proj_sheet.append((info[driver]['driverName'], float(info[driver]['SAL']), info[driver]['avgDiffTrack'], info[driver]['avgTrackDriverRating'], info[driver]['avgFinishTrack'], info[driver]['avgDiffTrackType3yrType'], info[driver]['avgTrackTypeDriverRating3yr'], info[driver]['avgFinishTrackType3yr'], info[driver]['start'], finish_formula, lap_formula, proj_formula, val_formula, info[driver]['ID'], info[driver]['FDOWN'], rank_formula))

wb.save(my_file)











