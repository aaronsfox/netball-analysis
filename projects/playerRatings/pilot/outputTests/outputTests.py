# -*- coding: utf-8 -*-
"""

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This code runs through various output tests related to the data. Typically, 
    it follows the work of Karl Jackson's thesis, as this is what the basis for
    replicating the player ratings analysis is built upon.

"""

# %% Import packages

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import seaborn as sns
from scipy.interpolate import Rbf
import pickle

# %% Set-up

#Set matplotlib parameters
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

#Set court width and length parameters
courtWidth_coord = 100
courtLength_coord = 200

# %% Import data

#Identify the filenames for import
fileList = os.listdir('..\\..\\data\\processed')

#Set up a dictionary to store individual datafiles
matchData = {}

#Loop through and import files
for file in fileList:
    
    #Identify the match Id in the filename
    matchId = int(file.split('_')[0])
    
    #Read into dictionary
    matchData[matchId] = pd.read_csv(f'..\\..\\data\\processed\\{file}')
    
    #Read into all data structure
    if fileList.index(file) == 0:
        #Read in first datafile
        allMatchData = pd.read_csv(f'..\\..\\data\\processed\\{file}')
    else:
        #Concatenate to build up dataframe
        allMatchData = pd.concat([allMatchData,
                                  pd.read_csv(f'..\\..\\data\\processed\\{file}')]).reset_index(drop = True)
        
# %% Heatmaps

"""

Here we test the concept of heatmaps, following a similar process outlined in
Chapter 4 of Karl Jackson's thesis. We take a simple example here of extracting
Liz Watson's (player Id: 994224) simple possessions, and map these to a netball
court.

"""

#Set Watson Id
watsonId = 994224

#Extract Watson's possessions across the dataset
watsonPossessions = allMatchData.loc[(allMatchData['playerId'] == watsonId) &
                                     (allMatchData['eventLabel'] == 'possession'),]

#Create figure to map data to
fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)

#Set spacing
plt.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.9)

#Set axis limits to court boundaries
ax.set_xlim([0,100])
ax.set_ylim([0,200])

#Turn off axis ticks
ax.set_xticks([])
ax.set_yticks([])

#Add court lines
#Third lines
ax.plot([0,courtWidth_coord], [courtLength_coord/3, courtLength_coord/3],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
ax.plot([0,courtWidth_coord], [courtLength_coord/3*2, courtLength_coord/3*2],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
#Centre circle (about 6% of court width)
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord/2), 0.06*courtWidth_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
#Shooting circles (about 16% of court length)
ax.add_patch(Circle((courtWidth_coord/2,0), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))

#Add the kdeplot for heat map
kdePlot = sns.kdeplot(data = watsonPossessions, x = 'xCoord', y = 'yCoord',
                      cmap = 'RdYlGn_r', alpha = 0.4, fill = True,
                      bw_method = 'scott', bw_adjust = 1, thresh = 0.00,
                      zorder = 2, ax = ax)

"""

Above plot looks OK - would like to find a way to remove the lines around contours
though. Otherwise the process seems to work and the Scott smoothing method is 
internally applied in the seaborn function.

"""

#Can contrast to someone like Kate Moloney
moloneyId = 991901

#Extract Moloney's possessions across the dataset
moloneyPossessions = allMatchData.loc[(allMatchData['playerId'] == moloneyId) &
                                      (allMatchData['eventLabel'] == 'possession'),]

#Create figure to map data to
fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)

#Set spacing
plt.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.9)

#Set axis limits to court boundaries
ax.set_xlim([0,100])
ax.set_ylim([0,200])

#Turn off axis ticks
ax.set_xticks([])
ax.set_yticks([])

#Add court lines
#Third lines
ax.plot([0,courtWidth_coord], [courtLength_coord/3, courtLength_coord/3],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
ax.plot([0,courtWidth_coord], [courtLength_coord/3*2, courtLength_coord/3*2],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
#Centre circle (about 6% of court width)
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord/2), 0.06*courtWidth_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
#Shooting circles (about 16% of court length)
ax.add_patch(Circle((courtWidth_coord/2,0), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))

#Add the kdeplot for heat map
kdePlot = sns.kdeplot(data = moloneyPossessions, x = 'xCoord', y = 'yCoord',
                      cmap = 'RdYlGn_r', alpha = 0.4, fill = True,
                      bw_method = 'scott', bw_adjust = 1, thresh = 0.00,
                      zorder = 2, ax = ax)

#Test one more example of Kim Green for a different team perspective
greenId = 80069

#Extract Moloney's possessions across the dataset
greenPossessions = allMatchData.loc[(allMatchData['playerId'] == greenId) &
                                    (allMatchData['eventLabel'] == 'possession'),]

#Create figure to map data to
fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)

