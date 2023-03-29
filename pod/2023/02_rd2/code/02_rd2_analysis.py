# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 2 SSN match-ups.
    
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

# %% Firebirds vs. Lightning

#Gain & turnover efficiency
    #Lacking by Firebirds - good by Lightning
    #Defensively Firebirds perhaps had a better game - more gains, same amount of general turnovers
        #Outdone by Lightning in converting these
            #Lightning 20 goals from turnovers and gains; Firebirds only 11
    #20 goal misses to 3 for Firebirds vs. Lightning

# %% Thunderbirds vs. Swifts

#Game was incredibly even statistically overall by half time
    #Lets talk more about this in detail shortly though...    

# %% Giants vs. Fever

#Standard vs. Super Shots
    #This game was 64-43 in Fever's favour just on standard shots
    #But 30-10 in Giants favour on Super Shots
#On nearly all areas, Fever dominated the game
    #Overall stat of NetPoints was 500 - ~344
        #3 x bigger disparity in this than any other game --- yet one of the closest on the scoreboard


# %% Magpies vs. Vixens

#Circle and shot positioning might be an interesting one to go back and rewatch
    #Vixens 86 total circle feeds, but only 59 of these had attempts
    #Magpies 68 total circle feeds, with 57 feeds having an attempt
        #Much better ratio there for Magpies
#Vixens with 11 gains
    #+10 on this category = win
#Vixens led centre pass receives 52-50

# %% Double the fun - where was Thunderbirds vs. Swifts headed...

#review team stats sheet

#Less about doubling the stats in this one as it would probably mask what was happening
#Trajectory of the match shifting towards Thunderbirds & away from Swifts in Q2
    #Scoring 
        #Swifts 16 in Q1 to 9 in Q2 for Swifts
    #Penalties went from 9 in Q1 up to 22 in Q2 for Swifts
    #Centre pass conversion was consistent around 60-70% for Thunderbirds
        #Dropped from 77% for Swifts in Q1 to 27% in Q2
    #Feeds
        #Thunderbirds up 15 to 19 from Q1-Q2
        #Swifts down 25 to 15 from Q1-Q2
    #General play turnovers
        #Thunderbirds 8 to 6 from Q1-Q2
        #Swifts 4 to 8 from Q1-A2

# %% Lightning's perfect half

#Read in team period stats
teamPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = 'all',
                                              fileStem = 'teamPeriodStats',
                                              matchOptions = ['regular', 'final'])

#Create dictionary to store shooting data across halves
shootingHalves = {'matchId': [], 'year': [], 'roundNo': [], 'squadId': [], 'halve': [],
                  'nAttempts': [], 'nMisses':[], 'shootingPlayerIds': []}

