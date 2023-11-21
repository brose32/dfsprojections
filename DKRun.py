import csv
import time
from DKNBAOpt import DKNBAOpt
starttime = time.time()
optimizer = DKNBAOpt()
optimizer.create_indicators()
lineups = []
clean_lineups = []
named_lineups = []
for i in range(optimizer.total_lineups):
    print(f"lineups generated: {i}", end='\r')
    #uncomment below if using randomness, commented out for speed enhancement
    #optimizer.addRandomness()
   # optimizer.addNormalRandomness()
    lineup = optimizer.lineupgen(lineups, named_lineups)
    lineups.append(lineup)
    (clean_lineup, names_lineup) = optimizer.printlineup(lineup)
    clean_lineups.append(clean_lineup)
    named_lineups.append(names_lineup)

with open('dklineups.csv', 'w', newline='') as f:
    c = csv.writer(f)
    for r in clean_lineups:
        c.writerow([player for player in r])

optimizer.getLineupsData(clean_lineups)
print('lineups generated in ', time.time()-starttime, "seconds")
