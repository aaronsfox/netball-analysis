# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the semi finals SSN match-ups.
    
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

# %% Perfect Power 5s

#Read in scoreflow data from Super Shot era
scoreFlowData_superShotEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                         years = [2020, 2021, 2022, 2023],
                                                         fileStem = 'scoreFlow',
                                                         matchOptions = ['regular', 'final'],
                                                         joined = True, addSquadNames = True)

#Calculate shooting percentage in the Power 5 periods
shootingPower5 = {'matchId': [], 'year': [], 'roundNo': [], 'matchType': [], 'period': [], 'squadName': [], 
                  'standardAttempts': [], 'standardMakes': [], 'standardMisses': [], 'standardPer': [],
                  'superAttempts': [], 'superMakes': [], 'superMisses': [], 'superPer': [],
                  'totalAttempts': [], 'totalMakes': [], 'totalMisses': [], 'totalPer': []}

#Loop through match Id's
for matchId in scoreFlowData_superShotEra['matchId'].unique():
    
    #Get the squad names for this match
    squadNames = scoreFlowData_superShotEra.loc[scoreFlowData_superShotEra['matchId'] == matchId,
                                                ]['squadName'].unique()
    
    #Loop through squads
    for squad in squadNames:
        
        #Get the period numbers
        periods = list(scoreFlowData_superShotEra.loc[(scoreFlowData_superShotEra['matchId'] == matchId) &
                                                      (scoreFlowData_superShotEra['squadName'] == squad),
                                                      ]['period'].unique())
        periods.sort()
        
        #Loop through periods of data
        for periodNo in periods:
            
            #Check for extra time period to take all data vs. Power 5
            if periodNo <= 4:
                
                #Extract shots from last 5 minutes
                currScoringData = scoreFlowData_superShotEra.loc[(scoreFlowData_superShotEra['matchId'] == matchId) &
                                                                 (scoreFlowData_superShotEra['squadName'] == squad) &
                                                                 (scoreFlowData_superShotEra['period'] == periodNo) &
                                                                 (scoreFlowData_superShotEra['periodSeconds'] >= 600),
                                                                 ]
                
            else:
                
                #Take all the data
                currScoringData = scoreFlowData_superShotEra.loc[(scoreFlowData_superShotEra['matchId'] == matchId) &
                                                                 (scoreFlowData_superShotEra['squadName'] == squad) &
                                                                 (scoreFlowData_superShotEra['period'] == periodNo),
                                                                 ]
        
        #Check for length of scoring data for any shots
        if len(currScoringData) > 0:
                
            #Get a count of the score names from the data
            scoreCounts = currScoringData.groupby('scoreName').count()['matchId']
            
            #Extract scoring counts
            #Need to try/except these as some might not be in the data series
            #Standard goals
            try:
                standardMakes = scoreCounts['goal']
            except:
                standardMakes = 0
            #Standard misses
            try:
                standardMisses = scoreCounts['miss']
            except:
                standardMisses = 0
            #Super makes
            try:
                superMakes = scoreCounts['2pt Goal']
            except:
                superMakes = 0
            #Super misses
            try:
                superMisses = scoreCounts['2pt Miss']
            except:
                superMisses = 0
                
            #Calculate total attempts
            standardAttempts = standardMakes + standardMisses
            superAttempts = superMakes + superMisses
            
            #Append data to dictionary
            shootingPower5['matchId'].append(matchId)
            shootingPower5['year'].append(currScoringData['year'].unique()[0])
            shootingPower5['roundNo'].append(currScoringData['roundNo'].unique()[0])
            shootingPower5['matchType'].append(currScoringData['matchType'].unique()[0])
            shootingPower5['period'].append(periodNo)
            shootingPower5['squadName'].append(squad)
            shootingPower5['standardAttempts'].append(standardAttempts)
            shootingPower5['standardMakes'].append(standardMakes)
            shootingPower5['standardMisses'].append(standardMisses)
            try:
                shootingPower5['standardPer'].append(standardMakes/standardAttempts*100)
            except:
                shootingPower5['standardPer'].append(np.nan)
            shootingPower5['superAttempts'].append(superAttempts)
            shootingPower5['superMakes'].append(superMakes)
            shootingPower5['superMisses'].append(superMisses)
            try:
                shootingPower5['superPer'].append(superMakes/superAttempts*100)
            except:
                shootingPower5['superPer'].append(np.nan)
            shootingPower5['totalAttempts'].append(standardAttempts+superAttempts)
            shootingPower5['totalMakes'].append(standardMakes+superMakes)
            shootingPower5['totalMisses'].append(standardMisses+superMisses)
            try:
                shootingPower5['totalPer'].append((standardMakes+superMakes)/(standardAttempts+superAttempts)*100)
            except:
                shootingPower5['totalPer'].append(np.nan)
        
