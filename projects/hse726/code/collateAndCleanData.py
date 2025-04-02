# -*- coding: utf-8 -*-
"""

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This script collates some data for use in a HSE726 assignment.


"""

# %% Import packages

import pandas as pd
import os
import numpy as np

# %% Set-up

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

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir(os.path.join('..','..','..','code','matchCentre'))
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = os.path.join('..','..','..','data','matchCentre','processed')

#Create dictionary to map squad names to ID's
squadDict = {804: 'Vixens',
             806: 'Swifts',
             807: 'Firebirds',
             8117: 'Lightning',
             810: 'Fever',
             # 8119: 'Magpies',
             801: 'Thunderbirds',
             8118: 'GIANTS',
             9698: 'Mavericks'}
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 # 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118,
                 'Mavericks': 9698}

#Read in team stats for 2024 season


#Read in relevant match centre game data for the 2023 season

#Team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2024],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'],
                                        joined = True, addSquadNames = True)

#Player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2024],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'],
                                          joined = True, addSquadNames = True)

#Player lists
playerList = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2024],
                                         fileStem = 'playerList',
                                         matchOptions = ['regular'],
                                         joined = True, addSquadNames = True)

# %% Sum team stats for the season

#Group and sum team stats
teamStatsSum = teamStats.groupby('squadName').sum(numeric_only = True).reset_index(drop = False)

#Set list of stats to extract
extractStats = ['squadName', 
                'attempt1', 'attempt2', 'goal1', 'goal2', 'goalAttempts',
                'contactPenalties', 'obstructionPenalties', 'penalties',
                'deflectionWithGain', 'deflectionWithNoGain', 'deflections', 'gain',
                'feeds', 'feedWithAttempt', 'generalPlayTurnovers', 'goalAssists',
                'goalsFromCentrePass', 'goalsFromGain', 'goalsFromTurnovers',
                'interceptPassThrown', 'intercepts', 'netPoints', 'pickups',
                'points']

#Extract team stats
teamStatsExtract = teamStatsSum[extractStats]

#Export to file
teamStatsExtract.to_csv(os.path.join('..','outputs','teamStatsSummed_2024.csv'), index = False)

# %% Extract Swifts players stats

#Get the Swifts player stats
swiftsPlayerStats = playerStats.loc[playerStats['squadName'] == 'Swifts',].reset_index(drop = True)

#Create a player name and win/loss column
playerName = []
matchResult = []

#Loop through entries
for ii in swiftsPlayerStats.index:
    
    #Get player id
    playerId = swiftsPlayerStats.iloc[ii]['playerId']
    
    #Get player name and append to list
    playerName.append(playerList.loc[playerList['playerId'] == playerId,
                                     ]['firstname'].unique()[0]+' '+playerList.loc[playerList['playerId'] == playerId,
                                                                                   ]['surname'].unique()[0])
                                                                                   
    #Get match result
    
    #Get match Id
    matchId = swiftsPlayerStats.iloc[ii]['matchId']
    
    #Get vixens and opposition score from team stats
    swiftsScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                                (teamStats['squadName'] == 'Swifts'),
                                ]['points'].values[0]
    oppScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                             (teamStats['squadName'] != 'Swifts'),
                             ]['points'].values[0]
    
    #Determine and append match result
    if swiftsScore > oppScore:
        matchResult.append('win')
    elif swiftsScore < oppScore:
        matchResult.append('loss')
    else:
        matchResult.append('draw')
        
#Append to dataframe
swiftsPlayerStats['playerName'] = playerName
swiftsPlayerStats['matchResult'] = matchResult

