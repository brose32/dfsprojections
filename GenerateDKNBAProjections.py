import json
import sys
import openpyxl
import csv
import statistics
import pandas as pd

import pymongo

#getting positions for players / opponent from fanduel download

fpath = "C:\\Users\\brose32\\Downloads\\" + sys.argv[2]
dkf = open(fpath)
csv_dkf = csv.reader(dkf)
next(csv_dkf)
info = []
for row in csv_dkf:
    teams = row[6].split('@')
    teams[1] = teams[1][:3]
    opp = teams[0] if teams[0] != row[7] else teams[1]
    info.append({'ID': row[1], 'playerName' : row[2], 'DKSAL': row[5], 'POS': row[0], 'TEAM': row[7], 'OPP': opp, 'MINs': 0, 'ELG': row[4]})
#print(info[4]['playerName'])

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
proj_sheet = wb.create_sheet("DKPROJECTIONS")
proj_sheet.append(('NAME', 'DKSAL', 'POS', 'TEAM', 'OPP', 'DVOA', 'TPPG', 'ImpTOTAL', 'DIFF', 'tPACE', 'oPACE', 'calcPACE',
                   'DKpts/min','MINs', 'DKPROJ', 'VAL', 'GOAL', 'ID', 'TIME', 'DKOWN'))

uri = "mongodb+srv://dfsprojections.4ay0gcw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = pymongo.MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile="C:\\Users\\brose32\\uploadprojections\\X509-cert-3043484743011169677.pem")
mongo_db = client.nba
proj_collection = mongo_db.dkProjections

#for i in range(1, len(info)):
#    proj_sheet.append((info[i]['playerName'], float(info[i]['SAL']), info[i]['POS'], info[i]['TEAM']))

#getting dvoa to match with position/opponent
# TEAM, POS, PTS, tOVP

dvoa = wb["TEAMOVP"]
tppg = wb['TEAMPPG']
dkpts = wb['DK PTS_MIN']
lines = wb['VEGAS_LINES']
# mins = wb['MINUTES_PROJ']
pace = wb['PACE']
DK_ownership = wb['DKOWNER']
with open('teamAbbrs.json') as f:
    team_abbrs = json.load(f)
#looping to add all data to main sheet
for player in info:
    player['DKptsmin'] = 0
    player['DKOWN'] = 0
    #clean up team abbreviations
    player['TEAM'] = team_abbrs[player['TEAM']]
    player['OPP'] = team_abbrs[player['OPP']]
    opponent = player['OPP']
    position = player['POS'].split("/")
    player['DVOA'] = []
    for row in dvoa:
        for pos in position:
            if opponent == row[0].value and pos == row[1].value:
                player['DVOA'].append(row[3].value)
    player['DVOA'] = statistics.mean(player['DVOA'])
    for row in dkpts:
        if player['playerName'] == row[0].value:
            player['DKptsmin'] = row[1].value
            #player['MINs'] = 0

    for row in lines:
        if player['TEAM'] == row[2].value:
            player['ImpTOTAL'] = row[3].value
            player['TIP'] = row[6].value
        elif player['TEAM'] == row[4].value:
            player['ImpTOTAL'] = row[5].value
            player['TIP'] = row[6].value
    for team in tppg:
        if player['TEAM'] == team[0].value:
            player['TPPG'] = team[1].value
    # for person in mins:
    #     if player['playerName'] == person[0].value:
    #         player['MINs'] = person[1].value
    for team in pace:
        if player['TEAM'] == team[0].value:
            player['tPACE'] = team[1].value
        if player['OPP'] == team[0].value:
            player['oPACE'] = team[1].value

    # doc = db.collection('nbaprojections').document(player['playerName']).get()
    # if doc.exists:
    #     player['MINs'] = doc.to_dict()['mins']
    doc = proj_collection.find_one({"name": player['playerName']})
    if doc != None:
        player['MINs'] = doc['mins']
    for ownership in DK_ownership:
        if player['playerName'] == ownership[0].value:
            player['DKOWN'] = ownership[1].value
#for i in range(1, len(info)):
#    proj_sheet.append((info[i]['playerName'], info[i]['SAL'], info[i]['POS'], info[i]['TEAM'], info[i]['OPP'],
#                       info[i]['DVOA']))

print(info[0])

#adding to sheet
for i in range(0, len(info)):

    #print(info[i]['playerName'])
    diff_formula = '=(((H' + str(i + 2) + '-G' + str(i + 2) + ')/100) + 1)'
    # (dk_pts_min * minutes_projected * gameflow rating) * (game total rating * DVOA)

    proj_formula = '=((M' + str(i+2) + '*N' + str(i+2)+ '*L' + str(i+2) +')*(F'+ str(i+2) + '*I' + str(i+2) + '))'
    value_formula = '=(O' + str(i+2) + '/(B' + str(i+2) +'/1000))'
    # ((team pace - avg pace) + (opp pace - avg pace) + avg pace) / team pace
    pace_formula = '=(((J' + str(i+2) + '-PACE!B32)+(K' + str(i+2) + '-PACE!B32)+PACE!B32)/J' + str(i+2) + ')'
    goal = ((float(info[i]['DKSAL']) / 1000) * 3.5) + 22
    proj_sheet.append((info[i]['playerName'], float(info[i]['DKSAL']), info[i]['ELG'], info[i]['TEAM'], info[i]['OPP'],
                       info[i]['DVOA'], info[i]['TPPG'], info[i]['ImpTOTAL'], diff_formula, info[i]['tPACE'],
                       info[i]['oPACE'], pace_formula, info[i]['DKptsmin'], info[i]['MINs'],
                       proj_formula, value_formula, goal, info[i]['ID'], info[i]['TIP'], info[i]['DKOWN']))
#NEED TO CHANGE TO HOME AND AWAY??? currently season avg

wb.save(my_file)

print("proj sheet generated")