#Set spacing
plt.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.9)

#Set axis limits to court boundaries
ax.set_xlim([0,100])
ax.set_ylim([0,200])

#Turn off axis ticks
ax.set_xticks([])
ax.set_yticks([])

#Add court lines
#Third lines
ax.plot([0,courtWidth_coord], [courtLength_coord/3, courtLength_coord/3],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
ax.plot([0,courtWidth_coord], [courtLength_coord/3*2, courtLength_coord/3*2],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
#Centre circle (about 6% of court width)
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord/2), 0.06*courtWidth_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
#Shooting circles (about 16% of court length)
ax.add_patch(Circle((courtWidth_coord/2,0), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))

#Add the kdeplot for heat map
kdePlot = sns.kdeplot(data = greenPossessions, x = 'xCoord', y = 'yCoord',
                      cmap = 'gray_r', alpha = 0.75, fill = True,
                      bw_method = 'scott', bw_adjust = 1, thresh = 0.00,
                      zorder = 2, ax = ax)

# %% Probability of next score

"""

This next section starts to pronbe the idea of field equity, by looking at the
probability of the next score based on field position. This is also covered in
chapter 4 of Karl Jackson's thesis. Here we take specific events (e.g. possession)
and look at the probability that the team with the ball in that location is the
next to score.

"""

#Set the colour pallette for probabilities
probCol = sns.color_palette('RdYlGn', 101)

#Set step block for coordinates
stepBlock = 10

#Extract the possession event data
# possessionData = allMatchData.loc[allMatchData['eventLabel'] == 'possession',].reset_index(drop = True)
contactData = allMatchData.loc[allMatchData['eventLabel'] == 'penalty_contact',].reset_index(drop = True)

#Loop through 10 coord step blocks and identify the probability of next score for 
#the current block
xStep = np.linspace(0, 90, stepBlock)
yStep = np.linspace(0, 190, stepBlock * 2)

#Create netball court to plot probabilities on
fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)

#Set spacing
plt.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.9)

#Set axis limits to court boundaries
ax.set_xlim([0,100])
ax.set_ylim([0,200])

#Turn off axis ticks
ax.set_xticks([])
ax.set_yticks([])

