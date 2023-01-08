# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    TODO:
        > Update below notes to relate to stat prediction project
    
    Function to help with creating the Netball Scoop fantasy team bot.
    This script aims to develop a model that predicts match stat lines.
    
    TODO:
        > Eliminate fantasy score related aspects
        > Create an optimisation script before this that optimises parameters related to predictions
            >> i.e. weightings on recent matches, weightings on opposition strength
        > Run optimisation on 2020 & 2021 seasons and make predictions against 2022
        > Predict week to week as well as across the whole season with predicted updates   
        > Add in an opposition weighting based on recent performance against position
    
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
squadDict = {804: 'Vixens',
             806: 'Swifts',
             807: 'Firebirds',
             8117: 'Lightning',
             810: 'Fever',
             8119: 'Magpies',
             801: 'Thunderbirds',
             8118: 'GIANTS'}
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118}

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

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

#Read in substitutions data
subsData = collatestats.getSeasonStats(baseDir = baseDir,
                                       years = [2020, 2021, 2022],
                                       fileStem = 'substitutions',
                                       matchOptions = ['regular'])

#Read in substitutions data
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
playerDict = {}
for year in list(playerLists.keys()):
    
    #Create dictionary to append players to
    playerDict[year] = {'playerId': [],
                        'firstName': [], 'surname': [], 'fullName': [],
                        'squadId': []}
    
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
        
#Convert to dataframes
playerData = {}
playerData[2020] = pd.DataFrame.from_dict(playerDict[2020])
playerData[2021] = pd.DataFrame.from_dict(playerDict[2021])
playerData[2022] = pd.DataFrame.from_dict(playerDict[2022])

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

#Create a predict stats list
predictStatsList = ['attempt1', 'attempt2',
                    'goal1', 'goal2', 'goalMisses', 'goalAssists',
                    'feeds', 'feedWithAttempt', 'centrePassReceives',
                    'gain', 'intercepts', 'deflections', 'deflectionWithGain',
                    'deflectionWithNoGain', 'rebounds', 'pickups',
                    'contactPenalties', 'obstructionPenalties',
                    'generalPlayTurnovers', 'interceptPassThrown',
                    'badHands', 'badPasses', 'offsides',
                    'minutesPlayed']

#Get stats in simpler format
#Regular season data
for year in [2020,2021,2022]:
    playerStats[year] = playerStats[year][selectStatsList]
#Preaseason data
playerStatsPreseason[2022] = playerStatsPreseason[2022][selectStatsList]
    
#Set the 2022 scoring system
pointVals = {'goal1': 2, 'goal2': 5, 'goalMisses': -5,
             'goalAssists': 3, 'feedWithAttempt': 1,
             'gain': 5, 'intercepts': 7, 'deflections': 6,
             'rebounds': 5, 'pickups': 7,
             'generalPlayTurnovers': -5, 'interceptPassThrown': -2,
             'badHands': -2, 'badPasses': -2, 'offsides': -2}

# #Read in price data and details for 2022 season
# #Combine starting and final prices as this should theoretically have all details
# startingPriceDetails = pd.read_csv('..\\..\\data\\startingPrices\\startingPrices_2022.csv')
# finalPriceDetails = pd.read_csv('..\\..\\data\\finalPrices\\finalPrices_2022.csv')

# #Link up player Id's to price databases

# #Create list to store data in
# startingPriceIds = []
# finalPriceIds = []

# #Loop through players in starting price list
# for ii in startingPriceDetails.index:
    
#     #Get player full name
#     playerFullName = f'{startingPriceDetails.iloc[ii]["firstName"]} {startingPriceDetails.iloc[ii]["surname"].capitalize()}'
    
#     #Compare current player name ratio to all from current year
#     nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[2022]['fullName']]
    
#     #Get index of maximum ratio
#     maxRatioInd = nameRatios.index(np.max(nameRatios))
    
#     #Get player Id at the index and append to list
#     startingPriceIds.append(playerData[2022].iloc[maxRatioInd]['playerId'])
    
# #Append player Id's to starting price list dataframe
# startingPriceDetails['playerId'] = startingPriceIds

# #Loop through players in final price list
# for ii in finalPriceDetails.index:
    
#     #Get player full name
#     playerFullName = f'{finalPriceDetails.iloc[ii]["firstName"]} {finalPriceDetails.iloc[ii]["surname"].capitalize()}'
    
#     #Compare current player name ratio to all from current year
#     nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[2022]['fullName']]
    
