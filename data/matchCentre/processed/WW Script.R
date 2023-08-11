# LOAD PACKAGES ------
install.packages(c("tidyverse", "pacman", "stringr", "here", "rjson", "gtsummary", "pander", "ggsignif", "broom", "manova", "ggpubr", "dplyr"))
library("tidyverse")
library("pacman")
library("here")
library("rjson")
library("gtsummary")
library("pander")
library("ggsignif")
library("broom")
library("manova")
library("ggpubr")
library("dplyr")

# SET THE DIRECTORY PATH -----
directory_path <- here()

# SET THE WORKING DIRECTORY
setwd <- here()

# FUNCTION TO PULL FILES INTO A DATA FRAME -----
build_data_frame <- function(file_string) {
  # Find files matching the specified string
  file_paths <- list.files(directory_path, pattern = file_string, full.names = T, recursive = T)
  
  # Read and store data frames into a single set
  data_frames <- list()
  
  # Loop through each file path
  for (file_path in file_paths) {
    if (str_detect(file_path, ".csv$")) {
      # Read the CSV file into a data frame
      data <- read.csv(file_path)
    } else if (str_detect(file_path, ".json")) {
      # Try to read the JSON file and handle parsing errors
      json_data <- tryCatch(
        {
          # Read the JSON file into a data frame
          json <- readLines(file_path)
          data <- fromJSON(paste(json, collapse = ""))
          data <- as.data.frame(data)
        },
        error = function(e) {
          message(paste("Error reading JSON file:", file_path))
          return(NULL)
        }
      )
      
      # Check if JSON parsing was successful
      if (is.null(json_data)) {
        next
      }
    } else {
      # Skip files that are not CSV or JSON
      next
    }
    
    # Extract the matchID, year, competition, round, and game from the file name
    matchID <- str_extract(file_path, "\\d{8}(?=_\\d{4}_)")
    year <- str_extract(file_path, "(?<=_)\\d{4}(?=_)")
    competition <- str_extract(file_path, "(?<=_)[A-Z]{3,4}(?=_)")
    round <- str_extract(file_path, "(?<=_)r\\d{1,2}(?=_)")
    game <- str_extract(file_path, "(?<=_)g\\d{1,2}(?=\\.)")
    
    # Remove the 'r' and 'g' from round and game
    round <- str_remove(round, "r")
    game <- str_remove(game, "g")

    # Add the extracted components as new columns in the data frame
    data <- dplyr::mutate(data, matchID = matchID, year = year, competition = competition, round = round, game = game)
    
    # Store the data frame in the list
    data_frames[[file_path]] <- data
  }
  
  # Combine into a single data frame
  combined_data <- dplyr::bind_rows(data_frames)
  
  # Assign the data frame to a dynamically generated name
  assign(paste0("data_", file_string), combined_data, envir = .GlobalEnv)
  
  # Return the data frame name
  return(paste0("data_", file_string))
}

# BUILD DATA FRAMES -----
  # Primary Dataframes ----
    build_data_frame <- { 
      data <- build_data_frame("lineUps")
      data <- build_data_frame("minutesPlayed")
      data <- build_data_frame("matchInfo")
      data <- build_data_frame("playerList")
      data <- build_data_frame("playerPeriodStats")
      data <- build_data_frame("playerStats")
      data <- build_data_frame("scoreFlow")
      data <- build_data_frame("substitutions")
      data <- build_data_frame("teamPeriodStats")
      data <- build_data_frame("teamStats")
  }
  # Filter data_substitutions to a structured observational df -----
  data_observed_substitutions <- data_substitutions %>%
    filter(startingTime != 0) %>%
    group_by(squadId, matchId) %>%
    summarize(substitution_count = n(),
              year = first(year),
              competition = first(competition),
              supershot = first(supershot),
              timeout = first(timeouts),
              round = first(round),
              game = first(game),
              substitution = first(substitutions),
              matchtype = first(matchType))   
  
# AMEND DATA FRAMES -----
  # Add matchtype (H,F) and rule change ----
    amend_all_data_frames <- function() {
          distinct_matchInfo <- data_matchInfo %>% distinct(matchId, .keep_all = TRUE)
          
          data_frames <- list(
            data_lineUps, data_minutesPlayed, data_playerList, data_playerPeriodStats,
            data_playerStats, data_scoreFlow, data_substitutions, data_teamPeriodStats,
            data_teamStats
          )
          
          data_frames <- lapply(data_frames, function(df) {
            df <- left_join(df, distinct_matchInfo %>% select(matchId, matchType), by = "matchId")
            
            # Add new column 'supershot' based on 'year' column
            df$supershot <- ifelse(df$year %in% c(2020, 2021, 2022, 2023), "After", "Before")
            
            # Add new column 'timeouts' based on 'year' column
            df$timeouts <- ifelse(df$year %in% c(2017, 2018, 2019, 2020, 2021, 2022, 2023), "After", "Before")
            
            # Add new column 'substitutions' based on 'year' column
            df$substitutions <- ifelse(df$year %in% c(2020, 2021, 2022, 2023), "After", "Before")
            
            return(df)
          })
          
          names(data_frames) <- c("data_lineUps", "data_minutesPlayed", "data_playerList",
                                  "data_playerPeriodStats", "data_playerStats", "data_scoreFlow",
                                  "data_substitutions", "data_teamPeriodStats", "data_teamStats")
          
          list2env(data_frames, envir = .GlobalEnv)
        }
      
    amend_all_data_frames()
    
  # Collingwood naming convention ----
    data_matchInfo <- data_matchInfo %>%
      mutate(
        homeSquadName = case_when(
          homeSquadName == "Magpies Netball" ~ "Collingwood Magpies",
          TRUE ~ homeSquadName
        ),
        awaySquadName = case_when(
          awaySquadName == "Magpies Netball" ~ "Collingwood Magpies",
          TRUE ~ awaySquadName
        )
      )
  
  # Add squadNames to data frames ----
    data_lineUps$squadName <- SSN_SquadNames$squadName[match(data_lineUps$squadId, SSN_SquadNames$squadId)]
    data_lineUps$oppsquadName <- SSN_SquadNames$squadName[match(data_lineUps$oppSquadId, SSN_SquadNames$squadId)]
  
    data_minutesPlayed$squadName <- SSN_SquadNames$squadName[match(data_minutesPlayed$squadId, SSN_SquadNames$squadId)]
    data_minutesPlayed$oppsquadName <- SSN_SquadNames$squadName[match(data_minutesPlayed$oppSquadId, SSN_SquadNames$squadId)]
    
    data_observed_substitutions$squadName <- SSN_SquadNames$squadName[match(data_observed_substitutions$squadId, SSN_SquadNames$squadId)]
    
    data_playerPeriodStats$squadName <- SSN_SquadNames$squadName[match(data_playerPeriodStats$squadId, SSN_SquadNames$squadId)]
    data_playerPeriodStats$oppsquadName <- SSN_SquadNames$squadName[match(data_playerPeriodStats$oppSquadId, SSN_SquadNames$squadId)]
  
    data_playerStats$squadName <- SSN_SquadNames$squadName[match(data_playerStats$squadId, SSN_SquadNames$squadId)]
    data_playerStats$oppsquadName <- SSN_SquadNames$squadName[match(data_playerStats$oppSquadId, SSN_SquadNames$squadId)]
    
    data_scoreFlow$squadName <- SSN_SquadNames$squadName[match(data_scoreFlow$squadId, SSN_SquadNames$squadId)]
    data_scoreFlow$oppsquadName <- SSN_SquadNames$squadName[match(data_scoreFlow$oppSquadId, SSN_SquadNames$squadId)]
    
    data_substitutions$squadName <- SSN_SquadNames$squadName[match(data_substitutions$squadId, SSN_SquadNames$squadId)]
    data_substitutions$oppsquadName <- SSN_SquadNames$squadName[match(data_substitutions$oppSquadId, SSN_SquadNames$squadId)]
    
    data_teamPeriodStats$squadName <- SSN_SquadNames$squadName[match(data_teamPeriodStats$squadId, SSN_SquadNames$squadId)]
    data_teamPeriodStats$oppsquadName <- SSN_SquadNames$squadName[match(data_teamPeriodStats$oppSquadId, SSN_SquadNames$squadId)]
    
    data_teamStats$squadName <- SSN_SquadNames$squadName[match(data_teamStats$squadId, SSN_SquadNames$squadId)]
    data_teamStats$oppsquadName <- SSN_SquadNames$squadName[match(data_teamStats$oppSquadId, SSN_SquadNames$squadId)]
    
  # Add teams current standing (W,L, D) ----
    data_scoreFlow <- data_scoreFlow %>%
      mutate(standing = ifelse(scoreDifferential < 0, "L",
                               ifelse(scoreDifferential > 0, "W", "D")))
    
    data_teamStats <- data_teamStats %>%
      mutate(standing = ifelse(margin < 0, "L",
                               ifelse(margin > 0, "W", "D")))
    
    data_teamPeriodStats <- data_teamPeriodStats %>%
      mutate(standing = ifelse(margin < 0, "L",
                               ifelse(margin > 0, "W", "D")))
  
  # Percentage, accuracy, and attempts, turnovers ----
    # Clean  df so the 'points' and 'goals' column is produced across all observations
      data_teamStats <- data_teamStats %>%
        mutate(points = ifelse(is.na(points), goals, points))
      
      data_teamPeriodStats <- data_teamPeriodStats %>%

    # Clean goals to be goal1 if blank
      data_teamStats <- data_teamStats %>%
        mutate(goal1 = ifelse(is.na(goal1), goals, goal1))
      
      data_teamPeriodStats <- data_teamPeriodStats %>%
        mutate(goal1 = ifelse(is.na(goal1), goals, goal1))
    
    # Clean goal_attempts to be goal1_attempts if blank
      data_teamStats <- data_teamStats %>%
        mutate(attempt1 = ifelse(is.na(attempt1), goalAttempts, attempt1))
      
      data_teamPeriodStats <- data_teamPeriodStats %>%
        mutate(attempt1 = ifelse(is.na(attempts1), goalAttempts, attempts1))
    
    # Add supershot goals missed
      data_teamStats <- data_teamStats %>%
        mutate(goal2_missed = attempt2 - goal2)
    
      data_teamPeriodStats <- data_teamPeriodStats %>%
        mutate(goal2_missed = attempts2 - goal2)
        
    # Add goals accuracy percentage
      data_teamStats <- data_teamStats %>%
        mutate(goal_accuracy = (goals / goalAttempts) * 100)
      
      data_teamPeriodStats <- data_teamPeriodStats %>%
        mutate(goal_accuracy = (goals / goalAttempts) * 100)
      
    # Add goal1 accuracy percentage
      data_teamStats <- data_teamStats %>%
        mutate(goal1_accuracy = (goal1 / attempt1) * 100)
      
      data_teamPeriodStats <- data_teamPeriodStats %>%
        mutate(goal1_accuracy = (goal1 / attempt1) * 100)
    
    # Add supershot accuracy percentage
      data_teamStats <- data_teamStats %>%
        mutate(goal2_accuracy = (goal2 / attempt2) * 100)
      
      data_teamPeriodStats <- data_teamPeriodStats %>%
        mutate(goal2_accuracy = (goal2 / attempts2) * 100)

    # Turnovers 
      data_teamStats <- data_teamStats %>%
        mutate(turnovers = ifelse(is.na(turnovers), generalPlayTurnovers + missedGoalTurnover, turnovers))
      
    # defensiveRebounds
      data_teamStats <- data_teamStats %>%
        mutate(defensiveRebounds = ifelse(is.na(defensiveRebounds), rebounds - offensiveRebounds, defensiveRebounds))

      data_teamPeriodStats <- data_teamPeriodStats %>%
        mutate(defensiveRebounds = ifelse(is.na(defensiveRebounds), rebounds - offensiveRebounds, defensiveRebounds))
      
  # Add margin to team stats and period stats ----
  data_teamStats <- data_teamStats %>%
    group_by(matchId) %>%
    mutate(margin = points - lag(points),
           opppoints = coalesce(lag(points), lead(points))) %>%
    mutate(margin = points - opppoints) %>%
    ungroup()
  
  data_teamPeriodStats <- data_teamPeriodStats %>%
    group_by(matchId, period) %>%
    mutate(margin = points - lag(points),
           opppoints = coalesce(lag(points), lead(points))) %>%
    mutate(margin = points - opppoints) %>%
    ungroup()
  
  view(data_teamStats %>% select(squadName, points, supershot, margin, standing))
  view(data_teamPeriodStats %>% select(squadName, points, supershot, margin, standing))
  
