import csv

import openpyxl
import pandas as pd
import sys
from pulp import *


class NBAsetup:

    def __init__(self):
        #change document file location here
        #pd.read_excel('C:\\Users\\brose32\\Documents\\nbaproj01302021.xlsx', sheet_name='PROJECTIONS'
        #             , skiprows=1).to_csv('C:\\Users\\brose32\\Documents\\nbaproj01302021.csv', index=False)
    # cannot have excel projections open and be able to read it into CSV makes no sense but whatever
        wb = openpyxl.load_workbook('C:\\Users\\brose32\\Documents\\nbaproj03012021.xlsx', data_only=True)
        sh = wb['PROJECTIONS']
        with open('C:\\Users\\brose32\\Documents\\nbaFD03012021.csv', 'w', newline="") as f:
            c = csv.writer(f)
            for r in sh.rows:
                c.writerow([cell.value for cell in r])
        self.players_df = self.loadinput('C:\\Users\\brose32\\Documents\\nbaFD03012021.csv')
        self.num_players = len(self.players_df.index)
        self.player_teams = []
        self.opp_teams = []
        self.num_teams = None
        self.num_opponents = None
        self.positions = {'PG':[], 'SG':[], 'SF':[], 'PF':[], 'C':[]}

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
        for player_team in self.players_df.loc[:, 'TEAM']:
            self.player_teams.append(1 if player_team == team else 0 for team in teams)

        #oops
        for player_opps in self.players_df.loc[:, 'OPP']:
            self.opp_teams.append(1 if player_opps == oppo else 0 for oppo in opps)


