# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 9 SSN match-ups.
    
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
                                         matchOptions = ['regular', 'final'])

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','final'])

#Create a unique player dictionary for each year
#As part of this also give each player a primary court position for the year
#based on where they've played the majority of their time.
#When predicting data for a new season, this data obviously won't be available
#so we will need to take a primary position from Super Netball's squad data
playerDict = {}
for year in list(playerLists.keys()):
    
    #Create dictionary to append players to
    playerDict[year] = {'playerId': [],
                        'firstName': [], 'surname': [], 'fullName': [],
                        'squadId': [], 'primaryPosition': []}
    
    #Get unique player Id's for year
    uniquePlayerIds = list(playerLists[year]['playerId'].unique())
    
    #Loop through unique player Id's
    for playerId in uniquePlayerIds:
        
        #Extract player details
        playerDetails = playerLists[year].loc[playerLists[year]['playerId'] == playerId,]
        
        #Collate player name variables and append
        playerDict[year]['playerId'].append(playerId)
        playerDict[year]['firstName'].append(playerDetails['firstname'].unique()[0])
        playerDict[year]['surname'].append(playerDetails['surname'].unique()[0])
        playerDict[year]['fullName'].append(f'{playerDetails["firstname"].unique()[0]} {playerDetails["surname"].unique()[0]}')
        playerDict[year]['squadId'].append(playerDetails['squadId'].unique()[0])
        
        #Extract the players primary position from the line-up data
        #Create a variable to store durations in
        posDurations = []
        #Loop through and extract durations of court positions
        for courtPos in courtPositions:
            posDurations.append(lineUpData[year].loc[lineUpData[year][courtPos] == playerId,]['duration'].sum())
        #Identify max duration index and look this up in court position list
        #Append this as players primary position for the year
        playerDict[year]['primaryPosition'].append(courtPositions[np.argmax(posDurations)])

#Convert to dataframes
playerData = {}
for year in list(playerLists.keys()):
    playerData[year] = pd.DataFrame.from_dict(playerDict[year])

# %% Perfect feeding

#Read in all player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Extract from 2018 onwards when feed with attempt has been recorded
playerStats_2018onwards = playerStats.loc[playerStats['year'] >= 2018].reset_index(drop = True)

#Group by player and year to sum the feeds and feeds with attempt
playerFeeds = playerStats_2018onwards.groupby(['playerId', 'year']).sum(numeric_only = True)[['feeds', 'feedWithAttempt']].reset_index(drop = False)

#Add player name for ease of interpretation
playerName = []
for ii in playerFeeds.index:
    #Get player id and year
    playerId = playerFeeds.iloc[ii]['playerId']
    year = playerFeeds.iloc[ii]['year']
    #Get player name
    playerName.append(playerData[year].loc[playerData[year]['playerId'] == playerId,]['fullName'].values[0])
playerFeeds['playerName'] = playerName

#Calculate the feed with attempt proportion
playerFeeds['attemptProp'] = playerFeeds['feedWithAttempt'] / playerFeeds['feeds'] * 100

#Limit to those with 50 or more feeds 
playerFeeds = playerFeeds.loc[playerFeeds['feeds'] >= 50,]

# %% Butler's Super Shots in 2020

#Group by player Id and year to average out Super Shot attempts
avgSuperAttempts = playerStats.loc[playerStats['year'] >= 2020,].groupby(['year', 'playerId']).mean(numeric_only = True).reset_index(drop = False)[['year','playerId','attempt2']]

#Add player name for ease of interpretation
playerName = []
for ii in avgSuperAttempts.index:
    #Get player id and year
    playerId = avgSuperAttempts.iloc[ii]['playerId']
    year = avgSuperAttempts.iloc[ii]['year']
    #Get player name
    playerName.append(playerData[year].loc[playerData[year]['playerId'] == playerId,]['fullName'].values[0])
avgSuperAttempts['playerName'] = playerName

# %% Best and worst quarter scoring performances

#Read in team period stats
teamPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = 'all',
                                              fileStem = 'teamPeriodStats',
                                              matchOptions = ['regular', 'final'],
                                              joined = True, addSquadNames = True)

