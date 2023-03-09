# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This code runs through simulations of the 2022 season to select an optimised
    fantasy team for the NetballScoop competition. This will serve asa foundation
    for the 2023 competition.
    
"""

# %% Import packages

import helperFunctions as helper
import pandas as pd
from difflib import SequenceMatcher
import pulp as pl
import matplotlib.pyplot as plt
import os
import numpy as np
from statsmodels.stats.weightstats import DescrStatsW
from scipy.stats import multivariate_normal, norm
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import pickle

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
                                          years = [2020, 2021, 2022],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'])

#Read in player stats data for the 2022 preseason if needed
playerStatsPreseason = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2022],
                                                   fileStem = 'playerStats',
                                                   matchOptions = ['preseason'])

#Read in line-up data
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2020, 2021, 2022],
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular'])

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021, 2022],
                                          fileStem = 'playerList',
                                          matchOptions = ['regular'])

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

#Get stats in simpler format
#Regular season data
for year in [2020,2021,2022]:
    playerStats[year] = playerStats[year][selectStatsList]
    
#Preaseason data
playerStatsPreseason[2022] = playerStatsPreseason[2022][selectStatsList]

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
    teamOppStats = pd.concat([playerStats[2020].loc[playerStats[2020]['oppSquadId'] == squadId, ],
                              playerStats[2021].loc[playerStats[2021]['oppSquadId'] == squadId, ]]
                             ).reset_index(drop = True)
    
    #Extract the stats not against the current team
    leagueOppStats = pd.concat([playerStats[2020].loc[playerStats[2020]['oppSquadId'] != squadId, ],
                                playerStats[2021].loc[playerStats[2021]['oppSquadId'] != squadId, ]]
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

# %% Make predictions of player stats for entire 2022

"""

The first step in developing the bot is to create a prediction of what's going
to happen across the entire 2022 season. This serves as the foundation for selecting
a starting team. Here we simulate the entire season and use this to calculate fantasy
scores and price changes.

TODO: Should this be simulated multiple times for confidence bounds on scores?

