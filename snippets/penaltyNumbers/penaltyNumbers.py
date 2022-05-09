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

#Set base directory for processed data
baseDir = '..\\..\\data\\matchCentre\\processed'

# %% Collate data

#Bring in team stats from Super Netball regular seasons
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2017, 2018, 2019, 2020, 2021, 2022],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'])

#Collate and display total penalties from first 7 rounds across years
for year in list(teamStats.keys()):
    #Get total penalties
    nPenalties = teamStats[year].loc[teamStats[year]['roundNo'] <= 7,
                                     ].sum()['penalties']
    #Get contact penalties
    nContact = teamStats[year].loc[teamStats[year]['roundNo'] <= 7,
                                   ].sum()['contactPenalties']
    #Get obstruction penalties
    nObstruction = teamStats[year].loc[teamStats[year]['roundNo'] <= 7,
                                       ].sum()['obstructionPenalties']
    #Print output
    print(f'In {year}: {nPenalties} total penalties; {nContact} contact penalties; {nObstruction} obstruction penalties')

#Get average number of penalties per game per year and display
for year in list(teamStats.keys()):
    #Get mean
    meanPenalties = teamStats[year].groupby('matchId').sum()['penalties'].mean()
    #Print output
    print(f'In {year}: {np.round(meanPenalties,2)} average penalties')
    
#Most and least penalised match each year
for year in list(teamStats.keys()):
    #Get max and min for year
    maxPenalties = teamStats[year].groupby('matchId').sum()['penalties'].max()
    minPenalties = teamStats[year].groupby('matchId').sum()['penalties'].min()
    #Get match Id for max and min
    maxMatchId = teamStats[year].groupby('matchId').sum()['penalties'][teamStats[year].groupby('matchId').sum()['penalties'] == maxPenalties].index[0]
    minMatchId = teamStats[year].groupby('matchId').sum()['penalties'][teamStats[year].groupby('matchId').sum()['penalties'] == minPenalties].index[0]
    #Get max and min by type
    maxContact = teamStats[year].groupby('matchId').sum()['contactPenalties'][maxMatchId]
    minContact = teamStats[year].groupby('matchId').sum()['contactPenalties'][minMatchId]
    maxObstruction = teamStats[year].groupby('matchId').sum()['obstructionPenalties'][maxMatchId]
    minObstruction = teamStats[year].groupby('matchId').sum()['obstructionPenalties'][minMatchId]
    #Print output
    print(f'In {year}: Max penalties in match = {maxPenalties} with {maxContact} contact & {maxObstruction} obstruction penalties')
    print(f'In {year}: Min penalties in match = {minPenalties} with {minContact} contact & {minObstruction} obstruction penalties')

# %% ----- End of penaltyNumbers.py -----