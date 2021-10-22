from pulp import *
from NFLSetup import NFLSetup


class NFLOpt(NFLSetup):
    def __init__(self):
        self.SALARYCAP = 60000
        self.MIN_SALARY = 59400
        self.overlap = 6
        super().__init__()


    def lineupgen(self, lineups):
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
        prob += (pulp.lpSum(self.positions['D'][i]*player_lineup[i] for i in range(self.num_players)) == 1)

        #Stack QB with 1+ teammates
        for qbid in range(self.num_players):
            if self.players_df.loc[qbid,'Position'] == 'QB':
                prob += pulp.lpSum([player_lineup[i] for i in range(self.num_players) if
                                    (self.players_df.loc[i,'Team'] == self.players_df.loc[qbid,'Team'] and
                                     self.players_df.loc[i,'Position'] in ('WR', 'TE'))] +
                                   [-1 * player_lineup[qbid]]) >= 0

        #Don't stack with opposing DST:
        for dstid in range(self.num_players):
            if self.players_df.loc[dstid, 'Position'] == 'D':
                prob += pulp.lpSum([player_lineup[i] for i in range(self.num_players) if
                                    self.players_df.loc[i,'Team'] == self.players_df.loc[dstid,'Opponent']] +
                                   [8 * player_lineup[dstid]]) <= 8
        #qb bring back
        for qbid in range(self.num_players):
            if self.players_df.loc[qbid, 'Position'] == 'QB':
                prob += pulp.lpSum([player_lineup[i] for i in range(self.num_players) if
                                    self.players_df.loc[i,'Team'] == self.players_df['Opponent'][qbid]] +
                                   [-1 * player_lineup[qbid]]) >= 0

        # max exposure for a specified player
        # set the percentage as decimal
        # if len(lineups) != 0:
        #      prob += ((pulp.lpSum((self.player_names['Alvin Kamara'][k] * lineups[i][k])
        #                  for i in range(len(lineups)) for k in range(self.num_players)))
        #                  + (pulp.lpSum((self.player_names['Alvin Kamara'][k] *
        #                   player_lineup[k] for k in range(self.num_players))))) <= ( .5 * (len(lineups) + 1))

            prob += ((pulp.lpSum((self.player_names['Joe Burrow'][k] * lineups[i][k])
                          for i in range(len(lineups)) for k in range(self.num_players)))
                          + (pulp.lpSum((self.player_names['Joe Burrow'][k] *
                           player_lineup[k] for k in range(self.num_players))))) <= (.4 * (len(lineups) + 1))

        # min exposure for a specified player
        if len(lineups) != 0:
            prob += ((pulp.lpSum((self.player_names['Patrick Mahomes'][k] * lineups[i][k])
                                   for i in range(len(lineups)) for k in range(self.num_players)))
                       + (pulp.lpSum((self.player_names['Patrick Mahomes'][k] *
                                      player_lineup[k] for k in range(self.num_players))))) >= (.25 * (len(lineups) + 1))

        # #if A not B etc
        prob += ((pulp.lpSum(self.player_names["Mark Andrews"][i] * player_lineup[i] +
                               self.player_names["Marquise Brown"][i] * player_lineup[i]
                               for i in range(self.num_players)) <= 1))


        for i in range(len(lineups)):
            prob += (pulp.lpSum(lineups[i][k] * player_lineup[k] for k in range(self.num_players)) <= self.overlap)

        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'Salary']*player_lineup[i] for i in range(self.num_players))
                 <= self.SALARYCAP)

        #min salary
        prob += (pulp.lpSum(self.players_df.loc[i, 'Salary'] * player_lineup[i] for i in range(self.num_players))
                 >= self.MIN_SALARY)

        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'Rand Proj']*player_lineup[i] for i in range(self.num_players)))
        prob.solve(CPLEX_PY(msg=0))

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
                        a_lineup[0] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                elif self.positions['RB'][num] == 1:
                    if a_lineup[1] == "":
                        a_lineup[1] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                    elif a_lineup[2] == "":
                        a_lineup[2] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                    elif a_lineup[7] == "":
                        a_lineup[7] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                elif self.positions['WR'][num] == 1:
                    if a_lineup[3] == "":
                        a_lineup[3] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                    elif a_lineup[4] == "":
                        a_lineup[4] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                    elif a_lineup[5] == "":
                        a_lineup[5] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                    elif a_lineup[7] == "":
                        a_lineup[7] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                elif self.positions['TE'][num] == 1:
                    if a_lineup[6] == '':
                        a_lineup[6] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                    elif a_lineup[7] == '':
                        a_lineup[7] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                elif self.positions['D'][num] == 1:
                    if a_lineup[8] == '':
                        a_lineup[8] = self.players_df.loc[num,"Id"]+":"+self.players_df.loc[num, 'Nickname']
                total_proj += self.players_df.loc[num, 'FD PROJ']
                a_lineup[9] = total_proj
        return a_lineup

    def getLineupsData(self, lineups):
        players = {}
        for lineup in lineups:
            for i in range(len(lineup)-1):
                if not players.__contains__(lineup[i]) and not lineup[i].isnumeric():
                    players[lineup[i]] = 1
                else:
                    players[lineup[i]] += 1
        sorted_players = sorted(players.items(), key=lambda x:x[1], reverse=True)
        for player in sorted_players:
            num = player[0].index(':')
            per = str((player[1]/len(lineups)* 100)) + '%'
            print(player[0][num+1:], player[1], per)
        print('Total players used: ', len(sorted_players))