# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 1 SSN match-ups.
    
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

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','final'])

#Create a unique player dictionary
#Create dictionary to append players to
playerDict = {'playerId': [],
              'firstName': [], 'surname': [], 'fullName': []}
for year in list(playerLists.keys()):
    
    #Get unique player Id's for year
    uniquePlayerIds = list(playerLists[year]['playerId'].unique())
    
    #Loop through unique player Id's
    for playerId in uniquePlayerIds:
        
        #Check if player Id already in dictionary list
        if not playerId in playerDict['playerId']:
        
            #Extract player details
            playerDetails = playerLists[year].loc[playerLists[year]['playerId'] == playerId,]
            
            #Collate player name variables and append
            playerDict['playerId'].append(playerId)
            playerDict['firstName'].append(playerDetails['firstname'].unique()[0])
            playerDict['surname'].append(playerDetails['surname'].unique()[0])
            playerDict['fullName'].append(f'{playerDetails["firstname"].unique()[0]} {playerDetails["surname"].unique()[0]}')

#Convert to dataframes
playerData = pd.DataFrame.from_dict(playerDict)

# %% Round match-ups

#Mostly reviewing match stat sheets throughout here --- comments added

# %% Fever vs. Vixens

#The Fever's defense was more Vixens like
    #Led the Vixens with 11 gains to 5 & converted 82% of their gains to goal vs. the Vixens 40%
#Vixens had 6 more goal attempts than Fever - but misses were 12-3
    #Vixens only converted 17% of their missed shots to goals vs. Fever's 67%
#You'd almost be surprised or happy as a Vixens fan to see these stats and to only have lost by 1

# %% Magpies vs. Swifts

#Pretty similar to the Fever vs. Vixens game to be honest
#Magpies much more effective in taking the ball off the Swifts at 16-7 for gains
#Magpies only had 1 more shot attempt than the Swifts --- but misses were 12-4
    #Only 1 of those misses from the Magpies actually resulted in a Swifts rebound
    
# %% Lightning vs. Giants

#Here's where we actually saw a difference in goal attempts
    #Lightning had 77 shots on goal vs. the Giants 51
    #Debatable to say you could ever win a game shooting 26 less shots than your opponent?
#Possession changes --- Giants lost the ball 29 times to Lightning's 16
#Huge penalty disparity
    #65 penalties to the Giants vs. 35 to the Lightning
    
# %% Firebirds vs. Thunderbirds

#Tale of two halves
    #32-16 goal second half for the Thunderbirds
#It seemed to be though from the 2nd quarter onwards that the Firebirds stuggled statistically
    #Centre pass to goal % was OK in Q1 for the Firebirds at 71%
    #Took a nose-dive from that point though all the way down to 38% in the last quarter
#Fun fact stat for this game
    #Shamera Sterling had more NetPoints just by herself in the 2nd half than the whole Firebirds team
    
# %% Penalties to gains - how rare is a player having >= 5 gains and less penalties

#Load in player stats data from ANZC/SSN history
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'])

#Identify when gains were readily recorded
for year in playerStats.keys():
    if playerStats[year]['gain'].sum() > 0:
        print(f'Gains collated in {year}  data')
#Note: gains readily collected from 2010 onwards

#Set-up dictionary to store data in
gainsOverPenalties = {'matchId': [], 'playerId': [], 'squadId': [], 'year': [],
                      'gain': [], 'penalties': []}

#Loop through years
for year in range(2010, 2024):
    #Loop through player entries
    for ii in range(len(playerStats[year])):
        #Check if >= 5 gains
        if playerStats[year].iloc[ii]['gain'] >= 5:
            #Check if less penalties than gains
            if playerStats[year].iloc[ii]['penalties'] <= playerStats[year].iloc[ii]['gain']:
                #Record these data
                gainsOverPenalties['year'].append(year)
                gainsOverPenalties['matchId'].append(playerStats[year].iloc[ii]['matchId'])
                gainsOverPenalties['playerId'].append(playerStats[year].iloc[ii]['playerId'])
                gainsOverPenalties['squadId'].append(playerStats[year].iloc[ii]['squadId'])
                gainsOverPenalties['gain'].append(playerStats[year].iloc[ii]['gain'])
                gainsOverPenalties['penalties'].append(playerStats[year].iloc[ii]['penalties'])

#Convert to dataframe
gainsOverPenalties_df = pd.DataFrame.from_dict(gainsOverPenalties)

#Calculate number of matches this has occurred in
nMatchesGains = len(gainsOverPenalties_df['matchId'].unique())

