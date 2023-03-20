# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the prelim final Giants match-up
    and grand final preview for podcast.
    
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

# %% Are Thunderbirds a go in 2023?

#Review some key stats from Thunderbirds season last year

#Read in 2022 team stats
teamStats2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2022],
                                            fileStem = 'teamStats',
                                            matchOptions = ['regular'])
teamStats2022 = teamStats2022[2022]

#Append team name to dataframe for easier interpretation
teamStats2022['squadName'] = [squadDict[squadId] for squadId in teamStats2022['squadId']]
teamStats2022['oppSquadName'] = [squadDict[squadId] for squadId in teamStats2022['oppSquadId']]

#Group by team name and sum to get statistical totals
teamStats2022_totals = teamStats2022.groupby('squadName').sum(numeric_only = True)
teamStats2022_avgs = teamStats2022.groupby('squadName').mean(numeric_only = True)
teamStats2022_oppTotals = teamStats2022.groupby('oppSquadName').sum(numeric_only = True)

#Could argue that the Thunderbirds had the #1 defense in the comp last year
    #Thunderbirds miles ahead at #1 in the comp for gains
        #242 across the season - the next closest was the Vixens at 181
            #Equates to averaging about 4-7 more gains than every other team in the league each game
    #Thunderbirds also allowed the least goal attempts of all teams across the season
#Could also argue though that the Thunerbirds had the least impressive attack in the comp last year too
    #Had the most general play turnovers out of any team in the comp for the season
        #The grand finalist Vixens & Fever were the best for this - and were recording about 5-6 less TOs per game
    #While the Thunderbirds allowed the least goal attempts by their opposition - as a team they also had the least attempts themselves
    #Despite the large number of gains they were generating - the Thunderbirds had the lowest conversion of these to goals out of all teams
    
#How did this contrast to the preseason tournament?

#Read in the 2023 preseason stats
teamPreseasonStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2023],
                                                     fileStem = 'teamStats',
                                                     matchOptions = ['preseason'])
teamPreseasonStats2023 = teamPreseasonStats2023[2023]

#Append team name to dataframe for easier interpretation
teamPreseasonStats2023['squadName'] = [squadDict[squadId] for squadId in teamPreseasonStats2023['squadId']]
teamPreseasonStats2023['oppSquadName'] = [squadDict[squadId] for squadId in teamPreseasonStats2023['oppSquadId']]

#Group by team name and sum to get statistical totals
teamPreseasonStats2023_totals = teamPreseasonStats2023.groupby('squadName').sum(numeric_only = True)
teamPreseasonStats2023_avgs = teamPreseasonStats2023.groupby('squadName').mean(numeric_only = True)
teamPreseasonStats2023_oppTotals = teamPreseasonStats2023.groupby('oppSquadName').sum(numeric_only = True)
    
#Across preseason - the Thunderbirds defense still seems to be firing
    #Still leading the way in gains - they were equal #1 with the Swifts in this stat category
    #Also led the way in limiting scoring opportunities - with their opponents having the least goal attempts
#There's perhaps some hope for a revamped Thunderbirds attack based on preseason
    #Had the 3rd least general play turnovers out of all teams
    #And their gain to goal rate is sitting middle of the road with respect to other teams
        #Still have about a 20% or so lag behind the Vixens & Fever

#Review Cardwell's stats from preseason
cardwellId = 1006558

#Read in player preseason stats
playerPreseasonStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                                       years = [2023],
                                                       fileStem = 'playerStats',
                                                       matchOptions = ['preseason'])
playerPreseasonStats2023 = playerPreseasonStats2023[2023]

#Extract Cardwell's data
cardwellPreseasonStats2023 = playerPreseasonStats2023.loc[playerPreseasonStats2023['playerId'] == cardwellId,]

#Quick check of shooting percentage
(cardwellPreseasonStats2023['goalAttempts'] - cardwellPreseasonStats2023['goalMisses']) / cardwellPreseasonStats2023['goalAttempts']

