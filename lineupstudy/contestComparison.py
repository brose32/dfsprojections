import pandas as pd
import sys
import requests

my_contest_fpath = "C:\\Users\\brose32\\Documents\\minimax-0208.csv"
other_fpath = "C:\\Users\\brose32\\Documents\\flagship0208.csv"
other_df = pd.read_csv(other_fpath, usecols=['Rank', 'EntryId', 'EntryName', 'Points', 'Lineup'])
my_contest_df = pd.read_csv(my_contest_fpath, usecols=['Rank', 'EntryId', 'EntryName', 'Points', 'Lineup'])
#print(my_contest_df.head())
#print(other_df.head())

#get payout details
my_contest_details = requests.get("https://api.draftkings.com/contests/v1/contests/158568486?format=json")
my_contest_dict = my_contest_details.json()['contestDetail']
my_contest_payouts = my_contest_details.json()['contestDetail']['payoutSummary']

other_contest_details = requests.get("https://api.draftkings.com/contests/v1/contests/158553858?format=json")
other_contest_dict = other_contest_details.json()['contestDetail']
other_contest_payouts = other_contest_details.json()['contestDetail']['payoutSummary']

#get number of 150 maxers in my tournament and comparison tournament
my_maxers = my_contest_df[my_contest_df['EntryName'].str.contains('150/150')]
print(f'My contest 150 maxers: {len(my_maxers)}')
other_maxers = other_df[other_df['EntryName'].str.contains('150/150')]
print(f'Other contest 150 maxers: {len(other_maxers)}')


#get number of 150 maxers who made / lost money


#get 1st place and min cash score my tournament and comparison tournament
my_first_place = my_contest_df[my_contest_df['Rank'] == 1]
print(f'My contest first place: {my_first_place["Points"].values[0]} {my_first_place["EntryName"].values[0]}')
other_first_place = other_df[other_df['Rank'] == 1]
print(f'Other contest first place: {other_first_place["Points"].values[0]} {other_first_place["EntryName"].values[0]}')

my_contest_cash_lus_all = my_contest_df[my_contest_df["Rank"] <= my_contest_payouts[-1]['maxPosition']]
print(f'My contest min cash: {my_contest_cash_lus_all["Points"].values[-1]}')
other_contest_cash_lus_all = other_df[other_df["Rank"] <= other_contest_payouts[-1]['maxPosition']]
print(f'Other contest min cash: {other_contest_cash_lus_all["Points"].values[-1]}')

#my lineups results in other tournament
my_lineups_df = my_contest_df[my_contest_df['EntryName'].str.contains('grassfairy6')]
new_other_df = pd.concat([other_df, my_lineups_df], axis=0).sort_values(by="Points", ascending=False).reset_index(drop=True)
new_other_df['newRank'] = new_other_df['Points'].rank(method='min', ascending=False)
my_lineups_other_df = new_other_df[new_other_df['EntryName'].str.contains('grassfairy6')]

other_winnings = 0
for rank in my_lineups_other_df['newRank']:
    for d in other_contest_payouts:
        if rank >= d['minPosition'] and rank <= d['maxPosition']:
            other_winnings += d['payoutDescriptions'][0]['value']
print(f"Other contest net winnings: {other_winnings - (len(my_lineups_other_df) * other_contest_dict['entryFee'])}")