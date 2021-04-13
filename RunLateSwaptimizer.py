import csv
import re

from NBAOpt import NBAOpt

optimizer = NBAOpt()
optimizer.create_indicators()
optimizer.addTimeIndicator()
#put submitted lineups into an array
named_lineups = []
with open('lineups.csv', 'r', newline='') as f:
    c = csv.reader(f)
    for row in c:
        for col in range(8):
            named_lineups.append(row)
#strip id away from player name
for i in range(len(named_lineups)):
    named_lineups[i] = named_lineups[i][:9]
    for k in range(len(named_lineups[i])):
        name_only = re.search(r'(?<=:).*', named_lineups[i][k]).group(0)
        named_lineups[i][k] = name_only

new_lineups_raw = []
new_lineups_names = []
for lineup in named_lineups:
    locks = optimizer.getLockedPlayers(lineup)
    new_lineup = optimizer.lateSwap(new_lineups_raw, locks)
    new_lineups_raw.append(new_lineup)
    new_lineups_names.append(optimizer.printlineup(new_lineup))
with open('lineups.csv', 'w', newline='') as f:
    c = csv.writer(f)
    for r in new_lineups_names:
        c.writerow([player for player in r])
optimizer.getLineupsData(new_lineups_names)