#Averaging stats out to per 60 minute basis
    #Looking at getting about 40 goals per 60 minute from Cardwell if preseason form holds
        #OK standard relative to other shooters - but also need to factor in Thunderbirds game pace which is typically slower (expect less shots)
    #Shooting percentage may be something to look out for with Cardwell
        #Shot at 80% and 75% in the first 2 preseason games
        #Did bring this back up to 91% in game 3
        
# %% Gains to goals

#Piggy-back of 2022 team stats created earlier

#Vixens led this stat in 2022, converting ~71% of their gains into goal scoring
    #This was a real weapon for the Vixens as they were also #2 in the leage for gains per game
    #Effectively the best team in turning their defense into attacking opportunities
#Magpies were #2 for gains to goal % at ~68%, and the eventual champion Fever were #3 at ~65%
    #Perhaps an ominous warning from preaseason though - the Fever led all teams at ~75% for this stat
        #Fever already a scoring powerhouse - and it could get even better if they keep this up
        
# %% Penalties to gain ratio

#Get player stats and player lists for 2022

#Read in 2022 player stats
playerStats2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerStats',
                                              matchOptions = ['regular'])
playerStats2022 = playerStats2022[2022]

#Read in player lists for 2022
playerLists2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular'])
playerLists2022 = playerLists2022[2022]

#Extract gains and penalties for ease of use
gainsPens2022 = playerStats2022[['playerId','gain','penalties']]

#Get player names for easier interpretation
playerName = []
for playerId in gainsPens2022['playerId']:
    playerName.append(playerLists2022.loc[playerLists2022['playerId'] == playerId,]['surname'].unique()[0])
gainsPens2022['surname'] = playerName

#Sum to get an idea across the year
gainsPens2022_sum = gainsPens2022.groupby(['playerId','surname']).sum().reset_index(drop = False)

#Keep players with at least 25 gains
gainsPens2022_sum = gainsPens2022_sum.loc[gainsPens2022_sum['gain'] >= 25,]

#Calculate penalty to gain ratio across individual games
gainsPens2022_sum['ratio'] = gainsPens2022_sum['penalties'] / gainsPens2022_sum['gain']

#What you're wanting here is a lower number, which equates to more gains relative to the amount of penalties
#What we've found is that most elite defenders seem to sit around or below 3 penalties per gain
    #Across 2022:
        #You've got some pretty good options like Klau, Weston & Dehany sitting at 3-3.5
        #You then step up to players like Bruce, Bakewell-Doran & Latanya Wilson sitting around 2.5
        #And then the real top-tier for last year was Shamera Sterling at about 1.6
            #Which means she's not even getting 2 penalties for every gain she creates

#Review 2021 to see where Pretorius sits

#Read in 2021 player stats
playerStats2021 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2021],
                                              fileStem = 'playerStats',
                                              matchOptions = ['regular'])
playerStats2021 = playerStats2021[2021]

#Read in player lists for 2021
playerLists2021 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2021],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular'])
playerLists2021 = playerLists2021[2021]

#Extract gains and penalties for ease of use
gainsPens2021 = playerStats2021[['playerId','gain','penalties']]

#Get player names for easier interpretation
playerName = []
for playerId in gainsPens2021['playerId']:
    playerName.append(playerLists2021.loc[playerLists2021['playerId'] == playerId,]['surname'].unique()[0])
gainsPens2021['surname'] = playerName

#Sum to get an idea across the year
gainsPens2021_sum = gainsPens2021.groupby(['playerId','surname']).sum().reset_index(drop = False)

#Keep players with at least 25 gains
gainsPens2021_sum = gainsPens2021_sum.loc[gainsPens2021_sum['gain'] >= 25,]

#Calculate penalty to gain ratio across individual games
gainsPens2021_sum['ratio'] = gainsPens2021_sum['penalties'] / gainsPens2021_sum['gain']

#Read in 2020 player stats
playerStats2020 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2020],
                                              fileStem = 'playerStats',
                                              matchOptions = ['regular'])
