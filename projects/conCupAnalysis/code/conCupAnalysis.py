# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Short script to review some data from recent international matches. Focus points:
        - Penalties in concup games
    
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

# #Create dictionary to map squad names to ID's
# squadDict = {804: 'Vixens',
#              806: 'Swifts',
#              807: 'Firebirds',
#              8117: 'Lightning',
#              810: 'Fever',
#              8119: 'Magpies',
#              801: 'Thunderbirds',
#              8118: 'GIANTS'}
# squadNameDict = {'Vixens': 804,
#                  'Swifts': 806,
#                  'Firebirds': 807,
#                  'Lightning': 8117,
#                  'Fever': 810,
#                  'Magpies': 8119,
#                  'Thunderbirds': 801,
#                  'GIANTS': 8118}

# %% Review international competition data

#Load in team stats
teamStatsData = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2014, 2015, 2016, 2017, 2018,
                                                     2019, 2021, 2022],
                                            fileStem = 'teamStats',
                                            matchOptions = ['international'])

# %% Collate total penalties in international matches

#Create dictionary to store data in
penaltiesDataDict = {'year': [],
                     'matchId': [],
                     'compType': [],
                     'totalPenalties': []}

#Loop through years
for year in list(teamStatsData.keys()):
    
    #Group by match ID and get total penalties
    totalPenalties = teamStatsData[year].groupby(['matchId']).sum()['penalties']
    
    #Set in dictionary
    for matchId in list(totalPenalties.index):
        #Get and append relevant data
        penaltiesDataDict['year'].append(year)
        penaltiesDataDict['matchId'].append(matchId)
        penaltiesDataDict['compType'].append(teamStatsData[year].loc[teamStatsData[year]['matchId'] == matchId,]['compType'].unique()[0])
        penaltiesDataDict['totalPenalties'].append(totalPenalties[matchId])

#Convert to dataframe
penaltiesData = pd.DataFrame.from_dict(penaltiesDataDict)
        
# %% Collate team penalties across matches

#Create dictionary to store data in
teamPenaltiesDataDict = {'year': [],
                         'matchId': [],
                         'squadId': [],
                         'compType': [],
                         'totalPenalties': []}

#Loop through years
for year in list(teamStatsData.keys()):
    
    #Group by match ID and get total penalties
    totalPenalties = teamStatsData[year].groupby(['matchId','squadId']).sum()['penalties'].reset_index(drop = False)
    
    #Set in dictionary
    for ii in list(totalPenalties.index):
        #Get and append relevant data
        teamPenaltiesDataDict['year'].append(year)
        teamPenaltiesDataDict['matchId'].append(int(totalPenalties.iloc[ii]['matchId']))
        teamPenaltiesDataDict['squadId'].append(int(totalPenalties.iloc[ii]['squadId']))
        teamPenaltiesDataDict['compType'].append(teamStatsData[year].loc[teamStatsData[year]['matchId'] == totalPenalties.iloc[ii]['matchId'],]['compType'].unique()[0])
        teamPenaltiesDataDict['totalPenalties'].append(totalPenalties.iloc[ii]['penalties'])

#Convert to dataframe
teamPenaltiesData = pd.DataFrame.from_dict(teamPenaltiesDataDict)

# %%% ----- End of conCupAnalysis.py -----