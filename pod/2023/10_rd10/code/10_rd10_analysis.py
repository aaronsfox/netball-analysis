# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 10 SSN match-ups.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
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
    
# %% Record round rebooted

# %% Margins across matches

#Collate margins from this season

#Read in team stats data
teamStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2023],
                                            fileStem = 'teamStats',
                                            matchOptions = ['regular', 'final'],
                                            joined = True, addSquadNames = True)

#Store margin data
margins2023 = {'matchId': [], 'roundNo': [], 'margin': [], 'squadNames': []}

#Loop through matches
for matchId in teamStats2023['matchId'].unique():
    
    #Get scores and squad names for current match
    scores = teamStats2023.loc[teamStats2023['matchId'] == matchId,
                               ].reset_index(drop = True)['points']
    squadNames = teamStats2023.loc[teamStats2023['matchId'] == matchId,
                               ].reset_index(drop = True)['squadName']
    
    #Append data
    margins2023['matchId'].append(matchId)
    margins2023['roundNo'].append(teamStats2023.loc[teamStats2023['matchId'] == matchId,]['roundNo'].unique()[0])
    margins2023['margin'].append(np.abs(scores[1] - scores[0]))
    margins2023['squadNames'].append(list(squadNames))

#Convert to dataframe
marginsData2023 = pd.DataFrame.from_dict(margins2023)

#Average margins by round
avgMarginsByRound2023 = marginsData2023.groupby('roundNo').mean()

# %% Highest scores and goals made

#Read in team stats data
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Store scoring data
scoringData = {'matchId': [], 'year': [], 'roundNo': [], 'squadName': [], 'oppSquadName': [],
               'score': [], 'goals': []}

#Loop through entries
for ii in teamStats.index:
    
    #Get score and goals
    if teamStats.iloc[ii]['year'] < 2020:
        score = teamStats.iloc[ii]['goals']
    else:
        score = teamStats.iloc[ii]['points']
    goals = teamStats.iloc[ii]['goals']
    
    #Store data
    scoringData['matchId'].append(teamStats.iloc[ii]['matchId'])
    scoringData['year'].append(teamStats.iloc[ii]['year'])
    scoringData['roundNo'].append(teamStats.iloc[ii]['roundNo'])
    scoringData['squadName'].append(teamStats.iloc[ii]['squadName'])
    scoringData['oppSquadName'].append(teamStats.iloc[ii]['oppSquadName'])
    scoringData['score'].append(score)
    scoringData['goals'].append(goals)
    
#Convert to dataframe
scoringData_df = pd.DataFrame.from_dict(scoringData)

#Get Super Shot era scores
scoringData_df_superShot = scoringData_df.loc[scoringData_df['year'] >= 2020,]

#Highest combined scoring total
scoringData_combinedTotal = scoringData_df.groupby('matchId').sum(numeric_only = True)

# %% Glasgow's Super Shots

#Read in player stats data from Super Shot era
playerStatsSuperEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                  years = [2020, 2021, 2022, 2023],
                                                  fileStem = 'playerStats',
                                                  matchOptions = ['regular', 'final'],
                                                  joined = True, addSquadNames = True)

#Store super shot data
superShotData = {'matchId': [], 'year': [], 'roundNo': [],
                 'squadName': [], 'oppSquadName': [], 'playerId': [], 'playerName': [],
                 'superMade': [], 'superAttempt': []}

#Extract only player stats where Super Shot was attempted
playerStatsSuperEra_shots = playerStatsSuperEra.loc[playerStatsSuperEra['attempt2'] > 0,].reset_index(drop = True)

#Loop through and store data
for ii in playerStatsSuperEra_shots.index:
    
    #Store general data
    superShotData['matchId'].append(playerStatsSuperEra_shots.iloc[ii]['matchId'])
    superShotData['year'].append(playerStatsSuperEra_shots.iloc[ii]['year'])
    superShotData['roundNo'].append(playerStatsSuperEra_shots.iloc[ii]['roundNo'])
    superShotData['squadName'].append(playerStatsSuperEra_shots.iloc[ii]['squadName'])
    superShotData['oppSquadName'].append(playerStatsSuperEra_shots.iloc[ii]['oppSquadName'])
    
    #Store player data
    superShotData['playerId'].append(playerStatsSuperEra_shots.iloc[ii]['playerId'])
    superShotData['playerName'].append(playerData[playerStatsSuperEra_shots.iloc[ii]['year']].loc[
        playerData[playerStatsSuperEra_shots.iloc[ii]['year']]['playerId'] == playerStatsSuperEra_shots.iloc[ii]['playerId'],
        ]['fullName'].values[0])
    
    #Store shooting data
    superShotData['superMade'].append(playerStatsSuperEra_shots.iloc[ii]['goal2'])
    superShotData['superAttempt'].append(playerStatsSuperEra_shots.iloc[ii]['attempt2'])
    
#Convert to dataframe
superShotData_df = pd.DataFrame.from_dict(superShotData)
    

# %% 50 by half time a record?

