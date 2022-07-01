# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Script to compile players 'eligible' for team of the season
    Eligibility criteria:
        - Played at least one-third of available season time (i.e. 33% of 14 * 60)
        - Played at least one-third of their time in a given position
    
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

# %% Compile list of players meeting conditions

#Read in minutes played data for the 2022 regular season
minutesPlayed = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2022],
                                            fileStem = 'minutesPlayed',
                                            matchOptions = ['regular'])
minutesPlayed = minutesPlayed[2022]

#Group by player Id and sum for minutes played
groupedMinutesPlayed = minutesPlayed.groupby('playerId').sum().reset_index(drop = False)

#Drop un-useful variables
groupedMinutesPlayed.drop(['matchId', 'squadId', 'oppSquadId', 'roundNo', 'gameNo'],
                          axis = 1, inplace = True)

#Create dictionary with player Id's and details
playerIdDict = {'playerId': [], 'squadId': [], 'firstName': [], 'surname': [], 'fullName': []}

#Read in player data
playerList = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2022],
                                         fileStem = 'playerList',
                                         matchOptions = ['regular'])
playerList = playerList[2022]

#Get unique player Id's
playerIds = playerList['playerId'].unique()
    
#Loop through Ids
for pId in playerIds:
    
    #Check if in list already
    if pId not in playerIdDict['playerId']:
        
        #Extract and append
        playerIdDict['playerId'].append(pId)
        playerIdDict['squadId'].append(playerList.loc[playerList['playerId'] == pId,
                                                        ['squadId']]['squadId'].unique()[0])
        playerIdDict['firstName'].append(playerList.loc[playerList['playerId'] == pId,
                                                        ['firstname']]['firstname'].unique()[0])
        playerIdDict['surname'].append(playerList.loc[playerList['playerId'] == pId,
                                                      ['surname']]['surname'].unique()[0])
        playerIdDict['fullName'].append(f'{playerIdDict["firstName"][-1]} {playerIdDict["surname"][-1]}')
        
#Extract players from minutes played dataset that played minimum eligible minutes
eligiblePlayerMinutes = groupedMinutesPlayed.loc[groupedMinutesPlayed['minutesPlayed'] >= 14*60*(1/3)]

#Read in line-up data to create positional lists
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2022],
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular'])
lineUpData = lineUpData[2022]

#Create dictionary to store eligible players in
courtPositions = ['GS','GA','WA','C','WD','GD','GK']
eligiblePlayers = {courtPos: [] for courtPos in courtPositions}

#Loop through court positions
for courtPos in courtPositions:
    
    #Group by current court position to sum minutes played in GS
    courtPosMinutes = lineUpData.groupby(courtPos).sum().reset_index(drop = False)
    
    #Loop through eligible players
    for pId in eligiblePlayerMinutes['playerId']:
        
        #Do first check to see if in current position list
        if pId in list(courtPosMinutes[courtPos]):
            
            #Check for minutes played in current position
            courtPosMinsPlayed = courtPosMinutes.loc[courtPosMinutes[courtPos] == pId,
                                                     ]['duration'].values[0] / 60
            
            #Get total minutes played for player
            totalMinsPlayed = eligiblePlayerMinutes.loc[eligiblePlayerMinutes['playerId'] == pId,
                                                        ]['minutesPlayed'].values[0]
            
            #Run check if meets one-third criteria
            if courtPosMinsPlayed >= totalMinsPlayed * (1/3):
                
                #Append to dictionary for eligible players
                #Get full name
                fullName = playerIdDict['fullName'][playerIdDict['playerId'].index(pId)]
                eligiblePlayers[courtPos].append(fullName)
                
#Print out lists to text files
for courtPos in courtPositions:
    #Sort player list
    eligiblePlayers[courtPos].sort()
    with open(f'..\\lists\\eligiblePlayers_{courtPos}.txt', 'w') as fp:
        for player in eligiblePlayers[courtPos]:
            # write each item on a new line
            fp.write('%s\n' % player)
        fp.close()

# %%% ----- End of compilePlayerLists.py -----