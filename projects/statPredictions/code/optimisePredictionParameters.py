# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This script aims to optimise the various input parameters associated with 
    stat predictions in Super Netball. The 2021 season (with 2020 reference data)
    is used as a 'training' dataset and then the optimised parameters are tested
    on the 2022 season. The parameters are optimised by calculating a standardised
    mean difference for each statistic and summing this across the statistics.
    
    TODO: fantasy point system as the optimisation...
    
    The parameters included in the statistical predictions, and hence optimised
    here are:
        
        
        NOTE: the parameters actually don't change the result that much, so seems
        a little wasteful to even bother --- or more likely we can just demonstrate
        that the selection of those parameters doesn't matter
        
        TODO: add parameters
        
    TODO: finalise notes...    
    
"""

# %% Import packages

import pandas as pd
import os
from difflib import SequenceMatcher
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.weightstats import DescrStatsW
from statsmodels.stats.moment_helpers import corr2cov
from scipy.stats import multivariate_normal
from scipy.optimize import minimize
import random

# %% Define functions

### TODO: define any functions here

#Create a function that calculates 2022 fantasy score from a series
def calcFantasyScore2022(statsData, playerId, playerPos):
    
    #Set the 2022 scoring system
    pointVals = {'goal1': 2, 'goal2': 5, 'goalMisses': -5,
                 'goalAssists': 3, 'feedWithAttempt': 1,
                 'gain': 5, 'intercepts': 7, 'deflections': 6,
                 'rebounds': 5, 'pickups': 7,
                 'generalPlayTurnovers': -5, 'interceptPassThrown': -2,
                 'badHands': -2, 'badPasses': -2, 'offsides': -2}
        
    #Set a variable to calculate fantasy score
    fantasyScore = 0

    #Calculate score if player is predicted to have played
    if statsData['minutesPlayed'] > 0:
        
        #Add to fantasy score for getting on court
        fantasyScore += 16 #starting score allocated to those who get on court
        
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
                fantasyScore += ((16-8) * (statsData['minutesPlayed'] - 30) / 30) + 8
            else:
                fantasyScore += (((16-8) * (statsData['minutesPlayed'] - 30) / 30) + 8) / 2
                    
    #Return the final calculated fantasy score
    return fantasyScore

#Define the function to calculate average RMSE between actual and predicted fantasy scores
def calcFantasyScoreError2021(x, info):

    #Start with those related to the timing of games relative to current round
    standardGameWeight = x[0] #this is applied to all games that aren't from the current year
    currentYearGameWeight = x[1] #this is applied to all games from the current year
    lastFourGameWeight = x[2] #this is applied to their last 4 games within current year
    mostRecentGameWeight = x[3] #this is applied to their most recent game
    
    #Set a variable to store the fantasy score errors in
    fantasyScoreRMSE = []
    
    #Loop through player stats data to predict
    for dataInd in statPredictionsData.index:    
    
        #Get the player Id and position for calculations
        playerId = statPredictionsData['playerId'][dataInd]
        playerPos = playerData[2021].loc[playerData[2021]['playerId'] == playerId].reset_index()['primaryPosition'][0]
    
        #Set the default weights        
        weights = np.ones(len(statPredictionsData['selectPlayerStats'][dataInd])) * standardGameWeight
        
        #Get current number of games from year
        nCurrentYear = statPredictionsData['nCurrentYear'][dataInd]
        
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
            weightedStats = DescrStatsW(statPredictionsData['selectPlayerStats'][dataInd][stat].to_numpy(),
                                        weights = weights)
            #Extract the weighted stats and append to list
            mu.append(weightedStats.mean)
            
        #Create covariance matrix from player stats
        covMat = np.cov(statPredictionsData['selectPlayerStats'][dataInd].to_numpy(),
                        rowvar = False, aweights = weights)
        
        #Create the multivariate normal distribution from the mean data and covariance matrix
        ##### NOTE: covariance matrix appears ill-conditioned or singular --- correct approach?
        predictStatsDistribution = multivariate_normal(mean = mu,
                                                       cov = covMat,
                                                       allow_singular = True)
        
        #Sample from the distribution to generate stat outcomes
        #Converting to int avoids the issue with very small negative numbers
        sampleStats = predictStatsDistribution.rvs(2000, random_state = int(playerId * roundNo)).astype(int)
        
        #Convert to dataframe for easiar manipulation
        sampleStats_df = pd.DataFrame(data = sampleStats,
                                      columns = predictStatsList)
        
        #Eliminate any +60 minute simulations as not necessarily achievable
        sampleStats_df = sampleStats_df.loc[sampleStats_df['minutesPlayed'] <= 60]
        
        #Eliminate any samples that have negative stats as unachievable
        sampleStats_df = sampleStats_df[~(sampleStats_df < 0).any(axis = 1)]
        
        #Calculate means from sampled data to compare to actual data
        sampleStats_mean = sampleStats_df.mean()
        
        #Convert actual player stats to series for comparison
        actualPlayerStats_vals = statPredictionsData['actualPlayerStats'][dataInd].squeeze()
        
        #Calculate fantasy scores for the actual and predicted stats asa the 
        #objective measure to optimise against
        predictedFantasyScore = calcFantasyScore2022(sampleStats_mean, playerId, playerPos)
        actualFantasyScore = calcFantasyScore2022(actualPlayerStats_vals, playerId, playerPos)
        
        #Calculate the root mean square error between predicted and actual fantasy scores
        #Append this to the variable list
        fantasyScoreRMSE.append(np.sqrt((predictedFantasyScore - actualFantasyScore) ** 2))
    
    #Apply a weight across the season to RMSE so that later rounds are weighted the most
    roundWeightings = np.array(statPredictionsData['roundNo'] / statPredictionsData['roundNo'].max())
    
    #Calculate the weighted fantasy score RMSE
    weightedFantasyScoreRMSE = np.array(fantasyScoreRMSE) * roundWeightings
    
    #Get the average RMSE
    avgFantasyScoreRMSE = np.mean(weightedFantasyScoreRMSE)
    # sumFantasyScoreRMSE = np.sum(fantasyScoreRMSE)
    
    #Display information from function evaluation
    #### TODO: print out headers every X iterations...
    print('{0:4d}   {1: 3.6f}   {2: 3.6f}   {3: 3.6f}   {4: 3.6f} {5: 3.6f}'.format(info['Nfeval'], x[0], x[1], x[2], x[3], avgFantasyScoreRMSE))
    # print('{0:4d}   {1: 3.6f}   {2: 3.6f}   {3: 3.6f}   {4: 3.6f} {5: 3.6f}'.format(info['Nfeval'], x[0], x[1], x[2], x[3], sumFantasyScoreRMSE))
    
    #Update function evaluation number
    info['Nfeval'] += 1
    
    #Return the value
    return avgFantasyScoreRMSE
    # return sumFantasyScoreRMSE ### TODO: if using sum then scale this???

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
                   'minutesPlayed']

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

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Read in the relevant data

#Read in player stats data from regular season matches
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

# %% Calculate opposition strength against stats relative to league average
#    Note that this returns to a starting value of 1 at the beginning of the year

#### TODO: eventually link this 'strength' up to positions/positional groups
#### Take the positional data eventually from the Super Netball rosters
#### NOTE: this takes an excessively long time --- so if it can be avoided and
#### good predictions made, then that is a good trade-off

#Set up dictionary to store data in
teamStrengthDict = {'squadId': [], 'year': [], 'afterRound': [], 
                    'stat': [], 'strengthRatio': []}

#Loop through squads
for squadId in list(squadDict.keys()):
    
    #Loop through years
    for year in list(playerStats.keys()):
        
        #Loop through rounds
        for roundNo in list(playerStats[year]['roundNo'].unique()):
            
            #Extract the stats against the current team up to the present round
            teamOppStats = playerStats[year].loc[(playerStats[year]['roundNo'] <= roundNo) &
                                                 (playerStats[year]['oppSquadId'] == squadId)]
            
            #Extract the stats not againts the current team up to the present round
            leagueOppStats = playerStats[year].loc[(playerStats[year]['roundNo'] <= roundNo) &
                                                   (playerStats[year]['oppSquadId'] != squadId)]
            
            # #Loop through court positions to calculate strength relative to primary positions
            # for courtPos in courtPositions:
                
            #     #Identify the players that are from the current court position
            #     #In the current team opposition stats
            #     teamOppCourtPosId = []
            #     for playerId in teamOppStats['playerId']:
            #         if playerData[year].loc[playerData[year]['playerId'] == playerId,
            #                                 ].reset_index()['primaryPosition'][0] == courtPos:
            #             teamOppCourtPosId.append(playerId)
            #     #For the league-wide opposition stats
            #     leagueOppCourtPosId = []
            #     for playerId in leagueOppStats['playerId']:
            #         if playerData[year].loc[playerData[year]['playerId'] == playerId,
            #                                 ].reset_index()['primaryPosition'][0] == courtPos:
            #             leagueOppCourtPosId.append(playerId)
                        
            #     #Extract the court position relevant stats from the datasets
            #     teamOppStatsCourtPos = teamOppStats.loc[teamOppStats['playerId'].isin(teamOppCourtPosId),]
            #     leagueOppStatsCourtPos = leagueOppStats.loc[leagueOppStats['playerId'].isin(leagueOppCourtPosId),]

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
                teamStrengthDict['year'].append(year)
                # teamStrengthDict['againstPosition'].append(courtPos)
                teamStrengthDict['stat'].append(statVar)
                teamStrengthDict['afterRound'].append(roundNo)
                teamStrengthDict['strengthRatio'].append(teamTotal / leagueTotal)
            
#Convert to dataframe
teamStrengthData = pd.DataFrame.from_dict(teamStrengthDict)

# %% Set-up the data required for the 2021 stats predictions

#### TODO: work in oppposition strength to prediction

#Get all round numbers from 2021
roundList = list(playerStats[2021]['roundNo'].unique())
roundList.sort()

#Create dictionaries to store actual stats and predictions in
statPredictionsDict = {'matchId': [], 'squadId': [], 'oppSquadId': [],
                       'playerId': [], 'roundNo': [], 'actualPlayerStats': [],
                       'selectPlayerStats': [], 'nCurrentYear': []}

##### TODO: what to do if there is no data to predict? Preseason...?
##### Hopefully every player in there had some preaseason stats?

##### TODO: need a rostered player database for which players to predict for each week
##### This can link up to the player positions database too

#Loop through player Id's in 2021 player list
for playerId in playerData[2021]['playerId']:
    
    #Loop through rounds and make predictions
    for roundNo in roundList:
        
        #Extract 2020 player stats and any 2021 stats preceeding current round
        #Extract any 2022 statistics preceding the current round
        selectPlayerStats = pd.concat([playerStats[2020].loc[playerStats[2020]['playerId'] == playerId, predictStatsList],
                                        playerStats[2021].loc[(playerStats[2021]['playerId'] == playerId) &
                                                              (playerStats[2021]['roundNo'] < roundNo), predictStatsList]])
        
        #### TODO: what if player is new in 2021???
        #### Accounting for this by needing at least 4 games for predictions...
        
        #Get the actual player stats for the present round
        actualPlayerStats = playerStats[2021].loc[(playerStats[2021]['playerId'] == playerId) &
                                                  (playerStats[2021]['roundNo'] == roundNo),
                                                  predictStatsList].reset_index(drop = True)
        
        #Check if player actually played the game
        #### TODO: will eventually need to change this in some way to simply predict
        #### everyone and give low values to those who aren't expected to play
        #### TODO: put in a better implementation for when < 4 games are there for selected player data
        #### NOTE: there seems to be a random time where a plaer plays two games
        #### in a week --- this may be some weird round issue. Hence actual player
        #### stats needs to equal exactly 1 here...
        if len(actualPlayerStats) == 1 and len(selectPlayerStats) >= 4:
            
            #Get match details
            matchId, squadId, oppSquadId = list(playerStats[2021].loc[(playerStats[2021]['playerId'] == playerId) &
                                                                      (playerStats[2021]['roundNo'] == roundNo),
                                                                      ].reset_index().iloc[0][['matchId',
                                                                                               'squadId',
                                                                                               'oppSquadId']
                                                                                               ].to_numpy(dtype = int))
                                                                                               
            
            #Check how many games have come from this year
            nCurrentYear = len(playerStats[2021].loc[(playerStats[2021]['playerId'] == playerId) &
                                                     (playerStats[2021]['roundNo'] < roundNo), predictStatsList])
            
            #Append data to stats predictions dictionary
            statPredictionsDict['matchId'].append(matchId)
            statPredictionsDict['squadId'].append(squadId)
            statPredictionsDict['oppSquadId'].append(oppSquadId)
            statPredictionsDict['playerId'].append(playerId)
            statPredictionsDict['roundNo'].append(roundNo)
            statPredictionsDict['actualPlayerStats'].append(actualPlayerStats)
            statPredictionsDict['selectPlayerStats'].append(selectPlayerStats)
            statPredictionsDict['nCurrentYear'].append(nCurrentYear)
            
            # #Set the weights for matches
            # #The process for applying weights is as follows:
            #     # > Begin by giving a default weight of 1 for every match
            #     # > Any matches from this year (i.e. based on round number) get increased to a value of 2.5
            #     # > The last 4 matches from the current year get increased to a value of 10
            #     # > The last match from the current year gets increased to a value of 25
            # #### TODO: consider if this works for missed matches in a year?
            # #### TODO: consider other options for weights?
            # #### TODO: consider if player misses a year?
            
            # #Set the default weights        
            # weights = np.ones(len(selectPlayerStats)) * standardGameWeight
            
            
            
            # #Allocate extra weight for any matches played this year
            # if nCurrentYear > 0:
            #     #Default weight for games from current year
            #     weights[-nCurrentYear:] = currentYearGameWeight
            #     #Allocate an appropriate weight for the players last 4 (or less) matches from the year
            #     if nCurrentYear >= 4:
            #         weights[-4:] = lastFourGameWeight
            #     else:
            #         weights[-nCurrentYear:] = lastFourGameWeight
            #     #Allocate the added weight for the most recent game
            #     weights[-1] = mostRecentGameWeight
                
            # #Calculate weighted mean for player stats
            # mu = []
            # #Loop through stats
            # for stat in predictStatsList:
            #     #Calculate the weighted stats
            #     weightedStats = DescrStatsW(selectPlayerStats[stat].to_numpy(),
            #                                 weights = weights)
            #     #Extract the weighted stats and append to list
            #     mu.append(weightedStats.mean)
                
            # #Create covariance matrix from player stats
            # covMat = np.cov(selectPlayerStats.to_numpy(), rowvar = False, aweights = weights)
            
            # #Create the multivariate normal distribution from the mean data and covariance matrix
            # ##### NOTE: covariance matrix appears ill-conditioned or singular --- correct approach?
            # predictStatsDistribution = multivariate_normal(mean = mu,
            #                                                cov = covMat,
            #                                                allow_singular = True)
            
            # #Sample from the distribution to generate stat outcomes
            # #Converting to int avoids the issue with very small negative numbers
            # sampleStats = predictStatsDistribution.rvs(2000, random_state = int(playerId * roundNo)).astype(int)
            
            # #Convert to dataframe for easiar manipulation
            # sampleStats_df = pd.DataFrame(data = sampleStats,
            #                               columns = predictStatsList)
            
            # #Eliminate any +60 minute simulations as not necessarily achievable
            # sampleStats_df = sampleStats_df.loc[sampleStats_df['minutesPlayed'] <= 60]
            
            # #Eliminate any samples that have negative stats as unachievable
            # sampleStats_df = sampleStats_df[~(sampleStats_df < 0).any(axis = 1)]
            
            # #Calculate means from sampled data to compare to actual data
            # sampleStats_mean = sampleStats_df.mean()
            
            # #Convert actual player stats to series for comparison
            # actualPlayerStats_vals = actualPlayerStats.squeeze()
            
            # #Calculate the root mean square error between predicted and actual stats
            # #### TODO: is this the best error measure given it might be skewed
            # #### by higher value stats?
            # rmse = []
            # for statVar in predictStatsList:
            #     rmse.append(np.sqrt((sampleStats_mean[statVar] - actualPlayerStats_vals[statVar]) ** 2))
            # sumRMSE = np.sum(rmse)
              
            # #Store predictions in dictionaries
            # statPredictionsDict['matchId'].append(matchId)
            # statPredictionsDict['squadId'].append(squadId)
            # statPredictionsDict['oppSquadId'].append(oppSquadId)
            # statPredictionsDict['playerId'].append(playerId)
            # statPredictionsDict['roundNo'].append(roundNo)
            # statPredictionsDict['sumRMSE'].append(sumRMSE)
            
#Convert stat predictions data to dataframe
statPredictionsData = pd.DataFrame.from_dict(statPredictionsDict).sort_values(
    ['matchId', 'squadId', 'playerId']).reset_index(drop = True)

# %% Run some random options to test how much the game weightings actually effect result

#Before actually checking whether a parameter optimisation is beneficial, we can
#use some random values to check if it ever makes a difference. Spoiler alert ---
#it doesn't...

#Set seed for random permutations
random.seed(12345)

#Loop through and calculate fantasy score errors using random values on parameters
for ii in range(100):
    calcFantasyScoreError2021([random.random(), random.random(), random.random(), random.random()], {'Nfeval': ii})

# %% Run the parameter optimisation on the 2021 season data

#Set the weighting parameters for applying to statistics

#### TODO: work in opposition strength weightings here...

#Start with those related to the timing of games relative to current round
standardGameWeight = 0.05 #this is applied to all games that aren't from the current year
currentYearGameWeight = 0.25 #this is applied to all games from the current year
lastFourGameWeight = 0.5 #this is applied to their last 4 games within current year
mostRecentGameWeight = 1 #this is applied to their most recent game

#Run optimisation
#### TODO: the optimisation here takes far too long due to the amount of time a 
#### single function call takes. We need to calculate all the relevant data first
#### to feed into a function (i.e. the players past stats etc.) and then simply
#### feed that into the optimisation so that no time-consuming processes need to
#### run...need bounds to avoid negatives too...
x0 = np.array([standardGameWeight, currentYearGameWeight, lastFourGameWeight, mostRecentGameWeight])
#### TODO: this is currently using default parameters
res = minimize(calcFantasyScoreError2021, x0,
               args = ({'Nfeval': 0},),
               bounds = ((1e-10, 1), (1e-10, 1), (1e-10, 1), (1e-10, 1)), #bounds set to weight between basically 0 and 1
               method = 'Nelder-Mead',
               tol = 1e-5, ### TODO: tolerance to use???
               options = {'disp': True})

# %% 





















# %%% ----- End of optimisePredictionParameters.py -----