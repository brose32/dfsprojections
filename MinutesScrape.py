import sys

from selenium import webdriver
from bs4 import BeautifulSoup as soup
import time
import openpyxl

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
driver.get('https://www.lineups.com/nba/nba-player-minutes-per-game')
# id=ngb-dd-items_per_page

item_list = driver.find_element_by_id('ngb-dd-items_per_page')
#print('drop down found')
item_list.click()
max_players = driver.find_elements_by_css_selector("label[for='checkbox 200']")
max_players.click()
time.sleep(5)
page_soup = soup(driver.page_source, "html.parser")
mins = page_soup.findAll("td", {"data-title": "Projected Minutes"})
names = page_soup.findAll("td", {"data-title": "Name"})
nameslist = []
for name in names:
    textname = name.find("span", {'class': 'player-name-col-lg'}).text
    nameslist.append(textname.replace("Jr.", "").replace("III", "").replace('II', '').
                       replace('Sr.','').strip())

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