#Calculate number of total matches over the period
nMatchesTotal = np.array([len(playerStats[year]['matchId'].unique()) for year in range(2010, 2024)]).sum()

#Calculate ratio of this
nGainsOverPenaltiesRatio = nMatchesGains / nMatchesTotal * 100

#Calculate the PG ratio for these
gainsOverPenalties_df['ratio'] = gainsOverPenalties_df['penalties'] / gainsOverPenalties_df['gain']

#Calculate the unique number of players
nUniquePlayers = len(gainsOverPenalties_df['playerId'].unique())

#Group by player Id and count entries
playerCount_df = gainsOverPenalties_df.groupby('playerId').count()

#Looking at players who have got 5 or more gains in a game with equal amount or lessof penalties since 2010 when gains regularly recorded
    #Has been achieved 122 times by 53 unique players
    #Has happened in ~14% of matches
        #So to see it happen in 75% of games over the weekend is a bit of a statistical outlier
    #Who has done it the most?
        #Achieved 10 times by 2 players each: Geva Mentor & Shamera Sterling
        #Just behind them at 9 times is Leana de Bruin --- stretching my player knowledge here
    #Notable performances:
        #5 gains 0 penalties by Jo Harten in 2017
        #7 gains 1 penalty by Renae Ingles in 2019

# %% Match turnarounds

#Read in score-flow data
scoreFlow = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'scoreFlow',
                                        matchOptions = ['regular', 'final'])

#Create dictionary to store data
turnaroundData = {'matchId': [], 'year': [], 'roundNo': [], 'matchType': [],
                  'homeSquadId': [], 'awaySquadId': [], 'winningSquadId': [],
                  'minMargin': [], 'maxMargin': [], 'absDiff': []}

#Loop through years
for year in scoreFlow.keys():
    
    #Loop through unique matchId's
    for matchId in list(scoreFlow[year]['matchId'].unique()):
        
        #Get current match score flow
        currMatchScoreFlow = scoreFlow[year].loc[scoreFlow[year]['matchId'] == matchId,].reset_index(drop = True)
        
        #First check if there is a positive and negative differential
        if currMatchScoreFlow['scoreDifferential'].to_numpy().min() < 0 and \
            currMatchScoreFlow['scoreDifferential'].to_numpy().max() > 0:
                
                #Get the min and max margin, and absolute difference between the two
                minMargin = currMatchScoreFlow['scoreDifferential'].to_numpy().min()
                maxMargin = currMatchScoreFlow['scoreDifferential'].to_numpy().max()
                absDiff = maxMargin - minMargin
                
                #Get the squad Id's
                #Find the first score differential that isn't zero
                indToCheck = np.argmax(currMatchScoreFlow['scoreDifferential'].to_numpy() != 0)
                #Identify home and away squads
                if currMatchScoreFlow['scoreDifferential'].to_numpy()[indToCheck] > 0:
                    homeSquadId = currMatchScoreFlow.iloc[indToCheck]['squadId']
                    awaySquadId = currMatchScoreFlow.iloc[indToCheck]['oppSquadId']
                else:
                    homeSquadId = currMatchScoreFlow.iloc[indToCheck]['oppSquadId']
                    awaySquadId = currMatchScoreFlow.iloc[indToCheck]['squadId']
                    
                #Get winning squad
                if currMatchScoreFlow['scoreDifferential'].to_numpy()[-1] > 0:
                    winningSquadId = homeSquadId.copy()
                elif currMatchScoreFlow['scoreDifferential'].to_numpy()[-1] < 0:
                    winningSquadId = awaySquadId.copy()
                else:
                    winningSquadId = 'draw'
                
                #Store data
                turnaroundData['matchId'].append(matchId)
                turnaroundData['year'].append(year)
                turnaroundData['roundNo'].append(currMatchScoreFlow['roundNo'].unique()[0])
                turnaroundData['matchType'].append(currMatchScoreFlow['matchType'].unique()[0])
                turnaroundData['homeSquadId'].append(homeSquadId)
                turnaroundData['awaySquadId'].append(awaySquadId)
                turnaroundData['winningSquadId'].append(winningSquadId)
                turnaroundData['minMargin'].append(minMargin)
                turnaroundData['maxMargin'].append(maxMargin)
                turnaroundData['absDiff'].append(absDiff)
                
#Convert to dataframe
turnaroundData_df = pd.DataFrame.from_dict(turnaroundData)

#There's many examples of larger turnarounds in the realm of 30-40 goals
    #But these often come from very small leads for 1 team getting blown out to huge wins by the other team