#Collate scoring by period
periodScoring = {'year': [], 'roundNo': [], 'squadName': [], 'period': [], 'score': []}

#Loop through periods
for ii in teamPeriodStats.index:
    #Append general data
    periodScoring['year'].append(teamPeriodStats.iloc[ii]['year'])
    periodScoring['roundNo'].append(teamPeriodStats.iloc[ii]['roundNo'])
    periodScoring['squadName'].append(teamPeriodStats.iloc[ii]['squadName'])
    periodScoring['period'].append(teamPeriodStats.iloc[ii]['period'])
    #Get score
    if teamPeriodStats.iloc[ii]['year'] < 2020:
        periodScoring['score'].append(teamPeriodStats.iloc[ii]['goals'])
    else:
        periodScoring['score'].append(teamPeriodStats.iloc[ii]['points'])
        
#Convert to dataframe and eliminate extra time
periodScoringData = pd.DataFrame.from_dict(periodScoring)
periodScoringData = periodScoringData.loc[periodScoringData['period'] <= 4,]

# %% Missed goal turnovers

#Extract data from when missed goal turnovers are collected (2021 onwards)
playerStats_2021onwards = playerStats.loc[playerStats['year'] >= 2021].reset_index(drop = True)

#Group by player and year to sum the missed goals and missed goal turnovers
playerMisses = playerStats_2021onwards.groupby(['playerId', 'year']).sum(numeric_only = True)[['goalAttempts', 'goalMisses', 'missedGoalTurnover']].reset_index(drop = False)

#Restrict to only those with goal attempts
playerMisses = playerMisses.loc[playerMisses['goalAttempts'] > 0,].reset_index(drop = True)

#Add player name for ease of interpretation
playerName = []
for ii in playerMisses.index:
    #Get player id and year
    playerId = playerMisses.iloc[ii]['playerId']
    year = playerMisses.iloc[ii]['year']
    #Get player name
    playerName.append(playerData[year].loc[playerData[year]['playerId'] == playerId,]['fullName'].values[0])
playerMisses['playerName'] = playerName

#Calculate the feed with attempt proportion
playerMisses['reboundProp'] = (playerMisses['goalMisses'] - playerMisses['missedGoalTurnover']) / playerMisses['goalMisses'] * 100

#Limit to players with 50 or more goal attempts in a season
playerMisses = playerMisses.loc[playerMisses['goalAttempts'] >= 50,]

# %% Close margins

#Read in team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Collate margins
marginDict = {'matchId': [], 'year': [], 'roundNo': [], 'margin': []}

#Loop through matches
for matchId in teamStats['matchId'].unique():
    
    #Get current match
    currMatch = teamStats.loc[teamStats['matchId'] == matchId,].reset_index(drop = True)
    
    #Calculate margin and append to dictionary
    if currMatch['year'][0] < 2020:
        marginDict['margin'].append(int(np.abs(currMatch['goals'][1] - currMatch['goals'][0])))
    else:
        marginDict['margin'].append(int(np.abs(currMatch['points'][1] - currMatch['points'][0])))
    
    #Collate general data
    marginDict['matchId'].append(matchId)
    marginDict['year'].append(currMatch['year'][0])
    marginDict['roundNo'].append(currMatch['roundNo'][0])
    
#Convert to dataframe
marginData = pd.DataFrame.from_dict(marginDict)

#Get a count by year of the different margins
marginCountByYear = marginData.groupby(['year', 'margin']).count().reset_index(drop = False)[['year','margin','matchId']]

#Calculate proportion for that year
yearlyProp = []
for ii in marginCountByYear.index:
    #Get year
    year = marginCountByYear.iloc[ii]['year']
    #Calculate and append proportion
    yearlyProp.append(marginCountByYear.iloc[ii]['matchId'] / len(teamStats.loc[teamStats['year'] == year]['matchId'].unique()) * 100)
marginCountByYear['yearlyProp'] = yearlyProp

#Get a count by year and round of the different margins
marginCountByYearRound = marginData.groupby(['year', 'roundNo', 'margin']).count().reset_index(drop = False)[['year', 'roundNo', 'margin','matchId']]
    
