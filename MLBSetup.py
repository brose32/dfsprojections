import csv
import datetime
import json
import random
import re
import sys
from copy import deepcopy

import openpyxl
import pandas as pd

class MLBSetup:

    def __init__(self):
        wb = openpyxl.load_workbook('C:\\Users\\brose32\\Documents\\mlbopttest.xlsx', data_only=True)
        sh = wb['PROJECTIONS']
        with open('C:\\Users\\brose32\\Documents\\mlblineups.csv', 'w+', newline="") as f:
            c = csv.writer(f)
            for r in sh.rows:
                row_data = []
                for cell in r:
                    row_data.append(cell.value)
                positions = row_data[1]
                firstpos = row_data[1][:2]
                row_data[1] = firstpos
                c.writerow(row_data)
                if positions.find("/") != -1:
                    secondpos = positions[positions.find("/") + 1:]
                    row_data[1] = secondpos
                    c.writerow(row_data)
        self.players_df = self.loadinput('C:\\Users\\brose32\\Documents\\mlblineups.csv')
        self.num_players = len(self.players_df.index)
        self.player_teams = {}
        self.opp_teams = []
        self.num_teams = None
        self.num_opponents = None
        self.positions = {'P' :[], 'C' :[], '1B' :[], '2B' :[], '3B' :[], 'SS':[], 'OF':[]}
        self.player_names = {}
        self.started = []
        self.randomness = 5

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
        for pos in self.players_df.loc[:, 'PO']:
            for key in self.positions:
                self.positions[key].append(1 if key in pos else 0)

        for team in teams:
            self.player_teams[team] = []
         #teams
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
