from pulp import *
from DKNBAsetup import DKNBAsetup
import json
import time
import math
import re
# from NpEncoder import NpEncoder
class DKNBAOpt(DKNBAsetup):
    def __init__(self):
        self.SALARYCAP = 50000
        self.MIN_SALARY = 48000
        self.overlap = 5 
        self.overlap_lateswap = 5
        self.max_per_team = 4
        self.total_lineups = 150
        self.max_sum_ownership = 251
        self.contest_size = 35671 
        #self.ownership_geomean = math.log(1/self.contest_size) / 8
        self.ownership_geomean = math.log(0.2)

        super().__init__()

    def safe_name(self, name):
        return re.sub(r'\W+', '_', name)

    def build_base_model(self):
        if self.randomness:
            self.addRandomness()
        if self.normal_randomness:
            self.addNormalRandomness()

        with open('NBAOptSettings.json') as f:
            settings = json.load(f)

        self.prob = pulp.LpProblem('NBA', LpMaximize)
        self.player_lineup = [pulp.LpVariable("player_{}".format(i + 1), cat="Binary") for i in range(self.num_players)]

        #fixed positional player constraints
        self.prob += (pulp.lpSum(self.player_lineup[i] for i in range(self.num_players)) == 8, "TotalPlayers")
        for pos in ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F']:
            self.prob += (pulp.lpSum(self.positions[pos][i]*self.player_lineup[i] for i in range(self.num_players)) >= 1, f"min_{pos}")

        #fixed global max players per team
        for team in self.player_teams:
            self.prob += (pulp.lpSum(self.player_teams[team][i]*self.player_lineup[i] for i in range(self.num_players)) <= self.max_per_team, f"globalteamcap_{team}")

        #global runtime settings
        for lock in settings['locks']:
            self.prob += ((pulp.lpSum(
                self.player_names[lock][i] * self.player_lineup[i] for i in range(self.num_players))) == 1, f"lock_{lock}")

        for exclude in settings['excludes']:
            self.prob += ((pulp.lpSum(
                self.player_names[exclude][i] * self.player_lineup[i] for i in range(self.num_players))) == 0, f"exclude_{exclude}")

        constraint_id = 0
        for group in settings['max_groups']:
            self.prob += (pulp.lpSum(self.player_names[player][i] * self.player_lineup[i] for player in group[:-1] for i in range(self.num_players)) <= group[-1], f"maxgroup_{constraint_id}")
            constraint_id += 1
        constraint_id = 0
        for group in settings['min_groups']:
            self.prob += (pulp.lpSum(self.player_names[player][i] * self.player_lineup[i] for player in group[:-1] for i in range(self.num_players)) >= group[-1], f"mingroup_{constraint_id}")
            constraint_id += 1

        constraint_id = 0
        for group in settings['force_groups']:
            self.prob += (pulp.lpSum(self.player_names[player][i] * self.player_lineup[i] for player in group[:-1] for i in range(self.num_players)) == group[-1], f"forcegroup_{constraint_id}")
            constraint_id += 1

        for team in settings['team_min']:
            self.prob += ((pulp.lpSum(self.player_teams[team][i] * self.player_lineup[i]
                                        for i in range(self.num_players)) >= settings['team_min'][team], f"teammin_{team}"))

        for team in settings['team_max']:
            self.prob += ((pulp.lpSum(self.player_teams[team][i] * self.player_lineup[i]
                                        for i in range(self.num_players)) <= settings['team_max'][team], f"teammax_{team}"))
        constraint_id = 0
        for team in settings['game_min']:
            self.prob += ((pulp.lpSum(self.player_teams[t][i] * self.player_lineup[i]
                                        for t in team[:-1] for i in range(self.num_players)) >= team[-1], f"gamemin_{constraint_id}"))
            constraint_id += 1

        constraint_id = 0
        for team in settings['game_max']:
            self.prob += ((pulp.lpSum(self.player_teams[t][i] * self.player_lineup[i]
                                        for t in team[:-1] for i in range(self.num_players)) <= team[-1], f"gamemax_{constraint_id}"))
            constraint_id += 1

        #fixed no duplicate players in same lineup
        for key in self.player_names:
            self.prob += (pulp.lpSum(self.player_names[key][i] * self.player_lineup[i] for i in range(self.num_players)) <= 1, f"dedupe_{self.safe_name(key)}")

        #fixed ownership geomean
        self.prob += (pulp.lpSum(self.log_ownerships[i] * self.player_lineup[i] for i in range(self.num_players)) / 8 <= self.ownership_geomean, "OwnershipGeoMean")

        #fixed salary constraint
        self.prob += (pulp.lpSum(self.players_df.loc[i, 'DKSAL']*self.player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP, "MaxSalary")
        self.prob += (pulp.lpSum(self.players_df.loc[i, 'DKSAL']*self.player_lineup[i] for i in range(self.num_players)) >= self.MIN_SALARY, "MinSalary")

        #objective
        if self.normal_randomness or self.randomness:
            self.prob += (pulp.lpSum(self.players_df.loc[i, 'Rand PROJ'] * self.player_lineup[i] for i in range(self.num_players)))
        else:
            self.prob += (pulp.lpSum(self.players_df.loc[i, 'DKPROJ']*self.player_lineup[i] for i in range(self.num_players)))

    def remove_dynamic_constraints(self):
        with open('NBAOptSettings.json') as f:
            settings = json.load(f)
        fixed = {"TotalPlayers", "MaxSalary", "MinSalary", "OwnershipGeoMean"}
        fixed.update(f"min_{pos}" for pos in ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F'])
        fixed.update(f"globalteamcap_{team}" for team in self.player_teams)
        fixed.update(f"lock_{lock}" for lock in settings['locks'])
        fixed.update(f"excludes_{exclude}" for exclude in settings['excludes'])
        fixed.update(f"maxgroup_{i}" for i in range(len(settings['max_groups'])))
        fixed.update(f"mingroup_{i}" for i in range(len(settings['min_groups'])))
        fixed.update(f"forcegroup_{i}" for i in range(len(settings['force_groups'])))
        fixed.update(f"teammin_{team}" for team in settings['team_min'])
        fixed.update(f"teammax_{team}" for team in settings['team_max'])
        fixed.update(f"gamemin_{i}" for i in range(len(settings['game_min'])))
        fixed.update(f"gamemax_{i}" for i in range(len(settings['game_max'])))
        fixed.update(f"dedupe_{self.safe_name(key)}" for key in self.player_names)
        fixed.update(f"luoverlap_{i}" for i in range(self.total_lineups))

        constraints_to_remove = [constraint for constraint in list(self.prob.constraints.keys()) if constraint not in fixed]
        for constraint in constraints_to_remove:
            self.prob.constraints.pop(constraint)


    def lineupgenwarm2(self, lineups, named_lineups):
        #add last created lineup overlap constraint
        if named_lineups != []:
            self.prob += (pulp.lpSum(self.player_names[player][j] * self.player_lineup[j] for player in named_lineups[-1]
                                for j in range(self.num_players)) <= self.overlap, f"luoverlap_{len(lineups)}")
        with open('NBAOptSettings.json') as f:
            settings = json.load(f)

        for player in settings['min_exp']:
            self.prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    self.player_lineup[k] for k in range(self.num_players))))) >= (settings['min_exp'][player] * (len(lineups) + 1)), f"minexp_{player}"

        for player in settings['max_exp']:
            self.prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    self.player_lineup[k] for k in range(self.num_players))))) <= (settings['max_exp'][player] * (len(lineups) + 1)), f'maxexp_{player}'

        if self.randomness or self.normal_randomness:
            self.prob.setObjective(pulp.lpSum(self.players_df.loc[i, 'Rand PROJ']*self.player_lineup[i] for i in range(self.num_players)))

        #debugging
        # prob.to_json('nbadkmodelpulp.json')
        # self.prob.writeLP('testlp.lp')
        # prob.writeMPS('testmps.mps')
        # self.model = prob.to_dict()

        #manually add lu overlap constraints
        # model = self.prob.to_dict()
        # model['constraints'] = model['constraints'] + self.overlap_lineups
        # var1, prob1 = pulp.LpProblem.from_dict(model)
        # status = prob1.solve(CPLEX_PY(msg=0, timeLimit=2))
        # print(len(self.prob.constraints.keys()))
        status = self.prob.solve(CPLEX_PY(msg=0, timeLimit=2))
        if status == -1:
            print('lineup not found')
            return None
        lineup_copy = []

        for i in range(self.num_players):
            if self.player_lineup[i].varValue == None:
                lineup_copy.append(0)
                continue
            elif self.player_lineup[i].varValue >= 0.9 and self.player_lineup[i].varValue <= 1.1:
                #print(player_lineup[i])
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)
            # if var1[f'player_{i + 1}'].varValue == None:
            #     lineup_copy.append(0)
            #     continue
            # elif var1[f'player_{i + 1}'].varValue >= 0.9 and var1[f'player_{i + 1}'].varValue <= 1.1:
            #     #print(player_lineup[i])
            #     lineup_copy.append(1)
            # else:
            #     lineup_copy.append(0)
        #print(prob)
        return lineup_copy

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
        # used_team = [pulp.LpVariable("u{}".format(i + 1), cat="Binary") for i in range(self.num_teams)]
        # prob += (pulp.lpSum(used_team[i] for i in range(self.num_teams)) >= 4)

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
            prob += ((pulp.lpSum(self.player_teams[t][i] * player_lineup[i]
                                        for t in team[:-1] for i in range(self.num_players)) <= team[-1]))
        #for team in settings['game_max']:
        #    prob += ((pulp.lpSum(self.player_teams[team[0]][i] * player_lineup[i] + self.player_teams[team[1]][i] * player_lineup[i]
        #                                for i in range(self.num_players)) <= team[2]))

        for player in settings['min_exp']:
            prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    player_lineup[k] for k in range(self.num_players))))) >= (settings['min_exp'][player] * (len(lineups) + 1))

        for player in settings['max_exp']:
            prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    player_lineup[k] for k in range(self.num_players))))) <= (settings['max_exp'][player] * (len(lineups) + 1)), f'maxexp_{player}'

        #no same player twice
        for key in self.player_names:
            prob += (pulp.lpSum(self.player_names[key][i] * player_lineup[i] for i in range(self.num_players)) <= 1)

        #Ownership constraint
        # prob += (pulp.lpSum(
        #     self.players_df.loc[i, 'DKOWN'] * player_lineup[i] for i in range(self.num_players)) <= self.max_sum_ownership)
        #ownership product
        #prob += (pulp.lpSum(self.log_ownerships[i] * player_lineup[i] for i in range(self.num_players)) <= math.log(1 / self.contest_size))
        #ownership geomean
        prob += (pulp.lpSum(self.log_ownerships[i] * player_lineup[i] for i in range(self.num_players)) / 8 <= self.ownership_geomean)

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
        # prob.to_json('nbadkmodelpulp.json')
        # prob.writeLP('testlp.lp')
        # prob.writeMPS('testmps.mps')
        # self.model = prob.to_dict()

        status = prob.solve(CPLEX_PY(msg=0, timeLimit=2))
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

    def lineupgen2(self, lineups, named_lineups):
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
        # used_team = [pulp.LpVariable("u{}".format(i + 1), cat="Binary") for i in range(self.num_teams)]
        # prob += (pulp.lpSum(used_team[i] for i in range(self.num_teams)) >= 4)

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
            prob += ((pulp.lpSum(self.player_teams[t][i] * player_lineup[i]
                                        for t in team[:-1] for i in range(self.num_players)) <= team[-1]))

        for player in settings['min_exp']:
            prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    player_lineup[k] for k in range(self.num_players))))) >= (settings['min_exp'][player] * (len(lineups) + 1))

        for player in settings['max_exp']:
            prob += ((pulp.lpSum((self.player_names[player][k] * lineups[i][k])
                                 for i in range(len(lineups)) for k in range(self.num_players)))
                     + (pulp.lpSum((self.player_names[player][k] *
                                    player_lineup[k] for k in range(self.num_players))))) <= (settings['max_exp'][player] * (len(lineups) + 1)), f'maxexp_{player}'

        #no same player twice
        for key in self.player_names:
            prob += (pulp.lpSum(self.player_names[key][i] * player_lineup[i] for i in range(self.num_players)) <= 1)

        #Ownership constraint
        # prob += (pulp.lpSum(
        #     self.players_df.loc[i, 'DKOWN'] * player_lineup[i] for i in range(self.num_players)) <= self.max_sum_ownership)
        #ownership product
        #prob += (pulp.lpSum(self.log_ownerships[i] * player_lineup[i] for i in range(self.num_players)) <= math.log(1 / self.contest_size))
        #ownership geomean
        prob += (pulp.lpSum(self.log_ownerships[i] * player_lineup[i] for i in range(self.num_players)) / 8 <= self.ownership_geomean)

        #salary constraint
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKSAL']*player_lineup[i] for i in range(self.num_players)) <= self.SALARYCAP)
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKSAL']*player_lineup[i] for i in range(self.num_players)) >= self.MIN_SALARY)

        # max num players from another lineup
        # for i in range(len(lineups)):
        #     prob += (pulp.lpSum(self.player_names[player][j] * player_lineup[j] for player in named_lineups[i]
        #                         for j in range(self.num_players)) <= self.overlap)

        #objective
        prob += (pulp.lpSum(self.players_df.loc[i, 'DKPROJ']*player_lineup[i] for i in range(self.num_players)))
        # prob.to_json('nbadkmodelpulp.json')
        # prob.writeLP('testlp.lp')
        # prob.writeMPS('testmps.mps')
        # self.model = prob.to_dict()
        model = prob.to_dict()
        model['constraints'] = model['constraints'] + self.overlap_lineups
        var1, prob1 = pulp.LpProblem.from_dict(model)
        status = prob1.solve(CPLEX_PY(msg=0, timeLimit=2))
        if status == -1:
            print('lineup not found')
            return None
        lineup_copy = []

        for i in range(self.num_players):
            # if player_lineup[i].varValue == None:
            #     lineup_copy.append(0)
            #     continue
            # elif player_lineup[i].varValue >= 0.9 and player_lineup[i].varValue <= 1.1:
            #     #print(player_lineup[i])
            #     lineup_copy.append(1)
            # else:
            #     lineup_copy.append(0)
            if var1[f'player_{i + 1}'].varValue == None:
                lineup_copy.append(0)
                continue
            elif var1[f'player_{i + 1}'].varValue >= 0.9 and var1[f'player_{i + 1}'].varValue <= 1.1:
                #print(player_lineup[i])
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)
        #print(prob)
        return lineup_copy

    def lineupgenwarm(self):
        # player_lineup, prob = LpProblem.from_json('nbadkmodelpulp.json')
        player_lineup, prob = LpProblem.from_dict(self.model)
        status = prob.solve(CPLEX_PY(msg=0))
        if status == -1:
            print('lineup not found')
            return None
        lineup_copy = []
        for i in range(self.num_players):
            if player_lineup[f'player_{i + 1}'].varValue == None:
                lineup_copy.append(0)
                continue
            elif player_lineup[f'player_{i + 1}'].varValue >= 0.9 and player_lineup[f'player_{i + 1}'].varValue <= 1.1:
                # print(player_lineup[i])
                lineup_copy.append(1)
            else:
                lineup_copy.append(0)
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
        prob += ((pulp.lpSum(self.player_names["Jayson Tatum"][i] * player_lineup[i] +
                             self.player_names["Kristaps Porzingis"][i] * player_lineup[i]
                             for i in range(self.num_players)) <= 1))
        prob += ((pulp.lpSum(self.player_names["Herbert Jones"][i] * player_lineup[i] +
                             self.player_names["Trey Murphy III"][i] * player_lineup[i]
                             for i in range(self.num_players)) <= 1))
        prob += ((pulp.lpSum(self.player_names["Bobby Portis"][i] * player_lineup[i] +
                             self.player_names["Brook Lopez"][i] * player_lineup[i]
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
        prob += ((pulp.lpSum((self.player_names["Lamar Stevens"][k]*lineups[i][k])
                           for i in range(len(lineups)) for k in range(self.num_players)))
                           + (pulp.lpSum((self.player_names["Lamar Stevens"][k]*
                               player_lineup[k] for k in range(self.num_players)))) <= (.8 * self.total_lineups))


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
        ownership_product = 1
        a_lineup = ['', '', '', '', '', '', '', '', '', '', '']
        names_only = []
               
        for num, player in enumerate(lineup):
            if player > 0.9 and player < 1.1:
                names_only.append(self.players_df.loc[num, 'NAME'])
                if self.positions['PG'][num] == 1:
                    if a_lineup[0] == '':
                        a_lineup[0] = self.players_df.loc[num, 'ID']
                    else:
                        a_lineup[7] = self.players_df.loc[num, 'ID']
                elif self.positions['SG'][num] == 1:
                    if a_lineup[1] == '':
                        a_lineup[1] = self.players_df.loc[num, 'ID']
                    else:
                        a_lineup[7] = self.players_df.loc[num, 'ID']
                elif self.positions['SF'][num] == 1:
                    if a_lineup[2] == '':
                        a_lineup[2] = self.players_df.loc[num, 'ID']
                    else:
                        a_lineup[7] = self.players_df.loc[num, 'ID']
                elif self.positions['PF'][num] == 1:
                    if a_lineup[3] == '':
                        a_lineup[3] = self.players_df.loc[num, 'ID']
                    else:
                        a_lineup[7] = self.players_df.loc[num, 'ID']
                elif self.positions['C'][num] == 1:
                    if a_lineup[4] == '':
                        a_lineup[4] = self.players_df.loc[num, 'ID']
                    else:
                        a_lineup[7] = self.players_df.loc[num, 'ID']
                elif self.positions['G'][num] == 1:
                    if a_lineup[5] == '':
                        a_lineup[5] = self.players_df.loc[num, 'ID']
                    else:
                        a_lineup[7] = self.players_df.loc[num, 'ID']
                elif self.positions['F'][num] == 1:
                    if a_lineup[6] == '':
                        a_lineup[6] = self.players_df.loc[num, 'ID']
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
                ownership_product *= self.players_df.loc[num, 'DKOWN']
                a_lineup[8] = total_proj
                a_lineup[9] = total_sal
            a_lineup[10] = ownership_product ** .125
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
            for i in range(len(lineup) - 3):
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


    def getPlayerEligiblePositions(self, name):
        return self.players_df[self.players_df['NAME'] == name]['POS'].values




