import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import numpy as np

def render_outfield_player_comparison(rag, filtered_data, position_type="All"):
    """
    Render the outfield player comparison interface.
    Reuses the comparison logic from app_components.py but adapted for outfield players.
    
    Args:
        rag: RAG system instance (OutfieldRAG, ForwardRAG, MidfielderRAG, or DefenderRAG)
        filtered_data: Dictionary of filtered player data
        position_type: Type of position being analyzed ("All", "Forward", "Midfielder", "Defender")
    """
    st.header(f"{position_type} Player Comparison")
    
    if not filtered_data:
        st.warning("No player data available. Please check your data source.")
        return
    
    # Allow selecting up to 3 players
    st.subheader("Select Players to Compare (up to 3)")

    # Add toggle for selection mode and per 90 minutes option
    col1, col2 = st.columns([1, 1])
    with col1:
        selection_mode = st.toggle("Multiselect Mode", value=True)
    with col2:
        per_90_mode = st.toggle("Per 90 Minutes Stats", value=False, 
                               help="Calculate all statistics per 90 minutes of play instead of per match")

    # Get available players
    available_players = list(filtered_data.keys())
    
    if not available_players:
        st.warning("No players available for comparison.")
        return

    # Player selection based on mode
    selected_players = []
    if selection_mode:
        # Multiselect mode
        selected_players = st.multiselect(
            "Select players to compare:",
            available_players,
            max_selections=3,
            help="Choose 2-3 players to compare their statistics"
        )
    else:
        # Individual selection mode
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                player = st.selectbox(
                    f"Player {i+1}:",
                    [""] + available_players,
                    key=f"player_{i}",
                    help=f"Select player {i+1} for comparison"
                )
                if player:
                    selected_players.append(player)

    if len(selected_players) < 2:
        st.info("Please select at least 2 players to compare.")
        return

    # Get available competitions
    available_competitions = set()
    for player in selected_players:
        if player in filtered_data:
            player_data = filtered_data[player]
            if 'competitions' in player_data:
                available_competitions.add(player_data['competitions'])
    
    available_competitions = sorted(list(available_competitions))

    # Competition selection for each selected player
    player_competitions = {}
    if available_competitions and selected_players:
        cols = st.columns(len(selected_players))
        for i, (col, player) in enumerate(zip(cols, selected_players)):
            with col:
                st.write(f"**{player}**")
                selected_comps = st.multiselect(
                    f"Competitions for {player}:",
                    available_competitions,
                    default=available_competitions,  # Default to all competitions
                    key=f"comp_{player}_{i}"
                )
                player_competitions[player] = selected_comps if selected_comps else available_competitions

    # Process player data for comparison
    player_data = {}
    player_stats = []
    
    for player in selected_players:
        if player in filtered_data:
            # Get player data and filter by selected competitions
            raw_data = filtered_data[player]
            
            # Filter match data by selected competitions
            selected_comps = player_competitions.get(player, available_competitions)
            filtered_matches = []
            
            for match in raw_data.get("match_data", []):
                if match.get("Competition") in selected_comps or not selected_comps:
                    filtered_matches.append(match)
            
            if filtered_matches:
                # Calculate statistics from filtered matches
                stats = calculate_outfield_stats(filtered_matches, per_90_mode)
                stats['selected_competitions'] = selected_comps
                player_data[player] = raw_data
                player_stats.append(stats)
            else:
                st.warning(f"No match data found for {player} in selected competitions.")
                return

    if len(player_stats) < 2:
        st.warning("Insufficient data for comparison.")
        return

    # Display comparison charts and analysis
    display_outfield_comparison_charts(selected_players, player_stats, per_90_mode)
    
    # Display detailed comparison table
    display_outfield_detailed_comparison(selected_players, player_stats, per_90_mode)
    
    # Display role analysis for outfield players
    display_outfield_role_analysis(selected_players, player_stats, position_type, per_90_mode)


