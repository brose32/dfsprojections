import json
import sys
import openpyxl
import csv
import pandas as pd
import re
fpath = "C:\\Users\\brose32\\Downloads\\" + sys.argv[2]

df = pd.read_csv(fpath, usecols=["Id", "Nickname", "Position", "Salary", "Game", "Team", "Opponent", "Injury Indicator", "Probable Pitcher"])
fanduel_pitchers = df[(df["Probable Pitcher"] == "Yes")].reset_index(drop=True)
fanduel_pitchers = fanduel_pitchers.drop(columns="Injury Indicator")
fanduel_hitters = df[(df["Position"] != "P") & (df["Injury Indicator"] != "IL")].reset_index(drop=True)
projfpath = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
teamHitterRating = pd.read_excel(projfpath, sheet_name="TeamHitRating")
ballParkFactor_df = pd.read_excel(projfpath, sheet_name="PARK FACTORS")
last14_pitcher_stats_df = pd.read_excel(projfpath, sheet_name="PITCHER LAST 14")
last3_season_pitcher_stats_df = pd.read_excel(projfpath, sheet_name="PITCHER L3 SEASON")
probable_pitcher_df = pd.read_excel(projfpath, sheet_name="PITCHER PROBS")
last14_hitter_stats = pd.read_excel(projfpath, sheet_name="HITTER LAST 14")
lhp_splits_df = pd.read_excel(projfpath, sheet_name="LHP 3YR SPLITS")
rhp_splits_df = pd.read_excel(projfpath, sheet_name="RHP 3YR SPLITS")
pitcherRating_df = pd.read_excel(projfpath, sheet_name="PITCHER RATING")
bullpenFactor_df = pd.read_excel(projfpath, sheet_name="BULLPEN RATING")

with open('hitter_bats.json') as f:
    hitter_bats = json.load(f)

for i in range(len(fanduel_pitchers)):

    pitcher_opponent = fanduel_pitchers.loc[i,"Opponent"]
    home_team = re.findall(r'@([a-zA-Z]+)', fanduel_pitchers.loc[i, "Game"])[0]
    fanduel_pitchers.loc[i,"Opp Rating"] = teamHitterRating[teamHitterRating["TEAM"] == pitcher_opponent]["OVR"].values[0]
    fanduel_pitchers.loc[i, "Park Factor"] = 1 + (1 - ballParkFactor_df[ballParkFactor_df["TEAM"] == home_team]["pFACT B"].values[0])
    l14_stats = last14_pitcher_stats_df[last14_pitcher_stats_df["NAME"] == fanduel_pitchers.loc[i,"Nickname"]]["LAST 14 FD AVG"].values
    l14_ip = last14_pitcher_stats_df[last14_pitcher_stats_df["NAME"] == fanduel_pitchers.loc[i, "Nickname"]]["IP/G"].values
    l3sea_stats = last3_season_pitcher_stats_df[last3_season_pitcher_stats_df["NAME"] == fanduel_pitchers.loc[i, "Nickname"]]["PITCHER L3 SEASON"].values
    if len(l14_stats) > 0 and len(l3sea_stats) > 0:
        fanduel_pitchers.loc[i, "Last 14"] = l14_stats[0]
        fanduel_pitchers.loc[i, "Last 3 Sea"] = l3sea_stats[0]
        fanduel_pitchers.loc[i, "IP"] = l14_ip[0]
    elif len(l14_stats) == 0:
        if len(l3sea_stats) > 0:
            fanduel_pitchers.loc[i, "Last 14"] = l3sea_stats[0]
            fanduel_pitchers.loc[i, "Last 3 Sea"] = l3sea_stats[0]
            fanduel_pitchers.loc[i, "IP"] = 5
        else:
            fanduel_pitchers.loc[i, "Last 14"] = 3
            fanduel_pitchers.loc[i, "Last 3 Sea"] = 3
            fanduel_pitchers.loc[i, "IP"] = 5
    elif len(l3sea_stats) == 0:
        fanduel_pitchers.loc[i, "Last 14"] = l14_stats[0]
        fanduel_pitchers.loc[i, "Last 3 Sea"] = l14_stats[0]
        fanduel_pitchers.loc[i, "IP"] = l14_ip[0]
    else:
        fanduel_pitchers.loc[i, "Last 14"] = 3
        fanduel_pitchers.loc[i, "Last 3 Sea"] = 3
        fanduel_pitchers.loc[i, "IP"] = 5

    '''fanduel_pitchers.loc[i, "FD PROJ"] = ((fanduel_pitchers.loc[i, "Last 14"] * .6) + (fanduel_pitchers.loc[i,"Last 3 Sea"] *.4))\
                                         * fanduel_pitchers.loc[i, "Park Factor"] * fanduel_pitchers.loc[i, "Opp Rating"]'''
    row_num = str(i+2)
    fanduel_pitchers.loc[i, "FD PROJ"] = '=((K' + row_num + '*.6)+(L' + row_num + '*.4))*M' + row_num + '*J' + row_num + '*I' + row_num
    fanduel_pitchers.loc[i, "FD VAL"] = '=N' + row_num + '/(D' + row_num + '/1000)'
