# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 10 & 11 Fever & Swifts match-up
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

# %% Fever match-up: Key numbers that jumped out

#Deflections:
    #Fever led this stat 19-12
    #Deflections with gain though was Vixens 6-1 Fever
    #Vixens with gains from 50% of deflections vs. Fever's ~5%
#Gain to goal percentage
    #Fever actuall converted 100% of gains to goals, but only had 7 gains
    #Vixens had 13 gains and converted 12 of these to goals - one off that +10 gains & 100% mark we've spoken about
#Vixens 6 gains in the first quarter - almost as many as the Fever had for the game
#25 to 13 shot attempts in first quarter to the Vixens

# %% Vixens beating Fever in first few minutes

#Read in the scoreflow data from the year
scoreFlow_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'scoreFlow',
                                             matchOptions = ['regular'])
scoreFlow_2022 = scoreFlow_2022[2022]

#Extract the current game
matchId = 116651002
scoreFlow_vixensFever = scoreFlow_2022.loc[scoreFlow_2022['matchId'] == matchId,
                                           ].reset_index(drop = True)

#Vixens got up 8-1 in the first four minutes
#Subtract this differential from the margin from this point
correctedMargin = scoreFlow_vixensFever['scoreDifferential'] + 7

#Take out these first four minutes and reset from there
#The game see-sawed a bit and the Vixens pushed out another 5 goal lead
#But from that point on it was an even game and Fever were on top just as much 
#as the Vixens - and would've come out on top

# %% Fowler's slow start

#Set Fowler Id
fowlerId = 80826

#Extract Fowler's shots from scoreflow data
fowlerShots_vixensMatchUp = scoreFlow_vixensFever.loc[scoreFlow_vixensFever['playerId'] == fowlerId,]

#First shot
fowlerShots_vixensMatchUp.reset_index()['matchSeconds'][0]

#Fowler's first shot in this match was 242 seconds in - i.e. 4 mins

#Has this ever happened before with Westo Coast Fever (since 2018)?

#Read in scoreflow data across those years
scoreFlowData = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2018, 2019, 2020, 2021, 2022],
                                            fileStem = 'scoreFlow',
                                            matchOptions = ['regular', 'final'])

#Set up dictionary to store data in
fowlerShotData = {'year': [],
                  'matchId': [],
                  'oppSquadId': [],
                  'matchSeconds': []}

#Loop through years
for year in list(scoreFlowData.keys()):
    
    #Extract Fowler's data from the year
    scoreFlow_Fowler = scoreFlowData[year].loc[scoreFlowData[year]['playerId'] == fowlerId,]
    
    #Get the match Id's
    fowlerMatches = scoreFlow_Fowler['matchId'].unique()
    
    #Loop through match Id's and extract first shot attempt time
    for matchId in fowlerMatches:
        #Get data
        currFowlerData = scoreFlow_Fowler.loc[scoreFlow_Fowler['matchId'] == matchId,
                                              ].reset_index(drop = True)
        #Extract and append the data
        fowlerShotData['year'].append(year)
        fowlerShotData['matchId'].append(matchId)
        fowlerShotData['oppSquadId'].append(currFowlerData['oppSquadId'][0])
        fowlerShotData['matchSeconds'].append(currFowlerData['matchSeconds'][0])

#Convert to dataframe
fowlerShotData_df = pd.DataFrame.from_dict(fowlerShotData)

#The 242 seconds is the 2nd longest time it's taken for Fowler to take a shot
#It's only taken longer in one match from 2019:
    #Round 8 against the Adelaide Thunderbirds where it took 333 seconds - i.e. 5 & a half minutes
    #Similar circumstances, where Kaylia Stanton shot the first goal a minute in
    #But then the Fever went down 7-1 before Fowler got her first shot up
    
# %% Olivia Lewis' match

#Reviewed player stats
    #3 gains in the first quarter setting up the match
    #5 total deflections across the game
    #Only 2 penalties each quarter, for a total of 8
        #With her 4 gains this match gave her that elite penalties to gain ratio of 2

# %% Swifts match-up: Key numbers that jumped out

#Vixens outgained Swifts 10-8
    #Gain to goal percentage of 90, so once again only one goal of that +10 & 100% gain to goal
#Vixens had more misses to go with their more attempts
    #But offensive rebounds 6-0, and missed shot conversion at 67% to Swifts at 0%
#Vixens 8 turnovers in the first quarter, but then only 10 for the remaining 3 quarters
    #Related to the Swifts 5 gains in the first quarter, but then only 1 in each of the remaining quarters
#2nd quarter turn-around
    #Go into quarter time break down 17-12
    #Come out and half their turnovers, only record 8 total penalties in 2nd quarter
    #Outscore Swifts 16-11
    #Match back level again at half-time
    
# %% Vixens line-up changes

#Reviewed line-up data spreadsheet
    #Starting line-up went down 4-8 in first 6 minutes
        #If this line-up kept this scoring rate for 60 minutes - would have lost by ~40
        #MJ	Austin	Mundy	Watson	Moloney	Weston	Lewis
    #Switch to Mannix in at GK for rest of first quarter
        #Only went down an extra goal
        #Extrapolated to 60 mins of match time still would have been a 6 goal deficit
    #Shift in the mid-court from 2nd quarter onwards
        #MJ	Austin	Watson	Moloney	Eddy	Weston	Mannix
        #Where they took over and a per 60 +/- 0f +11
        
