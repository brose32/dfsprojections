from pulp import *
from Optimizer import Optimizer


class NFLOpt(Optimizer):
    def __init__(self):
        self.SALARYCAP = 60000
        super().__init__()


    def lineupgen(self):
        prob = pulp.LpProblem('NFL', LpMaximize)
        player_lineup = [pulp.LpVariable("player_{}".format(i+1), cat="Binary") for i in range(self.num_players)]
        #player constraints
        prob += (pulp.lpSum(player_lineup[i] for i in range(self.num_players)) == 9)
        prob += (pulp.lpSum(self.positions['QB'][i]*player_lineup[i] for i in range(self.num_players)) == 1)
        prob += (2 <= pulp.lpSum(self.positions['RB'][i]*player_lineup[i] for i in range(self.num_players)))
        prob += (pulp.lpSum(self.positions['RB'][i]*player_lineup[i] for i in range(self.num_players)) <= 3)
        prob += (3 <= pulp.lpSum(self.positions['WR'][i]*player_lineup[i] for i in range(self.num_players)))
        prob += (pulp.lpSum(self.positions['WR'][i]*player_lineup[i] for i in range(self.num_players)) <= 4)
        prob += (1 <= pulp.lpSum(self.positions['TE'][i]*player_lineup[i] for i in range(self.num_players)))
        prob += (pulp.lpSum(self.positions['TE'][i]*player_lineup[i] for i in range(self.num_players)) <= 2)
        prob += (pulp.lpSum(self.positions['DST'][i]*player_lineup[i] for i in range(self.num_players)) == 1)

        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'salary']*player_lineup[i] for i in range(self.num_players))
                 <= self.SALARYCAP)


        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'proj']*player_lineup[i] for i in range(self.num_players)))
        #prob.solve(pulp.CPLEX_PY(msg=0))
        prob.solve()

        lineup_copy = []
        for i in range(self.num_players):
            if player_lineup[i].varValue >= 0.9 and player_lineup[i].varValue <= 1.1:
                #print(player_lineup[i])
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)

        return lineup_copy

    def printlineup(self, lineup):
        total_proj = 0
        a_lineup = ['', '', '', '', '', '', '', '', '', '']
        for num, player in enumerate(lineup):

            if player > 0.9 and player < 1.1:
                if self.positions['QB'][num] == 1:
                    if a_lineup[0] == "":
                        a_lineup[0] = self.players_df.loc[num, 'playerName']
                elif self.positions['RB'][num] == 1:
                    if a_lineup[1] == "":
                        a_lineup[1] = self.players_df.loc[num, 'playerName']
                    elif a_lineup[2] == "":
                        a_lineup[2] = self.players_df.loc[num, 'playerName']
                    elif a_lineup[8] == "":
                        a_lineup[8] = self.players_df.loc[num, 'playerName']
                elif self.positions['WR'][num] == 1:
                    if a_lineup[3] == "":
                        a_lineup[3] = self.players_df.loc[num, 'playerName']
                    elif a_lineup[4] == "":
                        a_lineup[4] = self.players_df.loc[num, 'playerName']
                    elif a_lineup[5] == "":
                        a_lineup[5] = self.players_df.loc[num, 'playerName']
                    elif a_lineup[8] == "":
                        a_lineup[8] = self.players_df.loc[num, 'playerName']
                elif self.positions['TE'][num] == 1:
                    if a_lineup[6] == '':
                        a_lineup[6] = self.players_df.loc[num, 'playerName']
                    elif a_lineup[8] == '':
                        a_lineup[8] = self.players_df.loc[num, 'playerName']
                elif self.positions['DST'][num] == 1:
                    if a_lineup[7] == '':
                        a_lineup[7] = self.players_df.loc[num, 'playerName']
                total_proj += self.players_df.loc[num, 'proj']
                a_lineup[9] = total_proj
        return a_lineup

