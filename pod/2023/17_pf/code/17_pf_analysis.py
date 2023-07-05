# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data for PF week.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
# import seaborn as sns

# #Set matplotlib parameters
# from matplotlib import rcParams
# # rcParams['font.family'] = 'sans-serif'
# rcParams['font.sans-serif'] = 'Arial'
# rcParams['font.weight'] = 'bold'
# rcParams['axes.labelsize'] = 12
# rcParams['axes.titlesize'] = 16
# rcParams['axes.linewidth'] = 1.5
# rcParams['axes.labelweight'] = 'bold'
# rcParams['legend.fontsize'] = 10
# rcParams['xtick.major.width'] = 1.5
# rcParams['ytick.major.width'] = 1.5
# rcParams['legend.framealpha'] = 0.0
# rcParams['savefig.dpi'] = 300
# rcParams['savefig.format'] = 'pdf'

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\\..\..\\code\\matchCentre')
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
             8118: 'GIANTS',
             809:'Magic',
             805: 'Mystics',
             803: 'Pulse',
             808: 'Steel',
             802: 'Tactix'}
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118,
                 'Magic': 809,
                 'Mystics': 805,
                 'Pulse': 803,
                 'Steel': 808,
                 'Tactix': 802}

#Create a court positions variable
courtPositions = ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']

#Set base directory for processed data
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

#Read in line-up data
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = 'all',
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular', 'final'],
                                         joined = True, addSquadNames = True)

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','final'],
                                          joined = True, addSquadNames = True)

#Grab unique players from each year
playerData = playerLists.drop_duplicates(subset = ['playerId', 'year'], keep = 'last')[
    ['year', 'playerId', 'firstname', 'surname', 'displayName', 'squadId']
    ].reset_index(drop = True)

# %% NetPoints differential

#Read in team stats from net points era
teamStats_netPointsEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                     fileStem = 'teamStats',
                                                     matchOptions = ['regular', 'final'],
                                                     joined = True, addSquadNames = True)

#Collate net points differential of winning team
netPointsDiff = {'matchId': [], 'year': [], 'roundNo': [], 'matchWinner': [], 'netPointsDiff':[]}

#Loop through match Id
for matchId in teamStats_netPointsEra['matchId'].unique():
    
    #Get scoring variable
    year = teamStats_netPointsEra.loc[teamStats_netPointsEra['matchId'] == matchId,
                                      ]['year'].unique()[0]
    if year < 2020:
        scoreVar = 'goals'
    else:
        scoreVar = 'points'
        
    #Get current match data
    currMatch = teamStats_netPointsEra.loc[teamStats_netPointsEra['matchId'] == matchId,].reset_index(drop = True)
        
    #Identify winning team
    scoreSquad1 = currMatch[scoreVar][0]
    scoreSquad2 = currMatch[scoreVar][1]
    
    #Identify winning squad and netpoints differential
    if scoreSquad1 > scoreSquad2:
        
        #Get NetPoints differential
        netPoints = currMatch['netPoints'][0] - currMatch['netPoints'][1]
        
        #Get winning squad
        winningSquad = currMatch['squadName'][0]
        
    elif scoreSquad1 < scoreSquad2:
        
        #Get NetPoints differential
        netPoints = currMatch['netPoints'][1] - currMatch['netPoints'][0]
        
        #Get winning squad
        winningSquad = currMatch['squadName'][1]
        
    #Append data to dictionary
    netPointsDiff['matchId'].append(matchId)
    netPointsDiff['year'].append(year)
    netPointsDiff['roundNo'].append(currMatch['roundNo'][0])
    netPointsDiff['matchWinner'].append(winningSquad)
    netPointsDiff['netPointsDiff'].append(netPoints)
    
#Convert to dataframe
netPointsDiff_df = pd.DataFrame.from_dict(netPointsDiff)

#Create an absolute differential column
netPointsDiff_df['netPointsDiff_abs'] = np.abs(netPointsDiff_df['netPointsDiff'])
        