# %% Proud stats from 1st quarter to later in match

#Review player stats period spreadsheet
    #In Q1 Proud had 12 feeds and 8 of those resulted in a shot attempt
        #In Q2 this dropped to 4 feeds total (all with an attempt) - cut in half
        #Only had 5 feeds with an attempt in the 3rd and 4th quarter too
    #In Q1 Proud had zero turnovers
        #In Q2 and Q3 she had 2 turnovers in each
    #n Q1 Proud had 47 NetPoints
        #In Q2 and Q3 she had only 7 & 6.5, respectively

# %% Lightning match preview

#Get Lightning team stats
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]
lightningTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Lightning'],]

#Get average team stats
avgTeamStats_2022 = teamStats_2022.groupby('squadId').mean().reset_index(drop = False)
avgTeamStats_2022['squadId'].replace(squadDict, inplace = True)

#Get variation in team stats
sdTeamStats_2022 = teamStats_2022.groupby('squadId').std().reset_index(drop = False)
sdTeamStats_2022['squadId'].replace(squadDict, inplace = True)

#Lightning's up and down season had me looking at variation in stats, rather than averages
    #Lightning have the second highest variation in their scoring
        #Looking at standard deviation around their average score it sits at +/- 10 goals
#Second highest average pace behind the Firebirds at #1 & just ahead of Fever
    #Playing at a high pace is not the Vixens thing - and they've been good at slowing other teams down
#Lightning have the lowest average gains of any team in the competition
    #Not great at forcing teams into turnovers
    #Vixens have been up and down with unforced turnovers
    #If they don't turn the ball over with their own errors - should be a low turnover game

# %% Fan questions

#What constitutes a turnover?
#https://twitter.com/MoggazM/status/1527801310065881088?s=20&t=jEPgNd82DUzKemuF4gHcQw

#Review Champion Data sheet:
    #General play turnover
        #Includes things like bad drops & bad passes, intercepts thrown, or turnovers via a deflection
        #Penalties like held ball, offside, breaks, over a third
        #Penalty while in possession
    #Question also talked about quad series - it might depend on who collates the stats 
        #e.g. Champion does SSN, they may do some internationals
        
#Is this the closest season in recent history?
#https://twitter.com/roystonpkroyal/status/1527165481727033344?s=20&t=jEPgNd82DUzKemuF4gHcQw

#Mathematically I think every team from top to bottom can still make finals with 3 rounds to go

#Read in team stats data from Super Netball era
teamStats_SuperNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2017, 2018, 2019, 2020, 2021, 2022],
                                                     fileStem = 'teamStats',
                                                     matchOptions = ['regular'])

#Loop through years and calculate wins through round 11
for year in list(teamStats_SuperNetball.keys()):
    
    #Create dictionary with each team and wins set at zero
    squad = []
    wins = []
    
    #Loop through squad Id's
    for squadId in list(squadDict.keys()):
        
        #Extract teams data from the current year through round 11
        currTeamData = teamStats_SuperNetball[year].loc[(teamStats_SuperNetball[year]['squadId'] == squadId) |
                                                        (teamStats_SuperNetball[year]['oppSquadId'] == squadId),]
        currTeamRoundData = currTeamData.loc[currTeamData['roundNo'] <= 11,]
        
        #Get match Id's
        teamMatchIds = currTeamRoundData['matchId'].unique()
        
        #Set win counter
        winCounter = 0
        
        #Loop through match Id's
        for matchId in teamMatchIds:
            
            #Get team score and opposition score
            if year < 2020:
                teamScore = currTeamRoundData.loc[(currTeamRoundData['matchId'] == matchId) &
                                                  (currTeamRoundData['squadId'] == squadId),
                                                  ]['goals'].values[0]
                oppScore = currTeamRoundData.loc[(currTeamRoundData['matchId'] == matchId) &
                                                 (currTeamRoundData['squadId'] != squadId),
                                                 ]['goals'].values[0]
            else:
                teamScore = currTeamRoundData.loc[(currTeamRoundData['matchId'] == matchId) &
                                                  (currTeamRoundData['squadId'] == squadId),
                                                  ]['points'].values[0]
                oppScore = currTeamRoundData.loc[(currTeamRoundData['matchId'] == matchId) &
                                                 (currTeamRoundData['squadId'] != squadId),
                                                 ]['points'].values[0]
                    
            
            #Check for win
            if teamScore > oppScore:
                winCounter += 1
                
        #Append squadId and win counter to list
        squad.append(squadId)
        wins.append(winCounter)
        
    #Convert to dataframe
    yearWins = pd.DataFrame(list(zip(squad, wins)),
                            columns = ['squadId', 'wins'])
    
    #Display results
    print(f'Wins at Rd. 11 for {year}')
    yearWins.sort_values(by = 'wins', ascending = False, inplace = True)
    yearWins['squadId'].replace(squadDict, inplace = True)
    yearWins.set_index('squadId', inplace = True)
    print(yearWins)
                
            

# %% Predictions

#Last week:
    #Just snuck in with Fever scoring 64 in range of 60-65
    #Swifts recorded 19 turnovers - which ws under the +20
    
#Get Vixens team stats
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]

#Lightning prediction
    #The Lightning have the highest per game average for shot misses
    #The Vixens have had 1 game with 11 rebounds and a couple with 10 rebounds
    #Predicting this match-up to be their highest rebounding match for the season so far

# %%% ----- End of 09_fever-swifts_analysis.py -----