# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    
    Function to help with creating the Netball Scoop fantasy team bot.
    This script aims to develop a regression model that predicts fantasy scores.
    
    See for bambi predictions: https://github.com/bambinos/bambi/pull/372
	
	Note: the interaction effect with round number is probably wrong, as this seems like it's for a categorical variable
    
"""

# %% Import packages

import pandas as pd
import os
from difflib import SequenceMatcher
import numpy as np
import pymc as pm
import bambi as bmb
import arviz as az
import matplotlib.pyplot as plt

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

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

#Read in player stats data for the 2020 and 2021 regular seasons
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'])

#Read in substitutions data
subsData = collatestats.getSeasonStats(baseDir = baseDir,
                                       years = [2020, 2021],
                                       fileStem = 'substitutions',
                                       matchOptions = ['regular'])

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021],
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

# %% Collate starting player prices and details

#Read in starting price data and details
fantasyPlayerDetails = {}
fantasyPlayerDetails[2020] = pd.read_csv('..\\..\\data\\startingPrices_2020.csv')
fantasyPlayerDetails[2021] = pd.read_csv('..\\..\\data\\startingPrices_2021.csv')

#Link up player Id's to price database
for year in list(fantasyPlayerDetails.keys()):
    
    #Create list to store data in
    playerPriceIds = []
    # playerNameCheck = []
    
    #Loop through players in price list
    for ii in fantasyPlayerDetails[year].index:
        
        #Get player full name
        playerFullName = f'{fantasyPlayerDetails[year].iloc[ii]["firstName"]} {fantasyPlayerDetails[year].iloc[ii]["surname"].capitalize()}'
        
        #Compare current player name ratio to all from current year
        nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[year]['fullName']]
        
        #Get index of maximum ratio
        maxRatioInd = nameRatios.index(np.max(nameRatios))
        
        #Get player Id at the index and append to list
        playerPriceIds.append(playerData[year].iloc[maxRatioInd]['playerId'])
        # playerNameCheck.append(playerFullName)
        
    #Append player Id's to price list dataframe
    fantasyPlayerDetails[year]['playerId'] = playerPriceIds
   

# %% Calculate fantasy scores

"""
See: https://netballscoop.com/forums/topic/2020-fantasy-netball-ssn-2/
See: https://netballscoop.com/forums/topic/2021-fantasy-netball-ssn/

