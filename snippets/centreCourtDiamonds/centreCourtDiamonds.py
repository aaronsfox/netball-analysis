# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to check out statistics for potential Diamonds selections
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Create dictionary to map squad names to ID's
squadDict = {804: 'Vixens',
             806: 'Swifts',
             807: 'Firebirds',
             8117: 'Lightning',
             810: 'Fever',
             8119: 'Magpies',
             801: 'Thunderbirds',
             8118: 'GIANTS'}

#Create dictionary to map player names to
playerDict = {991901: 'Moloney',
              80701: 'Price',
              80575: 'Browne',
              80299: 'Brazill',
              80574: 'Hadley',
              80833: 'Ravaillion'
              }

#Set base directory for processed data
baseDir = '..\\..\\data\\matchCentre\\processed'

# %% Collate data

#Bring in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2022],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'])
playerStats = playerStats[2022]

#Get total stats across players
totalStats = playerStats.groupby('playerId').sum().reset_index(drop = False)

#Get maximum stats across players
maxStats = playerStats.groupby('playerId').max().reset_index(drop = False)

#Extract relevant players and statistics

#Get list of player Id's
relevantPlayerIds = list(playerDict.keys())

#Totals
#Grab the data
relevantTotalStats = totalStats.loc[totalStats['playerId'].isin(relevantPlayerIds),
                                    ['playerId', 'feeds', 'feedWithAttempt', 'intercepts',
                                     'deflections', 'deflectionWithGain', 'generalPlayTurnovers']]
#Replace with dictionary values
relevantTotalStats.replace(playerDict, inplace = True)
#Print to file
relevantTotalStats.to_excel('seasonTotals.xlsx', index = False)

#Max in game
relevantMaxStats = maxStats.loc[maxStats['playerId'].isin(relevantPlayerIds),
                                ['playerId', 'feeds', 'feedWithAttempt', 'intercepts',
                                 'deflections', 'deflectionWithGain', 'generalPlayTurnovers']]
#Replace with dictionary values
relevantMaxStats.replace(playerDict, inplace = True)
#Print to file
relevantMaxStats.to_excel('seasonMaxInGame.xlsx', index = False)

#Per 60 minutes playing time
#Get totals
relevantPerStats = totalStats.loc[totalStats['playerId'].isin(relevantPlayerIds),
                                  ['playerId', 'feeds', 'feedWithAttempt', 'intercepts',
                                   'deflections', 'deflectionWithGain', 'generalPlayTurnovers',
                                   'minutesPlayed']]
#Normalise to per 60 across columns
for stat in ['feeds', 'feedWithAttempt', 'intercepts', 'deflections', 'deflectionWithGain', 'generalPlayTurnovers']:
    relevantPerStats[stat] = relevantPerStats[stat] / (relevantPerStats['minutesPlayed'] / 60)
#Replace with dictionary values
relevantPerStats.replace(playerDict, inplace = True)
#Print to file
relevantPerStats.to_excel('per60Played.xlsx', index = False)

# %% ----- End of centreCourtDiamonds.py -----