"""

#Set a conditional whether to predict or load stats
runWholeSeasonPrediction = True

#Set year to predict
yearToPredict = 2022

#Set years to use data from
yearsOfData = [2020, 2021]

#Get all round numbers from prediction year
roundList = list(playerStats[yearToPredict]['roundNo'].unique())
roundList.sort()

#Check whether to run stats predictions, otherwise we load the data
if runWholeSeasonPrediction:

    #Loop through player Id's in fantasy details
    for playerId in playerData[yearToPredict]['playerId']:

        #Create empty dataframe to enter player stat predictions into
        predictedPlayerData = pd.DataFrame(columns = predictStatsList + ['roundNo', 'matchId', 'squadId', 'oppSquadId', 'fantasyScore'])
        
        #Get players squad id
        squadId = playerData[yearToPredict].loc[playerData[yearToPredict]['playerId'] == playerId, ]['squadId'].unique()[0]
        
        #Get player primary position
        primaryPos = playerData[yearToPredict].loc[playerData[yearToPredict]['playerId'] == playerId, ]['primaryPosition'].unique()[0]
        
        #Loop through rounds and make predictions
        for roundNo in roundList:
            
            #Extract past year statistics and any that precede current round
            pastYearStats = pd.concat([playerStats[getYear].loc[playerStats[getYear]['playerId'] == playerId, predictStatsList] for getYear in yearsOfData])
            
            #Check whether current year stats are needed
            if roundNo > 1:
                #Get current year stats from predictions
                currentYearStats = predictedPlayerData.loc[predictedPlayerData['roundNo'] < roundNo, predictStatsList]
                selectPlayerStats = pd.concat([pastYearStats, currentYearStats])
            else:
                selectPlayerStats = pd.concat([pastYearStats])
            
            #Check if preseason stats are needed for the player 
            #We'll use these if there are < 4 games worth of data
            if len(selectPlayerStats) < 4:
                #Extract preseason stats
                selectPlayerPreseasonStats = playerStatsPreseason[yearToPredict].loc[playerStatsPreseason[yearToPredict]['playerId'] == playerId, predictStatsList]
                #Multiply the preseason stats by 1.5 so they match a 60 minute game
                selectPlayerPreseasonStats = selectPlayerPreseasonStats * 1.5
                #Concatenate regular to preseason stats
                selectPlayerStats = pd.concat([selectPlayerPreseasonStats, selectPlayerStats])
            
            #### TODO: Insert a check for if a player is listed to play when doing
            #### this round by round. For whole season, we just assume the player
            #### will play every game
            
            #Get the match Id and opposition squad Id
            matchId = playerStats[yearToPredict].loc[(playerStats[yearToPredict]['roundNo'] == roundNo) &
                                                     (playerStats[yearToPredict]['squadId'] == squadId),
                                                     ]['matchId'].unique()[0]
            oppSquadId = playerStats[yearToPredict].loc[(playerStats[yearToPredict]['roundNo'] == roundNo) &
                                                        (playerStats[yearToPredict]['squadId'] == squadId),
                                                        ]['oppSquadId'].unique()[0]
            
            #Need to check if there are stats to predict off before progressing
            if len(selectPlayerStats) > 0:
            
                #Set the weights for. See weights in set-up section for values
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
                #### TODO: determine from predicted data
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
                fantasyScore = helper.calcFantasyScore2022(statsData = meanPredictedStats,
                                                           playerPos = primaryPos)
                
                #Append the match details to the series
                meanPredictedStats = meanPredictedStats.append(
                    pd.Series([roundNo, matchId, squadId, oppSquadId, fantasyScore],
                    index = ['roundNo', 'matchId', 'squadId', 'oppSquadId', 'fantasyScore'])
                    )
                
                #Append predicted mean stats to the player dataframe
                predictedPlayerData = predictedPlayerData.append(meanPredictedStats, ignore_index = True)
                
        #Save player data to folder
        #Only do this if we have some predicted stats
        predictedPlayerData.to_csv(f'..\\data\\practiceFantasyBot2022\\statPredictionsEntireSeason\\{playerId}.csv',
                                   index = False)

# %% Read in fantasy player details and link up predicted vs. actual data

#Read in starting player prices and link up to player data & score predictions

#Read in starting price data and details
fantasyPlayerDetails = pd.read_csv(f'..\\data\\startingPrices\\startingPrices_{yearToPredict}.csv')

#Link up player Id's to price database

#Create list to store data in
playerPriceIds = []
playerPredictedScores = []
playerPredictedFinalPrice = []
playerActualScores = []
playerActualFinalPrice = []

#Loop through players in price list
for playerInd in fantasyPlayerDetails.index:
    
    #Get player full name
    playerFullName = f'{fantasyPlayerDetails.iloc[playerInd]["firstName"]} {fantasyPlayerDetails.iloc[playerInd]["surname"].capitalize()}'
    
    #Get players starting price
    playerPrice = fantasyPlayerDetails.iloc[playerInd]['price']
    
    #Compare current player name ratio to all from current year
    nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[yearToPredict]['fullName']]
    
    #Get index of maximum ratio
    maxRatioInd = nameRatios.index(np.max(nameRatios))
    
    #Get player Id
    playerId = playerData[yearToPredict].iloc[maxRatioInd]['playerId']
    
    #Get primary court position
    primaryPos = playerData[yearToPredict].loc[playerData[yearToPredict]['playerId'] == playerId, ]['primaryPosition'].unique()[0]
    
    #Read in predicted season scores and calculate predicted total
    #First try to read file, else allocate a score of zero
    try:
        
        #Read in predicted data
        predictedPlayerData = pd.read_csv(f'..\\data\\practiceFantasyBot2022\\statPredictionsEntireSeason\\{playerId}.csv')
        
        #Get total predicted fantasy score
        #Check if there is actually data predicted here
        if len(predictedPlayerData) > 0:
            
            #Calculate total predicted score
            totalFantasyScore = predictedPlayerData['fantasyScore'].sum()        
            
            #Work through round to round data to progressively calculate updated price
            for roundInd in predictedPlayerData.index:
                
                #Check to see if new player price needs to be calculated based 
                #on the threshold of 3 games being played
                if roundInd > 2:                
                    
                    #Get the sum of the most recent 3 scores
                    recentScoreSum = predictedPlayerData.iloc[roundInd-3:roundInd]['fantasyScore'].to_numpy().sum()                    
                    #Calculate exact new fantasy price
                    exactNewPrice = np.round((playerPrice * 0.00067) + (np.sum(recentScoreSum) / 9))
                    #Round down to nearest 5k as per pricing rules
                    #Update the player price variable here
                    playerPrice = np.floor(exactNewPrice / 5) * 5 * 1000
            
        else:
            
            #Set a total score of zero
            totalFantasyScore = 0
        
    except:
        
        #Set a total score of zero
        totalFantasyScore = 0
        
    #Append predicted data alongside player Id, total predicted score & final price to lists
    playerPriceIds.append(playerId)
    playerPredictedScores.append(totalFantasyScore)
    playerPredictedFinalPrice.append(playerPrice)
        
    #Get actual player data for the predicted year
    actualPlayerStats = playerStats[yearToPredict].loc[playerStats[yearToPredict]['playerId'] == playerId,
                                                       ].reset_index(drop = True).sort_values(by = 'roundNo')
    
    #Calculate players actual total fantasy score for the year
    if len(actualPlayerStats) > 0:
        actualTotalFantasyScore = np.sum([helper.calcFantasyScore2022(actualPlayerStats.iloc[ii], primaryPos) for ii in actualPlayerStats.index])
    else:
        actualTotalFantasyScore = 0
        
    #Calculate actual price at the end of the season
    
    #Reset price to original starting value
    playerPrice = fantasyPlayerDetails.iloc[playerInd]['price']
    
    #Get total predicted fantasy score
    #Check if there is actually data predicted here
    if len(actualPlayerStats) > 0:
        
        #Work through round to round data to progressively calculate updated price
        for roundInd in actualPlayerStats.index:
            
            #Check to see if new player price needs to be calculated based 
            #on the threshold of 3 games being played
            if roundInd > 2:                
                
                #Get the sum of the most recent 3 scores
                recentScoreSum = np.sum([helper.calcFantasyScore2022(actualPlayerStats.iloc[ii], primaryPos) for ii in range(roundInd-3,roundInd)])
                #Calculate exact new fantasy price
                exactNewPrice = np.round((playerPrice * 0.00067) + (np.sum(recentScoreSum) / 9))
                #Round down to nearest 5k as per pricing rules
                #Update the player price variable here
                playerPrice = np.floor(exactNewPrice / 5) * 5 * 1000
                
    #Append actual data values to lists
    playerActualScores.append(actualTotalFantasyScore)
    playerActualFinalPrice.append(playerPrice)
    
#Append new variables to dataframe
fantasyPlayerDetails['playerId'] = playerPriceIds
fantasyPlayerDetails['predictedPoints2022'] = playerPredictedScores
fantasyPlayerDetails['predictedFinalPrice'] = playerPredictedFinalPrice
fantasyPlayerDetails['actualPoints2022'] = playerActualScores
fantasyPlayerDetails['actualFinalPrice'] = playerActualFinalPrice

#Calculate price change variables and errors
fantasyPlayerDetails['predictedPriceChange'] = fantasyPlayerDetails['predictedFinalPrice'] - fantasyPlayerDetails['price']
fantasyPlayerDetails['actualPriceChange'] = fantasyPlayerDetails['actualFinalPrice'] - fantasyPlayerDetails['price']
fantasyPlayerDetails['priceChangeError'] = fantasyPlayerDetails['predictedPriceChange'] - fantasyPlayerDetails['actualPriceChange']

#Calculate error in predicted and actual scores
fantasyPlayerDetails['pointsError'] = fantasyPlayerDetails['predictedPoints2022'] - fantasyPlayerDetails['actualPoints2022']

# %% Make an initial team selection based on whole season simulation

"""

