import json
import re
import sys


import openpyxl
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
driver.maximize_window()
my_url = "https://fantasyteamadvice.com/dfs/nba/ownership"
driver.get(my_url)
elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "td"))
)
rows = driver.find_elements_by_xpath("//tbody/tr")

page_html = driver.page_source
driver.close()
page_soup = soup(page_html, "html.parser")

rows = page_soup.findAll("tr", {"data-testid": "ownershipPlayerRow"})
players = []
# with open('playerNames.json') as f:
#     player_names = json.load(f)
with open('dkNormalizedPlayerNames.json') as f:
    player_names = json.load(f)
for row in rows:
    name = row.find("td", {"data-testid": "ownershipPlayer"}).text
    fd_owner = float(re.search(r'^(.*?)%', row.find("td", {"data-testid": "ownershipPlayerDkOwnership"}).text).group(1))
    players.append({"name": player_names[name.replace(' Jr.', '').replace(' Jr','').replace(' Sr','').replace(' III', '').replace(' II', '').replace(' Sr.', '').replace(' IV', '').replace('.', '').replace("'", '').upper()], "DKowner": fd_owner})

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
fd_owner_sheet = wb.create_sheet("DKOWNER")
fd_owner_sheet.append(("NAME", "DKOWN"))
for player in players:
    fd_owner_sheet.append((player["name"], player["DKowner"]))

wb.save(my_file)





