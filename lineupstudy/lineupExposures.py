import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np

# get a usernames player exposures and players net winnings

username = 'youdacao'
contest_fpath = "C:\\Users\\brose32\\Documents\\flagship0208.csv"
contest_df = pd.read_csv(contest_fpath, usecols=['Rank', 'EntryId', 'EntryName', 'Points', 'Lineup'])
ownership_df = pd.read_csv(contest_fpath, usecols=['Player', 'Roster Position', '%Drafted', 'FPTS'])

contest_details = requests.get("https://api.draftkings.com/contests/v1/contests/158553858?format=json")
contest_dict = other_contest_details.json()['contestDetail']
contest_payouts = other_contest_details.json()['contestDetail']['payoutSummary']

lineups_df = contest_df[contest_df['EntryName'].str.contains(username)]
if len(lineups_df) > contest_dict['maximumEntriesPerUser']:
    print(f'ERROR - more than {contest_dict["maximumEntriesPerUser"]} lineups found')

player_exposures = {}

# get players net winnings
winnings = 0
for rank in lineups_df['Rank']:
    for d in other_contest_payouts:
        if rank >= d['minPosition'] and rank <= d['maxPosition']:
            winnings += d['payoutDescriptions'][0]['value']

print(f"{username} Net Winnings: {winnings - - (len(lineups_df) * contest_dict['entryFee'])}")

for lineup in lineups_df['Lineup']:
    pattern = r'(?<=C\s).*?(?=\sF\s)'
    center = re.search(pattern, lineup).group(0)
    player_exposures[center] = player_exposures.get(center, 0) + 1
    pattern = r'(?<=F\s).*?(?=\sG\s)'
    forward = re.search(pattern, lineup).group(0)
    player_exposures[forward] = player_exposures.get(forward, 0) + 1
    pattern = r'(?<=G\s).*?(?=\sPF\s)'
    guard = re.search(pattern, lineup).group(0)
    player_exposures[guard] = player_exposures.get(guard, 0) + 1
    pattern = r'(?<=PF\s).*?(?=\sPG\s)'
    powerforward = re.search(pattern, lineup).group(0)
    player_exposures[powerforward] = player_exposures.get(powerforward, 0) + 1
    pattern = r'(?<=PG\s).*?(?=\sSF\s)'
    pointguard = re.search(pattern, lineup).group(0)
    player_exposures[pointguard] = player_exposures.get(pointguard, 0) + 1
    pattern = r'(?<=SF\s).*?(?=\sSG\s)'
    smallforward = re.search(pattern, lineup).group(0)
    player_exposures[smallforward] = player_exposures.get(smallforward, 0) + 1
    pattern = r'(?<=SG\s).*?(?=\sUTIL\s)'
    shootingguard = re.search(pattern, lineup).group(0)
    player_exposures[shootingguard] = player_exposures.get(shootingguard, 0) + 1
    pattern = r'(?<=UTIL\s).*$'
    util = re.search(pattern, lineup).group(0)
    player_exposures[util] = player_exposures.get(util, 0) + 1

print(f'Player Pool: {len(player_exposures)}')
sorted_players = sorted(player_exposures.items(), key=lambda x: x[1], reverse=True)
for player in sorted_players:
    print(player[0], (player[1] / len(lineups_df) * 100))

# Players Top 10 owned players
player_top10 = dict(sorted_players[:10])
x = list(player_top10.keys())
x_axis = np.arange(len(x))

player_own = list([(player_top10[o] / len(lineups_df) * 100) for o in player_top10])
contest_own10_df = ownership_df[ownership_df['Player'].isin(x)]
contest_own = [float(contest_own10_df[contest_own10_df['Player'] == player]['%Drafted'].values[0].replace('%', '')) for
               player in x]

plt.bar(x_axis - 0.2, contest_own, 0.4, label='Field')
plt.bar(x_axis + 0.2, player_own, 0.4, label=username)
plt.xticks(x_axis, x, rotation='vertical')
plt.xlabel('Players')
plt.ylabel('Ownership %')
plt.title(f"{username} Top 10 owned vs Field")
plt.legend()
plt.show()

# plt.bar(list(player_top10.keys()), list([player / len(lineups_df) * 100 for player in player_top10.values()]))

# plt.title(f'{username} Top 10 Owned Players')
# plt.xlabel("Players")
# plt.ylabel("Ownership %")
# plt.xticks(rotation='vertical')
# plt.show()


# Top 10 owned contest players and username exposures
owned_top10 = ownership_df.head(10)
x = list(owned_top10['Player'].values)
x_axis = np.arange(len(x))

contest_own = list([float(o.replace('%', '')) for o in owned_top10['%Drafted']])
player_own = list(
    [player_exposures[player] / len(lineups_df) * 100 if player in player_exposures else 0 for player in x])

plt.bar(x_axis - 0.2, contest_own, 0.4, label='Field')
plt.bar(x_axis + 0.2, player_own, 0.4, label=username)
plt.xticks(x_axis, x, rotation='vertical')
plt.xlabel('Players')
plt.ylabel('Ownership %')
plt.title(f"Field Top 10 owned vs {username}")
plt.legend()
plt.show()
