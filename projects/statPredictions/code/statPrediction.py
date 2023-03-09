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
        > Consistency ratings (see: https://www.espn.com/fantasy/insider/football/insider/story/_/page/consistency2022/fantasy-football-consistency-ratings-2022)
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.weightstats import DescrStatsW
from scipy.stats import multivariate_normal, norm
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import helperFunctions as helper

# %% Define functions



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
# playerStatsPreseason[2022] = playerStatsPreseason[2022][selectStatsList.remove]

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

# %% Run stat predictions for 2022 season
#    Note that this prediction is week-to-week, whereby only one week is predicted
#    at a time (i.e. real data is used in predictions rather than chaining the
#    predictions on to prior predictions)

##### TODO: need a rostered player database for which players to predict for each week
##### This can link up to the player positions database too

#Set a conditional whether to predict or load stats
runStatPredictions2022 = False

#Set year to predict
yearToPredict = 2022

#Set years to use data from
yearsOfData = [2020, 2021]

#Get all round numbers from prediction year
roundList = list(playerStats[yearToPredict]['roundNo'].unique())
roundList.sort()

#Loop through player Id's in fantasy details
for playerId in playerData[yearToPredict]['playerId']:
    
    #Check whether to run stats predictions, otherwise we load the data
    if runStatsPredictions2022:
    
        #Create dictionary to store predicted data
        statPredictionsDict = {'matchId': [], 'playerId': [], 'squadId': [], 'oppSquadId': [],
                               'roundNo': [], 'stat': [], 'normDistribution': []}
        
        #Loop through rounds and make predictions
        for roundNo in roundList:
            
            #Extract past year statistics and any that precede current round
            pastYearStats = pd.concat([playerStats[getYear].loc[playerStats[getYear]['playerId'] == playerId, predictStatsList] for getYear in yearsOfData])
            currentYearStats = playerStats[yearToPredict].loc[(playerStats[yearToPredict]['playerId'] == playerId) &
                                                              (playerStats[yearToPredict]['roundNo'] < roundNo), predictStatsList]
            selectPlayerStats = pd.concat([pastYearStats, currentYearStats])
            
            #Check if preseason stats are needed for the player 
            #We'll use these if there are < 4 games worth of data
            if len(selectPlayerStats) < 4:
                #Extract preseason stats
                selectPlayerPreseasonStats = playerStatsPreseason[yearToPredict].loc[playerStatsPreseason[yearToPredict]['playerId'] == playerId, predictStatsList]
                #Multiply the preseason stats by 1.5 so they match a 60 minute game
                selectPlayerPreseasonStats = selectPlayerPreseasonStats * 1.5
                #Concatenate regular to preseason stats
                selectPlayerStats = pd.concat([selectPlayerPreseasonStats, selectPlayerStats])
            
            #Get the actual player stats for the present round
            actualPlayerStats = playerStats[yearToPredict].loc[(playerStats[yearToPredict]['playerId'] == playerId) &
                                                               (playerStats[yearToPredict]['roundNo'] == roundNo),
                                                               predictStatsList].reset_index(drop = True)
            
            #Check if player was actually listed for the game
            #We also need stats to predict, so check this here too
            #### TODO: will eventually need to change this in some way to simply predict
            #### everyone and give low values to those who aren't expected to play
            if len(actualPlayerStats) > 0 and len(selectPlayerStats) > 0:
            
                #Get match details
                matchId, squadId, oppSquadId = list(playerStats[yearToPredict].loc[(playerStats[yearToPredict]['playerId'] == playerId) &
                                                                                   (playerStats[2022]['roundNo'] == roundNo),
                                                                                   ].reset_index().iloc[0][['matchId',
                                                                                                            'squadId',
                                                                                                            'oppSquadId']
                                                                                                            ].to_numpy(dtype = int))
                
                #Set the weights for. See weights in set-up section for values
                #Have tested if there is an actual impact of these weights, yet changing
                #them doesn't really improve predictions that much. So the selection
                #of these weights is pretty much driven by subjective opinion
                #The process for applying weights is as follows:
                    # Begin by giving the standard weight for every match
                    # Any matches from this year (i.e. based on round number) get increased to the current year game weight
                    # The last 4 matches from the current year get increased to the last four game weight
                    # The last match from the current year gets increased to the most recent game weight
                #### TODO: consider if this works for missed matches in a year?
                #### TODO: consider other options for weights?
                #### TODO: consider if player misses a year?
                
                #Set the default weights        
                weights = np.ones(len(selectPlayerStats)) * standardGameWeight
                
                #Check how many games have come from this year
                nCurrentYear = len(playerStats[yearToPredict].loc[(playerStats[yearToPredict]['playerId'] == playerId) &
                                                                  (playerStats[yearToPredict]['roundNo'] < roundNo), predictStatsList])
                
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
                #### NOTE: covariance matrix appears ill-conditioned or singular --- correct approach?
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
                
                #Loop through each stat and store data related to predictions
                #Here we create and store a normal distribution based on the samples
                for statVar in sampleStats_summary.columns:
                    statPredictionsDict['matchId'].append(matchId)
                    statPredictionsDict['playerId'].append(playerId)
                    statPredictionsDict['squadId'].append(squadId)
                    statPredictionsDict['oppSquadId'].append(oppSquadId)
                    statPredictionsDict['roundNo'].append(roundNo)
                    statPredictionsDict['stat'].append(statVar)
                    statPredictionsDict['normDistribution'].append(norm(sampleStats_summary[statVar]['mean'],
                                                                        sampleStats_summary[statVar]['std']))
                    
        #Save the current players data to file
        with open(f'..\\results\\statPredictions2022\\{playerId}.pkl', 'wb') as pickleFile:
            pickle.dump(statPredictionsDict, pickleFile,
                        protocol = pickle.HIGHEST_PROTOCOL)
                
    # else:
        
    #     #Load the players data


#Convert predictions to dataframe
statPredictions = pd.DataFrame.from_dict(statPredictionsDict).sort_values(
        ['matchId', 'squadId', 'playerId']).reset_index(drop = True)

# %% Create an example visual comparing predicted stat accuracy
#    Example here used is Kate Moloney

##### TODO: up to creating this visualisation...

#### TODO:The lack of the truncated data here causes some strange values, 
#### particularly seems to happen at later rounds

#Set number of values to sample
nSamples = 1000

#Set year to predict
yearToPredict = 2022

#Get all round numbers from prediction year
roundList = list(playerStats[yearToPredict]['roundNo'].unique())
roundList.sort()

#Set player Id
playerId = 991901

#Identify player primary position to guide stats to plot
playerPos = playerData[yearToPredict].loc[playerData[yearToPredict]['playerId'] == playerId,
                                          ]['primaryPosition'].values[0]

#Extract the players stat predictions from dataframe
playerStatPredictions = statPredictions.loc[statPredictions['playerId'] == playerId,]

#Set up a figure to plot the comparisons to
#### TODO: currently just a 3 x 3 grid get the plots right before cleaning up
fig, ax = plt.subplots(figsize = (12, 6), nrows = 3, ncols = 3)

#Loop through the stats we want to visualise for the court position
#Note that this doesn't therefore predict all stats for the player
for statVar in courtPosPrimaryStats[playerPos]:
    
    #Create array to store sampled stat values in
    collatedStatVals = np.zeros((nSamples, len(roundList)))
    
    #Create an array to store the actual stat values
    actualStatVals = np.zeros((len(roundList)))
    
    #Loop through the round numbers for current stat
    for roundNo in roundList:
        
        #Check if the player played the current round
        if roundNo in playerStatPredictions['roundNo'].unique():
        
            #Take random samples from normal distribution for current stat
            #Set seed based on player Id, round number and the index of the stat variable
            sampledStatVals = playerStatPredictions.loc[(playerStatPredictions['roundNo'] == roundNo) &
                                                        (playerStatPredictions['stat'] == statVar),
                                                        ].reset_index(drop = True)['normDistribution'][0].rvs(
                                                            size = nSamples,
                                                            random_state = playerId * roundNo * predictStatsList.index(statVar)
                                                            )
            
            #Get the opposition stat multiplier
            #Get the opposition squad Id
            oppSquadId = playerStatPredictions.loc[playerStatPredictions['roundNo'] == roundNo,
                                                   ]['oppSquadId'].unique()[0]
            #Identify the stat multiplier for the current round
            if roundNo == 1:
                statMultiplier = 1
            else:
                statMultiplier = teamStrengthData.loc[(teamStrengthData['squadId'] == oppSquadId) &
                                                      (teamStrengthData['stat'] == statVar) &
                                                      (teamStrengthData['year'] == yearToPredict) &
                                                      (teamStrengthData['afterRound'] == (roundNo-1)),
                                                      ].reset_index(drop = True)['strengthRatio'][0]
                
            #Scale the stat values using the multiplier
            scaledStatVals = sampledStatVals * statMultiplier
            
            #Store values in array
            collatedStatVals[:,roundNo-1] = scaledStatVals
            
            #Extract actual stat value
            #Get match Id
            matchId = playerStatPredictions.loc[(playerStatPredictions['roundNo'] == roundNo) &
                                                        (playerStatPredictions['stat'] == statVar),
                                                        ].reset_index(drop = True)['matchId'][0]
            #Get players stat value for the match and add to array            
            actualStatVals[roundNo-1] = playerStats[yearToPredict].loc[(playerStats[yearToPredict]['matchId'] == matchId) & 
                                                                       (playerStats[yearToPredict]['playerId'] == playerId),
                                                                       ].reset_index(drop = True)[statVar][0]
            
    #Add to plot
    
    #Distributions of stat predictions
    vp = sns.violinplot(data = collatedStatVals,
                        inner = None,
                        linewidth = 0,
                        width = 0.5,
                        color = 'red', ###TODO: update to squad colour
                        cut = True,
                        zorder = 2,
                        ax = ax.flatten()[courtPosPrimaryStats[playerPos].index(statVar)])
    
    #Lower alpha of violin
    for poly in vp.collections:
        poly.set_alpha(0.3)
        
    #Plot predicted mean
    #### TODO: ...
    
    #Plot actual stat values
    #### TODO: tidy up, don't plot values if didn't play...
    ax.flatten()[courtPosPrimaryStats[playerPos].index(statVar)].scatter(
        x = np.linspace(0, roundList[-1]-1, len(roundList)), y = actualStatVals,
        s = 5, c = 'black', marker = '*',
        zorder = 3)

# %% Test out a linear prediction model of NetPoints on the basis of predicted stats
#    The general point of this is that we can't calculate NetPoints based on the
#    stats provided in the match centre. If a linear model from the stats we can
#    predict well works, then we can estimate NetPoints relatively well

# NOTE: it's possible this might work better in positional groupings, given the
# fact that different stats likely contribute to the NetPoints

# NOTE: there's also likely a significant amount of multicollinearity in the
# predictor variables here

#Test out on a specific year to begin with
yearToExamine = 2022

#Set the metric to predict
metricToPredict = 'netPoints'

#Set the position to predict
posToPredict = 'GS'
predictPlayers = playerData[yearToExamine].loc[playerData[yearToExamine]['primaryPosition'] == posToPredict,
                                               ]['playerId'].to_list()

#Extract the data to an array for model
# X = playerStats[yearToExamine][predictStatsList].to_numpy()
X = playerStats[yearToExamine].loc[playerStats[yearToExamine]['playerId'].isin(predictPlayers),
                                   ][predictStatsList].to_numpy()

#Extract the metric to predict
# Y = playerStats[yearToExamine][metricToPredict].to_numpy()
Y = playerStats[yearToExamine].loc[playerStats[yearToExamine]['playerId'].isin(predictPlayers),
                                   ][metricToPredict].to_numpy()

#Extract training and test datasets (70:30 split)
np.random.seed(12345)
indices = np.random.permutation(X.shape[0])
trainingInd, testInd = indices[:int(X.shape[0]*0.7)], indices[int(X.shape[0]*0.7):]
X_train, X_test = X[trainingInd,:], X[testInd,:]
Y_train, Y_test = Y[trainingInd], Y[testInd]

#Create linear regression object
linRegMod = linear_model.LinearRegression()

#Train the model using the training sets
linRegMod.fit(X_train, Y_train)

#Make predictions using the testing set
Y_pred = linRegMod.predict(X_test)

#Display the coefficients
print('Coefficients: \n', linRegMod.coef_)

#Display the mean squared error
print('Mean squared error: %.2f' % mean_squared_error(Y_test, Y_pred))

#The coefficient of determination: 1 is perfect prediction
print('Coefficient of determination: %.2f' % r2_score(Y_test, Y_pred))

#### On even overall data the coefficient of determination is quite high (0.95)
#### Added in components above the split by primary position to see if this improves
    #### Using just the GS position the MSE is similar, but the coefficient of
    #### determination slightly improves (0.97)    
                                                        
        
# %% Test out the consistency rating metric

#Set year to examine
yearToExamine = 2022

#Set metric to test on
metricToExamine = 'netPoints'

#Get total number of rounds
roundList = list(playerStats[yearToExamine]['roundNo'].unique())
roundList.sort()

#Create dictionary to store data in
consistencyRatingDict = {'playerId': [], 'squadId': [], 'afterRound': [],
                         'consistencyRating': []}

#Loop through players to create rolling consistency rating over each round of the season
for playerId in playerData[yearToExamine]['playerId']:
    
    #Extract the players data for games they played
    playerStatData = playerStats[yearToExamine].loc[(playerStats[yearToExamine]['playerId'] == playerId) &
                                                    (playerStats[yearToExamine]['minutesPlayed'] > 0),
                                                    ['matchId', 'squadId', 'playerId', 'roundNo', 'minutesPlayed', metricToExamine]]
    
    #Loop through rounds and calculate consistency rating
    #Start at second round given that round 1 alone isn't relevant
    for roundNo in np.linspace(2, np.max(roundList), np.max(roundList)-1):
        
        #Create check to see if player has played more than 1 game to calculate consistency
        if len(playerStatData) > 1:
        
            #Calculate mean and standard deviation of metric after current round
            mu = playerStatData.loc[playerStatData['roundNo'] <= roundNo,]['netPoints'].mean()
            sigma = playerStatData.loc[playerStatData['roundNo'] <= roundNo,]['netPoints'].std()
            
            #Calculate consistency rating
            cr = sigma/mu
            
            #Append data to dictionary
            consistencyRatingDict['playerId'].append(playerId)
            consistencyRatingDict['squadId'].append(playerStatData['squadId'].unique()[0])
            consistencyRatingDict['afterRound'].append(roundNo)
            consistencyRatingDict['consistencyRating'].append(cr)
            
#Convert to dataframe
consistencyRating = pd.DataFrame.from_dict(consistencyRatingDict)
    
##### NOTE: negative and nan values are possible here due to negative or zero netpoints
        
    
    

# %% ----- OLDER CODE BELOW ----- %% #

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