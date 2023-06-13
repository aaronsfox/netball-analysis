# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 13 SSN match-ups.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import groupby
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
    
# %% Defensive combos

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular','final'],
                                          joined = True, addSquadNames = True)

#Create dictionary to store combos in
defComboData = {'matchId': [], 'year': [], 'roundNo': [], 'squadName': [], 'oppSquadName': [],
                'GK': [], 'GD': [], 'mins': [],
                'gain': [], 'deflections': [], 'deflectionWithGain': [], 'deflectionWithNoGain': [],
                'intercepts': [], 'netPoints': []}

#Loop through match Id's and each squad to identify the most prominent GK/GD combo
for matchId in lineUpData['matchId'].unique():
    
    #Get the two squad Id's from match
    matchSquads = lineUpData.loc[lineUpData['matchId'] == matchId, ]['squadId'].unique()
    
    #Loop through squads
    for squadId in matchSquads:
        
        #Create a series of the GK/GD combos
        
        #Get current squad and match line-ups
        currSquadLineUps = lineUpData.loc[(lineUpData['matchId'] == matchId) &
                                          (lineUpData['squadId'] == squadId),
                                          ].reset_index(drop = True)
        
        #Create GK/GD series and get unique combo
        uniqueDefCombos = pd.Series([str(currSquadLineUps['GK'][ii])+'-'+str(currSquadLineUps['GD'][ii]) for ii in currSquadLineUps.index]).unique()
        
        #Loop through combos and calculate duration on court
        timeOnCourt = []
        for combo in uniqueDefCombos:
            #Check for invalid combo
            if not '-99999' in combo:
                #Get each position
                GK = int(combo.split('-')[0])
                GD = int(combo.split('-')[1])
                #Extract and append duration on court
                timeOnCourt.append(currSquadLineUps.loc[(currSquadLineUps['GK'] == GK) &
                                                        (currSquadLineUps['GD'] == GD),
                                                        ]['duration'].sum())
                
        #Check if time on court is empty indicating no valid combos
        if len(timeOnCourt) > 0:
            
            #Identify most prominent combination
            maxCombo = uniqueDefCombos[timeOnCourt.index(np.max(timeOnCourt))]
            
            #Append match and player data to dictionary
            defComboData['matchId'].append(matchId)
            defComboData['year'].append(currSquadLineUps['year'].unique()[0])
            defComboData['roundNo'].append(currSquadLineUps['roundNo'].unique()[0])
            defComboData['squadName'].append(currSquadLineUps['squadName'].unique()[0])
            defComboData['oppSquadName'].append(currSquadLineUps['oppSquadName'].unique()[0])
            defComboData['GK'].append(playerData.loc[(playerData['year'] == currSquadLineUps['year'].unique()[0]) &
                                                     (playerData['playerId'] == GK),]['firstname'].values[0]+' '+\
                                      playerData.loc[(playerData['year'] == currSquadLineUps['year'].unique()[0]) &
                                                     (playerData['playerId'] == GK),
                                                     ]['surname'].values[0])
            defComboData['GD'].append(playerData.loc[(playerData['year'] == currSquadLineUps['year'].unique()[0]) &
                                                     (playerData['playerId'] == GD),]['firstname'].values[0]+' '+\
                                      playerData.loc[(playerData['year'] == currSquadLineUps['year'].unique()[0]) &
                                                     (playerData['playerId'] == GD),
                                                     ]['surname'].values[0])
            defComboData['mins'].append(np.max(timeOnCourt)/60)
            
            #Grab combined player stats for the defensive combo
            defComboData['gain'].append(playerStats.loc[(playerStats['matchId'] == matchId) &
                                                        (playerStats['playerId'].isin([GK,GD])),
                                                        ]['gain'].sum())
            defComboData['deflections'].append(playerStats.loc[(playerStats['matchId'] == matchId) &
                                                               (playerStats['playerId'].isin([GK,GD])),
                                                               ]['deflections'].sum())
            defComboData['deflectionWithGain'].append(playerStats.loc[(playerStats['matchId'] == matchId) &
                                                                      (playerStats['playerId'].isin([GK,GD])),
                                                                      ]['deflectionWithGain'].sum())
            defComboData['deflectionWithNoGain'].append(playerStats.loc[(playerStats['matchId'] == matchId) &
                                                                      (playerStats['playerId'].isin([GK,GD])),
                                                                      ]['deflectionWithNoGain'].sum())
            defComboData['intercepts'].append(playerStats.loc[(playerStats['matchId'] == matchId) &
                                                              (playerStats['playerId'].isin([GK,GD])),
                                                              ]['intercepts'].sum())
            defComboData['netPoints'].append(playerStats.loc[(playerStats['matchId'] == matchId) &
                                                             (playerStats['playerId'].isin([GK,GD])),
                                                             ]['netPoints'].sum())
            
#Convert to dataframe
defComboData_df = pd.DataFrame.from_dict(defComboData)
        
# %% Housby's form

#Define function to count max run
def max_runs_of_ones(bits):
    maxvalue = 0
    for bit, group in groupby(bits):
        if bit: 
            maxvalue = max(maxvalue,sum(group))
    return maxvalue

#First check the players who have recorded at least 6 NetPoint matches in a row (2018 onwards)

#Create dictionary to store data in
netPointStreak = {'year': [], 'playerName': [], 'netPointStreak': []}

