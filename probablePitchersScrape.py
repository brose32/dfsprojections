import sys

from bs4 import BeautifulSoup as soup
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

my_url = "https://www.mlb.com/probable-pitchers"

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
driver.maximize_window()
driver.get(my_url)

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "probable-pitchers__container"))
)
page_soup = soup(driver.page_source, "html.parser")
driver.close()
full_grid = page_soup.find("div", {"class": "probable-pitchers__container"})

pitcher_grids = full_grid.findAll("div", {"class" : "probable-pitchers__matchup"})

pitchersDict = {}
for grid in pitcher_grids:
    pitcher_names = grid.findAll("a", {"class" : "probable-pitchers__pitcher-name-link"})
    throwing_hands = grid.findAll("span", {"class" : "probable-pitchers__pitcher-pitch-hand"})
    teams = grid.findAll("span", {"class": "probable-pitchers__team-name"})
    pitchersDict[pitcher_names[0].text] = {"throws": throwing_hands[0].text.strip(), "team" : teams[0].text.lstrip().rstrip()}
    pitchersDict[pitcher_names[1].text] = {"throws" : throwing_hands[1].text.strip(), "team" : teams[2].text.lstrip().rstrip()}

my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
probables_sheet = wb.create_sheet("PITCHER PROBS")
probables_sheet.append(("NAME", "THROWS", "TEAM"))
for key in pitchersDict:
    probables_sheet.append((key, pitchersDict[key]["throws"], pitchersDict[key]["team"]))
wb.save(my_file)