# %% Bruce's best game?

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Extract Bruce's key stats
bruceId = 80343
bruceStats = playerStats.loc[playerStats['playerId'] == bruceId,\
                             ][['playerId', 'year', 'roundNo', 'matchType',
                                'gain', 'deflections', 'intercepts', 'penalties',
                                'contactPenalties', 'obstructionPenalties',
                                'netPoints']]
                                
# %% Does anything outside of Super Shots matter?

#Pull in team stats from Super Shot era
teamStats_superShotEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2020, 2021, 2022, 2023],
                                                     fileStem = 'teamStats',
                                                     matchOptions = ['regular', 'final'],
                                                     joined = True, addSquadNames = True)

#Create a dataset related to shot differential between the different categories
#for each match and the winning team and margin
shootingDiff = {'matchId': [], 'year': [], 'roundNo': [], 'winSquad': [], 'lossSquad': [],
                'scoreDiff': [], 'standardDiff': [], 'superDiff': []}

#Loop through match Id
for matchId in teamStats_superShotEra['matchId'].unique():
    
    #Get match data
    currMatch = teamStats_superShotEra.loc[teamStats_superShotEra['matchId'] == matchId,].reset_index(drop = True)
        
    #Identify winning team and index
    scoreSquad1 = currMatch[scoreVar][0]
    scoreSquad2 = currMatch[scoreVar][1]
    if scoreSquad1 > scoreSquad2:
        winInd = 0
        lossInd = 1
    elif scoreSquad1 < scoreSquad2:
        winInd = 1
        lossInd = 0
    else:
        winInd = 'N/A'
        lossInd = 'N/A'
        
    #Check for winner/draw
    if winInd != 'N/A':
        
        #Collate standard and super shot differential
        standardDiff = currMatch['goal1'][winInd] - currMatch['goal1'][lossInd]
        superDiff = currMatch['goal2'][winInd] - currMatch['goal2'][lossInd]
        
        #Calculate margin
        scoreDiff = currMatch['points'][winInd] - currMatch['points'][lossInd]
        
        #Append data
        shootingDiff['matchId'].append(matchId)
        shootingDiff['year'].append(currMatch['year'][0])
        shootingDiff['roundNo'].append(currMatch['roundNo'][0])
        shootingDiff['winSquad'].append(currMatch['squadId'][winInd])
        shootingDiff['lossSquad'].append(currMatch['squadId'][lossInd])
        shootingDiff['scoreDiff'].append(scoreDiff)
        shootingDiff['standardDiff'].append(standardDiff)
        shootingDiff['superDiff'].append(superDiff)
        
#Convert to dataframe
shootingDiff_df = pd.DataFrame.from_dict(shootingDiff)

#Create a boolean of leading Standard and Super Shots
shootingDiff_df['leadStandard'] = [True if shotDiff > 0 else False for shotDiff in shootingDiff_df['standardDiff']]
shootingDiff_df['leadSuper'] = [True if shotDiff > 0 else False for shotDiff in shootingDiff_df['superDiff']]
shootingDiff_df['notLeadStandard'] = [True if shotDiff < 0 else False for shotDiff in shootingDiff_df['standardDiff']]
shootingDiff_df['notLeadSuper'] = [True if shotDiff < 0 else False for shotDiff in shootingDiff_df['superDiff']]

#Identify proportion of matches won by leading Super Shots
winSuper = shootingDiff_df['leadSuper'].sum() / len(shootingDiff_df) * 100
lossSuper = shootingDiff_df['notLeadSuper'].sum() / len(shootingDiff_df) * 100

#Collate wins where the team has lost the standard shots, but lead Super Shots
superWins = shootingDiff_df.loc[(shootingDiff_df['leadStandard'] == False) &
                                (shootingDiff_df['leadSuper'] == True),]

# %% ----- End of 17_pf_analysis.py ----- %% #
