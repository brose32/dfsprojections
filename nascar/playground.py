import pymongo

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                             tls=True,
                             tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
db = client.nascar
races_collection = db.races

races = races_collection.find()

for race in races:
    total_laps = race['laps']
    results_updated = race['results']
    for i in range(len(race['results'])):
        lapsLedPercentage = race['results'][i]['lapsLed'] / total_laps
        results_updated[i]['lapsLedPercentage'] = lapsLedPercentage
    filter = {"date": race['date']}
    races_collection.update_one(filter, {"$set": { "results": results_updated}})


