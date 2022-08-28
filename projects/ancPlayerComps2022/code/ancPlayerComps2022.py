# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Script examines statistics from 2022 SSN and ANC to determine closest player
    comparisons based on normalised statistics.
    
"""

# %% Import packages

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib import gridspec
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import numpy as np
from scipy.stats import zscore

# %% Set-up

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

#SSN
squadDict_SSN = {804: 'Vixens',
                 806: 'Swifts',
                 807: 'Firebirds',
                 8117: 'Lightning',
                 810: 'Fever',
                 8119: 'Magpies',
                 801: 'Thunderbirds',
                 8118: 'GIANTS'}
squadNameDict_SSN = {'Vixens': 804,
                     'Swifts': 806,
                     'Firebirds': 807,
                     'Lightning': 8117,
                     'Fever': 810,
                     'Magpies': 8119,
                     'Thunderbirds': 801,
                     'GIANTS': 8118}

#ANC
squadDict_ANC = {9199: 'Collingwood',
                 7872: 'Darters',
                 7871: 'Fever',
                 7867: 'Force',
                 7183: 'Fury',
                 9196: 'Giants',
                 9197: 'Lightning',
                 7869: 'Sapphires',
                 9198: 'Swifts',
                 7873: 'Tasmania'}
squadNameDict_ANC = {'Collingwood': 9199,
                     'Darters': 7872,
                     'Fever': 7871,
                     'Force': 7867,
                     'Fury': 7183,
                     'Giants': 9196,
                     'Lightning': 9197,
                     'Sapphires': 7869,
                     'Swifts': 9198,
                     'Tasmania': 7873}

#Colour settings for teams

#SSN
colourDict_SSN = {'Fever': '#00953b',
                  'Firebirds': '#4b2c69',
                  'GIANTS': '#f57921',
                  'Lightning': '#fdb61c',
                  'Magpies': '#494b4a',
                  'Swifts': '#ee3124',
                  'Thunderbirds': '#e54078',
                  'Vixens': '#00a68e'}

#ANC
colourDict_ANC = {'Collingwood': '#494b4a',
                  'Darters': '#b94098',
                  'Fever': '#00953b',
                  'Force': '#ed2327',
                  'Fury': '#00a890',
                  'Giants': '#f57921',
                  'Lightning': '#fdb61c',
                  'Sapphires': '#b41f73',
                  'Swifts': '#ee3124',
                  'Tasmania': '#025e4b'}

#Load the team logos into a dictionary for later use

#SSN
ssnLogoDict = {}
for squadName in list(squadNameDict_SSN.keys()):
    ssnLogoDict[squadName] = plt.imread(f'..\\images\\ssn\\{squadName}.png')
    
#ANC
ancLogoDict = {}
for squadName in list(squadNameDict_ANC.keys()):
    ancLogoDict[squadName] = plt.imread(f'..\\images\\anc\\{squadName}.png')
    
#Set matplotlib parameters
#Note that these will probably be manually manipulated later anyway
from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

#Add custom fonts for use with matplotlib
# [f.name for f in font_manager.fontManager.ttflist]
#Navigate to directory
os.chdir('..\\fonts\\')
#Add fonts
for font in font_manager.findSystemFonts(os.getcwd()):
    font_manager.fontManager.addfont(font)
#Return to base directory
os.chdir('..\\code\\')

#Create list of statistics to compare between players/competitions
statsToCompare = ['badHands', 'badPasses', 'blocked', 'blocks', 'centrePassReceives',
                  'contactPenalties', 'deflectionWithGain', 'deflectionWithNoGain',
                  'feedWithAttempt', 'feeds', 'gain', 'generalPlayTurnovers',
                  'goalAssists', 'goalAttempts', 'goalMisses', 'goals',
                  'interceptPassThrown', 'intercepts', 'obstructionPenalties',
                  'pickups', 'rebounds', 'secondPhaseReceive', 'unforcedTurnovers']

# %% Compile ANC statistics

#Read in player statistics from ANC competition
playerStats_ANC = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerStats',
                                              matchOptions = ['pathway', 'pathway final'])
playerStats_ANC = playerStats_ANC[2022]

#Read in minutes played from ANC competition
minutesPlayed_ANC = collatestats.getSeasonStats(baseDir = baseDir,
                                                years = [2022],
                                                fileStem = 'minutesPlayed',
                                                matchOptions = ['pathway', 'pathway final'])
minutesPlayed_ANC = minutesPlayed_ANC[2022]

#Sum the minutes played by players
totalMinutesPlayed_ANC = minutesPlayed_ANC.groupby('playerId').sum()['minutesPlayed']

#Sort by minutes played
totalMinutesPlayed_ANC = totalMinutesPlayed_ANC.sort_values(ascending = False)

#Extract the player Id's for the top 50 players to look at
ancPlayerList = totalMinutesPlayed_ANC.index.to_list()[0:50]
totalMinutesPlayed_ANC = totalMinutesPlayed_ANC.loc[totalMinutesPlayed_ANC.index.isin(ancPlayerList),]

#Re-sort minutes played by player index
totalMinutesPlayed_ANC.sort_index(inplace = True)

#Sum the player statistics to get total numbers
#As part of this extract the relevant statistics we want to compare totals for
totalPlayerStats_ANC = playerStats_ANC.groupby('playerId').sum()[statsToCompare]

#Retain the relevant players from the stats dataset
totalPlayerStats_ANC = totalPlayerStats_ANC.loc[totalPlayerStats_ANC.index.isin(ancPlayerList),]

#Sort by player Id index to align with minutes played
totalPlayerStats_ANC.sort_index(inplace = True)

#Calculate total stats to per 60 minute values
#Do this by dividing each row by minutes played / 60
per60PlayerStats_ANC = totalPlayerStats_ANC.div(np.array(totalMinutesPlayed_ANC) / 60, axis = 'rows')

#Normalise per 60 minute values to z-scores for each statistic
#This places all stats on a normalised scale
per60NormPlayerStats_ANC = per60PlayerStats_ANC.apply(zscore)

#Replace any stats that have complete nan's with zeros
per60NormPlayerStats_ANC.fillna(0, inplace = True)

# %% Create player dictionary for ANC players

#Read in player data to review line-ups
playerList_ANC = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'playerList',
                                             matchOptions = ['pathway', 'pathway final'])
playerList_ANC = playerList_ANC[2022]

#Create dictionary with player Id's
playerDict_ANC = {'playerId': [], 'playerName': [], 'squadId': []}

#Get unique player Id's
playerIds = playerList_ANC['playerId'].unique()

#Loop through Ids
for pId in playerIds:
    
    #Check if in list already
    if pId not in playerDict_ANC['playerId']:
        
        #Extract and append
        playerDict_ANC['playerId'].append(pId)
        playerDict_ANC['playerName'].append(playerList_ANC.loc[playerList_ANC['playerId'] == pId,
                                                               ['firstname']]['firstname'].unique()[0] + \
                                            ' ' + playerList_ANC.loc[playerList_ANC['playerId'] == pId,
                                                                     ['surname']]['surname'].unique()[0])
        playerDict_ANC['squadId'].append(playerList_ANC.loc[playerList_ANC['playerId'] == pId,
                                                            ['squadId']]['squadId'].unique()[0])
    
#Convert to dataframe
ancPlayer_df = pd.DataFrame.from_dict(playerDict_ANC)

# %% Compile SSN statistics

#Read in player statistics from SSN competition
playerStats_SSN = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerStats',
                                              matchOptions = ['regular'])
playerStats_SSN = playerStats_SSN[2022]

#Read in minutes played from ANC competition
minutesPlayed_SSN = collatestats.getSeasonStats(baseDir = baseDir,
                                                years = [2022],
                                                fileStem = 'minutesPlayed',
                                                matchOptions = ['regular'])
minutesPlayed_SSN = minutesPlayed_SSN[2022]

#Sum the minutes played by players
totalMinutesPlayed_SSN = minutesPlayed_SSN.groupby('playerId').sum()['minutesPlayed']

#Sort by minutes played
totalMinutesPlayed_SSN = totalMinutesPlayed_SSN.sort_values(ascending = False)

#Extract the player Id's players who played 60 or more minutes
totalMinutesPlayed_SSN = totalMinutesPlayed_SSN.loc[totalMinutesPlayed_SSN >= 60]
ssnPlayerList = totalMinutesPlayed_SSN.index.to_list()

#Re-sort minutes played by player index
totalMinutesPlayed_SSN.sort_index(inplace = True)

#Sum the player statistics to get total numbers
#As part of this extract the relevant statistics we want to compare totals for
totalPlayerStats_SSN = playerStats_SSN.groupby('playerId').sum()[statsToCompare]

#Retain the relevant players from the stats dataset
totalPlayerStats_SSN = totalPlayerStats_SSN.loc[totalPlayerStats_SSN.index.isin(ssnPlayerList),]

#Sort by player Id index to align with minutes played
totalPlayerStats_SSN.sort_index(inplace = True)

#Calculate total stats to per 60 minute values
#Do this by dividing each row by minutes played / 60
per60PlayerStats_SSN = totalPlayerStats_SSN.div(np.array(totalMinutesPlayed_SSN) / 60, axis = 'rows')

#Normalise per 60 minute values to z-scores for each statistic
#This places all stats on a normalised scale
per60NormPlayerStats_SSN = per60PlayerStats_SSN.apply(zscore)

#Replace any stats that have complete nan's with zeros
per60NormPlayerStats_SSN.fillna(0, inplace = True)

# %% Create player dictionary for SSN players

#Read in player data to review line-ups
playerList_SSN = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'playerList',
                                             matchOptions = ['regular'])
playerList_SSN = playerList_SSN[2022]

#Create dictionary with player Id's
playerDict_SSN = {'playerId': [], 'playerName': [], 'squadId': []}

#Get unique player Id's
playerIds = playerList_SSN['playerId'].unique()

#Loop through Ids
for pId in playerIds:
    
    #Check if in list already
    if pId not in playerDict_SSN['playerId']:
        
        #Extract and append
        playerDict_SSN['playerId'].append(pId)
        playerDict_SSN['playerName'].append(playerList_SSN.loc[playerList_SSN['playerId'] == pId,
                                                               ['firstname']]['firstname'].unique()[0] + \
                                            ' ' + playerList_SSN.loc[playerList_SSN['playerId'] == pId,
                                                                     ['surname']]['surname'].unique()[0])
        playerDict_SSN['squadId'].append(playerList_SSN.loc[playerList_SSN['playerId'] == pId,
                                                            ['squadId']]['squadId'].unique()[0])
    
#Convert to dataframe
ssnPlayer_df = pd.DataFrame.from_dict(playerDict_SSN)

# %% Make player comparisons based on normalised stats and Euclidean distance

#Create dictionary to store data
playerCompDict = {pId: {'ssnPlayerId': [], 'distance': []} for pId in ancPlayerList}

#Loop through ANC players
for playerId in ancPlayerList:
    
    #Get the iloc index for the current ANC player in the stats dataframe
    playerInd = per60NormPlayerStats_ANC.index.to_list().index(playerId)
    
    #Get the current ANC players stats as a numpy array
    ancPlayerStats = per60NormPlayerStats_ANC.iloc[playerInd].to_numpy()
    
    #Loop through the SSN players
    for playerId_SSN in per60NormPlayerStats_SSN.index.to_list():
        
        #Get the iloc index for the current SSN player in the stats dataframe
        playerInd_SSN = per60NormPlayerStats_SSN.index.to_list().index(playerId_SSN)
        
        #Get the current SSN players stats as a numpy array
        ssnPlayerStats = per60NormPlayerStats_SSN.iloc[playerInd_SSN].to_numpy()
        
        #Calculate distance and append to dictionary
        playerCompDict[playerId]['ssnPlayerId'].append(playerId_SSN)
        playerCompDict[playerId]['distance'].append(np.linalg.norm(ancPlayerStats-ssnPlayerStats))

# %% Create visual

#Get the maximum distance value for normalisation
distNormVal = np.max([np.max(playerCompDict[pId]['distance']) for pId in list(playerCompDict.keys())])

#Set-up figure
fig = plt.figure(figsize = (9, 24))

#Create the desired grid for axes to work with

#Set grid size for axes
gridSpec = gridspec.GridSpec(40, 20)

#Adjust the subplots
gridSpec.update(left = 0.02, right = 0.98,
                bottom = 0.02, top = 0.90, 
                wspace = 0.30, hspace = 0.30)

#Set row and column starting value
rowVal = 0
colVal = 0

#Loop through ANC player list
for playerId in ancPlayerList:
        
    #===== Player name =====#
    
    #Create the axes
    # playerLogoAx = plt.subplot(gridSpec.new_subplotspec((0,0), rowspan = 1, colspan = 1))
    playerNameAx = plt.subplot(gridSpec.new_subplotspec((rowVal,colVal), rowspan = 1, colspan = 4))
    
    #Get player squad Id and name
    playerSquadId = ancPlayer_df.loc[ancPlayer_df['playerId'] == playerId,
                                  ]['squadId'].unique()[0]
    playerSquadName = squadDict_ANC[playerSquadId]
    
    #Display the current players team logo
    # playerLogoAx.imshow(ancLogoDict[squadName])
    
    #Get player name
    playerName = ancPlayer_df.loc[ancPlayer_df['playerId'] == playerId,
                                  ]['playerName'].unique()[0]
    
    #Display the current players name
    ####TODO: colouring for some players seems wrong???
    playerNameAx.text(0.5, 0.6, playerName,
                      font = 'JerrySport', fontsize = 9,
                      ha = 'center', va = 'center', clip_on = False,
                      color = colourDict_ANC[playerSquadName])
    
    #Turn off axes lines
    # playerLogoAx.axis('off')
    # playerNameAx.axis('off')
    
    #Turn off unwanted spines
    playerNameAx.spines['top'].set_visible(False)
    playerNameAx.spines['left'].set_visible(False)
    playerNameAx.spines['right'].set_visible(False)
    playerNameAx.set_yticks([])
    
    #Colour bottom spine and remove ticks
    playerNameAx.set_xticks([])
    playerNameAx.spines['bottom'].set_color(colourDict_ANC[playerSquadName])
    
    #===== Player comps =====#
    
    #Get the players comparisons
    playerComps = playerCompDict[playerId]
    
    #Grab the max value from the comps for normalisation
    # maxCompVal = np.max(playerComps['distance'])
    
    #Get the indices of the 3 smallest values
    topInd = np.argsort(playerComps['distance'])[:3]
    
    #Get the top 3 comp player Id's and distance values
    #Normalise these distance values to the max here too
    compIds = [playerComps['ssnPlayerId'][ii] for ii in topInd]
    # compDists = np.array([(maxCompVal - playerComps['distance'][ii]) / maxCompVal for ii in topInd])
    compDists = np.array([(distNormVal - playerComps['distance'][ii]) / distNormVal for ii in topInd])
    
    #Get the comparison names
    compNames = [ssnPlayer_df.loc[ssnPlayer_df['playerId'] == pId,]['playerName'].values[0] for pId in compIds]
    
    #Get the comparison squad names
    compSquads = [squadDict_SSN[ssnPlayer_df.loc[ssnPlayer_df['playerName'] == ii]['squadId'].values[0]] for ii in compNames]
    
    #Loop through the top 3 comparisons
    for compNo in range(len(compNames)):
        
        #Create the axes for comp players
        compLogoAx = plt.subplot(gridSpec.new_subplotspec((rowVal+compNo+1,colVal), rowspan = 1, colspan = 1))
        compNameAx = plt.subplot(gridSpec.new_subplotspec((rowVal+compNo+1,colVal+1), rowspan = 1, colspan = 3))
    
        #Add comp player logo
        compLogoAx.imshow(ssnLogoDict[compSquads[compNo]])
    
        #Add player comp name to axis
        compNameAx.text(0, 0.55, compNames[compNo],
                        font = 'Coolvetica', fontsize = 7,
                        ha = 'left', va = 'bottom')
    
        #Add the similarity bar
        #Initial empty rectangle
        compNameAx.add_patch(Rectangle((0,0.15), 0.70, 0.30,
                                       edgecolor = 'k', facecolor = 'none'))
        #Add the fill based on the similarity value
        compNameAx.add_patch(Rectangle((0,0.15), 0.70*compDists[compNo], 0.30,
                                       edgecolor = 'k', facecolor = 'k'))
        
        #Add the percentage similarity value
        compNameAx.text(0.99, 0.05, f'{np.round(compDists[compNo]*100, 1)}%',
                        font = 'Coolvetica', fontsize = 10,
                        ha = 'right', va = 'bottom')
        
        #Turn off axes
        compLogoAx.axis('off')
        compNameAx.axis('off')
    
    #Add to the column value
    colVal += 4
    
    #Check whether to return to the first column and add to the rows
    if colVal == 20:
        colVal = 0
        rowVal += 4
    
#Add ANC figure
#Read in image
ancLogo = plt.imread('..\\images\\ANC.png')
#Use first axes to map the image as a reference against
logoAx = plt.gca()
#Create offset image
imOffset = OffsetImage(ancLogo, zoom = 0.14)
#Create annotation box
annBox = AnnotationBbox(imOffset, (0.025,0.95),
                        frameon = False,
                        box_alignment = (0.0,0.5),
                        xycoords = fig.transFigure,
                        pad = 0, zorder = 0)
#Add image
logoAx.add_artist(annBox)

#Add figure title
fig.text(0.175, 0.95, 'SSN PLAYER\nCOMPARISONS',
         ha = 'left', va = 'center',
         font = 'Gotham Black', fontsize = 20, c = 'black')

#Add descriptive text
#Set strings
string1 = 'Super Netball (SSN) player comparisons for players at the 2022 Australian Netball Championships (ANC).'
string2 = 'Player statistics\nfrom the 2022 SSN regular season were compared to those of players (top 50 players for minutes played) at the ANC.\n'
string3 = 'Each statistic was scaled to minutes played (i.e. per 60 mins) and normalised to the mean & variance of the statistic\nwithin the relevant competition.'
string4 = 'The degree of similarity was identified by calculating a normalised Euclidean\ndistance between the ANC player to those in SSN and the top 3 comparisons shown.'
#Display strings
fig.text(0.99, 0.990, f'{string1} {string2} {string3} {string4}',
         ha = 'right', va = 'top', wrap = True,
         font = 'Coolvetica', fontsize = 10, c = 'black')

#Save figure
plt.savefig('..\\outputs\\ancPlayerComps2022.png', format = 'png', 
            facecolor = fig.get_facecolor(), edgecolor = 'none',
            dpi = 300)

#Close figure
plt.close()

# %%% ----- End of ancPlayerComps2022.py -----