from pulp import *

from MLBSetup import MLBSetup

class MLBOpt(MLBSetup):

    def __init__(self):
        self.SALARYCAP = 35000
        self.MIN_SALARY = 34000
        self.overlap = 7
        self.overlap_lateswap = 8
        self.max_per_team = 4
        self.total_lineups = 150
        super().__init__()

    def lineupgen(self, lineups):
        prob = pulp.LpProblem('MLB', LpMaximize)
        player_lineup = [pulp.LpVariable("player_{}".format(i+1), cat="Binary") for i in range(self.num_hitters)]
        pitcher_lineup = [pulp.LpVariable("pitcher_{}".format(i + 1), cat="Binary") for i in range(self.num_pitchers)]
        #player constraints
        prob += (pulp.lpSum(player_lineup[i] for i in range(self.num_hitters)) == 8)
        prob += (pulp.lpSum(pitcher_lineup[i] for i in range(self.num_pitchers)) == 1)
        #prob += (pulp.lpSum(self.positions['P'][i]*pitcher_lineup[i] for i in range(self.num_pitchers)) == 1)
        prob += (pulp.lpSum(self.positions['1B'][i]*player_lineup[i] +
                            self.positions['C'][i]*player_lineup[i] for i in range(self.num_hitters)) >= 1)
        prob += (pulp.lpSum(self.positions['2B'][i]*player_lineup[i] for i in range(self.num_hitters)) >= 1)
        prob += (pulp.lpSum(self.positions['SS'][i]*player_lineup[i] for i in range(self.num_hitters)) >= 1)
        prob += (pulp.lpSum(self.positions['3B'][i]*player_lineup[i] for i in range(self.num_hitters)) >= 1)
        prob += (pulp.lpSum(self.positions['OF'][i]*player_lineup[i] for i in range(self.num_hitters)) >= 3)

        # team constraint
        used_team = [pulp.LpVariable("u{}".format(i + 1), cat="Binary") for i in range(self.hitter_num_teams)]
        prob += (pulp.lpSum(used_team[i] for i in range(self.hitter_num_teams)) >= 3)

        # max hitter per team
        for team in self.hitter_teams:
            prob += (pulp.lpSum(
                self.hitter_teams[team][i] * player_lineup[i] for i in range(self.num_hitters)) <= self.max_per_team)
        #stacks
        primary_batting_stack = [pulp.LpVariable("stack{}".format(i + 1), cat="Binary") for i in range(len(self.stacks))]
        for i in range(len(self.stacks)):
            prob += (4 * primary_batting_stack[i] <= pulp.lpSum(
                self.stacks[i][k] * player_lineup[k] for k in range(self.num_hitters)))
        prob += (pulp.lpSum(primary_batting_stack[i] for i in range(len(self.stacks))) >= 1)
        secondary_batting_stack = [pulp.LpVariable("sec_stack{}".format(i + 1), cat="Binary") for i in
                                 range(len(self.stacks))]
        for i in range(len(self.secondary_stacks)):
            prob += (3 * secondary_batting_stack[i] <= pulp.lpSum(
                self.secondary_stacks[i][k] * player_lineup[k] for k in range(self.num_hitters)))

        prob += (pulp.lpSum(secondary_batting_stack[i] for i in range(len(self.secondary_stacks))) >= 1)


        # if len(lineups) < 50:
        #     prob += (pulp.lpSum(
        #         self.hitter_teams['HOU'][i] * player_lineup[i] for i in range(self.num_hitters)) == self.max_per_team)
        #     if len(lineups) % 8 == 0:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ARI'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 8 == 1:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['PIT'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 8 == 2:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['TOR'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 8 == 3:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['OAK'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 8 == 4:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['NYY'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 8 == 5:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ATL'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 8 == 6:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['CWS'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     else:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['SEA'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        # elif len(lineups) < 80:
        #     prob += (pulp.lpSum(
        #         self.hitter_teams['ARI'][i] * player_lineup[i] for i in range(self.num_hitters)) == self.max_per_team)
        #     if len(lineups) % 7 == 0:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['HOU'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 1:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['PIT'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 2:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['TOR'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 3:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['CWS'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 4:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['NYY'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 5:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ATL'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     else:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['OAK'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        # elif len(lineups) < 110:
        #     prob += (pulp.lpSum(
        #         self.hitter_teams['PIT'][i] * player_lineup[i] for i in range(self.num_hitters)) == self.max_per_team)
        #     if len(lineups) % 7 == 0:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['HOU'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 1:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ARI'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 2:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['TOR'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 3:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['OAK'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 4:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['NYY'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 5:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ATL'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     else:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['CWS'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        # elif len(lineups) < 120:
        #     prob += (pulp.lpSum(
        #         self.hitter_teams['TOR'][i] * player_lineup[i] for i in range(self.num_hitters)) == self.max_per_team)
        #     if len(lineups) % 6 == 0:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['HOU'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6 == 1:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['PIT'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6== 2:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ARI'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6 == 3:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['OAK'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6 == 4:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['NYY'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     else:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ATL'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        # elif len(lineups) < 140:
        #     prob += (pulp.lpSum(
        #         self.hitter_teams['OAK'][i] * player_lineup[i] for i in range(self.num_hitters)) == self.max_per_team)
        #     if len(lineups) % 7 == 0:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['HOU'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 1:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['PIT'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7== 2:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['TOR'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 3:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['CWS'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 4:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['NYY'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 7 == 5:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ATL'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     else:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ARI'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        # else:
        #     prob += (pulp.lpSum(
        #         self.hitter_teams['ATL'][i] * player_lineup[i] for i in range(self.num_hitters)) == self.max_per_team)
        #     if len(lineups) % 6 == 0:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['HOU'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6 == 1:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['PIT'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6== 2:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['TOR'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6 == 3:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['OAK'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6 == 4:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['NYY'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)
        #     elif len(lineups) % 6 == 5:
        #         prob += (pulp.lpSum(
        #             self.hitter_teams['ARI'][i] * player_lineup[i] for i in range(self.num_hitters)) == 3)


        #no hitters against pitcher
        for i in range(self.num_pitchers):
            prob += 5*pitcher_lineup[i] + pulp.lpSum(self.pitcher_opps[k][i]*player_lineup[k] for k in range(self.num_hitters)) <= 5

        # player grouping rules samples are commented out
        # how to lock in a player
        # prob += ((pulp.lpSum(self.hitter_names["Shohei Ohtani"][i]*player_lineup[i] for i in range(self.num_hitters))) == 1)

        # if player A no player B... player N and vice versa
        # prob += ((pulp.lpSum(self.player_names["Zion Williamson"][i] * player_lineup[i] +
        #                     self.player_names["Christian Wood"][i] * player_lineup[i]
        #                      for i in range(self.num_players)) <= 1))

        # max exposure for a specified hitter
        # set the percentage as decimal
        '''
        if len(lineups) != 0:
            prob += ((pulp.lpSum((self.hitter_names['Shohei Ohtani'][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_hitters)))
                     + (pulp.lpSum((self.hitter_names['Shohei Ohtani'][k] *
                                    player_lineup[k] for k in range(self.num_hitters))))) <= (.6 * (len(lineups) + 1))
        '''

        #pitcher max exposure
        #prob += ((pulp.lpSum((self.pitcher_names['Brandon Woodruff'][k] * lineups[i][k + self.num_hitters])
        #                     for i in range(len(lineups)) for k in range(self.num_pitchers)))
        #         + (pulp.lpSum((self.pitcher_names['Brandon Woodruff'][k] *
        #                        pitcher_lineup[k] for k in range(self.num_pitchers))))) <= (.45 * (len(lineups) + 1))


        #prob += ((pulp.lpSum(self.hitter_teams["TOR"][i]*player_lineup[i] for i in range(self.num_hitters))) +
        #         (pulp.lpSum(self.hitter_teams["TOR"][k] * lineups[i][k] for i in range(len(lineups)) for k in range(self.num_hitters)))) >= (.5 * 4 * (len(lineups) + 1))

        #making sure no 2 of same player for multiple position eligibility
        for key in self.hitter_names:
            prob += (pulp.lpSum(self.hitter_names[key][i] * player_lineup[i] for i in range(self.num_hitters)) <= 1)

        #add a stack

        # salary constraint
        prob += (pulp.lpSum(
            (self.hitters_df.loc[i, 'Salary'] * player_lineup[i] for i in range(self.num_hitters))) +
            pulp.lpSum((self.pitchers_df.loc[i, 'Salary'] * pitcher_lineup[i] for i in range(self.num_pitchers))) <= self.SALARYCAP)
        prob += (pulp.lpSum(
            (self.hitters_df.loc[i, 'Salary'] * player_lineup[i] for i in range(self.num_hitters))) +
                 pulp.lpSum((self.pitchers_df.loc[i, 'Salary'] * pitcher_lineup[i] for i in
                             range(self.num_pitchers))) >= self.MIN_SALARY)

        # max num players from another lineup
        for i in range(len(lineups)):
            prob += (pulp.lpSum(lineups[i][k] * player_lineup[k] for k in range(self.num_hitters)) +
                     pulp.lpSum(lineups[i][self.num_hitters + j] * pitcher_lineup[j] for j in range(self.num_pitchers)) <= self.overlap)

        # objective
        #prob += (pulp.lpSum(self.hitters_df.loc[i, 'FD PROJ'] * player_lineup[i] for i in range(self.num_hitters)) +
        #         pulp.lpSum(self.pitchers_df.loc[i, 'FD PROJ'] * pitcher_lineup[i] for i in range(self.num_pitchers)))
        #obj w randomness
        prob += (pulp.lpSum(self.hitters_df.loc[i, 'Rand Proj'] * player_lineup[i] for i in range(self.num_hitters)) +
                 pulp.lpSum(self.pitchers_df.loc[i, 'Rand Proj'] * pitcher_lineup[i] for i in range(self.num_pitchers)))
        #prob.solve(CPLEX_PY(msg=0))
        prob.solve()
        lineup_copy = []

        for i in range(self.num_hitters):
            if player_lineup[i].varValue >= 0.9 and player_lineup[i].varValue <= 1.1:
                # print(player_lineup[i])
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)
        for i in range(self.num_pitchers):
            if pitcher_lineup[i].varValue >= 0.9 and player_lineup[i].varValue <= 1.1:
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)
        # print(prob)
        return lineup_copy

    def printlineup(self, lineup):
        total_proj = 0
        total_sal = 0
        a_lineup = ['', '', '', '', '', '', '', '', '', '', '']
        hitters_lineup = lineup[:self.num_hitters]
        pitchers_lineup = lineup[-1*self.num_pitchers:]
        for num, player in enumerate(hitters_lineup):

            if player > 0.9 and player < 1.1:
                total_proj += self.hitters_df.loc[num, 'FD PROJ']
                total_sal += self.hitters_df.loc[num, 'Salary']
                if self.positions['C'][num] == 1 and a_lineup[1] == '':
                    a_lineup[1] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    continue
                if self.positions['1B'][num] == 1 and a_lineup[1] == '':
                    a_lineup[1] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    continue
                if self.positions['2B'][num] == 1 and a_lineup[2] == '':
                    a_lineup[2] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    continue
                if self.positions['3B'][num] == 1 and a_lineup[3] == '':
                    a_lineup[3] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    continue
                if self.positions['SS'][num] == 1 and a_lineup[4] == '':
                    a_lineup[4] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    continue
                if self.positions['OF'][num] == 1:
                    if a_lineup[5] == '':
                        a_lineup[5] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    elif a_lineup[6] == '':
                        a_lineup[6] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    elif a_lineup[7] == '':
                        a_lineup[7] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                    else:
                        a_lineup[8] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
                else:
                    a_lineup[8] = self.hitters_df.loc[num, 'Id'] + ':' + self.hitters_df.loc[num,'Nickname']
        for num, pitcher in enumerate(pitchers_lineup):
            if pitcher > 0.9 and pitcher < 1.1:
                total_proj += self.pitchers_df.loc[num, 'FD PROJ']
                total_sal += self.pitchers_df.loc[num, 'Salary']
                a_lineup[0] = self.pitchers_df.loc[num, 'Id'] + ':' + self.pitchers_df.loc[num, "Nickname"]

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
        sorted_players = sorted(players.items(), key=lambda x:x[1], reverse=True)
        for player in sorted_players:
            num = player[0].index(':')
            per = str((player[1]/len(lineups)* 100)) + '%'
            print(player[0][num+1:], player[1], per)
        print('Total players used: ', len(sorted_players))