#Read in team period stats data
teamPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = 'all',
                                              fileStem = 'teamPeriodStats',
                                              matchOptions = ['regular', 'final'],
                                              joined = True, addSquadNames = True)

#Extract first half and group by match/squad Id to sum first half score
firstHalfScoring = teamPeriodStats.loc[teamPeriodStats['period'] <= 2,
                                       ].groupby(['matchId', 'squadId']).sum(
                                           numeric_only = True)[['goals', 'points']]


# %% Other checks

#Highest gains in a match
teamGains = teamStats[['matchId', 'year', 'roundNo', 'squadName', 'oppSquadName', 'gain']]

#Highest feeds in a match
teamFeeds = teamStats[['matchId', 'year', 'roundNo', 'squadName', 'oppSquadName', 'feeds']]

# %% Parmenter's performance

#Consider WD netpoints

#Read in regular season player stats for NetPoints era
playerStatsNetPoints = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                   fileStem = 'playerStats',
                                                   matchOptions = ['regular'])

#Get line-up data over concurrent period
lineUpsNetPoints = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2018, 2019, 2020, 2021, 2022, 2023],
                                               fileStem = 'lineUps',
                                               matchOptions = ['regular'])

#Set-up dictionary to store data
netPointsData = {'matchId': [], 'playerId': [], 'year': [], 'roundNo': [],
                 'primaryPos': [], 'netPoints': []}

#Loop years
for year in playerStatsNetPoints.keys():
    
    #Loop through player entries
    for ii in range(len(playerStatsNetPoints[year])):
        
        #Get details for current entry
        matchId = playerStatsNetPoints[year].iloc[ii]['matchId']
        playerId = playerStatsNetPoints[year].iloc[ii]['playerId']
        roundNo = playerStatsNetPoints[year].iloc[ii]['roundNo']
        netPoints = playerStatsNetPoints[year].iloc[ii]['netPoints']
        
        #Get players primary position
        #Get current match line-ups
        currLineUps = lineUpsNetPoints[year].loc[lineUpsNetPoints[year]['matchId'] == matchId,]
        
        #Loop through and extract durations of court positions
        posDurations = []
        for courtPos in courtPositions:
            posDurations.append(currLineUps.loc[currLineUps[courtPos] == playerId,]['duration'].sum())
        #Identify maximum time if any greater than zero
        if np.sum(posDurations) > 0:
            primaryPos = courtPositions[np.argmax(posDurations)]
        else:
            primaryPos = 'B'
            
        #Append data to dictionary
        netPointsData['matchId'].append(matchId)
        netPointsData['playerId'].append(playerId)
        netPointsData['year'].append(year)
        netPointsData['roundNo'].append(roundNo)
        netPointsData['primaryPos'].append(primaryPos)
        netPointsData['netPoints'].append(netPoints)
        
#Convert to dataframe
netPointsAll = pd.DataFrame.from_dict(netPointsData)

#Get WD NetPoints
netPointsWD = netPointsAll.loc[netPointsAll['primaryPos'] == 'WD',]

# %% Contest for Diamonds WD

#Set Brazill & Parmenter IDs
brazillId = 80299
parmenterId = 1001356

#Extract their player stats
playerStats_WD = playerStatsSuperEra.loc[(playerStatsSuperEra['year'] == 2023) &
                                          (playerStatsSuperEra['playerId'].isin([brazillId,parmenterId])),]

#Review this years data & average
playerStats_WD_avg2023 = playerStats_WD.groupby('playerId').mean(numeric_only = True)

#Do total stats too
playerStats_WD_total2023 = playerStats_WD.groupby('playerId').sum(numeric_only = True)

# %% Mannix's game compared to history

#Set Mannix id
mannixId = 994213

#Get all player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Extract Mannix data
mannixStats = playerStats.loc[playerStats['playerId'] == mannixId,]

#Extract key stats
mannixKeyStats = mannixStats[['matchId', 'year', 'roundNo', 'oppSquadName',
                              'gain', 'deflections', 'deflectionWithGain', 'intercepts', 'pickups', 'penalties']]

#Calculate PG ratio
mannixKeyStats['pgRatio'] = mannixKeyStats['penalties'] / mannixKeyStats['gain']

#Calculate career PG ratio
mannixKeyStats['penalties'].sum() / mannixKeyStats['gain'].sum()

# %% Mid-court turnovers and winning games

#Read in regular season player stats
playerStatsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                      years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                      fileStem = 'playerStats',
                                                      matchOptions = ['regular', 'final'],
                                                      joined = True, addSquadNames = True)

#Read in team stats over concurrent period
teamStatsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                    years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                    fileStem = 'teamStats',
                                                    matchOptions = ['regular', 'final'],
                                                    joined = True, addSquadNames = True)

#Get line-up data over concurrent period
lineUpsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                  years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                  fileStem = 'lineUps',
                                                  matchOptions = ['regular', 'final'],
                                                  joined = True, addSquadNames = True)

#Set-up dictionary to store data
turnOverData = {'matchId': [], 'playerId': [], 'year': [], 'squadId': [], 'roundNo': [],
                'primaryPos': [], 'generalPlayTurnover': []}

