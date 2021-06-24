import sys
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
wb.save('C:\\Users\\brose32\\Documents\\' + sys.argv[1])

import ballparkFactorScrape
import probablePitchersScrape
import bullpenFactorScrape