"""

#Create the statistics to score on
pointVals = {2020: {'goal1': 2, 'goal2': 4,
                    'goalMisses': -4, 'goalAssists': 2,
                    'feeds': 1, 'gain': 4,
                    'intercepts': 8, 'deflectionWithGain': 8,
                    'deflectionWithNoGain': 4, 'rebounds': 4,
                    'pickups': 8, 'contactPenalties': -0.5,
                    'obstructionPenalties': -0.5, 'generalPlayTurnovers': -4,
                    'interceptPassThrown': -4},
             2021: {'goal1': 2, 'goal2': 4,
                    'goalMisses': -4, 'goalAssists': 2,
                    'feedWithAttempt': 2, 'feeds': 1, 'gain': 4,
                    'intercepts': 6, 'deflections': 6,
                    'rebounds': 4, 'pickups': 6,
                    # 'contactPenalties': -0.5, 'obstructionPenalties': -0.5,
                    'generalPlayTurnovers': -2, 'interceptPassThrown': -2}}

#Loop through years
for year in list(playerStats.keys()):
        
    #Set a list to store fantasy scores in
    fantasyScores = []
    
    #Loop through dataframe indices
    for ii in playerStats[year].index:
        
        #Set starting score as zero
        score = 0
        
        #Get player Id
        playerId = playerStats[year].iloc[ii]['playerId']
        
        #Get match Id
        matchId = playerStats[year].iloc[ii]['matchId']
        
        #Get players fantasy position
        try:
            #Check in the fantasy list to start with
            fantasyPos = fantasyPlayerDetails[year].loc[fantasyPlayerDetails[year]['playerId'] == playerId,
                                                        ['position']].values[0][0]
        except:
            #Grab the player position from the match data
            matchPosData = subsData[year].loc[(subsData[year]['matchId'] == matchId) &
                                              (subsData[year]['playerId'] == playerId),
                                              ['startingPos','duration']].reset_index(drop = True)
            #Drop the substitution data
            matchPosData = matchPosData.loc[matchPosData['startingPos'] != 'S']
            #Get the unique position values in the same form as the fantasy data
            fantasyPos = '/'.join(list(matchPosData['startingPos'].unique()))
            #Do a quick check to see if there are mixed positions for CPR calculation
            if 'A' in fantasyPos and 'D' in fantasyPos:
                #Set court position to be that with highest duration
                fantasyPos = matchPosData.groupby('startingPos').sum().sort_values(
                        by = 'duration', ascending = False).reset_index().iloc[0]['startingPos']
        
        #Add the standard scoring values
        for stat in list(pointVals[year].keys()):
            score += playerStats[year].iloc[ii][stat] * pointVals[year][stat]
        
        #Anyone who gets on court = 20 points
        if playerStats[year].iloc[ii]['minutesPlayed'] > 0:
            score += 20

        #Centre pass receive = 0.5 points (GA/WA) / 3 points (GD/WD)
        if year == 2020:
            #Check for relevant player positions
            if 'GA' in fantasyPos or 'WA' in fantasyPos:
                score += playerStats[year].iloc[ii]['centrePassReceives'] * 0.5
            elif 'GD' in fantasyPos or 'WD' in fantasyPos:
                score += playerStats[year].iloc[ii]['centrePassReceives'] * 3
        #Centre pass receive = 1 point per 2 CPRs (GA/WA) / 3 points (GD/WD)
        if year == 2021:
            #Check for relevant player positions
            if 'GA' in fantasyPos or 'WA' in fantasyPos:
                score += np.floor(playerStats[year].iloc[ii]['centrePassReceives'] / 2) * 1
            elif 'GD' in fantasyPos or 'WD' in fantasyPos:
                score += playerStats[year].iloc[ii]['centrePassReceives'] * 3
        
        #Penalty calculation for for 2021
        #-1 point per 2 penalties
        if year == 2021:
            totalPenalties = playerStats[year].iloc[ii]['obstructionPenalties'] + playerStats[year].iloc[ii]['contactPenalties']
            score += np.floor(totalPenalties / 2) * -1
        
        #Check WD position for full game (10 points) or > half game (5 points)
        #Get substitution data for player and match
        matchPosData = subsData[year].loc[(subsData[year]['matchId'] == matchId) &
                                          (subsData[year]['playerId'] == playerId),
                                          ['startingPos','duration']].reset_index(drop = True)
        #Check for full game at WD - it will be the only position
        if len(list(matchPosData['startingPos'].unique())) == 1 and list(matchPosData['startingPos'].unique())[0] == 'WD':
            score += 10
        else:
            #Check if at least half of game was played at WD
            sumMatchPosData = matchPosData.groupby('startingPos').sum().reset_index()
            #Check for WD play
            if 'WD' in list(sumMatchPosData['startingPos']):
                #Check if duration > half of a match (4 * 900 / 2 seconds)
                if sumMatchPosData.loc[sumMatchPosData['startingPos'] == 'WD',
                                       'duration'].to_numpy()[0] >= (4 * 900 / 2):
                    score += 5

        #Append to fantasy score list
        fantasyScores.append(score)
        
    #Append to dataframe
    playerStats[year]['fantasyScore'] = fantasyScores

# %% Collate weekly fantasy data

#Set up dictionary to store data in
fantasyData = {}

#Loop through years
for year in list(playerStats.keys()):
    
    #Set-up dictionary for year to store data in
    fantasyData[year] = {'playerId': [], 'roundNo': [], 'fantasyPrice': [],
                         'fantasyScore': [], 'recentFantasyAvg': [], 'priorYearFantasyAvg': [],
                         'priceChange': [], 'totalPriceChange': []}
    
    #Loop through unique players
    for playerId in list(playerStats[year]['playerId'].unique()):
        
        #Look for the players average fantasy score from last year
        yearVar = f'avg{str(year-1)}'
        try:
            priorYearFantasyAvg = fantasyPlayerDetails[year].loc[fantasyPlayerDetails[year]['playerId'] == playerId,
                                                                 [yearVar]].values[0][0]
        except:
            priorYearFantasyAvg = np.nan
        
        #Extract the current players data
        currPlayerStats = playerStats[year].loc[playerStats[year]['playerId'] == playerId,]
        
        #Set games played variable
        gamesPlayed = 0
        
        #Loop through rounds
        allRounds = playerStats[year]['roundNo'].unique()
        allRounds.sort()
        for roundNo in allRounds:
            
            #Get the players fantasy score for the round
            #Try first to see if the player played the round
            try:
                fantasyScore = currPlayerStats.loc[currPlayerStats['roundNo'] == roundNo,
                                                   ['fantasyScore']].to_numpy()[0][0]
            except:
                fantasyScore = np.nan
                
            #Only progress and collate data if there was a score
            if fantasyScore > 0:
            
                #Set the players fantasy price for this round (/1000)
                #Also calculate the fantasy score average over last 3 rounds (if possible)
                if gamesPlayed < 3:
                    #Grab the starting price
                    #Try to find the starting price
                    try:
                        fantasyPrice = fantasyPlayerDetails[year].loc[fantasyPlayerDetails[year]['playerId'] == playerId,
                                                                      ['price']].to_numpy()[0][0] / 1000
                    except:
                        #Set a default starting price of 20
                        fantasyPrice = 20
                    #Set price change values to nan
                    priceChange = np.nan
                    totalPriceChange = np.nan
                    #Set a nan for recent score
                    recentFantasyAvg = np.nan
                else:
                    #Calculate recent fantasy average (last 3 games)
                    #Get scoring data for player
                    scoringToDate = pd.DataFrame.from_dict(fantasyData[year])['fantasyScore'].to_numpy()
                    #Get the 3 most recent scores (dropping any nan's)
                    recentScores = scoringToDate[~np.isnan(scoringToDate)][-3:]
                    #Calculate average over the scores
                    recentFantasyAvg = np.mean(recentScores)
                    #Calculate update price based on last 3 games
                    #Get their current price
                    currentPrice = pd.DataFrame.from_dict(fantasyData[year])['fantasyPrice'].to_numpy()[-1] * 1000
                    #Calculate exact new price (this is /1000)
                    exactNewPrice = np.round((currentPrice * 0.00067) + (np.sum(recentScores) / 9))
                    #Round down to nearest 5
                    fantasyPrice = np.floor(exactNewPrice / 5) * 5
                    #Check if fantasy price is sitting below the min of 20
                    if fantasyPrice < 20:
                        fantasyPrice = 20
                    #Calculate price change for round
                    priceChange = fantasyPrice - (currentPrice / 1000)
                    #Calculate total price change
                    #Try to find starting price
                    try:
                        totalPriceChange = fantasyPrice - fantasyPlayerDetails[year].loc[fantasyPlayerDetails[year]['playerId'] == playerId,
                                                                                         ['price']].to_numpy()[0][0] / 1000
                    except:
                        #Use a starting price of 20
                        totalPriceChange = fantasyPrice - 20
                
                #Add to the games played
                gamesPlayed += 1
                    
                #Append data to dictionary
                fantasyData[year]['playerId'].append(playerId)
                fantasyData[year]['roundNo'].append(roundNo)
                fantasyData[year]['fantasyPrice'].append(fantasyPrice)
                fantasyData[year]['fantasyScore'].append(fantasyScore)
                fantasyData[year]['recentFantasyAvg'].append(recentFantasyAvg)
                fantasyData[year]['priorYearFantasyAvg'].append(priorYearFantasyAvg)
                fantasyData[year]['priceChange'].append(priceChange)
                fantasyData[year]['totalPriceChange'].append(totalPriceChange)

##### TODO: finish cleaning this fantasy data up to useable format

# %% Test out Bayesian regression

"""