#Loop through years of data
for year in teamPeriodStats.keys():
    
    #Identify the match Id's from the year
    matchIds = list(teamPeriodStats[year]['matchId'].unique())
    
    #Loop through mathes
    for matchId in matchIds:
        
        #Extract current match data
        #Team period stats
        currMatchTeamPeriodStats = teamPeriodStats[year].loc[teamPeriodStats[year]['matchId'] == matchId, ].reset_index(drop = True)
        #Score flow
        currMatchScoreFlow = scoreFlow[year].loc[scoreFlow[year]['matchId'] == matchId, ].reset_index(drop = True)
        
        #Extract the squad Ids
        squads = list(currMatchTeamPeriodStats['squadId'].unique())
        
        #Extract relevant data across the match form both squads
        for squadId in squads:
        
            #First half
            shootingHalves['matchId'].append(matchId)
            shootingHalves['year'].append(year)
            shootingHalves['roundNo'].append(currMatchScoreFlow['roundNo'].unique()[0])
            shootingHalves['halve'].append('first')
            shootingHalves['squadId'].append(squadId)
            shootingHalves['nAttempts'].append(currMatchTeamPeriodStats.loc[(currMatchTeamPeriodStats['squadId'] == squadId) &
                                                                            (currMatchTeamPeriodStats['period'] <= 2),
                                                                            ]['goalAttempts'].sum())
            shootingHalves['nMisses'].append(currMatchTeamPeriodStats.loc[(currMatchTeamPeriodStats['squadId'] == squadId) &
                                                                          (currMatchTeamPeriodStats['period'] <= 2),
                                                                          ]['goalMisses'].sum())
            shootingHalves['shootingPlayerIds'].append(list(currMatchScoreFlow.loc[(currMatchScoreFlow['squadId'] == squadId) &
                                                                                   (currMatchScoreFlow['period'] <= 2),
                                                                                   ]['playerId'].unique()))
            
            #Second half
            shootingHalves['matchId'].append(matchId)
            shootingHalves['year'].append(year)
            shootingHalves['roundNo'].append(currMatchScoreFlow['roundNo'].unique()[0])
            shootingHalves['halve'].append('second')
            shootingHalves['squadId'].append(squadId)
            shootingHalves['nAttempts'].append(currMatchTeamPeriodStats.loc[(currMatchTeamPeriodStats['squadId'] == squadId) &
                                                                            (currMatchTeamPeriodStats['period'] >= 3),
                                                                            ]['goalAttempts'].sum())
            shootingHalves['nMisses'].append(currMatchTeamPeriodStats.loc[(currMatchTeamPeriodStats['squadId'] == squadId) &
                                                                          (currMatchTeamPeriodStats['period'] >= 3),
                                                                          ]['goalMisses'].sum())
            shootingHalves['shootingPlayerIds'].append(list(currMatchScoreFlow.loc[(currMatchScoreFlow['squadId'] == squadId) &
                                                                                   (currMatchScoreFlow['period'] >= 3),
                                                                                   ]['playerId'].unique()))
            
#Convert to dataframe
shootingHalves_data = pd.DataFrame.from_dict(shootingHalves)

#Add a shooting percentage column
shootingHalves_data['shootingPer'] = (shootingHalves_data['nAttempts'] - shootingHalves_data['nMisses']) / shootingHalves_data['nAttempts'] * 100

#Convert the player Id's to names
shootingPlayerNames = []
for ii in shootingHalves_data.index:
    shootingPlayerNames.append([playerData.loc[playerData['playerId'] == playerId, ]['fullName'].values[0] for playerId in shootingHalves_data.iloc[ii]['shootingPlayerIds']])
shootingHalves_data['shootingPlayerNames'] = shootingPlayerNames

#Get a count of the number of shooters
shootingHalves_data['nShooters'] = [len(shootingHalves_data['shootingPlayerNames'][ii]) for ii in shootingHalves_data.index]

#How often do 100% halves happen?
nPerfectHalves = len(shootingHalves_data.loc[shootingHalves_data['shootingPer'] == 100])
nPerfectHalvesPer = nPerfectHalves / len(shootingHalves_data) * 100

#Happened 35 times which equates to 0.95% of halves (just under 1 in 100 halves)
#Only 6 of those 35 times have happened with 3 shooters taking a shot
#3rd time Lightning has shot a perfect halve - Steph Wood has been on court for them every time
#The 39 attempts taken by the Lightning in the first half is the most attempts a teams had for a perfect half

# %% Perfect GK quarters

#Read in line-up data
lineUp = collatestats.getSeasonStats(baseDir = baseDir,
                                     years = 'all',
                                     fileStem = 'lineUps',
                                     matchOptions = ['regular', 'final'])

#Read in player quarter stat data
playerPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                                years = 'all',
                                                fileStem = 'playerPeriodStats',
                                                matchOptions = ['regular', 'final'])

#Read in score flow data
scoreFlow = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'scoreFlow',
                                        matchOptions = ['regular', 'final'])

#Set period seconds cut-offs
periodSeconds = {1: [0,900], 2: [901,1800], 3: [1801,2700], 4: [2701,3700]} # 100 second buffer on last quarter to get all

#Set-up dictionary to collate data
perfectGK = {'matchId': [], 'year': [], 'roundNo': [], 'squadId': [],
             'period': [], 'playerId': [], 'nPenalties': []}

