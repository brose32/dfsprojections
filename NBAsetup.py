import csv
import datetime
import json
import random
import re

import openpyxl
import pandas as pd
from pulp import *


class NBAsetup:

    def __init__(self):
        #change document file location here
        wb = openpyxl.load_workbook('C:\\Users\\brose32\\Documents\\nbaproj10212021.xlsx', data_only=True)
        sh = wb['PROJECTIONS']
        with open('C:\\Users\\brose32\\Documents\\nbaFDprojections.csv', 'w+', newline="") as f:
            c = csv.writer(f)
            for r in sh.rows:
                row_data = []
                for cell in r:
                    row_data.append(cell.value)
                positions = row_data[2]
                positions_list = positions.split("/")
                for pos in positions_list:
                    row_data[2] = pos
                    c.writerow(row_data)
        self.players_df = self.loadinput('C:\\Users\\brose32\\Documents\\nbaFDprojections.csv')
        self.num_players = len(self.players_df.index)
        self.player_teams = {}
        self.opp_teams = []
        self.num_teams = None
        self.num_opponents = None
        self.positions = {'PG': [], 'SG': [], 'SF': [], 'PF': [], 'C': []}
        self.player_names = {}
        self.started = []
        self.randomness = 10

    def loadinput(self, filename):
        try:
            data = pd.read_csv(filename)
        except IOError:
            sys.exit(0)
        return data

    def create_indicators(self):
        teams = list(set(self.players_df['TEAM'].values))
        self.num_teams = len(teams)
        opps = list(set(self.players_df['OPP'].values))
        self.num_opponents = len(opps)

        #position indicators
        for pos in self.players_df.loc[:, 'POS']:
            for key in self.positions:
                self.positions[key].append(1 if key in pos else 0)

        #teams
        for team in teams:
            self.player_teams[team] = []
        for player_team in self.players_df.loc[:, 'TEAM']:
            for team in teams:
                if player_team == team:
                    self.player_teams[team].append(1)
                else:
                    self.player_teams[team].append(0)
           # self.player_teams[player_team].append(1 if player_team == team else 0 for team in teams)
        #oops
        for player_opps in self.players_df.loc[:, 'OPP']:
            self.opp_teams.append(1 if player_opps == oppo else 0 for oppo in opps)

        #names

        for player in self.players_df.loc[:, 'NAME']:
            self.player_names[player] = []
            for name in self.players_df.loc[:,'NAME']:
                if player == name:
                    self.player_names[player].append(1)
                else:
                    self.player_names[player].append(0)

    def addTimeIndicator(self):
        current_time = datetime.datetime.now()
        for tip in self.players_df.loc[:,'TIME']:
            #separating hr and minutes
            tipoffhr = float(re.search(r'([^:]+)', tip).group(0))
            tipoffmin = float(re.search(r'(?<=:).*', tip).group(0)[:2]) / 60
            if current_time.hour + (current_time.minute / 60) < (tipoffhr + tipoffmin + 12):
                self.started.append(0)
            else:
                self.started.append(1)
    #    print(self.started)

    def getLockedPlayers(self, lineup):
        current_time = datetime.datetime.now()
        locked = []
        for player in lineup:
            player_row = self.players_df.loc[self.players_df['NAME'] == player]
            tip_json = json.loads(player_row.to_json())
            s = tip_json.get('TIME').values()
            tip = [x for x in s][0]
            tipoffhr = float(re.search(r'([^:]+)', tip).group(0))
            tipoffmin = float(re.search(r'(?<=:).*', tip).group(0)[:2]) / 60
            if tipoffhr + tipoffmin + 12 < current_time.hour + (current_time.minute / 60):
                locked.append(player)
        return locked





    def addRandomness(self):
        for i in range(len(self.players_df)):
            rand = random.randint(100 - self.randomness, 100 + self.randomness)
            og = self.players_df.loc[i,'PROJ']
            randproj = og * (rand/100)
            self.players_df.at[i, 'PROJ'] = randproj

