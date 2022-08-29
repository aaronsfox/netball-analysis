# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Script examines statistics from ANCZ/SSN and ANC to determine closest player
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

#Elite
squadDict_Historical = {804: 'Vixens',
                        806: 'Swifts',
                        807: 'Firebirds',
                        8117: 'Lightning',
                        810: 'Fever',
                        8119: 'Magpies',
                        801: 'Thunderbirds',
                        8118: 'GIANTS',
                        809:'Magic',
                        805: 'Mystics',
                        803: 'Pulse',
                        808: 'Steel',
                        802: 'Tactix'}
squadNameDict_Historical = {'Vixens': 804,
                            'Swifts': 806,
                            'Firebirds': 807,
                            'Lightning': 8117,
                            'Fever': 810,
                            'Magpies': 8119,
                            'Thunderbirds': 801,
                            'GIANTS': 8118,
                            'Magic': 809,
                            'Mystics': 805,
                            'Pulse': 803,
                            'Steel': 808,
                            'Tactix': 802}

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

#Elite
colourDict_Historical = {'Fever': '#00953b',
                         'Firebirds': '#4b2c69',
                         'Giants': '#f57921',
                         'Lightning': '#fdb61c',
                         'Magic': '#000000',
                         'Magpies': '#494b4a',
                         'Mystics': '#0000cd',
                         'Pulse': '#ffd500',
                         'Steel': '#00b7eb',
                         'Swifts': '#0082cd',
                         'Tactix': '#ee161f',
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

#Elite
historicalLogoDict = {}
for squadName in list(squadNameDict_Historical.keys()):
    historicalLogoDict[squadName] = plt.imread(f'..\\images\\anzc-ssn\\{squadName}_small.png')
    
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
# statsToCompare = ['badHands', 'badPasses', 'blocked', 'blocks', 'centrePassReceives',
#                   'contactPenalties', 'deflectionWithGain', 'deflectionWithNoGain',
#                   'feedWithAttempt', 'feeds', 'gain', 'generalPlayTurnovers',
#                   'goalAssists', 'goalAttempts', 'goalMisses', 'goals',
#                   'interceptPassThrown', 'intercepts', 'obstructionPenalties',
#                   'pickups', 'rebounds', 'secondPhaseReceive', 'unforcedTurnovers']
statsToCompare = ['badHands', 'badPasses', 'blocked', 'blocks', 'centrePassReceives',
                  'contactPenalties',
                  'feeds', 'gain',
                  'goalAssists', 'goalAttempts', 'goalMisses', 'goals',
                  'intercepts', 'obstructionPenalties',
                  'pickups', 'rebounds']

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

# %% Compile elite statistics

#Create new list to include player Id in extraction
statsToCompare.append('playerId')

#Read in player statistics from elite competition
#Ignored 2009 as some issues with stats
playerStats_Historical = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = list(np.linspace(2010,2022,13,dtype = int)),
                                                     fileStem = 'playerStats',
                                                     matchOptions = ['regular'])

#Extract relevant statistics to a singular dataframe
### NOTE: minimal stat set and potentially still some issues here
playerStats_Historical = pd.concat([playerStats_Historical[year][statsToCompare] for year in playerStats_Historical.keys()])

#Read in minutes played from ANC competition
minutesPlayed_Historical = collatestats.getSeasonStats(baseDir = baseDir,
                                                years = list(np.linspace(2010,2022,13,dtype = int)),
                                                fileStem = 'minutesPlayed',
                                                matchOptions = ['regular'])

#Extract minutes played to a singular dataframe
minutesPlayed_Historical = pd.concat([minutesPlayed_Historical[year] for year in minutesPlayed_Historical.keys()])

#Sum the minutes played by players
totalminutesPlayed_Historical = minutesPlayed_Historical.groupby('playerId').sum()['minutesPlayed']

#Sort by minutes played
totalminutesPlayed_Historical = totalminutesPlayed_Historical.sort_values(ascending = False)

