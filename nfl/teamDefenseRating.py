from bs4 import BeautifulSoup as soup

from urllib.request import urlopen
import openpyxl
import json
import sys

my_url = "https://www.pro-football-reference.com/years/2020/opp.htm"

uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
table_div = page_soup.find(id="div_team_stats")
tbody = table_div.tbody

teams = tbody.findAll("td", {'data-stat':"team"})

pass_attempts_against = tbody.findAll("td",{"data-stat":"pass_att"})
pass_yards_against = tbody.findAll("td", {"data-stat":"pass_yds"})
net_pass_yards_against = tbody.findAll("td", {"data-stat":"pass_net_yds_per_att"})
yards_per_rush = tbody.findAll("td", {"data-stat":"rush_yds_per_att"})
turnovers = tbody.findAll("td", {"data-stat":"turnovers"})
total_plays = tbody.findAll("td", {"data-stat":"plays_offense"})
teams_list = [team.text for team in teams]
pass_att_list = [float(att.text) for att in pass_attempts_against]
pass_yards_list = [float(yd.text) for yd in pass_yards_against]
net_pass_yards_list = [float(yd.text) for yd in net_pass_yards_against]
yards_per_rush_list = [float(yd.text)for yd in yards_per_rush]
total_plays_per_g = [float(ply.text)/16 for ply in total_plays]

defStats = {}
yards_per_pass_list = []
for att, pass_yds in zip(pass_att_list, pass_yards_list):
        yards_per_pass_list.append(pass_yds/att)
league_avg_yards_per_pass = sum(yards_per_pass_list)/len(yards_per_pass_list)
league_avg_net_yards_per_pass = sum(net_pass_yards_list)/len(net_pass_yards_list)
league_avg_yards_per_rush = sum(yards_per_rush_list)/len(yards_per_rush_list)
turnover_perc_list = []
for to, plays in zip(turnovers, total_plays):
    turnover_perc_list.append(float(to.text)/float(plays.text))
for team, to, per_pass, net_pass, per_rush, plays in zip(teams_list, turnover_perc_list, yards_per_pass_list, net_pass_yards_list, yards_per_rush_list, total_plays_per_g):
    defStats[team] = {
        "to" : to,
        "yd/pa" : per_pass,
        "yd/r" :per_rush,
        "net/pa" : net_pass,
        "opp plays" : plays
    }
adv_table = page_soup.find(id="advanced_defense")
tbody = adv_table.tbody
teams = tbody.findAll("th", {"scope":"row"})
sacks = tbody.findAll("td", {"data-stat":"sacks"})
pass_att = tbody.findAll("td", {'data-stat':"pass_att_opp"})
for team, sacks, att in zip(teams, sacks, pass_att):
    defStats[team.text]["sack"] = float(sacks.text) / (float(sacks.text) + float(att.text))
my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
defense_sheet = wb.create_sheet("DEF RAT")
defense_sheet.append(("TEAM", "Y/Pa", "NetY/Pa", "RuYd/A", "TOperc", "Sackperc", "Opp Plays"))
with open('fullNameToAbbr.json') as f:
    name_to_abbr = json.load(f)
#for team, pass_yds, net_pass, per_rush, to in zip(teams_list, yards_per_pass_list, net_pass_yards_list, yards_per_rush_list, turnover_perc_list):
#    defense_sheet.append((name_to_abbr[team], pass_yds/league_avg_yards_per_pass, net_pass/league_avg_net_yards_per_pass, per_rush/league_avg_yards_per_rush, to))
for key in defStats:
    defense_sheet.append((name_to_abbr[key], defStats[key]['yd/pa']/league_avg_yards_per_pass, defStats[key]['net/pa']/league_avg_net_yards_per_pass, defStats[key]['yd/r']/league_avg_yards_per_rush, defStats[key]['to'], defStats[key]['sack'], defStats[key]['opp plays']))
wb.save(my_file)







