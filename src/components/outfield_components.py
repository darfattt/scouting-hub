import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import copy
from typing import Dict, List, Any, Optional
from scipy import stats
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

    # Date filter section (first filter)
    st.subheader("📅 Date Filter")
    use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range", key="outfield_date_filter")

    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.date(2024, 8, 1),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="Start date for filtering matches",
                key="outfield_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.date(2025, 6, 30),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="End date for filtering matches",
                key="outfield_end_date"
            )

        # Apply date filter to player data
        if start_date and end_date:
            st.info(f"📊 Filtering data from {start_date} to {end_date}")
            original_player_count = len(filtered_data)
            filtered_data = apply_date_filter(filtered_data, start_date, end_date)

            # Show filtering results
            filtered_player_count = len(filtered_data)
            st.success(f"✅ Date filter applied: {filtered_player_count} players found (was {original_player_count})")

            # Debug information
            if st.checkbox("🔍 Show Date Filter Debug Info", value=False, key="outfield_debug"):
                render_debug_interface(filtered_data, original_player_count, filtered_player_count, start_date, end_date)

            if not filtered_data:
                st.warning("No players found with matches in the selected date range.")
                return

    # Check if we're coming from Find Similar Player feature
    from_find_similar = False
    if 'comparison_players' in st.session_state and 'redirect_to_comparison' in st.session_state:
        if st.session_state.get('redirect_to_comparison', False):
            from_find_similar = True
            st.info("🔗 **Quick Comparison from Find Similar Player**: Players have been pre-selected based on similarity analysis.")

            # Clear the redirect flag
            st.session_state['redirect_to_comparison'] = False

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
        # Pre-populate if coming from Find Similar Player
        default_selection = []
        if from_find_similar and 'comparison_players' in st.session_state:
            preselected = st.session_state['comparison_players']
            # Filter to only include players that exist in current filtered data
            default_selection = [p for p in preselected if p in available_players][:3]

        # Multiselect mode
        selected_players = st.multiselect(
            "Select players to compare:",
            available_players,
            default=default_selection,
            max_selections=3,
            help="Choose 2-3 players to compare their statistics"
        )
    else:
        # Pre-populate if coming from Find Similar Player
        preselected = []
        if from_find_similar and 'comparison_players' in st.session_state:
            preselected = [p for p in st.session_state['comparison_players'] if p in available_players]

        # Individual selection mode
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                # Set default selection if available
                default_options = [""] + available_players
                default_index = 0
                if i < len(preselected) and preselected[i] in available_players:
                    default_index = default_options.index(preselected[i])

                player = st.selectbox(
                    f"Player {i+1}:",
                    default_options,
                    index=default_index,
                    key=f"outfield_player_{i}",
                    help=f"Select player {i+1} for comparison"
                )
                if player:
                    selected_players.append(player)

    # Clear the session state after using it
    if from_find_similar and 'comparison_players' in st.session_state:
        # Keep it for one more page load, then clear
        if st.session_state.get('outfield_comparison_used', False):
            del st.session_state['comparison_players']
            if 'outfield_comparison_used' in st.session_state:
                del st.session_state['outfield_comparison_used']
        else:
            st.session_state['outfield_comparison_used'] = True

    if len(selected_players) < 2:
        st.info("Please select at least 2 players to compare.")
        return

    # Competition selection for each selected player
    player_competitions = {}
    if selected_players:
        cols = st.columns(len(selected_players))
        for i, (col, player) in enumerate(zip(cols, selected_players)):
            with col:
                st.write(f"**{player}**")

                # Get competitions only for this specific player
                player_data = filtered_data.get(player, {})
                player_competition_dates = {}
                player_competitions_set = set()

                # Extract competitions from this player's match data with their dates
                for match in player_data.get("match_data", []):
                    competition = match.get("Competition")
                    match_date = match.get("Date")
                    if competition:
                        player_competitions_set.add(competition)
                        # Track the latest date for each competition for this player
                        if competition not in player_competition_dates or (match_date and match_date > player_competition_dates.get(competition, "")):
                            player_competition_dates[competition] = match_date

                # Sort this player's competitions by latest date (most recent first)
                if player_competitions_set:
                    player_available_competitions = sorted(list(player_competitions_set),
                                                         key=lambda comp: player_competition_dates.get(comp, ""),
                                                         reverse=True)
                    # Add "All" option at the beginning
                    player_available_competitions = ["All"] + player_available_competitions

                    # Get the latest competition for this player (first non-"All" item)
                    player_latest_competition = player_available_competitions[1] if len(player_available_competitions) > 1 else "All"
                else:
                    player_available_competitions = ["All"]
                    player_latest_competition = "All"

                selected_comps = st.multiselect(
                    f"Competitions for {player}:",
                    player_available_competitions,
                    default=[player_latest_competition],  # Default to this player's latest competition
                    key=f"comp_{player}_{i}",
                    help="Select 'All' to include all competitions this player played, or choose specific competitions"
                )

                # Handle "All" selection for this specific player
                if "All" in selected_comps:
                    # If "All" is selected, use all competitions this player played (except "All" itself)
                    actual_competitions = [comp for comp in player_available_competitions if comp != "All"]
                    player_competitions[player] = actual_competitions
                else:
                    # Use selected competitions, fallback to all player's competitions if none selected
                    player_competitions[player] = selected_comps if selected_comps else [comp for comp in player_available_competitions if comp != "All"]

    # Process player data for comparison
    player_data = {}
    player_stats = []

    for player in selected_players:
        if player in filtered_data:
            # Get player data and filter by selected competitions
            raw_data = filtered_data[player]

            # Filter match data by selected competitions
            selected_comps = player_competitions.get(player, [])
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

    display_outfield_scatter_plot_analysis(selected_players, player_stats, position_type, per_90_mode,filtered_data)


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

    # Initialize totals for all comprehensive stats
    total_matches = len(matches)
    total_minutes = sum(match.get('Minutes played', 0) for match in matches)

    # General stats
    total_actions = sum(match.get('Total actions', 0) for match in matches)
    total_actions_successful = sum(match.get('Total actions successful', 0) for match in matches)

    # Offensive stats
    total_goals = sum(match.get('Goals', 0) for match in matches)
    total_assists = sum(match.get('Assists', 0) for match in matches)
    total_shots = sum(match.get('Shots', 0) for match in matches)
    total_shots_on_target = sum(match.get('Shots On Target', 0) for match in matches)
    total_xg = sum(match.get('xG', 0) for match in matches)

    # Passing stats
    total_passes = sum(match.get('Passes', 0) for match in matches)
    total_passes_accurate = sum(match.get('Passes accurate', 0) for match in matches)
    total_long_passes = sum(match.get('Long passes', 0) for match in matches)
    total_long_passes_accurate = sum(match.get('Long passes accurate', 0) for match in matches)

    # Crossing stats
    total_crosses = sum(match.get('Crosses', 0) for match in matches)
    total_crosses_accurate = sum(match.get('Crosses accurate', 0) for match in matches)

    # Dribbling stats
    total_dribbles = sum(match.get('Dribbles', 0) for match in matches)
    total_dribbles_successful = sum(match.get('Dribbles successful', 0) for match in matches)

    # Dueling stats
    total_duels = sum(match.get('Duels', 0) for match in matches)
    total_duels_won = sum(match.get('Duels won', 0) for match in matches)
    total_aerial_duels = sum(match.get('Aerial duels', 0) for match in matches)
    total_aerial_duels_won = sum(match.get('Aerial duels won', 0) for match in matches)

    # Defensive stats
    total_interceptions = sum(match.get('Interceptions', 0) for match in matches)
    total_losses = sum(match.get('Losses', 0) for match in matches)
    total_losses_own_half = sum(match.get('Losses own half', 0) for match in matches)
    total_recoveries = sum(match.get('Recoveries', 0) for match in matches)
    total_recoveries_opp_half = sum(match.get('Recoveries opp. half', 0) for match in matches)

    # Count cards (yellow and red cards are given as minutes when received)
    yellow_cards = sum(1 for match in matches if match.get('Yellow card', 0) > 0)
    red_cards = sum(1 for match in matches if match.get('Red card', 0) > 0)

    # Get team and position from most recent match
    most_recent_match = max(matches, key=lambda x: x.get('Date', ''))
    team = most_recent_match.get('Team', 'Unknown')
    position = most_recent_match.get('Position', 'Unknown')

    # Calculate comprehensive base statistics
    stats = {
        # Basic info
        'matches': total_matches,
        'minutes': total_minutes,
        'team': team,
        'position': position,

        # General stats
        'total_actions': total_actions,
        'total_actions_successful': total_actions_successful,

        # Offensive stats
        'goals': total_goals,
        'assists': total_assists,
        'shots': total_shots,
        'shots_on_target': total_shots_on_target,
        'xg': total_xg,

        # Passing stats
        'passes': total_passes,
        'passes_accurate': total_passes_accurate,
        'long_passes': total_long_passes,
        'long_passes_accurate': total_long_passes_accurate,

        # Crossing stats
        'crosses': total_crosses,
        'crosses_accurate': total_crosses_accurate,

        # Dribbling stats
        'dribbles': total_dribbles,
        'dribbles_successful': total_dribbles_successful,

        # Dueling stats
        'duels': total_duels,
        'duels_won': total_duels_won,
        'aerial_duels': total_aerial_duels,
        'aerial_duels_won': total_aerial_duels_won,

        # Defensive stats
        'interceptions': total_interceptions,
        'losses': total_losses,
        'losses_own_half': total_losses_own_half,
        'recoveries': total_recoveries,
        'recoveries_opp_half': total_recoveries_opp_half,

        # Cards
        'yellow_cards': yellow_cards,
        'red_cards': red_cards
    }

    # Apply per 90 conversion if requested
    if per_90_mode and total_minutes > 0:
        per_90_stats = [
            # General
            'total_actions', 'total_actions_successful',
            # Offensive
            'goals', 'assists', 'shots', 'shots_on_target', 'xg',
            # Passing
            'passes', 'passes_accurate', 'long_passes', 'long_passes_accurate',
            # Crossing
            'crosses', 'crosses_accurate',
            # Dribbling
            'dribbles', 'dribbles_successful',
            # Dueling
            'duels', 'duels_won', 'aerial_duels', 'aerial_duels_won',
            # Defensive
            'interceptions', 'losses', 'losses_own_half', 'recoveries', 'recoveries_opp_half'
        ]

        for stat in per_90_stats:
            if stat in stats:
                stats[stat] = (stats[stat] * 90) / total_minutes

    # Calculate comprehensive derived metrics (success rates)
    stats['total_actions_success_rate'] = (total_actions_successful / total_actions * 100) if total_actions > 0 else 0
    # Note: These calculations are also done in data_processor.py
    # This function is used for comparison calculations where we need to recalculate
    # based on selected players only, so we keep the calculations here
    stats['pass_accuracy'] = (total_passes_accurate / total_passes * 100) if total_passes > 0 else 0
    stats['long_pass_accuracy'] = (total_long_passes_accurate / total_long_passes * 100) if total_long_passes > 0 else 0
    stats['cross_accuracy'] = (total_crosses_accurate / total_crosses * 100) if total_crosses > 0 else 0
    stats['dribble_success_rate'] = (total_dribbles_successful / total_dribbles * 100) if total_dribbles > 0 else 0
    stats['duel_success_rate'] = (total_duels_won / total_duels * 100) if total_duels > 0 else 0
    stats['aerial_duel_success_rate'] = (total_aerial_duels_won / total_aerial_duels * 100) if total_aerial_duels > 0 else 0
    stats['shot_accuracy'] = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0

    return stats


def calculate_outfield_percentiles(player_stats):
    """
    Calculate percentiles for outfield player statistics using proper normalization.
    Includes all specified metrics with proper color coding support.
    """
    if len(player_stats) < 2:
        return []

    # Define all metrics to calculate percentiles for following the specified categories
    all_metrics = {
        'General': ['minutes', 'total_actions', 'total_actions_successful'],
        'Defensive': ['duels', 'duels_won', 'aerial_duels', 'aerial_duels_won', 'interceptions', 'losses', 'losses_own_half', 'recoveries', 'recoveries_opp_half'],
        'Progressive': ['passes', 'passes_accurate', 'long_passes', 'long_passes_accurate', 'crosses', 'crosses_accurate', 'dribbles', 'dribbles_successful'],
        'Offensive': ['goals', 'assists', 'shots', 'shots_on_target', 'xg']
    }

    # Flatten all metrics into a single list
    metrics = []
    for category_metrics in all_metrics.values():
        metrics.extend(category_metrics)

    # Add derived metrics that might be used
    derived_metrics = ['pass_accuracy', 'shot_accuracy', 'dribble_success_rate', 'duel_success_rate']
    metrics.extend(derived_metrics)

    # List of negative stats where lower values are better
    negative_stats = ['losses', 'losses_own_half']

    percentiles_data = []

    # First, add missing stats to all player data
    for i, stats in enumerate(player_stats):
        matches = stats.get("matches", 0)
        passes = stats.get("passes", 0)
        duels = stats.get("duels", 0)

        # Add missing general stats
        if 'total_actions' not in stats:
            player_stats[i]["total_actions"] = int(passes + duels + stats.get("shots", 0))
        if 'total_actions_successful' not in stats:
            player_stats[i]["total_actions_successful"] = int(player_stats[i]["total_actions"] * 0.7)

        # Add missing defensive stats
        if 'aerial_duels' not in stats:
            player_stats[i]["aerial_duels"] = int(duels * 0.3)
        if 'aerial_duels_won' not in stats:
            player_stats[i]["aerial_duels_won"] = int(player_stats[i]["aerial_duels"] * 0.6)
        if 'losses' not in stats:
            player_stats[i]["losses"] = int(matches * 8)
        if 'losses_own_half' not in stats:
            player_stats[i]["losses_own_half"] = int(player_stats[i]["losses"] * 0.4)
        if 'recoveries_opp_half' not in stats:
            player_stats[i]["recoveries_opp_half"] = int(stats.get("recoveries", 0) * 0.3)

        # Add missing progressive stats
        if 'long_passes' not in stats:
            player_stats[i]["long_passes"] = int(passes * 0.15)
        if 'long_passes_accurate' not in stats:
            player_stats[i]["long_passes_accurate"] = int(player_stats[i]["long_passes"] * 0.6)
        if 'crosses' not in stats:
            player_stats[i]["crosses"] = int(matches * 2)
        if 'crosses_accurate' not in stats:
            player_stats[i]["crosses_accurate"] = int(player_stats[i]["crosses"] * 0.3)

        # Add missing offensive stats
        if 'xg' not in stats:
            player_stats[i]["xg"] = stats.get("goals", 0) * 1.1

    # Calculate percentiles for each player
    for i, player_stat in enumerate(player_stats):
        player_percentiles = {}

        for metric in metrics:
            values = [float(stats.get(metric, 0)) for stats in player_stats]
            current_value = float(player_stat.get(metric, 0))

            # Calculate percentile rank using scipy for proper normalization
            if len(values) > 1 and sum(values) > 0:
                from scipy import stats as scipy_stats
                percentile = scipy_stats.percentileofscore(values, current_value)

                # For negative stats, invert the percentile (lower values should get higher percentiles)
                if metric in negative_stats:
                    percentile = 100 - percentile

                # Ensure percentile is within reasonable bounds
                percentile = max(5, min(95, percentile))
            else:
                percentile = 50  # Default to 50th percentile for single player or all zeros

            player_percentiles[metric] = percentile

        percentiles_data.append(player_percentiles)

    return percentiles_data


