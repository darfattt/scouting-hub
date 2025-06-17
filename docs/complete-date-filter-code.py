"""
Complete Local Date Filter Implementation
========================================

This file contains the complete code implementation for the local date filter
as documented in local-date-filter-implementation.md

Usage:
1. Copy the required functions to your component file
2. Add the UI components to your Streamlit interface
3. Call apply_date_filter() with your player data
4. Use the debug interface for troubleshooting
"""

import streamlit as st
import pandas as pd
import datetime
import copy


def render_date_filter_ui():
    """
    Render the date filter UI components.
    
    Returns:
        tuple: (use_date_filter, start_date, end_date)
    """
    # Date filter section
    st.subheader("📅 Date Filter")
    use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range")
    
    start_date = None
    end_date = None
    
    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.date(2024, 8, 1),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="Start date for filtering matches"
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=datetime.date(2025, 6, 30),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="End date for filtering matches"
            )
    
    return use_date_filter, start_date, end_date


def parse_date_multiple_formats(date_str):
    """
    Parse date string using multiple common formats.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime.date object or None if parsing fails
    """
    if not date_str:
        return None
        
    date_str = str(date_str).strip()
    
    # Common date formats to try
    date_formats = [
        "%Y-%m-%d",           # 2024-08-15
        "%d/%m/%Y",           # 15/08/2024
        "%m/%d/%Y",           # 08/15/2024
        "%d-%m-%Y",           # 15-08-2024
        "%Y/%m/%d",           # 2024/08/15
        "%d.%m.%Y",           # 15.08.2024
        "%Y-%m-%d %H:%M:%S",  # 2024-08-15 14:30:00
        "%d/%m/%Y %H:%M:%S",  # 15/08/2024 14:30:00
        "%m/%d/%Y %H:%M:%S",  # 08/15/2024 14:30:00
        "%Y-%m-%d %H:%M",     # 2024-08-15 14:30
        "%d/%m/%Y %H:%M",     # 15/08/2024 14:30
    ]
    
    # Try each format until one works
    for date_format in date_formats:
        try:
            return datetime.datetime.strptime(date_str, date_format).date()
        except (ValueError, TypeError):
            continue
    
    return None


def recalculate_goalkeeper_stats(filtered_player, filtered_matches):
    """
    Recalculate goalkeeper statistics from filtered matches.
    
    Args:
        filtered_player: Player data dictionary to update
        filtered_matches: List of filtered match data
    """
    total_conceded = sum(match.get("Conceded goals", 0) for match in filtered_matches)
    total_saves = sum(match.get("Saves", 0) for match in filtered_matches)
    total_shots_against = sum(match.get("Shots against", 0) for match in filtered_matches)
    
    # Calculate derived metrics
    save_percentage = (total_saves / total_shots_against * 100) if total_shots_against > 0 else 0
    goals_conceded_per_90 = (total_conceded / filtered_player["minutes"] * 90) if filtered_player["minutes"] > 0 else 0
    
    # Update player statistics
    filtered_player["conceded_goals"] = total_conceded
    filtered_player["saves"] = total_saves
    filtered_player["shots_against"] = total_shots_against
    filtered_player["save_percentage"] = save_percentage
    filtered_player["goals_conceded_per_90"] = goals_conceded_per_90