#Some notable bigger turnarounds than what we saw by the Thunderbirds on the weekend
    #The Firebirds were once again up big in a Rd 1 match-up against the Lightning in 2020
        #11 goals up in Q2 yet lost by 18 --- a 29 goal turnaround
    #A Rd 8 match-up in 2020 saw the Magpies up by 11 goals in Q2 against the Giants
        #Giants ended up winning by 15
    #Lastly a Rd 3 match-up in 2021 between the Lightning & Fever
        #Lightning up by 10 goals in Q2 ended up losing by 15
    #Best finals example is still that classic Vixens-Giants prelim from last year
        #Down 10 towards the end of the game to come back and win
        
# %% How common are 100% shooting games

#Set-up dictionary to collate 100% shooting games
shooting100per = {'matchId': [], 'squadId': [], 'year': [], 'playerId': [],
                  'goalAttempts': [], 'goalMisses': []}

#Loop through years to collate
for year in playerStats.keys():
    
    #Loop through player entries
    for ii in range(len(playerStats[year])):
        
        #Check for 100% shooting
        if playerStats[year].iloc[ii]['goalAttempts'] >= 10 and playerStats[year].iloc[ii]['goalMisses'] == 0:
            
            #Record info
            shooting100per['matchId'].append(playerStats[year].iloc[ii]['matchId'])
            shooting100per['year'].append(year)
            shooting100per['playerId'].append(playerStats[year].iloc[ii]['playerId'])
            shooting100per['squadId'].append(playerStats[year].iloc[ii]['squadId'])
            shooting100per['goalAttempts'].append(playerStats[year].iloc[ii]['goalAttempts'])
            shooting100per['goalMisses'].append(playerStats[year].iloc[ii]['goalMisses'])
            
#Convert to dataframe
shooting100per_df = pd.DataFrame.from_dict(shooting100per)

#Get a player count
shooting100per_playerCount = shooting100per_df.groupby('playerId').count()

#Clarifier here is minimum 10 attempts
#Somewhat surprised here that Fowler has done this 8 times
    #Puts her equal 3rd on the list for the number of 100% shooting games
    #She does have 4 of the top 5 records for the number of attempts in 100% games
        #Inc. #1 with 60 from 60 attempts in a rd 12 match last year
#You've also got Lenize Potgeiter nearby with 8 perfect games & Irene van Dyk with 9
#One player streets ahead with 26 perfect games in ANZC/SSN career
    #Cat Tuivaiti

# %% Volume of shots made in final 5 minutes

#Collate number of shots in last 5 minutes of Super Shot era
shotAttemptsPerGameSuper = []
for year in range(2020, 2024):
    
    #Extract number of attempts in last five minutes
    shotAttempts = scoreFlow[year].loc[scoreFlow[year]['periodSeconds'] >= 600, ].count()['matchId']
    
    #Append as shots per game
    shotAttemptsPerGameSuper.append(shotAttempts / len(scoreFlow[year]['matchId'].unique()))
    
#Do the same but for the 2017-2019
shotAttemptsPerGameStandard = []
for year in range(2017, 2020):
    
    #Extract number of attempts in last five minutes
    shotAttempts = scoreFlow[year].loc[scoreFlow[year]['periodSeconds'] >= 600, ].count()['matchId']
    
    #Append as shots per game
    shotAttemptsPerGameStandard.append(shotAttempts / len(scoreFlow[year]['matchId'].unique()))
    
#In the few years prior to the Super Shot matches there were around 44-46 shots per game in the last 5 minutes of Qs
    #So like 11 - 11.5 each quarter in that 5 minute period
#Since the Super Shot we're seeing about 47-48 shots per game in the last 5 minutes
    #So getting close to about 12 in each quarter
#So perhaps a slight increase, but nothing that I think would be really noticeable    
        
# %% Prediction

#Collate margins from the Super Shot era

#Create dictionary to store data
marginData = {'matchId': [], 'year': [], 'finalMargin': []}

#Loop through years
for year in range(2020, 2024):
    
    #Loop through unique matchId's
    for matchId in list(scoreFlow[year]['matchId'].unique()):
        
        #Get current match score flow
        currMatchScoreFlow = scoreFlow[year].loc[scoreFlow[year]['matchId'] == matchId,].reset_index(drop = True)
        
        #Get final absolute margin and append data
        marginData['matchId'].append(matchId)
        marginData['year'].append(year)
        marginData['finalMargin'].append(np.abs(currMatchScoreFlow.iloc[-1]['scoreDifferential']))
        
#Convert to dataframe
marginData_df = pd.DataFrame.from_dict(marginData)
        
# %% ----- End of 01_rd1_analysis.py ----- %% #