# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 14 Magpies match-up
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

# %% Magpies match-up: Key numbers that jumped out

#Pretty even game overall statistically which was reflected in result
#Vixens on top with deflections 13-9
    #Magpies only took 1 gain from their 9 deflections; Vixens only 3 from 13
#Vixens on top with gains as usual 10-5
#Exactly same number of goal attempts (60), goal makes (53) and goal misses (7)
    #Those pesky Super Shots made up the scoring difference
#Hard to tell where the Magpies generated their comeback from in the last Q
    #Gain to goal rate for Vixens 0% in Q4; 100% for Magpies
    #Turnover to goal rate 25% for Vixens in Q4; 60% for Magpies
    #Generating similar gains/turnovers but not being as efficient


# %% Penalties in match

#Review team stats spreadsheets
    #Magpies 81 to Vixens 65
        #Obstruction penalties Magpies 11 - Vixens 8
        #Contact penalties difference Magpies 70 - Vixens 57
        #Vixens cleanliness vs. Magpies willingness to be physical again?
    #Small difference in contact penalties i 1st & 2nd quarter
        #This blew out in 3rd Q with Magpies 24 - Vixens 15 contact penalties
        #May have been a part of where that lead blew out in the first half of the 3rd Q

# %% Watson Watch

#Set Watson Id
watsonId = 994224

#Get 2022 player stats
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'])
playerStats_2022 = playerStats_2022[2022]

#Extract Watson data
watsonPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == watsonId,]

#Still had a pretty solid game
    #43 feeds; 32 feeds with attempts; 29 goal assists
    #Lowest turnover game in the last 5 rounds
    #No intercept passes thrown
    
#Reviewed period player stats spreadsheet
    #Last quarter did have a drop off
    #7 feeds and only 4 feeds with attempt (think about 7 x 4 = 28 feeds total)
    #Only 2 goal assists of 29 for the match were in the last quarter
    #Only 7.5 NtePoints vs. 20+ in all other quarters
    
# %% Adamson vs. Ingles

#Review player period stat spreadsheets
    #Adamson a couple of turnovers in Q2 - Ingles none for the game
    #Adamson 6 contact penalties in the first quarter - Ingles 6 for entire game
    #Very few things showing up on statsheet for either player though
        #WD's getting no statsheet credit as usual right?
        
# %% Vixens gain to goal rate - season low?

#Read in team stats
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]

#Get Vixens team stats
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]

#Round 1 at 50% (W against Firebirds) and Round 5 at 33% (L to SCL)
#8 of 14 matches this year have been 70% or greater
#This was a tale of two halves
    #100% and 80% in 1st and 2nd Q
    #33% and 0% in 3rd and 4th Q
    #Progressively worsened as game went on


# %% Review Fever match-up

#Get Fever team stats
feverTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Fever'],]

#Fever still on typical scoring tear as of late
    #Only 1 game in last 7 scoring < 65 (against Vixens)
    #4 of those last 7 game sinclude scoring > 70
#Same thing goes as each time we've spoken about them
    #If you can keep them under 65 you seem to be in drivers seat

#Average out team stats
avgTeamStats_2022 = teamStats_2022.groupby('squadId').mean().reset_index(drop = False)
avgTeamStats_2022['squadId'].replace(squadDict, inplace = True)

#Often talk about Vixens being a clean side, but Fever actually average a few
#less penalties than the Vixens overall with a couple less contact penalties per game
    #Looking at Fever contact penalties they went up a little bit mid-season, but have come back down towards end

# %% Fan question

#Gain to goal rate over season
avgTeamStats_2022.sort_values(by = 'gainToGoalPerc')[['squadId','gainToGoalPerc']]

#A lot of people asking about this gain to goal percentage and the Tbirds
    #Unsurprisingly they were last in this stat at ~58.4% avg. across season
    #Contrast this to the Vixens who led this stat at ~71.1% avg. across season
#Top 4 in this stat were Vixens, Magpies, Fever & Giants - sound familiar to anything?

#Gain
avgTeamStats_2022.sort_values(by = 'gain')[['squadId','gain']]

#Goal from gains
avgTeamStats_2022.sort_values(by = 'goalsFromGain')[['squadId','goalsFromGain']]

