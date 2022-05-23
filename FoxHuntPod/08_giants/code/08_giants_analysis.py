# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 9 Giants match-up for
    podcast.
    
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
os.chdir('..\\..\..\\code\\matchCentre')
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
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Key numbers that jumped out

#Reviewed team stats and team period stats spreadsheets
#Super shots - obvious one being 12-1 in Giants favour
#Giants hands and missed opportunities - deflections with no gain led Vixens 19-11
#Pickups 22-7 in Vixens favour - loose balls
#Vixens super clean in extra time - 1 contact penalty and 1 turnover

# %% Giants super shots

#Read in team stats to review in context to year
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]

#Gret giants team stats
giantsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['GIANTS'],]

#Equal highest number of Super Shots with 12 - matches rd 7 28 goal victory against Lightning
#Scoreline with Super Shots counting for 1 would've been 65-51

#What about in a quarter?

#Read in team period stats
teamPeriodStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2022],
                                                   fileStem = 'teamPeriodStats',
                                                   matchOptions = ['regular'])
teamPeriodStats_2022 = teamPeriodStats_2022[2022]

#Get giants team period stats
giantsTeamPeriodStats_2022 = teamPeriodStats_2022.loc[teamPeriodStats_2022['squadId'] == squadNameDict['GIANTS'],]

#The five in the 3rd quarter is their most in a quarter in the year
#The three in both the 2nd and 3rd quarter is their 3rd highest for the year

# %% Vixens penalties

#Review team stats spreadsheet
#Total penalties 89-80
#Contact penalties 56-59; Obstruction penalties 33-21

#Review across periods
#Total penalties 27-14 in 1st quarter; 19-23 in 2nd quarter

#Review these in context of season
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]
vixensTeamPeriodStats_2022 = teamPeriodStats_2022.loc[teamPeriodStats_2022['squadId'] == squadNameDict['Vixens'],]
vixensTeamPeriodStats_2022.sort_values(by = 'penalties', inplace = True)

#Highest overall penalised game for the season for Vixens
#First quarter was their equal highest penalised quarter for the season

#How many times have Vixen's led opposition in penalties for the year?
vixensMatchStats_2022 = teamStats_2022.loc[(teamStats_2022['squadId'] == squadNameDict['Vixens']) |
                                           (teamStats_2022['oppSquadId'] == squadNameDict['Vixens']),]
vixensMatchStatsPenalties_2022 = vixensMatchStats_2022[['matchId', 'squadId', 'oppSquadId', 'penalties']]

#Only 3rd time this year Vixens have outpenalised opponent - where they beat the Fever & lost to Lightning as other 2

# %% Kumwenda's match

#Set kumwenda id
kumwendaId = 80540

#Get player stats for the year
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'])
playerStats_2022 = playerStats_2022[2022]

#Get kumwenda stats for the year
kumwendaPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == kumwendaId,]

#After an relatively average performance against the Magpies
    #2 weeks in a row with 50 goals - only times she's had 50+ for the year

#Extract scoreflow data for the year
scoreFlowData_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2022],
                                                 fileStem = 'scoreFlow',
                                                 matchOptions = ['regular'])
scoreFlowData_2022 = scoreFlowData_2022[2022]

#Get kumwenda's shooting
kumwendaScoreFlow_2022 = scoreFlowData_2022.loc[scoreFlowData_2022['playerId'] == kumwendaId,]

#Had a miss right at the end of round 8
#On a streak of 51 goals straight at the moment - we'll see how long she can take that

# %% Watson's match

#Set Watson Id
watsonId = 994224

#Get Watson season stats
watsonPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == watsonId,]

#Highest centre pass receives for the year so far at 36
#Just one below her top number of feeds for the year with 46
#Equal highest goal assists for her this year with 28
#Highest NetPoints for the year with 121
#Did all this with only 3 turnovers - 2nd lowest for the year

#Review player totals for the year
playerStatsTotals_2022 = playerStats_2022.groupby('playerId').sum()[['centrePassReceives',
                                                                     'feeds',
                                                                     'feedWithAttempt',
                                                                     'goalAssists',
                                                                     'generalPlayTurnovers']]

#So far for season totals:
    #No 2. for feeds
    #No 3. for feeds with attempt
    #No 3. for goal assists
    #No 3. for CPRs
    
#Calculate a feed to turnover ratio
playerStatsTotals_2022['turnoverPerFeed'] = playerStatsTotals_2022['generalPlayTurnovers'] / playerStatsTotals_2022['feeds']

#For turnovers per feed:
    #0.1 turnovers per feed for Watson
    #Just no. 2 in the league for this metric for players with > 200 feeds
        #Just behind Kelsey Brown

#Read in player list to check others
playerList_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular'])
playerList_2022 = playerList_2022[2022]

# %% Fever match preview

#Get Fever team stats
feverTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Fever'],]

#Get average team stats
avgTeamStats_2022 = teamStats_2022.groupby('squadId').mean().reset_index(drop = False)
avgTeamStats_2022['squadId'].replace(squadDict, inplace = True)

