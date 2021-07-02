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
        wb = openpyxl.load_workbook('C:\\Users\\brose32\\Documents\\07012021MLBFDproj.xlsx', data_only=True)
        sh = wb['FD HITTERS']
        with open('C:\\Users\\brose32\\Documents\\mlbhitters.csv', 'w+', newline="") as f:
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
        self.hitters_df = self.loadinput('C:\\Users\\brose32\\Documents\\mlbhitters.csv')
        self.pitchers_df = pd.read_excel('C:\\Users\\brose32\\Documents\\07012021MLBFDproj.xlsx', sheet_name="FD PITCHERS")
        self.num_hitters = len(self.hitters_df.index)
        self.num_pitchers = len(self.pitchers_df)
        self.hitter_teams = {}
        self.pitcher_teams = {}
        self.pitcher_opps = []
        self.hitter_num_teams = None
        self.pitcher_num_teams = None
        self.num_opponents = None
        self.positions = {'C' :[], '1B' :[], '2B' :[], '3B' :[], 'SS':[], 'OF':[]}
        self.hitter_names = {}
        self.started = []
        self.randomness = 5

    def loadinput(self, filename):
        try:
            data = pd.read_csv(filename)
        except IOError:
            sys.exit(0)
        return data

    def create_indicators(self):
        hitter_teams = list(set(self.hitters_df['Team'].values))
        pitcher_teams = list(set(self.pitchers_df['Team'].values))
        self.hitter_num_teams = len(hitter_teams)
        self.pitcher_num_teams = len(pitcher_teams)
        opps = list(set(self.hitters_df['Opponent'].values))
        self.num_opponents = len(opps)

        #position indicators
        for pos in self.hitters_df.loc[:, 'Po']:
            for key in self.positions:
                self.positions[key].append(1 if key in pos else 0)

        for team in hitter_teams:
            self.hitter_teams[team] = []
         #teams
        for player_team in self.hitters_df.loc[:, 'Team']:
            for team in hitter_teams:
                if player_team == team:
                    self.hitter_teams[team].append(1)
                else:
                    self.hitter_teams[team].append(0)
        for team in pitcher_teams:
            self.pitcher_teams[team] = []
         #teams
        for player_team in self.pitchers_df.loc[:, 'Team']:
            for team in pitcher_teams:
                if player_team == team:
                    self.pitcher_teams[team].append(1)
                else:
                    self.pitcher_teams[team].append(0)
           # self.player_teams[player_team].append(1 if player_team == team else 0 for team in teams)
        #oops TODO
        #for player_opps in self.players_df.loc[:, 'OPP']:
        #    self.opp_teams.append(1 if player_opps == oppo else 0 for oppo in opps)
        for player_opp in self.hitters_df.loc[:, "Opponent"]:
            self.pitcher_opps.append([1 if player_opp == team else 0 for team in self.pitchers_df.loc[:, "Team"]])

        #names

        for player in self.hitters_df.loc[:, 'Nickname']:
            self.hitter_names[player] = []
            for name in self.hitters_df.loc[:,'Nickname']:
                if player == name:
                    self.hitter_names[player].append(1)
                else:
                    self.hitter_names[player].append(0)