playerStats2020 = playerStats2020[2020]

#Read in player lists for 2020
playerLists2020 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2020],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular'])
playerLists2020 = playerLists2020[2020]

#Extract gains and penalties for ease of use
gainsPens2020 = playerStats2020[['playerId','gain','penalties']]

#Get player names for easier interpretation
playerName = []
for playerId in gainsPens2020['playerId']:
    playerName.append(playerLists2020.loc[playerLists2020['playerId'] == playerId,]['surname'].unique()[0])
gainsPens2020['surname'] = playerName

#Sum to get an idea across the year
gainsPens2020_sum = gainsPens2020.groupby(['playerId','surname']).sum().reset_index(drop = False)

#Keep players with at least 25 gains
gainsPens2020_sum = gainsPens2020_sum.loc[gainsPens2020_sum['gain'] >= 25,]

#Calculate penalty to gain ratio across individual games
gainsPens2020_sum['ratio'] = gainsPens2020_sum['penalties'] / gainsPens2020_sum['gain']

#The return of Pretorius is an interesting one to discuss here for the Lightning
    #Pretorius is another top tier defender who achieved a ratio of 1.8 back in the 2020 season
        #Still was short of the 1.5 achieved by Sterling that year
    #So now you have both an experienced defender in Pretorius + an improving defender in Dehany
    #anchoring the Lightning's defense --- who seem to both be able to be clean while generating gains

# %% How do you beat the Fever?

#Look at the Fever's losses vs. wins over the last 2 years

#Read in 2021 and 2022 team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2021, 2022],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'])

#Concatenate dataframes for easier use
teamStats = pd.concat([teamStats[2021], teamStats[2022]])

#Extract the Fever team stats
feverId = 810
teamStats_fever = teamStats.loc[teamStats['squadId'] == feverId, ].reset_index(drop = True)

#Extract opposition points for each Fever match-up
oppPoints = []
for matchId in teamStats_fever['matchId']:
    oppPoints.append(teamStats.loc[(teamStats['matchId'] == matchId) &
                                   (teamStats['oppSquadId'] == feverId),
                                   ]['points'].values[0])
teamStats_fever['oppPoints'] = oppPoints

#Create a margin variable
teamStats_fever['margin'] = teamStats_fever['points'] - teamStats_fever['oppPoints']

#Create win/loss variable to group by
teamStats_fever['result'] = ['win' if margin > 0 else 'loss' for margin in teamStats_fever['margin']]

#Look at some statistical averages in wins vs. losses
teamStats_fever_winLossAvgs = teamStats_fever.groupby('result').mean(numeric_only = True)

#Extract losses for characteristics
teamStats_fever_losses = teamStats_fever.loc[teamStats_fever['result'] == 'loss',]

#How to beat the Fever
    #You have to score --- 64 is the lowest total anyone has beat the Fever with over the last 2 years
        #To put this in perspective --- only the Firebirds and Fever averaged > 64 goals per match last year
            #The Fever average 72 FYI --- 6 more than everyone else in the comp
    #Slowing the game down might be effective
        #Over last 2 years, Fever average 8 more possessions per game in wins vs. losses
            #Indicative of reduced pace in the game
        #Another indicator here is 10 less feeds per game in losses vs. wins
            #Effectively reduce the scoring opportunities
    #Keep the game close
        #The Fever's wins over the last 2 years come with an average margin of about 11 goals
        #Once they're out to a lead it's probably unlikely teams will be chasing them down
        
# %% Prediction

#Sunshine Coast Lightning are my outside chance to cause teams trouble this year
    #They're playing the Giants in round 1 who they lost both match-ups too last season
    #Preseason was alright for the Lightning - statistically they improved in a few key
    #categories compared to last year
    #So for one, I'm predicting them to win this game --- but more than this predicting
    #a relatively easy win, let's say a 5 or more goal win

# %% ----- End of 00_preseason_analysis.py ----- %% #