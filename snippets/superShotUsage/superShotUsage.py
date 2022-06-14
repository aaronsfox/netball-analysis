# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to collate info on Super Shot usage and win/loss.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\data\\matchCentre\\processed'

#Create dictionary to map squad names to ID's
squadDict = {804: 'Vixens',
             806: 'Swifts',
             807: 'Firebirds',
             8117: 'Lightning',
             810: 'Fever',
             8119: 'Magpies',
             801: 'Thunderbirds',
             8118: 'GIANTS'}
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118}

# %% Collate data

#Get team stats from regular season Super Shot era
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2020, 2021, 2022],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'])

#Set up dictionary to store data in
superShotData = {'matchId': [], 'year': [], 'roundNo': [],
                 'squadId': [], 'oppSquadId': [],
                 'superShotMakes': [],
                 'margin': [], 'result': []}

#Loop through years
for year in teamStats.keys():
    
    #Loop through match data
    for dataInd in teamStats[year].index:
        
        #Get details
        matchId = teamStats[year]['matchId'][dataInd]
        squadId = teamStats[year]['squadId'][dataInd]
        oppSquadId = teamStats[year]['oppSquadId'][dataInd]
        roundNo = teamStats[year]['roundNo'][dataInd]
        
        #Extract team data for super shot makes and attempts
        superMakes = teamStats[year]['goal2'][dataInd]
        
        #Extract team and opponent score
        teamScore = teamStats[year]['points'][dataInd]
        oppScore = teamStats[year].loc[(teamStats[year]['matchId'] == matchId) &
                                       (teamStats[year]['oppSquadId'] == squadId),
                                       ]['points'].values[0]
        
        #Identify team relative margin
        margin = teamScore - oppScore
        
        #Identify match result
        if margin > 0:
            result = 'win'
        elif margin < 0:
            result = 'loss'
        else:
            result = 'draw'
            
        #Append to dictionary
        superShotData['matchId'].append(matchId)
        superShotData['year'].append(year)
        superShotData['roundNo'].append(roundNo)
        superShotData['squadId'].append(squadId)
        superShotData['oppSquadId'].append(oppSquadId)
        superShotData['superShotMakes'].append(superMakes)
        superShotData['margin'].append(margin)
        superShotData['result'].append(result)
        
#Convert to dataframe
superShotData_df = pd.DataFrame.from_dict(superShotData)

#Replace squad Id with names
superShotData_df['squadId'].replace(squadDict, inplace = True)

#Drop any draws
superShotData_df = superShotData_df.loc[superShotData_df['result'].isin(['win','loss'])] ]

# %% Visualise data

# #Create facet grid
# g = sns.FacetGrid(superShotData_df,
#                   col = 'squadId', col_wrap = 4,
#                   sharex = False, sharey = True)

# #Map the point plt to the grid
# g.map_dataframe(sns.pointplot,
#                 x = 'year', y = 'superShotMakes',
#                 join = False, dodge = 0.25,
#                 hue = 'result', palette = 'viridis',
#                 ci = 'sd', capsize = 0.1)


# #Map the stripplot to the grid
# g.map_dataframe(sns.stripplot,
#                 x = 'year', y = 'superShotMakes',
#                 dodge = 0.25, alpha = 0.3,
#                 hue = 'result', palette = 'viridis',
#                 zorder = 0)

# #Add legend
# plt.legend()

# #Fix legend
# ax = plt.gca()
# h,l = ax.get_legend_handles_labels()
# plt.legend(h[0:2],
#            l[0:2])

#Save data
superShotData_df.to_excel('superShotMakes_byWinLoss.xlsx')

    
# %% ----- End of superShotUsage.py -----