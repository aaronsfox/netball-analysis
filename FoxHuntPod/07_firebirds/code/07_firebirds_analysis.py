# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 6 Thunderbirds match-up for
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
#Vixens gain to goal percentage 100% to 60% of Firebirds
#Both teams recorded a number of misses - Vixens 13 and Firebirds 11 for shooting % of 83% and 84%
    #Neither really took advantage of this with only 4 Vixens rebounds to 3 for Firebirds
#Firebirds back racking up the penalties against Vixens at 62 - 47
    #Nowhere near the 91 in round 1 for Firebirds, but still a big contrast to the Vixens
    #Similar sort of physical game with contact penalties to last week - but Vixens looked like they handled it better
#Real first to second half shift in this one
    #Scoring 36-30 for Firebirds in 1st half; 32-24 for Vixens in 2nd half
    #4 gains by Vixens in 1st half up to 7 in 2nd half
    #Firebirds penalties 26 in 1st half vs. 36 in 2nd half
    #Also extended to key players
        #Watson 5 TOs in 1st half down to 2 in 2nd half
        #Wallam 28 goals in first half down to 21 in 2nd half

#Review team stats from year to see how things stack up
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]

#Get Vixens 2022 stats
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]

#Get Firebirds 2022 stats
firebirdsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Firebirds'],]

# %% Vixens mid-court shifts

#Read in line-up data for the year
lineUpData_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'lineUps',
                                              matchOptions = ['regular'])
lineUpData_2022 = lineUpData_2022[2022]

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

#Replace player Id's with names in line-up data
courtPositions = ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']
[lineUpData_2022[courtPos].replace(playerIdDict, inplace = True) for courtPos in courtPositions]

#Filter out Vixens round 8 data
vixensLineUps_round8 = lineUpData_2022.loc[(lineUpData_2022['squadId'] == squadNameDict['Vixens']) &
                                           (lineUpData_2022['roundNo'] == 8), ]

#Focus on +/- for this analysis
#Fairly standard starting line-up but with Olivia Lewis in GK started a bit slow - going -5 for +/-
#Shift with Mundy to WA, Watson to C, Moloney to WD started to peg it back but still didn't eat into margin - going -1 for +/-
    #Line-up was only in for a couple of minutes
#Second half line-up injecting Mannix into GK was where Vixens starte to get on top - going +2 for +/-
#By far the most effective line-up was switching Watson back to WA, Mundy at C, Moloney at WD, Mannix at GK - going +6 for +/-

# %% Vixens back under control to their best?

#Review Vixens team stats compared to other games

#Turnovers
#Turnovers at 17
#Back to 2nd lowest for season - only 15 in round 4 against Fever was lower
#Have brought these back down after being +20 in last two rounds


#Gains
#11 gains for the match
#Continues run of having over 10 gains in wins; less than 10 in losses

# %% Review scoreflow data

#Read in scoreflow data
scoreFlowData_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2022],
                                                 fileStem = 'scoreFlow',
                                                 matchOptions = ['regular'])
scoreFlowData_2022 = scoreFlowData_2022[2022]

#Extract relevant match
vixensFirebirds_scoreFlowData = scoreFlowData_2022.loc[scoreFlowData_2022['matchId'] == 116650801,].reset_index(drop = True)

#Set total match seconds
totalMatchSeconds = 900*4

#Loop through match seconds and identify who's in front at each second

#Create list to store data in
inFront = []

#Loop through match seconds
for timePoint in np.linspace(1, totalMatchSeconds, totalMatchSeconds):
    #Extract match seconds data less than time point
    scorePoint = vixensFirebirds_scoreFlowData.loc[vixensFirebirds_scoreFlowData['matchSeconds'] < timePoint,
                                                   ].reset_index(drop = True)
    #If no data then there then no scoring yet
    if len(scorePoint) == 0:
        inFront.append('tied')
    else:
        #Grab last data point for current margin
        scoreDifferential = scorePoint.iloc[-1]['scoreDifferential']
        #Check for possible options
        if scoreDifferential == 0:
            inFront.append('tied')
        elif scoreDifferential < 0:
            inFront.append('Firebirds')
        else:
            inFront.append('Vixens')
            
