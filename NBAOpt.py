from pulp import *
from NBAsetup import NBAsetup


class NBAOpt(NBAsetup):
    def __init__(self):
        self.SALARYCAP = 60000
        super().__init__()


    def lineupgen(self):
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
        #for i in range(0, self.num_teams):
        #    prob += (pulp.lpSum(self.player_teams[k][i] * player_lineup[k] for k in range(self.num_players)) <= 4*used_team[i])
        #prob += (pulp.lpSum(self.player_teams[i]*player_lineup[i] for i in range(self.num_teams)) <= 4)

        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)


        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'PROJ']*player_lineup[i] for i in range(self.num_players)))
        #prob.solve(pulp.CPLEX_PY(msg=0))
        prob.solve()

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
        a_lineup = ['', '', '', '', '', '', '', '', '', '']
        for num, player in enumerate(lineup):

            if player > 0.9 and player < 1.1:

                if self.positions['PG'][num] == 1:
                    if a_lineup[0] == "":
                        a_lineup[0] = self.players_df.loc[num, 'NAME']
                    elif a_lineup[1] == "":
                        a_lineup[1] = self.players_df.loc[num, 'NAME']
                elif self.positions['SG'][num] == 1:
                    if a_lineup[2] == "":
                        a_lineup[2] = self.players_df.loc[num, 'NAME']
                    elif a_lineup[3] == "":
                        a_lineup[3] = self.players_df.loc[num, 'NAME']
                elif self.positions['SF'][num] == 1:
                    if a_lineup[4] == '':
                        a_lineup[4] = self.players_df.loc[num, 'NAME']
                    elif a_lineup[5] == '':
                        a_lineup[5] = self.players_df.loc[num, 'NAME']
                elif self.positions['PF'][num] == 1:
                    if a_lineup[6] == '':
                        a_lineup[6] = self.players_df.loc[num, 'NAME']
                    elif a_lineup[7] == '':
                        a_lineup[7] = self.players_df.loc[num, 'NAME']
                elif self.positions['C'][num] == 1:
                    if a_lineup[8] == '':
                        a_lineup[8] = self.players_df.loc[num, 'NAME']
                total_proj += self.players_df.loc[num, 'PROJ']
                a_lineup[9] = total_proj
        return a_lineup