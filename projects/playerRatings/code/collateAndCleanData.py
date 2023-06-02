# -*- coding: utf-8 -*-
"""

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This script collates the notational data from the SSN 2018 season and aligns
    some of the parameters of the coded data with that from the Champion Data 
    match centre.


"""

# %% Import packages

import pandas as pd
import os
import numpy as np
from difflib import SequenceMatcher

# %% Set-up

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

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

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

#Create a dictionary that links up notational analysis file names to squads
#Note the removal of spaces here for ease of use
dataSquadDict = {'MelbourneVixens': 804,
                 'NSWSwifts': 806,
                 'QueenslandFirebirds': 807,
                 'SunshineCoastLightning': 8117,
                 'WestCoastFever': 810,
                 'MagpiesNetball': 8119,
                 'AdelaideThunderbirds': 801,
                 'GiantsNetball': 8118}

#Read in relevant match centre game data for the 2018 season

#Team stats
teamStats2018 = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2018],
                                            fileStem = 'teamStats',
                                            matchOptions = ['regular','final'])
teamStats2018 = teamStats2018[2018]

#Player lists
playerLists2018 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2018],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular','final'])
playerLists2018 = playerLists2018[2018]

# %% Clean up notational data

#Identify the file available from notational data
rawDataFiles = os.listdir('..\\data\\raw\\')

# #Do an initial run through of data files to identify all events in the dataset
# eventList = []
# for dataFile in rawDataFiles:
    
#     #Read in data (drop event nan's)
#     tempData = pd.read_csv(f'..\\data\\raw\\{dataFile}')
#     tempData = tempData[tempData['Event'].notna()].reset_index(drop = True)
    
#     #Append unique events to list
#     eventList = eventList + list(tempData['Event'].unique())
    
# #Identify unique elements
# uniqueEventList = list(pd.Series(eventList).unique())

#From running the above quick code we can create a dictionary of events to keep and label
#Note that this condenses some event categories by using the same label
eventsDict = {'Centre Pass' : 'centrePass',
              'Assist - Centre Pass Rec': 'centrePassReceive',
              'Assist - 2nd Phase': 'secondPhaseReceive',
              'Possession': 'possession',
              'Penaly - Contact': 'penalty_contact',
              'Assist - Circle Entry': 'feed',
              'Goal - Score': 'goalMake',
              'Loss - Drop': 'loss_drop',
              'Gain - Pick-up': 'gain_pickUp',
              'Deflect': 'deflection',
              'Throw In': 'throwIn',
              'Loss - Stopped Lead': 'loss_stoppedLead',
              'Gain - Inter': 'gain_intercept',
              'Loss - Step': 'loss_footwork',
              'Penaly - Obstruction': 'penalty_obstruction',
              'Gain - Tip (Deflect)': 'gain_deflection',
              'Loss - Bad Pass': 'loss_badPass',
              'Loss - Out of Court': 'loss_outOfCourt',
              'Loss - Offside': 'loss_offside',
              'Loss - Held Ball': 'loss_heldBall',
              'Goal - Miss': 'goalMiss',
              'Assist - Attack Rebound': 'attackingRebound',
              'Gain - Def Reb': 'gain_defensiveRebound',
              'Penaly - Other': 'penalty_other',
              'Loss - Break': 'loss_break',
              'Penaly - Contact on CP': 'penalty_contactOnCP',
              'Loss - Replay': 'loss_replay',
              'Loss - Off Contact': 'penalty_offContact',
              'Gain - Opposition Error': 'unforcedTurnover',
              'Gain - Opp Cont': 'penalty_offContact',
              'Loss - Unknown': 'loss_other',
              'Loss - Other': 'loss_other',
              'CP Infringe - ': 'cpInfringement',
              'Loss - Forced Pass': 'loss_badPass'}