#Get average margin by year
marginAvgByYear = marginData.groupby(['year']).mean().reset_index(drop = False)[['year','margin']]

# %% Prediction review - penalties matching name length

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Look up how many times a player has matched penalty count to name length
penaltiesNameLength = {'matchId': [], 'playerId': [], 'playerName': [],
                       'year': [], 'roundNo': [], 'matchType': [],
                       'nameLength': [], 'penaltyCount': [],
                       'match': []}

#Loop through player entries
for ii in playerStats.index:
    
    #Get player and match details
    playerId = playerStats.iloc[ii]['playerId']
    matchId = playerStats.iloc[ii]['matchId']
    year = playerStats.iloc[ii]['year']
    roundNo = playerStats.iloc[ii]['roundNo']
    matchType = playerStats.iloc[ii]['matchType']
    penaltyCount = playerStats.iloc[ii]['penalties']
    
    #Get player name
    playerName = playerData[year].loc[playerData[year]['playerId'] == playerId,
                                      ]['fullName'].values[0]
    nameLength = len(playerName.replace(' ',''))
    
    #Check for match
    if nameLength == penaltyCount:
        match = True
    else:
        match = False
        
    #Append in dictionary
    penaltiesNameLength['matchId'].append(matchId)
    penaltiesNameLength['playerId'].append(playerId)
    penaltiesNameLength['playerName'].append(playerName)
    penaltiesNameLength['year'].append(year)
    penaltiesNameLength['roundNo'].append(roundNo)
    penaltiesNameLength['matchType'].append(matchType)
    penaltiesNameLength['nameLength'].append(nameLength)
    penaltiesNameLength['penaltyCount'].append(penaltyCount)
    penaltiesNameLength['match'].append(match)
    
#Convert to dataframe
penaltiesNameLength_df = pd.DataFrame.from_dict(penaltiesNameLength)

#Calculate proportion of matches
print(f'% Players with Matched Name Length to Penalties: {penaltiesNameLength_df["match"].sum() / len(penaltiesNameLength_df) * 100}')

#Extract data to look at examples
penaltiesNameLength_matches = penaltiesNameLength_df.loc[penaltiesNameLength_df['match']]

#Look at most frequent in this situation
penaltiesNameLength_matchesCount = penaltiesNameLength_matches.groupby('playerName').count()['nameLength']

# %% Prediction

#Margin above average and sitting near the top end of the season (8-9 avg.)

#Review what this needs to reach to achieve top 5
marginScoring = {'year': [], 'roundNo': [], 'totalMargin': []}

#Loop through years of Super Netball
for year in [2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    
    #Identify regular season matches for current year
    currYearStats = teamStats.loc[(teamStats['year'] == year) & 
                                  (teamStats['matchType'] == 'regular'),].reset_index(drop = True)
    
    #Identify rounds in year
    allRounds = list(currYearStats['roundNo'].unique())
    
    #Loop through rounds
    for roundNo in allRounds:
        
        #Get current round stats
        currRoundStats = currYearStats.loc[currYearStats['roundNo'] == roundNo,]
        
        #Set variable to store margins in
        margin = []
        
        #Extract and total goals or points
        if year < 2020:            
            #Loop through matches
            for matchId in currRoundStats['matchId'].unique():                
                #Sum margin
                scores = currRoundStats.loc[currRoundStats['matchId'] == matchId,]['goals'].to_numpy()
                margin.append(np.abs(scores[0] - scores[1]))            
        else:            
            #Loop through matches
            for matchId in currRoundStats['matchId'].unique():                
                #Sum margin
                scores = currRoundStats.loc[currRoundStats['matchId'] == matchId,]['points'].to_numpy()
                margin.append(np.abs(scores[0] - scores[1]))
                
        #Append data
        marginScoring['year'].append(year)
        marginScoring['roundNo'].append(roundNo)
        marginScoring['totalMargin'].append(np.sum(margin))
    
#Convert to dataframe
marginScoringData = pd.DataFrame.from_dict(marginScoring)

#Calculate average (considering games)
marginScoringData['avgMargin'] = marginScoringData['totalMargin'] / 4

# %% ----- End of 09_rd9_analysis.py ----- %% #