#Extract the player Id's players who played a full season of minutes (over time)
totalminutesPlayed_Historical = totalminutesPlayed_Historical.loc[totalminutesPlayed_Historical >= (60*14)]
historicalPlayerList = totalminutesPlayed_Historical.index.to_list()

#Re-sort minutes played by player index
totalminutesPlayed_Historical.sort_index(inplace = True)

#Sum the player statistics to get total numbers
#As part of this extract the relevant statistics we want to compare totals for
#Revert back to original stats list
statsToCompare = ['badHands', 'badPasses', 'blocked', 'blocks', 'centrePassReceives',
                  'contactPenalties',
                  'feeds', 'gain',
                  'goalAssists', 'goalAttempts', 'goalMisses', 'goals',
                  'intercepts', 'obstructionPenalties',
                  'pickups', 'rebounds']
#Extract data
totalplayerStats_Historical = playerStats_Historical.groupby('playerId').sum()[statsToCompare]

#Retain the relevant players from the stats dataset
totalplayerStats_Historical = totalplayerStats_Historical.loc[totalplayerStats_Historical.index.isin(historicalPlayerList),]

#Sort by player Id index to align with minutes played
totalplayerStats_Historical.sort_index(inplace = True)

#Calculate total stats to per 60 minute values
#Do this by dividing each row by minutes played / 60
per60playerStats_Historical = totalplayerStats_Historical.div(np.array(totalminutesPlayed_Historical) / 60, axis = 'rows')

#Normalise per 60 minute values to z-scores for each statistic
#This places all stats on a normalised scale
per60NormplayerStats_Historical = per60playerStats_Historical.apply(zscore)

#Replace any stats that have complete nan's with zeros
per60NormplayerStats_Historical.fillna(0, inplace = True)

# %% Create player dictionary for elite players

#Read in player data to review line-ups
playerList_Historical = collatestats.getSeasonStats(baseDir = baseDir,
                                                    years = list(np.linspace(2010,2022,13,dtype = int)),
                                                    fileStem = 'playerList',
                                                    matchOptions = ['regular'])

#Extract player list to a singular dataframe
playerList_Historical = pd.concat([playerList_Historical[year] for year in playerList_Historical.keys()])

#Create dictionary with player Id's
playerDict_Historical = {'playerId': [], 'playerName': [], 'squadId': []}

#Get unique player Id's
playerIds = playerList_Historical['playerId'].unique()

#Loop through Ids
for pId in playerIds:
    
    #Check if in list already
    if pId not in playerDict_Historical['playerId']:
        
        #Extract and append
        #Id and Name
        playerDict_Historical['playerId'].append(pId)
        playerDict_Historical['playerName'].append(playerList_Historical.loc[playerList_Historical['playerId'] == pId,
                                                                      ['firstname']]['firstname'].unique()[0] + \
                                                   ' ' + playerList_Historical.loc[playerList_Historical['playerId'] == pId,
                                                                            ['surname']]['surname'].unique()[0])
        #Squad Id
        #Get list of teams played for
        squadList = list(playerList_Historical.loc[playerList_Historical['playerId'] == pId,
                                                   ['squadId']]['squadId'])
        #Get most frequent in list, or if even the latest one
        squadList.reverse()
        playerDict_Historical['squadId'].append(max(squadList, key = squadList.count))
    
#Convert to dataframe
historicalPlayer_df = pd.DataFrame.from_dict(playerDict_Historical)

# %% Make player comparisons based on normalised stats and Euclidean distance

#Create dictionary to store data
playerCompDict = {pId: {'historicalPlayerId': [], 'distance': []} for pId in ancPlayerList}