#Add court lines
#Third lines
ax.plot([0,courtWidth_coord], [courtLength_coord/3, courtLength_coord/3],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
ax.plot([0,courtWidth_coord], [courtLength_coord/3*2, courtLength_coord/3*2],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
#Centre circle (about 6% of court width)
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord/2), 0.06*courtWidth_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
#Shooting circles (about 16% of court length)
ax.add_patch(Circle((courtWidth_coord/2,0), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))

#Loop through steps of coordinate blocks
for xInt in xStep:
    for yInt in yStep:
        
        #Extract possessions within the one block coordinate window
        # currentBlock = possessionData.loc[(possessionData['xCoord'] >= xInt) &
        #                                   (possessionData['xCoord'] < xInt + stepBlock) &
        #                                   (possessionData['yCoord'] >= yInt) &
        #                                   (possessionData['yCoord'] < yInt + stepBlock),].reset_index(drop = True)
        currentBlock = contactData.loc[(contactData['xCoord'] >= xInt) &
                                       (contactData['xCoord'] < xInt + stepBlock) &
                                       (contactData['yCoord'] >= yInt) &
                                       (contactData['yCoord'] < yInt + stepBlock),].reset_index(drop = True)
        
        #Check if data in current block
        if len(currentBlock) > 0:
        
            #Calculate the current block probability of team with possession scoring next
            nextScoreBool = [1 if currentBlock.iloc[ii]['squadId'] == currentBlock.iloc[ii]['nextScoreSquadId'] else 0 for ii in currentBlock.index]
            
            #Calculate probability of next score
            nextScoreProb = np.sum(nextScoreBool) / len(nextScoreBool)
            
            #Plot rectangle at current location and probability
            ax.add_patch(Rectangle((xInt, yInt), stepBlock, stepBlock, #xy, width, height
                                   edgecolor = None, alpha = 0.7, zorder = 2,
                                   facecolor = probCol[int(np.round(nextScoreProb * 100))]
                                   ))
        
"""

The above map for possession highlights that irrespective of where you have the
ball, you've got a high probability of being the next team to score. We can take
a look at something more contrasting like contact penalties to see a difference
(edited in the code above).

"""

# %% Field equity test

"""

Examine the capacity to plot field equity for certain events. Here we start with
posession events. This attempts to replicate processes outlines in chapter 5 of
Karl Jackson's thesis for field equity - particularly generating contour maps.

"""

#Extract possession data
possessionData = allMatchData.loc[allMatchData['eventLabel'] == 'possession',].reset_index(drop = True)

#Set arbitrary distance to smooth equity within 
#(i.e. events within this distance considered in calculation)
smoothingDistance = 2

#Set dictionary to store data in
possessionFE = {'xCoord': [], 'yCoord': [], 'fieldEquity': []}

#Loop through possession data
##### NOTE: this process takes a decent amount of time --- was this taking so long due to multiple use of ii?
for ii in possessionData.index:
    
    #Get x and y coordinate (in metres) of current possession
    currPoint = np.array((possessionData.iloc[ii]['xCoordMetres'], possessionData.iloc[ii]['yCoordMetres']))
    
    #Get x and y coordinates (in metres) of all other points
    allPoints = np.array((possessionData['xCoordMetres'], possessionData['yCoordMetres'])).T
    
    #Calculate distances between points
    distances = np.linalg.norm(currPoint - allPoints, axis = 1)
    
    #Identify distances with smoothing value
    withinSmoothingDist = pd.Series(distances < smoothingDistance)
    
    #Extract the possessions within the smoothing distance
    feCalcData = possessionData[withinSmoothingDist.values].reset_index(drop = True)
    
    #Calculate equity for current possession and append to dataset
    nextScoreN = np.sum([True if feCalcData.iloc[jj]['squadId'] == feCalcData.iloc[jj]['nextScoreSquadId'] else False for jj in feCalcData.index])
    possessionFE['fieldEquity'].append(nextScoreN / len(feCalcData))
    possessionFE['xCoord'].append(possessionData.iloc[ii]['xCoord'])
    possessionFE['yCoord'].append(possessionData.iloc[ii]['yCoord'])

#Save as dictionary
with open('possessionFE.pkl', 'wb') as file:
    pickle.dump(possessionFE, file, protocol = pickle.HIGHEST_PROTOCOL)
#Load from dictionary
with open('possessionFE.pkl', 'rb') as file:
    possessionFE = pickle.load(file)
    
#Convert to dataframe for ease of use
possessionFE_data = pd.DataFrame.from_dict(possessionFE)
# possessionFE_data['xUnique'] = ~possessionFE_data['xCoord'].duplicated(keep = False)

#Add a very small amount of random noise to values to avoid duplicates
#This shouldn't be a problem as it doesn't shift the points beyond the distances
#included in calculating the FE
possessionFE_data['xCoord_noise'] = possessionFE['xCoord'] + np.random.normal(0,0.1,len(possessionFE_data))
possessionFE_data['yCoord_noise'] = possessionFE['yCoord'] + np.random.normal(0,0.1,len(possessionFE_data))

#Take just the first 5000 for speediness
contourData = possessionFE_data[1:5001]

##### TODO: stash these values somewhere once extracted...
#The above still takes a lot of time even without the double loop

#Below mapping to grid comes from: https://github.com/agilescientific/xlines/blob/master/notebooks/11_Gridding_map_data.ipynb

#Plot the data in a scatter format to examine
fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)
ax.scatter(possessionFE_data['xCoord_noise'],  possessionFE_data['yCoord_noise'],
           c = possessionFE_data['fieldEquity'])

#We then map a grid for what we want to predict values over
#For now we'll do grid intervals of 1 coordinate steps
grid_x, grid_y = np.mgrid[0:100:1, 0:200:1]
# plt.figure(figsize=(5,8))
# plt.scatter(grid_x, grid_y, s = 1)

