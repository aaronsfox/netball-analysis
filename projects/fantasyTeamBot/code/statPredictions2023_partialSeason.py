# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This code runs through simulations of the 2023 to predict the outputs of players
    who are selectable for the 2023 Netball Scoop fantasy season. It takes an input
    of which round onwards to predict from in calculating scores.
    
"""

# %% Import packages

import helperFunctions as helper
import pandas as pd
from difflib import SequenceMatcher
import matplotlib.pyplot as plt
import os
import numpy as np
from statsmodels.stats.weightstats import DescrStatsW
from scipy.stats import multivariate_normal, norm

# %% Inputs

##### CHANGE INFO WITHIN HERE ######

startPredictionsFromRound = 12

##### CHANGE INFO WITHIN HERE ######

# %% Set-up

#Set matplotlib parameters
from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

#Create dictionary to map squad names to ID's
#ID to name
squadDict = {804: 'Vixens', 806: 'Swifts', 807: 'Firebirds', 8117: 'Lightning',
             810: 'Fever', 8119: 'Magpies', 801: 'Thunderbirds', 8118: 'GIANTS'}
#Name to ID
squadNameDict = {'Vixens': 804, 'Swifts': 806, 'Firebirds': 807, 'Lightning': 8117,
                 'Fever': 810, 'Magpies': 8119, 'Thunderbirds': 801, 'GIANTS': 8118}

#Create a court positions variable
courtPositions = ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']

#Select the stats to keep in dataset based on what's relevant to fantasy scoring
selectStatsList = ['matchId', 'squadId', 'oppSquadId', 'playerId', 'roundNo',
                   'attempt1', 'attempt2',
                   'goal1', 'goal2', 'goalMisses', 'goalAssists',
                   'feeds', 'feedWithAttempt', 'centrePassReceives',
                   'gain', 'intercepts', 'deflections', 'deflectionWithGain',
                   'deflectionWithNoGain', 'rebounds', 'pickups',
                   'contactPenalties', 'obstructionPenalties',
                   'generalPlayTurnovers', 'interceptPassThrown',
                   'badHands', 'badPasses', 'offsides',
                   'netPoints', 'minutesPlayed']

#Create a list of stats to predict
predictStatsList = ['attempt1', 'attempt2',
                    'goal1', 'goal2', 'goalMisses', 'goalAssists',
                    'feeds', 'feedWithAttempt', 'centrePassReceives',
                    'gain', 'intercepts', 'deflections', 'deflectionWithGain',
                    'deflectionWithNoGain', 'rebounds', 'pickups',
                    'contactPenalties', 'obstructionPenalties',
                    'generalPlayTurnovers', 'interceptPassThrown',
                    'badHands', 'badPasses', 'offsides',
                    'minutesPlayed']

#Set the primary stats to examine across the various primary positions
courtPosPrimaryStats = {'GS': ['attempt1', 'attempt2', 'goal1', 'goal2', 'goalMisses', 'goalAssists'], 
                        'GA': ['attempt1', 'attempt2', 'goal1', 'goal2', 'goalMisses', 'goalAssists', 'feeds', 'feedWithAttempt', 'centrePassReceives'], 
                        'WA': ['feeds', 'feedWithAttempt', 'centrePassReceives', 'gain', 'intercepts', 'deflections', 'pickups', 'generalPlayTurnovers'], 
                        'C': ['feeds', 'feedWithAttempt', 'gain', 'intercepts', 'deflections', 'pickups', 'generalPlayTurnovers'], 
                        'WD': ['gain', 'intercepts', 'deflections', 'pickups', 'generalPlayTurnovers', 'contactPenalties', 'obstructionPenalties'], 
                        'GD': ['gain', 'intercepts', 'deflections', 'contactPenalties', 'obstructionPenalties', 'rebounds'], 
                        'GK': ['gain', 'intercepts', 'deflections', 'contactPenalties', 'obstructionPenalties', 'rebounds'], 
                        }

#Set weightings to allocate to stats related to games from different years in predictions
standardGameWeight = 0.05 #this is applied to all games that aren't from the current year
pastYearGameWeight = 0.10 # this is applied to all games from the most recent year
currentYearGameWeight = 0.25 #this is applied to all games from the current year
lastFourGameWeight = 0.5 #this is applied to their last 4 games within current year
mostRecentGameWeight = 1 #this is applied to their most recent game

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Read in relevant data

#Read in player stats data for the 2020 and 2021 regular seasons
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021, 2022, 2023],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'])

#Read in player stats data for the 2022 preseason if needed
playerStatsPreseason = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2023],
                                                   fileStem = 'playerStats',
                                                   matchOptions = ['preseason'])

#Read in line-up data
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2020, 2021, 2022, 2023],
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular', 'preseason'])

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021, 2022, 2023],
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','preseason'])

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
playerData[2020] = pd.DataFrame.from_dict(playerDict[2020])
playerData[2021] = pd.DataFrame.from_dict(playerDict[2021])
playerData[2022] = pd.DataFrame.from_dict(playerDict[2022])
playerData[2023] = pd.DataFrame.from_dict(playerDict[2023])

#Get stats in simpler format
#Regular season data
for year in [2020,2021,2022, 2023]:
    playerStats[year] = playerStats[year][selectStatsList]
    
#Preaseason data
playerStatsPreseason[2023] = playerStatsPreseason[2023][selectStatsList]

#Read in 2023 fixture data
fixtureData = pd.read_csv('..\\data\\fixtures\\ssnFixture_2023.csv')

#Read in starting player prices and link up to player data

#Read in player price data and details
#Only need to consider new prices once changes are happening
if startPredictionsFromRound > 3:
    #Read in predicted round prices
    fantasyPlayerDetails = pd.read_csv(f'..\\data\\roundPrices\\prices_round{startPredictionsFromRound}.csv')
else:
    #Read in starting prices
    fantasyPlayerDetails = pd.read_csv('..\\data\\startingPrices\\startingPrices_2023.csv')

#Link up player Id's to price database

#Create list to store data in
playerPriceIds = []
playerNameRatioCheck = []
primaryPos = []

#Loop through players in price list
for ii in fantasyPlayerDetails.index:
    
    #Get player full name
    playerFullName = f'{fantasyPlayerDetails.iloc[ii]["firstName"]} {fantasyPlayerDetails.iloc[ii]["surname"].capitalize()}'
    
    #Compare current player name ratio to all from current year
    #Check 2022 ratios first
    nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[2022]['fullName']]
    #If the max here is 1 (or greater than 0.99) then we take it
    if np.max(nameRatios) > 0.94:    
        #Get index of maximum ratio
        maxRatioInd = nameRatios.index(np.max(nameRatios))
        #Get player Id at the index and append to list
        playerPriceIds.append(playerData[2022].iloc[maxRatioInd]['playerId'])
        #Append ratio to check
        playerNameRatioCheck.append(np.max(nameRatios))
        #Append primary court position from 2022
        primaryPos.append(playerData[2022].iloc[maxRatioInd]['primaryPosition'])
    else:
        #We go to check the 2023 preseason name data
        nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[2023]['fullName']]
        #Get index of maximum ratio
        maxRatioInd = nameRatios.index(np.max(nameRatios))
        #Get player Id at the index and append to list
        playerPriceIds.append(playerData[2023].iloc[maxRatioInd]['playerId'])
        #Append ratio to check
        playerNameRatioCheck.append(np.max(nameRatios))
        #Append primary court position from 2023
        primaryPos.append(playerData[2023].iloc[maxRatioInd]['primaryPosition'])
    
#Append player Id's to price list dataframe
fantasyPlayerDetails['playerId'] = playerPriceIds
fantasyPlayerDetails['nameRatioCheck'] = playerNameRatioCheck
fantasyPlayerDetails['primaryPosition'] = primaryPos

# %% Set team strengths against specific statistics

"""

