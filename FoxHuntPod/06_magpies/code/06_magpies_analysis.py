# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 6 Thunderbirds match-up for
    podcast.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
# import matplotlib.pyplot as plt
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
os.chdir('..\\..\..\\code\\matchCentre')
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
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118}

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Key numbers that jumped out

#Reviewed team stats spreadsheets
#Lost the turnover count again - second week in a row with +20 turnovers
#Outgained by Magpies 12-9; gain to goal percentage in Magpies favour 75%-67%
#Missed goals in first 3 quarters 12 to 5 with Vixens having more
    
#Pull in season team stats to check some things
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]

#Get Vixens 2022 stats
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]

# %% Magpies turnovers and missed shots

#Reviewed team stats spreadsheet
#17 turnovers, below the 23+ in losses
#Vixens < 10 gains now in both of their losses

#Get Magpies stats
magpiesTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Magpies'],]

# %% Pressure around the circle

#Reviewed player stats for Brazill, Ward and Mentor
#A decent chunk of contact penalties & deflections
#Physicality of match-ups led to 'uncomfortableness'

# %% Replacing Kate Eddy?

#Set Eddy id
eddyId = 1001701

#Pull in season player stats to check some things
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'])
playerStats_2022 = playerStats_2022[2022]

#Calculate player averages
playerStatAverages_2022 = playerStats_2022.groupby('playerId').mean().reset_index(drop = False)

#Extract Eddy's data
eddysAverages_2022 = playerStatAverages_2022.loc[playerStatAverages_2022['playerId'] == eddyId,]

#Review Kelsey Browne's stats for the year in the context of this match

#Set Browne id
browneId = 80575

#Extract player stats
brownePlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == browneId,]

# %% How is Wallam going?

#Import player list to make this easier
playerList_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular'])
playerList_2022 = playerList_2022[2022]

#Set Wallam id
wallamId = playerList_2022.loc[playerList_2022['surname'] == 'Wallam']['playerId'].unique()[0]

#Extract Wallam player stats
wallamPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == wallamId,]

# %% Are the Firebirds still the most penalised team?

#Average out team stats to review this
avgTeamStats_2022 = teamStats_2022.groupby('squadId').mean().reset_index(drop = False)

#Replace squad Id's with names for ease of reading
avgTeamStats_2022['squadId'].replace(squadDict, inplace = True)

#Collate Firebirds stats across the year
firebirdsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Firebirds'],]

#Review gains to penalty ratio for Bakewell-Doran

#Take out gains and penalties from player stats dataframe
gainsPen = playerStats_2022[['playerId','gain','penalties']]

#Get stat totals by player id
gainsPenSum = gainsPen.groupby('playerId').sum().reset_index(drop = False)

#Create a penalties to gains ratio
gainsPenSum['ratio'] = gainsPenSum['penalties'] / gainsPenSum['gain']

#Extract display names for unique player Id's
playerId = []
displayName = []

#Loop through years
for year in list(playerList_2022.keys()):
    
    #Get unique player Id's
    playerIds = playerList_2022['playerId'].unique()
    
    #Loop through Ids
    for pId in playerIds:
        
        #Check if in list already
        if pId not in playerId:
            
            #Extract and append
            playerId.append(pId)
            displayName.append(playerList_2022.loc[playerList_2022['playerId'] == pId,
                                                    ['displayName']]['displayName'].unique()[0])
    
#Convert to player Id to name dictionary
playerIdDict = dict(zip(playerId, displayName))

#Replace player Id's with names
gainsPenSum.replace(playerIdDict, inplace = True)

# %% Fan questions

#Players getting across positions

#Get the line-ups data for ANZC/SSN
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = 'all',
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular', 'final'])

#Concatenate the dataframes together
lineUpDataAll = pd.concat([lineUpData[year] for year in list(lineUpData.keys())])
lineUpDataAll.reset_index(drop = True, inplace = True)

