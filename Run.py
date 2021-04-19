import csv
import time

from MLBOpt import MLBOpt
from NFLOpt import NFLOpt
from NBAOpt import NBAOpt

#To run enter Run.py into the terminal

sport = input("Enter '1' for NFL, '2' for NBA or '3' for MLB" +'\n')
starttime = time.time()
if sport == '1':
    optimizer = NFLOpt()
    optimizer.create_indicators()
    lineup = optimizer.lineupgen()
    print_lineup = optimizer.printlineup(lineup)
    print(print_lineup)
if sport == '2':
    optimizer = NBAOpt()
    optimizer.create_indicators()
    lineups = []
    clean_lineups = []
    for i in range(150):
        #uncomment below if using randomness, commented out for speed enhancement
        #optimizer = NBAOpt()
        #optimizer.create_indicators()
        #optimizer.addRandomness()
        lineup = optimizer.lineupgen(lineups)
        lineups.append(lineup)
        #print(optimizer.printlineup(lineup))
        clean_lineups.append(optimizer.printlineup(lineup))
    with open('lineups.csv', 'w', newline='') as f:
        c = csv.writer(f)
        for r in clean_lineups:
            c.writerow([player for player in r])
    optimizer.getLineupsData(clean_lineups)
if sport == '3':
    optimizer = MLBOpt()
    optimizer.create_indicators()
    lineups = []
    clean_lineups = []
    for i in range(150):
        # uncomment below if using randomness, commented out for speed enhancement
        # optimizer = MLBOpt()
        # optimizer.create_indicators()
        # optimizer.addRandomness()
        lineup = optimizer.lineupgen(lineups)
        lineups.append(lineup)
        clean_lineups.append(optimizer.printlineup(lineup))
    with open('mlblineups.csv', 'w', newline='') as f:
        c = csv.writer(f)
        for r in clean_lineups:
            c.writerow([player for player in r])
    #optimizer.getLineupsData(clean_lineups)

print('lineups generated in ', time.time()-starttime, "seconds")

