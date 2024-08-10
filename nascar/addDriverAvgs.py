import pymongo
from datetime import datetime

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                             tls=True,
                             tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
db = client.nascar
races_collection = db.races

# sample_races = races_collection.find({"date": {"$gte": datetime(2013, 1, 1)}})
sample_races = races_collection.find({"date": {"$gte": datetime(2024, 7, 21)}})

for sample_race in sample_races:
    race_docs = races_collection.find({"track": sample_race['track'], "date": sample_race['date']})[0]
    print(race_docs['track'], race_docs['date'])
    all_track_races = races_collection.find({"track": sample_race['track'], "date": {"$lt": race_docs['date']}})

    driver_results = {}
    race_drivers = [race_driver['driverName'] for race_driver in race_docs['results']]
    for race in all_track_races:
        laps = race['laps']
        for driver in race['results']:
            if driver['laps'] < laps:
                continue
            elif driver['driverName'] in race_drivers:
                if driver_results.__contains__(driver['driverName']):
                    driver_results[driver['driverName']]['avgDiffTrack'].append(driver['finish'] - driver['start'])
                    driver_results[driver['driverName']]['avgDriverRating'].append(driver['rating'])
                    driver_results[driver['driverName']]['avgFinishTrack'].append(driver['finish'])
                else:
                    driver_results[driver['driverName']] = {
                        "avgDiffTrack": [driver['finish'] - driver['start']],
                        "avgDriverRating": [driver['rating']],
                        "avgFinishTrack": [driver['finish']]
                    }

    for driver in driver_results:
        driver_results[driver]['trackRaces'] = len(driver_results[driver]['avgFinishTrack'])
        driver_results[driver]['avgDiffTrack'] = sum(driver_results[driver]['avgDiffTrack']) / len(driver_results[driver]['avgDiffTrack'])
        driver_results[driver]['avgDriverRating'] = sum(driver_results[driver]['avgDriverRating']) / len(driver_results[driver]['avgDriverRating'])
        driver_results[driver]['avgFinishTrack'] = sum(driver_results[driver]['avgFinishTrack']) / len(driver_results[driver]['avgFinishTrack'])

    for i in range(len(race_docs['results'])):
        for d in driver_results:
            if race_docs['results'][i]['driverName'] == d:
                race_docs['results'][i]['avgDiffTrack3yr'] = driver_results[d]['avgDiffTrack']
                race_docs['results'][i]['avgTrackDriverRating3yr'] = driver_results[d]['avgDriverRating']
                race_docs['results'][i]['avgFinishTrack3yr'] = driver_results[d]['avgFinishTrack']
                race_docs['results'][i]['trackRaces'] = driver_results[d]['trackRaces']
    # print(race_docs['results'][0])

    # filter = {"track": "Pocono", "date": race_docs['date']}
    # races_collection.update_one(filter, {"$set": {"results": race_docs['results']}})

    track_type_docs = races_collection.find({"type": race_docs['type'], "date": {"$lt": race_docs['date'], "$gt": datetime(race_docs['date'].year- 3, 1, 1)}, "track": {"$ne": race_docs['track']}})

    for driver in driver_results:
        driver_results[driver]['avgDiffTrackType'] = []
        driver_results[driver]['avgDriverRatingType'] = []
        driver_results[driver]['avgFinishTrackType'] = []

    for race in track_type_docs:
        laps = race['laps']
        for driver in race['results']:
            if driver['laps'] < laps:
                continue
            else:
                if driver['driverName'] in driver_results:
                    driver_results[driver['driverName']]['avgDiffTrackType'].append(driver['finish'] - driver['start'])
                    driver_results[driver['driverName']]['avgDriverRatingType'].append(driver['rating'])
                    driver_results[driver['driverName']]['avgFinishTrackType'].append(driver['finish'])

    for driver in driver_results:
        driver_results[driver]['typeRaces'] = len(driver_results[driver]['avgFinishTrackType'])
        if driver_results[driver]['avgDiffTrackType'] != []:
            driver_results[driver]['avgDiffTrackType'] = sum(driver_results[driver]['avgDiffTrackType']) / len(driver_results[driver]['avgDiffTrackType'])
            driver_results[driver]['avgDriverRatingType'] = sum(driver_results[driver]['avgDriverRatingType']) / len(driver_results[driver]['avgDriverRatingType'])
            driver_results[driver]['avgFinishTrackType'] = sum(driver_results[driver]['avgFinishTrackType']) / len(driver_results[driver]['avgFinishTrackType'])

    for i in range(len(race_docs['results'])):
        for d in driver_results:
            if race_docs['results'][i]['driverName'] == d:
                race_docs['results'][i]['avgDiffTrackType3yrType'] = driver_results[d]['avgDiffTrackType']
                race_docs['results'][i]['avgTrackTypeDriverRating3yr'] = driver_results[d]['avgDriverRatingType']
                race_docs['results'][i]['avgFinishTrackType3yr'] = driver_results[d]['avgFinishTrackType']
                race_docs['results'][i]['typeRaces'] = driver_results[d]['typeRaces']

    # print(race_docs['results'][0])

    filter = {"track": race_docs['track'], "date": race_docs['date']}
    races_collection.update_one(filter, {"$set": {"results": race_docs['results']}})