#     #Get index of maximum ratio
#     maxRatioInd = nameRatios.index(np.max(nameRatios))
    
#     #Get player Id at the index and append to list
#     finalPriceIds.append(playerData[2022].iloc[maxRatioInd]['playerId'])
    
# #Append player Id's to starting price list dataframe
# finalPriceDetails['playerId'] = finalPriceIds

# #Join dataframes, drop duplicate player and keep basic columns
# fantasyPlayerDetails = pd.concat([startingPriceDetails,
#                                   finalPriceDetails]).drop_duplicates(
#                                       subset = 'playerId', 
#                                       keep = 'first')[['surname',
#                                                       'firstName',
#                                                       'team',
#                                                       'position',
#                                                       'playerId']]

# %% Calculate opposition strength against stats relative to league average
#    Note that this returns to a starting value of 1 at the beginning of the year

#### TODO: eventually link this 'strength' up to positions/positional groups
#### Take the positional data eventually from the Super Netball rosters

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
                teamStrengthDict['stat'].append(statVar)
                teamStrengthDict['afterRound'].append(roundNo)
                teamStrengthDict['strengthRatio'].append(teamTotal / leagueTotal)
            
#Convert to dataframe
teamStrengthData = pd.DataFrame.from_dict(teamStrengthDict)
            
# %% Run stat predictions for 2022 season

### NOTE: this process does a week-to-week prediction, whereby only one week is
### predicted at a time (i.e. real data from the season is used in predictions,
### rather than chaining the predictions on to prior predictions)

#Get all round numbers from 2022
roundList = list(playerStats[2022]['roundNo'].unique())
roundList.sort()

#Create dictionaries to store actual stats and predictions in
#Upper and lower predictions are +/- 95% CIs
# statPredictionsDict = {'lowerPrediction': {stat: [] for stat in selectStatsList},
#                        'avgPrediction': {stat: [] for stat in selectStatsList},
#                        'upperPrediction': {stat: [] for stat in selectStatsList}}
statPredictionsDict = {'matchId': [], 'squadId': [], 'oppSquadId': [],
                       'playerId': [], 'roundNo': [],
                       'sampleStats': [], 'sampleStatsSummary': []}

##### TODO: what to do if there is no data to predict? Preseason...?
##### Hopefully every player in there had some preaseason stats?

##### TODO: need a rostered player database for which players to predict for each week
##### This can link up to the player positions database too