#Loop through years of data
for year in lineUp.keys():
    
    #Identify the match Id's from the year
    matchIds = list(lineUp[year]['matchId'].unique())
    
    #Loop through mathes
    for matchId in matchIds:
        
        #Extract current match data
        #Line-ups
        currMatchLineUp = lineUp[year].loc[lineUp[year]['matchId'] == matchId, ].reset_index(drop = True)
        #Player period stats
        currMatchPlayerPeriodStats = playerPeriodStats[year].loc[playerPeriodStats[year]['matchId'] == matchId, ].reset_index(drop = True)
        
        #Extract the two squads
        squads = list(currMatchLineUp['squadId'].unique())
        
        #Loop through squads
        for squadId in squads:
            
            #Extract current squads line-up data
            currSquadLineUp = currMatchLineUp.loc[currMatchLineUp['squadId'] == squadId, ].reset_index(drop = True)
            
            #Loop through the substition points at quarters and apply a column for each quarter
            for period in periodSeconds.keys():
                #Loop through entries and check within boundaries
                inQ = []
                for ii in currSquadLineUp.index:
                    #Space out seconds of line-up linearly
                    secondBySecond = np.linspace(currSquadLineUp.iloc[ii]['startingTime'], currSquadLineUp.iloc[ii]['finishTime'],
                                                 int(currSquadLineUp.iloc[ii]['finishTime'] - currSquadLineUp.iloc[ii]['startingTime']) + 1)
                    #Check if any fall within bracket
                    if ((secondBySecond >= periodSeconds[period][0]) & (secondBySecond <= periodSeconds[period][1])).any():
                        inQ.append(True)
                    else:
                        inQ.append(False)
                currSquadLineUp[f'inPeriod{period}'] = inQ   
            
            #Loop through the quarters to check if one GK played
            for period in periodSeconds.keys():
                
                #Identify line-ups from the current quarter
                currSquadPeriodLineUp = currSquadLineUp.loc[currSquadLineUp[f'inPeriod{period}'],]
                    
                #Check if one player was listed at GK
                if len(currSquadPeriodLineUp['GK'].unique()) == 1:
                    try: #need this to catch exception with incomplete game
                        #Extract this players penalties from the current period
                        nPenalties = playerPeriodStats[year].loc[(playerPeriodStats[year]['matchId'] == matchId) &
                                                                 (playerPeriodStats[year]['playerId'] == currSquadPeriodLineUp['GK'].unique()[0]) &
                                                                 (playerPeriodStats[year]['period'] == period),
                                                                 ]['penalties'].values[0]
                        #Check and collect data if zero penalties
                        if nPenalties == 0:
                            perfectGK['matchId'].append(matchId)
                            perfectGK['year'].append(year)
                            perfectGK['roundNo'].append(currSquadPeriodLineUp['roundNo'].unique()[0])
                            perfectGK['squadId'].append(squadId)
                            perfectGK['period'].append(period)
                            perfectGK['playerId'].append(currSquadPeriodLineUp['GK'].unique()[0])
                            perfectGK['nPenalties'].append(nPenalties)
                    except:
                        print('Found incomplete game with line-up errors...')
                    
#Convert to dataframe
perfectGK_data = pd.DataFrame.from_dict(perfectGK)

#Add in player names for readability
perfectGK_data['playerName'] = [playerData.loc[playerData['playerId'] == playerId, ]['fullName'].values[0] for playerId in perfectGK_data['playerId']]
                    
#Group players and get a count
groupedCount_perfectGK_data = perfectGK_data.groupby('playerName').count()

#Looked for players who spent the entire quarter at GK and received zero penalties
    #First time RBD has done it - perhaps more due to not playing GK that often
#Most prominent players who have achieved this (top 3):
    #Geva Mentor with 26 perfect quarters
    #Jane Watson with 20 perfect quarters
    #Sam Poolman with 19 perfect quarters

# %% Shooting streaks

#Create dictionary to store data in
shootingStreakHistory = {'playerId': [], 'year': [], 'maxStreak': []}