#Loop through years of NetPoints
for year in [2018, 2019, 2020, 2022, 2023]:
    
    #Extract player stats for that year
    currYearPlayerStats = playerStats.loc[playerStats['year'] == year,].reset_index(drop = True)
    
    #Loop through unique player Id's
    for playerId in currYearPlayerStats['playerId'].unique():
        
        #Extract current players NetPoint data
        currPlayerData = currYearPlayerStats.loc[currYearPlayerStats['playerId'] == playerId,
                                                 ][['roundNo', 'netPoints']].reset_index(drop = True)
        
        #Ensure data is sorted by round number
        currPlayerData.sort_values(by = 'roundNo', inplace = True)
        
        #Find matches > 100 NetPoints
        netPointStreak100 = np.multiply(np.array(list(currPlayerData['netPoints'] > 100)), 1)
        
        #Extract the maximum streak
        maxStreak = max_runs_of_ones(netPointStreak100>0)
        
        #Append data to dictionary
        netPointStreak['year'].append(year)
        netPointStreak['playerName'].append(playerData.loc[(playerData['year'] == year) &
                                                           (playerData['playerId'] == playerId),]['firstname'].values[0]+' '+\
                                            playerData.loc[(playerData['year'] == year) &
                                                           (playerData['playerId'] == playerId),
                                                           ]['surname'].values[0])
        netPointStreak['netPointStreak'].append(maxStreak)
        
#Convert to dataframe
netPointStreak_df = pd.DataFrame.from_dict(netPointStreak)

#Get average stats for Housby over the years
housbyId = 999128

#Extract Housby's stats and group by year to average
housbyStatAvgs = playerStats.loc[playerStats['playerId'] == housbyId,
                                 ].groupby('year').mean(numeric_only = True)[[
                                     'centrePassReceives', 'feeds', 'feedWithAttempt', 'goalAssists',
                                     'goalAttempts', 'goalMisses', 'goals', 'goal1', 'goal2',
                                     'points', 'netPoints',]]
                                     
# %% General play turnovers

#Read in team stats for this year
teamStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2023],
                                            fileStem = 'teamStats',
                                            matchOptions = ['regular'],
                                            joined = True, addSquadNames = True)

#Grab average team turnovers per game this year
avgGPTO = teamStats2023.groupby('squadName').mean(numeric_only = True)[['generalPlayTurnovers']]

#Total GPTOs in a game?
totalGPTO = teamStats2023.groupby('matchId').sum(numeric_only = True)[['generalPlayTurnovers']]
matchIDLookUp = teamStats2023[['matchId', 'roundNo', 'squadName']]

# %% Most deflections by a player in a game?

#Extract deflection statistics from player stats over time
deflectionStats = playerStats[['playerId', 'year', 'roundNo', 'matchType', 'deflections', 'deflectionWithGain', 'deflectionWithNoGain']]

#Loop through and get player name and summed deflections
playerName = []
totalDeflections = []
for ii in deflectionStats.index:
    
    #Check for deflections nan
    if np.isnan(deflectionStats.iloc[ii]['deflections']):
        totalDeflections.append(deflectionStats.iloc[ii]['deflectionWithGain']+deflectionStats.iloc[ii]['deflectionWithNoGain'])
    else:
        totalDeflections.append(deflectionStats.iloc[ii]['deflections'])
        
    #Get player name
    playerName.append(playerData.loc[(playerData['year'] == deflectionStats.iloc[ii]['year']) &
                                     (playerData['playerId'] == deflectionStats.iloc[ii]['playerId']),]['firstname'].values[0]+' '+\
                      playerData.loc[(playerData['year'] == deflectionStats.iloc[ii]['year']) &
                                     (playerData['playerId'] == deflectionStats.iloc[ii]['playerId']),
                                     ]['surname'].values[0])
        
#Add to dataframe
deflectionStats['playerName'] = playerName
deflectionStats['totalDeflections'] = totalDeflections
    
# %% Prediction

#Record numbers for the year?

#Read in regular season team stats
teamStatsRegular = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = 'all',
                                               fileStem = 'teamStats',
                                               matchOptions = ['regular'],
                                               joined = True, addSquadNames = True)

#Group by squad name and year to sum various statistics
seasonTotals = teamStatsRegular.groupby(['squadName','year']).sum(numeric_only = True)[[
    'goals', 'goalAttempts', 'goalMisses', 'gain', 'generalPlayTurnovers', 'goal2']]

#Calculate shooting percentage
seasonTotals['shootingPer'] = (seasonTotals['goalAttempts']-seasonTotals['goalMisses']) / seasonTotals['goalAttempts'] * 100

#Check some things out for player stats

#Read in regular season player stats
playerStatsRegular = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = 'all',
                                                 fileStem = 'playerStats',
                                                 matchOptions = ['regular'],
                                                 joined = True, addSquadNames = True)

#Add in player last name
playerName = []
for ii in playerStatsRegular.index:
    playerName.append(playerData.loc[(playerData['year'] == playerStatsRegular.iloc[ii]['year']) &
                                     (playerData['playerId'] == playerStatsRegular.iloc[ii]['playerId']),
                                     ]['surname'].values[0])
playerStatsRegular['playerName'] = playerName

#Group by player Id name and year to sum various statistics
seasonPlayerTotals = playerStatsRegular.groupby(['playerName','year']).sum(numeric_only = True)[[
    'goals', 'goalAttempts', 'goalMisses', 'gain', 'feeds', 'generalPlayTurnovers', 'goal2', 'netPoints']]

#Calculate shooting percentage
seasonPlayerTotals['shootingPer'] = (seasonPlayerTotals['goalAttempts']-seasonPlayerTotals['goalMisses']) / seasonPlayerTotals['goalAttempts'] * 100

# %% ----- End of 13_rd13_analysis.py ----- %% #