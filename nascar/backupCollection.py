import pymongo

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                             tls=True,
                             tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
db = client.nascar
races_collection_src = db.races
races_collection_dest = db.races_results
races_src_docs = races_collection_src.find()
for race_src in races_src_docs:
    races_collection_dest.insert_one(race_src)
