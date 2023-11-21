import openpyxl
import sys

wb = openpyxl.Workbook()
ws = wb.active
wb.save('C:\\Users\\brose32\\Documents\\' + sys.argv[1])


import CoversScrape
print('covers')
import DKFantasyProsWebScrape
print('dvoa')
import DKptsperminuteScrape
import PaceESPNScrape
print('pace')
import TeamPPGScrape
print('ppg')
import dkNbaOwnershipScrape
print('ownership')
import GenerateDKNBAProjections