#Get all of the players across the competition years
playerListData = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = 'all',
                                             fileStem = 'playerList',
                                             matchOptions = ['regular', 'final'])

#Extract display names for unique player Id's
playerId = []
displayName = []

#Loop through years
for year in list(playerListData.keys()):
    
    #Get unique player Id's
    playerIds = playerListData[year]['playerId'].unique()
    
    #Loop through Ids
    for pId in playerIds:
        
        #Check if in list already
        if pId not in playerId:
            
            #Extract and append
            playerId.append(pId)
            
            #Combine first name and surname
            nameToTake = playerListData[year].loc[playerListData[year]['playerId'] == pId,
                                                            ['firstname']]['firstname'].unique()[0] + ' ' + \
                playerListData[year].loc[playerListData[year]['playerId'] == pId,
                                                                ['surname']]['surname'].unique()[0]
                
            #Append
            displayName.append(nameToTake)
    
#Convert to player Id to name dictionary
playerIdDict = dict(zip(playerId, displayName))

#Create dictionary to store values in
posCheckDict = {'playerId': [],
                'GS': [], 'GS_duration': [],
                'GA': [], 'GA_duration': [],
                'WA': [], 'WA_duration': [],
                'C': [], 'C_duration': [],
                'WD': [], 'WD_duration': [],
                'GD': [], 'GD_duration': [],
                'GK': [], 'GK_duration': []}

#Need to exclude first 4 rounds of 2015 ANZC season due to errors in positional allocation
lineUpDataClean = lineUpDataAll.loc[(~lineUpDataAll['matchId'].astype("string").str.startswith('956301')) &
                                    (~lineUpDataAll['matchId'].astype("string").str.startswith('956302')) &
                                    (~lineUpDataAll['matchId'].astype("string").str.startswith('956303')) &
                                    (~lineUpDataAll['matchId'].astype("string").str.startswith('956304')),]

#Loop through player Ids and identify the positions they've played
for playerId in list(playerIdDict.keys()):
    
    #Append player Id to dictionary
    posCheckDict['playerId'].append(playerId)
    
    #Loop through positions
    for courtPos in ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']:
    
        #Do initial check
        if len(lineUpDataClean.loc[lineUpDataClean[courtPos] == playerId,]) == 0:
            
            #Set position to false and zero duration
            posCheckDict[f'{courtPos}'].append(False)
            posCheckDict[f'{courtPos}_duration'].append(0)
            
        else:
            
            #Check duration in mins
            durationMins = lineUpDataClean.loc[lineUpDataClean[courtPos] == playerId,]['duration'].sum() / 60
            
            if durationMins >= 120:
            
                #Set position to true and append duration
                posCheckDict[f'{courtPos}'].append(True)
                posCheckDict[f'{courtPos}_duration'].append(durationMins)
                
            else:
                
                #Set position to false and append duration
                posCheckDict[f'{courtPos}'].append(False)
                posCheckDict[f'{courtPos}_duration'].append(durationMins)
                    
            
#Convert to dataframe
posCheckData = pd.DataFrame.from_dict(posCheckDict)

#Sum the number of positions each player has played in
posCheckData['posCount'] = [sum(posCheckData.iloc[playerInd][['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']].to_list()) for playerInd in range(len(posCheckData))]

#Replace player Id's with names
posCheckData['playerId'].replace(playerIdDict, inplace = True)

# %% Predictions

#Review Vixens quarter by quarter team stats from this year
teamPeriodStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2022],
                                                   fileStem = 'teamPeriodStats',
                                                   matchOptions = ['regular'])
teamPeriodStats_2022 = teamPeriodStats_2022[2022]

#Get Vixens 2022 period stats
vixensTeamPeriodStats_2022 = teamPeriodStats_2022.loc[teamPeriodStats_2022['squadId'] == squadNameDict['Vixens'],]
vixensTeamPeriodStats_2022.sort_values(by = 'points', inplace = True)

# %%% ----- End of 06_magpies_analysis.py -----