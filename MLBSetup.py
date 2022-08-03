import csv
import datetime
import json
import random
import sys
import openpyxl
import pandas as pd
from itertools import combinations

class MLBSetup:

    def __init__(self):
        wb = openpyxl.load_workbook('C:\\Users\\brose32\\Documents\\07032021MLBFDproj.xlsx', data_only=True)
        sh = wb['FD HITTERS']
        with open('C:\\Users\\brose32\\Documents\\mlbhitters.csv', 'w+', newline="") as f:
            c = csv.writer(f)
            for r in sh.rows:
                row_data = []
                for cell in r:
                    row_data.append(cell.value)
                positions = row_data[1]
                positions_list = positions.split("/")
                for pos in positions_list:
                    row_data[1] = pos
                    c.writerow(row_data)
        self.hitters_df = self.loadinput('C:\\Users\\brose32\\Documents\\mlbhitters.csv')
        self.pitchers_df = pd.read_excel('C:\\Users\\brose32\\Documents\\07032021MLBFDproj.xlsx', sheet_name="FD PITCHERS")
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
        self.pitcher_names = {}
        self.stacks = []
        self.secondary_stacks = []
        self.started = []
        self.randomness = 25

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
        for pos in self.hitters_df.loc[:, 'Position']:
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
        #opps
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
        for player in self.pitchers_df.loc[:,'Nickname']:
            self.pitcher_names[player] = []
            for name in self.pitchers_df.loc[:,'Nickname']:
                if player == name:
                    self.pitcher_names[player].append(1)
                else:
                    self.pitcher_names[player].append(0)

        #stacks
        skips = 1
        for index, player in self.hitters_df.iterrows():
            team = player['Team']
            lu_spot = player['ORDER']
            teammates = [lu_spot + i if lu_spot <= 9 else lu_spot + i - 9 for i in range(1, 4 + skips)]
            combos = list(combinations(teammates, 3))
            player_stacks = [(lu_spot,) + combo for combo in combos]
            for stack in player_stacks:
                self.stacks.append([1 if (row['Team'] == team) and (row['ORDER'] in stack) else 0 for index, row in self.hitters_df.iterrows()])

        for index, player in self.hitters_df.iterrows():
            team = player['Team']
            lu_spot = player['ORDER']
            teammates = [lu_spot + i if lu_spot <= 9 else lu_spot + i - 9 for i in range(1, 3 + skips)]
            combos = list(combinations(teammates, 2))
            player_stacks = [(lu_spot,) + combo for combo in combos]
            for stack in player_stacks:
                self.secondary_stacks.append([1 if (row['Team'] == team) and (row['ORDER'] in stack) else 0 for index, row in self.hitters_df.iterrows()])


    def addRandomness(self):
        for i in range(self.num_hitters):
            #rand = random.randint(100 - self.randomness, 100 + self.randomness)
            rand = random.uniform(-self.randomness, self.randomness)
            self.hitters_df.loc[i, "Rand Proj"] = self.hitters_df.loc[i, "FD PROJ"] + (self.hitters_df.loc[i, "FD PROJ"] * (rand/100))
        for i in range(self.num_pitchers):
            rand = random.randint(100 - self.randomness, 100 + self.randomness)
            self.pitchers_df.loc[i, "Rand Proj"] = self.pitchers_df.loc[i, "FD PROJ"] * (rand / 100)
