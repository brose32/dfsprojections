from pulp import *
from NBAsetup import NBAsetup
import time
import json
class NBAOpt(NBAsetup):
    def __init__(self):
        self.SALARYCAP = 60000
        self.MIN_SALARY = 59500
        self.overlap = 6
        self.overlap_lateswap = 5
        self.max_per_team = 3
        self.total_lineups = 150
        self.max_sum_ownership = 251
        super().__init__()


    def lineupgen(self, lineups, named_lineups):
        with open('NBAOptSettings.json') as f:
            settings = json.load(f)

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
        prob += (pulp.lpSum(used_team[i] for i in range(self.num_teams)) >= 4)

        # max player per team
        for team in self.player_teams:
            prob += (pulp.lpSum(self.player_teams[team][i]*player_lineup[i] for i in range(self.num_players)) <= self.max_per_team)

        #player grouping rules samples are commented out
        #how to lock in a player
        #prob += ((pulp.lpSum(self.player_names["Stanley Johnson"][i]*player_lineup[i] for i in range(self.num_players))) == 1)
        #exclude player
        #prob += ((pulp.lpSum(self.player_names["Dwight Howard"][i]*player_lineup[i] for i in range(self.num_players))) == 0)
        for lock in settings['locks']:
            prob += ((pulp.lpSum(
                self.player_names[lock][i] * player_lineup[i] for i in range(self.num_players))) == 1)
        for lock in settings['excludes']:
            prob += ((pulp.lpSum(
                self.player_names[lock][i] * player_lineup[i] for i in range(self.num_players))) == 0)

        # if player A no player B... player N and vice versa
        # prob += ((pulp.lpSum(self.player_names["Trae Young"][i] * player_lineup[i] +
        #                             self.player_names["Dejounte Murray"][i] * player_lineup[i]
        #                              for i in range(self.num_players)) <= 1))
        for group in settings['max_groups']:
            prob += pulp.lpSum(self.player_names[player][i] * player_lineup[i] for player in group[:-1] for i in range(self.num_players)) <= group[-1]

        for group in settings['min_groups']:
            prob += pulp.lpSum(self.player_names[player][i] * player_lineup[i] for player in group[:-1] for i in range(self.num_players)) >= group[-1]

        for group in settings['force_groups']:
            prob += pulp.lpSum(self.player_names[player][i] * player_lineup[i] for player in group[:-1] for i in range(self.num_players)) == group[-1]

        # #set minimum for one team
        # lock_teams = ['GSW', 'DEN', 'OKC', 'ORL']
        # for team in lock_teams:
        #     prob += ((pulp.lpSum(self.player_teams[team][i] * player_lineup[i]
        #                                 for i in range(self.num_players)) >= 1))
        for team in settings['team_min']:
            prob += ((pulp.lpSum(self.player_teams[team][i] * player_lineup[i]
                                        for i in range(self.num_players)) >= settings['team_min'][team]))

        for team in settings['team_max']:
            prob += ((pulp.lpSum(self.player_teams[team][i] * player_lineup[i]
                                        for i in range(self.num_players)) <= settings['team_max'][team]))

        #force at least 4 players into late night hammer
        # prob += ((pulp.lpSum(self.player_teams['LAL'][i] * player_lineup[i] + self.player_teams['HOU'][i] * player_lineup[i]
        #             for i in range(self.num_players)) >= 4))
        #force on player from a game
        # prob += ((pulp.lpSum(self.player_teams['HOU'][i] * player_lineup[i] + self.player_teams['SAS'][i] * player_lineup[i]
        #                                 for i in range(self.num_players)) >= 1))
        for team in settings['game_min']:
            prob += ((pulp.lpSum(self.player_teams[team[0]][i] * player_lineup[i] + self.player_teams[team[1]][i] * player_lineup[i]
                                        for i in range(self.num_players)) >= team[2]))

        for team in settings['game_max']:
            prob += ((pulp.lpSum(self.player_teams[team[0]][i] * player_lineup[i] + self.player_teams[team[1]][i] * player_lineup[i]
                                        for i in range(self.num_players)) <= team[2]))

        #min exposure for a specified player
        # if len(lineups) != 0:
        #    prob += ((pulp.lpSum((self.player_names['Jayson Tatum'][k] * lineups[i][k])
        #                         for i in range(len(lineups)) for k in range(self.num_players)))
        #             + (pulp.lpSum((self.player_names['Jayson Tatum'][k] *
        #                            player_lineup[k] for k in range(self.num_players))))) >= (.6 * (len(lineups) + 1))
        # #    prob += ((pulp.lpSum((self.player_names['Kevin Durant'][k] * lineups[i][k])
        # #                         for i in range(len(lineups)) for k in range(self.num_players)))
        # #             + (pulp.lpSum((self.player_names['Kevin Durant'][k] *
        # #                            player_lineup[k] for k in range(self.num_players))))) >= (.1 * (len(lineups) + 1))
        # prob += ((pulp.lpSum((self.player_names['Jayson Tatum'][k] * lineups[i][k])
        #                      for i in range(len(lineups)) for k in range(self.num_players)))
        #          + (pulp.lpSum((self.player_names['Jayson Tatum'][k] *
        #                         player_lineup[k] for k in range(self.num_players))))) >= (.1 * (len(lineups) + 1))
        for player in settings['min_exp']:
            prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    player_lineup[k] for k in range(self.num_players))))) >= (settings['min_exp'][player] * (len(lineups) + 1))
        #max exposure for a specified player
        # set the percentage as decimal
        # if len(lineups) != 0:
        #     prob += ((pulp.lpSum((self.player_names['Anfernee Simons'][k]*lineups[i][k])
        #                    for i in range(len(lineups)) for k in range(self.num_players)))
        #                    + (pulp.lpSum((self.player_names['Anfernee Simons'][k]*
        #                        player_lineup[k] for k in range(self.num_players)))) <= (.75 * len(lineups) + 1))
        for player in settings['max_exp']:
            prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    player_lineup[k] for k in range(self.num_players))))) <= (settings['max_exp'][player] * (len(lineups) + 1))

        #no same player twice
        for key in self.player_names:
            prob += (pulp.lpSum(self.player_names[key][i] * player_lineup[i] for i in range(self.num_players)) <= 1)

        #Ownership constraint
        # prob += (pulp.lpSum(
        #     self.players_df.loc[i, 'OWN'] * player_lineup[i] for i in range(self.num_players)) <= 270)

        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)
        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) >= self.MIN_SALARY)
        # prob += (pulp.lpSum(
        #     self.players_df.loc[i, 'FDOWN'] * player_lineup[i] for i in range(self.num_players)) <= self.max_sum_ownership)

        # prob += (pulp.lpSum(
        #     self.players_df.loc[i, 'FDOWN'] * player_lineup[i] for i in range(self.num_players)) >= 200)

        # max num players from another lineup
        overlap_st = time.time()
        for i in range(len(lineups)):
            prob += (pulp.lpSum(self.player_names[player][j] * player_lineup[j] for player in named_lineups[i]
                                for j in range(self.num_players)) <= self.overlap)

        #max num players from another lineup old
        # for i in range(len(lineups)):
        #     prob += (pulp.lpSum(lineups[i][k]*player_lineup[k] for k in range(self.num_players)) <= self.overlap)
        overlap = time.time() - overlap_st
        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'PROJ']*player_lineup[i] for i in range(self.num_players)))

        status = prob.solve(CPLEX_PY(msg=0))

        if status == -1:
            print('lineup not found')
            return None
        lineup_copy = []

        for i in range(self.num_players):
            if player_lineup[i].varValue == None:
                lineup_copy.append(0)
                continue
            if player_lineup[i].varValue >= 0.9 and player_lineup[i].varValue <= 1.1:
                #print(player_lineup[i])
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)
        #print(prob)
        return lineup_copy

    def lateSwap(self, lineups, locked, named_lineups):
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

        # prob += (
        # (pulp.lpSum(self.player_teams["UTA"][i] * player_lineup[i] + self.player_teams["ATL"][i] * player_lineup[i]
        #             for i in range(self.num_players)) >= 1))

        #player grouping rules samples are commented out
        #how to lock in a player
        #prob += ((pulp.lpSum(self.player_names["Stanley Johnson"][i]*player_lineup[i] for i in range(self.num_players))) == 1)
        #locking in players whos game has started from lineup
        for player in locked:
            prob += ((pulp.lpSum(self.player_names[player][i]*player_lineup[i] for i in range(self.num_players))) == 1)
        #set number of locked players to same as locked players from lineup
        prob += ((pulp.lpSum(self.started[i]*player_lineup[i] for i in range(self.num_players))) == len(locked))

        #if player A no player B... player N and vice versa
        prob += ((pulp.lpSum(self.player_names["Damian Lillard"][i] * player_lineup[i] +
                                    self.player_names["Jerami Grant"][i] * player_lineup[i] +
                                    self.player_names["Anfernee Simons"][i] * player_lineup[i]
                                     for i in range(self.num_players)) <= 2))



        #no same player twice
        for key in self.player_names:
            prob += (pulp.lpSum(self.player_names[key][i] * player_lineup[i] for i in range(self.num_players)) <= 1)

        # prob += ((pulp.lpSum((self.player_names['Stephen Curry'][k] * lineups[i][k])
        #                      for i in range(len(lineups)) for k in range(self.num_players)))
        #          + (pulp.lpSum((self.player_names['Stephen Curry'][k] *
        #                         player_lineup[k] for k in range(self.num_players))))) >= (.15 * (len(lineups) + 1))
        #max exposure for a specified player
        # set the percentage as decimal
        # prob += ((pulp.lpSum((self.player_names['Anthony Davis'][k]*lineups[i][k])
        #                    for i in range(len(lineups)) for k in range(self.num_players)))
        #                    + (pulp.lpSum((self.player_names['Anthony Davis'][k]*
        #                        player_lineup[k] for k in range(self.num_players)))) <= (.6 * self.total_lineups))
        prob += ((pulp.lpSum((self.player_names['Ja Morant'][k]*lineups[i][k])
                           for i in range(len(lineups)) for k in range(self.num_players)))
                           + (pulp.lpSum((self.player_names['Ja Morant'][k]*
                               player_lineup[k] for k in range(self.num_players)))) <= (.3 * len(lineups)))


        # prob += ((pulp.lpSum(self.player_names["Joel Embiid"][i] * player_lineup[i] +
        #                              self.player_names["Tobias Harris"][i] * player_lineup[i]
        #                              for i in range(self.num_players)) <= 1))
        # prob += (pulp.lpSum(
        #     self.players_df.loc[i, 'OWN'] * player_lineup[i] for i in range(self.num_players)) <= 270)
        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)
        #prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) >= self.MIN_SALARY)

        #max num players from another lineup old
        # for i in range(len(lineups)):
        #     prob += (pulp.lpSum(lineups[i][k]*player_lineup[k] for k in range(self.num_players)) <= self.overlap_lateswap)

        # max num players from another lineup
        for i in range(len(lineups)):
            prob += (pulp.lpSum(self.player_names[player][j] * player_lineup[j] for player in named_lineups[i]
                                for j in range(self.num_players)) <= self.overlap_lateswap)

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
        names_only = []
        for num, player in enumerate(lineup):
            if player > 0.9 and player < 1.1:
                names_only.append(self.players_df.loc[num, 'NAME'])
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
        return a_lineup, names_only


    def getLineupsData(self, lineups):
        players = {}
        for lineup in lineups:
            for i in range(len(lineup) - 2):
                if not players.__contains__(lineup[i]) and not lineup[i].isnumeric():
                    players[lineup[i]] = 1
                else:
                    players[lineup[i]] += 1
        sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
        for player in sorted_players:
            num = player[0].index(':')
            per = str((player[1] / len(lineups) * 100)) + '%'
            print(player[0][num + 1:], player[1], per)
        print(f"Total players used: {len(sorted_players)}")



