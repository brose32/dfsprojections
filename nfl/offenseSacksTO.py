import time

from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.request import urlopen
import openpyxl
import json
import sys
realoptions = webdriver.ChromeOptions()
realoptions.add_argument("--headless")
my_url = "https://www.pro-football-reference.com/years/2021/index.htm"
PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH, options=realoptions)

driver.maximize_window()
driver.get(my_url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.ID, "team_stats"))
)

page_soup = soup(driver.page_source, "html.parser")

driver.quit()

table = page_soup.find(id="team_stats")
tbody = table.tbody

teams = tbody.findAll("td", {'data-stat':"team"})
total_plays = tbody.findAll("td", {"data-stat":"plays_offense"})
total_passes = tbody.findAll("td", {"data-stat":"pass_att"})
total_rushes = tbody.findAll("td", {"data-stat":"rush_att"})
turnovers = tbody.findAll("td", {"data-stat":"turnovers"})
teams_list = [team.text for team in teams]
turnover_perc_list = []
sacks_perc_list = []

for plays, passes, rushes in zip(total_plays, total_passes, total_rushes):
    sacks = float(plays.text)-float(passes.text)-float(rushes.text)
    sacks_perc_list.append(sacks/(float(passes.text) + sacks))
for to, plays in zip(turnovers, total_plays):
    turnover_perc_list.append(float(to.text)/float(plays.text))

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
off_sheet = wb.create_sheet("OFF STATS")
off_sheet.append(("TEAM", "TOper", "Sackper"))
with open('fullNameToAbbr.json') as f:
    name_to_abbr = json.load(f)
for team, to, sack in zip(teams_list, turnover_perc_list, sacks_perc_list):
    off_sheet.append((name_to_abbr[team], to, sack))

wb.save(my_file)
