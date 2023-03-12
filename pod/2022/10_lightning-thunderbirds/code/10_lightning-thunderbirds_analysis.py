# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 12 & 13 Lightning & Thunderbirds match-up
    for podcast.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
# import matplotlib.pyplot as plt
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
             8118: 'GIANTS'}
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118}

#Set base directory for processed data
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

# %% Lightning match-up: Key numbers that jumped out

#Shot attempts:
    #77-59 in Vixens favour; 75-47 standard shots for Vixens to 12-2 Super Shots for Lightning
    #Overall shooting percentage of 81.8% for Vixens vs. 88.1% for Lightning
    #Better percetnage despite taking potentially riskier shots
#Huge gain game from both teams:
    #20 for Vixens and 18 for Lightning
#Missed goal turnovers still equal though
    #Vixens hauled in all 7 of the Lightning's missies - no 2nd chances
    #Lightning only hauled in 7 of the Vixen's 14 misses
#Goals from gains:
    #Once again the Vixens led this 14-11
#Super Shots:
    #8 to 1 (i.e. 16 goals to 2) for the Lightning

# %% Gains & deflections in the match

#Get Vixens and Lightning team stats
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]
lightningTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Lightning'],]

#20 gains for the Vixen's - was this their highest for the season?
    #Equal highest gain game for the Vixens

#18 gains for the Lightning - was this their highest for the season?
    #Highest gain game for the Lightning

#Possession changes - 24 to Vixens, 29 to Lightning. Most in a game?

#Group team stats by match Id and sum
totalMatchStats_2022 = teamStats_2022.groupby('matchId').sum()

#Not really - not a lot of unforced turnovers

#20 deflections for the Vixen's - was this their highest for the season?
    #Second highest deflections game for Vixens

#17 deflections for the Lightning - was this their highest for the season?
    #Highest deflection game for Lightning
    
# %% Lightning Super Shots

#Particularly first quarter kept them in it
#Was their total proportion from Super Shots one of the highest?

#Read in quarter stats from the year
teamPeriodStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2022],
                                                   fileStem = 'teamPeriodStats',
                                                   matchOptions = ['regular'])
teamPeriodStats_2022 = teamPeriodStats_2022[2022]

#Create new variable that calculates proportion of total goals from Super Shots
teamPeriodStats_2022['superScoreProp'] = (teamPeriodStats_2022['goal2']*2) / teamPeriodStats_2022['points'] * 100
superScoreProp = teamPeriodStats_2022[['matchId', 'squadId', 'oppSquadId', 'period', 'superScoreProp']]

#Equal 9th highest proportion in a quarter coming from Super Shots at ~46.1%
#2nd highest proportion in a quarter for the Lightning for the year (once at ~58.8% in rd. 10, 4th quarter)

# %% Weston & Mannix 

#7 gains each in game
#Has this happened so far this year?

#Create dictionary to store data in
topTwoGains = {'matchId': [], 'squadId': [],
               'playerId_1': [], 'gain_1': [],
               'playerId_2': [], 'gain_2': []}

#Get player stats for the year
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'])
playerStats_2022 = playerStats_2022[2022]

#Loop through match Id's
matchIds = list(playerStats_2022['matchId'].unique())
for matchId in matchIds:
    
    #Get the squad Id's
    squadIds = list(playerStats_2022.loc[playerStats_2022['matchId'] == matchId,
                                         ]['squadId'].unique())
    
    #Loop through the two squad Id's
    for squadId in squadIds:
        
        #Extract data and sort by gains
        sortedByGains = playerStats_2022.loc[(playerStats_2022['matchId'] == matchId) &
                                             (playerStats_2022['squadId'] == squadId),
                                             ].sort_values(by = 'gain', ascending = False).reset_index()
        
        #Append data
        topTwoGains['matchId'].append(matchId)
        topTwoGains['squadId'].append(squadId)
        topTwoGains['playerId_1'].append(sortedByGains['playerId'][0])
        topTwoGains['gain_1'].append(sortedByGains['gain'][0])
        topTwoGains['playerId_2'].append(sortedByGains['playerId'][1])
        topTwoGains['gain_2'].append(sortedByGains['gain'][1])
        
#Convert to dataframe
topTwoGains_df = pd.DataFrame.from_dict(topTwoGains)

#Calculate variable that describes minimum of the two players gains
topTwoGains_df['minGainsByTwo'] = [np.min(np.array((topTwoGains_df['gain_1'][ind[0]],topTwoGains_df['gain_2'][ind[0]]))) for ind in enumerate(topTwoGains_df['matchId'])]
    
#7 gains by two players is the equal highest for the season
#Only other time it happened was also in round 12, game 1 by Magpies

# %% Watson's Game