#Loop through years and identify max shooting streaks within each
for year in scoreFlow.keys():
    
    #Identify the unique list of shooters from the year
    shootingPlayers = list(scoreFlow[year]['playerId'].unique())
    
    # #Create a dictionary to store max streaks in
    # shootingStreaks = {playerId: np.zeros(1) for playerId in shootingPlayers}
    
    #Loop through players and calculate maximum shooting streak within year
    for playerId in shootingPlayers:
        
        #Extract their scoring data
        playerScoring = scoreFlow[year].loc[scoreFlow[year]['playerId'] == playerId, ].reset_index(drop = True)
                
        #Convert the scoring points to boolean (i.e. anything > 0 = True)
        playerScoring['scoreBool'] = [True if scorePoints > 0 else False for scorePoints in playerScoring['scorePoints']]
        
        #Calculaate players current max streak
        maxStreak = (~playerScoring['scoreBool']).cumsum()[playerScoring['scoreBool']].value_counts().max()
        
        #Append details to dictionary
        shootingStreakHistory['playerId'].append(playerId)
        shootingStreakHistory['year'].append(year)
        shootingStreakHistory['maxStreak'].append(maxStreak)
    
#Convert to dataframe
shootingStreakHistory_data = pd.DataFrame.from_dict(shootingStreakHistory)

#Add player names for easier reading
shootingStreakHistory_data['playerName'] = [playerData.loc[playerData['playerId'] == playerId, ]['fullName'].values[0] for playerId in shootingStreakHistory_data['playerId']]

#Longest streak within a year does belong to Cat Tuivaiti - 139 in 2012
    #She also has the 3rd highest with a 121 goal streak
#Fowler has 114 so far this year, but has also had 105 in 2022 and 122 in 2021
    #Means she  has the 2nd, 4th and 6th highest streaks
        #Needs another 9 to break her best efforts
        #Needs another 26 to have the longest shooting streak within a season in history
#Next closest so far this year is Shimona Nelson with 79
    
# %% Centre pass receive and 2nd phase data

#Take a look at 2022 data for player stats first
#2nd phase only started being collected in 2022

#Read in regular season player stats
playerStats2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerStats',
                                              matchOptions = ['regular'])
playerStats2022 = playerStats2022[2022]

#Group by player Id and sum CPR and SPR
groupedPlayerStats2022 = playerStats2022.groupby('playerId').sum()
centrePassData2022 = groupedPlayerStats2022[['centrePassReceives', 'secondPhaseReceive']].reset_index(drop = False)

#Add in player name
centrePassData2022['playerName'] = [playerData.loc[playerData['playerId'] == playerId, ]['fullName'].values[0] for playerId in centrePassData2022['playerId']]
        
#Proud ranked #11 and Housby #13 for CPRs in 2022
#Proud ranked #8 for 2nd phase and Hadley #14, Housby #17
#Not outstanding numbers but perhaps a balance of options across the court in that space

#What about 2023

#Read in regular season player stats
playerStats2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2023],
                                              fileStem = 'playerStats',
                                              matchOptions = ['regular'])
playerStats2022 = playerStats2023[2023]

#Group by player Id and sum CPR and SPR
groupedPlayerStats2023 = playerStats2022.groupby('playerId').sum()
centrePassData2023 = groupedPlayerStats2023[['centrePassReceives', 'secondPhaseReceive']].reset_index(drop = False)

#Add in player name
centrePassData2023['playerName'] = [playerData.loc[playerData['playerId'] == playerId, ]['fullName'].values[0] for playerId in centrePassData2023['playerId']]
        
#Swifts players are a little further down the list this year
    #Housby leading centre pass receives for them at the moment
        #A different strategy than what they seemed to have last year
#2nd phase receives is perhaps becoming more of a shooters role this year
    #In 2022 the top 3 were Price, Simmons & Tippett
    #So far this year it's Garbin, Koenen & Glasgow in the top 3
        #Koenen interesting - about 2.5x more 2nd phase than the next typical GS in Kumwenda
        
# %% Question

#Is there a correlation between teams sticking with their starting 7 and winning games
#This perhaps happened more regularly before rolling substitutions, so look at this
#from 2020 onwards

#Read in line-up data
lineUp2020 = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2020, 2021, 2022, 2023],
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular', 'final'])

#Read in score flow data
scoreFlow2020 = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2020, 2021, 2022, 2023],
                                            fileStem = 'scoreFlow',
                                            matchOptions = ['regular', 'final'])

#Set dictionary to store data
lineUpChanges= {'matchId': [], 'year': [], 
                'squad1': [], 'squad1_changes': [], 'squad1_score': [],
                'squad2': [], 'squad2_changes': [], 'squad2_score': []}

