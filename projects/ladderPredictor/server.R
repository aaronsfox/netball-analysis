#Load packages
library(shiny)
library(shinyWidgets)
library(shinythemes)
library(reactable)

function(input, output) {
  
  #Create dataframe with starting ladder
  #Columns for dataframe
  Team <- c("Thunderbirds", "Magpies", "GIANTS", "Vixens", "Swifts", "Firebirds", "Lightning", "Fever")
  P <- c(0,0,0,0,0,0,0,0)
  W <- c(0,0,0,0,0,0,0,0)
  D <- c(0,0,0,0,0,0,0,0)
  L <- c(0,0,0,0,0,0,0,0)
  GF <- c(0,0,0,0,0,0,0,0)
  GA <- c(0,0,0,0,0,0,0,0)
  Pts <- c(0,0,0,0,0,0,0,0)
  Per <- c(0,0,0,0,0,0,0,0)
  #Construct the dataframe
  ladderData <- data.frame(Team, P, W, D, L, GF, GA, Pts, Per)
  
  #Set colours for teams
  feverCol <- "#00953b"
  firebirdsCol <- "#4b2c69"
  giantsCol <- "#f57921"
  lightningCol <- "#fdb61c"
  magpiesCol <- "#494b4a"
  swiftsCol <- "#0082cd"
  thunderbirdsCol <- "#e54078"
  vixensCol <- "#00a68e"
  
  #Set list for generic game labels
  gameLabels <- c("G1", "G2", "G3", "G4")
  
  #Set list for remaining rounds
  roundLabels <- c("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14")
  
  #Set list for games within round
  matchUpLabels <- list(
    
    #Round 1
    list(c("Thunderbirds", "Magpies"), c("Swifts", "GIANTS"), c("Firebirds", "Vixens"), c("Fever", "Lightning")),
	
	#Round 2
    list(c("Swifts", "Vixens"), c("Lightning", "Firebirds"), c("Magpies", "Fever"), c("Thunderbirds", "GIANTS")),
	
	#Round 3
    list(c("Vixens", "GIANTS"), c("Swifts", "Magpies"), c("Firebirds", "Fever"), c("Thunderbirds", "Lightning")),
	
	#Round 4
    list(c("Vixens", "Fever"), c("GIANTS", "Firebirds"), c("Magpies", "Lightning"), c("Thunderbirds", "Swifts")),
	
	#Round 5
    list(c("Lightning", "Vixens"), c("GIANTS", "Magpies"), c("Fever", "Swifts"), c("Firebirds", "Thunderbirds")),
	
	#Round 6
    list(c("Swifts", "Lightning"), c("Vixens", "Thunderbirds"), c("Firebirds", "Magpies"), c("GIANTS", "Fever")),
	
	#Round 7
    list(c("Firebirds", "Swifts"), c("Thunderbirds", "Fever"), c("Lightning", "GIANTS"), c("Vixens", "Magpies")),
	
	#Round 8
    list(c("Vixens", "Firebirds"), c("Lightning", "Thunderbirds"), c("Fever", "Magpies"), c("GIANTS", "Swifts")),
	
	#Round 9
    list(c("Lightning", "Fever"), c("GIANTS", "Vixens"), c("Magpies", "Firebirds"), c("Swifts", "Thunderbirds")),
	
	#Round 10
    list(c("Lightning", "Swifts"), c("Fever", "Vixens"), c("Magpies", "GIANTS"), c("Thunderbirds", "Firebirds")),
    
    #Round 11
    list(c("Firebirds", "Lightning"), c("Vixens", "Swifts"), c("Fever", "GIANTS"), c("Magpies", "Thunderbirds")),
    
    #Round 12
    list(c("Magpies", "Swifts"), c("Fever", "Firebirds"), c("Vixens", "Lightning"), c("GIANTS", "Thunderbirds")),
    
    #Round 13
    list(c("Firebirds", "GIANTS"), c("Thunderbirds", "Vixens"), c("Swifts", "Fever"), c("Lightning", "Magpies")),
    
    #Round 14
    list(c("GIANTS", "Lightning"), c("Fever", "Thunderbirds"), c("Swifts", "Firebirds"), c("Magpies", "Vixens"))
    
  )
  
  #Set match-up labels to round names
  names(matchUpLabels) <- roundLabels
  
  #Create the round tabs and game tabs within these
  
  #Create empty list to store tabs in
  matchTabsetList <- list()
  
  for (rr in 1:length(roundLabels)) {
    
    #Append a list within the broader matchup list for the current round
    #Also rename it to current round
    matchTabsetList[[length(matchTabsetList)+1]] <- list()
    names(matchTabsetList)[length(matchTabsetList)] <- roundLabels[rr]
    
    #Loop through the games within a round
    for (gg in 1:length(matchUpLabels[rr][[1]])) {
      
      #Create the tab panel for current game and append to round list
      matchTabsetList[rr][[1]][[length(matchTabsetList[rr][[1]])+1]] <- tabPanel(gameLabels[gg],
                                                                                 #Header for game
                                                                                 h4(paste(matchUpLabels[rr][[1]][[gg]][1],matchUpLabels[rr][[1]][[gg]][2], sep = ' vs. ')), 
                                                                                 #Radio button for including game
                                                                                 radioButtons(paste(roundLabels[rr],gameLabels[gg], sep = "_"),
                                                                                              "Include?", c("Yes", "No"), selected = "No"),
                                                                                 #Slider input for the two teams
                                                                                 #Team 1
                                                                                 sliderInput(paste(matchUpLabels[rr][[1]][[gg]][1], roundLabels[rr], sep = ""),
                                                                                             paste(matchUpLabels[rr][[1]][[gg]][1], "Score", sep = " "),
                                                                                             value = 0, min = 0, max = 100),
                                                                                 #Team 2
                                                                                 sliderInput(paste(matchUpLabels[rr][[1]][[gg]][2], roundLabels[rr], sep = ""),
                                                                                             paste(matchUpLabels[rr][[1]][[gg]][2], "Score", sep = " "),
                                                                                             value = 0, min = 0, max = 100)
      )
    }
  }
  
  
  #Current ladder table output
  output$currentLadderTable <- renderReactable({
    
    reactable(
      
      #Set data
      ladderData,
      
      #Set pagination
      pagination = FALSE,
      
      #Set parameters
      highlight = TRUE,
      searchable = FALSE,
      
      #Set the default sort column
      defaultSorted = c("Pts","Per"),
      defaultSortOrder = "desc",
      
      #Set row style for finalists
      rowStyle = function(index) {
        if (index == 4) list(borderBottom = "2px solid #555")
      },
      
      #Create a list of columns
      columns = list(
        
        #Create the team column
        Team = colDef(name = "Team",
                      sortable = FALSE,
                      style = list(fontSize = "12px", fontWeight = "bold"),
                      headerStyle = list(fontWeight = 700),
                      cell = function(value) {
                        image <- img(src = sprintf("Images/%s.png", value), height = "30px", alt = value)
                        tagList(
                          div(style = list(display = "inline-block", width = "30px"), image)
                        )
                      }
        ),
        
        #Create games played column
        P = colDef(
          name = "P",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create wins column
        W = colDef(
          name = "W",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create draws column
        D = colDef(
          name = "D",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create losses column
        L = colDef(
          name = "L",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create goals for column
        GF = colDef(
          name = "GF",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create goals against column
        GA = colDef(
          name = "GA",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create points column
        Pts = colDef(
          name = "Pts",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create percentage column
        Per = colDef(
          name = "Per",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
          format = colFormat(digits = 2)
        )
        
      ),
      
      #Set reactable options
      showSortIcon = FALSE,
      borderless = TRUE
      
    )
    
  })
  
  
  
  #Generate the predicted ladder dataframe upon clicking the action button
  predictedLadder <- eventReactive(input$runPrediction, {
    
    #Create a new copy of the starting ladder to alter
    ladderPredict <- data.frame(Team, P, W, D, L, GF, GA, Pts, Per)
    
    #Loop through rounds
    for (rr in 1:length(roundLabels)) {
      
      #Loop through games within round
      for (gg in 1:length(matchUpLabels[rr][[1]])) {
        
        #Get the current games radio button value for inclusion
        useGame <- input[[paste(roundLabels[rr],gameLabels[gg], sep = "_")]]
        
        if (useGame == "Yes") {
          
          #Get the two team names
          team1 <- matchUpLabels[rr][[1]][[gg]][1]
          team2 <- matchUpLabels[rr][[1]][[gg]][2]
          
          #Get row indexes for two teams
          teamInd1 <- which(ladderPredict$Team == team1)
          teamInd2 <- which(ladderPredict$Team == team2)
          
          #Get the two teams slider values
          score1 <- input[[paste(matchUpLabels[rr][[1]][[gg]][1], roundLabels[rr], sep = "")]]
          score2 <- input[[paste(matchUpLabels[rr][[1]][[gg]][2], roundLabels[rr], sep = "")]]
          
          #Add to each teams played column
          ladderPredict$P[teamInd1] <- ladderPredict$P[teamInd1] + 1
          ladderPredict$P[teamInd2] <- ladderPredict$P[teamInd2] + 1
          
          #Add goals for and against for the two teams
          #Goals for
          ladderPredict$GF[teamInd1] <- ladderPredict$GF[teamInd1] + score1
          ladderPredict$GF[teamInd2] <- ladderPredict$GF[teamInd2] + score2
          #Goals against
          ladderPredict$GA[teamInd1] <- ladderPredict$GA[teamInd1] + score2
          ladderPredict$GA[teamInd2] <- ladderPredict$GA[teamInd2] + score1
          
          #Add to points based on win vs. loss vs. draw
          if (score1 > score2) {
            #Give team1 the win + team2 the loss
            ladderPredict$Pts[teamInd1] <- ladderPredict$Pts[teamInd1] + 4
            ladderPredict$W[teamInd1] <- ladderPredict$W[teamInd1] + 1
            ladderPredict$L[teamInd2] <- ladderPredict$L[teamInd2] + 1
          } else if (score2 > score1) {
            #Give team2 the win + team1 the loss
            ladderPredict$Pts[teamInd2] <- ladderPredict$Pts[teamInd2] + 4
            ladderPredict$W[teamInd2] <- ladderPredict$W[teamInd2] + 1
            ladderPredict$L[teamInd1] <- ladderPredict$L[teamInd1] + 1
          } else if (score1 == score2) {
            #Share the points for a draw
            ladderPredict$Pts[teamInd1] <- ladderPredict$Pts[teamInd1] + 2
            ladderPredict$Pts[teamInd2] <- ladderPredict$Pts[teamInd2] + 2
            ladderPredict$D[teamInd1] <- ladderPredict$D[teamInd1] + 1
            ladderPredict$D[teamInd2] <- ladderPredict$D[teamInd2] + 1
          }
          
        } #end useGame if statement
        
      } #end games loop
      
    } #end rounds loop
    
    #Recalculate percentage
    ladderPredict$Per <- round(ladderPredict$GF / ladderPredict$GA * 100, 2)
    
    #Re-sort dataframe by total points and percentage
    ladderPredict <- ladderPredict[with(ladderPredict, order(-Pts, -Per)), ]
    
    return(ladderPredict)
    
  })
  
  
  
  #Render predicted ladder
  output$predictedLadderTable <- renderReactable({
    
    reactable(
      
      #Set data
      #Grab it from the predict ladder function
      predictedLadder(),
      
      #Set pagination
      pagination = FALSE,
      
      #Set parameters
      highlight = TRUE,
      searchable = FALSE,
      
      #Set the default sort column
      defaultSorted = c("Pts","Per"),
      defaultSortOrder = "desc",
      
      #Set row style for finalists
      rowStyle = function(index) {
        if (index == 4) list(borderBottom = "2px solid #555")
      },
      
      #Create a list of columns
      columns = list(
        
        #Create the team column
        Team = colDef(name = "Team",
                      sortable = FALSE,
                      style = list(fontSize = "12px", fontWeight = "bold"),
                      headerStyle = list(fontWeight = 700),
                      cell = function(value) {
                        image <- img(src = sprintf("Images/%s.png", value), height = "30px", alt = value)
                        tagList(
                          div(style = list(display = "inline-block", width = "30px"), image)
                        )
                      }
        ),
        
        #Create games played column
        P = colDef(
          name = "P",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create wins column
        W = colDef(
          name = "W",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create draws column
        D = colDef(
          name = "D",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create losses column
        L = colDef(
          name = "L",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create goals for column
        GF = colDef(
          name = "GF",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create goals against column
        GA = colDef(
          name = "GA",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create points column
        Pts = colDef(
          name = "Pts",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
        ),
        
        #Create percentage column
        Per = colDef(
          name = "Per",
          sortable = FALSE,
          defaultSortOrder = "desc",
          align = "center",
          class = "cell number",
          headerStyle = list(fontWeight = 700),
          format = colFormat(digits = 2)
        )
        
      ),
      
      #Set reactable options
      showSortIcon = FALSE,
      borderless = TRUE
      
    )
    
  })
  
  
}