# SSN SQUAD FILTERING AND LADDER CREATION -----
  # Squad Values
  SSN_Squads <- c(8118, 804, 801, 807, 8119, 806, 8117, 810)
  
  SSN_SquadNames <- data_matchInfo %>%
    select(homeSquadId, homeSquadName) %>%
    filter(homeSquadId %in% SSN_Squads) %>%
    rename(squadId = homeSquadId,
           squadName = homeSquadName) %>%
    unique()

  create_ladders <- function(){
  # 2017 ladder
    SSN_2017_ladder <- data.frame(
      Team = c(
        "Melbourne Vixens",
        "Sunshine Coast Lightning",
        "Giants Netball",
        "Collingwood Magpies",
        "Queensland Firebirds",
        "New South Wales Swifts",
        "West Coast Fever",
        "Adelaide Thunderbirds"
      ),
      W = c(11, 11, 10, 9, 7, 3, 2, 1),
      D = c(1, 1, 0, 0, 1, 1, 0, 0),
      L = c(2, 2, 4, 5, 6, 10, 12, 13),
      GF = c(874, 808, 773, 770, 778, 726, 670, 648),
      GA = c(774, 726, 728, 730, 756, 792, 779, 792),
      Perc = c(118, 111, 106, 106, 103, 92, 86, 82),
      PTS = c(23, 23, 20, 18, 15, 7, 4, 2),
      Finish = c("","Premiers","Runner Up","","","","","")
    )
  
  # 2018 ladder
    SSN_2018_ladder <- data.frame(
      Pos = c(1, 2, 3, 4, 5, 6, 7, 8),
      Team = c(
        "Giants Netball",
        "West Coast Fever",
        "Queensland Firebirds",
        "Sunshine Coast Lightning",
        "Melbourne Vixens",
        "New South Wales Swifts",
        "Collingwood Magpies",
        "Adelaide Thunderbirds"
      ),
      P = c(14, 14, 14, 14, 14, 14, 14, 14),
      W = c(10, 10, 9, 8, 8, 6, 3, 0),
      D = c(1, 0, 0, 1, 0, 1, 1, 0),
      L = c(3, 4, 5, 5, 6, 7, 10, 14),
      GF = c(841, 912, 858, 809, 855, 814, 801, 673),
      GA = c(776, 851, 751, 752, 814, 816, 858, 945),
      Perc = c(108.4, 107.2, 114.2, 107.6, 105.0, 99.8, 93.4, 71.2),
      PTS = c(76, 71, 69, 69, 59, 48, 39, 4),
      Finish = c("","Runner Up","","Premiers","","","","")
    )
  
  # 2019 ladder
    SSN_2019_ladder <- data.frame(
      Pos = c(1, 2, 3, 4, 5, 6, 7, 8),
      Team = c(
        "Sunshine Coast Lightning",
        "New South Wales Swifts",
        "Melbourne Vixens",
        "Collingwood Magpies",
        "Giants Netball",
        "West Coast Fever",
        "Adelaide Thunderbirds",
        "Queensland Firebirds"
      ),
      P = c(14, 14, 14, 14, 14, 14, 14, 14),
      W = c(12, 10, 8, 7, 7, 2, 3, 1),
      D = c(0, 1, 1, 2, 1, 3, 2, 2),
      L = c(2, 3, 5, 5, 6, 9, 9, 11),
      GF = c(855, 845, 836, 788, 834, 821, 708, 815),
      GA = c(759, 755, 775, 771, 821, 904, 803, 914),
      Perc = c(112.65, 111.92, 107.87, 102.20, 101.58, 90.82, 88.17, 89.17),
      PTS = c(81, 78, 63, 59, 59, 33, 30, 26),
      Finish = c("Runner Up","Premiers","","","","","","")
    )
  
  # 2020 ladder
    SSN_2020_Ladder <- data.frame(
      Pos = c(1, 2, 3, 4, 5, 6, 7, 8),
      Team = c(
        "Queensland Firebirds",
        "Melbourne Vixens",
        "West Coast Fever",
        "New South Wales Swifts",
        "Sunshine Coast Lightning",
        "Giants Netball",
        "Adelaide Thunderbirds",
        "Collingwood Magpies"
      ),
      P = c(14, 14, 14, 14, 14, 14, 14, 14),
      W = c(11, 9, 8, 8, 6, 5, 5, 1),
      D = c(1, 0, 1, 1, 1, 2, 0, 0),
      L = c(2, 5, 5, 5, 7, 7, 9, 13),
      GF = c(870, 821, 964, 898, 851, 885, 769, 770),
      GA = c(769, 824, 897, 885, 893, 891, 797, 872),
      Perc = c(113.33, 99.64, 107.46, 101.46, 95.29, 99.32, 96.48, 88.30),
      PTS = c(46, 36, 34, 34, 26, 24, 20, 4),
      Finish = c("","Premiers","Runner Up","","","","","")
    )
  
  # 2021 Ladder
    SSN_2021_Ladder <- data.frame(
      Pos = c(1, 2, 3, 4, 5, 6, 7, 8),
      Team = c(
        "Giants Netball",
        "New South Wales Swifts",
        "West Coast Fever",
        "Sunshine Coast Lightning",
        "Queensland Firebirds",
        "Collingwood Magpies",
        "Adelaide Thunderbirds",
        "Melbourne Vixens"
      ),
      P = 14,
      W = c(9, 9, 11, 8, 6, 6, 5, 2),
      D = c(0, 0, 0, 0, 0, 0, 0, 0),
      L = c(5, 5, 3, 6, 8, 8, 9, 12),
      GF = c(853, 853, 976, 825, 880, 829, 764, 718),
      GA = c(797, 808, 835, 834, 873, 882, 835, 834),
      Perc = c(107.03, 105.57, 116.89, 98.92, 100.8, 93.99, 91.5, 86.09),
      PTS = c(36, 36, 32, 32, 24, 24, 20, 8),
      Finish = c("Runner Up","Premiers","","","","","","")
    )
    
  # 2022 Ladder
    SSN_2022_Ladder <- data.frame(
      Pos = c(1, 2, 3, 4, 5, 6, 7, 8),
      Team = c(
        "Melbourne Vixens",
        "West Coast Fever",
        "Giants Netball",
        "Collingwood Magpies",
        "New South Wales Swifts",
        "Queensland Firebirds",
        "Adelaide Thunderbirds",
        "Sunshine Coast Lightning"
      ),
      P = c(14, 14, 14, 14, 14, 14, 14, 14),
      W = c(12, 10, 8, 6, 6, 5, 5, 4),
      D = c(0, 0, 0, 0, 0, 0, 0, 0),
      L = c(2, 4, 6, 8, 8, 9, 9, 10),
      GF = c(865, 1011, 895, 880, 816, 932, 724, 865),
      GA = c(824, 925, 886, 902, 838, 928, 747, 938),
      Perc = c(104.98, 109.30, 101.02, 97.56, 97.37, 100.43, 96.92, 92.22),
      PTS = c(48, 40, 32, 24, 24, 20, 20, 16),
      Finish = c("Runner Up","Premiers","","","","","","")
    )
  }
  
  create_ladders()