def recalculate_outfield_stats(filtered_player, filtered_matches):
    """
    Recalculate outfield player statistics from filtered matches.
    
    Args:
        filtered_player: Player data dictionary to update
        filtered_matches: List of filtered match data
    """
    # Basic offensive stats
    total_goals = sum(match.get("Goals", 0) for match in filtered_matches)
    total_assists = sum(match.get("Assists", 0) for match in filtered_matches)
    total_shots = sum(match.get("Shots", 0) for match in filtered_matches)
    total_shots_on_target = sum(match.get("Shots On Target", 0) for match in filtered_matches)
    total_xg = sum(match.get("xG", 0) for match in filtered_matches)
    
    # General action stats
    total_actions = sum(match.get("Total actions", 0) for match in filtered_matches)
    total_actions_successful = sum(match.get("Total actions successful", 0) for match in filtered_matches)
    
    # Passing stats
    total_passes = sum(match.get("Passes", 0) for match in filtered_matches)
    total_passes_accurate = sum(match.get("Passes accurate", 0) for match in filtered_matches)
    total_long_passes = sum(match.get("Long passes", 0) for match in filtered_matches)
    total_long_passes_accurate = sum(match.get("Long passes accurate", 0) for match in filtered_matches)
    
    # Crossing stats
    total_crosses = sum(match.get("Crosses", 0) for match in filtered_matches)
    total_crosses_accurate = sum(match.get("Crosses accurate", 0) for match in filtered_matches)
    
    # Dribbling stats
    total_dribbles = sum(match.get("Dribbles", 0) for match in filtered_matches)
    total_dribbles_successful = sum(match.get("Dribbles successful", 0) for match in filtered_matches)
    
    # Dueling stats
    total_duels = sum(match.get("Duels", 0) for match in filtered_matches)
    total_duels_won = sum(match.get("Duels won", 0) for match in filtered_matches)
    total_aerial_duels = sum(match.get("Aerial duels", 0) for match in filtered_matches)
    total_aerial_duels_won = sum(match.get("Aerial duels won", 0) for match in filtered_matches)
    
    # Defensive stats
    total_interceptions = sum(match.get("Interceptions", 0) for match in filtered_matches)
    total_losses = sum(match.get("Losses", 0) for match in filtered_matches)
    total_losses_own_half = sum(match.get("Losses own half", 0) for match in filtered_matches)
    total_recoveries = sum(match.get("Recoveries", 0) for match in filtered_matches)
    total_recoveries_opp_half = sum(match.get("Recoveries opp. half", 0) for match in filtered_matches)
    
    # Count cards
    yellow_cards = sum(1 for match in filtered_matches if match.get('Yellow card', 0) > 0)
    red_cards = sum(1 for match in filtered_matches if match.get('Red card', 0) > 0)
    
    # Calculate success rates
    total_actions_success_rate = (total_actions_successful / total_actions * 100) if total_actions > 0 else 0
    pass_accuracy = (total_passes_accurate / total_passes * 100) if total_passes > 0 else 0
    long_pass_accuracy = (total_long_passes_accurate / total_long_passes * 100) if total_long_passes > 0 else 0
    cross_accuracy = (total_crosses_accurate / total_crosses * 100) if total_crosses > 0 else 0
    dribble_success_rate = (total_dribbles_successful / total_dribbles * 100) if total_dribbles > 0 else 0
    duel_success_rate = (total_duels_won / total_duels * 100) if total_duels > 0 else 0
    aerial_duel_success_rate = (total_aerial_duels_won / total_aerial_duels * 100) if total_aerial_duels > 0 else 0
    shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0
    
    # Update player statistics
    # General stats
    filtered_player["total_actions"] = total_actions
    filtered_player["total_actions_successful"] = total_actions_successful
    
    # Offensive stats
    filtered_player["goals"] = total_goals
    filtered_player["assists"] = total_assists
    filtered_player["shots"] = total_shots
    filtered_player["shots_on_target"] = total_shots_on_target
    filtered_player["xg"] = total_xg
    
    # Passing stats
    filtered_player["passes"] = total_passes
    filtered_player["passes_accurate"] = total_passes_accurate
    filtered_player["long_passes"] = total_long_passes
    filtered_player["long_passes_accurate"] = total_long_passes_accurate
    
    # Crossing stats
    filtered_player["crosses"] = total_crosses
    filtered_player["crosses_accurate"] = total_crosses_accurate
    
    # Dribbling stats
    filtered_player["dribbles"] = total_dribbles
    filtered_player["dribbles_successful"] = total_dribbles_successful
    
    # Dueling stats
    filtered_player["duels"] = total_duels
    filtered_player["duels_won"] = total_duels_won
    filtered_player["aerial_duels"] = total_aerial_duels
    filtered_player["aerial_duels_won"] = total_aerial_duels_won
    
    # Defensive stats
    filtered_player["interceptions"] = total_interceptions
    filtered_player["losses"] = total_losses
    filtered_player["losses_own_half"] = total_losses_own_half
    filtered_player["recoveries"] = total_recoveries
    filtered_player["recoveries_opp_half"] = total_recoveries_opp_half
    
    # Cards
    filtered_player["yellow_cards"] = yellow_cards
    filtered_player["red_cards"] = red_cards
    
    # Success rates
    filtered_player["total_actions_success_rate"] = total_actions_success_rate
    filtered_player["pass_accuracy"] = pass_accuracy
    filtered_player["long_pass_accuracy"] = long_pass_accuracy
    filtered_player["cross_accuracy"] = cross_accuracy
    filtered_player["dribble_success_rate"] = dribble_success_rate
    filtered_player["duel_success_rate"] = duel_success_rate
    filtered_player["aerial_duel_success_rate"] = aerial_duel_success_rate
    filtered_player["shot_accuracy"] = shot_accuracy