Here we use the overall season prediction to identify an optimal team line-up
that maximises fantasy scoring.

Player selection is solved in a similar way to the multiple choice knapsack
problem via integer programming. Here we take the price of plauyers at the start
of the season, alongside their total score for the year and optimise who our
picks would have been at the start of the year to maximise end of year scoring. 

Through the code some other additions might be added, such as:
    - Adding other considerations to cost function (like score volatilty or price growth)
    
The NS fantasy rules are as follows:
    - A total salary cap of $750,000
    - 3 players from the shooters category
    - 3 players from the midcourters category
    - 3 players from the defenders category
    
NOTES:
    - There are a couple of options below commented in/out trying for different
      team structures with different budgets
    - At the moment, the team selection doesn't work well when considering a global
      optimisation. It's likely that additional elements to ensure "star" players
      are selected is necessary (i.e. X players > $$$, Y players < $$$ > $$, and
      Z players < $)

"""

#Create an option that removes players < $70,000 in price
fantasyPlayerDetailsReduced = fantasyPlayerDetails.loc[fantasyPlayerDetails['price'] >= 70000,].reset_index(drop = True)

#Run an integer programming optimisation to identify an optimal 10-player team

#Set-up the integer variables to use in the optimisation

#Set the n for the number of players
# n = len(fantasyPlayerDetails)
n = len(fantasyPlayerDetailsReduced)

#Player id as a string linked to the fantasy data index
players = [str(ii) for ii in range(n)]

#Points
# points = {str(ii): float(fantasyPlayerDetails['predictedPoints2022'][ii]) for ii in range(n)}
points = {str(ii): float(fantasyPlayerDetailsReduced['predictedPoints2022'][ii]) for ii in range(n)}

#Price
# price = {str(ii): float(fantasyPlayerDetails['price'][ii]) for ii in range(n)}
price = {str(ii): float(fantasyPlayerDetailsReduced['price'][ii]) for ii in range(n)}

#Position variables
          
#Positional group variables
#Set-up a dictionary to store all group dictionaries in
groupLabels = {'defender': {}, 'midcourt': {}, 'shooter': {}}
#Loop through court groupings and create individual dictionaries for each
#Create lists and dictionaries that link court positions to positional groups
courtGroups = ['defender', 'midcourt', 'shooter']
positionalGroups = {'defender': ['GK', 'GD'],
                    'midcourt': ['WD', 'C', 'WA'],
                    'shooter': ['GA', 'GS']}

#### NOTE: the use of half points for multiple position groups seems to ensure
#### the rules are met for selecting enough players from each positional group

#Loop through player number and identify value for current group
for ii in range(n):
    
    #Figure out positional groupings for current player
    # playerGroups = [not set(fantasyPlayerDetails['position'][ii].split('/')).isdisjoint(positionalGroups[group]) for group in courtGroups]
    playerGroups = [not set(fantasyPlayerDetailsReduced['position'][ii].split('/')).isdisjoint(positionalGroups[group]) for group in courtGroups]
    
    #Set the value by summing the boolean values. If it's > 1 then they are a
    #half position; if it's 1 then it's just a single group
    if sum(playerGroups) > 1:
        playerGroupVal = 0.5
    else:
        playerGroupVal = 1.0
        
    #Allocate the values to the dictionary
    for group in courtGroups:
        # if not set(fantasyPlayerDetails['position'][ii].split('/')).isdisjoint(positionalGroups[group]):
        if not set(fantasyPlayerDetailsReduced['position'][ii].split('/')).isdisjoint(positionalGroups[group]):
            groupLabels[group][str(ii)] = playerGroupVal
        else:
            groupLabels[group][str(ii)] = 0

#Create the problem
problem = pl.LpProblem('netballFantasyKnapsack', pl.LpMaximize)

#Create the player variable
playerVar = pl.LpVariable.dicts('players', players, 0, 1, pl.LpBinary)

#Add the objective function to the problem
#This function is the sum of total points
problem += pl.lpSum([points[ii] * playerVar[ii] for ii in players]), 'objectiveValue'

#Add the constraints

#Total number of players being 10
# problem += pl.lpSum([playerVar[ii] for ii in players]) == 10, 'totalPlayers10'
problem += pl.lpSum([playerVar[ii] for ii in players]) == 8, 'totalPlayers8'

#Total price being under $750,000
# problem += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= 750000, 'totalPrice750k'
problem += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= 690000, 'totalPrice690k'

#Have 3:4:3 players from defenders:midcourt:shooters groups
# problem += pl.lpSum([groupLabels['defender'][ii] * playerVar[ii] for ii in players]) == 3, 'defenderLimit'
# problem += pl.lpSum([groupLabels['midcourt'][ii] * playerVar[ii] for ii in players]) == 4, 'midcourtLimit'
# problem += pl.lpSum([groupLabels['shooter'][ii] * playerVar[ii] for ii in players]) == 3, 'shooterLimit'
problem += pl.lpSum([groupLabels['defender'][ii] * playerVar[ii] for ii in players]) == 2, 'defenderLimit'
problem += pl.lpSum([groupLabels['midcourt'][ii] * playerVar[ii] for ii in players]) == 3, 'midcourtLimit'
problem += pl.lpSum([groupLabels['shooter'][ii] * playerVar[ii] for ii in players]) == 3, 'shooterLimit'

# #At least one player from each position
# for courtPos in courtPositions:
#     problem += pl.lpSum([groupLabels[courtPos][ii] * playerVar[ii] for ii in players]) >= 1, f'desired{courtPos}'

#Solve the problem
status = problem.solve()

#Print the general status of the problem
print(f'Status: {pl.LpStatus[problem.status]}')

#Create a list that grabs index for selected players
selectedPlayers = []
#Loop through players
for player in problem.variables():
    #Check if player was selected
    if player.varValue == 1.0:
        #Append player index to list
        selectedPlayers.append(int(player.name.split('_')[1]))

#Extract the players from the fantasy details dataframe
# selectedPlayerDetailsPredicted = fantasyPlayerDetails.iloc[selectedPlayers]
selectedPlayerDetailsPredicted = fantasyPlayerDetailsReduced.iloc[selectedPlayers]

#Print out some details about the team

#Price
print(f'Purchase Price: {selectedPlayerDetailsPredicted["price"].sum()}')

#Predicted season score
print(f'Predicted Season Score: {selectedPlayerDetailsPredicted["predictedPoints2022"].sum()}')

#Actual season score
print(f'Actual Season Score: {selectedPlayerDetailsPredicted["actualPoints2022"].sum()}')

#Score error
print(f'Predicted Score Error: {selectedPlayerDetailsPredicted["pointsError"].sum()}')

# %% 





# %%% ----- End of practiceFantasyBot2022.py -----