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

    # Minutes filter and top 10 option
    col1, col2 = st.columns(2)
    with col1:
        min_minutes = st.slider(
            "Minimum Minutes Played",
            min_value=0,
            max_value=3000,
            value=90,
            step=90,
            help="Filter players by minimum minutes played"
        )
    with col2:
        show_top_10_only = st.checkbox(
            "Show Top 10 Only",
            value=True,
            help="Display only the top 10 most similar players"
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
            display_similar_players(selected_player, similar_players, selected_stats, per_90_mode, filtered_data, show_top_10_only)
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
                          selected_stats: List[str], per_90_mode: bool, player_data: Dict[str, Dict[str, Any]],
                          show_top_10_only: bool = True):
    """
    Display the similar players in a table format with role-based weight calculations.

    Args:
        selected_player: Name of the selected player
        similar_players: List of (player_name, similarity_score) tuples
        selected_stats: List of stats used for comparison
        per_90_mode: Whether per 90 stats were used
        player_data: Dictionary of all player data
        show_top_10_only: Whether to show only top 10 players
    """
    st.subheader(f"🎯 Similar Players to {selected_player}")

    if per_90_mode:
        st.info("Results based on per 90 minutes statistics")
    else:
        st.info("Results based on total statistics")

    # Determine how many players to show
    max_players = 10 if show_top_10_only else 20
    players_to_show = similar_players[:max_players]

    # Add info about results count
    total_similar = len(similar_players)
    if show_top_10_only and total_similar > 10:
        st.info(f"Showing top 10 of {total_similar} similar players found. Uncheck 'Show Top 10 Only' to see all results.")
    elif not show_top_10_only:
        st.info(f"Showing all {min(total_similar, 20)} similar players found.")
    else:
        st.info(f"Found {total_similar} similar players.")

    # Get role weights and determine position type
    role_weights, position_type = get_role_weights_for_players(selected_player, players_to_show, player_data)

    # Create display data
    display_data = []

    for i, (player_name, similarity_score) in enumerate(players_to_show, 1):
        # Get real player data
        player_stats = player_data.get(player_name, {})

        # Get the latest competition for this player
        latest_competition = "Unknown"
        if "match_data" in player_stats and player_stats["match_data"]:
            # Get the most recent match's competition
            latest_match = max(player_stats["match_data"], key=lambda x: x.get("Date", ""))
            latest_competition = latest_match.get("Competition", "Unknown")

        # Calculate strongest stats values for this player
        strongest_stats_values = {}
        for stat in selected_stats:
            if stat in player_stats:
                value = player_stats[stat]

                # Apply per 90 calculation if needed
                if per_90_mode and stat != "minutes" and "minutes" in player_stats:
                    minutes = player_stats.get("minutes", 0)
                    if minutes > 0:
                        value = (value / minutes) * 90
                        strongest_stats_values[stat] = f"{value:.2f}"
                    else:
                        strongest_stats_values[stat] = "0.00"
                else:
                    strongest_stats_values[stat] = str(value)
            else:
                strongest_stats_values[stat] = "0"

        # Calculate role scores for this player
        role_scores = calculate_role_scores(player_name, player_stats, role_weights, player_data, per_90_mode)

        # Create base display data
        player_display_data = {
            "Rank": i,
            "Player": player_name,
            "Team": player_stats.get("team", "Unknown"),
            "Competition": latest_competition,
            "Position": player_stats.get("position", "Unknown"),
            "Age": player_stats.get("age", 0),
            "Minutes": player_stats.get("minutes", 0),
            "Similarity Score": similarity_score * 100  # Convert to percentage
        }

        # Add role scores as dynamic columns
        for role_name, score in role_scores.items():
            player_display_data[f"{role_name} Score"] = score

        # Add individual strongest stats columns after role columns
        for stat in selected_stats:
            stat_display_name = stat.replace("_", " ").title()
            player_display_data[stat_display_name] = strongest_stats_values.get(stat, "0")

        display_data.append(player_display_data)
    
    if display_data:
        df = pd.DataFrame(display_data)

        # Configure base columns
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

        # Add dynamic role score columns
        for role_name in role_weights.keys():
            column_name = f"{role_name} Score"
            column_config[column_name] = st.column_config.ProgressColumn(
                role_name,
                help=f"Role score for {role_name} playing style",
                min_value=0,
                max_value=100,
                format="%.1f%%"
            )

        # Add individual strongest stats columns after role columns
        for stat in selected_stats:
            stat_display_name = stat.replace("_", " ").title()

            # Determine if this is a numeric stat for proper formatting
            if per_90_mode and stat != "minutes":
                column_config[stat_display_name] = st.column_config.NumberColumn(
                    stat_display_name,
                    help=f"{stat_display_name} per 90 minutes",
                    format="%.2f"
                )
            else:
                # Check if the stat values are numeric
                sample_values = [player_data[p[0]].get(stat, 0) for p in players_to_show[:3] if p[0] in player_data]
                if sample_values and all(isinstance(v, (int, float)) for v in sample_values):
                    column_config[stat_display_name] = st.column_config.NumberColumn(
                        stat_display_name,
                        help=f"{stat_display_name} total value",
                        format="%d" if all(isinstance(v, int) or v.is_integer() for v in sample_values if isinstance(v, (int, float))) else "%.1f"
                    )
                else:
                    column_config[stat_display_name] = st.column_config.TextColumn(
                        stat_display_name,
                        help=f"{stat_display_name} value"
                    )

        # Display the dataframe
        st.dataframe(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True
        )

        # Add role analysis insights
        st.subheader("🎭 Role Analysis Insights")

        role_insights = generate_role_insights(position_type, role_weights, per_90_mode)
        with st.expander("📊 **Role Weight Explanations**", expanded=False):
            st.markdown(role_insights)

        # Add AI insight analysis for top 3 results
        if len(similar_players) >= 1:
            st.subheader("🤖 AI Insights & Analysis")

            # Get top 3 players (or less if not available)
            top_players = similar_players[:3]

            # Generate AI insights
            ai_insights = generate_similarity_insights(
                selected_player,
                top_players,
                selected_stats,
                per_90_mode,
                player_data
            )

            # Display insights in an expandable section
            with st.expander("📊 **Detailed Analysis & Insights**", expanded=True):
                st.markdown(ai_insights)
        else:
            st.warning("No similar players found to generate insights.")
        
        # Show stats used for comparison
        st.subheader("📊 Stats Used for Comparison")
        stats_text = ", ".join([stat.replace("_", " ").title() for stat in selected_stats])
        mode_text = " (per 90 minutes)" if per_90_mode else " (total values)"
        st.info(f"Similarity calculated based on: {stats_text}{mode_text}")
        st.info("💡 **Individual stat columns** show the actual values for each of the strongest stats used in the similarity calculation.")
    else:
        st.warning("No similar players found.")


