# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 4 SSN match-ups.
    
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

# %% Round match-ups

#Mostly reviewing match stat sheets throughout here --- comments added

# %% Vixens vs. Lightning

#Gain to goal %
    #Vixens: 0%, 50%, 75%, 75%
    #Lightning: 67%, 100%, 0%, 50%
    #Double edged sword:
        #where gains for Vixens went up from Q1 + increased %
        #where gains for Lightning went down from Q1/Q2 + decreased %
#Goal scoring
    #Vixens consistent 15, 16, 16, 13
    #Lightning dropped off 17, 16, 12, 11
        #More so Vixens maintaining play and Lightning dropping off
#Vixens > 10 gains

# %% Magpies vs. Firebirds

#General play turnovers
    #25 Firebirds to Magpies 18
        #10 of the Firebirds 25 turnovers coming in 3rd quarter (Magpies only 2 in Q3)
#Centre pass to goal in Q3
    #44% for Firebirds to 93% for Magpies
    
#Goals scored in Q3 - lowest since?
#Read in team period stats for Super Shot era
teamPeriodStatsSuperEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                      years = [2020, 2021, 2022, 2023],
                                                      fileStem = 'teamPeriodStats',
                                                      matchOptions = ['regular','final'])

#Add year column to dataframes
for year in teamPeriodStatsSuperEra.keys():
    teamPeriodStatsSuperEra[year]['year'] = [year] * len(teamPeriodStatsSuperEra[year])

#Concatenate dataframes
teamPeriodStatsSuperEra = pd.concat([teamPeriodStatsSuperEra[year] for year in teamPeriodStatsSuperEra.keys()]).reset_index(drop = True)

#Extract points
teamPeriodStatsSuperEra_points = teamPeriodStatsSuperEra[['matchId', 'roundNo', 'year',
                                                          'squadId', 'oppSquadId', 'points']]

#Add this 8 goal quarter to the Firebirds 7 goal quarters in round 1 & 2, they
#now hold the bottom 3 scoring quarters for the year
    #No other team scored 8 or less yet this year

# %% Thunderbirds vs. Giants

#Gain to goal %
    #73% for Giants, 59% for Thunderbirds
        #Past year Thunderbird vibes - more gains but inefficient scoring from these
    #Without the Super Shot this might have been a low scoring game
        #46 shots made by Thunderbirds, 50 by Giants

# %% Swifts vs. Fever

#Gains + gain to goal %
    #Fever holding pre-season form
        #16 gains - 75% conversion to goal
#Another dominant NetPoints performance
    #fever 532 to Swifts 314.5
    
# %% Winning streaks

#Read in team stats over time
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular','final'])

#Add year column to dataframes
for year in teamStats.keys():
    teamStats[year]['year'] = [year] * len(teamStats[year])

#Concatenate dataframes
teamStats_all = pd.concat([teamStats[year] for year in teamStats.keys()]).reset_index(drop = True)

#Create a win/loss/draw column
result = []
for ii in teamStats_all.index:
    
    #Extract the current teams score
    if teamStats_all.iloc[ii]['year'] < 2020:
        teamScore = teamStats_all.iloc[ii]['goals']
    else:
        teamScore = teamStats_all.iloc[ii]['points']
        
    #Work out opposition score
    #Get match & squad Id
    matchId = teamStats_all.iloc[ii]['matchId']
    squadId = teamStats_all.iloc[ii]['squadId']
    #Find opposition score
    if teamStats_all.iloc[ii]['year'] < 2020:
        oppScore = teamStats_all.loc[(teamStats_all['matchId'] == matchId) &
                                     (teamStats_all['oppSquadId'] == squadId),
                                     ]['goals'].values[0]
    else:
        oppScore = teamStats_all.loc[(teamStats_all['matchId'] == matchId) &
                                     (teamStats_all['oppSquadId'] == squadId),
                                     ]['points'].values[0]
        
    #Append result to list
    if teamScore > oppScore:
        result.append('win')
    elif teamScore < oppScore:
        result.append('loss')
    else:
        result.append('draw')
        
#Append to dataframe
teamStats_all['result'] = result

#Set dictionary to store squad win streaks in
squadWinStreaks = {}