#Interpolate data using radial basis function

#Create the radial basis function from the data
# rbfi = Rbf(possessionFE_data['xCoord_noise'],  possessionFE_data['yCoord_noise'], possessionFE_data['fieldEquity'])
rbfi = Rbf(contourData['xCoord_noise'],  contourData['yCoord_noise'], contourData['fieldEquity'])

##### TODO: there may be a memory issue here - so potentially need to uniformyl
##### sample across court grid to get a reasonable sample size for function

#Use the function to predict data on the uniform grid
Z = rbfi(grid_x, grid_y)

#Define levels in z-axis where we want lines to appear
zLevels = np.linspace(0.1, 0.9, 9)
 
#Create contour plot of possession field equity

#Create figure and axis for court
fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)

#Set spacing
plt.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.9)

#Set axis limits to court boundaries
ax.set_xlim([0,100])
ax.set_ylim([0,200])

#Turn off axis ticks
ax.set_xticks([])
ax.set_yticks([])

#Add court lines
#Third lines
ax.plot([0,courtWidth_coord], [courtLength_coord/3, courtLength_coord/3],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
ax.plot([0,courtWidth_coord], [courtLength_coord/3*2, courtLength_coord/3*2],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
#Centre circle (about 6% of court width)
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord/2), 0.06*courtWidth_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
#Shooting circles (about 16% of court length)
ax.add_patch(Circle((courtWidth_coord/2,0), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))

#Create labelled contours
CS = ax.contour(grid_x, grid_y, Z, zLevels, zorder = 2)
ax.clabel(CS, inline = True, fontsize = 10)


"""

The use of point data and then mapping this to a standard grid via a radial basis
function allows us to create pretty reasonable contour maps of field equity. The
calculated radial basis function can likely also be applied to match data progressively
when calculated for the various events to simplify the process of estimating FE
at different points across the court.

The current problem with the above is in creating the dataset for the radial basis
function seems to take a significant amount of time to loop through all of the points.
This is therefore a step that would need to be conducted, the data saved and reloaded
rather than completed each time.

TODO:
    
    > Consider a smoothing function on field equity data - much like initial AR
      football contours, there is noisiness in these data

"""

# %% Field equity from specific match

"""

This uses the above processes but simplifies and speeds up to reduce computation time.

"""

#Extract data from first match
testMatchData = matchData[103930101]

#Set arbitrary distance to smooth equity within 
#(i.e. events within this distance considered in calculation)
smoothingDistance = 2

#Set dictionary to store data in
feData = {'xCoord': [], 'yCoord': [], 'eventLabel': [], 'fieldEquity': []}

#Extract unique events
matchEvents = list(testMatchData['eventLabel'].unique())

#Loop through events
for event in matchEvents:
    
    #Check for special cases
    
    #Centre passes
    if event == 'centrePass':
        #Simply calculate the centre pass FE as it's always at the same spot
        cpData = testMatchData.loc[testMatchData['eventLabel'] == 'centrePass',].reset_index(drop = True)
        nCP = len(cpData)
        nCP_score = np.sum([True if cpData.iloc[ii]['squadId'] == cpData.iloc[ii]['nextScoreSquadId'] else False for ii in cpData.index])
        cpFE = nCP_score / nCP
    elif event == 'goalMake':
        #Allocate the one-point FE for the score
        goalFE = 1
    ##### TODO: other special events...goal miss (skip?)...?
    
    else:
        
        #Extract matching event data
        eventData = testMatchData.loc[testMatchData['eventLabel'] == event,].reset_index(drop = True)
        
        #Loop through event datapoints
        for eventInd in eventData.index:
            
            #Get x and y coordinate (in metres) of current possession
            currPoint = np.array((eventData.iloc[eventInd]['xCoordMetres'], eventData.iloc[eventInd]['yCoordMetres']))
            
            #Get x and y coordinates (in metres) of all other points
            allPoints = np.array((eventData['xCoordMetres'], eventData['yCoordMetres'])).T
            
            #Calculate distances between points
            distances = np.linalg.norm(currPoint - allPoints, axis = 1)
            
            #Identify distances with smoothing value
            withinSmoothingDist = pd.Series(distances < smoothingDistance)
            
            #Extract the possessions within the smoothing distance
            feCalcData = eventData[withinSmoothingDist.values].reset_index(drop = True)
            
            #Calculate equity for current possession and append to dataset
            nextScoreN = np.sum([True if feCalcData.iloc[ii]['squadId'] == feCalcData.iloc[ii]['nextScoreSquadId'] else False for ii in feCalcData.index])
            feData['fieldEquity'].append(nextScoreN / len(feCalcData))
            feData['eventLabel'].append(event)
            feData['xCoord'].append(eventData.iloc[eventInd]['xCoord'])
            feData['yCoord'].append(eventData.iloc[eventInd]['yCoord'])
            
#Convert to dataframe for ease of use
feData_df = pd.DataFrame.from_dict(feData)

#Add a very small amount of random noise to values to avoid duplicates
#This shouldn't be a problem as it doesn't shift the points beyond the distances
#included in calculating the FE
feData_df['xCoord_noise'] = feData_df['xCoord'] + np.random.normal(0,0.1,len(feData_df))
feData_df['yCoord_noise'] = feData_df['yCoord'] + np.random.normal(0,0.1,len(feData_df))

#Below mapping to grid comes from: https://github.com/agilescientific/xlines/blob/master/notebooks/11_Gridding_map_data.ipynb

# #Plot the data in a scatter format to examine
# fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)
# ax.scatter(feData_df['xCoord_noise'],  feData_df['yCoord_noise'],
#            c = feData_df['fieldEquity'])

#We then map a grid for what we want to predict values over
#For now we'll do grid intervals of 1 coordinate steps
grid_x, grid_y = np.mgrid[0:100:1, 0:200:1]
# plt.figure(figsize=(5,8))
# plt.scatter(grid_x, grid_y, s = 1)

#Interpolate data using radial basis function

#Create the radial basis function from the data
rbfi = Rbf(feData_df['xCoord_noise'],  feData_df['yCoord_noise'], feData_df['fieldEquity'])

#Use the function to predict data on the uniform grid
Z = rbfi(grid_x, grid_y)
 
#Create contour plot of possession field equity

#Create figure and axis for court
fig, ax = plt.subplots(figsize = (5, 8), nrows = 1, ncols = 1)

#Set spacing
plt.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.9)