#Convert to dataframe
shootingPower5_df = pd.DataFrame.from_dict(shootingPower5)

#Review number of 100% efforts
shootingPer100_n = len(shootingPower5_df.loc[shootingPower5_df['totalPer'] == 100,])

#Extract 100% performances and count by team
teamShootingPer100_n = shootingPower5_df.loc[shootingPower5_df['totalPer'] == 100,].groupby('squadName').count()['matchId']

# %% GK performances

#Extract player period stats from this year
playerPeriodStats_2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2023],
                                                     fileStem = 'playerPeriodStats',
                                                     matchOptions = ['regular', 'final'],
                                                     joined = True, addSquadNames = True)

#Extract line-up stats from this year
lineUps_2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                           years = [2023],
                                           fileStem = 'lineUps',
                                           matchOptions = ['regular', 'final'],
                                           joined = True, addSquadNames = True)

#Identify players who plauyed in GK the entire match
gkFullMatch = {'matchId': [], 'roundNo': [], 'squadName': [], 'playerId': []}

#Loop through match Id's
for matchId in lineUps_2023['matchId'].unique():
    
    #Extract the squads for the game
    squadNames = lineUps_2023.loc[lineUps_2023['matchId'] == matchId,
                                  ]['squadName'].unique()
    
    #Loop through squads and identify if a player was in GK the entire game
    for squad in squadNames:
        
        #Check for single GK player
        if len(lineUps_2023.loc[(lineUps_2023['matchId'] == matchId) &
                             (lineUps_2023['squadName'] == squad),
                             ]['GK'].unique()) == 1:
            
            #Extract this to the dictionary
            gkFullMatch['matchId'].append(matchId)
            gkFullMatch['roundNo'].append(lineUps_2023.loc[lineUps_2023['matchId'] == matchId,]['roundNo'].unique()[0])
            gkFullMatch['squadName'].append(squad)
            gkFullMatch['playerId'].append(lineUps_2023.loc[(lineUps_2023['matchId'] == matchId) &
                                                            (lineUps_2023['squadName'] == squad),
                                                            ]['GK'].unique()[0])
        
#Convert to dataframe
gkFullMatch_df = pd.DataFrame.from_dict(gkFullMatch)

#Create a dictionary to store relevant statistics for GK performances
gkPerformances = {'matchId': [], 'matchType': [], 'roundNo': [], 'squadName': [], 'playerId': [],
                  'gainsQ1': [], 'deflectionsQ1': [], 'reboundsQ1': [], 'interceptsQ1': [], 'netPointsQ1': [],
                  'gains3Qavg': [], 'deflections3Qavg': [], 'rebounds3Qavg': [], 'intercepts3Qavg': [], 'netPoints3Qavg': [],
                  'gainsQ4': [], 'deflectionsQ4': [], 'reboundsQ4': [], 'interceptsQ4': [], 'netPointsQ4': [],
                  'gainsQ1-Q4': [], 'deflectionsQ1-Q4': [], 'reboundsQ1-Q4': [], 'interceptsQ1-Q4': [], 'netPointsQ1-Q4': [],
                  'gainsQavg-Q4': [], 'deflectionsQavg-Q4': [], 'reboundsQavg-Q4': [], 'interceptsQavg-Q4': [], 'netPointsQavg-Q4': []}

