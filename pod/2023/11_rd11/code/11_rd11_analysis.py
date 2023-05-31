# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 11 SSN match-ups.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
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
    
# %% Fever's lowest score?

#Read in team stats from Super Netball years
teamStatsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                                    fileStem = 'teamStats',
                                                    matchOptions = ['regular', 'final'],
                                                    joined = True, addSquadNames = True)

#Extract Fever stats and extract points/goals
teamStatsSuperNetball_FeverScoring = teamStatsSuperNetball.loc[teamStatsSuperNetball['squadName'] == 'Fever',
                                                        ][['year', 'roundNo', 'oppSquadName', 'goals', 'points']]

# %% Laura Dunkley's best game recently?

#Read in player stats from Super Netball years
playerStatsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                      years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                                      fileStem = 'playerStats',
                                                      matchOptions = ['regular', 'final'],
                                                      joined = True, addSquadNames = True)

#Extract Dunkley stats and extract relevant stats
playerStatsSuperNetball_Dunkley = playerStatsSuperNetball.loc[playerStatsSuperNetball['playerId'] == 1004472,
                                                        ][['year', 'roundNo', 'netPoints', 'feeds', 'feedWithAttempt', 'goalAssists']]

# %% Fever's one goal demons

#Collate yearly one-goal losses

#Read in team stats over time
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'],
                                        joined = True, addSquadNames = True)

#Collate margins across years
marginData = {'year': [], 'roundNo': [], 'squadName': [], 'margin': []}

#Loop through match Id's
for matchId in teamStats['matchId'].unique():
    
    #Extract current match data
    currMatch = teamStats.loc[teamStats['matchId'] == matchId,].reset_index(drop = True)
    
    #Calculate margin
    if currMatch['year'][0] < 2020:
        margin = currMatch['goals'][1] - currMatch['goals'][0]
    else:
        margin = currMatch['points'][1] - currMatch['points'][0]
    
    #Append data for both teams
    #Team 1
    marginData['year'].append(currMatch['year'][0])
    marginData['roundNo'].append(currMatch['roundNo'][0])
    marginData['squadName'].append(currMatch['squadName'][0])
    marginData['margin'].append(margin * -1)
    #Team 2
    marginData['year'].append(currMatch['year'][1])
    marginData['roundNo'].append(currMatch['roundNo'][1])
    marginData['squadName'].append(currMatch['squadName'][1])
    marginData['margin'].append(margin)
    
#Convert to dataframe
marginData_df = pd.DataFrame.from_dict(marginData)

#Extract one goal losses by teams
oneGoalLosses = marginData_df.loc[marginData_df['margin'] == -1,]

#Calculate the proportion of one goal losses
propOneGoal = len(oneGoalLosses) / len(teamStats['matchId'].unique()) * 100

#Extract a count of 1 goal losses per year by teams
oneGoalLosses_byTeamYear = oneGoalLosses.groupby(['year','squadName']).count()['margin']

#Probability of four one-goal losses
fourOneGoalProp = ((propOneGoal / 100) * (propOneGoal / 100) * (propOneGoal / 100) * (propOneGoal / 100)) * 100
fiveOneGoalProp = ((propOneGoal / 100) * (propOneGoal / 100) * (propOneGoal / 100) * (propOneGoal / 100) * (propOneGoal / 100)) * 100
    
# %% Donnell Wallam's performance

#Read in player period stats over time
playerPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                                years = 'all',
                                                fileStem = 'playerPeriodStats',
                                                matchOptions = ['regular', 'final'],
                                                joined = True, addSquadNames = False)

#Add player names
playerName = []
for ii in playerPeriodStats.index:
    #Get year and player Id
    year = playerPeriodStats.iloc[ii]['year']
    playerId = playerPeriodStats.iloc[ii]['playerId']
    #Get player name and append
    try:
        playerName.append(playerData[year].loc[playerData[year]['playerId'] == playerId,
                                               ]['fullName'].values[0])
    except:
        playerName.append('NA')            
#Add to dataframe
playerPeriodStats['playerName'] = playerName
    
#Review the scoring numbers from player period stats
playerPeriodStats_scoring = playerPeriodStats.loc[playerPeriodStats['goals'] > 0,
                                                  ][['year', 'roundNo', 'playerId', 'playerName', 'goals', 'points', 'period']]

# %% Penalty counts

#Start by looking at average penalties by teams all-time
avgPenaltiesAllTime = teamStats.groupby('squadName').mean(numeric_only = True)['penalties']

#Start by looking at average penalties by teams per year
avgPenaltiesPerYear = teamStats.groupby(['year','squadName']).mean(numeric_only = True)['penalties']

#Start by looking at average penalties by teams for this year
avgPenalties2023 = teamStats.loc[teamStats['year'] == 2023].groupby(['year','squadName']).mean(numeric_only = True)['penalties']

#Look at penalties across the year
penalties2023 = teamStats.loc[teamStats['year'] == 2023][['squadName', 'roundNo', 'penalties']]

#Look at penalties all-time
penaltiesAllTime = teamStats[['year','squadName', 'roundNo', 'penalties']]

# %% Fever's scoring

#Extract Fever stats and extract points/goals
teamStats_FeverScoring = teamStats.loc[teamStats['squadName'] == 'Fever',
                                       ][['year', 'roundNo', 'oppSquadName', 'goals', 'points']]

#Read in team period stats from Fowler Super Netball years
teamPeriodStatsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                          years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                          fileStem = 'teamPeriodStats',
                                                          matchOptions = ['regular', 'final'],
                                                          joined = True, addSquadNames = True)

#Pull out Fever data
teamPeriodStats_FeverScoring = teamPeriodStatsSuperNetball.loc[teamPeriodStatsSuperNetball['squadName'] == 'Fever',
                                                               ][['year', 'roundNo', 'oppSquadName', 'goals', 'points']]

#Extract Fowler stats and extract relevant stats
playerStatsSuperNetball_Fowler = playerStatsSuperNetball.loc[playerStatsSuperNetball['playerId'] == 80826,
                                                             ][['year', 'roundNo', 'goals', 'points']]

# %% Prediction

#Extract total penalty count for each match this year
teamStats2023 = teamStats.loc[teamStats['year'] == 2023,]
penaltyTotal2023 = teamStats.loc[teamStats['year'] == 2023,].groupby('matchId').sum(numeric_only = True)['penalties']



# %% ----- End of 11_rd11_analysis.py ----- %% #

