# dfsprojections

To get nba Fanduel projections run RunNBAScrapes.py in the terminal with the first argument as the filename of the Excel file to be created and the second as the name of the FanDuel csv file you have downloaded for today's slate.

Currently set up to generate 150 optimized lineups.  run Run.py Note: at this time must change filename manually in NBASetup.py first for Excel file.  CSV file will be created at the filename specified.  These lineups will be placed in a csv file in the same directory as the Python project

Potential bug:  I've noticed that sometimes pandas will not read the Excel values correctly for formula fields as it is specified in the functions parameters if you have the Excel file open, however, if you save and close the Excel file it fixes and will give you a lineup.

***Required Packages***

BeautifulSoup
pip install bs4

Selenium
pip install selenium
*must also install Chrome Webdriver from https://chromedriver.chromium.org/downloads and change the Path to where you place it

PuLP
pip install pulp

openpyxl
pip install openpyxl

etc urllib, requests, pandas, and anything else that is imported that you do not have