#The high rate of scoring combined with low possession changes means the Fever are the most efficient offensive team in the league
    #Not really a big secret that stopping this will help you beat them    
#Fever are still the highest average scoring team by +5 over the Firebirds, and then +8 over the Magpies
#Avg. differential between Fever and Vixens is ~10 goals
    #Key to winning is clearly both slowing down Fever scoring, while potentially increasing their own
#Fever also lead the league with the lowest number of possession changes
    #~20 per match; Vixens No.2 with ~22
    #Both teams clean with the ball - whoever can force the other into more mistakes will help win
    
# %% Swifts match preview

#Near opposite to Fever match-up
    #Swifts are 2nd lowest for average total goals and 2nd worst for possession changes (only behind Thunderbirds)
#2nd bottom in league for centre pass to goal conversion at 65%
#Bottom of the league for goal shooting percentage at ~79%
#It's hard to win doing these things so the Vixens would be wise to tyr and push the Swifts into this pattern

# %% Fan questions

#What is the highest number of successful super shots made by a team in a game?
#And what is the highest number shot by a losing team? 

#Read in team stats from Super Shot years
teamStats_superShotEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2020, 2021, 2022],
                                                     fileStem = 'teamStats',
                                                     matchOptions = ['regular', 'final'])

#Sort by super shots
goal2_superShotEra = {}
for year in list(teamStats_superShotEra.keys()):
    #Just select the relevant data
    goal2_superShotEra[year] = teamStats_superShotEra[year][['matchId','squadId', 'goal2']]
    #Sort by Super Shots
    goal2_superShotEra[year].sort_values(by = 'goal2',
                                         ascending = False,
                                         inplace = True)
    #Reset index
    goal2_superShotEra[year].reset_index(drop = True, inplace = True)
    
#Read in scoreflow data from Super Shot years
scoreFlow_superShotEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2020, 2021, 2022],
                                                     fileStem = 'scoreFlow',
                                                     matchOptions = ['regular', 'final'])

#Calculate team totals from score flow
scoreTotals = {}
for year in list(scoreFlow_superShotEra.keys()):
    scoreTotals[year] = scoreFlow_superShotEra[year].groupby(['matchId','squadId']).sum()['scorePoints'].reset_index(drop = False)
    
#Identify win or loss for each Super Shot value
for year in list(goal2_superShotEra.keys()):
    teamResult = []
    #Loop through indices
    for indNo in range(len(goal2_superShotEra[year])):
        #Find matching match id and squad Id score in score flow
        teamScore = scoreTotals[year].loc[(scoreTotals[year]['matchId'] == goal2_superShotEra[year]['matchId'][indNo]) &
                                          (scoreTotals[year]['squadId'] == goal2_superShotEra[year]['squadId'][indNo]),
                                          ]['scorePoints'].values[0]
        #Find opposition score in same match
        oppScore = scoreTotals[year].loc[(scoreTotals[year]['matchId'] == goal2_superShotEra[year]['matchId'][indNo]) &
                                         (scoreTotals[year]['squadId'] != goal2_superShotEra[year]['squadId'][indNo]),
                                         ]['scorePoints'].values[0]
        #Check match status
        if teamScore > oppScore:
            teamResult.append('win')
        elif teamScore < oppScore:
            teamResult.append('loss')
        else:
            teamResult.append('draw')
    #Add to dataframe
    goal2_superShotEra[year]['teamResult'] = teamResult
    #Replace squad Id's with name
    goal2_superShotEra[year]['squadId'].replace(squadDict, inplace = True)

#In 2020:
    #Giants recorded 17 in round 14 draw with Swifts
    #Swifts recorded 15 in round 12 loss to Fever
    #Giants recorded 12 in round 1 loss to Swifts
    
#In 2021:
    #Giants recorded 11 in round 4 win against Vixens
    #Giants recorded 10 in round 5 & 9 losses to Fever & Swifts
    
#In 2022:
    #Giants recorded 12 in round 9 loss to Vixens
    #Swifts recorded 12 in round 5 loss to Fever
    #Giants recorded 12 in round 7 win to Lightning

# %% Predictions - Fever

#Last week predicted > 15 gains + 100% gain to goal rate
#Vixens had 16 gains but gain to goal rate of 63%
#Was 20% and 60% in 1st & 2nd quarter - but 100% for 2nd half and extra time

#Check Fever's scoring for the season
feverTeamStats_2022['points']

#Fever have only been held under 70 twice this season
    #Against the Vixens earlier this year with 66 [loss]
    #Against the Thunderbirds with 60 a few rounds bac [win]
#Deja vu with prediction
    #Vixens will hold the Fever under 70
    #And this time it will be in the range of 60-65
    
# %% Predictions - Swifts

#Get Swifts team stats
swiftsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Swifts'],]

#Seven of their 9 games have had 20+ turnovers, including last 3
#With the Vixens solid defence I'd say this 20+ turnover trend will continue

# %%% ----- End of 08_giants_analysis.py -----