#Loop through full match instances
for ii in gkFullMatch_df.index:
        
    #Extract the current players period statistics
    currPlayerStats = playerPeriodStats_2023.loc[(playerPeriodStats_2023['matchId'] == gkFullMatch_df.iloc[ii]['matchId']) &
                                                 (playerPeriodStats_2023['roundNo'] == gkFullMatch_df.iloc[ii]['roundNo']) &
                                                 (playerPeriodStats_2023['playerId'] == gkFullMatch_df.iloc[ii]['playerId']) &
                                                 (playerPeriodStats_2023['squadName'] == gkFullMatch_df.iloc[ii]['squadName'])]
    
    #Check if there is a 4th quarter given shortened match
    if max(currPlayerStats['period']) >= 4:    
    
        #Append generic match details
        gkPerformances['matchId'].append(gkFullMatch_df.iloc[ii]['matchId'])
        gkPerformances['matchType'].append(currPlayerStats['matchType'].unique()[0])
        gkPerformances['roundNo'].append(gkFullMatch_df.iloc[ii]['roundNo'])
        gkPerformances['squadName'].append(gkFullMatch_df.iloc[ii]['squadName'])
        gkPerformances['playerId'].append(gkFullMatch_df.iloc[ii]['playerId'])
        
        #Collate Q1 statistics
        gkPerformances['gainsQ1'].append(currPlayerStats.loc[currPlayerStats['period'] == 1,]['gain'].values[0])
        gkPerformances['deflectionsQ1'].append(currPlayerStats.loc[currPlayerStats['period'] == 1,]['deflections'].values[0])
        gkPerformances['reboundsQ1'].append(currPlayerStats.loc[currPlayerStats['period'] == 1,]['rebounds'].values[0])
        gkPerformances['interceptsQ1'].append(currPlayerStats.loc[currPlayerStats['period'] == 1,]['intercepts'].values[0])
        gkPerformances['netPointsQ1'].append(currPlayerStats.loc[currPlayerStats['period'] == 1,]['netPoints'].values[0])
        
        #Collate 3Q avg. statistics
        gkPerformances['gains3Qavg'].append(currPlayerStats.loc[currPlayerStats['period'] <= 3,]['gain'].mean())
        gkPerformances['deflections3Qavg'].append(currPlayerStats.loc[currPlayerStats['period'] <= 3,]['deflections'].mean())
        gkPerformances['rebounds3Qavg'].append(currPlayerStats.loc[currPlayerStats['period'] <= 3,]['rebounds'].mean())
        gkPerformances['intercepts3Qavg'].append(currPlayerStats.loc[currPlayerStats['period'] <= 3,]['intercepts'].mean())
        gkPerformances['netPoints3Qavg'].append(currPlayerStats.loc[currPlayerStats['period'] <= 3,]['netPoints'].mean())
        
        #Collate Q4 statstics
        gkPerformances['gainsQ4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['gain'].values[0])
        gkPerformances['deflectionsQ4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['deflections'].values[0])
        gkPerformances['reboundsQ4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['rebounds'].values[0])
        gkPerformances['interceptsQ4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['intercepts'].values[0])
        gkPerformances['netPointsQ4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['netPoints'].values[0])
        
        #Collate Q1 to Q4 differential
        gkPerformances['gainsQ1-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['gain'].values[0] - currPlayerStats.loc[currPlayerStats['period'] == 1,]['gain'].values[0])
        gkPerformances['deflectionsQ1-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['deflections'].values[0] - currPlayerStats.loc[currPlayerStats['period'] == 1,]['deflections'].values[0])
        gkPerformances['reboundsQ1-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['rebounds'].values[0] - currPlayerStats.loc[currPlayerStats['period'] == 1,]['rebounds'].values[0])
        gkPerformances['interceptsQ1-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['intercepts'].values[0] - currPlayerStats.loc[currPlayerStats['period'] == 1,]['intercepts'].values[0])
        gkPerformances['netPointsQ1-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['netPoints'].values[0] - currPlayerStats.loc[currPlayerStats['period'] == 1,]['netPoints'].values[0])
            
        #Collate Q4 to 3Q average differential
        gkPerformances['gainsQavg-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['gain'].values[0] - currPlayerStats.loc[currPlayerStats['period'] <= 3,]['gain'].mean())
        gkPerformances['deflectionsQavg-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['deflections'].values[0] - currPlayerStats.loc[currPlayerStats['period'] <= 3,]['deflections'].mean())
        gkPerformances['reboundsQavg-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['rebounds'].values[0] - currPlayerStats.loc[currPlayerStats['period'] <= 3,]['rebounds'].mean())
        gkPerformances['interceptsQavg-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['intercepts'].values[0] - currPlayerStats.loc[currPlayerStats['period'] <= 3,]['intercepts'].mean())
        gkPerformances['netPointsQavg-Q4'].append(currPlayerStats.loc[currPlayerStats['period'] == 4,]['netPoints'].values[0] - currPlayerStats.loc[currPlayerStats['period'] <= 3,]['netPoints'].mean())    

#Convert to dataframe
gkPerformance_df = pd.DataFrame.from_dict(gkPerformances)

#Add player names
playerName = []
for playerId in gkPerformance_df['playerId']:
    playerName.append(playerData.loc[(playerData['year'] == 2023) &
                                     (playerData['playerId'] == playerId),
                                     ]['displayName'].values[0])
gkPerformance_df['playerName'] = playerName    

#Split into separate dataframes
gkPerformance_Q4vQ1 = gkPerformance_df[['matchId', 'matchType', 'roundNo', 'squadName', 'playerId', 'playerName',
                                        'gainsQ1-Q4', 'deflectionsQ1-Q4', 'reboundsQ1-Q4', 'interceptsQ1-Q4', 'netPointsQ1-Q4',]]
gkPerformance_Q4vQvg = gkPerformance_df[['matchId', 'matchType', 'roundNo', 'squadName', 'playerId', 'playerName',
                                         'gainsQavg-Q4', 'deflectionsQavg-Q4', 'reboundsQavg-Q4', 'interceptsQavg-Q4', 'netPointsQavg-Q4',]]
    
# %% Finals performers

#Extract player and team stats from finals
playerStats_finals = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = 'all',
                                                 fileStem = 'playerStats',
                                                 matchOptions = ['final'],
                                                 joined = True, addSquadNames = True)
teamStats_finals = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = 'all',
                                               fileStem = 'teamStats',
                                               matchOptions = ['final'],
                                               joined = True, addSquadNames = True)

#Extract players who were on court for final
playerStats_finals = playerStats_finals.loc[playerStats_finals['minutesPlayed'] > 0,].reset_index(drop = True)

#Collate data on player finals performances
finalsPerformers = {'matchId': [], 'year': [], 'playerId': [], 'squadName': [],
                    'result': [], 'netPoints': []}

#Loop through unique players featuring in the finals dataset
for playerId in playerStats_finals['playerId'].unique():
    
    #Extract players stats from finals
    currPlayerStats_finals = playerStats_finals.loc[playerStats_finals['playerId'] == playerId,].reset_index(drop = True)
    
    #Loop through matches to extract result
    for ii in currPlayerStats_finals.index:
        
        #Identify match data
        matchId = currPlayerStats_finals.iloc[ii]['matchId']
        squadId = currPlayerStats_finals.iloc[ii]['squadId']
        year = currPlayerStats_finals.iloc[ii]['year']
        
        #Get result for players team
        #Extract scores
        if year < 2020:
            teamScore = teamStats_finals.loc[(teamStats_finals['matchId'] == matchId) &
                                             (teamStats_finals['squadId'] == squadId),
                                             ]['goals'].values[0]
            oppScore = teamStats_finals.loc[(teamStats_finals['matchId'] == matchId) &
                                            (teamStats_finals['squadId'] != squadId),
                                            ]['goals'].values[0]
        else:
            teamScore = teamStats_finals.loc[(teamStats_finals['matchId'] == matchId) &
                                             (teamStats_finals['squadId'] == squadId),
                                             ]['points'].values[0]
            oppScore = teamStats_finals.loc[(teamStats_finals['matchId'] == matchId) &
                                            (teamStats_finals['squadId'] != squadId),
                                            ]['points'].values[0]
        #Determine results
        if teamScore > oppScore:
            result = 'win'
        elif teamScore < oppScore:
            result = 'loss'
        else:
            result = 'draw'
            
        #Extract NetPoints
        netPoints = currPlayerStats_finals.iloc[ii]['netPoints']
        
        #Append to data dictionary
        finalsPerformers['matchId'].append(matchId)
        finalsPerformers['year'].append(year)
        finalsPerformers['playerId'].append(playerId)
        finalsPerformers['squadName'].append(currPlayerStats_finals.iloc[ii]['squadName'])
        finalsPerformers['result'].append(result)
        finalsPerformers['netPoints'].append(netPoints)

#Convert to dataframe
finalsPerformers_df = pd.DataFrame.from_dict(finalsPerformers)

#Add player names
playerName = []
for playerId in finalsPerformers_df['playerId']:
    playerName.append(playerData.loc[playerData['playerId'] == playerId,
                                     ]['displayName'].values[-1])
finalsPerformers_df['playerName'] = playerName

#Get a count of finals matches
finalsMatchesCount = finalsPerformers_df.groupby('playerName').count()['matchId']

#Get a count of finals wins
finalsWinsCount = finalsPerformers_df.loc[finalsPerformers_df['result'] == 'win'].groupby('playerName').count()['matchId']

#Get average NetPoints
finalsNetPointsAvg = finalsPerformers_df.groupby('playerName').mean(numeric_only = True)['netPoints']

# %% Ladder position vs. grand final win

#Read in team and team period stats over Super Netball years
teamStats_superNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                                     fileStem = 'teamStats',
                                                     matchOptions = ['regular'],
                                                     joined = True, addSquadNames = True)
teamPeriodStats_superNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                           years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                                           fileStem = 'teamPeriodStats',
                                                           matchOptions = ['regular'],
                                                           joined = True, addSquadNames = True)

#Create dictionary of premiers for each year
premiers = {2017: 'Lightning',
            2018: 'Lightning',
            2019: 'Swifts',
            2020: 'Vixens',
            2021: 'Swifts',
            2022: 'Fever'}

#Loop through years
for year in premiers.keys():
    
    #Identify number of rounds
    nRounds = teamStats_superNetball.loc[teamStats_superNetball['year'] == year,]['roundNo'].max()
    
    #Extract current years data without final round
    teamStatsCurrentYear = teamStats_superNetball.loc[(teamStats_superNetball['year'] == year) &
                                                      (teamStats_superNetball['roundNo'] <= nRounds),].reset_index(drop = True)
    
    #Extract team period stats for current year without final round (if necessary)
    if year in [2018,2019]:
        teamPeriodStatsCurrentYear = teamPeriodStats_superNetball.loc[(teamPeriodStats_superNetball['year'] == year) &
                                                                      (teamPeriodStats_superNetball['roundNo'] < nRounds),].reset_index(drop = True)
    
    #Create dataframe to store ladder data
    ladderData = pd.DataFrame(list(zip([0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
                                       [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0])),
                              columns = ['points', 'W', 'D', 'L', 'GF', 'GA'],
                              index = list(teamStatsCurrentYear['squadName'].unique()))
    
    #Loop through match Id's to allocate ladder points and goals for/against
    for matchId in teamStatsCurrentYear['matchId'].unique():
        
        #Get current match data
        currMatch = teamStatsCurrentYear.loc[teamStatsCurrentYear['matchId'] == matchId,].reset_index(drop = True)
        
        #Get period stats for current match (if necessary)
        if year in [2018,2019]:
            currMatchPeriods = teamPeriodStatsCurrentYear.loc[teamPeriodStatsCurrentYear['matchId'] == matchId,].reset_index(drop = True)
        
        #Get the squad names
        matchSquads = [currMatch['squadName'].iloc[0], currMatch['squadName'].iloc[1]]
        
        #Get the scores for each team
        if year < 2020:
            matchScores = [int(currMatch['goals'].iloc[0]), int(currMatch['goals'].iloc[1])]
        else:
            matchScores = [int(currMatch['points'].iloc[0]), int(currMatch['points'].iloc[1])]
            
        #Determine winner
        if matchScores[0] > matchScores[1]:
            matchWinner = matchSquads[0]
            matchLoser = matchSquads[1]
        elif matchScores[0] < matchScores[1]:
            matchWinner = matchSquads[1]
            matchLoser = matchSquads[0]
        else:
            matchWinner = 'draw'
        
        #Allocate 4 match points to winner
        if matchWinner != 'draw':
            ladderData.at[matchWinner, 'points'] = ladderData.at[matchWinner, 'points'] + 4
            ladderData.at[matchWinner, 'W'] = ladderData.at[matchWinner, 'W'] + 1
            ladderData.at[matchLoser, 'L'] = ladderData.at[matchLoser, 'L'] + 1
        else:
            #Allocate 2 points each for draw
            ladderData.at[matchSquads[0], 'points'] = ladderData.at[matchSquads[0], 'points'] + 2
            ladderData.at[matchSquads[1], 'points'] = ladderData.at[matchSquads[1], 'points'] + 2
            ladderData.at[matchSquads[0], 'D'] = ladderData.at[matchSquads[0], 'D'] + 1
            ladderData.at[matchSquads[1], 'D'] = ladderData.at[matchSquads[1], 'D'] + 1
            
        #Add goals for and against
        ladderData.at[matchSquads[0], 'GF'] = ladderData.at[matchSquads[0], 'GF'] + matchScores[0]
        ladderData.at[matchSquads[0], 'GA'] = ladderData.at[matchSquads[0], 'GA'] + matchScores[1]
        ladderData.at[matchSquads[1], 'GF'] = ladderData.at[matchSquads[1], 'GF'] + matchScores[1]
        ladderData.at[matchSquads[1], 'GA'] = ladderData.at[matchSquads[1], 'GA'] + matchScores[0]
        
        #Add bonus points for relevant years
        if year in [2018,2019]:
            
            #Loop through periods
            for periodNo in currMatchPeriods['period'].unique():
                
                #Get current period data
                currPeriodData = currMatchPeriods.loc[currMatchPeriods['period'] == periodNo, ].reset_index(drop = True)
                
                #Get the squads from this data frame
                periodSquads = [currPeriodData['squadName'].iloc[0], currPeriodData['squadName'].iloc[1]]
                
                #Get scores for current period
                periodScores = [int(currPeriodData['goals'].iloc[0]), int(currPeriodData['goals'].iloc[1])]
                
                #Determine winner of the period
                if periodScores[0] > periodScores[1]:
                    periodWinner = periodSquads[0]
                elif periodScores[0] < periodScores[1]:
                    periodWinner = periodSquads[1]
                else:
                    periodWinner = 'draw'
                    
                #Allocate bonus point to winner
                if periodWinner != 'draw':
                    ladderData.at[periodWinner, 'points'] = ladderData.at[periodWinner, 'points'] + 1
                    
    #Calculate percentage for ladder
    ladderData['per'] = ladderData['GF'] / ladderData['GA'] * 100
    
    #Sort ladder by points then percentgae
    ladderData.sort_values(by = ['points', 'per'], ascending = False, inplace = True)
    
    #Print out placement of premier
    print(f'Premiers: {premiers[year]}, Ladder Position: {list(ladderData.index).index(premiers[year])+1}')

# %% ----- End of 15_sf_analysis.py ----- %% #