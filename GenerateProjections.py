import sys

import openpyxl
import csv
#getting positions for players / opponent from fanduel download

fpath = "C:\\Users\\brose32\\Downloads\\" + sys.argv[2]
fdf = open(fpath)
csv_fdf = csv.reader(fdf)

info = []
for row in csv_fdf:

    info.append({'playerName' : row[3], 'SAL': row[7], 'POS': row[1], 'TEAM': row[9], 'OPP': row[10], 'MINs': 0})
#print(info[4]['playerName'])

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
proj_sheet = wb.create_sheet("PROJECTIONS")
#proj_sheet.append(('test', 'dee'))
proj_sheet.append(('NAME', 'SAL', 'POS', 'TEAM', 'OPP', 'DVOA', 'TPPG', 'ImpTOTAL', 'DIFF', 'tPACE', 'oPACE', 'calcPACE',
                   'FDpts/min','MINs', 'PROJ', 'VAL'))
#for i in range(1, len(info)):
#    proj_sheet.append((info[i]['playerName'], float(info[i]['SAL']), info[i]['POS'], info[i]['TEAM']))

#getting dvoa to match with position/opponent
# TEAM, POS, PTS, tOVP

dvoa = wb["TEAMOVP"]
tppg = wb['TEAMPPG']
fdpts = wb['FD PTS_MIN']
lines = wb['VEGAS_LINES']
mins = wb['MINUTES_PROJ']
pace = wb['PACE']
#looping to add all data to main sheet
for player in info:
    player['FDptsmin'] = 0
    if player['TEAM'] == 'SA':
        player['TEAM'] = 'SAS'
    if player['OPP'] == 'SA':
        player['OPP'] = 'SAS'
    if player['TEAM'] == 'NY':
        player['TEAM'] = 'NYK'
    if player['OPP'] == 'NY':
        player['OPP'] = 'NYK'
    if player['TEAM'] == 'GS':
        player['TEAM'] = 'GSW'
    if player['OPP'] == 'GS':
        player['OPP'] = 'GSW'
    if player['TEAM'] == 'NO':
        player['TEAM'] = 'NOR'
    if player['OPP'] == 'NO':
        player['OPP'] = 'NOR'
    if player['TEAM'] == 'PHX':
        player['TEAM'] = 'PHO'
    if player['OPP'] == 'PHX':
        player['OPP'] = 'PHO'
    opponent = player['OPP']
    position = player['POS']

    for row in dvoa:
        if opponent == row[0].value and position == row[1].value:
            player['DVOA'] = row[3].value
    for row in fdpts:
        if player['playerName'] == row[0].value:
            player['FDptsmin'] = row[1].value
            #player['MINs'] = 0

    for row in lines:
        if player['TEAM'] == row[2].value:
            player['ImpTOTAL'] = row[3].value
        elif player['TEAM'] == row[4].value:
            player['ImpTOTAL'] = row[5].value
    for team in tppg:
        if player['TEAM'] == team[0].value:
            player['TPPG'] = team[1].value
    for person in mins:
        if player['playerName'] == person[0].value:
            player['MINs'] = person[1].value
    for team in pace:
        if player['TEAM'] == team[0].value:
            player['tPACE'] = team[1].value
        if player['OPP'] == team[0].value:
            player['oPACE'] = team[1].value
#for i in range(1, len(info)):
#    proj_sheet.append((info[i]['playerName'], info[i]['SAL'], info[i]['POS'], info[i]['TEAM'], info[i]['OPP'],
#                       info[i]['DVOA']))

#print(info)

#adding to sheet

for i in range(1, len(info)):
    print(info[i]['playerName'])
    diff_formula = '=(((H' + str(i + 1) + '-G' + str(i + 1) + ')/100) + 1)'
    # (fd_pts_min * minutes_projected * gameflow rating) * (game total rating * DVOA)

    proj_formula = '=((M' + str(i+1) + '*N' + str(i+1)+ '*L' + str(i+1) +')*(F'+ str(i+1) + '*I' + str(i+1) + '))'
    value_formula = '=(O' + str(i+1) + '/(B' + str(i+1) +'/1000))'
    # ((team pace - avg pace) + (opp pace - avg pace) + avg pace) / team pace
    pace_formula = '=(((J' + str(i+1) + '-PACE!B32)+(K' + str(i+1) + '-PACE!B32)+PACE!B32)/J' + str(i+1) + ')'
    proj_sheet.append((info[i]['playerName'], float(info[i]['SAL']), info[i]['POS'], info[i]['TEAM'], info[i]['OPP'],
                       info[i]['DVOA'], info[i]['TPPG'], info[i]['ImpTOTAL'], diff_formula, info[i]['tPACE'],
                       info[i]['oPACE'], pace_formula, info[i]['FDptsmin'], info[i]['MINs'],
                       proj_formula, value_formula))
#NEED TO CHANGE TO HOME AND AWAY??? currently season avg


wb.save(my_file)

print("proj sheet generated")