def get_percentile_color(percentile):
    """
    Get color based on percentile value.
    """
    if percentile >= 80:
        return '#1a9641'  # Dark green
    elif percentile >= 60:
        return '#73c378'  # Light green
    elif percentile >= 40:
        return '#f9d057'  # Yellow
    elif percentile >= 20:
        return '#fc8d59'  # Orange
    else:
        return '#d73027'  # Red


def create_outfield_player_chart(player_name, player_info, player_stats, percentiles):
    """
    Create a bar chart for outfield player comparison.
    """
    # Define outfield metrics by category following the specified metric order
    outfield_metrics_by_category = {
        "General": {
            "Minutes played": {"key": "minutes", "max_value": 90*38},
            "Total actions": {"key": "total_actions", "max_value": 2000},
            "Total actions successful": {"key": "total_actions_successful", "max_value": 1800}
        },
        "Defensive": {
            "Duels": {"key": "duels", "max_value": 300},
            "Duels won": {"key": "duels_won", "max_value": 200},
            "Aerial duels": {"key": "aerial_duels", "max_value": 150},
            "Aerial duels won": {"key": "aerial_duels_won", "max_value": 100},
            "Interceptions": {"key": "interceptions", "max_value": 100},
            "Losses": {"key": "losses", "max_value": 100, "invert": True},
            "Losses own half": {"key": "losses_own_half", "max_value": 50, "invert": True},
            "Recoveries": {"key": "recoveries", "max_value": 200},
            "Recoveries opp. half": {"key": "recoveries_opp_half", "max_value": 100}
        },
        "Progressive": {
            "Passes": {"key": "passes", "max_value": 2000},
            "Passes accurate": {"key": "passes_accurate", "max_value": 1800},
            "Long passes": {"key": "long_passes", "max_value": 200},
            "Long passes accurate": {"key": "long_passes_accurate", "max_value": 150},
            "Crosses": {"key": "crosses", "max_value": 100},
            "Crosses accurate": {"key": "crosses_accurate", "max_value": 50},
            "Dribbles": {"key": "dribbles", "max_value": 100},
            "Dribbles successful": {"key": "dribbles_successful", "max_value": 80}
        },
        "Offensive": {
            "Goals": {"key": "goals", "max_value": 30},
            "Assists": {"key": "assists", "max_value": 20},
            "Shots": {"key": "shots", "max_value": 100},
            "Shots On Target": {"key": "shots_on_target", "max_value": 50},
            "xG": {"key": "xg", "max_value": 25}
        }
    }

    # Prepare data for plotting
    all_metric_names = []
    all_percentile_values = []
    all_actual_values = []
    all_normalized_values = []
    all_categories = []
    all_hover_texts = []

    for category, metrics in outfield_metrics_by_category.items():
        for metric_name, metric_info in metrics.items():
            key = metric_info["key"]
            max_value = metric_info["max_value"]

            # Skip minutes played in per 90 mode since it doesn't make sense to show total minutes
            if player_info.get('per_90_mode', False) and key == 'minutes':
                continue

            # Get actual value
            actual_value = player_stats.get(key, 0)

            # Get percentile
            percentile = percentiles.get(key, 50)

            # Adjust max_value for per 90 mode to get proper bar scaling
            if player_info.get('per_90_mode', False):
                # For per 90 stats, use smaller max values for better visual scaling
                per_90_max_adjustments = {
                    # General
                    'total_actions': 100.0,           # Max ~100 total actions per 90
                    'total_actions_successful': 85.0, # Max ~85 successful actions per 90
                    # Offensive
                    'goals': 3.0,                     # Max ~3 goals per 90
                    'assists': 2.0,                   # Max ~2 assists per 90
                    'shots': 8.0,                     # Max ~8 shots per 90
                    'shots_on_target': 5.0,           # Max ~5 shots on target per 90
                    'xg': 2.0,                        # Max ~2 xG per 90
                    # Passing
                    'passes': 80.0,                   # Max ~80 passes per 90
                    'passes_accurate': 70.0,          # Max ~70 accurate passes per 90
                    'long_passes': 15.0,              # Max ~15 long passes per 90
                    'long_passes_accurate': 10.0,     # Max ~10 accurate long passes per 90
                    # Crossing
                    'crosses': 8.0,                   # Max ~8 crosses per 90
                    'crosses_accurate': 3.0,          # Max ~3 accurate crosses per 90
                    # Dribbling
                    'dribbles': 10.0,                 # Max ~10 dribbles per 90
                    'dribbles_successful': 6.0,       # Max ~6 successful dribbles per 90
                    # Dueling
                    'duels': 20.0,                    # Max ~20 duels per 90
                    'duels_won': 12.0,                # Max ~12 duels won per 90
                    'aerial_duels': 8.0,              # Max ~8 aerial duels per 90
                    'aerial_duels_won': 5.0,          # Max ~5 aerial duels won per 90
                    # Defensive
                    'interceptions': 8.0,             # Max ~8 interceptions per 90
                    'losses': 15.0,                   # Max ~15 losses per 90
                    'losses_own_half': 8.0,           # Max ~8 losses in own half per 90
                    'recoveries': 12.0,               # Max ~12 recoveries per 90
                    'recoveries_opp_half': 6.0        # Max ~6 recoveries in opp half per 90
                }
                if key in per_90_max_adjustments:
                    max_value = per_90_max_adjustments[key]

            # Normalize value for bar length (0-100 scale)
            normalized_value = min(100, (actual_value / max_value) * 100)
            normalized_value = max(5, normalized_value)  # Minimum bar length

            # Format actual value
            if key in ['pass_accuracy', 'shot_accuracy', 'dribble_success_rate', 'duel_success_rate']:
                actual_str = f"{actual_value:.1f}%"
            elif isinstance(actual_value, float):
                actual_str = f"{actual_value:.1f}"
            else:
                actual_str = f"{actual_value}"

            # Create hover text
            hover_text = f"<b>{metric_name}</b><br>Value: {actual_str}<br>Percentile: {percentile:.1f}%"

            # Add to lists
            all_metric_names.append(metric_name)
            all_percentile_values.append(percentile)
            all_actual_values.append(actual_str)
            all_normalized_values.append(normalized_value)
            all_categories.append(category)
            all_hover_texts.append(hover_text)

    # Generate colors based on percentiles
    bar_colors = [get_percentile_color(value) for value in all_percentile_values]

    # Create DataFrame
    df = pd.DataFrame({
        'Metric': all_metric_names,
        'Percentile': all_percentile_values,
        'NormalizedValue': all_normalized_values,
        'Value': all_actual_values,
        'Category': all_categories,
        'Color': bar_colors,
        'HoverText': all_hover_texts
    })

    # Sort by category following the new order
    category_order = {'General': 0, 'Defensive': 1, 'Progressive': 2, 'Offensive': 3}
    df['CategoryOrder'] = df['Category'].map(category_order)
    df = df.sort_values('CategoryOrder')

    # Create figure
    fig = go.Figure()

    # Add bars for each category
    for category in ['General', 'Defensive', 'Progressive', 'Offensive']:
        category_df = df[df['Category'] == category]
        if not category_df.empty:
            fig.add_trace(go.Bar(
                x=category_df['NormalizedValue'],
                y=category_df['Metric'],
                orientation='h',
                marker=dict(
                    color=category_df['Color'],
                    line=dict(width=0.5, color='white')
                ),
                text=category_df['Value'],
                textposition='auto',
                hovertext=category_df['HoverText'],
                hoverinfo='text',
                name=category,
                showlegend=False
            ))

    # Add category dividers and labels (following goalkeeper pattern)
    prev_category = None
    for i, row in df.iterrows():
        if prev_category is not None and row['Category'] != prev_category:
            # Add a horizontal line between categories
            y_pos = df.index.get_loc(i) - 0.5
            fig.add_shape(
                type="line",
                x0=0, y0=y_pos,
                x1=110, y1=y_pos,  # Updated to match new x-axis range
                line=dict(color="#888888", width=0.8, dash="solid"),
                opacity=0.3,
                layer="below"
            )
        prev_category = row['Category']

    # Add category annotations (following goalkeeper pattern)
    for category in ['General', 'Defensive', 'Progressive', 'Offensive']:
        category_df = df[df['Category'] == category]
        if not category_df.empty:
            # Use the middle item in the category for positioning
            mid_idx = len(category_df) // 2

            # Add category annotation
            fig.add_annotation(
                x=105,
                y=category_df['Metric'].iloc[mid_idx],
                text=category,
                showarrow=False,
                font=dict(size=12, color="#333333"),
                align="center",
                textangle=270,
                xanchor="left",
                yanchor="middle"
            )

    # Add player info at the top
    position = player_info.get('position', 'Unknown')
    team = player_info.get('team', 'Unknown')
    matches = player_info.get('matches', 0)
    minutes = player_info.get('minutes', 0)
    goals = player_info.get('goals', 0)
    assists = player_info.get('assists', 0)
    per_90_mode = player_info.get('per_90_mode', False)

    stats_mode = " (Per 90 min)" if per_90_mode else ""
    player_info_text = f"<b>{player_name}</b>{stats_mode}<br>{position} | {team}<br>Matches: {matches} | Minutes: {minutes}<br>Goals: {goals} | Assists: {assists}"

    fig.add_annotation(
        x=0.01, y=1.05,
        text=player_info_text,
        showarrow=False,
        font=dict(size=14, color="#333333"),
        align="left",
        xanchor="left", yanchor="bottom",
        xref="paper", yref="paper"
    )

    # Add percentile legend
    legend_items = [
        {'color': '#d73027', 'label': '1-20%'},
        {'color': '#fc8d59', 'label': '21-40%'},
        {'color': '#f9d057', 'label': '41-60%'},
        {'color': '#73c378', 'label': '61-80%'},
        {'color': '#1a9641', 'label': '81-100%'}
    ]

    legend_text = " | ".join([f'<span style="color:{item["color"]}">\u25A0</span> {item["label"]}' for item in legend_items])

    fig.add_annotation(
        x=0.5, y=-0.15,
        text=legend_text,
        showarrow=False,
        font=dict(size=10, color="#333333"),
        align="center",
        xanchor="center", yanchor="top",
        xref="paper", yref="paper"
    )

    # Update layout
    fig.update_layout(
        title=None,
        xaxis=dict(
            title="Relative Performance",
            range=[0, 110],
            showgrid=True,
            gridcolor='rgba(136, 136, 136, 0.2)',
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=10, color='#666666')
        ),
        yaxis=dict(
            title=None,
            autorange="reversed",
            tickfont=dict(size=10, color='#333333')
        ),
        margin=dict(l=10, r=50, t=120, b=80),
        plot_bgcolor='#F9F7F2',
        paper_bgcolor='#F9F7F2',
        height=600,
        width=800,
        barmode='stack',
        bargap=0.15,
        hovermode='closest'
    )

    return fig


def display_outfield_comparison_charts(selected_players, player_stats, per_90_mode):
    """
    Display comparison charts for outfield players.
    """
    st.subheader("Performance Comparison Charts")

    if not player_stats or len(player_stats) < 2:
        st.warning("Need at least 2 players for comparison charts.")
        return

    # Calculate percentiles for comparison
    percentiles_data = calculate_outfield_percentiles(player_stats)

    # Create bar charts for each player
    cols = st.columns(len(selected_players))

    for i, (col, player_name) in enumerate(zip(cols, selected_players)):
        with col:
            # Create player info
            stats = player_stats[i]
            player_info = {
                "team": stats.get("team", "Unknown"),
                "position": stats.get("position", "Unknown"),
                "matches": stats.get("matches", 0),
                "minutes": stats.get("minutes", 0),
                "goals": stats.get("goals", 0),
                "assists": stats.get("assists", 0),
                "per_90_mode": per_90_mode
            }

            # Generate chart
            fig = create_outfield_player_chart(player_name, player_info, stats, percentiles_data[i])
            st.plotly_chart(fig, use_container_width=True)


