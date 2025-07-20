import csv
import json
import time
from DKNBAOpt import DKNBAOpt
starttime = time.time()
optimizer = DKNBAOpt()
optimizer.create_indicators()
optimizer.build_base_model()
lineups = []
clean_lineups = []
named_lineups = []
for i in range(optimizer.total_lineups):
    print(f"lineups generated: {i}", end='\r')
    #uncomment below if using randomness, commented out for speed enhancement
    if optimizer.randomness:
        optimizer.addRandomness()
    if optimizer.normal_randomness:
        optimizer.addNormalRandomness()

    lineup = optimizer.lineupgenwarm2(lineups, named_lineups)
    lineups.append(lineup)
    (clean_lineup, names_lineup) = optimizer.printlineup(lineup)
    clean_lineups.append(clean_lineup)
    named_lineups.append(names_lineup)
    # lineup_name_vars = {
    #   "sense": -1,
    #   "pi": None,
    #   "constant": optimizer.overlap * -1,
    #   "name": f"luoverlap_{i}",
    #   "coefficients": []
    # }
    # for name in names_lineup:
    #     for idx, x in enumerate(optimizer.player_names[name]):
    #         if x == 1:
    #             lineup_name_vars['coefficients'].append({"name": f"player_{idx + 1}", "value": 1})
    # optimizer.overlap_lineups.append(lineup_name_vars)

    #remove dynamic constraints
    optimizer.remove_dynamic_constraints()
with open('dklineups.csv', 'w', newline='') as f:
    c = csv.writer(f)
    for r in clean_lineups:
        c.writerow([player for player in r])

optimizer.getLineupsData(clean_lineups)
print('lineups generated in ', time.time()-starttime, "seconds")
