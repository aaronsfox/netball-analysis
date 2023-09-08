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

#Read in team stats for 2023 season


#Read in relevant match centre game data for the 2023 season

#Team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2023],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'],
                                        joined = True, addSquadNames = True)

#Player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2023],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'],
                                          joined = True, addSquadNames = True)

#Player lists
playerList = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2023],
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
teamStatsExtract.to_csv('..\\outputs\\teamStatsSummed.csv', index = False)

# %% Extract Vixens players stats

#Get the Vixens player stats
vixensPlayerStats = playerStats.loc[playerStats['squadName'] == 'Vixens',
                                    ].reset_index(drop = True)

#Create a player name and win/loss column
playerName = []
matchResult = []

#Loop through entries
for ii in vixensPlayerStats.index:
    
    #Get player id
    playerId = vixensPlayerStats.iloc[ii]['playerId']
    
    #Get player name and append to list
    playerName.append(playerList.loc[playerList['playerId'] == playerId,
                                     ]['firstname'].unique()[0]+' '+playerList.loc[playerList['playerId'] == playerId,
                                                                                   ]['surname'].unique()[0])
                                                                                   
    #Get match result
    
    #Get match Id
    matchId = vixensPlayerStats.iloc[ii]['matchId']
    
    #Get vixens and opposition score from team stats
    vixensScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                                (teamStats['squadName'] == 'Vixens'),
                                ]['points'].values[0]
    oppScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                             (teamStats['squadName'] != 'Vixens'),
                             ]['points'].values[0]
    
    #Determine and append match result
    if vixensScore > oppScore:
        matchResult.append('win')
    elif vixensScore < oppScore:
        matchResult.append('loss')
    else:
        matchResult.append('draw')
        
#Append to dataframe
vixensPlayerStats['playerName'] = playerName
vixensPlayerStats['matchResult'] = matchResult

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
playerStatsExtract = vixensPlayerStats[extractStats]

#Export to file
playerStatsExtract.to_csv('..\\outputs\\vixensPlayersSeasonStats.csv', index = False)

# %% Extract Vixens team stats for the season

#Extract Vixens team stats
vixensTeamStats = teamStats.loc[teamStats['squadName'] == 'Vixens',
                                ].reset_index(drop = True)

#Create a win/loss column
matchResult = []

#Loop through entries
for ii in vixensTeamStats.index:
    
    #Get match Id
    matchId = vixensTeamStats.iloc[ii]['matchId']
    
    #Get vixens and opposition score from team stats
    vixensScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                                (teamStats['squadName'] == 'Vixens'),
                                ]['points'].values[0]
    oppScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                             (teamStats['squadName'] != 'Vixens'),
                             ]['points'].values[0]
    
    #Determine and append match result
    if vixensScore > oppScore:
        matchResult.append('win')
    elif vixensScore < oppScore:
        matchResult.append('loss')
    else:
        matchResult.append('draw')
        
#Add to dataframe
vixensTeamStats['matchResult'] = matchResult

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
vixensTeamStatsExtract = vixensTeamStats[extractStats]

#Export to file
vixensTeamStatsExtract.to_csv('..\\outputs\\vixensTeamSeasonStats.csv', index = False)

# %% Extract individual player data

#Extract Sterling and Klau stats
sterlingId = 80830
klauId = 998404

#Get the players stats
sterlingPlayerStats = playerStats.loc[playerStats['playerId'] == sterlingId,
                                      ].reset_index(drop = True)
klauPlayerStats = playerStats.loc[playerStats['playerId'] == klauId,
                                  ].reset_index(drop = True)

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
sterlingExtractStats = sterlingPlayerStats[extractStats]
klauExtractStats = klauPlayerStats[extractStats]

#Export to file
sterlingExtractStats.to_csv('..\\outputs\\sterlingSeasonStats.csv', index = False)
klauExtractStats.to_csv('..\\outputs\\klauSeasonStats.csv', index = False)


# %% ----- End of collateAndCleanData.py ----- %% #