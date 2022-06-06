# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to check out statistics relating to panel questions.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\data\\matchCentre\\processed'

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

# %% Collate relevant data

#Bring in team stats from relevant Super Netball regular seasons
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2020, 2021, 2022],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'])

#Bring in player stats from relevant Super Netball regular seasons
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021, 2022],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'])

# %% Statistical differences across recent years

#Collate averages across years
avgTeamStats = []
for year in list(teamStats.keys()):
    #Get and clean data
    currStats = teamStats[year].groupby('squadId').mean().reset_index(drop = False)
    currStats.drop(['matchId', 'oppSquadId'], axis = 1, inplace = True)
    currStats['squadId'].replace(squadDict, inplace = True)
    #Add to list
    avgTeamStats.append(currStats)
    #Export to file
    currStats.to_csv(f'avgTeamStats_{year}.csv', index = False)

#Ability to force turnovers - i.e. gains statistic
    #Middle of the pack ranked #5 in 2021 - but ranked #2 in 2022
#It's moreso been the convert these gains to scoring though
    #In 2020, Vixens were #1 for converting their gains to goals
    #In 2021, Vixens were 2nd last in league for this
    #Now in 2022, Vixens are back at #1 for this statistic
    
#Vixens aren't the highest scoring team in the league - sitting #5 in league with ~62 goals per game
    #This is a big jump from 2021 though where they were bottom of the league with ~51 goals per game
    #Likely reflective of the Watson injury and Philp/Thwaites retirement - big changes at attacking end
    #Vixens had similar ~62 goals per game in 2020
    
#General play turnovers
    #Vixens least in the league with ~19 per game in 2020
    #Vixens had third highest in the league with ~25 per game in 2021
    #Vixens back down to ~18 per game in 2022 - second lowest in the league
    
# %% Statistical categories Vixens players are leading?

#Read in player data to create dictionary
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

#Get player stats for the year
playerStats_2022 = playerStats[2022]

#Get averages
avgPlayerStats_2022 = playerStats_2022.groupby('playerId').mean().reset_index(drop = False)

#Clean up dataset
#Remove unwantd columns
avgPlayerStats_2022.drop(['matchId','oppSquadId'], axis = 1, inplace = True)
#Replace player Ids with names
avgPlayerStats_2022['playerId'].replace(playerIdDict, inplace = True)
#Replace squad Id with names
avgPlayerStats_2022['squadId'].replace(squadDict, inplace = True)

#Export to file
avgPlayerStats_2022.to_csv('avgPlayerStats_2022.csv', index = False)

#Liz Watson having another great season
    #Currently #2 just behind Maddy proud for circle feeds, circle feeds with a shot attempt & goal assists
#Vixens mid-court duo are all over the loose balls
    #Moloney and Watson are #1 and #2 respectively for pick-ups
#Kumwenda sitting #3 behind Fowler and Nelson for average total goals
#Jo Weston sitting #5 in the league for gains

# %% Where should Vixens focus on for finals?

#Collate Vixens team stats from the year
vixensTeamStats_2022 = teamStats[2022].loc[teamStats[2022]['squadId'] == squadNameDict['Vixens'],]

#In their two losses this year - Vixens have recorded < 10 gains
#Recorded 10 or more gains in every remaining game where they've won
#Forcing opposition into turnovers is key to winning it seems

#Fever scoring still have a pattern?
teamStats_2022 = teamStats[2022]

#Grab out team stats and get Fever's scores
feverGoals = teamStats_2022.loc[(teamStats_2022['squadId'] == squadNameDict['Fever']) &
                                (teamStats_2022['matchType'] == 'regular'),
                                ]['points']
avgFeverGoals = np.mean(feverGoals)

#Get average team scores from 2020 and 2021
#2020
teamStats[2020].groupby(['squadId'])['points'].mean().reset_index(
    drop = False).replace(squadDict).sort_values(by = 'points', ascending = False)
#2021
teamStats[2021].groupby(['squadId'])['points'].mean().reset_index(
    drop = False).replace(squadDict).sort_values(by = 'points', ascending = False)

