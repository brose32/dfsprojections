import csv

from NFLOpt import NFLOpt
from NBAOpt import NBAOpt

import Optimizer
#To run enter Run.py into the terminal

sport = input("Enter '1' for NFL and '2' for NBA" +'\n')
if sport == '1':
    optimizer = NFLOpt()
    optimizer.create_indicators()
    lineup = optimizer.lineupgen()
    print_lineup = optimizer.printlineup(lineup)
    print(print_lineup)
if sport == '2':
    optimizer = NBAOpt()
    optimizer.create_indicators()
    #lineup = optimizer.lineupgen()
    #print(optimizer.printlineup(lineup))
    lineups = []
    clean_lineups = []
    for i in range(150):
        #print(i)
        lineup = optimizer.lineupgen(lineups)
        lineups.append(lineup)
        #print(optimizer.printlineup(lineup))
        clean_lineups.append(optimizer.printlineup(lineup))
    with open('final.csv', 'w', newline='') as f:
        c = csv.writer(f)
        for r in clean_lineups:
            c.writerow([player for player in r])


print('lineup generation complete')