See: https://towardsdatascience.com/bayesian-linear-regression-in-python-using-machine-learning-to-predict-student-grades-part-2-b72059a8ac7e
See: https://towardsdatascience.com/applied-bayesian-inference-with-pymc3-and-bambi-pt-3-d4bfb3211509

"""

#Extract the 2020 data to a dataframe to test out
df = pd.DataFrame.from_dict(fantasyData[2020])

#Formula for Bayesian linear regression
#### TODO: should this include starting price too? Or does price change cover this?
regressionFormula = 'fantasyScore ~ fantasyPrice + recentFantasyAvg + priorYearFantasyAvg + (priceChange | roundNo) + totalPriceChange'

#Context for the model
####TODO: consider parameters...
"""
The glm module is deprecated and will be removed in version 4.0
We recommend to instead use Bambi https://bambinos.github.io/bambi/
pymc3 seems to fail now after package updates to get bambi to work
"""
# with pm.Model() as normal_model:
    
#     #The prior for the model parameters will be a normal distribution
#     family = pm.glm.families.Normal()
    
#     #Creating the model requires a formula and data (and optionally a family)
#     pm.GLM.from_formula(regressionFormula, data = df, family = family)
    
#     #Perform Markov Chain Monte Carlo sampling
#     normal_trace = pm.sample(draws = 1000, chains = 4, tune = 1000)

# #Model plots    
# #Trace plot
# pm.traceplot(normal_trace)
# plt.tight_layout()
# #Forest plot
# pm.forestplot(normal_trace)
# #Posteriors
# pm.plot_posterior(normal_trace, figsize = (14, 14))

# #Model summary
# pm.summary(normal_trace)

# #Display model formula
# model_formula = 'fantasyScore = '
# for variable in normal_trace.varnames:
#     model_formula += ' %0.2f * %s +' % (np.mean(normal_trace[variable]), variable)

# ' '.join(model_formula.split(' ')[:-1])




# %% Bambi variant

"""
See: https://github.com/bambinos/bambi/blob/main/docs/notebooks/multi-level_regression.ipynb
See: https://github.com/bambinos/bambi/blob/main/docs/notebooks/ESCS_multiple_regression.ipynb
See: https://www.pymc.io/projects/examples/en/latest/generalized_linear_models/GLM-robust.html
TODO: Need to consider interaction effects with player? Or round number and price change?
Bambi doesn't seem to work with incomplete data
"""
#Initialize the fixed effects only model
df_clean = df.dropna()
model = bmb.Model(regressionFormula, df_clean)

#Fit the model using 1000 on each of 4 chains
### TODO: consider sampling parameters
results = model.fit(draws = 1000, chains = 4)

#Plot posteriors
az.plot_trace(results, compact = True)
plt.tight_layout()

#Key summary and diagnostic info on the model parameters
az.summary(results)

# #Display model formula
# model_formula = 'fantasyScore = '
# for variable in results.varnames:
#     model_formula += ' %0.2f * %s +' % (np.mean(normal_trace[variable]), variable)

# ' '.join(model_formula.split(' ')[:-1])

#Compute the posterior preductive distribution
posterior_predictive = model.predict(results, kind = 'pps')
az.plot_ppc(results)



#Test out trace on a sample from the database

# for variable in results.varnames:
#         var_dict[variable] = trace[variable]

# %% Bambi beta regression

"""
See: https://github.com/bambinos/bambi/blob/main/docs/notebooks/beta_regression.ipynb
"""

# #Plot fantasy score as histogram
# df['fantasyScore'].hist(bins = 50)

# #Model fantasy scores using an intercept only model
# model_avg = bmb.Model('fantasyScore ~ 1', df, family = 'beta')
# avg_fitted = model_avg.fit()













# %%% ----- End of scorePrediction.py -----