import csv
import random

import pandas as pd
import sys
from pulp import *


class NFLSetup:

    def __init__(self):
        self.players_df = self.loadinput('C:\\Users\\brose32\\Documents\\NFLFDproj.csv')
        #remove players with low projections
        self.players_df = self.players_df[(self.players_df["FD PROJ"] > 2)].reset_index(drop=True)
        self.num_players = len(self.players_df.index)
        self.player_teams = []
        self.player_names = {}
        self.opp_teams = []
        self.num_teams = None
        self.num_opponents = None
        self.randomness = 10
        self.positions = {'QB':[], 'RB':[], 'WR':[], 'TE':[], 'D':[]}

    def loadinput(self, filename):
        try:
            data = pd.read_csv(filename)
        except IOError:
            sys.exit(0)
        return data

    def create_indicators(self):
        teams = list(set(self.players_df['Team'].values))
        self.num_teams = len(teams)
        opps = list(set(self.players_df['Opponent'].values))
        self.num_opponents = len(opps)

        #position indicators
        for pos in self.players_df.loc[:, 'Position']:
            for key in self.positions:
                self.positions[key].append(1 if key in pos else 0)

         #teams
        for player_team in self.players_df.loc[:, 'Team']:
            self.player_teams.append(1 if player_team == team else 0 for team in teams)

        #oops
        for player_opps in self.players_df.loc[:, 'Opponent']:
            self.opp_teams.append(1 if player_opps == opp else 0 for opp in opps)

        # names
        for player in self.players_df.loc[:, 'Nickname']:
            self.player_names[player] = []
            for name in self.players_df.loc[:, 'Nickname']:
                if player == name:
                    self.player_names[player].append(1)
                else:
                    self.player_names[player].append(0)



    def addRandomness(self):
        for i in range(self.num_players):
            #rand = random.randint(100 - self.randomness, 100 + self.randomness)
            rand = random.uniform(-self.randomness, self.randomness)
            self.players_df.loc[i, "Rand Proj"] = self.players_df.loc[i, "FD PROJ"] + (self.players_df.loc[i, "FD PROJ"] * (rand/100))
