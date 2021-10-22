import re

from bs4 import BeautifulSoup as soup

from urllib.request import urlopen
import openpyxl
import json
import sys
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
my_url = "https://www.covers.com/sports/nfl/matchups"
uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
games = page_soup.findAll("div", {"class":"cmg_game_data"})
games.pop(-1)
imp_totals = {}
for game in games:
    home_team = game.find("div", {"class":"cmg_matchup_list_column_3"}).div.text
    home_team_abbr = re.search('[A-Z][A-Z]?[A-Z]', home_team)[0]
    away_team = game.find("div", {"class":"cmg_matchup_list_column_1"}).div.text
    away_team_abbr = re.search('[A-Z][A-Z]?[A-Z]', away_team)[0]
    game_time = game.find("div", {"class":"cmg_game_time"}).text
    odds_box = game.find("div", {"class":"cmg_team_live_odds"}).findAll("span")
    total = float(re.search('\s(.*)', odds_box[1].text)[0])
    home_team_line = float(re.search('\s(.*)', odds_box[2].text)[0])
    imp_totals[home_team_abbr] = {
                                    'impTotal' : (total / 2) - (home_team_line/2),
                                    'O/U' : total
                                 }
    imp_totals[away_team_abbr] = {
                                    'impTotal' : (total / 2) + (home_team_line/2),
                                    'O/U' : total
                                 }

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
lines_sheet = wb.create_sheet("VEGAS LINES")
lines_sheet.append(("TEAM", "Imp", "O/U"))
for key in imp_totals:
    lines_sheet.append((key, imp_totals[key]['impTotal'], imp_totals[key]['O/U']))

wb.save(my_file)