# SET THEME -----
    # Set Theme
    theme_set(theme_minimal())
    
    theme_update(
      axis.text.x = element_text(angle = 45, hjust = 1, face = "bold", margin = margin(b = 10)), 
      axis.text.y = element_text(),
      axis.title.x = element_text(size = 10, face = "bold", margin = margin(t = 10)),
      axis.title.y = element_text(size = 10, face = "bold", angle = 90, margin = margin(r = 10)),
      plot.title = element_text(size = 14, face = "bold", hjust = 0.5, margin = margin(b = 20)),
      legend.title = element_text(size = 10, face = "bold")
    )   


# RESEARCH FUNCTIONS ----
    # Summary statistics ----
      # data_teamStats ----
        summary_teamStats <- function(var) {
          dataf <- data_teamStats %>%
            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
          var <- ensym(var)
          
          format_mean_sd <- function(mean_val, sd_val) {
            formatted_mean <- sprintf("%.2f", mean_val)
            formatted_sd <- sprintf("± %.2f", sd_val)
            return(paste(formatted_mean, formatted_sd))
          }
          
          format_se <- function(se_val) {
            formatted_se <- sprintf("%.2f", se_val)
            return(formatted_se)
          }
          
          summary_0 <- dataf %>%
            summarise(Total = sum(!!var, na.rm = TRUE),
                      Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                      SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))        
          
          summary_1 <- dataf %>%
            group_by(supershot) %>%
            summarise(Total = sum(!!var, na.rm = TRUE),
                      Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                      SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))
          
          summary_2 <- dataf %>%
            group_by(squadName) %>%
            summarise(Total = sum(!!var, na.rm = TRUE),
                      Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                      SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))
          
          summary_3 <- dataf %>%
            group_by(year) %>%
            summarise(Total = sum(!!var, na.rm = TRUE),
                      Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                      SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n()))) %>%
            filter(Total != 0)
          
          summary_4 <- dataf %>%
            group_by(squadName, supershot) %>%
            summarise(Total = sum(!!var, na.rm = TRUE),
                      Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                      SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))
          
          summary_5 <- dataf %>%
            group_by(squadName, year) %>%
            summarise(Total = sum(!!var, na.rm = TRUE),
                      Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                      SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n()))) %>%
            filter(Total != 0)
          
          view(summary_0)
          view(summary_1)
          view(summary_2)
          view(summary_3)
          view(summary_4)
          view(summary_5)
        }
    
      # data_teamPeriodStats ----
      summary_teamPeriodsStats <- function(var) {
        dataf <- data_teamPeriodStats %>%
          filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, period <= 4)
        var <- ensym(var)
        
        format_mean_sd <- function(mean_val, sd_val) {
          formatted_mean <- sprintf("%.2f", mean_val)
          formatted_sd <- sprintf("± %.2f", sd_val)
          return(paste(formatted_mean, formatted_sd))
        }
        
        format_se <- function(se_val) {
          formatted_se <- sprintf("%.2f", se_val)
          return(formatted_se)
        }
        
        summary_0 <- dataf %>%
          summarise(Total = sum(!!var, na.rm = TRUE),
                    Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                    SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))        
        
        summary_1 <- dataf %>%
          group_by(period) %>%
          summarise(Total = sum(!!var, na.rm = TRUE),
                    Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                    SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))
        
        summary_2 <- dataf %>%
          group_by(period, squadName) %>%
          summarise(Total = sum(!!var, na.rm = TRUE),
                    Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                    SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))
        
        summary_3 <- dataf %>%
          group_by(period, supershot) %>%
          summarise(Total = sum(!!var, na.rm = TRUE),
                    Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                    SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n()))) %>%
          filter(Total != 0)
        
        summary_4 <- dataf %>%
          group_by(period, year) %>%
          summarise(Total = sum(!!var, na.rm = TRUE),
                    Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                    SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n())))
        
        summary_5 <- dataf %>%
          group_by(period, squadName, year) %>%
          summarise(Total = sum(!!var, na.rm = TRUE),
                    Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                    SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n()))) %>%
          filter(Total != 0)
        
        summary_6 <- dataf %>%
          group_by(period, squadName, supershot) %>%
          summarise(Total = sum(!!var, na.rm = TRUE),
                    Mean_SD = format_mean_sd(mean(!!var, na.rm = TRUE), sd(!!var, na.rm = TRUE)),
                    SE = format_se(sd(!!var, na.rm = TRUE) / sqrt(n()))) %>%
          filter(Total != 0)
        
        view(summary_0)
        view(summary_1)
        view(summary_2)
        view(summary_3)
        view(summary_4)
        view(summary_5)
        view(summary_6)
      }   
    
    # Bar Graphs ----
      # data_teamStats ----
        # between squads
          bar_teamBySquad <- function(var, title) {
          var <- ensym(var)
          graph <- ggplot(data_teamStats %>% 
                            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                            group_by(squadName) %>% 
                            summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)),
                          aes(x = reorder(factor(squadName), -mean1), y = mean1)) +
              geom_col(fill = "navy") +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), vjust = 2, size = 3, color = "white") +
              labs(title = paste(title, " between Super Netball squads"),
                   subtitle = "H&A season since 2020",
                   x = "SSN Squad",
                   y = paste("Average ", title)) +
              theme_get() +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(graph)
          }
    
        # before and after supershot rule change
          bar_teamBySupershot <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(supershot) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)),
                            aes(x = factor(supershot, levels = c("Before", "After")), y = mean1)) +
              geom_col(fill = "navy") +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), vjust = 2, size = 3, color = "white") +
              labs(title = paste(title, "before and after supershot rule change"),
                   subtitle = "H&A season",
                   x = "Rule change period",
                   y = paste("Average ", title)) +
              theme_get()
            print(graph)
          }
      
        # over time
          bar_teamOverTime <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(year) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                              filter(mean1 != 0),
                            aes(x = year, y = mean1)) +
              geom_col(fill = "navy") +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), vjust = 2, size = 3, color = "white") +
              labs(title = paste(title, "change over time"),
                   subtitle = "H&A season",
                   x = "Year",
                   y = paste("Average ", title)) +
              theme_minimal()
            print(graph)
          }
      
        # before and after rule change for each squad
          bar_bySquad_bySupershot <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(squadName, supershot) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                              filter(mean1 != 0),
                            aes(x = factor(supershot, levels = c("Before", "After")), y = mean1)) +
              geom_col(fill = "navy") +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), vjust = 2, size = 3, color = "white") +
              labs(title = paste(title, "change before and after rule change for each squad"),
                   subtitle = "H&A season",
                   x = "Rule change period",
                   y = paste("Average ", title)) +
              theme_minimal() +
              facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom")
            print(graph)
          }
  
        # over time for each squad
          bar_bySquad_overTime <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(squadName, year) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                              ungroup() %>%
                              filter(mean1 != 0),
                            aes(x = year, y = mean1)) +
              geom_col(fill = "navy") +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), vjust = 2, size = 3, color = "white") +
              labs(title = paste(title, "change pover time for each squad"),
                   subtitle = "H&A season",
                   x = "Year",
                   y = paste("Average ", title)) +
              theme_minimal() +
              facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom")
            print(graph)
          }

        # stacked changed over time 
          barStack_bySquad_overTime <- function(var, title) {
            var <- ensym(var)
              ggplot(data_teamStats %>%
                   filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                   group_by(year, squadName) %>%
                   summarize(total = sum(!! var, na.rm = TRUE)) %>%
                   group_by(year) %>%
                   mutate(percentage = total / sum(total) * 100) %>%
                   filter(!is.na(percentage)),
                 aes(x = reorder(factor(year), year), y = percentage, fill = factor(squadName))) +
            geom_col(position = "stack", width = 0.7) +
            geom_text(aes(label = scales::percent(percentage, scale = 1, accuracy = 0.01)), 
                      position = position_stack(vjust = 0.5), size = 3, color = "white") +
            labs(title = paste("Change in percentage of", title, "over time by squad"),
                 caption = "H&A season",
                 x = "Year",
                 y = paste("Change in", title),
                 fill = "Squad") +
            scale_y_continuous(labels = scales::percent_format(scale = 1, accuracy = 0.01), 
                               limits = c(0, 100), expand = c(0, 0)) +
            theme_get()
          }
      
      # data_teamPeriodStats ----
        # across period
          bar_period <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamPeriodStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(period) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                              filter(mean1 != 0),
                            aes(x = period, y = mean1)) +
              geom_col(fill = "navy") +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), vjust = 2, size = 3, color = "white") +
              labs(title = paste("Average", title, "per period"),
                   subtitle = "H&A season",
                   x = "Period",
                   y = paste("Average ", title)) +
              theme_get()
            print(graph)
          }
        
        # before and after supershot rule change
          bar_period_supershot <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamPeriodStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(period, supershot) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                              filter(mean1 != 0) %>%
                              mutate(supershot = factor(supershot, levels = c("Before", "After"))),
                            aes(x = factor(period), y = mean1)) +
              geom_col(position = position_dodge(width = 0.7), width = 0.6, fill = "forestgreen", show.legend = F) +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), 
                        position = position_dodge(width = 0.7), vjust = 2, size = 3, color = "white") +
              labs(title = paste(title, "across periods before and after supershot rule change"),
                    subtitle = "H&A season",
                    x = "Rule change period",
                    y = paste("Average ", title)) +
              theme_get() +
              facet_wrap(~ supershot, ncol = 2, scales = "free_x", strip.position = "bottom", dir = "h")
            print(graph)
          }
        
        # between squads across periods
          bar_period_bySquad <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamPeriodStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(squadName, period) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                              ungroup() %>%
                              filter(mean1 != 0),
                            aes(x = period, y = mean1)) +
              geom_col(fill = "navy") +
              geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), vjust = 2, size = 3, color = "white") +
              labs(title = paste("Average", title, "per period for each squad"),
                   subtitle = "H&A season",
                   x = "Year",
                   y = paste("Average ", title)) +
              theme_minimal() +
              facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom")
            print(graph)
          }
        
        # over time across periods
          bar_period_bySquad_overTime <- function(var, title) {
            var <- ensym(var)
            graph <- ggplot(data_teamPeriodStats %>% 
                              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
                              group_by(period, year) %>% 
                              summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                              filter(mean1 != 0)) +
              geom_col(aes(x = factor(period), y = mean1), position = position_dodge(width = 0.7), width = 0.6, fill = "forestgreen", show.legend = FALSE) +
              geom_text(aes(x = factor(period), y = mean1, label = paste(round(mean1, 2), " ± ", round(sd1, 2))), 
                        position = position_dodge(width = 0.7), vjust = 2, size = 3, color = "white") +
              labs(title = paste(title, "across periods before and after supershot rule change"),
                   subtitle = "H&A season",
                   x = "Period",
                   y = paste("Average ", title)) +
              theme_minimal() +
              facet_wrap(~ year, ncol = 2, scales = "free_x", strip.position = "bottom", dir = "h")
            print(graph)
          }

        # over time for each squad across periods
          bar_period_bySquad_overTime <- function(var, title) {
            var <- ensym(var)
            squad_graph <- function(squadID) {
              graph <- ggplot(data_teamPeriodStats %>% 
                                filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, squadId == squadID) %>%
                                group_by(period, year) %>% 
                                summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                                filter(mean1 != 0),
                              aes(x = factor(period), y = mean1)) +
                geom_col(position = position_dodge(width = 0.7), width = 0.6, fill = "forestgreen", show.legend = FALSE) +
                geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), 
                          position = position_dodge(width = 0.7), vjust = 2, size = 3, color = "white") +
                labs(title = paste(title, "across periods over time"),
                     subtitle = paste(unique(data_teamPeriodStats$squadName[data_teamPeriodStats$squadId == squadID]), " - H&A season"),
                     x = "Period",
                     y = paste("Average ", title)) +
                theme_minimal() +
                facet_wrap(~ year, ncol = 1, scales = "free_x", strip.position = "bottom", dir = "h")
              
              return(graph)
            }
        
            for (squadID in SSN_Squads) {
              print(squad_graph(squadID))
            }
          }

        # before and after supershot rule change for each squad across periods
          bar_period_bySquad_supershot <- function(var, title) {
            var <- ensym(var)
            squad_graph <- function(squadID) {
              graph <- ggplot(data_teamPeriodStats %>% 
                                filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, squadId == squadID) %>%
                                group_by(period, supershot) %>% 
                                summarize(mean1 = mean(!!var, na.rm = TRUE), sd1 = sd(!!var, na.rm = TRUE)) %>%
                                filter(mean1 != 0) %>%
                                mutate(supershot = factor(supershot, levels = c("Before", "After"))),
                              aes(x = factor(period), y = mean1)) +
                geom_col(position = position_dodge(width = 0.7), width = 0.6, fill = "forestgreen", show.legend = FALSE) +
                geom_text(aes(label = paste(round(mean1, 2), " ± ", round(sd1, 2))), 
                          position = position_dodge(width = 0.7), vjust = 2, size = 3, color = "white") +
                labs(title = paste(title, "across periods before and after supershot rule change"),
                     subtitle = paste(unique(data_teamPeriodStats$squadName[data_teamPeriodStats$squadId == squadID]), " - H&A season"),
                     x = "Period",
                     y = paste("Average ", title)) +
                theme_minimal() +
                facet_wrap(~ supershot, ncol = 2, scales = "free_x", strip.position = "bottom", dir = "h")
              
              return(graph)
            }
            
            for (squadID in SSN_Squads) {
              print(squad_graph(squadID))
            }
          }
          
    # Violin plot ----
      # data_teamStats ----
        # by squad
          violin_bySquad <- function(var) {
            dataf <- data_teamStats %>%
            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
          
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = squadName, y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(squadName) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = squadName, y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "between squads",
                   x = "squad",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # before and after supershot rule change
          violin_bySupershot <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = factor(supershot, levels = c("Before", "After")), y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(supershot) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = factor(supershot, levels = c("Before", "After")), y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "before and after supershot rule change",
                   x = "Rule change",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # over time
          violin_overTime <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = year, y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(year) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = year, y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "over time",
                   x = "Year",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # before and after supershot rule change for each squad
          violin_bySupershot_bySquad <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = factor(supershot, levels = c("Before", "After")), y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(supershot) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = factor(supershot, levels = c("Before", "After")), y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "Before and After Rule Changes",
                   x = "Rule change",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom") +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # over time for each sqaud
          violin_overTime_bySquad <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = year, y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(year) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = year, y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "over time",
                   x = "Year",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom") +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }

      # data_teamPeriodStats ----
        # across periods
          violin_period <- function(var) {
            dataf <- data_teamPeriodStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, period <= 4)
            
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = factor(period), y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(period) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = period, y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "between periods",
                   x = "period",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # before and after supershot rule change across periods
          violin_period_supershot <- function(var) {
            dataf <- data_teamPeriodStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, period <= 4)
            
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = factor(period), y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(period) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = period, y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "Before and After Rule Changes",
                   x = "Rule change",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              facet_wrap(~factor(supershot, levels = c("Before", "After")), ncol = 1, scales = "fixed", strip.position = "bottom")
            theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # between squads across periods
          violin_period_squads <- function(var) {
            dataf <- data_teamPeriodStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, period <= 4)
            
            var <- ensym(var)
            
            plot <- ggplot(dataf,
                           aes(x = factor(period), y = !!var)) +
              geom_violin(fill = "lightblue", color = "black", width = 0.6) +
              geom_violin(fill = "lightblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
              geom_point(data = dataf %>%
                           group_by(period) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = period, y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "Before and After Rule Changes",
                   x = "Rule change",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              facet_wrap(~ squadName, ncol = 3, scales = "fixed", strip.position = "bottom")
            theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # over time for each squad across periods

          
        # before and after supershot rule change for each squad across periods
          
          
    # Scatter plots ----
      # data_teamStats ----
        # all
          scatter_teamStats <- function(x_var, y_var) {
            x_var <- ensym(x_var)
            y_var <- ensym(y_var)
            plot <- ggplot(data_teamStats %>% 
                            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017),
                            filter(complete.cases({{ x_var }}, {{ y_var }})) %>%
                          aes(x = !!x_var, y = !!y_var)) +
              geom_point(color = "navy", size = 1, alpha = 0.5) +
              geom_smooth(method = "lm", se = FALSE, color = "red") +
              labs(title = paste("Comparing", quo_name(x_var), "and", quo_name(y_var)),
                   x = quo_name(x_var),
                   y = quo_name(y_var)) +
              theme_get()
            print(plot)
          }
  
        # between squads
          scatter_teamStats_bySquad <- function(x_var, y_var) {
            x_var <- ensym(x_var)
            y_var <- ensym(y_var)
            plot <- ggplot(data_teamStats %>% 
                            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017),
                            filter(complete.cases({{ x_var }}, {{ y_var }})) %>%
                          aes(x = !!x_var, y = !!y_var)) +
              geom_point(color = "navy", size = 1, alpha = 0.5) +
              geom_smooth(method = "lm", se = FALSE, color = "red") +
              labs(title = paste("Comparing", quo_name(x_var), "and", quo_name(y_var), "for each squad"),
                   x = quo_name(x_var),
                   y = quo_name(y_var)) +
              facet_wrap(~ squadName, ncol = 2, scales = "fixed") +
              theme_get()
            print(plot)
          }
        
        # before and after supershot rule change
          scatter_teamStats_supershot <- function(x_var, y_var) {
            x_var <- ensym(x_var)
            y_var <- ensym(y_var)
            plot <- ggplot(data_teamStats %>% 
                             filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017),
                           filter(complete.cases({{ x_var }}, {{ y_var }})) %>%
                             aes(x = !!x_var, y = !!y_var)) +
              geom_point(color = "navy", size = 1, alpha = 0.5) +
              geom_smooth(method = "lm", se = FALSE, color = "red") +
              labs(title = paste("Comparing", quo_name(x_var), "and", quo_name(y_var), "before and after supershot rule change"),
                   x = quo_name(x_var),
                   y = quo_name(y_var)) +
              facet_wrap(~ factor(supershot, levels = c("Before", "After")), ncol = 2, scales = "fixed") +
              theme_get()
            print(plot)
          }     
      
        # over time
          scatter_teamStats_overTime <- function(x_var, y_var) {
            x_var <- ensym(x_var)
            y_var <- ensym(y_var)
            plot <- ggplot(data_teamStats %>% 
                            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017),
                            filter(complete.cases({{ x_var }}, {{ y_var }})) %>%
                          aes(x = !!x_var, y = !!y_var)) +
              geom_point(color = "navy", size = 1, alpha = 0.5) +
              geom_smooth(method = "lm", se = FALSE, color = "red") +
              labs(title = paste("Comparing", quo_name(x_var), "and", quo_name(y_var), "over time"),
                   x = quo_name(x_var),
                   y = quo_name(y_var)) +
              facet_wrap(~ year, ncol = 2, scales = "fixed") +
              theme_get()
            print(plot)
          }
  
        # before and after rule change for each squad
          scatter_teamStats_bySquad_supershot <- function(x_var, y_var) {
            x_var <- ensym(x_var)
            y_var <- ensym(y_var)
            plot <- ggplot(data_teamStats %>% 
                            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017),
                            filter(complete.cases({{ x_var }}, {{ y_var }})) %>%
                          aes(x = !!x_var, y = !!y_var)) +
              geom_point(color = "navy", size = 1, alpha = 0.5) +
              geom_smooth(method = "lm", se = FALSE, color = "red") +
              labs(title = paste("Comparing", quo_name(x_var), "and", quo_name(y_var), "for each squad"),
                   x = quo_name(x_var),
                   y = quo_name(y_var)) +
              facet_grid(squadName ~ factor(supershot, levels = c("Before", "After")), scales = "fixed") +
              theme_get()
            print(plot)
          }
      
        # over time for each squad
          scatter_teamStats_bySquad_overTime <- function(x_var, y_var) {
            x_var <- ensym(x_var)
            y_var <- ensym(y_var)
            plot <- ggplot(data_teamStats %>% 
                            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017),
                            filter(complete.cases({{ x_var }}, {{ y_var }})) %>%
                          aes(x = !!x_var, y = !!y_var)) +
              geom_point(color = "navy", size = 1, alpha = 0.5) +
              geom_smooth(method = "lm", se = FALSE, color = "red") +
              labs(title = paste("Comparing", quo_name(x_var), "and", quo_name(y_var), "for each squad"),
                   x = quo_name(x_var),
                   y = quo_name(y_var)) +
              facet_grid(squadName ~ year, scales = "fixed") +
              theme_get()
            print(plot)
          }

      # data_teamPeriodStats ----
        # across periods

        # before and after supershot rule change

        # between squads across periods

        # over time across periods

        # over time for each squad across periods

        # before and after supershot rule change for each squad across periods
               
    # Box and whisker plots ----
      # data_teamStats ----
          # by squad
          box_bySquad <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            plot <- ggplot(dataf,
                           aes(x = squadName, y = !!var)) +
              geom_boxplot(fill = "navy", color = "black", width = 0.6) +
              geom_point(data = dataf %>%
                           group_by(squadName) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = squadName, y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "between squads",
                   x = "squad",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_get() +
              theme(axis.text.x = element_text(angle = 45, hjust = 1))
            print(plot)
          }
          
        # before and after supershot rule change
          box_bySupershot <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            plot <- ggplot(dataf,
                          aes(x = factor(supershot, levels = c("Before", "After")), y = !!var)) +
            geom_boxplot(fill = "navy", color = "black", width = 0.6) +
            geom_point(data = dataf %>%
                        group_by(supershot) %>%
                        summarize(mean1 = mean(!!var, na.rm = TRUE)),
                       aes(x = reorder(supershot, -mean1), y = mean1),
                       color = "white", size = 1) +
            labs(title = quo_name(var), "Before and After Rule Changes",
                 x = "Rule Change",
                 y = quo_name(var)) +
            scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
            theme_minimal()
            print(plot)
          }
          
        # over time
          box_overTime <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            var <- ensym(var)

            plot <- ggplot(dataf,
                           aes(x = reorder(as.numeric(year), year), y = !!var)) +
            geom_boxplot(fill = "navy", color = "black", width = 0.6) +
            geom_point(data = dataf %>%
                        filter(var != 0) %>%
                        group_by(year) %>%
                        summarize(mean1 = mean(!!var, na.rm = TRUE)),
                      aes(x = reorder(as.numeric(year), year), y = mean1),
                      color = "white", size = 1) +
            labs(title = quo_name(var), "over time",
                   x = "Year",
                   y = quo_name(var)) +
            scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
            theme_minimal()
            print(plot)
          }

        # before and after rule change for each squad
          box_bySupershot_bySquad <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            plot <- ggplot(dataf,
                           aes(x = factor(supershot, levels = c("Before", "After")), y = !!var)) +
            geom_boxplot(fill = "navy", color = "black", width = 0.6) +
            geom_point(data = dataf %>%
                        group_by(supershot) %>%
                        summarize(mean1 = mean(!!var, na.rm = TRUE)),
                      aes(x = reorder(supershot, -mean1), y = mean1),
                      color = "white", size = 1) +
            labs(title = quo_name(var), "Before and After Rule Changes",
                   x = "Rule Change",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
            facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom")
            print(plot)
          }
          
        # over time for each squad
          box_overTime_bySquad <- function(var) {
            dataf <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            plot <- ggplot(dataf,
                           aes(x = reorder(as.numeric(year), year), y = !!var)) +
              geom_boxplot(fill = "navy", color = "black", width = 0.6) +
              geom_point(data = dataf %>%
                           group_by(year) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = reorder(as.numeric(year), year), y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "over time",
                   x = "Year",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
            facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom")
            print(plot)
          }

      # data_teamPeriodStats ----
        # across periods
          box_period <- function(var) {
            dataf <- data_teamPeriodStats %>%
                    filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
            
            var <- ensym(var)
            plot <- ggplot(dataf,
                          aes(x = reorder(as.numeric(period), year), y = !!var)) +
              geom_boxplot(fill = "navy", color = "black", width = 0.6) +
              geom_point(data = dataf %>%
                           group_by(period) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = as.numeric(period), y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "over time",
                   x = "Period",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal()
            
            print(plot)
          }
          
        # before and after supershot rule change across periods
          box_period_supershot <- function(var, title) {
            dataf <- data_teamPeriodStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, period <= 4)
            
            var <- ensym(var)
            plot <- ggplot(dataf,
                           aes(x = reorder(as.numeric(period), year), y = !!var)) +
              geom_boxplot(fill = "navy", color = "black", width = 0.6) +
              geom_point(data = dataf %>%
                           group_by(period) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = as.numeric(period), y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "before and after supershot rule change",
                   x = "Period",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
            facet_wrap(~factor(supershot, levels = c("Before", "After")), ncol = 4, scales = "fixed", strip.position = "bottom")
            
            print(plot)
          }
    
        # between squads across periods
          box_period_bySquad <- function(var, title) {
            dataf <- data_teamPeriodStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, period <= 4)
            
            var <- ensym(var)
            plot <- ggplot(dataf,
                           aes(x = reorder(as.numeric(period), year), y = !!var)) +
              geom_boxplot(fill = "navy", color = "black", width = 0.6) +
              geom_point(data = dataf %>%
                           group_by(period) %>%
                           summarize(mean1 = mean(!!var, na.rm = TRUE)),
                         aes(x = as.numeric(period), y = mean1),
                         color = "white", size = 1) +
              labs(title = quo_name(var), "over time",
                   x = "Period",
                   y = quo_name(var)) +
              scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
              theme_minimal() +
              facet_wrap(~squadName, ncol = 4, scales = "fixed", strip.position = "bottom")
            
            print(plot)
          }
            
        # over time across periods
          box_period_bySquad_overTime <- function(var, title) {
              dataf <- data_teamPeriodStats %>%
                filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017, period <= 4)
              
              var <- ensym(var)
              plot <- ggplot(dataf,
                             aes(x = reorder(as.numeric(period), year), y = !!var)) +
                geom_boxplot(fill = "navy", color = "black", width = 0.6) +
                geom_point(data = dataf %>%
                             group_by(period) %>%
                             summarize(mean1 = mean(!!var, na.rm = TRUE)),
                           aes(x = as.numeric(period), y = mean1),
                           color = "white", size = 1) +
                labs(title = paste(quo_name(var), "over time"),
                     x = "Period",
                     y = quo_name(var)) +
                scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
                theme_minimal() +
                facet_grid(~year, scales = "fixed")
              
              print(plot)
            }
            
        # over time for each squad across periods
          box_period_bySquad_overTime <- function(var, title)
        
        # before and after supershot rule change for each squad across periods
          box_period_bySquad_supershot <- function(var, title) 
            
    # Correlations ----
      # data_teamStats ----
        correlation_teamStats <- function(var1, var2) {
          dataf <- data_teamStats %>%
            filter(squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017)
          
          var1 <- ensym(var1)
          var2 <- ensym(var2)
          
          cor_0 <- dataf %>%
            summarise(Correlation = cor(!!sym(var1), !!sym(var2), use = "pairwise.complete.obs"))
          
          cor_1 <- dataf %>%
            group_by(supershot) %>%
            summarise(Correlation = cor(!!sym(var1), !!sym(var2), use = "pairwise.complete.obs"))

          cor_2 <- dataf %>%
            group_by(year) %>%
            summarise(Correlation = cor(!!sym(var1), !!sym(var2), use = "pairwise.complete.obs")) %>%
            filter(!is.na(Correlation))

          cor_3 <- dataf %>%
            group_by(squadName) %>%
            summarise(Correlation = cor(!!sym(var1), !!sym(var2), use = "pairwise.complete.obs"))
          
          cor_4 <- dataf %>%
            group_by(squadName, supershot) %>%
            summarise(Correlation = cor(!!sym(var1), !!sym(var2), use = "pairwise.complete.obs"))
          
          cor_5 <- dataf %>%
            group_by(squadName, year) %>%
            summarise(Correlation = cor(!!sym(var1), !!sym(var2), use = "pairwise.complete.obs")) %>%
            filter(!is.na(Correlation))
      
          view(cor_0)
          view(cor_1)
          view(cor_2)
          view(cor_3)
          view(cor_4)
          view(cor_5)
        }
          
    # Significance tests ----
      # t test ----
        # Independent t test - is 'var' statistically significant before and after SS rule change
          paired_tTest_supershot <- function(var) {
            var <- ensym(var)
            
            before_data <- data_teamStats %>%
              filter(supershot == "Before", squadId %in% SSN_Squads, matchType == "H", year >= 2017) %>%
              group_by(squadId) %>%
              summarize(before_mean = mean(!!var))
            
            after_data <- data_teamStats %>%
              filter(supershot == "After", squadId %in% SSN_Squads, matchType == "H", year >= 2017) %>%
              group_by(squadId) %>%
              summarize(after_mean = mean(!!var))
            
            matched_data <- before_data %>%
              left_join(after_data, by = c("squadId"))
            
            result <- t.test(matched_data$before_mean, matched_data$after_mean, paired = T)
              cat("Paired t-test results for", quo_name(var), "variable:\n")
              cat("T-statistic:", result$statistic, "\n")
              cat("Degrees of freedom:", result$parameter, "\n")
              cat("P-value:", result$p.value, "\n")
              
              if (result$p.value < 0.05) {
                cat("The difference is statistically significant (p < 0.05).\n")
              } else {
                cat("There is no significant difference (p >= 0.05).\n")
              }
          }
          
        # Independent t test - which squads 'var' is statistically significant before SS rule
          paired_tTest_supershot_squad <- function(var) {
            var <- ensym(var)
            
            before_data <- data_teamStats %>%
              filter(supershot == "Before", matchType == "H", year >= 2017) %>%
              group_by(squadId, round) %>%
              summarize(before_mean = mean(!!var))
            
            after_data <- data_teamStats %>%
              filter(supershot == "After", matchType == "H", year >= 2017) %>%
              group_by(squadId, round) %>%
              summarize(after_mean = mean(!!var))
            
            matched_data <- left_join(before_data, after_data, by = c("squadId", "round"))
            
            for (squadId in SSN_Squads) {
              result <- t.test(matched_data$before_mean[matched_data$squadId == squadId],
                               matched_data$after_mean[matched_data$squadId == squadId],
                               paired = TRUE)
              
              cat("Paired t-test results for", quo_name(var), "variable and squad:", squadId, "\n")
              cat("T-statistic:", result$statistic, "\n")
              cat("Degrees of freedom:", result$parameter, "\n")
              cat("P-value:", result$p.value, "\n")
              
              if (result$p.value < 0.05) {
                cat("The difference is statistically significant (p < 0.05).\n")
              } else {
                cat("There is no significant difference (p >= 0.05).\n")
              }
              cat("\n")
            }
          }
     
        # One sample t test - which squads 'var' is statistically significant to itself 
          onesample_tTest <- function(var) {
            var <- ensym(var)
            
            data <- data_teamStats %>%
              filter(squadId %in% SSN_Squads, matchType == "H", year >= 2017)
            
            v1 <- pull(data, !!var)

              squad_values <- data %>%
                filter(squadId == "8118") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)
              
              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("GIANTS Netball")
              print(t_test)
              
              squad_values <- data %>%
                filter(squadId == "804") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)

              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("Melbourne Vixens")
              print(t_test) 
              
              squad_values <- data %>%
                filter(squadId == "807") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)
              
              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("Queensland Firebirds")
              print(t_test) 
              
              squad_values <- data %>%
                filter(squadId == "801") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)
              
              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("Adelaide Thunderbirds")
              print(t_test)
            
              squad_values <- data %>%
                filter(squadId == "806") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)
              
              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("NSW Swifts")
              print(t_test)  
              
              squad_values <- data %>%
                filter(squadId == "8117") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)
              
              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("Sunshine Coast Lightning")
              print(t_test)
              
              squad_values <- data %>%
                filter(squadId == "810") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)
              
              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("West Coast Fever")
              print(t_test)
              
              squad_values <- data %>%
                filter(squadId == "8119") %>%
                pull(!!var)
              
              squad_mean <- mean(squad_values)
              
              t_test <- t.test(v1, mu = squad_mean, alternative = "two.sided")
              print("Collingwood Magpies")
              print(t_test) 
            }
            
          onesample_tTest(goals)

      # (M)ANOVAS ----
        anova_aftersupershot <- function(var) {
          var <- ensym(var)
          
          result <- data_teamStats %>%
            filter(squadId %in% SSN_Squads, matchType == "H", year >= 2017, !is.na(!!var)) %>%
            group_by(squadName) %>%
            summarize(mean_var = mean(!!var))
          
          anova_result <- aov(formula = mean_var ~ squadName, data = result)
          
          posthoc_result <- TukeyHSD(anova_result)
          
          print(posthoc_result)
        }
        
    # Pie graphs ----
      # data_teamStats ----
        pie_bySquad <- function(var) {
          var <- ensym(var)
          pie <- data_teamStats %>%
            filter(squadId %in% SSN_Squads, supershot == "After", matchType == "H") %>%
            group_by(squadName) %>%
            summarize(total_goal2 = sum(!!var, na.rm = TRUE), .groups = "drop") %>%
            mutate(percentage = total_goal2 / sum(total_goal2)) %>% 
            ggplot(aes(x = "", y = percentage, fill = fct_rev(reorder(squadName, desc(percentage))))) +
            geom_bar(width = 2, stat = "identity") +
            coord_polar(theta = "y") +
            geom_text(aes(label = sprintf("%.2f%%", round(percentage * 100, 2))),
                      position = position_stack(vjust = 0.5), size = 3) + 
            labs(title = paste("Percentage of", quo_name(var), "by squad"),
                 caption = "H&A season",
                 fill = "SSN Squad") +
            theme_minimal() +
            theme(axis.text = element_blank(),
                  axis.title = element_blank(),
                  panel.grid = element_blank()) +
            scale_fill_brewer(palette = "Greens")   
          print(pie)
        }
        
        pie_overTime <- function(var) {
          var <- ensym(var)
          pie <- data_teamStats %>%
            filter(squadId %in% SSN_Squads, supershot == "After", matchType == "H") %>%
            group_by(year) %>%
            summarize(total_goal2 = sum(!!var, na.rm = TRUE), .groups = "drop") %>%
            mutate(percentage = total_goal2 / sum(total_goal2)) %>% 
            ggplot(aes(x = "", y = percentage, fill = fct_rev(reorder(year, desc(percentage))))) +
            geom_bar(width = 2, stat = "identity") +
            coord_polar(theta = "y") +
            geom_text(aes(label = sprintf("%.2f%%", round(percentage * 100, 2))),
                      position = position_stack(vjust = 0.5), size = 3) + 
            labs(title = paste("Percentage of", quo_name(var), "over time"),
                 caption = "H&A season",
                 fill = "Year") +
            theme_minimal() +
            theme(axis.text = element_blank(),
                  axis.title = element_blank(),
                  panel.grid = element_blank()) +
            scale_fill_brewer(palette = "Greens")   
          print(pie)
        }
        
    # Results (w/l/d) ----
      # teamStats Summary Stats ----
        standing_stats <- function() {
          summary_0 <- data_teamStats %>%
            filter(!is.na(standing), squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
            group_by(squadName, standing, .groups = "drop") %>%
            summarize(total_games = n()) %>%
            pivot_wider(names_from = standing, values_from = total_games, values_fill = 0) %>%
            mutate(
              W_p = round(W / sum(W, L, D) * 100, 2),
              L_p = round(L / sum(W, L, D) * 100, 2),
              D_p = round(D / sum(W, L, D) * 100, 2)
            ) %>%
            select(W, L, D, W_p, L_p, D_p)
          
          summary_1 <- data_teamStats %>%
            filter(!is.na(standing), squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
            group_by(squadName, year, standing, .groups = "drop") %>%
            summarize(total_games = n()) %>%
            pivot_wider(names_from = standing, values_from = total_games, values_fill = 0) %>%
            mutate_at(vars(W, L, D), as.numeric) %>%
            mutate(
              W_p = round(W / sum(W, L, D) * 100, 2),
              L_p = round(L / sum(W, L, D) * 100, 2),
              D_p = round(D / sum(W, L, D) * 100, 2)
            ) %>%
            select(squadName, year, W, L, D, W_p, L_p, D_p)
   
          summary_2 <- data_teamStats %>%
            filter(!is.na(standing), squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
            group_by(squadName, supershot, standing, .groups = "drop") %>%
            summarize(total_games = n()) %>%
            pivot_wider(names_from = standing, values_from = total_games, values_fill = 0) %>%
            mutate_at(vars(W, L, D), as.numeric) %>%
            mutate(
              W_p = round(W / sum(W, L, D) * 100, 2),
              L_p = round(L / sum(W, L, D) * 100, 2),
              D_p = round(D / sum(W, L, D) * 100, 2)
            ) %>%
            select(squadName, supershot, W, L, D, W_p, L_p, D_p)
          
          summary_3 <- data_teamPeriodStats %>%
            filter(!is.na(standing), squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
            group_by(squadName, period, standing, .groups = "drop") %>%
            summarize(total_games = n()) %>%
            pivot_wider(names_from = standing, values_from = total_games, values_fill = 0) %>%
            mutate_at(vars(W, L, D), as.numeric) %>%
            mutate(
              W_p = round(W / sum(W, L, D) * 100, 2),
              L_p = round(L / sum(W, L, D) * 100, 2),
              D_p = round(D / sum(W, L, D) * 100, 2)
            ) %>%
            select(squadName, period, W, L, D, W_p, L_p, D_p)

          summary_4 <- data_teamPeriodStats %>%
            filter(!is.na(standing), squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
            group_by(squadName, period, year, standing, .groups = "drop") %>%
            summarize(total_games = n()) %>%
            pivot_wider(names_from = standing, values_from = total_games, values_fill = 0) %>%
            mutate_at(vars(W, L, D), as.numeric) %>%
            mutate(
              W_p = round(W / sum(W, L, D) * 100, 2),
              L_p = round(L / sum(W, L, D) * 100, 2),
              D_p = round(D / sum(W, L, D) * 100, 2)
            ) %>%
            select(squadName, period, year, W, L, D, W_p, L_p, D_p)
          
          summary_5 <- data_teamPeriodStats %>%
            filter(!is.na(standing), squadId %in% SSN_Squads, matchType == "H", as.numeric(as.character(year)) >= 2017) %>%
            group_by(squadName, period, supershot, standing, .groups = "drop") %>%
            summarize(total_games = n()) %>%
            pivot_wider(names_from = standing, values_from = total_games, values_fill = 0) %>%
            mutate_at(vars(W, L, D), as.numeric) %>%
            mutate(
              W_p = round(W / sum(W, L, D) * 100, 2),
              L_p = round(L / sum(W, L, D) * 100, 2),
              D_p = round(D / sum(W, L, D) * 100, 2)
            ) %>%
            select(squadName, period, supershot, W, L, D, W_p, L_p, D_p)
      
          view(summary_0)
          view(summary_1)
          view(summary_2)
          view(summary_3)
          view(summary_4)
          view(summary_5)
        }
      # teamStats Stacked bars ---- 
        standing_teamStats_stackBar <- function() {
          # Plot 1: Standing distribution per squad
          plot1 <- ggplot(data_teamStats %>% 
                   filter(squadId %in% SSN_Squads,  year >= 2017, matchType == "H") %>% 
                   count(squadName, standing) %>%
                   group_by(squadName) %>%
                   mutate(percentage = n / sum(n) * 100),
                 aes(x = squadName, y = percentage, fill = standing)) +
            geom_bar(stat = "identity") +
            scale_fill_manual(
              values = c("W" = "seagreen3", "L" = "tomato1", "D" = "yellow2"),
              guide = guide_legend(title = "Outcome")
            ) +
            labs(title = "Results of Super Netball squads",
                 x = "Squad", 
                 y = "Percentage") +
            theme_minimal() +
            theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
            geom_text(aes(label = sprintf("%.2f%%", percentage)), color = "white", size = 3, position = position_stack(vjust = 0.5))
          
          # Plot 2: Standing distribution per squad over time
          plot2 <- ggplot(data_teamStats %>% 
                   filter(squadId %in% SSN_Squads, year >= 2017, matchType == "H") %>% 
                   count(squadName, standing, year) %>%
                   group_by(squadName, year) %>%
                   mutate(percentage = n / sum(n) * 100),
                 aes(x = year, y = percentage, fill = standing)) +
            geom_bar(stat = "identity") +
            scale_fill_manual(
              values = c("W" = "seagreen3", "L" = "tomato1", "D" = "yellow2"),
              guide = guide_legend(title = "Outcome")
            ) +
            labs(title = "Results of Super Netball squads over time",
                 x = "Year", 
                 y = "Percentage") +
            theme_minimal() +
            theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
            geom_text(aes(label = sprintf("%.2f%%", percentage)), position = position_stack(vjust = 0.5)) +
            facet_wrap(. ~ squadName, ncol = 2, scales = "free_x", strip.position = "bottom")
          
          # Plot 3: Standing distribution per squad before and after rule changes
          plot3 <- ggplot(data_teamStats %>% 
                   filter(squadId %in% SSN_Squads, year >= 2017, matchType == "H") %>% 
                   count(squadName, standing, supershot) %>%
                   group_by(squadName, supershot) %>%
                   mutate(percentage = n / sum(n) * 100),
                 aes(x = factor(supershot, levels = c("Before", "After")), y = percentage, fill = standing)) +
            geom_bar(stat = "identity") +
            scale_fill_manual(
              values = c("W" = "seagreen3", "L" = "tomato1", "D" = "yellow2"),
              guide = guide_legend(title = "Outcome")
            ) +
            labs(title = "Results of Super Netball squads before and after rule changes",
                 x = "Rule Change", 
                 y = "Percentage") +
            theme_minimal() +
            theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
            geom_text(aes(label = sprintf("%.2f%%", percentage)), position = position_stack(vjust = 0.5)) +
            facet_wrap(. ~ squadName, ncol = 2, scales = "free_x", strip.position = "bottom")
        
          print(plot1)
          print(plot2)
          print(plot3)
        }

      # teamPeriodStats Stacked bars ----
        standing_periodStats_stackBar1 <- function() {
          plot3 <- ggplot(data_teamPeriodStats %>% 
                            filter(squadId %in% SSN_Squads, year >= 2017, matchType == "H", period <=4) %>% 
                            count(squadName, standing, period) %>%
                            group_by(squadName, period) %>%
                            mutate(percentage = n / sum(n) * 100),
                          aes(x = period, y = percentage, fill = standing)) +
            geom_bar(stat = "identity") +
            scale_fill_manual(
              values = c("W" = "seagreen3", "L" = "tomato1", "D" = "yellow2"),
              guide = guide_legend(title = "Outcome")
            ) +
            labs(title = "Results of Super Netball squads for each period",
                 x = "period", 
                 y = "Percentage") +
            theme_minimal() +
            theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
            geom_text(aes(label = sprintf("%.2f%%", percentage)), position = position_stack(vjust = 0.5)) +
            facet_wrap(. ~ squadName, ncol = 2, scales = "free_x", strip.position = "bottom")
        }
          
        standing_periodStats_stackBar2 <- function(squadId) {
          ggplot(data_teamPeriodStats %>% 
                   filter(squadId %in% SSN_Squads, year >= 2017, matchType == "H", period <= 4) %>% 
                   count(squadName, standing, period, supershot) %>%
                   group_by(squadName, period) %>%
                   mutate(percentage = n / sum(n) * 100),
                 aes(x = period, y = percentage, fill = standing)) +
            geom_bar(stat = "identity") +
            scale_fill_manual(
              values = c("W" = "seagreen3", "L" = "tomato1", "D" = "yellow2"),
              guide = guide_legend(title = "Outcome")
            ) +
            labs(x = "Period", y = "Percentage") +
            ggtitle(paste("Results of", squadID, "for Super Netball squads per period")) +
            theme_minimal() +
            theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
            geom_text(aes(label = sprintf("%.2f%%", percentage)), position = position_stack(vjust = 0.5))
        }
        
        # Generate and print the plots for each squad
        for (squadID in SSN_Squads) {
          print(standing_periodStats_stackBar(squadId))
        }
        
# HOW ARE RULE CHANGES BEING USED BY SQUADS ----
  # How has supershot impacted scoring? ----
    # How has supershot scoring differed between squads?
      summary_teamStats(goal2)
      box_bySquad(goal2)
      pie_bySquad(goal2)
      
      
      summary_teamStats(attempt2)
      box_bySquad(attempt2)
      pie_bySquad(attempt2)
      
    # How has supershot scoring changed over time?
      box_overTime(goal2)
      box_overTime(goal2)
      box_overTime_bySquad(goal2)
      barStack_bySquad_overTime(goal2, "Supershots")
      
      box_overTime(attempt2)
      box_overTime(attempt2)
      box_overTime_bySquad(attempt2)
      barStack_bySquad_overTime(attempt2, "Supershot attempts")
      
    # How have squads supershot scoring impacted regular goals?
      summary_teamStats(goal1)
      
    # How has supershot accuracy differed between squads?
      summary_teamStats(goal2_accuracy)
      box_bySquad(goal2_accuracy)
  
    # How has supershot accuracy changed over time?
      box_overTime(goal2_accuracy)
      box_overTime_bySquad(goal2_accuracy)
      
    # Has the supershot rule affected regular goal accuracy?
      summary_teamStats(goal1_accuracy)
      box_overTime(goal1_accuracy)
      box_overTime_bySquad(goal1_accuracy)
  
    # Which periods during a match are squads most likely to score a supershot?
      summary_teamPeriodsStats(goal2)
      
  # How have supershots impacted possession and passing? ----
    # Are teams who score more supershots more likely to make more turnovers?
      correlation_teamStats(goal2, turnovers)

  # How have supershots impacted defensive actions? ----
    # Have supershots resulted in more turnovers? 
      summary_teamStats(turnovers)
      correlation_teamStats(goal2, turnovers)
      correlation_teamStats(goal2, turnovers)
      scatter_teamStats(goals, turnovers)
      scatter_teamStats_supershot(goals, turnovers)
    
      colnames(data_teamStats)
    # Do missed supershots result in more defensiveRebounds than regular goals ?
      scatter_teamStats_supershot(attempt1, defensiveRebounds)
      correlation_teamStats(attempt1, defensiveRebounds)
      
      scatter_teamStats(attempt2, defensiveRebounds)
      correlation_teamStats(attempt2, defensiveRebounds)     

      scatter_teamStats(goalMisses, defensiveRebounds)
      correlation_teamStats(goalMisses, defensiveRebounds)
      
      scatter_teamStats(goal2_missed, defensiveRebounds)
      correlation_teamStats(goal2_missed, defensiveRebounds)
      
      
view(data_teamStats %>% filter(is.na(defensiveRebounds)) %>% select(defensiveRebounds, offensiveRebounds, rebounds, year))
      
  # How have supershots impacted attacking actions? ----
    
      
  # How have supershots impacted penalties, offenses, and clangers?  ----
        
# HOW ARE RULE CHANGES AFFECTING MATCH OUTCOMES
  # Has the introduction of supershots altered scoring dynamics (i.e.: have scores increased or decreased?)
    summary_teamStats(points)
    box_overTime(points)
    box_overTime_bySquad(points)
    box_bySupershot_bySquad(points)
   
  # How has the introduction of supershots influenced the average winning margin in matches? Are matches becoming more closely contested or more lopsided? 
  
  # Are squads that are more proficient in scoring supershots more likely to win matches compared to squads that rely more on traditional scoring methods?
    
      
######  ------
  # goal 2accuracy
  # can you look a the last five minutes of the game to compare supershots ?
  # Update all functions to filter for home V away games
  # Percentage of points from goal2
  # Build the foundations of subs data
      
  # Discuss with Aaron
    # building the observed subs
    # HvA filtering
    # complex to tell who is winning V losing, and who won V lost?
    # where's the timeout data?
      
  head(data_scoreFlow)
