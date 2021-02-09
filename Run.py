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
    lineup = optimizer.lineupgen()
    print(optimizer.printlineup(lineup))