def calculate_outfield_stats(matches, per_90_mode=False):
    """
    Calculate aggregate statistics for outfield players from match data.
    
    Args:
        matches: List of match dictionaries
        per_90_mode: Whether to calculate per 90 minute statistics
        
    Returns:
        Dictionary of calculated statistics
    """
    if not matches:
        return {}
    
    # Initialize totals
    total_matches = len(matches)
    total_minutes = sum(match.get('Minutes played', 0) for match in matches)
    total_goals = sum(match.get('Goals', 0) for match in matches)
    total_assists = sum(match.get('Assists', 0) for match in matches)
    total_shots = sum(match.get('Shots', 0) for match in matches)
    total_shots_on_target = sum(match.get('Shots on target', 0) for match in matches)
    total_passes = sum(match.get('Passes', 0) for match in matches)
    total_passes_accurate = sum(match.get('Passes accurate', 0) for match in matches)
    total_dribbles = sum(match.get('Dribbles', 0) for match in matches)
    total_dribbles_successful = sum(match.get('Dribbles successful', 0) for match in matches)
    total_duels = sum(match.get('Duels', 0) for match in matches)
    total_duels_won = sum(match.get('Duels won', 0) for match in matches)
    total_interceptions = sum(match.get('Interceptions', 0) for match in matches)
    total_recoveries = sum(match.get('Recoveries', 0) for match in matches)
    
    # Count cards (yellow and red cards are given as minutes when received)
    yellow_cards = sum(1 for match in matches if match.get('Yellow card', 0) > 0)
    red_cards = sum(1 for match in matches if match.get('Red card', 0) > 0)
    
    # Get team and position from most recent match
    most_recent_match = max(matches, key=lambda x: x.get('Date', ''))
    team = most_recent_match.get('Team', 'Unknown')
    position = most_recent_match.get('Position', 'Unknown')
    
    # Calculate base statistics
    stats = {
        'matches': total_matches,
        'minutes': total_minutes,
        'team': team,
        'position': position,
        'goals': total_goals,
        'assists': total_assists,
        'shots': total_shots,
        'shots_on_target': total_shots_on_target,
        'passes': total_passes,
        'passes_accurate': total_passes_accurate,
        'dribbles': total_dribbles,
        'dribbles_successful': total_dribbles_successful,
        'duels': total_duels,
        'duels_won': total_duels_won,
        'interceptions': total_interceptions,
        'recoveries': total_recoveries,
        'yellow_cards': yellow_cards,
        'red_cards': red_cards
    }
    
    # Apply per 90 conversion if requested
    if per_90_mode and total_minutes > 0:
        per_90_stats = [
            'goals', 'assists', 'shots', 'shots_on_target', 'passes', 'passes_accurate',
            'dribbles', 'dribbles_successful', 'duels', 'duels_won', 
            'interceptions', 'recoveries'
        ]
        
        for stat in per_90_stats:
            if stat in stats:
                stats[stat] = (stats[stat] * 90) / total_minutes
    
    # Calculate derived metrics
    stats['pass_accuracy'] = (total_passes_accurate / total_passes * 100) if total_passes > 0 else 0
    stats['shot_accuracy'] = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0
    stats['dribble_success_rate'] = (total_dribbles_successful / total_dribbles * 100) if total_dribbles > 0 else 0
    stats['duel_success_rate'] = (total_duels_won / total_duels * 100) if total_duels > 0 else 0
    
    return stats


def display_outfield_comparison_charts(selected_players, player_stats, per_90_mode):
    """
    Display comparison charts for outfield players.
    """
    st.subheader("Performance Comparison Charts")
    
    # Create comparison charts similar to goalkeeper charts but with outfield stats
    # This would include goals, assists, passing, dribbling, etc.
    
    # For now, show a placeholder
    st.info("Outfield player comparison charts will be implemented here, similar to the goalkeeper charts but with relevant outfield statistics.")


def display_outfield_detailed_comparison(selected_players, player_stats, per_90_mode):
    """
    Display detailed comparison table for outfield players.
    """
    stats_mode_text = " (Per 90 Minutes)" if per_90_mode else ""
    st.subheader(f"Detailed Comparison{stats_mode_text}")
    
    # Create detailed comparison table
    st.info("Detailed outfield player comparison table will be implemented here.")


def display_outfield_role_analysis(selected_players, player_stats, position_type, per_90_mode):
    """
    Display role analysis for outfield players based on their position.
    """
    role_stats_mode_text = " (Per 90 Minutes)" if per_90_mode else ""
    st.subheader(f"{position_type} Role Analysis{role_stats_mode_text}")
    
    # Position-specific role analysis
    st.info(f"{position_type} role analysis will be implemented here with position-specific roles and weights.")
