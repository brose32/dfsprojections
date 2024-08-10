import pymongo
from datetime import datetime
import pandas as pd

# uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
# client = pymongo.MongoClient(uri,
#                              tls=True,
#                              tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
# db = client.nascar
# races_collection = db.races
#
# race_doc = races_collection.find({"date": {"$gte": datetime(2024, 7, 14)}})[0]
#
# df = pd.DataFrame.from_dict(race_doc['results'])
#
# predict_position = []
#
# for index, row in df.iterrows():
#     predict_position.append((df.loc[index, 'start'] * 0.17683916) + (df.loc[index, 'avgDiffTrack3yr'] * -0.02883035) +
#                             (df.loc[index, 'avgTrackDriverRating3yr'] * -0.07021222) + (df.loc[index, 'avgFinishTrack3yr'] * 0.10316635) +
#                             (df.loc[index, 'avgDiffTrackType3yrType'] * 0.04463035) + (df.loc[index, 'avgTrackTypeDriverRating3yr'] * -0.12950424) + (df.loc[index, 'avgFinishTrackType3yr'] * -0.00846429) + 26.089638400612174)
#
# df['predictPosition'] = predict_position
#
# df.dropna(inplace=True)
# print(len(df))




