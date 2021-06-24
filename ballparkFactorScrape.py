import json
import sys

import openpyxl
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#lefties
parkfactorsLefty = {}
PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
driver.maximize_window()
my_url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2021&batSide=L&stat=index_wOBA&condition=All&rolling="
driver.get(my_url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "default-table-row"))
)
page_soup = soup(driver.page_source, "html.parser")
tablebody = page_soup.find("div", {'id':'parkFactors'}).table.tbody
trows = tablebody.findAll("tr", {'class': 'default-table-row'})
for row in trows:
    rowData = row.findAll("td")
    parkName = rowData[2].text.rstrip().lstrip()
    parkfactorsLefty[parkName] = float(rowData[4].text.lstrip()) / 100
#get righties
my_url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2021&batSide=R&stat=index_wOBA&condition=All&rolling="
driver.get(my_url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "default-table-row"))
)
page_soup = soup(driver.page_source, "html.parser")
tablebody = page_soup.find("div", {'id':'parkFactors'}).table.tbody
trows = tablebody.findAll("tr", {'class': 'default-table-row'})
parkfactorsRighty = {}
for row in trows:
    rowData = row.findAll("td")
    parkName = rowData[2].text.rstrip().lstrip()
    parkfactorsRighty[parkName] = float(rowData[4].text.lstrip()) / 100

#both for pitcher ballpark factor
my_url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2021&batSide=&stat=index_wOBA&condition=All&rolling="
driver.get(my_url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "default-table-row"))
)
page_soup = soup(driver.page_source, "html.parser")
tablebody = page_soup.find("div", {'id':'parkFactors'}).table.tbody
trows = tablebody.findAll("tr", {'class': 'default-table-row'})
parkfactorsBoth = {}
for row in trows:
    rowData = row.findAll("td")
    parkName = rowData[2].text.rstrip().lstrip()
    parkfactorsBoth[parkName] = float(rowData[4].text.lstrip()) / 100

parkFactorsNestedDict = {}
with open('parkToAbbr.json') as f:
    park_to_abbr = json.load(f)

for key in parkfactorsLefty:
    parkFactorsNestedDict[park_to_abbr[key]] = {
        "L" : parkfactorsLefty[key],
        "R" : parkfactorsRighty[key],
        "B" : parkfactorsBoth[key]
    }

#grab Rangers and Blue Jays from 2021 season - new ball park doesnt show up in rolling
#lefties
my_url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2021&batSide=L&stat=index_wOBA&condition=All&rolling=no"
driver.get(my_url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "default-table-row"))
)
rangers_left = driver.find_elements_by_xpath("//tr[@id='parkFactors-tr_5325']/td[5]")[0].text
bluejays_left = driver.find_elements_by_xpath("//tr[@id='parkFactors-tr_2536']/td[5]")[0].text
#righties
my_url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2021&batSide=R&stat=index_wOBA&condition=All&rolling=no"
driver.get(my_url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "default-table-row"))
)
rangers_right = driver.find_elements_by_xpath("//tr[@id='parkFactors-tr_5325']/td[5]")[0].text
bluejays_right = driver.find_elements_by_xpath("//tr[@id='parkFactors-tr_2536']/td[5]")[0].text
#both for pitchers
my_url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2021&batSide=&stat=index_wOBA&condition=All&rolling=no"
driver.get(my_url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "default-table-row"))
)
rangers_both = driver.find_elements_by_xpath("//tr[@id='parkFactors-tr_5325']/td[5]")[0].text
bluejays_both = driver.find_elements_by_xpath("//tr[@id='parkFactors-tr_2536']/td[5]")[0].text
parkFactorsNestedDict["TEX"] = {
    "L" : float(rangers_left) / 100,
    "R" : float(rangers_right) / 100,
    "B" : float(rangers_both) / 100
}
parkFactorsNestedDict["TOR"] = {
    "L" : float(bluejays_left) / 100,
    "R" : float(bluejays_right) / 100,
    "B" : float(bluejays_both) / 100
}

driver.close()

#add Excel sheet
my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
park_factors_sheet = wb.create_sheet("PARK FACTORS")
park_factors_sheet.append(('TEAM', 'pFACT B', 'pFACT L', 'pFACT R'))
for key in parkFactorsNestedDict:
    park_factors_sheet.append((key, parkFactorsNestedDict[key]['B'], parkFactorsNestedDict[key]['L'], parkFactorsNestedDict[key]['R']))

wb.save(my_file)