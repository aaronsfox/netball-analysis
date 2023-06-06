# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 12 SSN match-ups.
    
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
    
# %% Lightning low penalties?

#Read in team stats for year
teamStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2023],
                                            fileStem = 'teamStats',
                                            matchOptions = ['regular'],
                                            joined = True, addSquadNames = True)

#Grab penalties
teamStats2023_penalties = teamStats2023[['roundNo', 'squadName', 'penalties']]

# %% Obstruction penalties

#Read in team stats over time
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Read in player stats over time
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Extract obstruction penalties from games
teamStats_obstructionPenalties = teamStats[['year', 'roundNo', 'matchType', 'squadName', 'oppSquadName',
                                            'obstructionPenalties']]

#Set dictionary to record obstruction data to
obstructionData = {'playerId': [], 'playerName': [], 'squadName': [], 'year': [], 'roundNo': [], 'matchType': [],
                   'minsWD': [], 'minsGD': [], 'minsGK': [], 'minsDEF': [], 'obstructionPenalties': []}

#Loop through stats and extract penalties for players who were in defensive positions
#for at least 30 mins in a game
for ii in playerStats.index:
    
    #Extract player, squad and match Id
    playerId = playerStats.iloc[ii]['playerId']
    matchId =  playerStats.iloc[ii]['matchId']
    squadId =  playerStats.iloc[ii]['squadId']
    
    #Identify sum of minutes in defensive positions for this player and match
    minsWD = lineUpData.loc[(lineUpData['matchId'] == matchId) &
                            (lineUpData['squadId'] == squadId) &
                            (lineUpData['WD'] == playerId),]['duration'].sum() / 60
    minsGD = lineUpData.loc[(lineUpData['matchId'] == matchId) &
                            (lineUpData['squadId'] == squadId) &
                            (lineUpData['GD'] == playerId),]['duration'].sum() / 60
    minsGK = lineUpData.loc[(lineUpData['matchId'] == matchId) &
                            (lineUpData['squadId'] == squadId) &
                            (lineUpData['GK'] == playerId),]['duration'].sum() / 60
    minsDEF = minsWD + minsGD + minsGK
    
    #Check for minutes exceeding threshold
    if minsDEF >= 30:
        
        #Extract the details to dictionary
        obstructionData['playerId'].append(playerId)
        obstructionData['playerName'].append(playerData.loc[(playerData['playerId'] == playerId) &
                                                            (playerData['year'] == playerStats.iloc[ii]['year']),
                                                            ]['displayName'].values[0])
        obstructionData['squadName'].append(playerStats.iloc[ii]['squadName'])
        obstructionData['year'].append(playerStats.iloc[ii]['year'])
        obstructionData['roundNo'].append(playerStats.iloc[ii]['roundNo'])
        obstructionData['matchType'].append(playerStats.iloc[ii]['matchType'])
        obstructionData['minsWD'].append(minsWD)
        obstructionData['minsGD'].append(minsGD)
        obstructionData['minsGK'].append(minsGK)
        obstructionData['minsDEF'].append(minsDEF)
        obstructionData['obstructionPenalties'].append(playerStats.iloc[ii]['obstructionPenalties'])
        
#Convert to dataframe
obstructionData_df = pd.DataFrame.from_dict(obstructionData)

#Extract those with 0 obstruction penalties and get a count of the occurrences
obstructionFreeCount = obstructionData_df.loc[obstructionData_df['obstructionPenalties'] == 0,
                                              ].groupby(['playerId', 'playerName']).count()[['obstructionPenalties']]
    
# %% Biggest score differentials week to week

#Grab in regular season team stats
teamStatsRegular = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = 'all',
                                               fileStem = 'teamStats',
                                               matchOptions = ['regular'],
                                               joined = True, addSquadNames = True)

#Get the list of years to work through
yearsOfData = teamStatsRegular['year'].unique()
yearsOfData.sort()

#Create dictionary to store data
scoreDiffData = {'year': [], 'roundNo': [], 'squadName': [],
                 'currRoundScore': [], 'priorRoundScore': [], 'scoreDiff': []}

#Loop through years
for year in yearsOfData:
    
    #Get the rounds for the current year
    yearRounds = list(teamStatsRegular.loc[teamStatsRegular['year'] == year,
                                           ]['roundNo'].unique())
    yearRounds.sort()
    
    #Get the squad Id's for the year
    yearSquads = list(teamStatsRegular.loc[teamStatsRegular['year'] == year,
                                           ]['squadName'].unique())
    yearSquads.sort()
    
    #Set the scoring variable to use
    if year < 2020:
        scoreVar = 'goals'
    else:
        scoreVar = 'points'
    
    #Loop through squads and rounds
    for squadName in yearSquads:
        for roundNo in yearRounds:
            
            #Ensure first roundis skipped
            if roundNo > 1:
                
                #Get score from current round
                #Take the average to cover for instances where multiple games are played
                currRoundScore = teamStatsRegular.loc[(teamStatsRegular['year'] == year) &
                                                      (teamStatsRegular['roundNo'] == roundNo) &
                                                      (teamStatsRegular['squadName'] == squadName),
                                                      ][scoreVar].mean()
                
                #Get score from prior round
                #Take the average to cover for instances where multiple games are played
                priorRoundScore = teamStatsRegular.loc[(teamStatsRegular['year'] == year) &
                                                       (teamStatsRegular['roundNo'] == (roundNo-1)) &
                                                       (teamStatsRegular['squadName'] == squadName),
                                                       ][scoreVar].mean()
                
                #Calculate differential
                scoreDiff = currRoundScore - priorRoundScore
                
                #Append data to dictionary
                scoreDiffData['year'].append(year)
                scoreDiffData['roundNo'].append(roundNo)
                scoreDiffData['squadName'].append(squadName)
                scoreDiffData['currRoundScore'].append(currRoundScore)
                scoreDiffData['priorRoundScore'].append(priorRoundScore)
                scoreDiffData['scoreDiff'].append(scoreDiff)
                
