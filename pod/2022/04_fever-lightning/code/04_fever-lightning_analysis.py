# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 4 & 5 Fever and Lightning
    match-ups for podcast.
    
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

#Set relevant squad Id's
vixensSquadId = 804
feverSquadId = 810
lightningSquadId = 8117
thunderbirdsSquadId = 801

#Identify round data directory for any specific loading
procDatDir = '..\\..\\..\\..\\data\\matchCentre\\processed\\116650301_2022_SSN_11665_r3_g1\\'

#Set base directory for processed data
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

# %% Key numbers that jumped out - Fever match

#Reviewed team stats spreadsheets
#Vixens flirting with danger? Fever had 23 deflections but 16 of these with no gain
#Statistically was a pretty tight game
#Vixens once again slightly more efficient than opponent
#Fever had one more gain but less efficient
    # - Centre pass to goal 80% - 73% in Vixens favour
    # - Gain to goal 80% - 64% in Vixens favour
#Fever had +4 unforced turnovers

#The timing of how things played out also probably had an impact on the way the game went
    # - Barrage of Super Shots in 1st half by Vixens 7 to 1 vs. 6 to 1 in 2nd half
    
# %% How was Lewis' game?

#Set Lewis id
lewisId = 1004510

#Reviewed player stats sheet
#Underwhelming when looking at the stat sheet outside of 3 intercepts
#Good defensive play not really recorded statistically

#Fowler recorded 15 goals in 2nd half - how often does that happen when playing full half?

#Set Fowler id
fowlerId = 80826

#Bring in player period stats from Super Netball
playerPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                                years = [2018, 2019, 2020, 2021, 2022],
                                                fileStem = 'playerPeriodStats',
                                                matchOptions = ['regular', 'final'])

#Set counters
more15_InHalf = 0
less15_InHalf = 0

#Loop through years
for year in list(playerPeriodStats.keys()):
    
    #Extract data and Fowler stats
    fowlerPeriodStats = playerPeriodStats[year].loc[playerPeriodStats[year]['playerId'] == fowlerId,]
    
    #Get match Id's
    matchIds = list(fowlerPeriodStats['matchId'].unique())
    
    #Loop through match Id's
    for matchId in matchIds:
        
        #Extract match data
        fowlerMatchData = fowlerPeriodStats.loc[fowlerPeriodStats['matchId'] == matchId,]
        
        #Check if played full halves
        #First half
        if fowlerMatchData.loc[(fowlerMatchData['period'] == 1) |
                               (fowlerMatchData['period'] == 2),
                               ['minutesPlayed']].sum().to_numpy()[0] >=30:
            fullFirstHalf = True
        else:
            fullFirstHalf = False
        #Second half
        if fowlerMatchData.loc[(fowlerMatchData['period'] == 3) |
                               (fowlerMatchData['period'] == 4),
                               ['minutesPlayed']].sum().to_numpy()[0] >=30:
            fullSecondHalf = True
        else:
            fullSecondHalf = False
            
        #Check halves if necessary
        
        #First half
        if fullFirstHalf:
            if year >= 2020:
                #Sum points
                goalsFirstHalf = fowlerMatchData.loc[(fowlerMatchData['period'] == 1) |
                                                     (fowlerMatchData['period'] == 2),
                                                     ['points']].sum().to_numpy()[0]
            else:
                #Sum goals
                goalsFirstHalf = fowlerMatchData.loc[(fowlerMatchData['period'] == 1) |
                                                     (fowlerMatchData['period'] == 2),
                                                     ['goals']].sum().to_numpy()[0]
            #Check and apply to counter
            if goalsFirstHalf > 15:
                more15_InHalf += 1
            else:
                less15_InHalf += 1
                
        #Second half
        if fullSecondHalf:
            if year >= 2020:
                #Sum points
                goalsSecondHalf = fowlerMatchData.loc[(fowlerMatchData['period'] == 3) |
                                                     (fowlerMatchData['period'] == 4),
                                                     ['points']].sum().to_numpy()[0]
            else:
                #Sum goals
                goalsSecondHalf = fowlerMatchData.loc[(fowlerMatchData['period'] == 3) |
                                                     (fowlerMatchData['period'] == 4),
                                                     ['goals']].sum().to_numpy()[0]
            #Check and apply to counter
            if goalsSecondHalf > 15:
                more15_InHalf += 1
            else:
                less15_InHalf += 1
                
#In Super Netball years - this match was first time being held to 15 or less goals!

# %% Key numbers that jumped out - Lightning match

#Reviewed team stats sheet
#Vixens being outgained 6 to 11 by Lightning
#Vixens lack of efficiency from gains with gain to goal per 33% to 82% Lightning
#Vixens only 2 goals from gains