#Set list of stats to extract
extractStats = ['playerName', 'squadName', 'oppSquadName', 'roundNo', 'matchResult',
                'attempt1', 'attempt2', 'goal1', 'goal2', 'goalAttempts',
                'badPasses', 'badHands', 'offsides', 'breaks',
                'contactPenalties', 'obstructionPenalties', 'penalties',
                'centrePassReceives', 'secondPhaseReceive', 
                'deflectionWithGain', 'deflectionWithNoGain', 'deflections', 'gain',
                'feeds', 'feedWithAttempt', 'generalPlayTurnovers', 'goalAssists',
                'interceptPassThrown', 'intercepts', 'netPoints', 'pickups',
                'points']
    
#Extract player stats
playerStatsExtract = swiftsPlayerStats[extractStats]

#Export to file
playerStatsExtract.to_csv(os.path.join('..','outputs','swiftsPlayersSeasonStats_2024.csv'), index = False)

# %% Extract Swifts team stats for the season

#Extract Vixens team stats
swiftsTeamStats = teamStats.loc[teamStats['squadName'] == 'Swifts',].reset_index(drop = True)

#Create a win/loss column
matchResult = []

#Loop through entries
for ii in swiftsTeamStats.index:
    
    #Get match Id
    matchId = swiftsTeamStats.iloc[ii]['matchId']
    
    #Get vixens and opposition score from team stats
    swiftsScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                                (teamStats['squadName'] == 'Swifts'),
                                ]['points'].values[0]
    oppScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                             (teamStats['squadName'] != 'Swifts'),
                             ]['points'].values[0]
    
    #Determine and append match result
    if swiftsScore > oppScore:
        matchResult.append('win')
    elif swiftsScore < oppScore:
        matchResult.append('loss')
    else:
        matchResult.append('draw')
        
#Add to dataframe
swiftsTeamStats['matchResult'] = matchResult

#Set list of stats to extract
extractStats = ['squadName', 'oppSquadName', 'roundNo', 'matchResult',
                'attempt1', 'attempt2', 'goal1', 'goal2', 'goalAttempts',
                'contactPenalties', 'obstructionPenalties', 'penalties',
                'deflectionWithGain', 'deflectionWithNoGain', 'deflections', 'gain',
                'feeds', 'feedWithAttempt', 'generalPlayTurnovers', 'goalAssists',
                'goalsFromCentrePass', 'goalsFromGain', 'goalsFromTurnovers',
                'interceptPassThrown', 'intercepts', 'netPoints', 'pickups',
                'points']
    
#Extract vixens team stats
swiftsTeamStatsExtract = swiftsTeamStats[extractStats]

#Export to file
swiftsTeamStatsExtract.to_csv(os.path.join('..','outputs','swiftsTeamSeasonStats_2024.csv'), index = False)

# %% Extract individual player data

#Extract Weston and Mannix stats
westonId = 80577
mannixId = 994213

#Get the players stats
westonPlayerStats = playerStats.loc[playerStats['playerId'] == westonId,].reset_index(drop = True)
mannixPlayerStats = playerStats.loc[playerStats['playerId'] == mannixId,].reset_index(drop = True)

#Set list of stats to extract
extractStats = ['squadName', 'oppSquadName', 'roundNo',
                'attempt1', 'attempt2', 'goal1', 'goal2', 'goalAttempts',
                'badPasses', 'badHands', 'offsides', 'breaks',
                'contactPenalties', 'obstructionPenalties', 'penalties',
                'centrePassReceives', 'secondPhaseReceive', 
                'deflectionWithGain', 'deflectionWithNoGain', 'deflections', 'gain',
                'feeds', 'feedWithAttempt', 'generalPlayTurnovers', 'goalAssists',
                'interceptPassThrown', 'intercepts', 'netPoints', 'pickups',
                'points']

#Extract the stats
westonPlayerStats = westonPlayerStats[extractStats]
mannixPlayerStats = mannixPlayerStats[extractStats]

#Export to file
westonPlayerStats.to_csv(os.path.join('..','outputs','westonSeasonStats_2024.csv'), index = False)
mannixPlayerStats.to_csv(os.path.join('..','outputs','klauSeasonStats_2024.csv'), index = False)


# %% ----- End of collateAndCleanData.py ----- %% #