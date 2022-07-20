# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Script to compile players 'eligible' for all time team
    Eligibility criteria:
        - Played at least half of available season time (i.e. 50% of nRounds * 60) in at least 1 season
        - Played at least one-third of their time in a given position (higher minutes at position = selected position)
    
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

# %% Compile list of players meeting conditions

#Read in player data
playerList = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = 'all',
                                         fileStem = 'playerList',
                                         matchOptions = ['regular'])

#Read in minutes played data for the 2022 regular season
minutesPlayed = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = 'all',
                                            fileStem = 'minutesPlayed',
                                            matchOptions = ['regular'])

#Identify max rounds played in each year
nRounds = {}
for year in list(minutesPlayed.keys()):
    nRounds[year] = minutesPlayed[year]['roundNo'].max()

#Append year column to minutes played & player list dataframe
for year in list(minutesPlayed.keys()):
    minutesPlayed[year]['year'] = [year]*len(minutesPlayed[year])
    playerList[year]['year'] = [year]*len(playerList[year])
    
#Concatenate player lists from each year
playerListAll = pd.concat([playerList[year] for year in list(playerList.keys())])

#Get unique player Id's
playerIds = playerListAll['playerId'].unique()

#Concatenate minutes played from each year
minutesPlayedAll = pd.concat([minutesPlayed[year] for year in list(minutesPlayed.keys())])

#Group by player/squad Id and year then sum for minutes played
groupedMinutesPlayed = minutesPlayedAll.groupby(['playerId', 'squadId','year']).sum().reset_index(
    drop = False).drop(['matchId','oppSquadId','roundNo','gameNo'], axis = 1)

#Set list to store kept players in
keepPlayerIds = []

#Loop through player Id's and check if meeting conditions
for playerId in playerIds:
    
    #Extract their minutes played
    currPlayerMinutes = groupedMinutesPlayed.loc[groupedMinutesPlayed['playerId'] == playerId,]
    
    #Run first check if player was in comp for 3 or more seasons
    if len(currPlayerMinutes['year'].unique()) >= 1:
        
        #Count number of years where player had >= 50% of minutes played
        eligibleSeasons = 0
        for year in currPlayerMinutes['year']:
            #Get minutes played
            minsPlayed = currPlayerMinutes.loc[currPlayerMinutes['year'] == year,
                                               ]['minutesPlayed'].values[0]
            #Compare to potential total minutes
            if minsPlayed >= nRounds[year] * 60 * 0.5:
                eligibleSeasons += 1
                
        #Check if meeting the 3 seasons threshold
        if eligibleSeasons >= 1:
            keepPlayerIds.append(playerId)
    
#Create player dictionary with names and details
playerIdDict = {'playerId': [],
                'firstName': [], 'surname': [], 'fullName': [],
                'squadNamesYears': []}
    
#Loop through Ids
for pId in keepPlayerIds:

    #Extract details
    currPlayer = playerListAll.loc[playerListAll['playerId'] == pId,].reset_index(drop = True)
    playerIdDict['playerId'].append(pId)
    #Names (use last listed in competition)
    playerIdDict['firstName'].append(currPlayer['firstname'].to_list()[-1])
    playerIdDict['surname'].append(currPlayer['surname'].to_list()[-1])
    playerIdDict['fullName'].append(f'{currPlayer["firstname"].to_list()[-1]} {currPlayer["surname"].to_list()[-1]}')
    #Extract squads and years
    squadYear = currPlayer.groupby(['year','squadId']).describe().index
    squadYearList = [str(squadDict[squadYear[ii][1]])+': '+str(squadYear[ii][0]) for ii in range(len(squadYear))]
    playerIdDict['squadNamesYears'].append('; '.join(squadYearList))

#Convert to dataframe for viewing
playerIdDf = pd.DataFrame.from_dict(playerIdDict)

#Read in line-up data to create positional lists
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = 'all',
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular'])

#Append year column to lineup data
for year in list(lineUpData.keys()):
    lineUpData[year]['year'] = [year]*len(lineUpData[year])

#Concatenate lineup data from each year
lineUpDataAll = pd.concat([lineUpData[year] for year in list(lineUpData.keys())])

#Melt data into appropriate shape for calculating minutes in each position
positionalMinutes = pd.melt(lineUpDataAll.reset_index(), id_vars = ['duration'],
                            value_vars = ['GS','GA','WA','C','WD','GD','GK'],
                            var_name = 'courtPosition', value_name = 'playerId')

#Convert seconds to minutes
positionalMinutes['minutesPlayed'] = positionalMinutes['duration'] / 60

#Group minutes by position and player Id
groupedPositionalMinutes = positionalMinutes.groupby(['playerId', 'courtPosition']).sum().reset_index(
    drop = False).drop(['duration'], axis = 1)
    
#Create dictionary to store eligible players in
courtPositions = ['GS','GA','WA','C','WD','GD','GK']
eligiblePlayers = {courtPos: [] for courtPos in courtPositions}
eligiblePlayersSimple = {courtPos: [] for courtPos in courtPositions}

#Loop through kept players and identify if they meet condition of 33% in position
for pId in keepPlayerIds:
    
    #Identify appropriate position for player based on maximum minutes played
    selectData = groupedPositionalMinutes.loc[groupedPositionalMinutes['playerId'] == pId,
                                              ].sort_values(by = 'minutesPlayed', ascending = False).reset_index(
                                                  drop = True).iloc[0][['courtPosition','minutesPlayed']]
    selectPos = selectData['courtPosition']
    selectMins = selectData['minutesPlayed']
    
    #Get total minutes for player
    totalMins = groupedMinutesPlayed.loc[groupedMinutesPlayed['playerId'] == pId,
                                         ]['minutesPlayed'].sum()
    
    #Check if meets the one-third criteria of total minutes at position
    if selectMins >= totalMins * (1/3):
        
        #Append player to eligible list for selected position
        #Get player name and teams played for
        fullName = playerIdDict['fullName'][playerIdDict['playerId'].index(pId)]
        squads = playerIdDict['squadNamesYears'][playerIdDict['playerId'].index(pId)]
        #Join together and append to appropriate dictionary
        eligiblePlayers[selectPos].append(f'{fullName} ({squads})')
        eligiblePlayersSimple[selectPos].append(f'{fullName}')
                       
#Print out lists to text files
for courtPos in courtPositions:
    #Sort player list
    eligiblePlayers[courtPos].sort()
    eligiblePlayersSimple[courtPos].sort()
    with open(f'..\\lists\\eligiblePlayers_{courtPos}.txt', 'w') as fp:
        for player in eligiblePlayers[courtPos]:
            # write each item on a new line
            fp.write('%s\n' % player)
        fp.close()
    with open(f'..\\lists\\eligiblePlayersSimple_{courtPos}.txt', 'w') as fp:
        for player in eligiblePlayersSimple[courtPos]:
            # write each item on a new line
            fp.write('%s\n' % player)
        fp.close()

# %%% ----- End of compilePlayerLists.py -----