import pandas as pd
from sklearn import linear_model
import pymongo
from datetime import datetime
import numpy as np

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                             tls=True,
                             tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
db = client.nascar
races_collection = db.races

track = "Richmond"

track_races = races_collection.find({"date": {"$gte": datetime(2013, 1, 1)}, "date": {"$lte": datetime(2024, 8, 1)}, "track": track})

race_dfs = [pd.DataFrame.from_dict(race['results']) for race in track_races]
races_df = pd.concat(race_dfs).reset_index(drop=True)
races_df.drop(races_df[((races_df.trackRaces < 3) & (races_df.typeRaces < 6)) | (races_df.completeRace == False)].index, inplace=True)
races_df.dropna(inplace=True)

x = races_df[['start', 'avgDiffTrack3yr', 'avgTrackDriverRating3yr', 'avgFinishTrack3yr', 'avgDiffTrackType3yrType', 'avgTrackTypeDriverRating3yr', 'avgFinishTrackType3yr']].values

finish_y = races_df['finish'].to_numpy()
print(len(x))
for idx, val in enumerate(x):
    for i in val:
        if type(i) == list:
            print(idx)
reg = linear_model.LinearRegression()
reg.fit(x, finish_y)
print('start', 'avgDiffTrack3yr', 'avgTrackDriverRating3yr', 'avgFinishTrack3yr', 'avgDiffTrackType3yrType', 'avgTrackTypeDriverRating3yr', 'avgFinishTrackType3yr')
print(reg.coef_)
print(reg.score(x, finish_y))
print(reg.intercept_)

print('laps led')
laps_led_y = races_df['lapsLedPercentage'].to_numpy()

laps_reg = linear_model.LinearRegression()
laps_reg.fit(x, laps_led_y)
print('start', 'avgDiffTrack3yr', 'avgTrackDriverRating3yr', 'avgFinishTrack3yr', 'avgDiffTrackType3yrType', 'avgTrackTypeDriverRating3yr', 'avgFinishTrackType3yr')
print(laps_reg.coef_)
print(laps_reg.score(x, laps_led_y))
print(laps_reg.intercept_)