#Another 40 feeds for Watson
#How many times has she reached 40+ feeds? How many times have others in the league done this?

#Grab unique player Ids from player stats
playerIds = list(playerStats_2022['playerId'].unique())

#Set-up dictionary to store data in
fortyPlusFeeds = {'playerId': [], 'nGames': []}

#Loop through players
for playerId in playerIds:
    
    #Extract players data and sort by feeds
    playerFeeds = playerStats_2022.loc[playerStats_2022['playerId'] == playerId,
                                       ].sort_values(by = 'feeds', ascending = False).reset_index(drop = True)
    
    #Find index of feeds less than 40
    n40PlusFeeds = np.where(playerFeeds['feeds'].to_numpy() < 40)[0][0]
    
    #Append to dataframe
    fortyPlusFeeds['playerId'].append(playerId)
    fortyPlusFeeds['nGames'].append(n40PlusFeeds)
    
#Convert to dataframe
fortyPlusFeeds_df = pd.DataFrame.from_dict(fortyPlusFeeds)

#Liz Watson has 9 40+ feed games this year - more than anyone else in comp
#playerId 80439 has 8, next most has 4

# %% Thunderbirds match-up: Key numbers that jumped out

#Penalties over match:
    #24-8 penalty count by Vixens in first quarter
    #By the end of the game the Thunderbirds led the penalty count 64-60
#Gains and deflections:
    #Somewhat dominanted by Thunderbirds - 17 gains + 14 deflections with no gain
    #Still 13 gains for the Vixens which isn't a bad total
#Thunderbirds will rue missed opportunities
    #Tbirds gain to goal % of 65% - Vixens at 69%
    #Tbirds TO to goal % of 50% - Vixens at 73%
    #Tbirds missed shot conversion % at 0% - Vixens at 44%


# %% Gains and turnovers to scoring

#From Vixens team stats
    #Ball bounced around a lot - the 27 possession changes by Vixens equals their highest for the season
    #Equalled their round 7 total for the loss to the Magpies
    
#Get Thunderbirds stats
tbirdsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Thunderbirds'],]

#Despite the Vixens equalling their season high - the Tbirds still had more total possession losses at 28
#This is actually right around the Tbirds average for this stat at ~29
#They've actually had games with 30+ and even 40 possession changes/losses this year

#Average out team stats
avgTeamStats_2022 = teamStats_2022.groupby('squadId').mean().reset_index(drop = False)
avgTeamStats_2022['squadId'].replace(squadDict, inplace = True)

#Tbirds avg. gain to goal % is ~63% - 4th in league; Vixens is ~72% - no. 1 in league
#Tbirds TO to goal % is ~59% second worse in league
#Weren't far off their season averages - so the issues that plagued them in converting to scores this game are common

# %% Getting the ball into the circle

#Huge games from Shamera Sterling and Latanya Wilson
    #Sterling - 8 gains with only 7 penalties (0.875 ratio)
    #Wilson - 6 gains with only 9 penalties (1.5 ratio)

#Review Vixens stats for pace:
    #This match was the 2nd lowest pace for the Vixens at 83 possession per 60 mins
    #Indicative of the difficulty it took getting the ball into the circle
    
#Review feeding player stats

#Watson
watsonId = 994224

#Get Watson player stats
watsonPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == watsonId,]

#Review feeds with attempt to feeds ratio
watsonPlayerStats_2022['feedWithAttempt'] / watsonPlayerStats_2022['feeds']

#Last two weeks ease of connection between Watson and circle shooters
    #85% and 80% of her feeds have resulted in a shot attempt
#Against Tbirds this was down to 65%
    #Indicative of even when the ball was getting in there the shooters didn't feel in the best spot
    
# %% Review Liv Lewis game

#Reviewed line-up spreadsheets
    #Thunderbirds were starting to get on top on the scoreboard early in the 3rd quarter
        #Vixens -3 in the first few minutes
    #Liv Lewis injection at GK seemed to stem this flow

#Review player period stats spreadsheet
    #3 gains over the third quarter and start of 4th quarter
    #Only giving up 4 penalties over this period
    
# %% Last quarter scoring

#Was this the worst scoring performance ever?

#Read in period stats data
teamPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                              fileStem = 'teamPeriodStats',
                                              matchOptions = ['regular','final'])

