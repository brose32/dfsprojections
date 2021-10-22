import openpyxl
import sys

wb = openpyxl.Workbook()
ws = wb.active
wb.save('C:\\Users\\brose32\\Documents\\' + sys.argv[1])


