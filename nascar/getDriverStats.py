import pymongo
from datetime import datetime

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                             tls=True,
                             tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
db = client.nascar
races_collection = db.races

name = "Josh Berry"
track = "Richmond"
stats = {
    "avgDiffTrack": [],
    "avgFinishTrack": [],
    "avgDriverRatingTrack": [],
    "avgDiffType": [],
    "avgFinishType": [],
    "avgDriverRatingType": []
}
track_races = races_collection.find({"track": track})
track_type = track_races[0]['type']

for race in track_races:
    for driver in race['results']:
        if driver['driverName'] == name:
            stats["avgDiffTrack"].append(driver['finish'] - driver['start'])
            stats["avgFinishTrack"].append(driver['finish'])
            stats["avgDriverRatingTrack"].append(driver['rating'])

stats["avgDiffTrack"] = sum(stats["avgDiffTrack"])/len(stats["avgDiffTrack"])
stats["avgFinishTrack"] = sum(stats["avgFinishTrack"])/len(stats["avgFinishTrack"])
stats["avgDriverRatingTrack"] = sum(stats["avgDriverRatingTrack"])/len(stats["avgDriverRatingTrack"])

type_races = races_collection.find({"date": {"$gte": datetime(datetime.now().year - 3, 1, 1)}, "type": track_type, "track": {"$ne": track}})

for race in type_races:
    for driver in race['results']:
        if driver['driverName'] == name:
            stats["avgDiffType"].append(driver['finish'] - driver['start'])
            stats["avgFinishType"].append(driver['finish'])
            stats["avgDriverRatingType"].append(driver['rating'])

stats["avgDiffType"] = sum(stats["avgDiffType"])/len(stats["avgDiffType"])
stats["avgFinishType"] = sum(stats["avgFinishType"])/len(stats["avgFinishType"])
stats["avgDriverRatingType"] = sum(stats["avgDriverRatingType"])/len(stats["avgDriverRatingType"])

print(stats)