#Loop through squad Id's
for squadId in squadDict:
    
    #Extract current squads data
    teamStatsSquad = teamStats_all.loc[teamStats_all['squadId'] == squadId, ].reset_index(drop = True)
    
    #Set current streak
    currentWinStreak = 0
    
    #Set list to store in
    winStreak = []
    
    #Convert the result to a boolean for wins
    teamStatsSquad['winBool'] = [True if result == 'win' else False for result in teamStatsSquad['result']]
    
    ts = teamStatsSquad[['matchId', 'squadId', 'year', 'roundNo', 'winBool', 'matchType']]
    
    #Loop through matches and append win streak
    for ii in teamStatsSquad.index:
        #Set counter
        if teamStatsSquad.iloc[ii]['winBool']:
            currentWinStreak += 1
        else:
            currentWinStreak = 0
        #Append to list
        winStreak.append(currentWinStreak)
        
    #Append to dataframe
    teamStatsSquad['winStreak'] = winStreak
    
    #Store in dictionary
    squadWinStreaks[squadDict[squadId]] = teamStatsSquad[['matchId', 'squadId', 'year', 'roundNo',
                                                          'matchType', 'winStreak']]
    
#Fever's current 8 game win streak beats their highest number of wins in a row
#that they reached in round 7 of 2021

#Other squad highs:
    #Firebirds 21 game streak from the 2015 through to 2016 season
    #Giants = 5
    #Lightning = 9 (broken with a GF loss in 2019)
    #Magic = 14 back in 2013
    #Magpies = 3
    #Mystics = 4
    #Pulse = 5
    #Steel = 10 (2016)
    #Swifts = 13 in rd 14 of 2010 - then proceeded to lose 2 straight finals
    #Tactix = 2
    #Thunderbirds = 16 (most of 2013 into the first few weeks of 2014)
    #Vixens = 11 at rd 5 of 2010
    
# %% Wood as a barometer for the Lightning

#Set Wood id
woodId = 80475

#Read in 2023 player stats
playerStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2023],
                                              fileStem = 'playerStats',
                                              matchOptions = ['regular'])
playerStats2023 = playerStats2023[2023]

#Extract Wood stats
woodPlayerStats2023 = playerStats2023.loc[playerStats2023['playerId'] == woodId,]
    
#Read in 2023 player stats
playerPeriodStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                                    years = [2023],
                                                    fileStem = 'playerPeriodStats',
                                                    matchOptions = ['regular'])
playerPeriodStats2023 = playerPeriodStats2023[2023]
        
#Extract Wood stats
woodPlayerPeriodStats2023 = playerPeriodStats2023.loc[playerPeriodStats2023['playerId'] == woodId,]

# %% Wing defences as netballs unsung heroes

#Link up primary positions to this years player stats
primaryPos = []
for playerId in playerStats2023['playerId']:
    #Get primary position
    primaryPos.append(playerData[2023].loc[playerData[2023]['playerId'] == playerId,]['primaryPosition'].values[0])
#Append to dataframe
playerStats2023['primaryPosition'] = primaryPos

#Extract the WD data
playerStats2023_WD = playerStats2023.loc[playerStats2023['primaryPosition'] == 'WD',]

# %% Which players are the most consistent from a fantasy scoring perspective

#Let's go with Netball Scoops 2023 scoring parameters for calculating fantasy score

#Define fantasy score calculation
def calcFantasyScore2023(statsData = None, playerPos = None):
    
    """
    
    Inputs:
        
        statsData - a pandas series object that contains the values for relevant stats
        playerPos - string of the players primary court playing position
        
    Outputs:
        
        fantasyScore - calculated fantasy score value
    
    """
    
    #Function input checks
    
    #Check for all variables
    if statsData is None or playerPos is None:
        raise ValueError('All inputs are required for function to run.')
        
    #Check for appropriate court position
    if playerPos not in ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']:
        raise ValueError("Player position must be one of 'GS', 'GA', 'WA', 'C', 'WD', 'GD' or 'GK'")
    
    #Set the 2022 scoring system
    pointVals = {'goal1': 2, 'goal2': 6, 'goalMisses': -5,
                 'goalAssists': 4,
                 'gain': 5, 'intercepts': 10, 'deflections': 6,
                 'rebounds': 5, 'pickups': 6,
                 'generalPlayTurnovers': -5, 'interceptPassThrown': -5}
        
    #Set a variable to calculate fantasy score
    fantasyScore = 0

    #Calculate score if player is predicted to have played
    if statsData['minutesPlayed'] > 0:
        
        #Add to fantasy score for getting on court
        fantasyScore += 12 #starting score allocated to those who get on court
        
        #Predict how many quarters the player was on for
        #Rough way of doing this is diving by quarter length of 15
        #Take the rounded ceiling of this to estimate quarters played
        fantasyScore += int(np.ceil(statsData['minutesPlayed'] / 15) * 4)
        
        #Loop through the scoring elements and add the scoring for these
        for stat in list(pointVals.keys()):
            fantasyScore += statsData[stat] * pointVals[stat]
            
        #Calculate centre pass receives points
        #This requires different point values across the various positions
        #Here we make an estimate that attacking players would be in the GA/WA group
        #and that defensive players would be in the GD/WD group
        if playerPos in ['GS', 'GA', 'WA', 'C']:
            fantasyScore += np.floor(statsData['centrePassReceives'] / 2) * 1
        elif playerPos in ['WD', 'GD', 'GK']:
            fantasyScore += statsData['centrePassReceives'] * 3
        
        #Calculate penalty points
        fantasyScore += np.floor((statsData['obstructionPenalties'] + statsData['contactPenalties']) / 2) * -1
        
        #Estimate the time played in WD based on player position
        #8 points for half a game at WD / 16 points for a full game at WD
        #Here we'll provide partial points on the basis of minutes played
        #alongside the fantasy position. If a player is exclusively a WD then
        #we'll allocate all of the partial points, but if they're DPP then
        #we'll allocate half of the partial points. This gives an inexact
        #estimate, but may be the best we can do.
        if playerPos == 'WD':
            #Check if minutes played is > than a half of play (i.e. 30 mins)
            if statsData['minutesPlayed'] > 30:
                fantasyScore += ((16-8) * (statsData['minutesPlayed'] - 30) / 30) + 6
            else:
                fantasyScore += (((16-8) * (statsData['minutesPlayed'] - 30) / 30) + 6) / 2
                    
    #Return the final calculated fantasy score
    return fantasyScore

