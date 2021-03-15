import re

from pulp import *
from NBAsetup import NBAsetup


class NBAOpt(NBAsetup):
    def __init__(self):
        self.SALARYCAP = 60000
        self.overlap = 6
        self.max_per_team = 4
        super().__init__()


    def lineupgen(self, lineups):
        prob = pulp.LpProblem('NBA', LpMaximize)
        player_lineup = [pulp.LpVariable("player_{}".format(i+1), cat="Binary") for i in range(self.num_players)]
        #player constraints
        prob += (pulp.lpSum(player_lineup[i] for i in range(self.num_players)) == 9)
        prob += (pulp.lpSum(self.positions['PG'][i]*player_lineup[i] for i in range(self.num_players)) == 2)
        prob += (pulp.lpSum(self.positions['SG'][i]*player_lineup[i] for i in range(self.num_players)) == 2)
        prob += (pulp.lpSum(self.positions['SF'][i]*player_lineup[i] for i in range(self.num_players)) == 2)
        prob += (pulp.lpSum(self.positions['PF'][i]*player_lineup[i] for i in range(self.num_players)) == 2)
        prob += (pulp.lpSum(self.positions['C'][i]*player_lineup[i] for i in range(self.num_players)) == 1)

        #team constraint
        used_team = [pulp.LpVariable("u{}".format(i + 1), cat="Binary") for i in range(self.num_teams)]
        prob += (pulp.lpSum(used_team[i] for i in range(self.num_teams)) >= 3)

        # max player per team
        for team in self.player_teams:
            prob += (pulp.lpSum(self.player_teams[team][i]*player_lineup[i] for i in range(self.num_players)) <= self.max_per_team)

        #player grouping rules samples are commented out
        #how to lock in a player
        #prob += ((pulp.lpSum(self.player_names["Stanley Johnson"][i]*player_lineup[i] for i in range(self.num_players))) == 1)

        #if player A no player B... player N and vice versa
        #prob += ((pulp.lpSum(self.player_names["Jimmy Butler"][i]*player_lineup[i] +
        #                     self.player_names["Brandon Ingram"][i] * player_lineup[i]  for i in range(self.num_players))
        #          <= 1))

        #max exposure checker
        #all players under a certain %
        # doesnt work yet
        #for i in range(len(lineups)):
         #   prob += (pulp.lpSum(lineups[i][k] + player_lineup[k] for k in range(self.num_players)) <= 100)


        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)
        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) >= 59400)

        #max num players from another lineup = 6
        for i in range(len(lineups)):
            prob += (pulp.lpSum(lineups[i][k]*player_lineup[k] for k in range(self.num_players)) <= self.overlap)

        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'PROJ']*player_lineup[i] for i in range(self.num_players)))
        prob.solve(CPLEX_PY(msg=0))
        lineup_copy = []

        for i in range(self.num_players):
            if player_lineup[i].varValue >= 0.9 and player_lineup[i].varValue <= 1.1:
                #print(player_lineup[i])
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)

        #print(prob)
        return lineup_copy

    def printlineup(self, lineup):
        total_proj = 0
        total_sal = 0
        a_lineup = ['', '', '', '', '', '', '', '', '', '', '']
        for num, player in enumerate(lineup):

            if player > 0.9 and player < 1.1:

                if self.positions['PG'][num] == 1:
                    if a_lineup[0] == "":
                        a_lineup[0] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                    elif a_lineup[1] == "":
                        a_lineup[1] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif self.positions['SG'][num] == 1:
                    if a_lineup[2] == "":
                        a_lineup[2] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                    elif a_lineup[3] == "":
                        a_lineup[3] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif self.positions['SF'][num] == 1:
                    if a_lineup[4] == '':
                        a_lineup[4] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                    elif a_lineup[5] == '':
                        a_lineup[5] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif self.positions['PF'][num] == 1:
                    if a_lineup[6] == '':
                        a_lineup[6] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                    elif a_lineup[7] == '':
                        a_lineup[7] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif self.positions['C'][num] == 1:
                    if a_lineup[8] == '':
                        a_lineup[8] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                total_proj += self.players_df.loc[num, 'PROJ']
                total_sal += self.players_df.loc[num, 'SAL']
                a_lineup[9] = total_proj
                a_lineup[10] = total_sal
        return a_lineup


    def getLineupsData(self, lineups):
        players = {}
        for lineup in lineups:
            for i in range(len(lineup)-2):
                if not players.__contains__(lineup[i]) and not lineup[i].isnumeric():
                    players[lineup[i]] = 1
                else:
                    players[lineup[i]] += 1
        for player in players:
            num = player.index(':')
            per = str((players[player]/len(lineups)* 100)) + '%'
            print(player[num+1:], players[player], per)
        print('Total players used: ', len(players))