def generate_similarity_insights(selected_player: str, top_players: List[Tuple[str, float]],
                                selected_stats: List[str], per_90_mode: bool,
                                player_data: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate AI insights comparing the selected player with top similar players.

    Args:
        selected_player: Name of the selected player
        top_players: List of (player_name, similarity_score) tuples for top similar players
        selected_stats: List of stats used for comparison
        per_90_mode: Whether per 90 stats were used
        player_data: Dictionary of all player data

    Returns:
        Formatted markdown string with AI insights
    """
    if not top_players or selected_player not in player_data:
        return "**No insights available** - Insufficient data for analysis."

    # Get selected player data
    selected_player_stats = player_data[selected_player]

    # Prepare insights
    insights = []

    # Header
    mode_text = "per 90 minutes" if per_90_mode else "total"
    insights.append(f"## 🎯 Similarity Analysis for **{selected_player}**")
    insights.append(f"*Analysis based on {mode_text} statistics*")
    insights.append("")

    # Player overview
    selected_team = selected_player_stats.get("team", "Unknown")
    selected_position = selected_player_stats.get("position", "Unknown")
    selected_age = selected_player_stats.get("age", "Unknown")

    insights.append(f"**Player Profile:** {selected_position} | {selected_team} | Age: {selected_age}")
    insights.append("")

    # Strongest stats analysis
    insights.append("### 💪 Strongest Statistical Attributes")
    strongest_stats_values = []
    for stat in selected_stats:
        if stat in selected_player_stats:
            value = selected_player_stats[stat]
            if per_90_mode and stat != "minutes" and "minutes" in selected_player_stats:
                minutes = selected_player_stats.get("minutes", 0)
                if minutes > 0:
                    value = (value / minutes) * 90
            strongest_stats_values.append((stat, value))

    for stat, value in strongest_stats_values:
        stat_display = stat.replace("_", " ").title()
        if per_90_mode and stat != "minutes":
            insights.append(f"- **{stat_display}**: {value:.2f} per 90 minutes")
        else:
            insights.append(f"- **{stat_display}**: {value}")

    insights.append("")

    # Top similar players analysis
    insights.append("### 🔍 Most Similar Players")

    for i, (player_name, similarity_score) in enumerate(top_players, 1):
        if player_name in player_data:
            player_stats = player_data[player_name]
            team = player_stats.get("team", "Unknown")
            position = player_stats.get("position", "Unknown")
            age = player_stats.get("age", "Unknown")

            insights.append(f"**{i}. {player_name}** ({similarity_score*100:.1f}% similarity)")
            insights.append(f"   - *{position} | {team} | Age: {age}*")

            # Compare key stats
            stat_comparisons = []
            for stat in selected_stats[:3]:  # Show top 3 stats
                if stat in player_stats and stat in selected_player_stats:
                    player_value = player_stats[stat]
                    selected_value = selected_player_stats[stat]

                    # Apply per 90 calculation if needed
                    if per_90_mode and stat != "minutes":
                        if "minutes" in player_stats and player_stats["minutes"] > 0:
                            player_value = (player_value / player_stats["minutes"]) * 90
                        if "minutes" in selected_player_stats and selected_player_stats["minutes"] > 0:
                            selected_value = (selected_value / selected_player_stats["minutes"]) * 90

                    stat_display = stat.replace("_", " ").title()
                    if per_90_mode and stat != "minutes":
                        stat_comparisons.append(f"{stat_display}: {player_value:.2f} vs {selected_value:.2f}")
                    else:
                        stat_comparisons.append(f"{stat_display}: {player_value} vs {selected_value}")

            if stat_comparisons:
                insights.append(f"   - *Key Stats: {' | '.join(stat_comparisons)}*")

            insights.append("")

    # Insights and recommendations
    insights.append("### 🧠 Key Insights")

    if len(top_players) >= 3:
        # Analyze similarity patterns
        high_similarity = [p for p in top_players if p[1] > 0.8]
        medium_similarity = [p for p in top_players if 0.6 <= p[1] <= 0.8]

        if high_similarity:
            insights.append(f"- **Strong Similarity Pattern**: {len(high_similarity)} player(s) show very high similarity (>80%), indicating a clear playing style match.")

        if medium_similarity:
            insights.append(f"- **Moderate Similarity**: {len(medium_similarity)} player(s) show good similarity (60-80%), suggesting similar roles but with some variations.")

        # Position analysis
        similar_positions = [player_data[p[0]].get("position", "Unknown") for p in top_players if p[0] in player_data]
        unique_positions = list(set(similar_positions))

        if len(unique_positions) == 1 and unique_positions[0] == selected_position:
            insights.append(f"- **Position Consistency**: All similar players play the same position ({selected_position}), confirming role-specific similarity.")
        elif len(unique_positions) > 1:
            insights.append(f"- **Cross-Position Similarity**: Similar players span multiple positions ({', '.join(unique_positions)}), indicating versatile playing style.")

        # Team diversity analysis
        similar_teams = [player_data[p[0]].get("team", "Unknown") for p in top_players if p[0] in player_data]
        unique_teams = list(set(similar_teams))

        if len(unique_teams) == len(top_players):
            insights.append(f"- **Team Diversity**: Similar players come from different teams, suggesting the playing style transcends team tactics.")
        else:
            insights.append(f"- **Team Clustering**: Some similar players share teams, which may indicate tactical system influence.")

    # Recommendations
    insights.append("")
    insights.append("### 💡 Recommendations")

    if top_players:
        best_match = top_players[0]
        insights.append(f"- **Best Match**: **{best_match[0]}** ({best_match[1]*100:.1f}% similarity) represents the closest playing style match.")

        if len(top_players) >= 2:
            insights.append(f"- **Alternative Options**: Consider **{top_players[1][0]}** and **{top_players[2][0] if len(top_players) >= 3 else 'others'}** as additional similar players with different team contexts.")

        insights.append(f"- **Scouting Focus**: Use these similar players as benchmarks for performance evaluation and tactical fit assessment.")

        if per_90_mode:
            insights.append(f"- **Performance Context**: Per-90-minute analysis provides normalized comparison, ideal for players with different playing time.")
        else:
            insights.append(f"- **Volume Analysis**: Total statistics comparison shows overall contribution and consistency across the season.")

    return "\n".join(insights)


def get_role_weights_for_players(selected_player: str, players_to_show: List[Tuple[str, float]],
                                player_data: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, float]], str]:
    """
    Get appropriate role weights based on player positions.

    Args:
        selected_player: Name of the selected player
        players_to_show: List of (player_name, similarity_score) tuples
        player_data: Dictionary of all player data

    Returns:
        Tuple of (role_weights_dict, position_type)
    """
    # Get selected player position
    selected_position = player_data.get(selected_player, {}).get("position", "")

    # Define role weights for different positions
    center_forward_role_weights = {
        "Advance Forward": {
            "goals": 0.3,
            "shots": 0.2,
            "shots_on_target": 0.15,
            "dribbles_successful": 0.15,
            "passes": 0.1,
            "minutes": 0.1
        },
        "Pressing Forward": {
            "duels_won": 0.25,
            "recoveries": 0.2,
            "interceptions": 0.2,
            "goals": 0.15,
            "shots": 0.1,
            "duel_success_rate": 0.1
        },
        "Deep-lying Forward": {
            "assists": 0.25,
            "passes_accurate": 0.25,
            "pass_accuracy": 0.15,
            "passes": 0.15,
            "dribbles": 0.1,
            "goals": 0.1
        },
        "Poacher": {
            "goals": 0.5,
            "shots": 0.3,
            "shots_on_target": 0.2
        }
    }

    center_back_role_weights = {
        "No-Nonsense Centre-Back": {
            "duels_won": 0.25,
            "duel_success_rate": 0.2,
            "recoveries": 0.2,
            "interceptions": 0.15,
            "duels": 0.1,
            "passes_accurate": 0.1
        },
        "Central Defender": {
            "duels_won": 0.2,
            "duel_success_rate": 0.2,
            "interceptions": 0.15,
            "recoveries": 0.15,
            "passes_accurate": 0.15,
            "duels": 0.1,
            "pass_accuracy": 0.05
        },
        "Ball Playing Defender": {
            "passes_accurate": 0.25,
            "pass_accuracy": 0.2,
            "passes": 0.15,
            "duels_won": 0.15,
            "duel_success_rate": 0.1,
            "interceptions": 0.1,
            "recoveries": 0.05
        }
    }

    # Define goalkeeper role weights
    goalkeeper_role_weights = {
        "Shot Stopper": {
            "saves": 0.3,
            "saves_with_reflexes": 0.25,
            "conceded_goals": -0.2,
            "xcg": -0.15,
            "shots_against": 0.1
        },
        "Sweeper Keeper": {
            "exits": 0.25,
            "long_passes_accurate": 0.2,
            "short_passes_accurate": 0.15,
            "goal_kicks": 0.1,
            "short_goal_kicks": 0.05,
            "long_goal_kicks": 0.05
        }
    }

    # Determine position type and return appropriate weights
    if selected_position == "GK":
        return goalkeeper_role_weights, "Goalkeeper"
    elif "CF" in selected_position or "FW" in selected_position:
        return center_forward_role_weights, "Center Forward"
    elif "CB" in selected_position or "DF" in selected_position:
        return center_back_role_weights, "Center Back"
    else:
        # Default to center forward for other outfield positions
        return center_forward_role_weights, "Outfield"


def calculate_role_scores(player_name: str, player_stats: Dict[str, Any], role_weights: Dict[str, Dict[str, float]],
                         all_players_data: Dict[str, Dict[str, Any]], per_90_mode: bool) -> Dict[str, float]:
    """
    Calculate role scores for a player based on role weights.

    Args:
        player_name: Name of the player
        player_stats: Player's statistics
        role_weights: Dictionary of role weights
        all_players_data: All players data for normalization
        per_90_mode: Whether to use per 90 calculations

    Returns:
        Dictionary of role scores
    """
    role_scores = {}

    for role_name, weights in role_weights.items():
        total_score = 0
        total_weight = 0

        for stat, weight in weights.items():
            if stat in player_stats:
                value = player_stats[stat]

                # Apply per 90 calculation if needed
                if per_90_mode and stat != "minutes" and "minutes" in player_stats:
                    minutes = player_stats.get("minutes", 0)
                    if minutes > 0:
                        value = (value / minutes) * 90

                # Get all values for normalization
                all_values = []
                for other_player, other_stats in all_players_data.items():
                    if stat in other_stats:
                        other_value = other_stats[stat]
                        if per_90_mode and stat != "minutes" and "minutes" in other_stats:
                            other_minutes = other_stats.get("minutes", 0)
                            if other_minutes > 0:
                                other_value = (other_value / other_minutes) * 90
                        all_values.append(other_value)

                if len(all_values) > 1:
                    # Normalize to 0-1 scale
                    min_val = min(all_values)
                    max_val = max(all_values)
                    if max_val > min_val:
                        normalized_value = (value - min_val) / (max_val - min_val)
                    else:
                        normalized_value = 0.5

                    # Handle negative weights (lower is better)
                    if weight < 0:
                        normalized_value = 1 - normalized_value
                        weight = abs(weight)

                    total_score += normalized_value * weight
                    total_weight += weight

        # Calculate final score
        if total_weight > 0:
            role_scores[role_name] = (total_score / total_weight) * 100
        else:
            role_scores[role_name] = 0

    return role_scores


def generate_role_insights(position_type: str, role_weights: Dict[str, Dict[str, float]], per_90_mode: bool) -> str:
    """
    Generate insights about role weights and their meanings.

    Args:
        position_type: Type of position (Goalkeeper, Center Forward, etc.)
        role_weights: Dictionary of role weights
        per_90_mode: Whether per 90 stats are being used

    Returns:
        Formatted markdown string with role insights
    """
    insights = []

    # Header
    mode_text = "per 90 minutes" if per_90_mode else "total"
    insights.append(f"## 🎭 {position_type} Role Analysis")
    insights.append(f"*Analysis based on {mode_text} statistics*")
    insights.append("")

    # Role explanations
    insights.append("### 📋 Role Definitions")

    if position_type == "Goalkeeper":
        insights.append("**Shot Stopper**: Focuses on making saves and preventing goals through reflexes and positioning.")
        insights.append("- Emphasizes saves, reflexes, and shot-stopping ability")
        insights.append("- Lower goals conceded and xCG are better")
        insights.append("")
        insights.append("**Sweeper Keeper**: Acts as an extra defender with good distribution and game reading.")
        insights.append("- Emphasizes exits, passing accuracy, and distribution")
        insights.append("- Good with both short and long passing")
        insights.append("")

    elif position_type == "Center Forward":
        insights.append("**Advance Forward**: Focuses on goal scoring and attacking threat.")
        insights.append("- Emphasizes goals, shots, and dribbling ability")
        insights.append("- High attacking output and individual skill")
        insights.append("")
        insights.append("**Pressing Forward**: Focuses on defensive work and pressing.")
        insights.append("- Emphasizes duels won, recoveries, and interceptions")
        insights.append("- Combines goal threat with defensive contribution")
        insights.append("")
        insights.append("**Deep-lying Forward**: Focuses on playmaking and assists.")
        insights.append("- Emphasizes assists, passing accuracy, and creativity")
        insights.append("- Links play between midfield and attack")
        insights.append("")
        insights.append("**Poacher**: Pure goal scorer with clinical finishing.")
        insights.append("- Heavily emphasizes goals and shots")
        insights.append("- Specialist finisher in the penalty area")
        insights.append("")

    elif position_type == "Center Back":
        insights.append("**No-Nonsense Centre-Back**: Focuses on defensive fundamentals.")
        insights.append("- Emphasizes duels won, recoveries, and interceptions")
        insights.append("- Strong physical presence and defensive actions")
        insights.append("")
        insights.append("**Central Defender**: Balanced defensive approach.")
        insights.append("- Combines defensive actions with some passing ability")
        insights.append("- Well-rounded defensive performance")
        insights.append("")
        insights.append("**Ball Playing Defender**: Focuses on distribution and passing.")
        insights.append("- Emphasizes passing accuracy and ball distribution")
        insights.append("- Builds play from the back with technical ability")
        insights.append("")

    # Weight explanations
    insights.append("### ⚖️ How Role Scores Work")
    insights.append("- **Normalization**: All statistics are normalized to 0-100% scale compared to other players")
    insights.append("- **Weighting**: Each statistic is weighted based on its importance for the role")
    insights.append("- **Negative Weights**: Some stats use negative weights (lower values are better)")
    insights.append("- **Final Score**: Weighted average of all relevant statistics for each role")
    insights.append("")

    # Detailed weight breakdown
    insights.append("### 📊 Weight Breakdown")
    for role_name, weights in role_weights.items():
        insights.append(f"**{role_name}**:")
        sorted_weights = sorted(weights.items(), key=lambda x: abs(x[1]), reverse=True)
        for stat, weight in sorted_weights:
            stat_display = stat.replace("_", " ").title()
            weight_percent = abs(weight) * 100
            direction = "↓ Lower is better" if weight < 0 else "↑ Higher is better"
            insights.append(f"- {stat_display}: {weight_percent:.0f}% {direction}")
        insights.append("")

    # Usage tips
    insights.append("### 💡 How to Use Role Scores")
    insights.append("- **Compare across roles**: See which playing style suits each player best")
    insights.append("- **Identify specialists**: Players with high scores in specific roles")
    insights.append("- **Find versatile players**: Players with good scores across multiple roles")
    insights.append("- **Tactical fit**: Match player strengths to your tactical system")

    if per_90_mode:
        insights.append("- **Per 90 analysis**: Normalized for playing time, ideal for comparing players with different minutes")
    else:
        insights.append("- **Total statistics**: Shows overall contribution and consistency across the season")

    return "\n".join(insights)
