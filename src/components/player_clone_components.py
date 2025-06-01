"""
Player Clone Components

This module provides functionality to find similar players based on a selected player's strongest stats.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


def render_player_clone(data_provider, filtered_data: Dict[str, Dict[str, Any]], position_type: str):
    """
    Render the Player Clone page.
    
    Args:
        data_provider: The data provider object (RAG system)
        filtered_data: Pre-filtered player data
        position_type: Type of players (Goalkeepers, All Outfield, etc.)
    """
    # Add CSS for better styling
    st.markdown("""
    <style>
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .stDataFrame {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stDataFrame > div {
        width: 100% !important;
        overflow-x: auto !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("🔍 Find Similar Player")
    st.markdown("Find players with similar playing styles based on strongest statistical attributes.")
    
    # Get player data
    if not filtered_data:
        st.warning("No players found with the current filters. Try adjusting the global filters in the sidebar.")
        return
    
    players = sorted(list(filtered_data.keys()))
    
    if len(players) < 2:
        st.warning("Not enough players found with the current filters. Need at least 2 players.")
        return
    
    # Player selection
    st.subheader("🎯 Select Player")
    selected_player = st.selectbox(
        "Choose a player to find similar players:",
        players,
        help="Select the player whose playing style you want to match"
    )
    
    if not selected_player:
        return
    
    # Configuration
    st.subheader("⚙️ Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        per_90_mode = st.checkbox(
            "Use Per 90 Stats", 
            value=False, 
            help="Calculate statistics per 90 minutes of play instead of total stats"
        )
    
    with col2:
        min_stats = st.slider(
            "Minimum Stats to Consider",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of strongest stats to use for similarity calculation"
        )
    
    # Get strongest stats for the selected player
    strongest_stats = get_strongest_stats(selected_player, filtered_data, position_type, per_90_mode, min_stats)
    
    if not strongest_stats:
        st.error("Could not determine strongest stats for the selected player.")
        return
    
    # Display strongest stats
    st.subheader(f"💪 Strongest Stats for {selected_player}")
    
    # Create multiselect with strongest stats pre-selected
    all_available_stats = get_available_stats(position_type)
    
    selected_stats = st.multiselect(
        "Stats to Compare:",
        all_available_stats,
        default=strongest_stats,
        help="These are the player's strongest stats. You can modify the selection."
    )
    
    if len(selected_stats) < 3:
        st.warning("Please select at least 3 stats for comparison.")
        return
    
    # Additional filters
    st.subheader("🔧 Additional Filters")
    
    # Age range filter
    col1, col2 = st.columns(2)
    with col1:
        min_age = st.number_input("Minimum Age", min_value=16, max_value=45, value=16)
    with col2:
        max_age = st.number_input("Maximum Age", min_value=16, max_value=45, value=45)
    
    # Minutes filter
    min_minutes = st.slider(
        "Minimum Minutes Played",
        min_value=0,
        max_value=3000,
        value=90,
        step=90,
        help="Filter players by minimum minutes played"
    )
    
    # Calculate and display similar players
    if st.button("🚀 Find Similar Players", type="primary", use_container_width=True):
        similar_players = calculate_similarity(
            selected_player,
            filtered_data,
            selected_stats,
            per_90_mode,
            min_age,
            max_age,
            min_minutes
        )
        
        if similar_players:
            display_similar_players(selected_player, similar_players, selected_stats, per_90_mode, filtered_data)
        else:
            st.warning("No similar players found with the current criteria.")


def get_strongest_stats(player_name: str, player_data: Dict[str, Dict[str, Any]], 
                       position_type: str, per_90_mode: bool, num_stats: int) -> List[str]:
    """
    Get the strongest stats for a player based on percentile rankings.
    
    Args:
        player_name: Name of the player
        player_data: Dictionary of all player data
        position_type: Type of players (Goalkeepers, All Outfield, etc.)
        per_90_mode: Whether to use per 90 stats
        num_stats: Number of strongest stats to return
        
    Returns:
        List of strongest stat names
    """
    if player_name not in player_data:
        return []
    
    player_stats = player_data[player_name]
    available_stats = get_available_stats(position_type)
    
    # Calculate percentiles for all stats
    stat_percentiles = {}
    
    for stat in available_stats:
        if stat not in player_stats:
            continue
            
        # Get all values for this stat
        all_values = []
        for other_player, other_stats in player_data.items():
            if stat in other_stats:
                value = other_stats[stat]
                
                # Apply per 90 calculation if needed
                if per_90_mode and stat != "minutes" and "minutes" in other_stats:
                    minutes = other_stats.get("minutes", 0)
                    if minutes > 0:
                        value = (value / minutes) * 90
                
                all_values.append(value)
        
        if len(all_values) < 2:
            continue
            
        # Get player's value
        player_value = player_stats[stat]
        if per_90_mode and stat != "minutes" and "minutes" in player_stats:
            minutes = player_stats.get("minutes", 0)
            if minutes > 0:
                player_value = (player_value / minutes) * 90
        
        # Calculate percentile
        percentile = (sum(1 for v in all_values if v < player_value) / len(all_values)) * 100
        stat_percentiles[stat] = percentile
    
    # Sort by percentile and return top stats
    sorted_stats = sorted(stat_percentiles.items(), key=lambda x: x[1], reverse=True)
    return [stat for stat, _ in sorted_stats[:num_stats]]


def get_available_stats(position_type: str) -> List[str]:
    """
    Get available stats based on position type.
    
    Args:
        position_type: Type of players
        
    Returns:
        List of available stat names
    """
    if position_type == "Goalkeepers":
        return [
            "saves", "saves_with_reflexes", "conceded_goals", "xcg", "shots_against",
            "exits", "long_passes", "long_passes_accurate", "short_passes", 
            "short_passes_accurate", "goal_kicks", "short_goal_kicks", "long_goal_kicks",
            "xg_against", "prevented_goals", "clean_sheets", "save_rate", "aerial_duels"
        ]
    else:
        return [
            "goals", "assists", "shots", "xg", "passes", "passes_accurate", 
            "long_passes", "long_passes_accurate", "crosses", "crosses_accurate",
            "dribbles", "dribbles_successful", "duels", "duels_won", 
            "aerial_duels", "aerial_duels_won", "interceptions", "losses", 
            "recoveries", "yellow_card", "red_card"
        ]


def calculate_similarity(selected_player: str, player_data: Dict[str, Dict[str, Any]], 
                        selected_stats: List[str], per_90_mode: bool,
                        min_age: int, max_age: int, min_minutes: int) -> List[Tuple[str, float]]:
    """
    Calculate similarity scores between selected player and all other players.
    
    Args:
        selected_player: Name of the selected player
        player_data: Dictionary of all player data
        selected_stats: List of stats to use for comparison
        per_90_mode: Whether to use per 90 stats
        min_age: Minimum age filter
        max_age: Maximum age filter
        min_minutes: Minimum minutes filter
        
    Returns:
        List of tuples (player_name, similarity_score) sorted by similarity
    """
    if selected_player not in player_data:
        return []
    
    # Prepare data for similarity calculation
    players_for_comparison = []
    stat_matrix = []
    
    # Get selected player's stats
    selected_stats_values = []
    selected_player_data = player_data[selected_player]
    
    for stat in selected_stats:
        if stat in selected_player_data:
            value = selected_player_data[stat]
            
            # Apply per 90 calculation if needed
            if per_90_mode and stat != "minutes" and "minutes" in selected_player_data:
                minutes = selected_player_data.get("minutes", 0)
                if minutes > 0:
                    value = (value / minutes) * 90
            
            selected_stats_values.append(value)
        else:
            selected_stats_values.append(0)
    
    # Collect data for all other players
    for player_name, player_stats in player_data.items():
        if player_name == selected_player:
            continue
            
        # Apply filters
        age = player_stats.get("age", 0)
        minutes = player_stats.get("minutes", 0)
        
        if age < min_age or age > max_age or minutes < min_minutes:
            continue
        
        # Get stats for this player
        player_stat_values = []
        for stat in selected_stats:
            if stat in player_stats:
                value = player_stats[stat]
                
                # Apply per 90 calculation if needed
                if per_90_mode and stat != "minutes" and "minutes" in player_stats:
                    player_minutes = player_stats.get("minutes", 0)
                    if player_minutes > 0:
                        value = (value / player_minutes) * 90
                
                player_stat_values.append(value)
            else:
                player_stat_values.append(0)
        
        players_for_comparison.append(player_name)
        stat_matrix.append(player_stat_values)
    
    if not stat_matrix:
        return []
    
    # Normalize the data
    all_data = [selected_stats_values] + stat_matrix
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(all_data)
    
    # Calculate cosine similarity
    selected_normalized = normalized_data[0].reshape(1, -1)
    others_normalized = normalized_data[1:]
    
    similarities = cosine_similarity(selected_normalized, others_normalized)[0]
    
    # Create list of (player, similarity) tuples
    similar_players = list(zip(players_for_comparison, similarities))
    
    # Sort by similarity (descending)
    similar_players.sort(key=lambda x: x[1], reverse=True)
    
    return similar_players


def display_similar_players(selected_player: str, similar_players: List[Tuple[str, float]],
                          selected_stats: List[str], per_90_mode: bool, player_data: Dict[str, Dict[str, Any]]):
    """
    Display the similar players in a table format.

    Args:
        selected_player: Name of the selected player
        similar_players: List of (player_name, similarity_score) tuples
        selected_stats: List of stats used for comparison
        per_90_mode: Whether per 90 stats were used
        player_data: Dictionary of all player data
    """
    st.subheader(f"🎯 Similar Players to {selected_player}")

    if per_90_mode:
        st.info("Results based on per 90 minutes statistics")
    else:
        st.info("Results based on total statistics")

    # Create display data
    display_data = []

    for i, (player_name, similarity_score) in enumerate(similar_players[:20], 1):  # Show top 20
        # Get real player data
        player_stats = player_data.get(player_name, {})

        # Get the latest competition for this player
        latest_competition = "Unknown"
        if "match_data" in player_stats and player_stats["match_data"]:
            # Get the most recent match's competition
            latest_match = max(player_stats["match_data"], key=lambda x: x.get("Date", ""))
            latest_competition = latest_match.get("Competition", "Unknown")

        display_data.append({
            "Rank": i,
            "Player": player_name,
            "Team": player_stats.get("team", "Unknown"),
            "Competition": latest_competition,
            "Position": player_stats.get("position", "Unknown"),
            "Age": player_stats.get("age", 0),
            "Minutes": player_stats.get("minutes", 0),
            "Similarity Score": similarity_score * 100  # Convert to percentage
        })
    
    if display_data:
        df = pd.DataFrame(display_data)
        
        # Configure columns
        column_config = {
            "Rank": st.column_config.NumberColumn("Rank", format="%d"),
            "Player": st.column_config.TextColumn("Player"),
            "Team": st.column_config.TextColumn("Team"),
            "Competition": st.column_config.TextColumn("Competition"),
            "Position": st.column_config.TextColumn("Position"),
            "Age": st.column_config.NumberColumn("Age", format="%d"),
            "Minutes": st.column_config.NumberColumn("Minutes", format="%d"),
            "Similarity Score": st.column_config.ProgressColumn(
                "Similarity Score",
                help="Similarity percentage based on selected stats",
                min_value=0,
                max_value=100,
                format="%.1f%%"
            )
        }
        
        # Display the dataframe
        st.dataframe(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True
        )
        
        # Show stats used for comparison
        st.subheader("📊 Stats Used for Comparison")
        stats_text = ", ".join([stat.replace("_", " ").title() for stat in selected_stats])
        st.info(f"Similarity calculated based on: {stats_text}")
    else:
        st.warning("No similar players found.")