#Loop through player stat entries
for ii in playerStatsSuperNetball.index:
    
    #Get details for current entry
    matchId = playerStatsSuperNetball.iloc[ii]['matchId']
    playerId = playerStatsSuperNetball.iloc[ii]['playerId']
    squadId = playerStatsSuperNetball.iloc[ii]['squadId']
    year = playerStatsSuperNetball.iloc[ii]['year']
    roundNo = playerStatsSuperNetball.iloc[ii]['roundNo']
    gpTO = playerStatsSuperNetball.iloc[ii]['generalPlayTurnovers']
    
    #Get players primary position
    #Get current match line-ups
    currLineUps = lineUpsSuperNetball.loc[lineUpsSuperNetball['matchId'] == matchId,]
    
    #Loop through and extract durations of court positions
    posDurations = []
    for courtPos in courtPositions:
        posDurations.append(currLineUps.loc[currLineUps[courtPos] == playerId,]['duration'].sum())
    #Identify maximum time if any greater than zero
    if np.sum(posDurations) > 0:
        primaryPos = courtPositions[np.argmax(posDurations)]
    else:
        primaryPos = 'B'
        
    #Append data to dictionary
    turnOverData['matchId'].append(matchId)
    turnOverData['playerId'].append(playerId)
    turnOverData['year'].append(year)
    turnOverData['squadId'].append(squadId)
    turnOverData['roundNo'].append(roundNo)
    turnOverData['primaryPos'].append(primaryPos)
    turnOverData['generalPlayTurnover'].append(gpTO)
    
#Convert to dataframe
turnOverData_df = pd.DataFrame.from_dict(turnOverData)

#Extract mid-court turnover data
turnoverData_midCourt = turnOverData_df.loc[turnOverData_df['primaryPos'].isin(['WD', 'C', 'WA'])]

#Group by match and squad Id and sum turnovers
turnoverData_midCourt_total = turnoverData_midCourt.groupby(['matchId', 'squadId']).sum(
    numeric_only = True)['generalPlayTurnover'].reset_index(drop = False)

#Set up dictionary to store data
turnoverCorr = {'matchId': [], 'toDiff': [], 'scoreDiff': []}

#Loop through matches
for matchId in turnoverData_midCourt_total['matchId'].unique():
    
    #Extract the squads and turnovers
    squad1, squad2 = tuple(turnoverData_midCourt_total.loc[turnoverData_midCourt_total['matchId'] == matchId,
                                                           ]['squadId'].values)
    to1, to2 = tuple(turnoverData_midCourt_total.loc[turnoverData_midCourt_total['matchId'] == matchId,
                                                     ]['generalPlayTurnover'].values)
    
    #Extract the team scores from the corresponding match
    if teamStatsSuperNetball.loc[teamStatsSuperNetball['matchId'] == matchId, ]['year'].values[0] < 2020:
        score1 = teamStatsSuperNetball.loc[(teamStatsSuperNetball['matchId'] == matchId) & 
                                           (teamStatsSuperNetball['squadId'] == squad1),
                                           ]['goals'].values[0]
        score2 = teamStatsSuperNetball.loc[(teamStatsSuperNetball['matchId'] == matchId) & 
                                           (teamStatsSuperNetball['squadId'] == squad2),
                                           ]['goals'].values[0]
    else:
        score1 = teamStatsSuperNetball.loc[(teamStatsSuperNetball['matchId'] == matchId) & 
                                           (teamStatsSuperNetball['squadId'] == squad1),
                                           ]['points'].values[0]
        score2 = teamStatsSuperNetball.loc[(teamStatsSuperNetball['matchId'] == matchId) & 
                                           (teamStatsSuperNetball['squadId'] == squad2),
                                           ]['points'].values[0]
        
    #Append data
    turnoverCorr['matchId'].append(matchId)
    turnoverCorr['toDiff'].append(to2 - to1)
    turnoverCorr['scoreDiff'].append(score2 - score1)
            
#Convert to dataframe
turnoverCorr_df = pd.DataFrame.from_dict(turnoverCorr)

#Run linear models on data

#Centre pass
regr_TO = linear_model.LinearRegression()
regr_TO.fit(turnoverCorr_df['toDiff'].to_numpy().reshape(-1,1),
            turnoverCorr_df['scoreDiff'].to_numpy().reshape(-1,1))
pred_score = regr_TO.predict(turnoverCorr_df['toDiff'].to_numpy().reshape(-1,1))
print("Mean squared error: %.2f" % mean_squared_error(turnoverCorr_df['scoreDiff'].to_numpy().reshape(-1,1), pred_score))
print("Coefficient of determination: %.2f" % r2_score(turnoverCorr_df['scoreDiff'].to_numpy().reshape(-1,1), pred_score))
    
#Review scatter plot
plt.scatter(turnoverCorr_df['toDiff'], turnoverCorr_df['scoreDiff'])

# %% Prediction review

#Read in team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'],
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

#Get average margin by round
avgRoundMargin = marginData.groupby(['year', 'roundNo']).mean(numeric_only = True)['margin']

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

# %% ----- End of 10_rd10_analysis.py ----- %% #

