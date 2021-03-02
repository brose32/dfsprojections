import json
import sys
import time

from selenium import webdriver
from bs4 import BeautifulSoup as soup
import openpyxl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
driver.get('https://www.lineups.com/nba/nba-player-minutes-per-game')
# id=ngb-dd-items_per_page
element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ngb-dd-items_per_page")))
item_list = driver.find_element_by_id('ngb-dd-items_per_page')
#print('drop down found')
item_list.click()
players_num_list = driver.find_elements_by_css_selector("label[class='m-0']")
max_players = players_num_list[-1]
max_players.click()
time.sleep(1)
page_soup = soup(driver.page_source, "html.parser")
mins = page_soup.findAll("td", {"data-title": "Projected Minutes"})
names = page_soup.findAll("td", {"data-title": "Name"})
nameslist = []
with open('playerNames.json') as f:
    player_names = json.load(f)
for name in names:
    textname = name.find("span", {'class': 'player-name-col-lg'}).text
    nameslist.append(player_names[textname.strip()])

player_mins = []
for i in range(0, len(mins)) :
    player_mins.append({'NAME': nameslist[i], 'MINs': mins[i].span.text})

#print(player_mins[4])
driver.close()

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
mins_sheet = wb.create_sheet("MINUTES_PROJ")
mins_sheet.append(("Name", "Minutes"))
for player in player_mins:
    mins_sheet.append((player['NAME'], float(player['MINs'])))

wb.save(my_file)