#Calculate total proportions in front
propTied = inFront.count('tied') / len(inFront) * 100
propFirebirds = inFront.count('Firebirds') / len(inFront) * 100
propVixens = inFront.count('Vixens') / len(inFront) * 100

#Overall across match:
    #Tied ~13.2% of match time
    #Firebirds in front for ~56.5% of match time
    #Vixens in front for ~30.3% of match time
    
#Extract first three quarters of data
inFront_first3 = inFront[0:900*3]

#Calculate total proportions in front across first 3 quarters
propTied_first3 = inFront_first3.count('tied') / len(inFront_first3) * 100
propFirebirds_first3 = inFront_first3.count('Firebirds') / len(inFront_first3) * 100
propVixens_first3 = inFront_first3.count('Vixens') / len(inFront_first3) * 100

#Across first 3 quarters:
    #Tied ~11.2% of match time
    #Firebirds in front for ~73.8% of match time
    #Vixens in front for ~15.0% of match time
    
#Extract 2nd and 3rd quarters
inFront_middle = inFront[900:2700]

#Calculate total proportions in front across first 3 quarters
propTied_middle = inFront_middle.count('tied') / len(inFront_middle) * 100
propFirebirds_middle = inFront_middle.count('Firebirds') / len(inFront_middle) * 100
propVixens_middle = inFront_middle.count('Vixens') / len(inFront_middle) * 100

#Across second and third quarters:
    #Tied ~6.8% of match time
    #Firebirds in front for ~90.6% of match time
    #Vixens in front for ~2.6% of match time
    
#Extract final quarter
inFront_finalQ = inFront[-901:-1]

#Calculate total proportions in front across final quarter
propTied_finalQ = inFront_finalQ.count('tied') / len(inFront_finalQ) * 100
propFirebirds_finalQ = inFront_finalQ.count('Firebirds') / len(inFront_finalQ) * 100
propVixens_finalQ = inFront_finalQ.count('Vixens') / len(inFront_finalQ) * 100

#Across final quarter:
    #Tied ~19.3% of match time
    #Firebirds in front for ~4.8% of match time
    #Vixens in front for ~75.9% of match time

# %% Bakewell-Doran not as clean?

#Read in player stats for the year
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'])
playerStats_2022 = playerStats_2022[2022]

#Set Bakewell-Doran id
bakewellDoranId = 1016035

#Extract Bakewell-Doran data
bakewellDoran_stats = playerStats_2022.loc[playerStats_2022['playerId'] == bakewellDoranId,]

#Best game for the year gain wise with 6 gains
#13 contact penalties - first time for the year > 10 contact penalties
#16 total penalties - also most for the year and first time > 10

# %% Giants match preview

#Extract Giants team statistics
giantsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['GIANTS'],]

#Looking back to round 3 game the Vixens had their biggest game for gains with 20
#The Giants just had one of their slowest paced and lowest rated attacking game for the year last week

#Look into Giants line-up data
giantsLineUps = lineUpData_2022.loc[lineUpData_2022['squadId'] == squadNameDict['GIANTS'],]



# %% Fan questions

#From https://twitter.com/georgiadoyle258/status/1523223637775437824?s=20&t=X1IpAq-dI0RNDPJn5ih1wg

#100% gain to goal conversion this week - has that ever happened in SSN history

#Read in team stats data from SSN years
teamStats_SSN = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2017, 2018, 2019, 2020, 2021, 2022],
                                            fileStem = 'teamStats',
                                            matchOptions = ['regular','final'])

