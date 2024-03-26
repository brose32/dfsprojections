from pulp import *
from DKNBAsetup import DKNBAsetup
import json
import time
class DKNBAOpt(DKNBAsetup):
    def __init__(self):
        self.SALARYCAP = 50000
        self.MIN_SALARY = 48000
        self.overlap = 6
        self.overlap_lateswap = 5
        self.max_per_team = 3
        self.total_lineups = 50
        self.max_sum_ownership = 251
        super().__init__()


    def lineupgen(self, lineups, named_lineups):
        with open('NBAOptSettings.json') as f:
            settings = json.load(f)

        prob = pulp.LpProblem('NBA', LpMaximize)
        player_lineup = [pulp.LpVariable("player_{}".format(i+1), cat="Binary") for i in range(self.num_players)]
        #player constraints
        prob += (pulp.lpSum(player_lineup[i] for i in range(self.num_players)) == 8)
        prob += (pulp.lpSum(self.positions['PG'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['SG'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['SF'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['PF'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['C'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['G'][i] * player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['F'][i] * player_lineup[i] for i in range(self.num_players)) >= 1)
        # prob += (pulp.lpSum(self.positions['UTIL'][i] * player_lineup[i] for i in range(self.num_players)) == 1)

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

        for group in settings['max_groups']:
            prob += pulp.lpSum(self.player_names[player][i] * player_lineup[i] for player in group[:-1] for i in range(self.num_players)) <= group[-1]

        for group in settings['min_groups']:
            prob += pulp.lpSum(self.player_names[player][i] * player_lineup[i] for player in group[:-1] for i in range(self.num_players)) >= group[-1]

        for group in settings['force_groups']:
            prob += pulp.lpSum(self.player_names[player][i] * player_lineup[i] for player in group[:-1] for i in range(self.num_players)) == group[-1]

        for team in settings['team_min']:
            prob += ((pulp.lpSum(self.player_teams[team][i] * player_lineup[i]
                                        for i in range(self.num_players)) >= settings['team_min'][team]))

        for team in settings['team_max']:
            prob += ((pulp.lpSum(self.player_teams[team][i] * player_lineup[i]
                                        for i in range(self.num_players)) <= settings['team_max'][team]))

        for team in settings['game_min']:
            prob += ((pulp.lpSum(self.player_teams[t][i] * player_lineup[i]
                                        for t in team[:-1] for i in range(self.num_players)) >= team[-1]))

        for team in settings['game_max']:
            prob += ((pulp.lpSum(self.player_teams[team[0]][i] * player_lineup[i] + self.player_teams[team[1]][i] * player_lineup[i]
                                        for i in range(self.num_players)) <= team[2]))

        for player in settings['min_exp']:
            prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    player_lineup[k] for k in range(self.num_players))))) >= (settings['min_exp'][player] * (len(lineups) + 1))

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
        #     self.players_df.loc[i, 'DKOWN'] * player_lineup[i] for i in range(self.num_players)) <= self.max_sum_ownership)

        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKSAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKSAL']*player_lineup[i] for i in range(self.num_players)) >= self.MIN_SALARY)

        # max num players from another lineup
        for i in range(len(lineups)):
            prob += (pulp.lpSum(self.player_names[player][j] * player_lineup[j] for player in named_lineups[i]
                                for j in range(self.num_players)) <= self.overlap)

        #max num players from another lineup old
        # for i in range(len(lineups)):
        #     prob += (pulp.lpSum(lineups[i][k]*player_lineup[k] for k in range(self.num_players)) <= self.overlap)

        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKPROJ']*player_lineup[i] for i in range(self.num_players)))

        status = prob.solve(CPLEX_PY(msg=0))

        if status == -1:
            print('lineup not found')
            return None
        lineup_copy = []

        for i in range(self.num_players):
            if player_lineup[i].varValue == None:
                lineup_copy.append(0)
                continue
            elif player_lineup[i].varValue >= 0.9 and player_lineup[i].varValue <= 1.1:
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
        prob += (pulp.lpSum(player_lineup[i] for i in range(self.num_players)) == 8)
        prob += (pulp.lpSum(self.positions['PG'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['SG'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['SF'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['PF'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['C'][i]*player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['G'][i] * player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['F'][i] * player_lineup[i] for i in range(self.num_players)) >= 1)
        prob += (pulp.lpSum(self.positions['UTIL'][i] * player_lineup[i] for i in range(self.num_players)) == 1)
        #team constraint
        used_team = [pulp.LpVariable("u{}".format(i + 1), cat="Binary") for i in range(self.num_teams)]
        prob += (pulp.lpSum(used_team[i] for i in range(self.num_teams)) >= 3)

        # max player per team
        for team in self.player_teams:
            prob += (pulp.lpSum(self.player_teams[team][i]*player_lineup[i] for i in range(self.num_players)) <= self.max_per_team)


        #player grouping rules samples are commented out
        #how to lock in a player
        #prob += ((pulp.lpSum(self.player_names["Stanley Johnson"][i]*player_lineup[i] for i in range(self.num_players))) == 1)
        #locking in players whos game has started from lineup
        for player in locked:
            prob += ((pulp.lpSum(self.player_names[player[0]][i]*player_lineup[i]*self.positions[player[1]][i] for i in range(self.num_players))) == 1)
        #set number of locked players to same as locked players from lineup so no players from already started games
        prob += ((pulp.lpSum(self.started[i]*player_lineup[i] for i in range(self.num_players))) == len(locked))

        #if player A no player B... player N and vice versa
        # prob += ((pulp.lpSum(self.player_names["Nikola Vucevic"][i] * player_lineup[i] +
        #                                     self.player_names["Coby White"][i] * player_lineup[i] +
        #                                     self.player_names["DeMar DeRozan"][i] * player_lineup[i]
        #                                      for i in range(self.num_players)) <= 1))
        prob += ((pulp.lpSum(self.player_names["LeBron James"][i] * player_lineup[i] +
                             self.player_names["Anthony Davis"][i] * player_lineup[i]
                             for i in range(self.num_players)) <= 1))
        prob += ((pulp.lpSum(self.player_names["CJ McCollum"][i] * player_lineup[i] +
                             self.player_names["Zion Williamson"][i] * player_lineup[i]
                             for i in range(self.num_players)) <= 1))
        # prob += ((pulp.lpSum(self.player_names["Paul George"][i] * player_lineup[i] +
        #                      self.player_names["Kawhi Leonard"][i] * player_lineup[i]
        #                      for i in range(self.num_players)) <= 1))
        # prob += ((pulp.lpSum(self.player_names["Giannis Antetokounmpo"][i] * player_lineup[i] +
        #                      self.player_names["Damian Lillard"][i] * player_lineup[i]
        #                      for i in range(self.num_players)) <= 1))

        # prob += (
        # (pulp.lpSum(self.player_teams['UTA'][i] * player_lineup[i] + self.player_teams['SAS'][i] * player_lineup[i]
        #             for i in range(self.num_players)) <= 5))

        #no same player twice
        for key in self.player_names:
            prob += (pulp.lpSum(self.player_names[key][i] * player_lineup[i] for i in range(self.num_players)) <= 1)

        # prob += ((pulp.lpSum((self.player_names['Stephen Curry'][k] * lineups[i][k])
        #                      for i in range(len(lineups)) for k in range(self.num_players)))
        #          + (pulp.lpSum((self.player_names['Stephen Curry'][k] *
        #                         player_lineup[k] for k in range(self.num_players))))) >= (.15 * (len(lineups) + 1))
        #max exposure for a specified player
        # set the percentage as decimal
        # prob += ((pulp.lpSum((self.player_names["Jalen Smith"][k]*lineups[i][k])
        #                    for i in range(len(lineups)) for k in range(self.num_players)))
        #                    + (pulp.lpSum((self.player_names["Jalen Smith"][k]*
        #                        player_lineup[k] for k in range(self.num_players)))) <= (.8 * self.total_lineups))


        # prob += ((pulp.lpSum(self.player_names["Joel Embiid"][i] * player_lineup[i] +
        #                              self.player_names["Tobias Harris"][i] * player_lineup[i]
        #                              for i in range(self.num_players)) <= 1))
        # prob += (pulp.lpSum(
        #     self.players_df.loc[i, 'OWN'] * player_lineup[i] for i in range(self.num_players)) <= 270)
        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKSAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)
        #prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) >= self.MIN_SALARY)

        #max num players from another lineup old
        # for i in range(len(lineups)):
        #     prob += (pulp.lpSum(lineups[i][k]*player_lineup[k] for k in range(self.num_players)) <= self.overlap_lateswap)

        # max num players from another lineup
        for i in range(len(lineups)):
            prob += (pulp.lpSum(self.player_names[player][j] * player_lineup[j] for player in named_lineups[i]
                                for j in range(self.num_players)) <= self.overlap_lateswap)

        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKPROJ']*player_lineup[i] for i in range(self.num_players)))
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
        a_lineup = ['', '', '', '', '', '', '', '', '', '']
        names_only = []
        for num, player in enumerate(lineup):
            if player > 0.9 and player < 1.1:
                names_only.append(self.players_df.loc[num, 'NAME'])
                # print(self.players_df.loc[num, 'NAME'])
                if self.positions['PG'][num] == 1 and a_lineup[0] == '':
                    a_lineup[0] = self.players_df.loc[num, 'ID']
                elif self.positions['SG'][num] == 1 and a_lineup[1] == '':
                    a_lineup[1] = self.players_df.loc[num, 'ID']
                elif self.positions['SF'][num] == 1 and a_lineup[2] == '':
                    a_lineup[2] = self.players_df.loc[num, 'ID']
                elif self.positions['PF'][num] == 1 and a_lineup[3] == '':
                    a_lineup[3] = self.players_df.loc[num, 'ID']
                elif self.positions['C'][num] == 1 and a_lineup[4] == '':
                    a_lineup[4] = self.players_df.loc[num, 'ID']
                elif self.positions['G'][num] == 1 and a_lineup[5] == '':
                    a_lineup[5] = self.players_df.loc[num, 'ID']
                elif self.positions['F'][num] == 1 and a_lineup[6] == '':
                    a_lineup[6] = self.players_df.loc[num, 'ID']
                elif self.positions['UTIL'][num] == 1 and a_lineup[7] == '':
                    a_lineup[7] = self.players_df.loc[num, 'ID']
                else:
                    a_lineup[7] = self.players_df.loc[num, 'ID']
                # if self.positions['PG'][num] == 1:
                #     if a_lineup[0] == '':
                #         a_lineup[0] = self.players_df.loc[num, 'ID']
                #     else:
                #         a_lineup[7] = self.players_df.loc[num, 'ID']
                # elif self.positions['SG'][num] == 1:
                #     if a_lineup[1] == '':
                #         a_lineup[1] = self.players_df.loc[num, 'ID']
                #     else:
                #         a_lineup[7] = self.players_df.loc[num, 'ID']
                # elif self.positions['SF'][num] == 1:
                #     if a_lineup[2] == '':
                #         a_lineup[2] = self.players_df.loc[num, 'ID']
                #     else:
                #         a_lineup[7] = self.players_df.loc[num, 'ID']
                # elif self.positions['PF'][num] == 1:
                #     if a_lineup[3] == '':
                #         a_lineup[3] = self.players_df.loc[num, 'ID']
                #     else:
                #         a_lineup[7] = self.players_df.loc[num, 'ID']
                # elif self.positions['C'][num] == 1:
                #     if a_lineup[4] == '':
                #         a_lineup[4] = self.players_df.loc[num, 'ID']
                #     else:
                #         a_lineup[7] = self.players_df.loc[num, 'ID']
                # elif self.positions['G'][num] == 1:
                #     if a_lineup[5] == '':
                #         a_lineup[5] = self.players_df.loc[num, 'ID']
                #     else:
                #         a_lineup[7] = self.players_df.loc[num, 'ID']
                # elif self.positions['F'][num] == 1:
                #     if a_lineup[6] == '':
                #         a_lineup[6] = self.players_df.loc[num, 'ID']
                #     else:
                #         a_lineup[7] = self.players_df.loc[num, 'ID']
                # elif self.positions['UTIL'][num] == 1:
                #     a_lineup[7] = self.players_df.loc[num, 'ID']
                # else:
                #     a_lineup[7] = self.players_df.loc[num, 'ID']
                total_proj += self.players_df.loc[num, 'DKPROJ']
                total_sal += self.players_df.loc[num, 'DKSAL']
                a_lineup[8] = total_proj
                a_lineup[9] = total_sal
        # print('NEW LINEUP')
        return a_lineup, names_only

    def setLineupPositions(self, lineup):
        #sets UTIL to latest game start highest salary
        time_order = self.players_df[self.players_df['ID'].isin(lineup)].sort_values(by=['TIME', 'DKSAL'], ascending=False)
        og_util = lineup[7]
        lineup[7] = time_order.iloc[0]['ID']
        og_positions = self.players_df[self.players_df['ID'] == og_util]['POS'].values



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
            num = player[0].index('(')
            per = str((player[1] / len(lineups) * 100)) + '%'
            print(player[0][:num - 1], player[1], per)
        print('Total players used: ', len(sorted_players))