#Loop through ANC players
for playerId in ancPlayerList:
    
    #Get the iloc index for the current ANC player in the stats dataframe
    playerInd = per60NormPlayerStats_ANC.index.to_list().index(playerId)
    
    #Get the current ANC players stats as a numpy array
    ancPlayerStats = per60NormPlayerStats_ANC.iloc[playerInd].to_numpy()
    
    #Loop through the SSN players
    for playerId_Historical in per60NormplayerStats_Historical.index.to_list():
        
        #Get the iloc index for the current SSN player in the stats dataframe
        playerInd_SSN = per60NormplayerStats_Historical.index.to_list().index(playerId_Historical)
        
        #Get the current SSN players stats as a numpy array
        historicalPlayerStats = per60NormplayerStats_Historical.iloc[playerInd_SSN].to_numpy()
        
        #Calculate distance and append to dictionary
        playerCompDict[playerId]['historicalPlayerId'].append(playerId_Historical)
        playerCompDict[playerId]['distance'].append(np.linalg.norm(ancPlayerStats-historicalPlayerStats))

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
    playerNameAx.text(0.5, 0.6, playerName,
                      font = 'JerrySport', fontsize = 9,
                      ha = 'center', va = 'center', clip_on = False,
                      color = colourDict_ANC[playerSquadName])
    
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
    
    #Get the indices of the 3 smallest values
    topInd = np.argsort(playerComps['distance'])[:3]
    
    #Get the top 3 comp player Id's and distance values
    #Normalise these distance values to the max here too
    compIds = [playerComps['historicalPlayerId'][ii] for ii in topInd]
    # compDists = np.array([(maxCompVal - playerComps['distance'][ii]) / maxCompVal for ii in topInd])
    compDists = np.array([(distNormVal - playerComps['distance'][ii]) / distNormVal for ii in topInd])
    
    #Get the comparison names
    compNames = [historicalPlayer_df.loc[historicalPlayer_df['playerId'] == pId,]['playerName'].values[0] for pId in compIds]
    
    #Get the comparison squad names
    compSquads = [squadDict_Historical[historicalPlayer_df.loc[historicalPlayer_df['playerName'] == ii]['squadId'].values[0]] for ii in compNames]
    
    #Loop through the top 3 comparisons
    for compNo in range(len(compNames)):
        
        #Create the axes for comp players
        compLogoAx = plt.subplot(gridSpec.new_subplotspec((rowVal+compNo+1,colVal), rowspan = 1, colspan = 1))
        compNameAx = plt.subplot(gridSpec.new_subplotspec((rowVal+compNo+1,colVal+1), rowspan = 1, colspan = 3))
    
        #Add comp player logo
        compLogoAx.imshow(historicalLogoDict[compSquads[compNo]])
    
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
fig.text(0.175, 0.95, 'PLAYER\nCOMPARISONS',
         ha = 'left', va = 'center',
         font = 'Gotham Black', fontsize = 20, c = 'black')

#Add descriptive text
#Set strings
string1 = 'Historical (i.e. ANZC/SSN) player comparisons for players at the 2022 Australian Netball Championships (ANC).'
string2 = 'Player statistics\nfrom the 2010-2022 elite regular seasons were compared to those of players (top 50 players for minutes played) at the ANC.\n'
string3 = 'Each statistic was scaled to minutes played (i.e. per 60 mins) and normalised to the mean & variance of the statistic\nwithin the relevant competition.'
string4 = 'The degree of similarity was identified by calculating a normalised Euclidean\ndistance between the ANC player to those in elite competition and the top 3 comparisons shown.'
#Display strings
fig.text(0.99, 0.990, f'{string1} {string2} {string3} {string4}',
         ha = 'right', va = 'top', wrap = True,
         font = 'Coolvetica', fontsize = 10, c = 'black')

#Save figure
plt.savefig('..\\outputs\\ancHistoricalPlayerComps2022.png', format = 'png', 
            facecolor = fig.get_facecolor(), edgecolor = 'none',
            dpi = 300)

#Close figure
plt.close()

# %%% ----- End of ancPlayerComps2022.py -----