#We'll start fresh and calculate this over the last year and a bit
playerStatsFantasy = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2022, 2023],
                                                 fileStem = 'playerStats',
                                                 matchOptions = ['regular', 'final'])

#Create dictionary to store fantasy data in
fantasyScores = {'matchId': [], 'year': [], 'roundNo': [], 'playerId': [], 'playerName': [], 'fantasyScore': []}

#Loop through data and calcute fantasy score
#Loop through years
for year in playerStatsFantasy.keys():
    
    #Loop through player stats
    for ii in playerStatsFantasy[year].index:
        
        #Extract player stats series & id
        playerId = playerStatsFantasy[year].iloc[ii]['playerId']
        selectStats = playerStatsFantasy[year].iloc[ii]
        
        #Extract players primary position and name
        playerPos = playerData[year].loc[playerData[year]['playerId'] == playerId,
                                         ]['primaryPosition'].values[0]
        playerName = playerData[year].loc[playerData[year]['playerId'] == playerId,
                                         ]['fullName'].values[0]
        
        #Calculate fantasy score
        fantasyScore = calcFantasyScore2023(statsData = selectStats, playerPos = playerPos)
        
        #Append data to dictionary
        fantasyScores['matchId'].append(playerStatsFantasy[year].iloc[ii]['matchId'])
        fantasyScores['year'].append(year)
        fantasyScores['roundNo'].append(playerStatsFantasy[year].iloc[ii]['roundNo'])
        fantasyScores['playerId'].append(playerId)
        fantasyScores['playerName'].append(playerName)
        fantasyScores['fantasyScore'].append(fantasyScore)
        
#Convert to dataframe
fantasyScoreData = pd.DataFrame.from_dict(fantasyScores)

#Calculate mean and standard deviation
meanFantasyScore = fantasyScoreData.groupby(['playerId', 'playerName']).mean()['fantasyScore']
stdFantasyScore = fantasyScoreData.groupby(['playerId', 'playerName']).std()['fantasyScore']

#Calculate consistency rating
consistencyRating = stdFantasyScore / meanFantasyScore

# %% Prediction

# Goals scored across entire weekend will sit in top #5

#Review what this needs to reach to achieve top 5
roundScoring = {'year': [], 'roundNo': [], 'totalGoals': []}

#Loop through years of Super Netball
for year in [2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    
    #Identify regular season matches for current year
    currYearStats = teamStats[year].loc[teamStats[year]['matchType'] == 'regular',].reset_index(drop = True)
    
    #Identify rounds in year
    allRounds = list(currYearStats['roundNo'].unique())
    
    #Loop through rounds
    for roundNo in allRounds:
        
        #Extract and total goals or points
        if year < 2020:
            totalGoals = currYearStats.loc[currYearStats['roundNo'] == roundNo,]['goals'].sum()
        else:
            totalGoals = currYearStats.loc[currYearStats['roundNo'] == roundNo,]['points'].sum()
            
        #Append data
        roundScoring['year'].append(year)
        roundScoring['roundNo'].append(roundNo)
        roundScoring['totalGoals'].append(totalGoals)
    
#Convert to dataframe
roundScoringData = pd.DataFrame.from_dict(roundScoring)


# %% ----- End of 04_rd4_analysis.py ----- %% #