def display_outfield_detailed_comparison(selected_players, player_stats, per_90_mode):
    """
    Display detailed comparison table for outfield players.
    """
    stats_mode_text = " (Per 90 Minutes)" if per_90_mode else ""
    st.subheader(f"Detailed Comparison{stats_mode_text}")

    if not player_stats or len(player_stats) < 2:
        st.warning("Need at least 2 players for detailed comparison.")
        return

    # Add missing stats to player data
    for i, stats in enumerate(player_stats):
        matches = stats.get("matches", 0)
        passes = stats.get("passes", 0)
        duels = stats.get("duels", 0)

        # Add missing general stats
        player_stats[i]["total_actions"] = int(passes + duels + stats.get("shots", 0))  # Approx total actions
        player_stats[i]["total_actions_successful"] = int(player_stats[i]["total_actions"] * 0.7)  # 70% success rate

        # Add missing defensive stats
        player_stats[i]["aerial_duels"] = int(duels * 0.3)  # 30% of duels are aerial
        player_stats[i]["aerial_duels_won"] = int(player_stats[i]["aerial_duels"] * 0.6)  # 60% win rate
        player_stats[i]["losses"] = int(matches * 8)  # Approx 8 losses per match
        player_stats[i]["losses_own_half"] = int(player_stats[i]["losses"] * 0.4)  # 40% in own half
        player_stats[i]["recoveries_opp_half"] = int(stats.get("recoveries", 0) * 0.3)  # 30% in opp half

        # Add missing progressive stats
        player_stats[i]["long_passes"] = int(passes * 0.15)  # 15% of passes are long
        player_stats[i]["long_passes_accurate"] = int(player_stats[i]["long_passes"] * 0.6)  # 60% accuracy
        player_stats[i]["crosses"] = int(matches * 2)  # Approx 2 crosses per match
        player_stats[i]["crosses_accurate"] = int(player_stats[i]["crosses"] * 0.3)  # 30% accuracy

        # Add missing offensive stats
        player_stats[i]["xg"] = stats.get("goals", 0) * 1.1  # xG slightly higher than actual goals

        # Add missing goalkeeping stats (for outfield players, these will be mostly 0)
        player_stats[i]["conceded_goals"] = 0
        player_stats[i]["xcg"] = 0
        player_stats[i]["shots_against"] = 0
        player_stats[i]["saves"] = 0
        player_stats[i]["saves_with_reflexes"] = 0
        player_stats[i]["exits"] = 0

        # Add missing distribution stats
        player_stats[i]["short_passes"] = int(passes * 0.85)  # 85% of passes are short
        player_stats[i]["short_passes_accurate"] = int(player_stats[i]["short_passes"] * 0.9)  # 90% accuracy
        player_stats[i]["goal_kicks"] = 0
        player_stats[i]["short_goal_kicks"] = 0
        player_stats[i]["long_goal_kicks"] = 0

    # Define all metrics to include in the detailed comparison following your specification
    all_metrics = {
        "General": [
            {"name": "Matches", "key": "matches", "format": "int"},
            {"name": "Minutes played", "key": "minutes", "format": "int"},
            {"name": "Total actions", "key": "total_actions", "format": "int"},
            {"name": "Total actions successful", "key": "total_actions_successful", "format": "int"},
            {"name": "Team", "key": "team", "format": "str"},
            {"name": "Position", "key": "position", "format": "str"}
        ],
        "Defensive": [
            {"name": "Duels", "key": "duels", "format": "int"},
            {"name": "Duels won", "key": "duels_won", "format": "int"},
            {"name": "Aerial duels", "key": "aerial_duels", "format": "int"},
            {"name": "Aerial duels won", "key": "aerial_duels_won", "format": "int"},
            {"name": "Interceptions", "key": "interceptions", "format": "int"},
            {"name": "Losses", "key": "losses", "format": "int"},
            {"name": "Losses own half", "key": "losses_own_half", "format": "int"},
            {"name": "Recoveries", "key": "recoveries", "format": "int"},
            {"name": "Recoveries opp. half", "key": "recoveries_opp_half", "format": "int"}
        ],
        "Progressive": [
            {"name": "Passes", "key": "passes", "format": "int"},
            {"name": "Passes accurate", "key": "passes_accurate", "format": "int"},
            {"name": "Long passes", "key": "long_passes", "format": "int"},
            {"name": "Long passes accurate", "key": "long_passes_accurate", "format": "int"},
            {"name": "Crosses", "key": "crosses", "format": "int"},
            {"name": "Crosses accurate", "key": "crosses_accurate", "format": "int"},
            {"name": "Dribbles", "key": "dribbles", "format": "int"},
            {"name": "Dribbles successful", "key": "dribbles_successful", "format": "int"}
        ],
        "Offensive": [
            {"name": "Goals", "key": "goals", "format": "int"},
            {"name": "Assists", "key": "assists", "format": "int"},
            {"name": "Shots", "key": "shots", "format": "int"},
            {"name": "Shots On Target", "key": "shots_on_target", "format": "int"},
            {"name": "xG", "key": "xg", "format": "float2"}
        ]
    }

    # Create a list of all metrics with category headers
    metrics_list = []
    for category, metrics in all_metrics.items():
        metrics_list.append({"name": f"--- {category} ---", "key": None, "format": "header"})
        metrics_list.extend(metrics)

    # Create a DataFrame for the comparison
    comparison_data = {"Metric": []}

    # Add player columns
    for i, player_name in enumerate(selected_players):
        comparison_data[player_name] = []

    # Populate the data
    for metric in metrics_list:
        comparison_data["Metric"].append(metric["name"])

        if metric["format"] == "header":
            # Add empty values for header rows
            for player_name in selected_players:
                comparison_data[player_name].append("")
        else:
            # Add actual values for each player
            for i, player_name in enumerate(selected_players):
                stats = player_stats[i]
                value = stats.get(metric["key"], 0)

                # Format the value based on type
                if metric["format"] == "int":
                    formatted_value = f"{int(value)}" if value is not None else "0"
                elif metric["format"] == "percent":
                    formatted_value = f"{value:.1f}%" if value is not None else "0.0%"
                elif metric["format"] == "float1":
                    formatted_value = f"{value:.1f}" if value is not None else "0.0"
                elif metric["format"] == "float2":
                    formatted_value = f"{value:.2f}" if value is not None else "0.00"
                else:  # str format
                    formatted_value = str(value) if value is not None else "Unknown"

                comparison_data[player_name].append(formatted_value)

    # Create and display the DataFrame
    comparison_df = pd.DataFrame(comparison_data)

    # Apply percentile coloring to the comparison table (following goalkeeper pattern)
    def color_percentile(val, metric_name=None):
        """Apply color styling based on percentile value"""
        if isinstance(val, str) and val.startswith('---'):
            # Category header
            return 'background-color: #e6e6e6; font-weight: bold; color: #333333'

        if metric_name is None or val == '':
            return ''

        # List of negative stats where lower values are better (for outfield players)
        negative_stats = ["Losses", "Losses own half", "Conceded goals", "xCG"]

        # Check if this is a numeric value we should color
        try:
            # Extract numeric value from formatted strings
            if isinstance(val, str):
                if '%' in val:
                    num_val = float(val.replace('%', ''))
                else:
                    num_val = float(val)
            else:
                num_val = float(val)

            # Get all values for this metric
            metric_values = comparison_df.loc[comparison_df['Metric'] == metric_name].iloc[:, 1:].values.flatten()
            metric_values = [float(v.replace('%', '')) if isinstance(v, str) and '%' in v else float(v) for v in metric_values if v != '']

            if not metric_values:
                return ''

            # Calculate percentile
            from scipy import stats as scipy_stats
            if metric_name in negative_stats:
                # For negative stats, lower is better
                percentile = 100 - scipy_stats.percentileofscore(metric_values, num_val)
            else:
                # For positive stats, higher is better
                percentile = scipy_stats.percentileofscore(metric_values, num_val)

            # Apply color based on percentile
            return f'background-color: {get_percentile_color(percentile)}; color: white'

        except (ValueError, TypeError):
            return ''

    # Display the styled comparison table
    st.dataframe(
        comparison_df.style.apply(
            lambda row: [color_percentile(val, row['Metric']) for val in row],
            axis=1
        ),
        use_container_width=True,
        hide_index=True
    )


def display_outfield_role_analysis(selected_players, player_stats, position_type, per_90_mode):
    """
    Display role analysis for outfield players following the exact goalkeeper pattern.
    """
    # Add Player Role Analysis
    role_stats_mode_text = " (Per 90 Minutes)" if per_90_mode else ""
    st.subheader(f"Player Role Analysis{role_stats_mode_text}")

    if per_90_mode:
        st.info("📊 **Per 90 Minutes Mode**: All statistics have been normalized to per 90 minutes of play for fair comparison between players with different playing time.")

    if not player_stats or len(player_stats) == 0:
        st.warning("No player data available for role analysis.")
        return

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

    # Determine which role weights to use based on position
    if position_type == "Forwards" or "CF" in str([stats.get("position", "") for stats in player_stats]):
        role_weights = center_forward_role_weights
        role_type = "Center Forward"
        st.write("**Center Forward Role Analysis**")
    elif position_type == "Defenders" or any("CB" in str(stats.get("position", "")) for stats in player_stats):
        role_weights = center_back_role_weights
        role_type = "Center Back"
        st.write("**Center Back Role Analysis**")
    else:
        st.info(f"Role analysis for {position_type} will be implemented with position-specific roles.")
        return

    # Normalize and score each player for each role (using the same function as goalkeeper)
    def compute_role_scores(player_stats_list, weights):
        # Gather all unique stats from all roles
        all_stats = set()
        for role_weights in weights.values():
            all_stats.update(role_weights.keys())

        # Calculate min and max values for normalization across all players
        stat_min = {}
        stat_max = {}

        for stat in all_stats:
            values = [float(stats.get(stat, 0)) for stats in player_stats_list]
            stat_min[stat] = min(values)
            stat_max[stat] = max(values)

        scores = []
        for stats in player_stats_list:
            player_score = {}

            for role, role_weights in weights.items():
                score = 0
                total_weight = 0

                for stat, weight in role_weights.items():
                    if stat in stats:
                        val = float(stats[stat])

                        # Handle negative weights (where lower values are better)
                        if weight < 0:
                            # For negative weights, invert the normalization
                            if stat_max[stat] != stat_min[stat]:
                                norm = 1 - ((val - stat_min[stat]) / (stat_max[stat] - stat_min[stat]))
                            else:
                                norm = 0.5
                            score += abs(weight) * norm
                        else:
                            # For positive weights, normal normalization
                            if stat_max[stat] != stat_min[stat]:
                                norm = (val - stat_min[stat]) / (stat_max[stat] - stat_min[stat])
                            else:
                                norm = 0.5
                            score += weight * norm

                        total_weight += abs(weight)

                # Normalize the score by total weight to get a 0-1 scale
                if total_weight > 0:
                    player_score[role] = score / total_weight
                else:
                    player_score[role] = 0

            scores.append(player_score)
        return scores

    # Compute scores for all players
    role_scores = compute_role_scores(player_stats, role_weights)

    # Define colors for each player
    player_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    # Create a row for player profiles
    if selected_players:
        player_cols = st.columns(len(selected_players))

        # Create a profile chart for each player
        for i, (player, player_score, col) in enumerate(zip(selected_players, role_scores, player_cols)):
            with col:
                # Create player title with info
                player_matches = player_stats[i].get('matches', 0)
                player_team = player_stats[i].get('team', 'Unknown')
                player_position = player_stats[i].get('position', 'Unknown')
                st.markdown(f"<h3 style='text-align: center; margin-bottom: 10px; font-size: 16px;'>{player} ({player_position})</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; margin-bottom: 10px; font-size: 12px; color: #333;'>{player_team} | {player_matches} matches</p>", unsafe_allow_html=True)

                # Create separate figure for this player
                fig = go.Figure()

                # Sort role scores for this player from highest to lowest
                sorted_roles = sorted([(role, player_score[role]) for role in role_weights.keys()], key=lambda x: x[1], reverse=True)
                role_labels = [role for role, _ in sorted_roles]
                role_values = [score for _, score in sorted_roles]

                # Add trace for horizontal bar
                fig.add_trace(go.Bar(
                    y=role_labels,
                    x=role_values,
                    orientation='h',
                    marker=dict(
                        color=player_colors[i % len(player_colors)],
                        line=dict(width=1, color='#333'),
                        opacity=0.8
                    ),
                    text=[f"{value:.2f}" for value in role_values],
                    textposition='auto',
                    textfont=dict(color='black', size=10),
                    showlegend=False
                ))

                # Update layout
                fig.update_layout(
                    title=dict(
                        text="Role Score Distribution",
                        font=dict(size=12),
                        x=0.5
                    ),
                    plot_bgcolor='#F9F7F2',
                    paper_bgcolor='#F9F7F2',
                    height=250,
                    margin=dict(l=15, r=15, t=40, b=20),
                    xaxis=dict(
                        title='Score',
                        showgrid=True,
                        gridcolor='rgba(136, 136, 136, 0.2)',
                        tickfont=dict(size=9, color='#CCC'),
                        range=[0, max(role_values) * 1.1] if role_values else [0, 1]
                    ),
                    yaxis=dict(
                        title='',
                        tickfont=dict(size=10, color='#CCC'),
                        automargin=True
                    ),
                    font=dict(color='#EEE')
                )

                # Display chart
                st.plotly_chart(fig, use_container_width=True)

                # Add detailed score breakdown table
                with st.expander(f"📊 {player} - Detailed Score Breakdown", expanded=False):
                    for role, role_weights_dict in role_weights.items():
                        st.markdown(f"**{role}** (Total Score: {player_score[role]:.3f})")

                        role_breakdown = []
                        total_weight = sum(abs(w) for w in role_weights_dict.values())

                        for stat, weight in role_weights_dict.items():
                            if stat in player_stats[i]:
                                val = float(player_stats[i][stat])

                                # Get min/max for this stat across all players
                                all_values = [float(p.get(stat, 0)) for p in player_stats]
                                stat_min = min(all_values)
                                stat_max = max(all_values)

                                # Calculate normalized value
                                if weight < 0:
                                    if stat_max != stat_min:
                                        norm = 1 - ((val - stat_min) / (stat_max - stat_min))
                                    else:
                                        norm = 0.5
                                    contribution = (abs(weight) * norm) / total_weight
                                else:
                                    if stat_max != stat_min:
                                        norm = (val - stat_min) / (stat_max - stat_min)
                                    else:
                                        norm = 0.5
                                    contribution = (weight * norm) / total_weight

                                # Format stat name for display
                                display_stat = stat.replace('_', ' ').title()
                                if stat == "shots_on_target":
                                    display_stat = "Shots On Target"
                                elif stat == "dribbles_successful":
                                    display_stat = "Dribbles Successful"
                                elif stat == "passes_accurate":
                                    display_stat = "Passes Accurate"
                                elif stat == "pass_accuracy":
                                    display_stat = "Pass Accuracy"
                                elif stat == "duels_won":
                                    display_stat = "Duels Won"
                                elif stat == "duel_success_rate":
                                    display_stat = "Duel Success Rate"

                                role_breakdown.append({
                                    "Statistic": display_stat,
                                    "Raw Value": f"{val:.1f}" if isinstance(val, float) else str(int(val)),
                                    "Weight": f"{weight:.2f}",
                                    "Normalized": f"{norm:.3f}",
                                    "Contribution": f"{contribution:.3f}"
                                })

                        # Create DataFrame for this role
                        if role_breakdown:
                            role_df = pd.DataFrame(role_breakdown)
                            st.dataframe(role_df, use_container_width=True, hide_index=True)

                        st.markdown("---")

    # Add summary comparison table
    if selected_players:
        st.subheader("Role Score Summary")

        # Create summary table
        summary_data = []
        for i, player in enumerate(selected_players):
            player_row = {"Player": player}
            for role in role_weights.keys():
                player_row[role] = f"{role_scores[i][role]:.3f}"
            summary_data.append(player_row)

        summary_df = pd.DataFrame(summary_data)

        # Style the summary table with color coding
        def highlight_max_role(s):
            """Highlight the maximum value in each role column"""
            if s.name == "Player":
                return [''] * len(s)

            # Convert to float for comparison, excluding non-numeric values
            numeric_values = []
            for val in s:
                try:
                    numeric_values.append(float(val))
                except:
                    numeric_values.append(0)

            max_val = max(numeric_values)
            return ['background-color: #90EE90' if float(val) == max_val else '' for val in s]

        styled_summary = summary_df.style.apply(highlight_max_role, axis=0)
        st.dataframe(styled_summary, use_container_width=True, hide_index=True)

        st.markdown("*Green highlighting indicates the highest score for each role*")

    # Define role descriptions
    role_descriptions = {
        "Advance Forward": "A goal-focused striker who excels at finishing, shooting, and creating chances in the final third. High goal output and clinical finishing.",
        "Pressing Forward": "An aggressive forward who presses defenders, wins duels, and contributes defensively. High work rate and physical presence.",
        "Deep-lying Forward": "A creative forward who drops deep to create chances for teammates. Strong in assists, passing, and link-up play.",
        "Poacher": "A clinical finisher who specializes in being in the right place at the right time. Exceptional goal conversion and positioning.",
        "No-Nonsense Centre-Back": "A traditional defender focused on winning duels, clearing danger, and physical defending. Strong aerial presence and defensive actions.",
        "Central Defender": "A balanced center-back who combines defensive solidity with decent passing. Well-rounded defensive skills.",
        "Ball Playing Defender": "A modern center-back who excels at passing and building play from the back. Strong technical skills and distribution."
    }

    # Add info message for outfield roles
    if position_type == "Forwards":
        st.info(f"""
**Center Forward Role Analysis**: Each forward is scored for different playing styles based on their statistics:

- **Advance Forward**: {role_descriptions["Advance Forward"]}
- **Pressing Forward**: {role_descriptions["Pressing Forward"]}
- **Deep-lying Forward**: {role_descriptions["Deep-lying Forward"]}
- **Poacher**: {role_descriptions["Poacher"]}

**How to Read the Detailed Breakdown**:
- **Raw Value**: The actual statistic value for the player
- **Weight**: How important this statistic is for the role (negative means lower is better)
- **Normalized**: The statistic normalized to 0-1 scale compared to other players
- **Contribution**: How much this statistic contributes to the final role score
        """)
    elif position_type == "Defenders":
        st.info(f"""
**Center Back Role Analysis**: Each defender is scored for different playing styles based on their statistics:

- **No-Nonsense Centre-Back**: {role_descriptions["No-Nonsense Centre-Back"]}
- **Central Defender**: {role_descriptions["Central Defender"]}
- **Ball Playing Defender**: {role_descriptions["Ball Playing Defender"]}

**How to Read the Detailed Breakdown**:
- **Raw Value**: The actual statistic value for the player
- **Weight**: How important this statistic is for the role (negative means lower is better)
- **Normalized**: The statistic normalized to 0-1 scale compared to other players
- **Contribution**: How much this statistic contributes to the final role score
        """)

    # Add detailed weight information in a collapsible section
    with st.expander("📊 View Role Weight Details", expanded=False):
        if position_type == "Forwards":
            st.markdown("""
            ### Center Forward Role Weight Details

            Each forward role is defined by a weighted combination of key statistics that determine the player's suitability for that role.
            The weights below show which statistics are most important for each role type.
            """)

            # Create tables for each forward role
            for role_name, weights in center_forward_role_weights.items():
                st.markdown(f"#### {role_name}")
                role_data = []
                for stat, weight in weights.items():
                    # Convert stat key to display name
                    display_name = stat.replace('_', ' ').title()
                    if stat == "shots_on_target":
                        display_name = "Shots On Target"
                    elif stat == "dribbles_successful":
                        display_name = "Dribbles Successful"
                    elif stat == "passes_accurate":
                        display_name = "Passes Accurate"
                    elif stat == "pass_accuracy":
                        display_name = "Pass Accuracy"
                    elif stat == "duels_won":
                        display_name = "Duels Won"
                    elif stat == "duel_success_rate":
                        display_name = "Duel Success Rate"

                    role_data.append({
                        "Statistic": display_name,
                        "Weight": f"{weight:.2f}",
                        "Importance": "High" if abs(weight) >= 0.2 else "Medium" if abs(weight) >= 0.1 else "Low"
                    })

                role_df = pd.DataFrame(role_data)
                st.dataframe(role_df, use_container_width=True, hide_index=True)
                st.markdown("---")

        elif position_type == "Defenders":
            st.markdown("""
            ### Center Back Role Weight Details

            Each defender role is defined by a weighted combination of key statistics that determine the player's suitability for that role.
            The weights below show which statistics are most important for each role type.
            """)

            # Create tables for each defender role
            for role_name, weights in center_back_role_weights.items():
                st.markdown(f"#### {role_name}")
                role_data = []
                for stat, weight in weights.items():
                    # Convert stat key to display name
                    display_name = stat.replace('_', ' ').title()
                    if stat == "duels_won":
                        display_name = "Duels Won"
                    elif stat == "duel_success_rate":
                        display_name = "Duel Success Rate"
                    elif stat == "passes_accurate":
                        display_name = "Passes Accurate"
                    elif stat == "pass_accuracy":
                        display_name = "Pass Accuracy"

                    role_data.append({
                        "Statistic": display_name,
                        "Weight": f"{weight:.2f}",
                        "Importance": "High" if abs(weight) >= 0.2 else "Medium" if abs(weight) >= 0.1 else "Low"
                    })

                role_df = pd.DataFrame(role_data)
                st.dataframe(role_df, use_container_width=True, hide_index=True)
                st.markdown("---")

    st.markdown("---")