#Convert to dataframe
scoreDiffData_df = pd.DataFrame.from_dict(scoreDiffData)
                
# %% Scoring consistency this year

#Remove Thunderbirds-Swifts round 2 score from calcuations
scoringConsistencyCalc = teamStats2023[['matchId', 'roundNo', 'squadName', 'points']]
scoringConsistencyCalc = scoringConsistencyCalc.loc[scoringConsistencyCalc['matchId'] != 120450202,]

#Get each teams average and standard deviation for scoring
avgScore = scoringConsistencyCalc.groupby('squadName').mean(numeric_only = True)['points']
sdScore = scoringConsistencyCalc.groupby('squadName').std(numeric_only = True)['points']

#Loop through and calculate each teams consistency rating
scoreConsistencyRating = {squadName: sdScore[squadName] / avgScore[squadName] for squadName in avgScore.index}

# %% Wallam's record total?

#Create dictionary to store total score and relative to team
playerScoringData = {'year': [], 'roundNo': [], 'squadName': [], 'matchType': [],
                     'playerId': [], 'playerName': [],
                     'playerScore': [], 'teamScore': [], 'scoreContribution': []}

#Loop through player stats
for ii in playerStats.index:
    
    #Check for scoring player
    if playerStats.iloc[ii]['goals'] > 0:
        
        #Get player, match and squad Id
        playerId = playerStats.iloc[ii]['playerId']
        matchId =  playerStats.iloc[ii]['matchId']
        squadId =  playerStats.iloc[ii]['squadId']
        
        #Extract total score
        if playerStats.iloc[ii]['year'] < 2020:
            playerScore = playerStats.iloc[ii]['goals']
        else:
            playerScore = playerStats.iloc[ii]['points']
            
        #Extract the team score for the match
        if playerStats.iloc[ii]['year'] < 2020:
            teamScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                                      (teamStats['squadId'] == squadId),
                                      ]['goals'].values[0]
        else:
            teamScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                                      (teamStats['squadId'] == squadId),
                                      ]['points'].values[0]
            
        #Append data
        playerScoringData['year'].append(playerStats.iloc[ii]['year'])
        playerScoringData['roundNo'].append(playerStats.iloc[ii]['roundNo'])
        playerScoringData['squadName'].append(playerStats.iloc[ii]['squadName'])
        playerScoringData['matchType'].append(playerStats.iloc[ii]['matchType'])
        playerScoringData['playerId'].append(playerId)
        playerScoringData['playerName'].append(playerData.loc[(playerData['playerId'] == playerId) &
                                                              (playerData['year'] == playerStats.iloc[ii]['year']),
                                                              ]['displayName'].values[0])
        playerScoringData['playerScore'].append(playerScore)
        playerScoringData['teamScore'].append(teamScore)
        playerScoringData['scoreContribution'].append(playerScore / teamScore * 100)
        
#Convert to dataframe
playerScoringData_df = pd.DataFrame.from_dict(playerScoringData)
        

# %% Is there a scoring end in netball?

#Read in team period stats
teamPeriodStatsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                          years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                                          fileStem = 'teamPeriodStats',
                                                          matchOptions = ['regular', 'final'],
                                                          joined = True, addSquadNames = True)

#Create a dictionary to store data in
scoringEndDifferences = {'matchId': [], 'year': [], 'roundNo': [], 'squadNames': [],
                         'highEnd': [], 'lowEnd': []}