def apply_date_filter(player_data, start_date, end_date):
    """
    Apply date filter to player data and recalculate statistics.
    
    Args:
        player_data: Dictionary of player data
        start_date: Start date for filtering
        end_date: End date for filtering
    
    Returns:
        Filtered player data with recalculated statistics
    """
    filtered_data = {}
    
    for player_name, player_stats in player_data.items():
        # Create a deep copy to avoid reference issues
        filtered_player = copy.deepcopy(player_stats)
        
        # Filter match data
        filtered_matches = []
        for match in player_stats.get("match_data", []):
            include_match = True
            
            # Apply date filter
            if "Date" in match:
                try:
                    date_str = str(match["Date"]).strip()
                    match_date = parse_date_multiple_formats(date_str)
                    
                    if match_date:
                        if match_date < start_date or match_date > end_date:
                            include_match = False
                    else:
                        # If we can't parse the date, log it for debugging and keep the match
                        print(f"Could not parse date '{date_str}' for player {player_name}")
                        
                except Exception as e:
                    # If any error occurs, log it and keep the match
                    print(f"Date parsing error for player {player_name}: {match.get('Date', 'No Date')} - Error: {e}")
            
            if include_match:
                filtered_matches.append(match)
        
        # Only include player if they have matches after filtering
        if filtered_matches:
            # Update match data
            filtered_player["match_data"] = filtered_matches
            
            # Recalculate aggregate statistics based on player type
            total_matches = len(filtered_matches)
            total_minutes = sum(match.get("Minutes played", 0) for match in filtered_matches)
            
            # Update basic info
            filtered_player["matches"] = total_matches
            filtered_player["minutes"] = total_minutes
            
            # Check if this is goalkeeper or outfield player data
            if "saves" in player_stats:  # Goalkeeper data
                recalculate_goalkeeper_stats(filtered_player, filtered_matches)
            else:  # Outfield player data
                recalculate_outfield_stats(filtered_player, filtered_matches)
            
            filtered_data[player_name] = filtered_player
    
    return filtered_data


def render_debug_interface(player_data, original_player_count, filtered_player_count, start_date, end_date):
    """
    Render debug interface for date filter verification.
    
    Args:
        player_data: Filtered player data
        original_player_count: Number of players before filtering
        filtered_player_count: Number of players after filtering
        start_date: Start date used for filtering
        end_date: End date used for filtering
    """
    if st.checkbox("🔍 Show Date Filter Debug Info", value=False):
        st.markdown("### 🔍 Date Filter Debug Information")
        
        # Show overall filtering results
        st.markdown(f"**Original player count**: {original_player_count}")
        st.markdown(f"**Filtered player count**: {filtered_player_count}")
        st.markdown(f"**Date range**: {start_date} to {end_date}")
        
        # Check if specific player is in the data (example with David da Silva)
        test_player = "David da Silva"
        if test_player in player_data:
            player_stats = player_data[test_player]
            st.markdown(f"**🎯 {test_player} Debug Info (After Date Filter):**")
            st.markdown(f"**Filtered Minutes**: {player_stats.get('minutes', 'N/A')}")
            st.markdown(f"**Filtered Matches**: {player_stats.get('matches', 'N/A')}")
            
            # Show match data details
            match_data = player_stats.get('match_data', [])
            st.markdown(f"**Match Data Count**: {len(match_data)}")
            
            if match_data:
                # Calculate total minutes from match data to verify
                total_minutes_from_matches = sum(match.get('Minutes played', 0) for match in match_data)
                st.markdown(f"**Total Minutes from Match Data**: {total_minutes_from_matches}")
                
                # Show date range
                dates = [match.get('Date', '') for match in match_data if match.get('Date')]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    st.markdown(f"**Date Range in Filtered Data**: {min_date} to {max_date}")
                
                # Show first few matches for verification
                st.markdown("**First 3 Filtered Matches:**")
                for i, match in enumerate(match_data[:3]):
                    date = match.get('Date', 'No Date')
                    minutes = match.get('Minutes played', 0)
                    st.write(f"  {i+1}. {date} - {minutes} minutes")
                
                # Check if minutes match
                if player_stats.get('minutes', 0) == total_minutes_from_matches:
                    st.success("✅ Minutes calculation is consistent!")
                else:
                    st.error(f"❌ Minutes mismatch! Stored: {player_stats.get('minutes', 0)}, Calculated: {total_minutes_from_matches}")
        else:
            st.warning(f"{test_player} not found in filtered data")
            
            # Show available players for debugging
            available_players = list(player_data.keys())[:10]  # Show first 10
            st.markdown(f"**Available players (first 10)**: {', '.join(available_players)}")


# Example usage in a Streamlit component
def example_usage():
    """
    Example of how to use the date filter in a Streamlit component.
    """
    # Render date filter UI
    use_date_filter, start_date, end_date = render_date_filter_ui()
    
    # Apply date filter if enabled
    if use_date_filter and start_date and end_date:
        st.info(f"📊 Filtering data from {start_date} to {end_date}")
        original_player_count = len(player_data)
        player_data = apply_date_filter(player_data, start_date, end_date)
        
        # Update players list after filtering
        players = list(player_data.keys())
        players.sort()
        
        # Show filtering results
        filtered_player_count = len(players)
        st.success(f"✅ Date filter applied: {filtered_player_count} players found (was {original_player_count})")
        
        # Render debug interface
        render_debug_interface(player_data, original_player_count, filtered_player_count, start_date, end_date)
        
        if not players:
            st.warning("No players found with matches in the selected date range.")
            return
    
    # Continue with your component logic using the filtered player_data
    # ...