#Are these season lows for the Vixens?
#Bring in team stats from this year
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]

#Get Vixens stats
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == vixensSquadId, ]
vixensTeamStats_2022['gain'] #season low for gains
vixensTeamStats_2022['gainToGoalPerc'] #season low for gain to goal
vixensTeamStats_2022['goalsFromGain'] #season low for goals from gains

#Anything else that jumps out?
vixensTeamStats_2022['goals'] / vixensTeamStats_2022['goalAttempts']
#season low shooting % - ~84% when most games have been up around ~87-90%
#also failed to convert any of these missed shots (0% missed goal turnover)

vixensTeamStats_2022['penalties'] #Season high for penalties

#Basically everything the Vixens have done well this year - did not happen in this game


# %% Watson's game vs. Lightning compared to others?

#Set Watson Id
watsonId = 994224

#Grab in player stats
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'])
playerStats_2022 = playerStats_2022[2022]

#Extract Watson's stats
watsonPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == watsonId,]

#Check across matches
watsonPlayerStats_2022['feeds'] #season low
watsonPlayerStats_2022['feedWithAttempt'] #season low
watsonPlayerStats_2022['centrePassReceives'] #season low
watsonPlayerStats_2022['secondPhaseReceive'] #season high

#Shut-down but still involved at second phase more than usual
#Perhaps interupted the flow of the Vixens attack

# %% Question

#Impact of fatigue in stats?
#Differences in penalties? Differences in turnovers? Net points?

#Read in team period stats from this year
teamPeriodStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2022],
                                                   fileStem = 'teamPeriodStats',
                                                   matchOptions = ['regular'])
teamPeriodStats_2022 = teamPeriodStats_2022[2022]

#Group by period and average out data
averagePeriodStats = teamPeriodStats_2022.groupby(['period']).mean()

#Penalties
averagePeriodStats['penalties'] 
# period
# 1    15.0
# 2    15.2
# 3    15.8
# 4    15.1

#Contact penalties
averagePeriodStats['contactPenalties'] 
# period
# 1    11.600
# 2    11.925
# 3    12.500
# 4    12.200

#General play turnovers
averagePeriodStats['generalPlayTurnovers'] 
# period
# 1    5.075
# 2    5.150
# 3    4.650
# 4    5.275

#Unforced turnovers
averagePeriodStats['unforcedTurnovers']
# period
# 1    2.850
# 2    3.625
# 3    3.050
# 4    3.475

#Pace per 60
averagePeriodStats['pacePer60']
# period
# 1    93.2
# 2    95.0
# 3    92.6
# 4    93.3

#What about in these last few rounds?

#Group by round
averageRoundStats = teamStats_2022.groupby(['roundNo']).mean()

#Penalties
averageRoundStats['penalties'] 
# roundNo
# 1    62.875
# 2    59.375
# 3    62.500
# 4    59.750
# 5    61.000

#Contact penalties
averageRoundStats['contactPenalties'] 
# roundNo
# 1    49.625
# 2    47.375
# 3    47.500
# 4    47.625
# 5    49.000

#General play turnovers
averageRoundStats['generalPlayTurnovers'] 
# roundNo
# 1    19.250
# 2    20.250
# 3    19.125
# 4    19.750
# 5    22.375

#Unforced turnovers
averageRoundStats['unforcedTurnovers']
# roundNo
# 1    12.625
# 2    14.750
# 3    11.000
# 4    12.500
# 5    14.125

#Pace per 60
averageRoundStats['pacePer60']
# roundNo
# 1    92.375
# 2    94.500
# 3    91.875
# 4    93.250
# 5    95.625

# %% Predictions...

#Review Scherian stas for the year
scherianId = 80296
scherianPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == scherianId,]

#How have the Thunderbirds been going?
tbirdsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == thunderbirdsSquadId,]

#Compare squad averages
averageTeamStats = teamStats_2022.replace(squadDict).groupby('squadId').mean()

#Thunderbirds actually have the lowest goals against - 250 over five matches (avg. 50 per match)
#They also have the lowest goals for - 255 over 5 matches (avg. 51 per match)
#Highest average unforced turnovers and general play turnovers
#Highest average intercepts and gains (avg. gain = 19)
#Vixens are lowest for avg. general play turnovers

#Vixens only give up ~18 general play turnovers a game

#First time the Thunderbirds had 60 scored against them was on the weekend with Firebirds

#Prediction is less than 20 turnovers for the match and they can continue the trend
#of scoring 60+ on the Thunderbirds


# %%% ----- End of 04_fever-lightning_analysis.py -----