#Loop through match Id's
for matchId in teamPeriodStatsSuperNetball['matchId'].unique():
    
    #Get the two squads from the match
    matchSquads = list(teamPeriodStatsSuperNetball.loc[teamPeriodStatsSuperNetball['matchId'] == matchId,
                                                       ]['squadName'].unique())
    
    #Set scoring variable
    if teamPeriodStatsSuperNetball.loc[teamPeriodStatsSuperNetball['matchId'] == matchId,]['year'].unique()[0] < 2020:
        scoreVar = 'goals'
    else:
        scoreVar = 'points'
    
    #Extract the score from each 'end' and team
    end1_team1 = teamPeriodStatsSuperNetball.loc[(teamPeriodStatsSuperNetball['matchId'] == matchId) &
                                                 (teamPeriodStatsSuperNetball['squadName'] == matchSquads[0]) &
                                                 (teamPeriodStatsSuperNetball['period'].isin([1,3])),
                                                 ][scoreVar].sum()
    end1_team2 = teamPeriodStatsSuperNetball.loc[(teamPeriodStatsSuperNetball['matchId'] == matchId) &
                                                 (teamPeriodStatsSuperNetball['squadName'] == matchSquads[1]) &
                                                 (teamPeriodStatsSuperNetball['period'].isin([2,4])),
                                                 ][scoreVar].sum()
    end2_team1 = teamPeriodStatsSuperNetball.loc[(teamPeriodStatsSuperNetball['matchId'] == matchId) &
                                                 (teamPeriodStatsSuperNetball['squadName'] == matchSquads[0]) &
                                                 (teamPeriodStatsSuperNetball['period'].isin([2,4])),
                                                 ][scoreVar].sum()
    end2_team2 = teamPeriodStatsSuperNetball.loc[(teamPeriodStatsSuperNetball['matchId'] == matchId) &
                                                 (teamPeriodStatsSuperNetball['squadName'] == matchSquads[1]) &
                                                 (teamPeriodStatsSuperNetball['period'].isin([1,3])),
                                                 ][scoreVar].sum()
    end1_total = end1_team1 + end1_team2
    end2_total = end2_team1 + end2_team2
    
    #Append data to dictionary
    scoringEndDifferences['matchId'].append(matchId)
    scoringEndDifferences['year'].append(teamPeriodStatsSuperNetball.loc[teamPeriodStatsSuperNetball['matchId'] == matchId,]['year'].unique()[0])
    scoringEndDifferences['roundNo'].append(teamPeriodStatsSuperNetball.loc[teamPeriodStatsSuperNetball['matchId'] == matchId,]['roundNo'].unique()[0])
    scoringEndDifferences['squadNames'].append(matchSquads)
    if end1_total >= end2_total:
        scoringEndDifferences['highEnd'].append(end1_total)
        scoringEndDifferences['lowEnd'].append(end2_total)
    else:
        scoringEndDifferences['lowEnd'].append(end1_total)
        scoringEndDifferences['highEnd'].append(end2_total)
        
#Convert to dataframe
scoringEndDifferences_df = pd.DataFrame.from_dict(scoringEndDifferences)

#Calculate difference
scoringEndDifferences_df['diff'] =  scoringEndDifferences_df['highEnd'] - scoringEndDifferences_df['lowEnd']
    
#Calculate the average and 95% confidence intervals for the scoring end in a match
avgDiff = scoringEndDifferences_df['diff'].mean()
avgDiff_lowerCI = scoringEndDifferences_df['diff'].mean() - (1.96 * (scoringEndDifferences_df['diff'].std() / np.sqrt(len(scoringEndDifferences_df))))
avgDiff_upperCI = scoringEndDifferences_df['diff'].mean() + (1.96 * (scoringEndDifferences_df['diff'].std() / np.sqrt(len(scoringEndDifferences_df))))

# %% Prediction review

#Extract total penalty count for each match this year
penaltyTotal2023 = teamStats2023.groupby('matchId').sum(numeric_only = True)['penalties']

# %% Prediction

#Extract team stats over Super Netball years
teamStatsSuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                                    fileStem = 'teamStats',
                                                    matchOptions = ['regular'],
                                                    joined = True, addSquadNames = True)

#Create dictionary to store data in
spookyRoundData = {'year': [], 'squadName': [], 'margin': [], 'result': []}

#Review team results for round 13 over Super Netball years
for squadName in teamStatsSuperNetball['squadName'].unique():
    
    #Extract score and opposition score from round 13 match across years
    for year in [2017, 2018, 2019, 2020, 2021, 2022]:
        
        #Check for scoring variable
        if year < 2020:
            scoreVar = 'goals'
        else:
            scoreVar = 'points'
            
        #Extract scores
        try:
            squadScore = teamStatsSuperNetball.loc[(teamStatsSuperNetball['squadName'] == squadName) &
                                                   (teamStatsSuperNetball['year'] == year) &
                                                   (teamStatsSuperNetball['roundNo'] == 13),
                                                   ][scoreVar].values[0]
            oppScore = teamStatsSuperNetball.loc[(teamStatsSuperNetball['oppSquadName'] == squadName) &
                                                 (teamStatsSuperNetball['year'] == year) &
                                                 (teamStatsSuperNetball['roundNo'] == 13),
                                                 ][scoreVar].values[0]
            
            #Append data
            spookyRoundData['year'].append(year)
            spookyRoundData['squadName'].append(squadName)
            spookyRoundData['margin'].append(squadScore - oppScore)
            if (squadScore - oppScore) < 0:
                spookyRoundData['result'].append('loss')
            elif (squadScore - oppScore) > 0:
                spookyRoundData['result'].append('win')
            else:
                spookyRoundData['result'].append('draw')
                
        except:
            
            print('Data not available...')
            
#Convert to dataframe
spookyRoundData_df = pd.DataFrame.from_dict(spookyRoundData)

# %% ----- End of 12_rd12_analysis.py ----- %% #