#Loop through years
for year in lineUp2020.keys():
    
    #Identify the match Id's from the year
    matchIds = list(lineUp2020[year]['matchId'].unique())
    
    #Loop through mathes
    for matchId in matchIds:
        
        #Extract current match data
        currMatchLineUp = lineUp2020[year].loc[lineUp2020[year]['matchId'] == matchId, ].reset_index(drop = True)
        
        #Identify squads
        squads = list(currMatchLineUp['squadId'].unique())
        
        #Extract data
        lineUpChanges['matchId'].append(matchId)
        lineUpChanges['year'].append(year)
        lineUpChanges['squad1'].append(squads[0])
        lineUpChanges['squad1_changes'].append(len(currMatchLineUp.loc[currMatchLineUp['squadId'] == squads[0],]) - 1)
        lineUpChanges['squad1_score'].append(scoreFlow[year].loc[(scoreFlow[year]['matchId'] == matchId) &
                                                                 (scoreFlow[year]['squadId'] == squads[0]),
                                                                 ]['scorePoints'].sum())
        lineUpChanges['squad2'].append(squads[0])
        lineUpChanges['squad2_changes'].append(len(currMatchLineUp.loc[currMatchLineUp['squadId'] == squads[1],]) - 1)
        lineUpChanges['squad2_score'].append(scoreFlow[year].loc[(scoreFlow[year]['matchId'] == matchId) &
                                                                 (scoreFlow[year]['squadId'] == squads[1]),
                                                                 ]['scorePoints'].sum())
        
#Convert to dataframe
lineUpChanges_data = pd.DataFrame.from_dict(lineUpChanges)
        
#Check to see if there are any games with both teams using no changes
lineUpChanges_data.loc[(lineUpChanges_data['squad1_changes'] == 0) &
                       (lineUpChanges_data['squad2_changes'] == 0)]

#No games where both teams have kept starting seven

#Check how often these were won
noSquadChangesGames = lineUpChanges_data.loc[(lineUpChanges_data['squad1_changes'] == 0) |
                                             (lineUpChanges_data['squad2_changes'] == 0)
                                             ].reset_index(drop = True)

#Loop through these games and see who won
winCounter = 0
for ii in noSquadChangesGames.index:
    if noSquadChangesGames.iloc[ii]['squad1_changes'] == 0:
        if noSquadChangesGames.iloc[ii]['squad1_score'] - noSquadChangesGames.iloc[ii]['squad2_score'] > 0:
            winCounter += 1
    else:
        if noSquadChangesGames.iloc[ii]['squad2_score'] - noSquadChangesGames.iloc[ii]['squad1_score'] > 0:
            winCounter += 1
            
#Calculate ratio
noSquadWinRatio = winCounter / len(noSquadChangesGames) * 100

#Out of 24 games since 2020 where teams haven't changed their line-up, they've won 75% of games

#Check what the ratio of wins are when making less substitutions
winCounterSubs = 0
gameCounter = 0
for ii in lineUpChanges_data.index:
    if lineUpChanges_data.iloc[ii]['squad1_changes'] < lineUpChanges_data.iloc[ii]['squad2_changes']:
        if lineUpChanges_data.iloc[ii]['squad1_score'] - lineUpChanges_data.iloc[ii]['squad2_score'] > 0:
            winCounterSubs += 1
    elif lineUpChanges_data.iloc[ii]['squad2_changes'] < lineUpChanges_data.iloc[ii]['squad1_changes']:
        if lineUpChanges_data.iloc[ii]['squad2_score'] - lineUpChanges_data.iloc[ii]['squad1_score'] > 0:
            winCounterSubs += 1
    gameCounter += 1
    
#Calculate ratio
lessSquadWinRatio = winCounterSubs / gameCounter * 100
        
#Teams who make less line-up changes than opponent win 63% of games
        
        
        

# %% Prediction

#Fowler went 58/61 and 61/63 against Magpies last year
#Fowler went 59/60 and 62/66 against Magpies in 2021
    #Despite not having a perfect game against the Magpies recently, will have
    #another and given this hit the longest streak in Super Netball


# %% ----- End of 02_rd2_analysis.py ----- %% #