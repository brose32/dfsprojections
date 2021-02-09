# dfsprojections

To get nba Fanduel projections run RunNBAScrapes.py in the terminal with the first argument as the filename of the Excel file to be created.

To create an optimized lineup run Run.py Note: at this time must change filename manually in NBASetup.py first for Excel file.  CSV file will be created at the filename specified.  

Potential bug:  I've noticed that sometimes pandas will not read the Excel values correctly for formula fields as it is specified however, if you save and close the Excel file it fixes and will give you a lineup.