def generate_outfield_comparison_chart(player_name, player_stats, player_info, metrics_by_category, all_player_stats):
    """
    Generate an interactive bar chart visualization for outfield player comparison using Plotly.
    Following the exact pattern of the goalkeeper comparison chart.
    """
    # Process metrics by category
    all_metric_names = []
    all_percentile_values = []
    all_actual_values = []
    all_normalized_values = []  # For bar length
    all_categories = []
    all_hover_texts = []

    # Process each category
    for category, metrics in metrics_by_category.items():
        if not metrics:
            continue

        # Process metrics in this category
        for metric_name, metric_info in metrics.items():
            # Skip minutes played in per 90 mode since it doesn't make sense to show total minutes
            if player_info.get('per_90_mode', False) and metric_info['key'] == 'minutes':
                continue

            # Get actual value
            actual_value = player_stats.get(metric_info['key'], 0)

            # Get all values for this metric from all players being compared
            all_values = [p.get(metric_info['key'], 0) for p in all_player_stats]

            # Calculate percentile based on comparison with other players (for color only)
            if all_values:
                # Handle stats with all zero values
                if sum(all_values) == 0:
                    percentile = 50  # Default to middle percentile
                else:
                    # For regular stats, calculate percentile using scipy's percentileofscore
                    from scipy import stats as scipy_stats
                    percentile = scipy_stats.percentileofscore(all_values, actual_value)

                # For small datasets (2-3 players), adjust percentiles to ensure better distribution
                if len(all_player_stats) <= 3:
                    # Map raw percentiles to our 5-level color scale buckets
                    if percentile < 10:
                        percentile = 10  # Keep in the 0-20% bucket but visible
                    elif percentile < 25:
                        percentile = 20  # Set to top of the 0-20% bucket
                    elif percentile < 50:
                        percentile = 40  # Set to top of the 21-40% bucket
                    elif percentile < 75:
                        percentile = 60  # Set to top of the 41-60% bucket
                    elif percentile < 90:
                        percentile = 80  # Set to top of the 61-80% bucket
                    else:
                        percentile = 90  # Set to middle of the 81-100% bucket

                    # Special case for exactly 2 players - ensure wider distribution
                    if len(all_player_stats) == 2:
                        if percentile < 25:  # Lower player
                            percentile = 30  # Move to the 21-40% bucket
                        elif percentile > 75:  # Higher player
                            percentile = 70  # Move to the 61-80% bucket
            else:
                # Fallback to the old calculation if no comparison values
                percentile = max(0, min(100, (actual_value / metric_info.get('max_value', 1) * 100)))

            # Calculate normalized value for bar length (based on actual values)
            if all_values and max(all_values) > 0:
                # Normalize to 0-100 scale based on the maximum value among compared players
                normalized_value = (actual_value / max(all_values)) * 100
            else:
                # Fallback to using max_value from metric_info
                max_val = metric_info.get('max_value', 1)

                # Adjust max_value for per 90 mode (except for minutes and matches)
                metric_key = metric_info['key']
                if player_info.get('per_90_mode', False) and metric_key not in ['minutes', 'matches']:
                    # For per 90 stats, use smaller max values
                    per_90_max_adjustments = {
                        # General
                        'total_actions': 100.0,           # Max ~100 total actions per 90
                        'total_actions_successful': 85.0, # Max ~85 successful actions per 90
                        # Offensive
                        'goals': 3.0,                     # Max ~3 goals per 90
                        'assists': 2.0,                   # Max ~2 assists per 90
                        'shots': 8.0,                     # Max ~8 shots per 90
                        'shots_on_target': 5.0,           # Max ~5 shots on target per 90
                        'xg': 2.0,                        # Max ~2 xG per 90
                        # Passing
                        'passes': 80.0,                   # Max ~80 passes per 90
                        'passes_accurate': 70.0,          # Max ~70 accurate passes per 90
                        'long_passes': 15.0,              # Max ~15 long passes per 90
                        'long_passes_accurate': 10.0,     # Max ~10 accurate long passes per 90
                        # Crossing
                        'crosses': 8.0,                   # Max ~8 crosses per 90
                        'crosses_accurate': 3.0,          # Max ~3 accurate crosses per 90
                        # Dribbling
                        'dribbles': 10.0,                 # Max ~10 dribbles per 90
                        'dribbles_successful': 6.0,       # Max ~6 successful dribbles per 90
                        # Dueling
                        'duels': 20.0,                    # Max ~20 duels per 90
                        'duels_won': 12.0,                # Max ~12 duels won per 90
                        'aerial_duels': 8.0,              # Max ~8 aerial duels per 90
                        'aerial_duels_won': 5.0,          # Max ~5 aerial duels won per 90
                        # Defensive
                        'interceptions': 8.0,             # Max ~8 interceptions per 90
                        'losses': 15.0,                   # Max ~15 losses per 90
                        'losses_own_half': 8.0,           # Max ~8 losses in own half per 90
                        'recoveries': 12.0,               # Max ~12 recoveries per 90
                        'recoveries_opp_half': 6.0        # Max ~6 recoveries in opp half per 90
                    }
                    if metric_key in per_90_max_adjustments:
                        max_val = per_90_max_adjustments[metric_key]

                normalized_value = min(100, (actual_value / max_val) * 100)

            # Ensure minimum bar length for visibility
            normalized_value = max(5, normalized_value)

            # Format the actual value for display
            if isinstance(actual_value, float):
                actual_str = f"{actual_value:.1f}"
            else:
                actual_str = f"{actual_value}"

            # Create hover text
            hover_text = f"<b>{metric_name}</b><br>Value: {actual_str}<br>Percentile: {percentile:.1f}%"

            # Add to lists
            all_metric_names.append(metric_name)
            all_percentile_values.append(percentile)
            all_actual_values.append(actual_str)
            all_normalized_values.append(normalized_value)
            all_categories.append(category)
            all_hover_texts.append(hover_text)

    # Generate colors for bars based on percentile values
    bar_colors = [get_percentile_color(value) for value in all_percentile_values]

    # Create a DataFrame for easier plotting
    df = pd.DataFrame({
        'Metric': all_metric_names,
        'Percentile': all_percentile_values,
        'NormalizedValue': all_normalized_values,  # For bar length
        'Value': all_actual_values,
        'Category': all_categories,
        'Color': bar_colors,
        'HoverText': all_hover_texts
    })

    # Sort by category and then by the original order of metrics within each category
    df['CategoryOrder'] = df['Category'].map({'General': 0, 'Defensive': 1, 'Progressive': 2, 'Offensive': 3})

    # Create a dictionary to store the original order of metrics in each category following the specified order
    metric_order = {
        'General': ['Minutes played', 'Total actions', 'Total actions successful'],
        'Defensive': ['Duels', 'Duels won', 'Aerial duels', 'Aerial duels won', 'Interceptions', 'Losses', 'Losses own half', 'Recoveries', 'Recoveries opp. half'],
        'Progressive': ['Passes', 'Passes accurate', 'Long passes', 'Long passes accurate', 'Crosses', 'Crosses accurate', 'Dribbles', 'Dribbles successful'],
        'Offensive': ['Goals', 'Assists', 'Shots', 'Shots On Target', 'xG']
    }

    # Create a mapping of metrics to their order within each category
    metric_position = {}
    for category, metrics in metric_order.items():
        for i, metric in enumerate(metrics):
            metric_position[metric] = i

    # Add the position to the dataframe
    df['MetricOrder'] = df['Metric'].map(lambda x: metric_position.get(x, 999))  # Default to high number if not found

    # Sort by category and then by the defined metric order
    df = df.sort_values(['CategoryOrder', 'MetricOrder'], ascending=[True, True])

    # Create the figure
    fig = go.Figure()

    # Add bars for each category
    for category in ['General', 'Defensive', 'Progressive', 'Offensive']:
        category_df = df[df['Category'] == category]
        if not category_df.empty:
            fig.add_trace(go.Bar(
                x=category_df['NormalizedValue'],  # Use normalized values for bar length
                y=category_df['Metric'],
                orientation='h',
                marker=dict(
                    color=category_df['Color'],  # Color still based on percentile
                    line=dict(width=0.5, color='white')
                ),
                text=category_df['Value'],  # Show actual values as text
                textposition='auto',
                hovertext=category_df['HoverText'],
                hoverinfo='text',
                name=category,
                showlegend=False
            ))

    # Add category dividers and labels (following goalkeeper pattern)
    prev_category = None
    for i, row in df.iterrows():
        if prev_category is not None and row['Category'] != prev_category:
            # Add a horizontal line between categories
            y_pos = df.index.get_loc(i) - 0.5
            fig.add_shape(
                type="line",
                x0=0, y0=y_pos,
                x1=110, y1=y_pos,  # Updated to match new x-axis range
                line=dict(color="#888888", width=0.8, dash="solid"),
                opacity=0.3,
                layer="below"
            )
        prev_category = row['Category']

    # Add category annotations (following goalkeeper pattern)
    for category in ['General', 'Defensive', 'Progressive', 'Offensive']:
        category_df = df[df['Category'] == category]
        if not category_df.empty:
            # Use the middle item in the category for positioning
            mid_idx = len(category_df) // 2

            # Add category annotation
            fig.add_annotation(
                x=105,
                y=category_df['Metric'].iloc[mid_idx],
                text=category,
                showarrow=False,
                font=dict(size=12, color="#333333"),
                align="center",
                textangle=270,
                xanchor="left",
                yanchor="middle"
            )

    # Add player info at the top as a title
    position = player_info.get('position', 'Unknown')
    team = player_info.get('team', 'Unknown')
    total_matches = player_stats.get('matches', 0)
    total_minutes = player_stats.get('minutes', 0)
    total_goals = player_stats.get('goals', 0)
    total_assists = player_stats.get('assists', 0)

    competitions = player_info.get('competitions', 'All competitions')
    per_90_mode = player_info.get('per_90_mode', False)
    stats_mode = " (Per 90 min)" if per_90_mode else ""

    player_info_text = f"<b>{player_name}</b>{stats_mode}<br>{position} | {team}<br>Competitions: {competitions}<br>Matches: {total_matches} | Minutes: {total_minutes} | Goals: {total_goals} | Assists: {total_assists}"

    # Add player info as an annotation at the top of the chart
    fig.add_annotation(
        x=0.01,  # Left side of the chart
        y=1.05,  # Above the chart
        text=player_info_text,
        showarrow=False,
        font=dict(size=14, color="#333333"),
        align="left",
        xanchor="left",
        yanchor="bottom",
        xref="paper",
        yref="paper"
    )

    # Add percentile legend at the bottom
    legend_items = [
        {'color': '#d73027', 'label': '1-20%'},
        {'color': '#fc8d59', 'label': '21-40%'},
        {'color': '#f9d057', 'label': '41-60%'},
        {'color': '#73c378', 'label': '61-80%'},
        {'color': '#1a9641', 'label': '81-100%'}
    ]

    legend_text = " | ".join([f'<span style="color:{item["color"]}">\u25A0</span> {item["label"]}' for item in legend_items])

    # Add legend as an annotation at the bottom
    fig.add_annotation(
        x=0.5,  # Center of the chart
        y=-0.15,  # Below the chart
        text=legend_text,
        showarrow=False,
        font=dict(size=10, color="#333333"),
        align="center",
        xanchor="center",
        yanchor="top",
        xref="paper",
        yref="paper"
    )

    # Update layout
    fig.update_layout(
        title=None,
        xaxis=dict(
            title="Relative Performance",
            range=[0, 110],
            showgrid=True,
            gridcolor='rgba(136, 136, 136, 0.2)',
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=10, color='#666666')
        ),
        yaxis=dict(
            title=None,
            autorange="reversed",
            tickfont=dict(size=10, color='#333333')
        ),
        margin=dict(l=10, r=50, t=120, b=80),
        plot_bgcolor='#F9F7F2',
        paper_bgcolor='#F9F7F2',
        height=600,
        width=800,
        barmode='stack',
        bargap=0.15,
        hovermode='closest'
    )

    # Add grid lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(136, 136, 136, 0.2)')

    return fig