#fanduel_pitchers.to_excel("C:\\Users\\brose32\\Documents\\mlbFDprojections.xlsx", sheet_name="PROJECTIONS")
for i in range(len(fanduel_hitters)):
    fanduel_hitters.loc[i, "Probable Pitcher"] = probable_pitcher_df[probable_pitcher_df["TEAM"] == fanduel_hitters.loc[i,"Opponent"]]["NAME"].values[-1]
    opp_pitcher_throws = probable_pitcher_df[probable_pitcher_df["TEAM"] == fanduel_hitters.loc[i,"Opponent"]]["THROWS"].values[-1]
    home_team = re.findall(r'@([a-zA-Z]+)', fanduel_hitters.loc[i, "Game"])[0]
    p_rat = pitcherRating_df[pitcherRating_df["NAME"] == fanduel_hitters.loc[i, "Probable Pitcher"]]["RATING"].values
    if len(p_rat) == 0:
        fanduel_hitters.loc[i, "Opp P Rating"] = 1
    else:
        fanduel_hitters.loc[i, "Opp P Rating"] = p_rat[0]
    bats = hitter_bats[fanduel_hitters.loc[i, "Nickname"]]
    if bats == "L":
        fanduel_hitters.loc[i, "Park Factor"] = ballParkFactor_df[ballParkFactor_df["TEAM"] == home_team]["pFACT L"].values[0]
    elif bats == "R":
        fanduel_hitters.loc[i, "Park Factor"] = ballParkFactor_df[ballParkFactor_df["TEAM"] == home_team]["pFACT R"].values[0]
    else:
        fanduel_hitters.loc[i, "Park Factor"] = ballParkFactor_df[ballParkFactor_df["TEAM"] == home_team]["pFACT B"].values[0]
    fanduel_hitters.loc[i, "Bullpen Rating"] = bullpenFactor_df[bullpenFactor_df["TEAM"] == fanduel_hitters.loc[i, "Opponent"]]["FD RATING"].values[0]
    #print(fanduel_hitters.loc[i, "Nickname"])
    if opp_pitcher_throws == "LHP":
        split_stat = lhp_splits_df[lhp_splits_df["NAME"] == fanduel_hitters.loc[i, "Nickname"]]["FDproj/PA"].values
    else:
        split_stat = rhp_splits_df[rhp_splits_df["NAME"] == fanduel_hitters.loc[i, "Nickname"]]["FDproj/PA"].values

    l14_stat = last14_hitter_stats[last14_hitter_stats["NAME"] == fanduel_hitters.loc[i, "Nickname"]]["FDproj/PA"].values
    pa_g = last14_hitter_stats[last14_hitter_stats["NAME"] == fanduel_hitters.loc[i, "Nickname"]]["PA/G"].values
    if len(split_stat) > 0:
        fanduel_hitters.loc[i, "3 Yr Split"] = split_stat
        if len(l14_stat) > 0:
            fanduel_hitters.loc[i, "L14 Days"] = l14_stat
            fanduel_hitters.loc[i, "PA/G"] = pa_g
        else:
            fanduel_hitters.loc[i, "L14 Days"] = split_stat
            fanduel_hitters.loc[i, "PA/G"] = 4
    elif len(l14_stat) > 0:
        fanduel_hitters.loc[i, "3 Yr Split"] = l14_stat
        fanduel_hitters.loc[i, "L14 Days"] = l14_stat
        fanduel_hitters.loc[i, "PA/G"] = pa_g
    else:
        fanduel_hitters.loc[i, "3 Yr Split"] = 0
        fanduel_hitters.loc[i, "L14 Days"] = 0
        fanduel_hitters.loc[i, "PA/G"] = 3

    '''fanduel_hitters.loc[i, "FD PROJ"] = (((fanduel_hitters.loc[i, "L14 Days"] * .6) + (fanduel_hitters.loc[i, "3 Yr Split"] * .4))
                                         * fanduel_hitters.loc[i, "Park Factor"] * fanduel_hitters.loc[i, "Opp P Rating"]
                                         * (fanduel_hitters.loc[i, "PA/G"] - 1)) + (fanduel_hitters.loc[i, "L14 Days"]
                                         * fanduel_hitters.loc[i, "Park Factor"] * fanduel_hitters.loc[i, "Bullpen Rating"])
    fanduel_hitters.loc[i, "FD VAL"] = fanduel_hitters.loc[i, "FD PROJ"] / (fanduel_hitters.loc[i, "Salary"] / 1000)'''
    row_num = str(i+2)
    fanduel_hitters.loc[i, "FD PROJ"] = '=(((M' + row_num + '*.6)+(L' + row_num + '*.4))*J' + row_num + '*I' + row_num + \
                                    '*(N' + row_num + '-1))+(M' + row_num + '*J' + row_num + '*K' + row_num + ')'
    fanduel_hitters.loc[i, "FD VAL"] = '=O' + row_num + '/(D' + row_num + '/1000)'

fanduel_hitters = fanduel_hitters.drop(columns=["Injury Indicator"])
#print(fanduel_hitters.head())

writer = pd.ExcelWriter('C:\\Users\\brose32\\Documents\\07012021MLBFDproj.xlsx', engine='xlsxwriter')
fanduel_pitchers.to_excel(writer, sheet_name="FD PITCHERS", index=False)
fanduel_hitters.to_excel(writer, sheet_name="FD HITTERS", index=False)
writer.save()