#Loop through files for cleaning
for dataFile in rawDataFiles:
    
    #Check if finals datafile
    if 'Finals' in dataFile:
        
        #Identify the two teams in the filename
        #Team A - splits by vs., then by FInals and hyphens, drops spaces and numbers
        teamA = ''.join([ii for ii in dataFile.split('vs')[0].split('Finals')[-1].split('-')[-1] if not ii.isdigit()]).replace(' ','')
        teamA_id = dataSquadDict[teamA]
        #Team B - splits by vs., then by .csv, drops spaces and numbers
        teamB = ''.join([ii for ii in dataFile.split('vs')[1].split('.csv')[0] if not ii.isdigit()]).replace(' ','')
        teamB_id = dataSquadDict[teamB]
    
        #Identify the round number - simply allocated here
        #Note we add 14 to the round here to signify rounds following finals
        if '- SF -' in dataFile:
            roundNo = 15
        elif '- PF -' in dataFile:
            roundNo = 16
        elif '- GF -' in dataFile:
            roundNo = 17
            
        #Identify the match Id from the two team Id's and round number
        #Get unique match Id - note subtracting 14 from round number is required
        matchId = teamStats2018.loc[(teamStats2018['matchType'] == 'final') &
                                    (teamStats2018['roundNo'] == roundNo-14) &
                                    (teamStats2018['squadId'].isin([teamA_id, teamB_id])),
                                    ]['matchId'].unique()
        #Check length to determine that unique Id has been found
        if len(matchId) == 1:
            matchId = matchId[0]
        else:
            raise ValueError('Multiple match Id identified...')

    else:
    
        #Identify the two teams in the filename
        #Team A - splits by vs., then by round, drops spaces and numbers
        teamA = ''.join([ii for ii in dataFile.split('vs')[0].split('Round')[-1] if not ii.isdigit()]).replace(' ','')
        teamA_id = dataSquadDict[teamA]
        #Team B - splits by vs., then by .csv, drops spaces and numbers
        teamB = ''.join([ii for ii in dataFile.split('vs')[1].split('.csv')[0] if not ii.isdigit()]).replace(' ','')
        teamB_id = dataSquadDict[teamB]
        
        #Identify the round number
        roundNo = int(''.join([ii for ii in dataFile.split('Round')[-1] if ii.isdigit()]))
        
        #Identify the match Id from the two team Id's and round number
        #Get unique match Id
        matchId = teamStats2018.loc[(teamStats2018['matchType'] == 'regular') &
                                    (teamStats2018['roundNo'] == roundNo) &
                                    (teamStats2018['squadId'].isin([teamA_id, teamB_id])),
                                    ]['matchId'].unique()
        #Check length to determine that unique Id has been found
        if len(matchId) == 1:
            matchId = matchId[0]
        else:
            raise ValueError('Multiple match Id identified...')
        
    #Read in data (drop nan's for players)
    codedData = pd.read_csv(f'..\\data\\raw\\{dataFile}')
    codedData = codedData[codedData['Player'].notna()].reset_index(drop = True)
    
    #Clean up data a little further
    #Drop any nans for X and Y coords
    codedData = codedData[codedData['XCoord'].notna()].reset_index(drop = True)
    codedData = codedData[codedData['YCoord'].notna()].reset_index(drop = True)
    #Drop any events that aren't in our list
    codedData = codedData.loc[codedData['Event'].isin(list(eventsDict.keys())),].reset_index(drop = True)
    #Convert coordinate data to integer
    codedData['YCoord'] = codedData['YCoord'].astype(int)
    codedData['XCoord'] = codedData['XCoord'].astype(int)
    
    #Add team Id's to coded data
    codedData['squadId'] = [teamA_id if teamNo == 0 else teamB_id for teamNo in codedData['Team']]
    
    #Add event labels to coded data
    codedData['eventLabel'] = [eventsDict[event] for event in codedData['Event']]
    
    #Add in matchId
    codedData['matchId'] = [matchId] * len(codedData)
    
    #Special name checks in data
    #M. Robinson to M. Browne for Magpies
    for ii in codedData.index:
        if codedData.iloc[ii]['Player'] == 'Robinson' and codedData.iloc[ii]['squadId'] == 8119:
            codedData.at[ii,'Player'] = 'Browne'
    
    #Align player names with Id's
    #### TODO: handling special characters (e.g. Manu'a)
    
    #Get names from current match
    matchPlayerNames = playerLists2018.loc[playerLists2018['matchId'] == matchId, ].reset_index(drop = True)
    
    #Get unique names from coded data
    codedPlayerNames = list(codedData['Player'].unique())
    
    #Loop through coded player names and sequence match to surnames from list
    #### NOTE: this might struggle with matching player surnames
    playerId = []
    for playerSurname in codedPlayerNames:
        
        #Identify the team this player is from to make it easier
        if codedData.loc[codedData['Player'] == playerSurname,]['Team'].unique()[0] == 0:
            playerTeam = teamA_id
        else:
            playerTeam = teamB_id
            
        #Drop end space of player name if present
        if playerSurname[-1] == ' ':
            playerSurname = playerSurname[0:-1]
            
        #Get the players team names
        teamPlayerNames = matchPlayerNames.loc[matchPlayerNames['squadId'] == playerTeam,].reset_index(drop = True)
        
        #Calculate name ratios
        nameRatios = [SequenceMatcher(None, playerSurname, matchDataSurname.encode('cp1252').decode('utf-8')).ratio() for matchDataSurname in teamPlayerNames['surname']]
        
        #Check for a good match else raise and error
        if np.max(nameRatios) >= 0.85:
            #Extract the player Id
            playerId.append(teamPlayerNames.iloc[nameRatios.index(np.max(nameRatios))]['playerId'])
        else:
            #Raise an error
            raise ValueError('Name ratio not high enough to allocate player Id...')
        
    #Link up two lists into dictionary
    playerIdData = dict(zip(codedPlayerNames, playerId))
    
    #Add player Id's to coded data
    codedData['playerId'] = [playerIdData[surname] for surname in codedData['Player']]
    
    #Create a better scoreline that adds the score when there is a make
    #Create variables to calculate score    
    newScoreA, newScoreB = [], []
    scoreA, scoreB = 0, 0
    #Loop through events and allocate new scores
    for ii in codedData.index:
        #Check for goal make
        if codedData.iloc[ii]['eventLabel'] == 'goalMake':
            #Check which team made it
            if codedData.iloc[ii]['Team'] == 0:
                scoreA += 1
            else:
                scoreB += 1
        #Append current score to list variables
        newScoreA.append(scoreA)
        newScoreB.append(scoreB)
    #Append to dataframe
    codedData['scoreA'] = newScoreA
    codedData['scoreB'] = newScoreB
                
    #Convert scores to a team and opposition score
    #This therefore aligns with the team events on a row by row basis
    codedData['squadScore'] = [codedData.iloc[ii]['scoreA'] if codedData.iloc[ii]['Team'] == 0 else codedData.iloc[ii]['scoreB'] for ii in codedData.index]
    codedData['oppSquadScore'] = [codedData.iloc[ii]['scoreB'] if codedData.iloc[ii]['Team'] == 0 else codedData.iloc[ii]['scoreA'] for ii in codedData.index]

    #Create a next squad score Id variable
    nextScoreId = []
    #Loop through event indices and identify next team score based on next goal make
    for ii in codedData.index:
        #Get the current period
        period = codedData.iloc[ii]['Period']
        #First check if there is a goal make event remaining within the quarter
        if np.array(codedData.loc[codedData['Period'] == period].loc[ii:]['eventLabel'] == 'goalMake').any():
            #Find the next goal make
            nextGoalInd = np.argmax(np.array(codedData.iloc[ii:]['eventLabel']) == 'goalMake') + ii
            #Check which squad has the next goal make event and append
            nextScoreId.append(codedData.iloc[nextGoalInd]['squadId'])
        else:
            #Append for no next score
            nextScoreId.append(np.nan)
    #Add to dataframe
    codedData['nextScoreSquadId'] = nextScoreId
    
    #Convert team label to A and B to match score labelling
    codedData['teamLabel'] = ['A' if teamNo == 0 else 'B' for teamNo in codedData['Team']]
    
    #Convert XY coords so that attacking and defensive ends are the same for each team
    #Data is structured so that Y coordinates of 0-200 go from defense to attack
    #X coordinates are from 0-100 from left to right looking from the defensive end
    #(i.e. the origin is in 'bottom-left' of the court)
    newX, newY = [], []
    #Loop through events
    for ii in codedData.index:

        #Get all shot attempts for the current index this team in the period
        #Check whether Y coordinate data is at the south end of the convert
        #If it is we invert the coordinates for the event
        if codedData.loc[(codedData['Period'] == codedData.iloc[ii]['Period']) &
                         (codedData['teamLabel'] == codedData.iloc[ii]['teamLabel']) &
                         (codedData['eventLabel'].isin(['goalMake','goalMiss'])),
                         ]['YCoord'].mean() < 33:
            #Invert the data
            newX.append(100 - codedData.iloc[ii]['XCoord'])
            newY.append(200 - codedData.iloc[ii]['YCoord'])
        else:
            #Leave as is
            newX.append(codedData.iloc[ii]['XCoord'])
            newY.append(codedData.iloc[ii]['YCoord'])
            
    #Add to the dataframe
    codedData['xCoord'] = newX
    codedData['yCoord'] = newY
    
    #Convert coordinates to metres based on court dimensions
    xDimensions, yDimensions = 15.25, 30.5
    codedData['xCoordMetres'] = xDimensions * (codedData['xCoord'] / 100)
    codedData['yCoordMetres'] = yDimensions * (codedData['yCoord'] / 200)
    
    #Rename period to lowercase for consistency
    codedData['period'] = codedData['Period']
        
    #### TODO: can we convert feeds to feeds with vs. without an attempt?
    
    #Select data to export
    exportData = codedData[['matchId', 'squadId', 'playerId', 'teamLabel', 'period',
                            'eventLabel', 'xCoord', 'yCoord', 'xCoordMetres', 'yCoordMetres',
                            'scoreA', 'scoreB', 'squadScore', 'oppSquadScore', 'nextScoreSquadId',
                            ]]
    
    #Export processed data
    exportData.to_csv(f'..\\data\\processed\\{matchId}_{teamA_id}_{teamB_id}_round{roundNo}.csv',
                      index = False)
    
# %% TODO: any extra code here...

# %% ----- End of collateAndCleanData.py ----- %% #