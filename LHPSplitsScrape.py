import sys

from bs4 import BeautifulSoup as soup
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#vs LHP splits past 3 calendar years min 20 PAs
PATH = 'C:\Program Files (x86)\chromedriver.exe'
ops = webdriver.ChromeOptions()
ops.add_argument("--headless")
driver = webdriver.Chrome(PATH, options=ops)

driver.maximize_window()
my_url = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=1&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=player&statgroup=1&startDate=2018-6-21&endDate=2021-6-20&players=&filter=PA%7Cgt%7C20&groupBy=season&sort=-1,1&pageitems=3000&pg=0"
driver.get(my_url)

element = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "td"))
)
print("elements found")

page_soup = soup(driver.page_source, "html.parser")
driver.close()
table_body = page_soup.find("div", {"class" : "table-scroll"}).table.tbody

rows = table_body.findAll("tr")

hitterVsLHPDict = {}

for row in rows:
    batter_data = row.findAll("td")
    #rownum, season, name, team, g, pa, ab, h, 1b, 2b, 3b, hr, r, rbi, bb, ibb, so, hbp, sf, sh, gdp, sb, cs, avg
    if not hitterVsLHPDict.__contains__(batter_data[2].text):
        hitterVsLHPDict[batter_data[2].text] = {
            "NAME" : batter_data[2].text,
            "AB" : float(batter_data[6].text),
            "PA" : float(batter_data[5].text),
            "1B" : float(batter_data[8].text),
            "2B" : float(batter_data[9].text),
            "3B" : float(batter_data[10].text),
            "HR" : float(batter_data[11].text),
            "R" : float(batter_data[12].text),
            "RBI" : float(batter_data[13].text),
            "BB" : float(batter_data[14].text),
            "IBB" : float(batter_data[15].text),
            "HBP" : float(batter_data[17].text),
            "SB" : float(batter_data[21].text)
        }
    else:
        hitterVsLHPDict[batter_data[2].text]["PA"] = hitterVsLHPDict[batter_data[2].text]["PA"] + float(batter_data[5].text)
        hitterVsLHPDict[batter_data[2].text]["AB"] = hitterVsLHPDict[batter_data[2].text]["AB"] + float(
            batter_data[6].text)
        hitterVsLHPDict[batter_data[2].text]["1B"] = hitterVsLHPDict[batter_data[2].text]["1B"] + float(
            batter_data[8].text)
        hitterVsLHPDict[batter_data[2].text]["2B"] = hitterVsLHPDict[batter_data[2].text]["2B"] + float(
            batter_data[9].text)
        hitterVsLHPDict[batter_data[2].text]["3B"] = hitterVsLHPDict[batter_data[2].text]["3B"] + float(
            batter_data[10].text)
        hitterVsLHPDict[batter_data[2].text]["HR"] = hitterVsLHPDict[batter_data[2].text]["HR"] + float(
            batter_data[11].text)
        hitterVsLHPDict[batter_data[2].text]["R"] = hitterVsLHPDict[batter_data[2].text]["R"] + float(
            batter_data[12].text)
        hitterVsLHPDict[batter_data[2].text]["RBI"] = hitterVsLHPDict[batter_data[2].text]["RBI"] + float(
            batter_data[13].text)
        hitterVsLHPDict[batter_data[2].text]["BB"] = hitterVsLHPDict[batter_data[2].text]["BB"] + float(
            batter_data[14].text)
        hitterVsLHPDict[batter_data[2].text]["IBB"] = hitterVsLHPDict[batter_data[2].text]["IBB"] + float(
            batter_data[15].text)
        hitterVsLHPDict[batter_data[2].text]["HBP"] = hitterVsLHPDict[batter_data[2].text]["HBP"] + float(
            batter_data[17].text)
        hitterVsLHPDict[batter_data[2].text]["SB"] = hitterVsLHPDict[batter_data[2].text]["SB"] + float(
            batter_data[21].text)

for key in hitterVsLHPDict:
    hitterVsLHPDict[key]["SLUG"] = (hitterVsLHPDict[key]["1B"] + (hitterVsLHPDict[key]["2B"] * 2) +
                                    (hitterVsLHPDict[key]["3B"] * 3) + (hitterVsLHPDict[key]["HR"] * 4)) / hitterVsLHPDict[key]["AB"]
    hitterVsLHPDict[key]["BB%"] = hitterVsLHPDict[key]["BB"] / hitterVsLHPDict[key]["PA"]
    hitterVsLHPDict[key]["SB/PA"] = hitterVsLHPDict[key]["SB"] / hitterVsLHPDict[key]["PA"]
    hitterVsLHPDict[key]["R/PA"] = hitterVsLHPDict[key]["R"] / hitterVsLHPDict[key]["PA"]
    hitterVsLHPDict[key]["RBI/PA"] = hitterVsLHPDict[key]["RBI"] / hitterVsLHPDict[key]["PA"]

for key in hitterVsLHPDict:
    hitterVsLHPDict[key]["FDproj/PA"] = (hitterVsLHPDict[key]["SLUG"] * 3) + (hitterVsLHPDict[key]["BB%"] * 3) + \
                                         (hitterVsLHPDict[key]["R/PA"] * 3.2) + (hitterVsLHPDict[key]["RBI/PA"] * 3.5) + \
                                         (hitterVsLHPDict[key]["SB/PA"] * 6)
#add to excel sheet
my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
vs_lhp_sheet = wb.create_sheet("LHP 3YR SPLITS")
vs_lhp_sheet.append(("NAME", "FDproj/PA"))
for key in hitterVsLHPDict:
    vs_lhp_sheet.append((key, hitterVsLHPDict[key]["FDproj/PA"]))

wb.save(my_file)