#Extract Fever's and opponents scores from each of these years

#Loop through years
for year in list(teamStats.keys()):
    
    #Set lists to store
    feverScore = []
    oppScore = []
    
    #Extract fever match Id's
    matchIds = list(teamStats[year].loc[teamStats[year]['squadId'] == squadNameDict['Fever'],
                                        ]['matchId'].unique())
    
    #Extract scores from these games
    for matchId in matchIds:
        feverScore.append(teamStats[year].loc[(teamStats[year]['matchId'] == matchId) &
                                              (teamStats[year]['squadId'] == squadNameDict['Fever']),
                                              ]['points'].values[0])
        oppScore.append(teamStats[year].loc[(teamStats[year]['matchId'] == matchId) &
                                            (teamStats[year]['squadId'] != squadNameDict['Fever']),
                                            ]['points'].values[0])
        
    #Set to dataframe
    scoreComp = pd.DataFrame(zip(feverScore, oppScore),
                             columns = ['Fever', 'Opp'])
    
    #Calculate margin
    scoreComp['margin'] = scoreComp['Fever'] - scoreComp['Opp']
    
    #Sort by Fever score
    scoreComp.sort_values(by = 'Fever')
    
#Fever rarely win when scoring under 65-70 goals
#Right around where the Vixens have kept them this year
#Also don't have many close games - so keeping it tight seems to build the pressure
#and they have a much worse winning record in those matches

# %% Any statistical trends relating to wins this year?

#Create a margin variable for this years matches
margin = []
for matchData in enumerate(teamStats_2022['matchId']):
    #Extract details of match
    squadId = teamStats_2022['squadId'][matchData[0]]
    #Get scores
    score = teamStats_2022.loc[(teamStats_2022['matchId'] == matchData[1]) &
                               (teamStats_2022['squadId'] == squadId),
                               ]['points'].to_numpy()[0]
    oppScore = teamStats_2022.loc[(teamStats_2022['matchId'] == matchData[1]) &
                                  (teamStats_2022['squadId'] != squadId),
                                  ]['points'].to_numpy()[0]
    #Calculate and append margin
    margin.append(score - oppScore)
    
#Add to dataframe
teamStats_2022['margin'] = margin

#Create some plots to inspect relationships

#Set variable to inspect
statVar = 'unforcedTurnovers'

#Visualise
plt.scatter(teamStats_2022[statVar], teamStats_2022['margin'])
plt.xlabel(statVar)
plt.ylabel('margin')

#Calculate relationship and display
pCorr = np.corrcoef(teamStats_2022[statVar], teamStats_2022['margin'])
plt.title(f'r = {pCorr[0][1]}')

#Weak to moderate correlation for general play turnovers and gains
    #i.e. less turnovers or more gains equals higher match margin
    
#Look for +X general play turnovers & win rate
#Set turnover number
nTO = 25
#Calculate frequencies
nGamesOver = len(teamStats_2022.loc[teamStats_2022['generalPlayTurnovers'] > nTO,])
nWinsOver = len(teamStats_2022.loc[(teamStats_2022['generalPlayTurnovers'] > nTO) &
                                     (teamStats_2022['margin'] > 0),])
#Calculate proportion
print(f'Win proportion: {nWinsOver/nGamesOver*100}')

#Turnovers pretty big - teams only won 1 in 4 games when having more than 25 general play TOs    

#Look for +X gain & win rate
#Set turnover number
nGain = 15
#Calculate frequencies
nGamesOver = len(teamStats_2022.loc[teamStats_2022['gain'] > nGain,])
nWinsOver = len(teamStats_2022.loc[(teamStats_2022['gain'] > nGain) &
                                     (teamStats_2022['margin'] > 0),])
#Calculate proportion
print(f'Win proportion: {nWinsOver/nGamesOver*100}')

#Conversely if you record over 15 gains (i.e. forced TOs) you win 75% of games this year

# %% ----- End of vixensBrunch.py -----