#Loop through player Id's in fantasy details
for playerId in list(fantasyPlayerDetails['playerId'].unique()):
    
    #Loop through rounds and make predictions
    for roundNo in roundList:
        
        #Extract 2020 and 2021 player statistics
        #Extract any 2022 statistics preceding the current round
        selectPlayerStats  = pd.concat([playerStats[2020].loc[playerStats[2020]['playerId'] == playerId, predictStatsList],
                                        playerStats[2021].loc[playerStats[2021]['playerId'] == playerId, predictStatsList],
                                        playerStats[2022].loc[(playerStats[2022]['playerId'] == playerId) &
                                                              (playerStats[2022]['roundNo'] < roundNo), predictStatsList]])
        
        ##### TODO: should we include preseason stats if there aren't any games
        ##### from the present year? Or might this skew for certain players?
        
        #Check if preseason stats are needed for the player 
        #We'll use these if there are < 4 games worth of data
        if len(selectPlayerStats) < 4:
            #Extract preseason stats
            selectPlayerPreseasonStats = playerStatsPreseason[2022].loc[playerStatsPreseason[2022]['playerId'] == playerId, predictStatsList]
            #Multiply the preseason stats by 1.5 so they match a 60 minute game
            selectPlayerPreseasonStats = selectPlayerPreseasonStats * 1.5
            #Concatenate regular to preseason stats
            selectPlayerStats = pd.concat([selectPlayerPreseasonStats, selectPlayerStats])
        
        #Get the actual player stats for the present round
        actualPlayerStats = playerStats[2022].loc[(playerStats[2022]['playerId'] == playerId) &
                                                  (playerStats[2022]['roundNo'] == roundNo),
                                                  predictStatsList].reset_index(drop = True)
        
        #Check if player actually played the game
        #### TODO: will eventually need to change this in some way to simply predict
        #### everyone and give low values to those who aren't expected to play
        if len(actualPlayerStats) > 0:
        
            #Get match details
            matchId, squadId, oppSquadId = list(playerStats[2022].loc[(playerStats[2022]['playerId'] == playerId) &
                                                                      (playerStats[2022]['roundNo'] == roundNo),
                                                                      ].reset_index().iloc[0][['matchId',
                                                                                               'squadId',
                                                                                               'oppSquadId']
                                                                                               ].to_numpy(dtype = int))
            
            #Set the weights for matches
            #The process for applying weights is as follows:
                # > Begin by giving a default weight of 1 for every match
                # > Any matches from this year (i.e. based on round number) get increased to a value of 2.5
                # > The last 4 matches from the current year get increased to a value of 10
                # > The last match from the current year gets increased to a value of 25
            #### TODO: consider if this works for missed matches in a year?
            #### TODO: consider other options for weights?
            #### TODO: consider if player misses a year?
            
            #### TODO: the above numerical values can be worked into an optimisation
            #### process to determine what optimises prediction accuracy against a 
            #### summative statistic like NetPoints
            
            #Set the default weights        
            weights = np.ones(len(selectPlayerStats))
            
            #Check how many games have come from this year
            nCurrentYear = len(playerStats[2022].loc[(playerStats[2022]['playerId'] == playerId) &
                                                     (playerStats[2022]['roundNo'] < roundNo), predictStatsList])
            
            #Allocate extra weight for any matches played this year
            if nCurrentYear > 0:
                #Default weight for games from current year
                weights[-nCurrentYear:] = 2.5
                #Allocate an appropriate weight for the players last 4 (or less) matches from the year
                if nCurrentYear >= 4:
                    weights[-4:] = 10
                else:
                    weights[-nCurrentYear:] = 10
                #Allocate the added weight for the most recent game
                weights[-1] = 25
                
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
            covMat = np.cov(selectPlayerStats.to_numpy(), rowvar = False, aweights = weights)
            
            #Create the multivariate normal distribution from the mean data and covariance matrix
            ##### covariance matrix appears ill-conditioned or singular --- correct approach?
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
            
            #Calculate summary statistics from the sampled stats
            sampleStats_summary = sampleStats_df.describe()
            
            #### TODO: instead of storing all stat data, convert each one to a
            #### normal distribution to later refer to...
            
            #Store predictions in dictionaries
            statPredictionsDict['matchId'].append(matchId)
            statPredictionsDict['squadId'].append(squadId)
            statPredictionsDict['oppSquadId'].append(oppSquadId)
            statPredictionsDict['playerId'].append(playerId)
            statPredictionsDict['roundNo'].append(roundNo)
            statPredictionsDict['sampleStats'].append(sampleStats_df)
            statPredictionsDict['sampleStatsSummary'].append(sampleStats_summary)
            # #General match details
            # for predictionLabel in list(statPredictionsDict.keys()):
            #     statPredictionsDict[predictionLabel]['matchId'].append(matchId)
            #     statPredictionsDict[predictionLabel]['squadId'].append(squadId)
            #     statPredictionsDict[predictionLabel]['oppSquadId'].append(oppSquadId)
            #     statPredictionsDict[predictionLabel]['playerId'].append(playerId)
            #     statPredictionsDict[predictionLabel]['roundNo'].append(roundNo)
            # #Predicted stats
            # for stat in predictStatsList:
            #     statPredictionsDict['lowerPrediction'][stat].append(sampleStats_summary[stat]['mean'] - (1.96 * (sampleStats_summary[stat]['std'] / np.sqrt(sampleStats_summary[stat]['count']))))
            #     statPredictionsDict['avgPrediction'][stat].append(sampleStats_summary[stat]['mean'])
            #     statPredictionsDict['upperPrediction'][stat].append(sampleStats_summary[stat]['mean'] + (1.96 * (sampleStats_summary[stat]['std'] / np.sqrt(sampleStats_summary[stat]['count']))))

#Convert predictions to dataframe
statPredictions = pd.DataFrame.from_dict(statPredictionsDict).sort_values(
        ['matchId', 'squadId', 'playerId']).reset_index(drop = True)

# %% Compare stats and fantasy score predictions to actual data

#Set the 2022 scoring system
pointVals = {'goal1': 2, 'goal2': 5, 'goalMisses': -5,
             'goalAssists': 3, 'feedWithAttempt': 1,
             'gain': 5, 'intercepts': 7, 'deflections': 6,
             'rebounds': 5, 'pickups': 7,
             'generalPlayTurnovers': -5, 'interceptPassThrown': -2,
             'badHands': -2, 'badPasses': -2, 'offsides': -2}