Here we take the previous two years worth of data to get some team strength scaling
factors on the statistical categories. This is a bit different to a round by round
approach where the strength is scaled repeatedly across the year based on weekly
stats.

"""

#Set up dictionary to store data in
teamStrengthDict = {'squadId': [], 'stat': [], 'strengthRatio': []}

#Loop through squads
for squadId in list(squadDict.keys()):
    
    #Extract the stats against the current team
    teamOppStats = pd.concat([playerStats[2022].loc[playerStats[2022]['oppSquadId'] == squadId, ],
                              playerStats[2023].loc[playerStats[2023]['oppSquadId'] == squadId, ]]
                             ).reset_index(drop = True)
    
    #Extract the stats not against the current team
    leagueOppStats = pd.concat([playerStats[2022].loc[playerStats[2022]['oppSquadId'] != squadId, ],
                                playerStats[2023].loc[playerStats[2023]['oppSquadId'] != squadId, ]]
                               ).reset_index(drop = True)

    #Compare the current teams total relative to the league average for predictable stats
    for statVar in predictStatsList:
        #Calculate the team total for the stat
        teamTotal = teamOppStats[statVar].sum()
        #Calculate the rest of league average
        #Note that this needs to be divided by the remaining number of teams
        leagueTotal = leagueOppStats[statVar].sum() / (len(squadDict)-1)
        #Calculate team strength relative to league average for current stat
        #Store this in a dictionary alongside info data
        teamStrengthDict['squadId'].append(squadId)
        teamStrengthDict['stat'].append(statVar)
        teamStrengthDict['strengthRatio'].append(teamTotal / leagueTotal)
            
#Convert to dataframe
teamStrengthData = pd.DataFrame.from_dict(teamStrengthDict)

# %% Make predictions of player stats for the remainder of 2023

"""

