# This code is used to grab match data from the Champion Data match centre

# %% Set-up SuperNetballR package -----
# This section only needs to be run to install the necessary package
# library(remotes) 
# remotes::install_github("SteveLane/superNetballR")

# %% Load appropriate packages -----
library(dplyr)
library(superNetballR)
library(jsonlite)
library(here)

# %% Create list housing competition details and ID's -----
compDetails <- list(
  
  year = c(
  #ANZC+SSN (TODO: add SSN 2023)
  rep(c(2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
        2017, 2018, 2019, 2020, 2021, 2022), each = 2),
  #TGC
  rep(c(2022), each = 3),
  rep(c(2023), each = 3),
  #ANC
  rep(c(2022), each = 2),
  #Internationals
  c(2014, 2014, 2015, 2015, 2016, 2016, 2016, 2017, 2017, 2017, 2018, 2018, 2018,
    2019, 2019, 2021, 2022, 2022, 2022)),
  
  league = c(rep("ANZC", each = 16),
             rep("SSN", each = 12),
             rep("TGC", each = 6),
             rep("ANC", each = 2),
             #Internationals (more sporadic)
             "CONCUP", "ENG-SERIES", "TTU19", "CONCUP", "ENG-SERIES", "CONCUP", "SUPER-SERIES",
             "QUAD", "QUAD", "CONCUP", "QUAD", "CONCUP", "QUAD", "QUAD", "CONCUP", "CONCUP",
             "QUAD", "CONCUP", "MENS-TTC"),
  
  id = c(
    #ANZC
    8005, 8006, 8012, 8013, 8018, 8019, 8028, 8029, 8035, 8036, 9084, 9085, 9563, 9564, 9818, 9819,
    #SSN
    10083, 10084, 10393, 10394, 10724, 10725, 11108, 11109, 11391, 11392, 11665, 11666,
    #TGC
    11706, 11707, 11708,
    12125, 12205, 12126,
    #ANC
    11915, 11916,
    #Internationals
    9315, 9355, 9663, 9644, 9843, 9953, 9973,
    10200, 10293, 10294, 10423, 10564, 10565, 10734, 10985, 11315,
    11695, 11946, 11995)
  )

# %% Loop through competition IDs and extract data -----
for (compInd in 1:lengths(compDetails)['id']) {
  
  #Get the competition details
  compYear <- compDetails[["year"]][compInd]
  compLeague <- compDetails[["league"]][compInd]
  compId <- compDetails[["id"]][compInd]

  #Set the starting round value
  
  #Loop through rounds (set to irresponsibly large value but breaks used)
  for (getRound in 1:25) {
    
    #Loop through matches (set to irresponsibly large value but breaks used)
    for (getMatch in 1:25) {
      
      #Download match data with current parameters
      matchData <- downloadMatch(compId, getRound, getMatch)
      
      #Check if match data present
      if (is.null(matchData)) {
        break
      }
      #Write data
      write_json(matchData, paste0(here(),"/data/matchCentre/raw/",compYear,"_",compLeague,"_",compId,"_r",getRound,"_g",getMatch,".json"))

    } #end of for getMatch loop
    
  } #end of for getRound loop
  
} #end of for compInd loop

# %% Option to extract individual competition, year, league and round

#Set the competition details
compYear <- 2023
compLeague <- "SSN"
compId <- 12045

#Set the round to get
getRound <- 8

#Loop through matches (set to irresponsibly large value but breaks used)
for (getMatch in 1:25) {
  
  #Download match data with current parameters
  matchData <- downloadMatch(compId, getRound, getMatch)
  
  #Check if match data present
  if (is.null(matchData)) {
    break
  }
  #Write data
  write_json(matchData, paste0(here(),"/data/matchCentre/raw/",compYear,"_",compLeague,"_",compId,"_r",getRound,"_g",getMatch,".json"))
  
} #end of for getMatch loop


# %% ----- end of matchCentre_matchGrabber.R -----