#Review scoring data over years
for year in list(teamPeriodStats.keys()):
    #Loop through scores and check for 5 or less
    for goalsScored in enumerate(teamPeriodStats[year]['goals']):
        #Extract goals for iteration
        if year < 2020:
            goals = goalsScored[1]
        else:
            goals = teamPeriodStats[year]['points'][goalsScored[0]]
        #Review goals scored
        if goals <= 5:
            #Extract details
            squadId = teamPeriodStats[year]['squadId'][goalsScored[0]]
            oppSquadId = teamPeriodStats[year]['oppSquadId'][goalsScored[0]]
            roundNo = teamPeriodStats[year]['roundNo'][goalsScored[0]]
            quarterNo = teamPeriodStats[year]['period'][goalsScored[0]]
            #Print out details - check for extra time period
            if quarterNo <= 4:
                print(f'{goals} total goals scored by {squadId} against {oppSquadId} in quarter {quarterNo} of round {roundNo} in {year}.')

#As acknowledge by Michael Hutchinson already on Twitter
    #The last time a 5 goal quarter happened in Super Netball was 2017
        #Firebirds and Thunderbirds each had a 5 goal quarter
#This match and the Tbirds on the weekend are the only matches in Super Netball history with 5 goal quarters
#Has never happened since Super Shot was introduced
#This did seem to happen more often in the early years of the ANZC though

# %% Fan question

#Has any team has had 17 gains in a match and still lost?

#Read in team stats data
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular','final'])

#Set spot to store outputs
highGainsOutcomes = {'year': [], 'matchId':[],
                     'squadId': [], 'oppSquadId': [],
                     'score': [], 'oppScore': [],
                     'nGains': []}

#Create a game counter
nTotalGames = 0

#Look into gain stats from 2010 onwards when recorded
for year in np.linspace(2010, 2022, 13, dtype = int):
    #Loop through matches from the year
    for gains in enumerate(teamStats[year]['gain']):
        #Check if meeting gains threshold
        if gains[1] >= 17:
            #Add to games counter
            nTotalGames += 1 
            #Get match details
            nGains = gains[1]
            squadId = teamStats[year]['squadId'][gains[0]]
            oppSquadId = teamStats[year]['oppSquadId'][gains[0]]
            matchId = teamStats[year]['matchId'][gains[0]]
            #Get score details
            if year < 2020:
                score = teamStats[year]['goals'][gains[0]]
                oppScore = teamStats[year].loc[(teamStats[year]['matchId'] == matchId) &
                                               (teamStats[year]['squadId'] != squadId),
                                               ]['goals'].values[0]
            else:
                score = teamStats[year]['points'][gains[0]]
                oppScore = teamStats[year].loc[(teamStats[year]['matchId'] == matchId) &
                                               (teamStats[year]['squadId'] != squadId),
                                               ]['points'].values[0]
            #Check for loss
            if score < oppScore:
                # #Print output
                # print(f'{squadId} lost {score}-{oppScore} to {oppSquadId} in {year} with {nGains} gains.')
                #Store outputs
                highGainsOutcomes['year'].append(year)
                highGainsOutcomes['matchId'].append(matchId)
                highGainsOutcomes['squadId'].append(squadId)
                highGainsOutcomes['oppSquadId'].append(oppSquadId)
                highGainsOutcomes['score'].append(score)
                highGainsOutcomes['oppScore'].append(oppScore)
                highGainsOutcomes['nGains'].append(nGains)
                
#Convert to dataframe
highGainsOutcomes_df = pd.DataFrame.from_dict(highGainsOutcomes)

#Replace with squad names
highGainsOutcomes_df['squadId'].replace(squadDict, inplace = True)
highGainsOutcomes_df['oppSquadId'].replace(squadDict, inplace = True)

#See proportion of times it's happened in total
len(highGainsOutcomes_df) / nTotalGames

#Actually happened more than I expected:
    #In games where teams have got 17 or more gains, teams have lost ~26% of the time
#But it's not great news for the Thunderbirds this year:
    #There's been 6 games this year where a team has had 17+ gains and lost
    #Out of those 6 times it's happened - the Thunderbirds have been the losing team 5/6 times
#For our Vixens fans out there:
    #The Vixens have managed to win their last two games while the opposition got 17 & 18 gains
                    
# %% Predictions

#Last week - predicted highest rebound game for season for the Vixens
#Vixens recorded 9 rebounds - which wasn't their highest
    #Had one game with 11 rebounds and three with 10
#Lightning didn't help having their second least amount of goal misses for the year
    #well below their average goal misses
#If anything Kumwenda helped this one out a little bit with some easy misses that she quickly pulled down

#Didn't have a prediction for the Thunderbirds game - which was probably lucky as it was one strange game

#Magpies prediction
magpiesTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Magpies'],]

#Magpies are second in the league for unforced turnovers at ~12.5 per game
#Finals situation that this game is going to present, where it's very likely
#the Magpies are going to need to win to get in to the finals presents a pressure situation
#It's sink or swim for them I think - and if they sink (i.e. lose) I think it's
#going to come from a high unforce turnover game

# %%% ----- End of 10_lightning-thunderbirds_analysis.py -----