The first step in developing the bot is to create a prediction of what's going
to happen across the 2023 season. This serves as the foundation for selecting
a starting team or trades. Here we simulate the rest of the season and use this
to calculate fantasy scores and price changes.

The players season is both simulated based on their previous season stats, but 
also the preseason and regular season stats. We then use a scaling balance to
predict the actual players season fantasy score based on these two settings.

TODO: Should this be simulated multiple times for confidence bounds on scores?

"""

#Create directory to store data in
try:
    os.mkdir(f'..\\data\\fantasyBot2023\\statPredictionsPartialSeason\\rd{startPredictionsFromRound}_onwards')
except:
    print(f'Directory already created to store round {startPredictionsFromRound} results...')

#Set year to predict
yearToPredict = 2023

#Set years to use data from (past years)
yearsOfData = [2021, 2022]

#Get all round numbers from remainder of the year
#Assumes 14 round season
roundList = [ii for ii in range(1,15)]

#Loop through player Id's in fantasy details
for playerId in fantasyPlayerDetails['playerId']:

    #Create empty dataframe to enter player stat predictions into
    predictedPlayerData_season = pd.DataFrame(columns = predictStatsList + ['roundNo', 'squadId', 'oppSquadId', 'fantasyScore'])
    predictedPlayerData_preseason = pd.DataFrame(columns = predictStatsList + ['roundNo', 'squadId', 'oppSquadId', 'fantasyScore'])
    
    #Get players name and squad id
    playerName = ' '.join(list(fantasyPlayerDetails.loc[fantasyPlayerDetails['playerId'] == playerId,
                                                        ['firstName', 'surname']].values[0]))
    squadName = fantasyPlayerDetails['team'][list(fantasyPlayerDetails['playerId']).index(playerId)]
    squadId = squadNameDict[fantasyPlayerDetails['team'][list(fantasyPlayerDetails['playerId']).index(playerId)]]
    
    #Get player primary position
    primaryPos = fantasyPlayerDetails.iloc[list(fantasyPlayerDetails['playerId']).index(playerId)]['primaryPosition']
    
    #Extract player preseason stats
    #Extract preseason stats
    pastPreseasonStats = playerStatsPreseason[yearToPredict].loc[playerStatsPreseason[yearToPredict]['playerId'] == playerId, predictStatsList]
    #Multiply the preseason stats by 1.5 so they match a 60 minute game
    pastPreseasonStats = pastPreseasonStats * 1.5
    
    #Extract past years statistics and any that precede current round
    pastYearStats = pd.concat([playerStats[getYear].loc[playerStats[getYear]['playerId'] == playerId, predictStatsList] for getYear in yearsOfData])
    
    #Loop through rounds and get actual stats or make predictions
    for roundNo in roundList:
        
        #Check whether current round is before prediction time frame
        if roundNo < startPredictionsFromRound:
            
            ##### GRAB ACTUAL STATS FROM SEASON #####
            
            #Get the data out as a series for regular season
            #Try for player data actually being there
            try:
                actualRoundStats = playerStats[2023].loc[(playerStats[2023]['playerId'] == playerId) &
                                                         (playerStats[2023]['roundNo'] == roundNo),
                                                         ].reset_index(drop = True).iloc[0]
            
                #Calculate fantasy score for the round
                fantasyScore = helper.calcFantasyScore2023(statsData = actualRoundStats,
                                                           playerPos = primaryPos)
                
                #Append the fantasy score to the series
                roundStatsToAppend = pd.concat([actualRoundStats,
                                                pd.Series([fantasyScore], index = ['fantasyScore'])])
                
                #Simply put the players actual stats into the regular & preseason data
                predictedPlayerData_season = pd.concat([predictedPlayerData_season,
                                                        pd.DataFrame(roundStatsToAppend).T])
                predictedPlayerData_preseason = pd.concat([predictedPlayerData_preseason,
                                                           pd.DataFrame(roundStatsToAppend).T])
                
            except:
                print(f'No data from current round for {playerName}...')
        
        #Otherwise make the predictions
        else:
            
            #Check whether current year stats are needed
            if roundNo > 1:
                #Get current year stats from predictions
                currentYearStats = predictedPlayerData_season.loc[predictedPlayerData_season['roundNo'] < roundNo, predictStatsList]
                selectPlayerStats = pd.concat([pastYearStats, currentYearStats])
                selectPlayerPreseasonStats = pd.concat([pastPreseasonStats, currentYearStats])
            else:
                selectPlayerStats = pd.concat([pastYearStats])
                selectPlayerPreseasonStats = pd.concat([pastPreseasonStats])   
            
            #Get the opposition squad Id
            if len(fixtureData.loc[(fixtureData['roundNo'] == roundNo) &
                                   (fixtureData['homeTeam'] == squadName)]) > 0:
                #Grab the away team Id
                oppSquadId = squadNameDict[fixtureData.loc[(fixtureData['roundNo'] == roundNo) &
                                                           (fixtureData['homeTeam'] == squadName)].reset_index(
                                                               drop = True).iloc[0]['awayTeam']]
            else:
                #Grab the home team Id for the correct match
                oppSquadId = squadNameDict[fixtureData.loc[(fixtureData['roundNo'] == roundNo) &
                                                           (fixtureData['awayTeam'] == squadName)].reset_index(
                                                               drop = True).iloc[0]['homeTeam']]
                                                               
            ##### USING REGULAR SEASON STATS #####
                                                               
            #Need to check if there are stats to predict off before progressing
            #There needs to be at least 3 games in predicting here to be of any
            #value, otherwise we have to rely on preseason data
            if len(selectPlayerStats) >= 3:
            
                #Set the weights for matches. See weights in set-up section for values
                #Have tested if there is an actual impact of these weights, yet changing
                #them doesn't really improve predictions that much. So the selection
                #of these weights is pretty much driven by subjective opinion
                #The process for applying weights is as follows:
                    # Begin by giving the standard weight for every match
                    # Any matches from this year (i.e. based on round number) get increased to the current year game weight
                    # The last 4 matches from the current year get increased to the last four game weight
                    # The last match from the current year gets increased to the most recent game weight
                
                #Set the default weights        
                weights = np.ones(len(selectPlayerStats)) * standardGameWeight
                
                #Check how many games have come from this year
                nCurrentYear = roundNo - 1
                
                #Check how many games are from the past year
                nPastYear = len(playerStats[yearToPredict-1].loc[playerStats[yearToPredict-1]['playerId'] == playerId, predictStatsList])
                
                #Allocate extra weight for matches played in the past year
                if nPastYear > 0:
                    #Default weight for games from current year
                    weights[-(nPastYear+nCurrentYear):] = pastYearGameWeight

                #Allocate extra weight for any matches played this year
                if nCurrentYear > 0:
                    #Default weight for games from current year
                    weights[-nCurrentYear:] = currentYearGameWeight
                    #Allocate an appropriate weight for the players last 4 (or less) matches from the year
                    if nCurrentYear >= 4:
                        weights[-4:] = lastFourGameWeight
                    else:
                        weights[-nCurrentYear:] = lastFourGameWeight
                    #Allocate the added weight for the most recent game
                    weights[-1] = mostRecentGameWeight
                    
                #Calculate weighted mean for player stats
                mu = []
                #Loop through stats
                for stat in predictStatsList:
                    #Calculate the weighted stats
                    weightedStats = DescrStatsW(selectPlayerStats[stat].to_numpy(),
                                                weights = weights)
                    #Extract the weighted stats and append to list
                    mu.append(weightedStats.mean)
                    
                #Create covariance matrix from player stats
                if len(selectPlayerStats) > 1:
                    covMat = np.cov(selectPlayerStats.to_numpy(), rowvar = False, aweights = weights)
                else:
                    covMat = np.cov(selectPlayerStats.to_numpy(), rowvar = False)
                
                #Create the multivariate normal distribution from the mean data and covariance matrix
                predictStatsDistribution = multivariate_normal(mean = mu,
                                                               cov = covMat,
                                                               allow_singular = True)
                
                #Sample from the distribution to generate stat outcome options
                #Converting to int avoids the issue with very small negative numbers
                #### TODO: consider more appropriate seed when simulating the game multiple times...
                sampleStats = predictStatsDistribution.rvs(2000, random_state = int(playerId * roundNo)).astype(int)
                
                #Convert to dataframe for easiar manipulation
                sampleStats_df = pd.DataFrame(data = sampleStats,
                                              columns = predictStatsList)
                
                #Eliminate any +60 minute simulations as not necessarily achievable
                sampleStats_df = sampleStats_df.loc[sampleStats_df['minutesPlayed'] <= 60]
                
                #Replace any negative stats with zeros
                sampleStats_df = sampleStats_df[~(sampleStats_df < 0).any(axis = 1)]
                
                #Extract the mean predicted data as a series
                meanPredictedStats = sampleStats_df.describe().loc['mean']
                
                #Scale the stats to opposition team strength
                for var in meanPredictedStats.index:
                    meanPredictedStats.loc[var] = meanPredictedStats.loc[var] * teamStrengthData.loc[(teamStrengthData['squadId'] == oppSquadId) &
                                                                                                     (teamStrengthData['stat'] == var),
                                                                                                     ]['strengthRatio'].values[0]
                
                #Calculate fantasy score from predicted stats
                fantasyScore = helper.calcFantasyScore2023(statsData = meanPredictedStats,
                                                           playerPos = primaryPos)
                
                #Append the match details to the series
                meanPredictedStats = pd.concat([meanPredictedStats,
                    pd.Series([roundNo, squadId, oppSquadId, fantasyScore],
                    index = ['roundNo', 'squadId', 'oppSquadId', 'fantasyScore'])]
                    )
                
                #Append predicted mean stats to the player dataframe
                predictedPlayerData_season = pd.concat([predictedPlayerData_season,
                                                        pd.DataFrame(meanPredictedStats).T])

            ##### USING PRESEASON STATS #####                             
                                                                            
            #Need to check if there are stats to predict off before progressing
            if len(selectPlayerPreseasonStats) > 0:
             
                 #Set the weights for matches. For preseason stats now we set the
                 #default match weight and then give a higher weight to the regular
                 #season match-up
                 
                 #Set the default weights
                 weights = np.ones(len(selectPlayerPreseasonStats)) * standardGameWeight
                 
                 #Check how many games have come from this year
                 nCurrentYear = roundNo - 1

                 #Allocate extra weight for any matches played this year
                 if nCurrentYear > 0:
                     #Default weight for games from current year
                     weights[-nCurrentYear:] = currentYearGameWeight
                     #Allocate an appropriate weight for the players last 4 (or less) matches from the year
                     if nCurrentYear >= 4:
                         weights[-4:] = lastFourGameWeight
                     else:
                         weights[-nCurrentYear:] = lastFourGameWeight
                     #Allocate the added weight for the most recent game
                     weights[-1] = mostRecentGameWeight
                                       
                 #Calculate weighted mean for player stats
                 mu = []
                 #Loop through stats
                 for stat in predictStatsList:
                     #Calculate the weighted stats
                     weightedStats = DescrStatsW(selectPlayerPreseasonStats[stat].to_numpy(),
                                                 weights = weights)
                     #Extract the weighted stats and append to list
                     mu.append(weightedStats.mean)
                     
                 #Create covariance matrix from player stats
                 if len(selectPlayerPreseasonStats) > 1:
                     covMat = np.cov(selectPlayerPreseasonStats.to_numpy(), rowvar = False, aweights = weights)
                 else:
                     covMat = np.cov(selectPlayerPreseasonStats.to_numpy(), rowvar = False)
                 
                 #Create the multivariate normal distribution from the mean data and covariance matrix
                 predictStatsDistribution = multivariate_normal(mean = mu,
                                                                cov = covMat,
                                                                allow_singular = True)
                 
                 #Sample from the distribution to generate stat outcome options
                 #Converting to int avoids the issue with very small negative numbers
                 #### TODO: consider more appropriate seed when simulating the game multiple times...
                 sampleStats = predictStatsDistribution.rvs(2000, random_state = int(playerId * roundNo)).astype(int)
                 
                 #Convert to dataframe for easiar manipulation
                 sampleStats_df = pd.DataFrame(data = sampleStats,
                                               columns = predictStatsList)
                 
                 #Eliminate any +60 minute simulations as not necessarily achievable
                 sampleStats_df = sampleStats_df.loc[sampleStats_df['minutesPlayed'] <= 60]
                 
                 #Eliminate any samples that have negative stats as unachievable
                 sampleStats_df = sampleStats_df[~(sampleStats_df < 0).any(axis = 1)]
                 
                 #Extract the mean predicted data as a series
                 meanPredictedStats = sampleStats_df.describe().loc['mean']
                 
                 #Scale the stats to opposition team strength
                 for var in meanPredictedStats.index:
                     meanPredictedStats.loc[var] = meanPredictedStats.loc[var] * teamStrengthData.loc[(teamStrengthData['squadId'] == oppSquadId) &
                                                                                                      (teamStrengthData['stat'] == var),
                                                                                                      ]['strengthRatio'].values[0]
                 
                 #Calculate fantasy score from predicted stats
                 fantasyScore = helper.calcFantasyScore2023(statsData = meanPredictedStats,
                                                            playerPos = primaryPos)
                 
                 #Append the match details to the series
                 meanPredictedStats = pd.concat([meanPredictedStats,
                     pd.Series([roundNo, squadId, oppSquadId, fantasyScore],
                     index = ['roundNo', 'squadId', 'oppSquadId', 'fantasyScore'])]
                     )
                 
                 #Append predicted mean stats to the player dataframe
                 predictedPlayerData_preseason = pd.concat([predictedPlayerData_preseason,
                                                            pd.DataFrame(meanPredictedStats).T])
                 
                 #Append preseason predictions to regular season data if needed
                 if len(selectPlayerStats) < 3:
                     predictedPlayerData_season = pd.concat([predictedPlayerData_season,
                                                             pd.DataFrame(meanPredictedStats).T])
                     
            
    #Save player data to folder
    #Season based stats
    predictedPlayerData_season.to_csv(f'..\\data\\fantasyBot2023\\statPredictionsPartialSeason\\rd{startPredictionsFromRound}_onwards\\{playerId}_season.csv',
                                      index = False)
    #Preseason based stats
    predictedPlayerData_preseason.to_csv(f'..\\data\\fantasyBot2023\\statPredictionsPartialSeason\\rd{startPredictionsFromRound}_onwards\\{playerId}_preseason.csv',
                                         index = False)
    
    #Print confirmation
    print(f'Exported data for {playerName} (id: {playerId})...')

# %% ----- End of statPredictions2023_partialSeason.py ----- %% #