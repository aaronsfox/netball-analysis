# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Short script to extract Super Shot attempt and make numbers for each team
    across the first three years of competition. These are used in the simulation
    paper.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

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

# %% Compile super shot data for each team

#Read in minutes played data for the 2022 regular season
scoreFlowData = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2020, 2021, 2022],
                                            fileStem = 'scoreFlow',
                                            matchOptions = ['regular'])

#Add a year column to each dataset
for year in list(scoreFlowData.keys()):
    scoreFlowData[year]['year'] = [year]*len(scoreFlowData[year])
    

#Concatenate dataframes to one
scoreFlowDataAll = pd.concat([scoreFlowData[year] for year in list(scoreFlowData.keys())]).reset_index(drop = True)

#Drop data from outside of the super shot period based on time
scoreFlowSuper = scoreFlowDataAll.loc[scoreFlowDataAll['periodSeconds'] > 600,].reset_index(drop = True)

#Add a column for make/miss
scoreFlowSuper['shotOutcome'] = [True if scoreFlowSuper['scoreName'][ii] in ['goal', '2pt Goal'] else False for ii in scoreFlowSuper.index]
        

#Group by squad Id and score name and sum
teamSuperCounts = scoreFlowSuper.groupby(['squadId', 'scoreName', 'shotOutcome']).count()['matchId'].reset_index(drop = False)

#Rename column
teamSuperCounts.rename(columns = {'matchId': 'shotCount'}, inplace = True)

#Rename squad Id
teamSuperCounts['squadId'].replace(squadDict, inplace = True)

#Sort by team name
teamSuperCounts.sort_values(by = 'squadId', inplace = True)

#Do all of the above but for opposition squad Id

#Group by squad Id and score name and sum
oppSuperCounts = scoreFlowSuper.groupby(['oppSquadId', 'scoreName', 'shotOutcome']).count()['matchId'].reset_index(drop = False)

#Rename column
oppSuperCounts.rename(columns = {'matchId': 'shotCount'}, inplace = True)

#Rename squad Id
oppSuperCounts['oppSquadId'].replace(squadDict, inplace = True)

#Sort by team name
oppSuperCounts.sort_values(by = 'oppSquadId', inplace = True)

#Clean up super shot scoreflow for export

#Rename squad Id for consistency
scoreFlowSuper['squadId'].replace(squadDict, inplace = True)

#Drop player Id for non-identifiable data
scoreFlowSuper.drop('playerId', axis = 1, inplace = True)

# %% Export data

#Export to csv
teamSuperCounts.to_csv('..\\outputs\\teamSuperCounts.csv', index = False)
oppSuperCounts.to_csv('..\\outputs\\oppSuperCounts.csv', index = False)
scoreFlowSuper.to_csv('..\outputs\\scoreFlowSuper.csv', index = False)

# %%% ----- End of extractSuperShotNumbers.py -----