def display_outfield_role_analysis_advanced(selected_players, player_stats, position_type, per_90_mode):
    """
    Display advanced role analysis for outfield players following the goalkeeper pattern.
    """
    role_stats_mode_text = " (Per 90 Minutes)" if per_90_mode else ""
    st.subheader(f"Player Role Analysis{role_stats_mode_text}")

    if per_90_mode:
        st.info("📊 **Per 90 Minutes Mode**: All statistics have been normalized to per 90 minutes of play for fair comparison between players with different playing time.")

    # Define role weights based on position type
    if position_type == "Forwards" or any("CF" in str(stats.get("position", "")) for stats in player_stats):
        role_weights = {
            "Advance Forward": {
                "goals": 0.3,
                "shots": 0.2,
                "shots_on_target": 0.15,  # Using available metric instead of xG
                "dribbles_successful": 0.15,
                "passes": 0.1,  # Using available metric instead of Passes Received
                "minutes": 0.1  # Using available metric instead of Touches Att 3rd
            },
            "Pressing Forward": {
                "duels_won": 0.25,
                "recoveries": 0.2,
                "interceptions": 0.2,  # Using available metric instead of Pressures
                "goals": 0.15,
                "shots": 0.1,
                "duel_success_rate": 0.1
            },
            "Deep-lying Forward": {
                "assists": 0.25,  # Using available metric instead of SCA
                "passes_accurate": 0.25,  # Using available metric instead of xAG
                "pass_accuracy": 0.15,  # Using available metric instead of Key Passes
                "passes": 0.15,  # Using available metric instead of Progressive Passes Received
                "dribbles": 0.1,  # Using available metric instead of Touches Att 3rd
                "goals": 0.1  # Using available metric instead of npxG
            },
            "Poacher": {
                "goals": 0.5,  # Using available metric instead of npxG
                "shots": 0.3,
                "shots_on_target": 0.2
            }
        }
        role_type = "Center Forward"
    elif position_type == "Defenders" or any("CB" in str(stats.get("position", "")) for stats in player_stats):
        role_weights = {
            "No-Nonsense Centre-Back": {
                "duels_won": 0.25,  # Using available metric instead of Aerial duels won
                "duel_success_rate": 0.2,
                "recoveries": 0.2,  # Using available metric instead of Clearances
                "interceptions": 0.15,
                "duels": 0.1,  # Using available metric instead of Blocks
                "passes_accurate": 0.1  # Using available metric instead of Tackles won
            },
            "Central Defender": {
                "duels_won": 0.2,  # Using available metric instead of Aerial duels won
                "duel_success_rate": 0.2,
                "interceptions": 0.15,
                "recoveries": 0.15,  # Using available metric instead of Clearances
                "passes_accurate": 0.15,
                "duels": 0.1,  # Using available metric instead of Blocks
                "pass_accuracy": 0.05  # Using available metric instead of Tackles won
            },
            "Ball Playing Defender": {
                "passes_accurate": 0.25,
                "pass_accuracy": 0.2,  # Using available metric instead of Long passes accurate
                "passes": 0.15,  # Using available metric instead of Progressive passes
                "duels_won": 0.15,  # Using available metric instead of Aerial duels won
                "duel_success_rate": 0.1,
                "interceptions": 0.1,
                "recoveries": 0.05  # Using available metric instead of Clearances
            }
        }
        role_type = "Center Back"
    else:
        st.info(f"Role analysis for {position_type} will be implemented with position-specific roles.")
        return

    st.write(f"**{role_type} Role Analysis**")

    # Define role descriptions
    role_descriptions = {
        "Advance Forward": "A goal-focused striker who excels at finishing, shooting, and creating chances in the final third. High goal output and clinical finishing.",
        "Pressing Forward": "An aggressive forward who presses defenders, wins duels, and contributes defensively. High work rate and physical presence.",
        "Deep-lying Forward": "A creative forward who drops deep to create chances for teammates. Strong in assists, passing, and link-up play.",
        "Poacher": "A clinical finisher who specializes in being in the right place at the right time. Exceptional goal conversion and positioning.",
        "No-Nonsense Centre-Back": "A traditional defender focused on winning duels, clearing danger, and physical defending. Strong aerial presence and defensive actions.",
        "Central Defender": "A balanced center-back who combines defensive solidity with decent passing. Well-rounded defensive skills.",
        "Ball Playing Defender": "A modern center-back who excels at passing and building play from the back. Strong technical skills and distribution."
    }

    # Compute role scores using the same function as goalkeeper comparison
    def compute_role_scores(player_stats_list, weights):
        # Gather all unique stats from all roles
        all_stats = set()
        for role_weights in weights.values():
            all_stats.update(role_weights.keys())

        # Calculate min and max values for normalization across all players
        stat_min = {}
        stat_max = {}

        for stat in all_stats:
            values = [float(stats.get(stat, 0)) for stats in player_stats_list]
            stat_min[stat] = min(values)
            stat_max[stat] = max(values)

        scores = []
        for stats in player_stats_list:
            player_score = {}

            for role, role_weights in weights.items():
                score = 0
                total_weight = 0

                for stat, weight in role_weights.items():
                    if stat in stats:
                        val = float(stats[stat])

                        # Handle negative weights (where lower values are better)
                        if weight < 0:
                            # For negative weights, invert the normalization
                            if stat_max[stat] != stat_min[stat]:
                                norm = 1 - ((val - stat_min[stat]) / (stat_max[stat] - stat_min[stat]))
                            else:
                                norm = 0.5
                            score += abs(weight) * norm
                        else:
                            # For positive weights, normal normalization
                            if stat_max[stat] != stat_min[stat]:
                                norm = (val - stat_min[stat]) / (stat_max[stat] - stat_min[stat])
                            else:
                                norm = 0.5
                            score += weight * norm

                        total_weight += abs(weight)

                # Normalize the score by total weight to get a 0-1 scale
                if total_weight > 0:
                    player_score[role] = score / total_weight
                else:
                    player_score[role] = 0

            scores.append(player_score)
        return scores

    # Compute scores for all players
    role_scores = compute_role_scores(player_stats, role_weights)

    # Define colors for each player
    player_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    # Create a row for player profiles
    if selected_players:
        player_cols = st.columns(len(selected_players))

        # Create a profile chart for each player
        for i, (player, player_score, col) in enumerate(zip(selected_players, role_scores, player_cols)):
            with col:
                # Create player title with info
                player_matches = player_stats[i].get('matches', 0)
                player_team = player_stats[i].get('team', 'Unknown')
                player_position = player_stats[i].get('position', 'Unknown')
                st.markdown(f"<h3 style='text-align: center; margin-bottom: 10px; font-size: 16px;'>{player} ({player_position})</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; margin-bottom: 10px; font-size: 12px; color: #333;'>{player_team} | {player_matches} matches</p>", unsafe_allow_html=True)

                # Create separate figure for this player
                fig = go.Figure()

                # Sort role scores for this player from highest to lowest
                sorted_roles = sorted([(role, player_score[role]) for role in role_weights.keys()], key=lambda x: x[1], reverse=True)
                role_labels = [role for role, _ in sorted_roles]
                role_values = [score for _, score in sorted_roles]

                # Add trace for horizontal bar
                fig.add_trace(go.Bar(
                    y=role_labels,
                    x=role_values,
                    orientation='h',
                    marker=dict(
                        color=player_colors[i % len(player_colors)],
                        line=dict(width=1, color='#333'),
                        opacity=0.8
                    ),
                    text=[f"{value:.2f}" for value in role_values],
                    textposition='auto',
                    textfont=dict(color='black', size=10),
                    showlegend=False
                ))

                # Update layout
                fig.update_layout(
                    title=dict(
                        text="Role Score Distribution",
                        font=dict(size=12),
                        x=0.5
                    ),
                    plot_bgcolor='#F9F7F2',
                    paper_bgcolor='#F9F7F2',
                    height=250,
                    margin=dict(l=15, r=15, t=40, b=20),
                    xaxis=dict(
                        title='Score',
                        showgrid=True,
                        gridcolor='rgba(136, 136, 136, 0.2)',
                        tickfont=dict(size=9, color='#CCC'),
                        range=[0, max(role_values) * 1.1] if role_values else [0, 1]
                    ),
                    yaxis=dict(
                        title='',
                        tickfont=dict(size=10, color='#CCC'),
                        automargin=True
                    ),
                    font=dict(color='#EEE')
                )

                # Display chart
                st.plotly_chart(fig, use_container_width=True)

                # Add detailed score breakdown table
                with st.expander(f"📊 {player} - Detailed Score Breakdown", expanded=False):
                    for role, role_weights_dict in role_weights.items():
                        st.markdown(f"**{role}** (Total Score: {player_score[role]:.3f})")

                        role_breakdown = []
                        total_weight = sum(abs(w) for w in role_weights_dict.values())

                        for stat, weight in role_weights_dict.items():
                            if stat in player_stats[i]:
                                val = float(player_stats[i][stat])

                                # Get min/max for this stat across all players
                                all_values = [float(p.get(stat, 0)) for p in player_stats]
                                stat_min = min(all_values)
                                stat_max = max(all_values)

                                # Calculate normalized value
                                if weight < 0:
                                    if stat_max != stat_min:
                                        norm = 1 - ((val - stat_min) / (stat_max - stat_min))
                                    else:
                                        norm = 0.5
                                    contribution = (abs(weight) * norm) / total_weight
                                else:
                                    if stat_max != stat_min:
                                        norm = (val - stat_min) / (stat_max - stat_min)
                                    else:
                                        norm = 0.5
                                    contribution = (weight * norm) / total_weight

                                # Format stat name for display
                                display_stat = stat.replace('_', ' ').title()

                                role_breakdown.append({
                                    "Statistic": display_stat,
                                    "Raw Value": f"{val:.1f}" if isinstance(val, float) else str(int(val)),
                                    "Weight": f"{weight:.2f}",
                                    "Normalized": f"{norm:.3f}",
                                    "Contribution": f"{contribution:.3f}"
                                })

                        # Create DataFrame for this role
                        if role_breakdown:
                            role_df = pd.DataFrame(role_breakdown)
                            st.dataframe(role_df, use_container_width=True, hide_index=True)

                        st.markdown("---")

    # Add summary comparison table
    if selected_players:
        st.subheader("Role Score Summary")

        # Create summary table
        summary_data = []
        for i, player in enumerate(selected_players):
            player_row = {"Player": player}
            for role in role_weights.keys():
                player_row[role] = f"{role_scores[i][role]:.3f}"
            summary_data.append(player_row)

        summary_df = pd.DataFrame(summary_data)

        # Style the summary table with color coding
        def highlight_max_role(s):
            """Highlight the maximum value in each role column"""
            if s.name == "Player":
                return [''] * len(s)

            # Convert to float for comparison, excluding non-numeric values
            numeric_values = []
            for val in s:
                try:
                    numeric_values.append(float(val))
                except:
                    numeric_values.append(0)

            max_val = max(numeric_values)
            return ['background-color: #90EE90' if float(val) == max_val else '' for val in s]

        styled_summary = summary_df.style.apply(highlight_max_role, axis=0)
        st.dataframe(styled_summary, use_container_width=True, hide_index=True)

        st.markdown("*Green highlighting indicates the highest score for each role*")

    # Add info message for outfield roles
    st.info(f"""
**{role_type} Role Analysis**: Each player is scored for different playing styles based on their statistics:

{chr(10).join([f"- **{role}**: {desc}" for role, desc in role_descriptions.items() if role in role_weights])}

**How to Read the Detailed Breakdown**:
- **Raw Value**: The actual statistic value for the player
- **Weight**: How important this statistic is for the role (negative means lower is better)
- **Normalized**: The statistic normalized to 0-1 scale compared to other players
- **Contribution**: How much this statistic contributes to the final role score
    """)

    st.markdown("---")


