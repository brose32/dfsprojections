import csv
import datetime
import json
import random
import re
import numpy as np
import openpyxl
import pandas as pd
from pulp import *


class nascarFDSetup:

    def __init__(self):
        #change document file location here
        wb = openpyxl.load_workbook('C:\\Users\\brose32\\Documents\\nascarfdproj07242024.xlsx', data_only=True)
        sh = wb['PROJECTIONS']
        with open('C:\\Users\\brose32\\Documents\\nascarFDprojections.csv', 'w+', newline="") as f:
            c = csv.writer(f)
            for r in sh.rows:
                row_data = []
                for cell in r:
                    row_data.append(cell.value)
                c.writerow(row_data)
        self.players_df = self.loadinput('C:\\Users\\brose32\\Documents\\nascarFDprojections.csv')
        #sort by ascending time and salary
        self.num_players = len(self.players_df.index)
        print(self.num_players)
        self.player_names = {}
        self.randomness = 10
        self.normal_randomness = 0.1
        self.model = None
        self.overlap_lineups = []

    def loadinput(self, filename):
        try:
            data = pd.read_csv(filename)
        except IOError:
            sys.exit(0)
        return data

    def create_indicators(self):
        for player in self.players_df.loc[:, 'NAME']:
            self.player_names[player] = []
            for name in self.players_df.loc[:,'NAME']:
                if player == name:
                    self.player_names[player].append(1)
                else:
                    self.player_names[player].append(0)


    def addRandomness(self):
        for i in range(self.num_players):
            #rand = random.randint(100 - self.randomness, 100 + self.randomness)
            rand = random.uniform(-self.randomness, self.randomness)
            self.players_df.loc[i, "Rand PROJ"] = self.players_df.loc[i, "PROJ"] + (self.players_df.loc[i, "PROJ"] * (rand/100))

    def addNormalRandomness(self):
        rand_proj = []
        for proj in self.players_df["PROJ"]:
            rand_proj.append(np.random.normal(proj, proj * self.normal_randomness))
        self.players_df["Rand PROJ"] = rand_proj