#Set axis limits to court boundaries
ax.set_xlim([0,100])
ax.set_ylim([0,200])

#Turn off axis ticks
ax.set_xticks([])
ax.set_yticks([])

#Add court lines
#Third lines
ax.plot([0,courtWidth_coord], [courtLength_coord/3, courtLength_coord/3],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
ax.plot([0,courtWidth_coord], [courtLength_coord/3*2, courtLength_coord/3*2],
        linestyle = '-', linewidth = 1.5, color = 'k',
        zorder = 1, clip_on = True)
#Centre circle (about 6% of court width)
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord/2), 0.06*courtWidth_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
#Shooting circles (about 16% of court length)
ax.add_patch(Circle((courtWidth_coord/2,0), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))
ax.add_patch(Circle((courtWidth_coord/2,courtLength_coord), 0.16*courtLength_coord, 
                    linestyle = '-', linewidth = 1.5, edgecolor = 'k', facecolor = 'none',
                    zorder = 1))

#Create labelled contours
CS = ax.contourf(grid_x, grid_y, Z, zorder = 2)
ax.clabel(CS, inline = True, fontsize = 10)           
    
    
    


# %% Field equity application

"""

TODO:
    > Consider walking through a game step by step and calculating change in equity
      at each point to examine player ratings potential...

"""

#Start by working out some general field equity values to map to certain events

#Centre passes (i.e. these always occur from the same location)
#Simply divide the number of all centre passes by those where the next team score
#comes from the team with the centre pass
cpData = allMatchData.loc[allMatchData['eventLabel'] == 'centrePass',].reset_index(drop = True)
nCP = len(cpData)
nCP_score = np.sum([True if cpData.iloc[ii]['squadId'] == cpData.iloc[ii]['nextScoreSquadId'] else False for ii in cpData.index])
cpFE = nCP_score / nCP











# %% ----- End of outputTests.py ----- %% #