#Loop through the sampled stats and calculate fantasy scores
for ii in statPredictions.index:
    
    #Extract the sampled stats dataframe for current index for easy use
    sampleStats = statPredictions.iloc[ii]['sampleStats'].reset_index(drop = True)
    
    #Get current players Id
    playerId = statPredictions.iloc[ii]['playerId']
    
    #Extract the players fantasy position from price list details
    playerPos = fantasyPlayerDetails.loc[fantasyPlayerDetails['playerId'] == playerId,
                                         ].reset_index().iloc[0]['position']
    
    #Set a list to store the calculated fantasy score samples in
    calcFantasyScores = []
    
    #Loop through the sampled stats dataframe
    for sampleInd in sampleStats.index:
            
        #Set a variable to calculate fantasy score
        fantasyScore = 0
        
        #Check the predicted total minutes played in sample
        totalMinutesPlayed = sampleStats.iloc[sampleInd]['minutesPlayed']
        
        #Calculate score if player is predicted to have played
        if totalMinutesPlayed > 0:
            
            #Add to fantasy score for getting on court
            fantasyScore += 16 #starting score allocated to those who get on court
            
            #Predict how many quarters the player was on for
            #Rough way of doing this is diving by quarter length of 15
            #Take the rounded ceiling of this to estimate quarters played
            fantasyScore += int(np.ceil(totalMinutesPlayed / 15) * 4)
            
            #Loop through the scoring elements and add the scoring for these
            for stat in list(pointVals.keys()):
                fantasyScore += sampleStats.iloc[sampleInd][stat] * pointVals[stat]
                
            #Calculate centre pass receives points
            #This requires different point values across the various positions
            if 'GA' in playerPos or 'WA' in playerPos:
                fantasyScore += np.floor(sampleStats.iloc[sampleInd]['centrePassReceives'] / 2) * 1
            elif 'GD' in playerPos or 'WD' in playerPos:
                fantasyScore += sampleStats.iloc[sampleInd]['centrePassReceives'] * 3
            
            #Calculate penalty points
            fantasyScore += np.floor((sampleStats.iloc[sampleInd]['obstructionPenalties'] + sampleStats.iloc[sampleInd]['contactPenalties']) / 2) * -1
            
            #Estimate the time played in WD based on player position
            #8 points for half a game at WD / 16 points for a full game at WD
            #Here we'll provide partial points on the basis of minutes played
            #alongside the fantasy position. If a player is exclusively a WD then
            #we'll allocate all of the partial points, but if they're DPP then
            #we'll allocate half of the partial points. This gives an inexact
            #estimate, but may be the best we can do.
            if 'WD' in playerPos:
                #Check if minutes played is > than a half of play (i.e. 30 mins)
                if totalMinutesPlayed > 30:
                    #Calculate the estimate between the 8 & 16 points based on minutes played
                    #Check if player is exclusively WD or a DPP & adjust accordingly
                    if playerPos == 'WD':
                        fantasyScore += ((16-8) * (totalMinutesPlayed - 30) / 30) + 8
                    else:
                        fantasyScore += (((16-8) * (totalMinutesPlayed - 30) / 30) + 8) / 2
                        
        #Append to calculated fantasy score list
        calcFantasyScores.append(fantasyScore)
        
        #Example basic histogram plot
        # plt.hist(calcFantasyScores, bins = 20)
        # sns.histplot(calcFantasyScores, bins = 20)
        #### TODO: fit a normal distribution to this to extract a sampled prediction???
        
    #Append fantasy score to sample stats dataframe
    statPredictions.iloc[ii]['sampleStats']['fantasyScore'] = calcFantasyScores
    
    
    ##### UP TO HERE --- FANTASY SCORES CALCULATED FOR SAMPLES...
    
            
# %% OLD BELOW HERE >>> 

# %% Compare stats and fantasy score predictions to actual data

#### NOTE: check the knapsack problem for efficient fantasy score calculations
    

# %% 

#### The above goes OK - but it produces some large values, as well as negative values
#### Creating the covaraince matrix from the individual players stats seems to work better --- still negative values
#### This then uses the weighted mean but not variance in distribution
#### Samples outside of bounds for certain variables could be ignore
#### Variables like deflections and then with or without gain seem to add up which makes sense --- except for when negative...

#### Overall this seems to work OK but could maybe use some tweaks to clean up
#### Or checks in place to avoid weird results
    #### e.g. eliminate any +60 minute match
    #### e.g. then eliminate rows with any negative values?





# %% ----- End of statPrediction.py -----