import openpyxl
import sys

wb = openpyxl.Workbook()
ws = wb.active
wb.save('C:\\Users\\brose32\\Documents\\' + sys.argv[1])


import CoversScrape
import fantasyProsWebScrape
import FDptsperminuteScrape
import MinutesScrape
import PaceESPNScrape
import TeamPPGScrape
import GenerateProjections