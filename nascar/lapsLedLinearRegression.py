import pandas as pd
import numpy as np
from sklearn import linear_model, model_selection
import pymongo

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                             tls=True,
                             tlsCertificateKeyFile='C:\\Users\\brose32\\Documents\\mongo\\X509-cert-6872311124111469588.pem')
db = client.nascar
races_collection = db.races




