from pulp import *

from nascarFDSetup import nascarFDSetup


class nascarFDOpt(nascarFDSetup):
    def __init__(self):
        self.SALARYCAP = 50000
        self.MIN_SALARY = 47000
        self.overlap = 4
        self.total_lineups = 20
        self.max_sum_ownership = 251
        super().__init__()

    def lineupgen(self, lineups, named_lineups):
        with open('NascarOptSettings.json') as f:
            settings = json.load(f)
        prob = pulp.LpProblem('NASCAR', LpMaximize)
        player_lineup = [pulp.LpVariable("player_{}".format(i+1), cat="Binary") for i in range(self.num_players)]
        #player constraints
        prob += (pulp.lpSum(player_lineup[i] for i in range(self.num_players)) == 5)

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

        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)
        prob += (pulp.lpSum(self.players_df.loc[i, 'SAL']*player_lineup[i] for i in range(self.num_players)) >= self.MIN_SALARY)

        # max num players from another lineup
        for i in range(len(lineups)):
            prob += (pulp.lpSum(self.player_names[player][j] * player_lineup[j] for player in named_lineups[i]
                                for j in range(self.num_players)) <= self.overlap)

        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'Rand PROJ']*player_lineup[i] for i in range(self.num_players)))

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

    def printlineup(self, lineup):
        total_proj = 0
        total_sal = 0
        total_act = 0
        a_lineup = ['', '', '', '', '', '', '', '']
        names_only = []
        for num, player in enumerate(lineup):
            if player > 0.9 and player < 1.1:
                names_only.append(self.players_df.loc[num, 'NAME'])
                if a_lineup[0] == "":
                    a_lineup[0] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif a_lineup[1] == "":
                    a_lineup[1] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif a_lineup[2] == '':
                        a_lineup[2] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif a_lineup[3] == '':
                    a_lineup[3] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                elif a_lineup[4] == '':
                        a_lineup[4] = self.players_df.loc[num, 'ID'] + ':' + self.players_df.loc[num, 'NAME']
                total_proj += self.players_df.loc[num, 'PROJ']
                total_sal += self.players_df.loc[num, 'SAL']
                total_act += self.players_df.loc[num, 'Actual']
                a_lineup[5] = total_proj
                a_lineup[6] = total_sal
                a_lineup[7] = total_act
        return a_lineup, names_only

    def getLineupsData(self, lineups):
        players = {}
        for lineup in lineups:
            for i in range(len(lineup) - 3):
                if not players.__contains__(lineup[i]):
                    players[lineup[i]] = 1
                else:
                    players[lineup[i]] += 1
        sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
        for player in sorted_players:
            num = player[0].index(':')
            per = str((player[1] / len(lineups) * 100)) + '%'
            print(player[0][num + 1:], player[1], per)
        print(f"Total players used: {len(sorted_players)}")