#Despite being last in gain to goal % - the Tbirds still top the league for
#absolute goals from gains sitting at 10 per match
    #Vixens are second at ~9.4 per match
#Kind of incredible to think they can be at either end of these stats but it's
#because they are averaged ~17.2 gains per match, way out ahead of the #2 placed
#Vixens at ~12.9 per game
    #You can almost see the notion that if they just fixed that conversion part
    #of their game they'd be right up the top of the league
    
#Which shooting combo had the most goals scored scaled by minutes played?

#Read in line-up data
lineUpData_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'lineUps',
                                              matchOptions = ['regular'])
lineUpData_2022 = lineUpData_2022[2022]

#Extract just the shooting combos and relevant stats from dataframe
shootingCombos = lineUpData_2022[['matchId',
                                  'squadId',
                                  'GS', 'GA',
                                  'teamStartScore',
                                  'teamEndScore',
                                  'duration']]

#Create a scoring variable
shootingCombos['scoring'] = shootingCombos['teamEndScore'] - shootingCombos['teamStartScore']

#Create a grouped dataframe based on shooting player Id's
#Sum the variables and keep the relevant data
groupedShootingCombos = shootingCombos.groupby(
    ['GS','GA']).sum().reset_index(drop = False)
groupedShootingCombos.drop(['matchId', 'squadId', 'teamStartScore', 'teamEndScore'],
                           axis = 1, inplace = True)

#Create a per 60 minute variable
groupedShootingCombos['scoringPer60'] = groupedShootingCombos['scoring'] / (groupedShootingCombos['duration'] / 60) * 60

#Read in player data to review line-ups
playerList_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular'])
playerList_2022 = playerList_2022[2022]

#Create dictionary with player Id's
playerId = []
displayName = []

#Loop through years
for year in list(playerList_2022.keys()):
    
    #Get unique player Id's
    playerIds = playerList_2022['playerId'].unique()
    
    #Loop through Ids
    for pId in playerIds:
        
        #Check if in list already
        if pId not in playerId:
            
            #Extract and append
            playerId.append(pId)
            displayName.append(playerList_2022.loc[playerList_2022['playerId'] == pId,
                                                    ['displayName']]['displayName'].unique()[0])
    
#Convert to player Id to name dictionary
playerIdDict = dict(zip(playerId, displayName))

#Replace player Id's with names
[groupedShootingCombos[courtPos].replace(playerIdDict, inplace = True) for courtPos in ['GS','GA']]

#Let's limit this to combos that played at least one full quarter worth of time together
    #There were 32 GS/GA combos that met this criteria
#Highest overall scoring combo was Harten & Dwyer with 804 total 
    #Followed by Wallam & Bueta in #2 with 798
    #Kumwenda & Austin were at #4 w/ 739
    #Fan question interested in the Swifts - Fawns & Housby #7 + Housby & Singleton #8
#Question was scoring rate though - so calculated a per 60 minute (theoretical whole game score)
    #No. 1 was Stower & Bueta at ~76 goals per 60 min
    #No. 2 was Wood & Batcheldor at ~75 goals per 60 min
    #Best Vixens combo here was Kumwenda & Samason at #5 w/ ~67 goals per 60 min
        #Sensing that the Super Shot period might have played a role in these combos
    #Best Swifts combo was Singleton at GS and Housby at GA, ranked #12 at ~64 goals per 60 min
           
# %% Predictions

#Last week - predicted Magpies would sink or swim dependent on their average unforced
#turnovers of 12.5

#Get Magpies team stats
magpiesTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Magpies'],]

#You could argue that they both sank and swam - but they did record 15 unforced
#turnovers which was above their season average. In fact was their highest since
#recording 15 in round 5 earlier this year

#Fever prediction
    #Old favourite - Vixens will hold them between 60-65 goals (50% hit rate so far on this)
    #I'll add in that the Fever have had 17 & 18 general play TOs in matches against Vixens
        #But 2 of their last 3 matches have had 20+ turnovers
        #If the Vixens are back at their best then I think they can force this many TOs

# %%% ----- End of 11_magpies.py -----