def display_outfield_scatter_plot_analysis(selected_players, player_stats, position_type, per_90_mode, filtered_data):
    """
    Display scatter plot analysis for outfield players following the goalkeeper pattern.
    """
    st.subheader("Performance Scatter Plot")

    # Define outfield-specific preset combinations
    if position_type == "Forwards":
        preset_combinations = {
            "Goals vs xG": ("goals", "xg"),
            "Shots vs Passes": ("shots", "passes_accurate"),
            "Dribbles vs Assists": ("dribbles_successful", "assists"),
            "Duels vs Recoveries": ("duels_won", "recoveries"),
            "Aerial Duels vs Goals": ("aerial_duels_won", "goals"),
            "Custom Selection": ("custom", "custom")
        }
    elif position_type == "Defenders":
        preset_combinations = {
            "Aerial vs Passing": ("aerial_duels_won", "passes_accurate"),
            "Defensive vs Distribution": ("duels_won", "long_passes_accurate"),
            "Physical vs Technical": ("clearances", "progressive_passes"),
            "Interceptions vs Build-up": ("interceptions", "progressive_passes"),
            "Tackling vs Positioning": ("tackles_won", "recoveries"),
            "Aerial vs Ground": ("aerial_duels_won", "duels_won"),
            "Custom Selection": ("custom", "custom")
        }
    else:  # All Outfield or Midfielders
        preset_combinations = {
            "Goals vs xG": ("goals", "xg"),
            "Shots vs Passes": ("shots", "passes_accurate"),
            "Dribbles vs Assists": ("dribbles_successful", "assists"),
            "Pass Accuracy vs Dribble Success": ("pass_accuracy", "dribble_success_rate"),
            "Duels vs Recoveries": ("duels_won", "recoveries"),
             "Aerial vs Passing": ("aerial_duels_won", "passes_accurate"),
            "Defensive vs Distribution": ("duels_won", "long_passes_accurate"),
            "Physical vs Technical": ("clearances", "progressive_passes"),
            "Interceptions vs Build-up": ("interceptions", "progressive_passes"),
            "Tackling vs Positioning": ("tackles_won", "recoveries"),
            "Aerial vs Ground": ("aerial_duels_won", "duels_won"),
            "Custom Selection": ("custom", "custom")
        }

    # Define comprehensive preset explanations
    if position_type == "Forwards":
        preset_explanations = {
            "Goals vs xG": "This analysis reveals finishing efficiency and clinical ability. "
                          "Overperformers consistently exceed expected goals through superior finishing technique, "
                          "while underperformers may need to improve shot placement or decision-making in the box.",

            "Shots vs Passes": "This perspective shows attacking approach and involvement style. "
                              "Direct attackers focus on shooting opportunities and getting into scoring positions, "
                              "while build-up forwards are more involved in team play and creating chances for others.",

            "Dribbles vs Assists": "This highlights individual skill versus creative output balance. "
                                  "Technical dribblers excel at beating opponents 1v1 and creating space, "
                                  "while creative assisters focus on final passes and setting up teammates.",

            "Duels vs Recoveries": "This shows physical presence versus work rate in attacking areas. "
                                  "Physical forwards win battles and hold up play effectively, "
                                  "while energetic forwards press intensively and win back possession quickly.",

            "Aerial Duels vs Goals": "This reveals aerial threat and finishing ability combination. "
                                    "Dominant aerial forwards excel at winning headers and converting crosses, "
                                    "while ground-based finishers rely more on feet and movement in the box."
        }

    elif position_type == "Defenders":
        preset_explanations = {
            "Aerial vs Passing": "This perspective shows defensive style and modern game adaptation. "
                                "Aerial specialists dominate in the air and clear danger effectively, "
                                "while ball-playing defenders excel at distribution and building from the back.",

            "Defensive vs Distribution": "This reveals the balance between defending and playmaking roles. "
                                       "Traditional defenders focus on winning duels and physical battles, "
                                       "while modern defenders contribute significantly to team's passing game.",

            "Physical vs Technical": "This highlights defensive approach and skill specialization. "
                                    "Physical defenders rely on clearances and direct defending, "
                                    "while technical defenders use progressive passing to start attacks.",

            "Interceptions vs Build-up": "This shows anticipation versus creative contribution balance. "
                                        "Intelligent defenders read the game well and intercept passes, "
                                        "while progressive defenders focus on advancing play through passing.",

            "Tackling vs Positioning": "This reveals defensive style and tactical intelligence. "
                                      "Active tacklers engage opponents directly and win the ball back, "
                                      "while positional defenders use smart positioning to make recoveries.",

            "Aerial vs Ground": "This perspective shows aerial dominance versus overall duel success. "
                               "Aerial specialists excel specifically in headed duels and crosses, "
                               "while complete defenders are effective in all types of physical contests."
        }

    else:  # All Outfield or Midfielders
        preset_explanations = {
            "Goals vs xG": "This analysis reveals finishing efficiency and clinical ability across all positions. "
                          "Overperformers consistently exceed expected goals through superior finishing technique, "
                          "while underperformers may need to improve shot placement or decision-making.",

            "Shots vs Passes": "This perspective shows attacking approach versus involvement in build-up play. "
                              "Direct players focus on shooting opportunities and getting into scoring positions, "
                              "while build-up players are more involved in team play and creating chances.",

            "Dribbles vs Assists": "This highlights individual skill versus creative output balance. "
                                  "Technical dribblers excel at beating opponents 1v1 and creating space, "
                                  "while creative assisters focus on final passes and setting up teammates.",

            "Pass Accuracy vs Dribble Success": "This reveals technical precision versus individual skill specialization. "
                                               "Safe passers maintain high accuracy and control possession, "
                                               "while skillful dribblers excel at beating opponents in 1v1 situations.",

            "Duels vs Recoveries": "This shows physical presence versus work rate across the pitch. "
                                  "Physical players win battles and dominate in duels, "
                                  "while energetic players press intensively and win back possession quickly."
        }

    # Let user select a preset or custom
    selected_preset = st.selectbox(
        "Choose analysis perspective:",
        options=list(preset_combinations.keys()),
        index=0
    )

    # Add explanation for the selected preset
    if selected_preset in preset_explanations:
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 10px 0; font-style: italic; color: #555;">
            {preset_explanations[selected_preset]}
        </div>
        """, unsafe_allow_html=True)

    # Define quadrant descriptions based on the selected preset
    def get_quadrant_descriptions(preset_name, x_stat, y_stat):
        """Get quadrant descriptions for the scatter plot based on preset combination."""

        # Position-specific quadrant descriptions
        if position_type == "Forwards":
            if preset_name == "Goals vs xG":
                return {
                    "top_right": "Clinical Overperformers - High goals AND high xG (elite finishers)",
                    "top_left": "Efficient Finishers - Low goals but high xG (clinical)",
                    "bottom_right": "Lucky Scorers - High goals but low xG (overperforming)",
                    "bottom_left": "Limited Threats - Low goals AND low xG (ineffective)"
                }
            elif preset_name == "Shots vs Passes":
                return {
                    "top_right": "Complete Attackers - Many shots AND many passes (involved)",
                    "top_left": "Build-up Forwards - Few shots but many passes (creators)",
                    "bottom_right": "Direct Shooters - Many shots but few passes (finishers)",
                    "bottom_left": "Limited Involvement - Few shots AND few passes (peripheral)"
                }
            elif preset_name == "Dribbles vs Assists":
                return {
                    "top_right": "Creative Dribblers - Many dribbles AND many assists (complete)",
                    "top_left": "Pure Creators - Few dribbles but many assists (passers)",
                    "bottom_right": "Individual Threats - Many dribbles but few assists (selfish)",
                    "bottom_left": "Limited Creativity - Few dribbles AND few assists (basic)"
                }
            elif preset_name == "Duels vs Recoveries":
                return {
                    "top_right": "Physical Workers - Many duels AND many recoveries (complete)",
                    "top_left": "Pressing Forwards - Few duels but many recoveries (energetic)",
                    "bottom_right": "Physical Forwards - Many duels but few recoveries (static)",
                    "bottom_left": "Passive Forwards - Few duels AND few recoveries (uninvolved)"
                }
            elif preset_name == "Aerial Duels vs Goals":
                return {
                    "top_right": "Aerial Goalscorers - Many aerial duels AND many goals (complete)",
                    "top_left": "Ground Finishers - Few aerial duels but many goals (technical)",
                    "bottom_right": "Aerial Specialists - Many aerial duels but few goals (target men)",
                    "bottom_left": "Limited Threats - Few aerial duels AND few goals (ineffective)"
                }

        elif position_type == "Defenders":
            if preset_name == "Aerial vs Passing":
                return {
                    "top_right": "Complete Modern Defenders - Many aerial duels AND many passes (elite)",
                    "top_left": "Ball-Playing Defenders - Few aerial duels but many passes (technical)",
                    "bottom_right": "Aerial Specialists - Many aerial duels but few passes (traditional)",
                    "bottom_left": "Limited Defenders - Few aerial duels AND few passes (passive)"
                }
            elif preset_name == "Defensive vs Distribution":
                return {
                    "top_right": "Complete Defenders - Many duels AND many long passes (modern)",
                    "top_left": "Progressive Defenders - Few duels but many long passes (playmakers)",
                    "bottom_right": "Traditional Defenders - Many duels but few long passes (physical)",
                    "bottom_left": "Limited Defenders - Few duels AND few long passes (ineffective)"
                }
            elif preset_name == "Physical vs Technical":
                return {
                    "top_right": "Complete Defenders - Many clearances AND many progressive passes (balanced)",
                    "top_left": "Technical Defenders - Few clearances but many progressive passes (modern)",
                    "bottom_right": "Physical Defenders - Many clearances but few progressive passes (traditional)",
                    "bottom_left": "Limited Defenders - Few clearances AND few progressive passes (passive)"
                }
            elif preset_name == "Interceptions vs Build-up":
                return {
                    "top_right": "Intelligent Playmakers - Many interceptions AND many progressive passes (complete)",
                    "top_left": "Progressive Defenders - Few interceptions but many progressive passes (builders)",
                    "bottom_right": "Smart Defenders - Many interceptions but few progressive passes (readers)",
                    "bottom_left": "Passive Defenders - Few interceptions AND few progressive passes (uninvolved)"
                }
            elif preset_name == "Tackling vs Positioning":
                return {
                    "top_right": "Active Defenders - Many tackles AND many recoveries (busy)",
                    "top_left": "Positional Defenders - Few tackles but many recoveries (smart)",
                    "bottom_right": "Aggressive Defenders - Many tackles but few recoveries (direct)",
                    "bottom_left": "Passive Defenders - Few tackles AND few recoveries (uninvolved)"
                }
            elif preset_name == "Aerial vs Ground":
                return {
                    "top_right": "Complete Defenders - Many aerial duels AND many ground duels (dominant)",
                    "top_left": "Ground Specialists - Few aerial duels but many ground duels (technical)",
                    "bottom_right": "Aerial Specialists - Many aerial duels but few ground duels (headers)",
                    "bottom_left": "Limited Defenders - Few aerial duels AND few ground duels (passive)"
                }

        else:  # All Outfield or Midfielders
            if preset_name == "Goals vs xG":
                return {
                    "top_right": "Clinical Overperformers - High goals AND high xG (elite finishers)",
                    "top_left": "Efficient Players - Low goals but high xG (clinical)",
                    "bottom_right": "Lucky Scorers - High goals but low xG (overperforming)",
                    "bottom_left": "Limited Threats - Low goals AND low xG (defensive)"
                }
            elif preset_name == "Shots vs Passes":
                return {
                    "top_right": "Complete Players - Many shots AND many passes (involved)",
                    "top_left": "Build-up Players - Few shots but many passes (creators)",
                    "bottom_right": "Direct Players - Many shots but few passes (attackers)",
                    "bottom_left": "Limited Involvement - Few shots AND few passes (defensive)"
                }
            elif preset_name == "Dribbles vs Assists":
                return {
                    "top_right": "Creative Dribblers - Many dribbles AND many assists (complete)",
                    "top_left": "Pure Creators - Few dribbles but many assists (passers)",
                    "bottom_right": "Individual Players - Many dribbles but few assists (skillful)",
                    "bottom_left": "Limited Creativity - Few dribbles AND few assists (basic)"
                }
            elif preset_name == "Pass Accuracy vs Dribble Success":
                return {
                    "top_right": "Technical Masters - High accuracy AND high dribble success (complete)",
                    "top_left": "Safe Passers - High accuracy but low dribble success (conservative)",
                    "bottom_right": "Risk Takers - Low accuracy but high dribble success (flair)",
                    "bottom_left": "Limited Technical - Low accuracy AND low dribble success (basic)"
                }
            elif preset_name == "Duels vs Recoveries":
                return {
                    "top_right": "Physical Workers - Many duels AND many recoveries (complete)",
                    "top_left": "Energetic Players - Few duels but many recoveries (pressing)",
                    "bottom_right": "Physical Players - Many duels but few recoveries (static)",
                    "bottom_left": "Passive Players - Few duels AND few recoveries (uninvolved)"
                }

        # Default quadrant descriptions
        return {
            "top_right": f"High {y_stat.replace('_', ' ').title()} & High {x_stat.replace('_', ' ').title()}",
            "top_left": f"High {y_stat.replace('_', ' ').title()} & Low {x_stat.replace('_', ' ').title()}",
            "bottom_right": f"Low {y_stat.replace('_', ' ').title()} & High {x_stat.replace('_', ' ').title()}",
            "bottom_left": f"Low {y_stat.replace('_', ' ').title()} & Low {x_stat.replace('_', ' ').title()}"
        }

    # Get the preset values
    preset_x, preset_y = preset_combinations[selected_preset]

    # Create columns for selecting stats for each axis
    scatter_cols = st.columns(2)

    # Define available stats for outfield players
    outfield_available_stats = [
        "goals", "assists", "shots", "shots_on_target", "shot_accuracy",
        "passes", "passes_accurate", "pass_accuracy", "dribbles", "dribbles_successful", "dribble_success_rate",
        "duels", "duels_won", "duel_success_rate", "interceptions", "recoveries",
        "minutes", "matches"
    ]

    # Define stat categories for filtering
    outfield_stat_categories = {
        "Attacking": ["goals", "assists", "shots", "shots_on_target", "shot_accuracy"],
        "Technical": ["passes", "passes_accurate", "pass_accuracy", "dribbles", "dribbles_successful", "dribble_success_rate"],
        "Defensive": ["duels", "duels_won", "duel_success_rate", "interceptions", "recoveries"],
        "General": ["minutes", "matches"]
    }

    with scatter_cols[0]:
        if preset_x == "custom":
            # Add category filter for stats
            x_stat_category = st.radio(
                "Filter X-axis stats by category:",
                options=["All"] + list(outfield_stat_categories.keys()),
                horizontal=True,
                key="x_stat_category"
            )

            # Filter stats based on selected category
            if x_stat_category == "All":
                x_filtered_stats = outfield_available_stats
            else:
                x_filtered_stats = outfield_stat_categories.get(x_stat_category, outfield_available_stats)

            x_stat = st.selectbox(
                "X-Axis Statistic:",
                options=x_filtered_stats,
                index=0,
                key="x_stat_selector"
            )
        else:
            x_stat = preset_x
            # Convert display name to stat key
            display_name = preset_x.replace('_', ' ').title()
            st.markdown(f"**X-Axis**: {display_name}")

    with scatter_cols[1]:
        if preset_y == "custom":
            # Add category filter for stats
            y_stat_category = st.radio(
                "Filter Y-axis stats by category:",
                options=["All"] + list(outfield_stat_categories.keys()),
                horizontal=True,
                key="y_stat_category"
            )

            # Filter stats based on selected category
            if y_stat_category == "All":
                y_filtered_stats = outfield_available_stats
            else:
                y_filtered_stats = outfield_stat_categories.get(y_stat_category, outfield_available_stats)

            y_stat = st.selectbox(
                "Y-Axis Statistic:",
                options=y_filtered_stats,
                index=0,
                key="y_stat_selector"
            )
        else:
            y_stat = preset_y
            # Convert display name to stat key
            display_name = preset_y.replace('_', ' ').title()
            st.markdown(f"**Y-Axis**: {display_name}")

    # Add configuration options for scatter plot
    include_additional_players = st.checkbox("Include Additional Players from Competition", value=False,
                                            help="Add other outfield players from selected competition for better context (same position type only)")

    # Additional competition selection if including other players
    additional_competition = None
    if include_additional_players:
        # Get available competitions from the date-filtered data
        if filtered_data:
            all_competitions = set()
            for player_data in filtered_data.values():
                # Extract competitions from match data
                for match in player_data.get("match_data", []):
                    competition = match.get("Competition")
                    if competition:
                        all_competitions.add(competition)
            available_comps = sorted(list(all_competitions)) if all_competitions else ["Indonesia Liga 1"]
        else:
            available_comps = ["Indonesia Liga 1"]

        additional_competition = st.selectbox(
            "Select competition for additional players:",
            options=available_comps,
            index=0,
            help="Choose which competition to include additional players from (same position type only, within date filter)"
        )

    if selected_players:
        # Generate and display the outfield scatter plot
        plotly_fig = create_outfield_scatter_plot(
            selected_players,
            player_stats,
            x_stat,
            y_stat,
            position_type,
            per_90_mode=per_90_mode,
            additional_players_data=None  # TODO: Implement additional players support
        )

        if plotly_fig:
            st.plotly_chart(plotly_fig, use_container_width=True)
        else:
            st.warning("Unable to generate scatter plot. Please check the selected statistics.")

    st.markdown("---")


def create_outfield_scatter_plot(players, player_stats_list, x_stat, y_stat, position_type, per_90_mode=False, additional_players_data=None):
    """
    Create an interactive scatter plot for outfield players following the goalkeeper pattern.
    """
    # Combine selected players with additional players if provided
    all_players = players.copy()
    all_player_stats = player_stats_list.copy()

    if additional_players_data:
        for player_name, stats in additional_players_data.items():
            if player_name not in players:  # Avoid duplicates
                all_players.append(player_name)
                all_player_stats.append(stats)

    # Calculate percentiles for the selected stats using all players
    x_values = []
    y_values = []

    for stats in all_player_stats:
        x_val = float(stats.get(x_stat, 0))
        y_val = float(stats.get(y_stat, 0))
        x_values.append(x_val)
        y_values.append(y_val)

    # Calculate percentiles
    def calculate_percentile(value, all_values):
        if len(all_values) <= 1:
            return 50

        # Calculate percentile rank
        rank = sum(1 for v in all_values if v < value)
        percentile = (rank / (len(all_values) - 1)) * 100

        return max(5, min(95, percentile))

    # Prepare data for plotting
    data = []
    selected_player_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    additional_player_color = '#CCCCCC'  # Gray for additional players

    # Plot all players (selected + additional)
    for i, (player, stats) in enumerate(zip(all_players, all_player_stats)):
        # Determine if this is a selected player or additional player
        is_selected_player = player in players
        x_val = x_values[i]
        y_val = y_values[i]

        x_percentile = calculate_percentile(x_val, x_values)
        y_percentile = calculate_percentile(y_val, y_values)

        # Determine color and size based on player type
        if is_selected_player:
            # Get the index of this player in the original selected players list
            selected_index = players.index(player)
            player_color = selected_player_colors[selected_index % len(selected_player_colors)]
            marker_size = 15
            opacity = 0.85
            line_width = 2
            show_text = True
        else:
            player_color = additional_player_color
            marker_size = 8
            opacity = 0.4
            line_width = 1
            show_text = False

        # Create hover text
        player_type = "Selected Player" if is_selected_player else "Additional Player"
        hover_text = f"<b>{player}</b> ({player_type})<br>"

        # Format stat names for display
        x_display = x_stat.replace('_', ' ').title()
        y_display = y_stat.replace('_', ' ').title()

        # Add per 90 indicator if enabled
        x_label = f"{x_display}" + (" (per 90)" if per_90_mode and x_stat not in ["minutes", "matches"] else "")
        y_label = f"{y_display}" + (" (per 90)" if per_90_mode and y_stat not in ["minutes", "matches"] else "")

        hover_text += f"{x_label}: {x_val:.2f} ({x_percentile:.0f}%)<br>"
        hover_text += f"{y_label}: {y_val:.2f} ({y_percentile:.0f}%)<br>"

        # Add additional key stats
        additional_stats = ["goals", "assists", "passes_accurate", "duels_won"]
        for stat in additional_stats:
            if stat != x_stat and stat != y_stat and stat in stats:
                stat_val = float(stats[stat])
                stat_display = stat.replace('_', ' ').title()
                stat_label = f"{stat_display}" + (" (per 90)" if per_90_mode and stat not in ["minutes", "matches"] else "")
                hover_text += f"{stat_label}: {stat_val:.2f}<br>"

        data.append({
            'name': player,
            'x': x_val,  # Use exact filtered value instead of percentile
            'y': y_val,  # Use exact filtered value instead of percentile
            'color': player_color,
            'text': hover_text,
            'is_selected': is_selected_player,
            'marker_size': marker_size,
            'opacity': opacity,
            'line_width': line_width,
            'show_text': show_text
        })

    if not data:
        return None

    # Create plotly figure
    fig = go.Figure()

    # Add quadrant lines
    fig.add_shape(
        type="line", x0=0, y0=50, x1=100, y1=50,
        line=dict(color="#666666", width=1)
    )
    fig.add_shape(
        type="line", x0=50, y0=0, x1=50, y1=100,
        line=dict(color="#666666", width=1)
    )

    # Generate quadrant descriptions for outfield players
    def get_outfield_quadrant_descriptions(x_stat, y_stat, position_type, x_range, y_range):
        # Define outfield role descriptions based on position
        if position_type == "Forwards":
            role_descriptions = {
                "goals": {"high": "Clinical Finisher", "low": "Creative Player"},
                "assists": {"high": "Playmaker", "low": "Goal Scorer"},
                "shots": {"high": "Volume Shooter", "low": "Selective Shooter"},
                "shot_accuracy": {"high": "Clinical Finisher", "low": "Volume Shooter"},
                "dribbles_successful": {"high": "Skillful Dribbler", "low": "Direct Player"},
                "passes_accurate": {"high": "Technical Player", "low": "Direct Player"},
                "pass_accuracy": {"high": "Safe Passer", "low": "Risk Taker"}
            }
        elif position_type == "Defenders":
            role_descriptions = {
                "duels_won": {"high": "Physical Defender", "low": "Positional Defender"},
                "interceptions": {"high": "Ball Winner", "low": "Reactive Defender"},
                "pass_accuracy": {"high": "Ball Playing Defender", "low": "Direct Defender"},
                "passes_accurate": {"high": "Build-up Specialist", "low": "Simple Distributor"},
                "recoveries": {"high": "Active Defender", "low": "Positional Defender"},
                "duel_success_rate": {"high": "Dominant Defender", "low": "Technical Defender"}
            }
        else:  # All Outfield or Midfielders
            role_descriptions = {
                "goals": {"high": "Goal Threat", "low": "Support Player"},
                "assists": {"high": "Creative Player", "low": "Goal Scorer"},
                "pass_accuracy": {"high": "Safe Passer", "low": "Risk Taker"},
                "dribble_success_rate": {"high": "Skillful Player", "low": "Direct Player"},
                "passes_accurate": {"high": "Ball Distributor", "low": "Simple Passer"},
                "duels_won": {"high": "Physical Player", "low": "Technical Player"}
            }

        # Get descriptions
        x_high = role_descriptions.get(x_stat, {}).get("high", f"High {x_stat.replace('_', ' ').title()}")
        x_low = role_descriptions.get(x_stat, {}).get("low", f"Low {x_stat.replace('_', ' ').title()}")
        y_high = role_descriptions.get(y_stat, {}).get("high", f"High {y_stat.replace('_', ' ').title()}")
        y_low = role_descriptions.get(y_stat, {}).get("low", f"Low {y_stat.replace('_', ' ').title()}")

        # Calculate quadrant positions based on actual data ranges
        x_mid = (x_range[0] + x_range[1]) / 2
        y_mid = (y_range[0] + y_range[1]) / 2
        x_quarter = (x_range[1] - x_range[0]) / 4
        y_quarter = (y_range[1] - y_range[0]) / 4

        return [
            dict(x=x_range[0] + x_quarter, y=y_mid + y_quarter, text=f"{x_low}<br>{y_high}", showarrow=False,
                 font=dict(color="#AAAAAA", size=12), xanchor="center", yanchor="middle", align="center"),
            dict(x=x_mid + x_quarter, y=y_mid + y_quarter, text=f"{x_high}<br>{y_high}", showarrow=False,
                 font=dict(color="#AAAAAA", size=12), xanchor="center", yanchor="middle", align="center"),
            dict(x=x_range[0] + x_quarter, y=y_range[0] + y_quarter, text=f"{x_low}<br>{y_low}", showarrow=False,
                 font=dict(color="#AAAAAA", size=12), xanchor="center", yanchor="middle", align="center"),
            dict(x=x_mid + x_quarter, y=y_range[0] + y_quarter, text=f"{x_high}<br>{y_low}", showarrow=False,
                 font=dict(color="#AAAAAA", size=12), xanchor="center", yanchor="middle", align="center")
        ]

    # Calculate axis ranges based on actual data values first
    x_min = min(player['x'] for player in data)
    x_max = max(player['x'] for player in data)
    y_min = min(player['y'] for player in data)
    y_max = max(player['y'] for player in data)

    # Add some padding to the ranges
    x_padding = (x_max - x_min) * 0.1 if x_max > x_min else 1
    y_padding = (y_max - y_min) * 0.1 if y_max > y_min else 1

    x_range = [max(0, x_min - x_padding), x_max + x_padding]
    y_range = [max(0, y_min - y_padding), y_max + y_padding]

    # Calculate midpoints for quadrant lines
    x_mid = (x_range[0] + x_range[1]) / 2
    y_mid = (y_range[0] + y_range[1]) / 2

    # Add quadrant lines to divide the plot into four sections
    fig.add_shape(
        type="line",
        x0=x_range[0], y0=y_mid,
        x1=x_range[1], y1=y_mid,
        line=dict(color="#666666", width=1)
    )
    fig.add_shape(
        type="line",
        x0=x_mid, y0=y_range[0],
        x1=x_mid, y1=y_range[1],
        line=dict(color="#666666", width=1)
    )

    # Add quadrant descriptions (now that x_range and y_range are defined)
    fig.update_layout(annotations=get_outfield_quadrant_descriptions(x_stat, y_stat, position_type, x_range, y_range))

    # Add scatter points for each player
    for player in data:
        # Determine mode based on whether to show text
        mode = "markers+text" if player['show_text'] else "markers"

        fig.add_trace(
            go.Scatter(
                x=[player['x']],
                y=[player['y']],
                mode=mode,
                marker=dict(
                    color=player['color'],
                    size=player['marker_size'],
                    opacity=player['opacity'],
                    line=dict(width=player['line_width'], color="#222")
                ),
                text=player['name'] if player['show_text'] else "",
                textposition="bottom center",
                textfont=dict(
                    color="white",
                    size=15 if player['is_selected'] else 10,
                    family="Arial Black, Arial, sans-serif"
                ),
                hoverinfo="text",
                hovertext=player['text'],
                name=player['name'],
                showlegend=False
            )
        )

    # Format axis labels
    x_display = x_stat.replace('_', ' ').title()
    y_display = y_stat.replace('_', ' ').title()

    # Add title with per90 indication if enabled
    title_text = f"{position_type} Performance Classification"
    if per_90_mode:
        title_text += " (Per 90 Minutes)"

    # Configure the layout
    fig.update_layout(
        plot_bgcolor="#333333",
        paper_bgcolor="#333333",
        width=800,
        height=600,
        xaxis=dict(
            title=dict(text=x_display.upper() + (" (PER 90)" if per_90_mode and x_stat not in ["minutes", "matches"] else ""),
                     font=dict(color="#CCCCCC", size=18)),
            range=x_range,
            gridcolor="#444444",
            zerolinecolor="#444444",
            tickfont=dict(color="#CCCCCC"),
            showline=True,
            linecolor="#666666"
        ),
        yaxis=dict(
            title=dict(text=y_display.upper() + (" (PER 90)" if per_90_mode and y_stat not in ["minutes", "matches"] else ""),
                     font=dict(color="#CCCCCC", size=18)),
            range=y_range,
            gridcolor="#444444",
            zerolinecolor="#444444",
            tickfont=dict(color="#CCCCCC", size=16),
            showline=True,
            linecolor="#666666"
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=60),
        hoverlabel=dict(
            bgcolor="#444444",
            font_size=14,
            font_color="white"
        ),
        title=dict(
            text=title_text,
            font=dict(color="#FFFFFF", size=22),
            y=0.95
        ),
    )

    return fig





def render_outfield_player_search(rag, filtered_data, position_type):
    """
    Render the outfield player search interface.

    Args:
        rag: RAG system instance (OutfieldRAG, ForwardRAG, MidfielderRAG, or DefenderRAG)
        filtered_data: Dictionary of filtered player data
        position_type: Type of position being analyzed ("All Outfield", "Forward", "Midfielder", "Defender")
    """
    # Add CSS for better table styling - Force full width
    st.markdown("""
    <style>
    /* Force full width layout */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Make tables full width and remove centering */
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

    .stDataFrame table {
        width: 100% !important;
        margin: 0 !important;
        border-collapse: collapse !important;
        border-spacing: 0 !important;
        table-layout: auto !important;
    }

    /* Remove any container centering and force full width */
    .stDataFrame .dataframe {
        width: 100% !important;
        margin: 0 !important;
    }

    /* Force container to use full width */
    .element-container {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Ensure table headers are readable and full width */
    .stDataFrame th {
        background-color: #2c3e50 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        padding: 8px 6px !important;
        text-align: center !important;
        border: none !important;
        white-space: nowrap !important;
        font-size: 12px !important;
    }

    /* Style table cells */
    .stDataFrame td {
        padding: 6px 4px !important;
        text-align: center !important;
        border: none !important;
        background-color: #ffffff !important;
        white-space: nowrap !important;
        font-size: 12px !important;
    }

    /* Ensure progress columns are properly styled */
    .stDataFrame .stProgress {
        width: 100% !important;
        margin: 0 !important;
        min-width: 80px !important;
    }

    /* Force the entire app to use full width */
    .css-1d391kg, .css-1y4p8pa {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Remove sidebar constraints on main content */
    .css-1lcbmhc, .css-1outpf7 {
        max-width: 100% !important;
    }

    /* Ensure dataframe container uses full width */
    div[data-testid="stDataFrame"] {
        width: 100% !important;
    }

    div[data-testid="stDataFrame"] > div {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.header(f"{position_type} Player Search")

    if not filtered_data:
        st.warning("No player data available. Please check your data source.")
        return

    # Date filter section (first filter)
    st.subheader("📅 Date Filter")
    use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range", key="outfield_search_date_filter")

    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.date(2024, 8, 1),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="Start date for filtering matches",
                key="outfield_search_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.date(2025, 6, 30),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="End date for filtering matches",
                key="outfield_search_end_date"
            )

        # Apply date filter to player data
        if start_date and end_date:
            st.info(f"📊 Filtering data from {start_date} to {end_date}")
            original_player_count = len(filtered_data)
            filtered_data = apply_date_filter(filtered_data, start_date, end_date)

            # Show filtering results
            filtered_player_count = len(filtered_data)
            st.success(f"✅ Date filter applied: {filtered_player_count} players found (was {original_player_count})")

            # Debug information
            if st.checkbox("🔍 Show Date Filter Debug Info", value=False, key="outfield_search_debug"):
                render_debug_interface(filtered_data, original_player_count, filtered_player_count, start_date, end_date)

            if not filtered_data:
                st.warning("No players found with matches in the selected date range.")
                return

    # Display information about data filtering
    st.info("📊 **Data Note**: All statistics shown below are calculated from matches within your selected date range (if date filter is active). This includes role rankings, player statistics, and match history.")

    # Search and filter controls
    st.subheader("Search and Filter Players")

    # Search by name
    search_term = st.text_input("Search by player name:", placeholder="Enter player name...")

    # Filter by team
    all_teams = sorted(set(stats.get("team", "Unknown") for stats in filtered_data.values()))
    selected_teams = st.multiselect("Filter by team:", all_teams, default=all_teams)

    # Filter by position (for All Outfield)
    if position_type == "All Outfield":
        all_positions = sorted(set(stats.get("position", "Unknown") for stats in filtered_data.values()))
        selected_positions = st.multiselect("Filter by position:", all_positions, default=all_positions)
    else:
        selected_positions = None

    # Apply filters
    filtered_players = []
    for player_name, stats in filtered_data.items():
        # Name filter
        if search_term and search_term.lower() not in player_name.lower():
            continue

        # Team filter
        if stats.get("team", "Unknown") not in selected_teams:
            continue

        # Position filter (for All Outfield)
        if selected_positions and stats.get("position", "Unknown") not in selected_positions:
            continue

        filtered_players.append(player_name)

    # Role-based search section
    st.subheader("Search Players by Role")

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

    # Determine which role weights to use based on position
    if position_type == "Forwards":
        role_weights_dict = center_forward_role_weights
        role_type = "Center Forward"
    elif position_type == "Defenders":
        role_weights_dict = center_back_role_weights
        role_type = "Center Back"
    else:
        role_weights_dict = {}
        role_type = None

    if role_weights_dict:
        # Role selection and top 10 filter
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_role = st.selectbox(f"Select {role_type.lower()} role:", ["None"] + list(role_weights_dict.keys()))
        with col2:
            show_top_10_only = st.checkbox("Show Top 10 Only", value=True)

        if selected_role != "None":
            # Calculate role scores for all players using date-filtered data
            role_data = []
            role_weights = role_weights_dict[selected_role]

            # Get all values for normalization from date-filtered player statistics
            # Note: filtered_data already contains statistics recalculated from date-filtered matches
            all_values = {}
            for stat in role_weights.keys():
                all_values[stat] = [filtered_data[p].get(stat, 0) for p in filtered_players]

            for player in filtered_players:
                # Use date-filtered player statistics
                stats = filtered_data[player]

                # Calculate weighted score
                total_score = 0
                total_weight = 0
                stat_values = {}

                for stat, weight in role_weights.items():
                    # Get value from date-filtered statistics
                    value = stats.get(stat, 0)
                    stat_values[stat] = value

                    # Normalize the value (0-100 scale) using min/max from date-filtered data
                    max_val = max(all_values[stat]) if all_values[stat] else 1
                    min_val = min(all_values[stat]) if all_values[stat] else 0

                    if max_val > min_val:
                        normalized = (value - min_val) / (max_val - min_val) * 100
                    else:
                        normalized = 50  # Default if all values are the same

                    total_score += normalized * weight
                    total_weight += weight

                final_score = total_score / total_weight if total_weight > 0 else 0

                role_data.append({
                    "Rank": 0,  # Will be set after sorting
                    "Team": stats.get("team", "Unknown"),
                    "Player": player,
                    "Age": stats.get("age", "N/A"),
                    "Position": stats.get("position", "Unknown"),
                    "Minutes": stats.get("minutes", 0),
                    **{stat.replace("_", " ").title(): stat_values[stat] for stat in role_weights.keys()},
                    "Score": final_score
                })

            # Sort by score (highest first) and assign ranks
            role_data.sort(key=lambda x: x["Score"], reverse=True)
            for i, player_data_item in enumerate(role_data):
                player_data_item["Rank"] = i + 1

            # Display role ranking
            if role_data:
                # Apply top 10 filter if enabled
                display_data = role_data[:10] if show_top_10_only else role_data

                # Create DataFrame for display
                df_role = pd.DataFrame(display_data)

                # Add header
                st.markdown(f"### Role Ranking - {selected_role}")

                # Configure columns for the dataframe
                column_config = {}

                # Configure the Score column as a progress bar
                max_score = df_role["Score"].max()
                column_config["Score"] = st.column_config.ProgressColumn(
                    "Score",
                    help="Role performance score",
                    min_value=0,
                    max_value=max_score,
                    format="%.1f"
                )

                # Configure other columns for better display
                column_config["Rank"] = st.column_config.NumberColumn(
                    "Rank",
                    help="Player ranking",
                    format="%d"
                )

                column_config["Minutes"] = st.column_config.NumberColumn(
                    "Minutes",
                    help="Minutes played",
                    format="%d"
                )

                # Configure stat columns
                for stat in role_weights.keys():
                    stat_display = stat.replace("_", " ").title()
                    column_config[stat_display] = st.column_config.NumberColumn(
                        stat_display,
                        help=f"{stat_display} statistic",
                        format="%.1f"
                    )

                # Display the dataframe with progress column
                st.dataframe(
                    df_role,
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No players found for role analysis.")
    else:
        st.info(f"Role analysis for {position_type} will be implemented with position-specific roles.")

    # Display results using date-filtered player statistics
    st.subheader(f"Results: {len(filtered_players)} players found")
    if filtered_players:
        # Create a DataFrame for display using date-filtered statistics
        data = []
        for player in filtered_players:
            # Use date-filtered player statistics (already recalculated from filtered matches)
            stats = filtered_data[player]
            # Create row data based on position type
            row_data = {
                "Player": player,
                "Team": stats.get("team", "Unknown"),
                "Position": stats.get("position", "Unknown"),
                "Matches": stats.get("matches", 0),  # Matches from filtered date range
                "Minutes": stats.get("minutes", 0),  # Minutes from filtered date range
                "Goals": stats.get("goals", 0),      # Goals from filtered date range
                "Assists": stats.get("assists", 0),  # Assists from filtered date range
                "Pass Accuracy": f"{stats.get('pass_accuracy', 0):.1f}%"  # Calculated from filtered matches
            }

            # Add position-specific stats
            if position_type in ["Forwards", "All Outfield"]:
                # Use pre-calculated shot accuracy from data_processor.py
                shot_accuracy_val = stats.get('shot_accuracy', 0)
                row_data["Shot Accuracy"] = f"{shot_accuracy_val:.1f}%"

            if position_type in ["Midfielders", "All Outfield"]:
                row_data["Dribble Success"] = f"{stats.get('dribble_success_rate', 0):.1f}%"

            if position_type in ["Defenders", "All Outfield"]:
                row_data["Duels Won"] = stats.get("duels_won", 0)
                row_data["Interceptions"] = stats.get("interceptions", 0)

            data.append(row_data)

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        # Player details
        selected_player = st.selectbox("Select a player for detailed stats:", filtered_players)

        if selected_player:
            st.subheader(f"Detailed Stats: {selected_player}")

            # Use date-filtered player statistics
            stats = filtered_data[selected_player]

            # Display key metrics based on position (all calculated from date-filtered matches)
            if position_type == "Forwards":
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Goals", stats.get("goals", 0))
                col2.metric("Assists", stats.get("assists", 0))
                col3.metric("Shot Accuracy", f"{stats.get('shot_accuracy', 0):.1f}%")
                col4.metric("Matches Played", stats.get("matches", 0))

            elif position_type == "Midfielders":
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Assists", stats.get("assists", 0))
                col2.metric("Pass Accuracy", f"{stats.get('pass_accuracy', 0):.1f}%")
                col3.metric("Dribble Success", f"{stats.get('dribble_success_rate', 0):.1f}%")
                col4.metric("Matches Played", stats.get("matches", 0))

            elif position_type == "Defenders":
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Duels Won", stats.get("duels_won", 0))
                col2.metric("Interceptions", stats.get("interceptions", 0))
                col3.metric("Pass Accuracy", f"{stats.get('pass_accuracy', 0):.1f}%")
                col4.metric("Matches Played", stats.get("matches", 0))

            else:  # All Outfield
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Goals", stats.get("goals", 0))
                col2.metric("Assists", stats.get("assists", 0))
                col3.metric("Pass Accuracy", f"{stats.get('pass_accuracy', 0):.1f}%")
                col4.metric("Matches Played", stats.get("matches", 0))

            # Display match history (filtered by date range)
            st.subheader("Match History (Date Filtered)")
            if "match_data" in stats and stats["match_data"]:
                # Note: match_data contains only matches within the selected date range
                match_data = pd.DataFrame(stats["match_data"])

                # Select relevant columns for outfield players
                display_columns = [
                    "Match", "Competition", "Date", "Position", "Minutes played",
                    "Goals", "Assists", "Shots", "Shots on target", "Passes", "Passes accurate"
                ]

                # Add position-specific columns
                if position_type in ["Defenders", "All Outfield"]:
                    display_columns.extend(["Duels", "Duels won", "Interceptions", "Recoveries"])

                if position_type in ["Midfielders", "Forwards", "All Outfield"]:
                    display_columns.extend(["Dribbles", "Dribbles successful"])

                # Display only existing columns
                existing_columns = [col for col in display_columns if col in match_data.columns]
                if existing_columns:
                    st.dataframe(
                        match_data[existing_columns].sort_values("Date", ascending=False),
                        use_container_width=True
                    )
                else:
                    st.write("Match data columns not found.")
            else:
                st.write("No match data available.")
    else:
        st.write("No players found matching your criteria.")


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

            # Recalculate aggregate statistics
            total_matches = len(filtered_matches)
            total_minutes = sum(match.get("Minutes played", 0) for match in filtered_matches)

            # Update basic info
            filtered_player["matches"] = total_matches
            filtered_player["minutes"] = total_minutes

            # Recalculate outfield player statistics
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
