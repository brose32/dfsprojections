# dfsprojections

To get nba Fanduel projections run RunNBAScrapes.py in the terminal with the first argument as the filename of the Excel file to be created and the second as the name of the FanDuel csv file you have downloaded for today's slate.

Currently set up to generate 150 optimized lineups.  run Run.py Note: at this time must change filename manually in NBASetup.py first for Excel file.  CSV file will be created at the filename specified.  These lineups will be placed in a csv file in the same directory as the Python project. See lineups.csv for example output file.  Copy and paste the lineups into Fanduel csv upload template

For late swaptimizer run RunLateSwaptimizer.py in the terminal

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

CPLEX
pip install docplex

etc urllib, requests, pandas, and anything else that is imported that you do not have
