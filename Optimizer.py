import csv
import pandas as pd
import sys
from pulp import *


class Optimizer:

    def __init__(self):
        self.players_df = self.loadinput('C:\\Users\\brose32\\Documents\\nfltest.csv')
        self.num_players = len(self.players_df.index)
        self.player_teams = []
        self.opp_teams = []
        self.num_teams = None
        self.num_opponents = None
        self.positions = {'QB':[], 'RB':[], 'WR':[], 'TE':[], 'DST':[]}

    def loadinput(self, filename):
        try:
            data = pd.read_csv(filename)
        except IOError:
            sys.exit(0)
        return data

    def create_indicators(self):
        teams = list(set(self.players_df['team'].values))
        self.num_teams = len(teams)
        opps = list(set(self.players_df['opp'].values))
        self.num_opponents = len(opps)

        #position indicators
        for pos in self.players_df.loc[:, 'pos']:
            for key in self.positions:
                self.positions[key].append(1 if key in pos else 0)

         #teams
        for player_team in self.players_df.loc[:, 'team']:
            self.player_teams.append(1 if player_team == team else 0 for team in teams)

        #oops
        for player_opps in self.players_df.loc[:, 'opp']:
            self.opp_teams.append(1 if player_opps == opp else 0 for opp in opps)