#Subselect gains and gains from goals
for year in list(teamStats_SSN.keys()):
    #Extract the data
    teamStats_SSN[year] = teamStats_SSN[year][['matchId', 'squadId', 'gain', 'goalsFromGain']]
    #Calculate goal to gain percentage as it isn't in some years
    teamStats_SSN[year]['goalToGainPer'] = teamStats_SSN[year]['goalsFromGain'] / teamStats_SSN[year]['gain']

#Seems to be happening once a year
#For matches where teams have got 10 or more gains:
    #In 2018 Magpies got 10 goals from 10 gains in 103930601 (round 6 game 1) [won]
    #In 2019 Swifts got 11 goals from 11 gains in 107240703 (round 7 game 3) [won]
    #In 2020 Vixens got 13 goals from 13 gains in 111081101 (round 11 game 1) [won]
    #In 2021 Fever got 13 goals from 13 gains in 113910101 (round 1 game 1) [won]
    #In 2022 the Vixens are the only one to do this with 11 goals from 11 gains [won]
#Vixens only team to have achieved this twice over SSN years
#Important to distinguish between goals from gains vs. goals from turnovers
    #There were unforced turnovers from the Firebirds on the weekend that the Vixens didn't score from

#Which team causes the most unforced errors from the Vixens

#Have only recorded unforced turnovers in 2021 and 2022

#Read in team stats data from SSN years again
teamStats_TOs = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2021, 2022],
                                            fileStem = 'teamStats',
                                            matchOptions = ['regular'])

#Set up dictionary for Vixens stats
vixensStats_TOs = {}

#Loop through years
for year in list(teamStats_TOs.keys()):
    
    #Extract Vixens data
    vixensStats_TOs[year] = teamStats_TOs[year].loc[teamStats_TOs[year]['squadId'] == squadNameDict['Vixens'],
                                                  ][['matchId', 'squadId', 'unforcedTurnovers']]
    
    #Loop through match Id's and extract opposition
    oppId = []
    for matchId in vixensStats_TOs[year]['matchId']:
        oppId.append(teamStats_TOs[year].loc[(teamStats_TOs[year]['matchId'] == matchId) &
                                             (teamStats_TOs[year]['squadId'] != squadNameDict['Vixens']),
                                             ]['squadId'].values[0])
    vixensStats_TOs[year]['oppId'] = oppId
    
    #Replace with squad name
    vixensStats_TOs[year]['oppId'].replace(squadDict, inplace = True)

#Only been recording unforced turnovers for 2021 and 2022 seasons
#Hasn't been that much of a consistency across the two years - but perhaps some trends emerging
#In 2021 the top 3 against them were the Magpies with 20, Thunderbirds with 19 and Fever with 18
#So far in 2022 the top 3 against them are the Swifts with 17, Thunderbirds with 16 and Magpies with 15
#The Magpies and Thunderbirds make both top 3 lists so these could be the troublesome teams for unforced turnovers
#In 2022 against the Fever the Vixens only had 8 unforced turnovers vs. 18 and 17 in 2021, so perhaps they've figure them out

# %% Predictions

#Last week predicted > 20 goal quarter

#Review Vixens quarter by quarter team stats from this year
teamPeriodStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2022],
                                                   fileStem = 'teamPeriodStats',
                                                   matchOptions = ['regular'])
teamPeriodStats_2022 = teamPeriodStats_2022[2022]

#Get Vixens 2022 period stats
vixensTeamPeriodStats_2022 = teamPeriodStats_2022.loc[teamPeriodStats_2022['squadId'] == squadNameDict['Vixens'],]
vixensTeamPeriodStats_2022.sort_values(by = 'points', inplace = True)

#The 17 they recorded across the 2nd, 3rd and 4th quarter is their equal highest
#quarter score for the season and this is the only match so far this year where
#they've scored 17+ in at least 3 quarters
    #So didn't quite reach the mark but was still one of the more higher scoring contests for the Vixens


#### TODO: current round prediction...


# %%% ----- End of 07_firebirds_analysis.py -----