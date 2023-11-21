import csv
import re
import pandas as pd
from DKNBAOpt import DKNBAOpt


optimizer = DKNBAOpt()
optimizer.create_indicators()
optimizer.addTimeIndicator()
#put submitted lineups into an array
old_lineups = []
with open('dklineups.csv', 'r', newline='') as f:
    c = csv.reader(f)
    for row in c:
        old_lineups.append(row)
#strip id away from player name
for i in range(len(old_lineups)):

    old_lineups[i] = old_lineups[i][:8]
    for k in range(len(old_lineups[i])):
        name_only = re.search(r'^(.*?)\s\(', old_lineups[i][k]).group(1)
        old_lineups[i][k] = name_only
new_lineups_raw = []
new_lineups_names = []
named_lineups = []
for lineup in old_lineups:
    print(f"lineups generated: {len(new_lineups_names)}", end='\r')
    locks = optimizer.getLockedPlayers(lineup)
    new_lineup = optimizer.lateSwap(new_lineups_raw, locks, named_lineups)
    new_lineups_raw.append(new_lineup)
    (new_lineup, names_lineup) = optimizer.printlineup(new_lineup)
    new_lineups_names.append(new_lineup)
    named_lineups.append(names_lineup)
    # optimizer.addRandomness()
    # optimizer.addNormalRandomness()
#
#
with open('fjokic.csv', 'w', newline='') as f:
    c = csv.writer(f)
    for r in new_lineups_names:
        c.writerow([player for player in r])
optimizer.getLineupsData(new_lineups_names)


