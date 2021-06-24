import sys

from bs4 import BeautifulSoup as soup
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#vs RHP splits past 3 calendar years min 20 PAs
PATH = 'C:\Program Files (x86)\chromedriver.exe'
ops = webdriver.ChromeOptions()
#ops.add_argument("--headless")
driver = webdriver.Chrome(PATH, options=ops)

driver.maximize_window()
my_url = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=2&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=player&statgroup=1&startDate=2018-6-21&endDate=2021-6-20&players=&filter=PA%7Cgt%7C20&groupBy=season&sort=-1,1&pageitems=300&pg=0"
driver.get(my_url)

#driver.close()

ad = WebDriverWait(driver,10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "ezmob-footer-close"))
)
ad.click()

current_page = 1
page_total = 1000
hitterVsRHPDict = {}
iters = 0
while current_page < page_total:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "align-right"))
    )
    print("elements found")

    page_soup = soup(driver.page_source, "html.parser")
    iters += 1
    print("loop", iters)
    page_total = int(page_soup.find("span", {"class": "table-control-total"}).text.strip())
    current_page = int(page_soup.find("input", {"class": "table-control-page"}).get("value"))
    print("page total is", page_total)
    print("current page is", current_page)
    table_body = page_soup.find("div", {"class": "table-scroll"}).table.tbody
    rows = table_body.findAll("tr")
    for row in rows:
        batter_data = row.findAll("td")
        #rownum, season, name, team, g, pa, ab, h, 1b, 2b, 3b, hr, r, rbi, bb, ibb, so, hbp, sf, sh, gdp, sb, cs, avg
        if not hitterVsRHPDict.__contains__(batter_data[2].text):
            hitterVsRHPDict[batter_data[2].text] = {
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
            hitterVsRHPDict[batter_data[2].text]["PA"] = hitterVsRHPDict[batter_data[2].text]["PA"] + float(batter_data[5].text)
            hitterVsRHPDict[batter_data[2].text]["AB"] = hitterVsRHPDict[batter_data[2].text]["AB"] + float(
                batter_data[6].text)
            hitterVsRHPDict[batter_data[2].text]["1B"] = hitterVsRHPDict[batter_data[2].text]["1B"] + float(
                batter_data[8].text)
            hitterVsRHPDict[batter_data[2].text]["2B"] = hitterVsRHPDict[batter_data[2].text]["2B"] + float(
                batter_data[9].text)
            hitterVsRHPDict[batter_data[2].text]["3B"] = hitterVsRHPDict[batter_data[2].text]["3B"] + float(
                batter_data[10].text)
            hitterVsRHPDict[batter_data[2].text]["HR"] = hitterVsRHPDict[batter_data[2].text]["HR"] + float(
                batter_data[11].text)
            hitterVsRHPDict[batter_data[2].text]["R"] = hitterVsRHPDict[batter_data[2].text]["R"] + float(
                batter_data[12].text)
            hitterVsRHPDict[batter_data[2].text]["RBI"] = hitterVsRHPDict[batter_data[2].text]["RBI"] + float(
                batter_data[13].text)
            hitterVsRHPDict[batter_data[2].text]["BB"] = hitterVsRHPDict[batter_data[2].text]["BB"] + float(
                batter_data[14].text)
            hitterVsRHPDict[batter_data[2].text]["IBB"] = hitterVsRHPDict[batter_data[2].text]["IBB"] + float(
                batter_data[15].text)
            hitterVsRHPDict[batter_data[2].text]["HBP"] = hitterVsRHPDict[batter_data[2].text]["HBP"] + float(
                batter_data[17].text)
            hitterVsRHPDict[batter_data[2].text]["SB"] = hitterVsRHPDict[batter_data[2].text]["SB"] + float(
                batter_data[21].text)
    if current_page != page_total:
        next_page = driver.find_element_by_class_name("next")
        next_page.click()
driver.close()
for key in hitterVsRHPDict:
    hitterVsRHPDict[key]["SLUG"] = (hitterVsRHPDict[key]["1B"] + (hitterVsRHPDict[key]["2B"] * 2) +
                                    (hitterVsRHPDict[key]["3B"] * 3) + (hitterVsRHPDict[key]["HR"] * 4)) / hitterVsRHPDict[key]["AB"]
    hitterVsRHPDict[key]["BB%"] = hitterVsRHPDict[key]["BB"] / hitterVsRHPDict[key]["PA"]
    hitterVsRHPDict[key]["SB/PA"] = hitterVsRHPDict[key]["SB"] / hitterVsRHPDict[key]["PA"]
    hitterVsRHPDict[key]["R/PA"] = hitterVsRHPDict[key]["R"] / hitterVsRHPDict[key]["PA"]
    hitterVsRHPDict[key]["RBI/PA"] = hitterVsRHPDict[key]["RBI"] / hitterVsRHPDict[key]["PA"]

for key in hitterVsRHPDict:
    hitterVsRHPDict[key]["FDproj/PA"] = (hitterVsRHPDict[key]["SLUG"] * 3) + (hitterVsRHPDict[key]["BB%"] * 3) + \
                                         (hitterVsRHPDict[key]["R/PA"] * 3.2) + (hitterVsRHPDict[key]["RBI/PA"] * 3.5) + \
                                         (hitterVsRHPDict[key]["SB/PA"] * 6)
#add to excel sheet
my_file = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
wb = openpyxl.load_workbook(my_file)
vs_rhp_sheet = wb.create_sheet("RHP 3YR SPLITS")
vs_rhp_sheet.append(("NAME", "FDproj/PA"))
for key in hitterVsRHPDict:
    vs_rhp_sheet.append((key, hitterVsRHPDict[key]["FDproj/PA"]))

wb.save(my_file)

print("RHP splits done")