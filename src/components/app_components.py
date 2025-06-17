import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from typing import Any, Dict


def add_global_filters() -> Dict[str, Any]:
    """
    Add global filters to the sidebar for date range.

    Returns:
        Dictionary containing the filter settings
    """
    st.sidebar.markdown("## Global Filters")

    # Date range filter
    use_date_filter = st.sidebar.checkbox("Filter by date range", value=False)

    start_date = datetime.date(2024, 8, 1)
    end_date = datetime.date(2025, 6, 30)

    if use_date_filter:
        date_range = st.sidebar.date_input(
            "Date range",
            value=(start_date, end_date),
            min_value=datetime.date(2020, 1, 1),
            max_value=datetime.date(2030, 12, 31)
        )

        # Handle single date selection
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = date_range
            end_date = date_range

    st.sidebar.markdown("---")

    return {
        "use_date_filter": use_date_filter,
        "start_date": start_date,
        "end_date": end_date
    }

def filter_player_data(data_provider, filters: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Filter player data based on global filters.
    Works for both goalkeeper and outfield player data.

    Args:
        data_provider: The data provider object (RAG system)
        filters: Dictionary containing filter settings

    Returns:
        Filtered player data
    """
    if not data_provider.data_processor.player_data:
        data_provider.data_processor.process_data()

    filtered_data = {}

    for player_name, player_data in data_provider.data_processor.player_data.items():
        # Create a copy of the player data
        filtered_player = player_data.copy()

        # Filter match data
        filtered_matches = []
        for match in player_data["match_data"]:
            include_match = True

            # Apply date filter
            if filters["use_date_filter"] and "Date" in match:
                try:
                    match_date = datetime.datetime.strptime(match["Date"], "%Y-%m-%d").date()
                    if match_date < filters["start_date"] or match_date > filters["end_date"]:
                        include_match = False
                except (ValueError, TypeError):
                    # If date parsing fails, keep the match
                    pass

            if include_match:
                filtered_matches.append(match)

        # Only include player if they have matches after filtering
        if filtered_matches:
            # Update match data
            filtered_player["match_data"] = filtered_matches

            # Recalculate aggregate statistics based on player type
            total_matches = len(filtered_matches)
            total_minutes = sum(match.get("Minutes played", 0) for match in filtered_matches)

            # Check if this is goalkeeper or outfield player data
            if "saves" in player_data:  # Goalkeeper data
                total_conceded = sum(match.get("Conceded goals", 0) for match in filtered_matches)
                total_saves = sum(match.get("Saves", 0) for match in filtered_matches)
                total_shots_against = sum(match.get("Shots against", 0) for match in filtered_matches)

                # Calculate derived metrics
                save_percentage = (total_saves / total_shots_against * 100) if total_shots_against > 0 else 0
                goals_conceded_per_90 = (total_conceded / total_minutes * 90) if total_minutes > 0 else 0

                # Update player statistics
                filtered_player["matches"] = total_matches
                filtered_player["minutes"] = total_minutes
                filtered_player["conceded_goals"] = total_conceded
                filtered_player["saves"] = total_saves
                filtered_player["shots_against"] = total_shots_against
                filtered_player["save_percentage"] = save_percentage
                filtered_player["goals_conceded_per_90"] = goals_conceded_per_90

            else:  # Outfield player data
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

                # Calculate success rates (following data_processor.py pattern)
                total_actions_success_rate = (total_actions_successful / total_actions * 100) if total_actions > 0 else 0
                pass_accuracy = (total_passes_accurate / total_passes * 100) if total_passes > 0 else 0
                long_pass_accuracy = (total_long_passes_accurate / total_long_passes * 100) if total_long_passes > 0 else 0
                cross_accuracy = (total_crosses_accurate / total_crosses * 100) if total_crosses > 0 else 0
                dribble_success_rate = (total_dribbles_successful / total_dribbles * 100) if total_dribbles > 0 else 0
                duel_success_rate = (total_duels_won / total_duels * 100) if total_duels > 0 else 0
                aerial_duel_success_rate = (total_aerial_duels_won / total_aerial_duels * 100) if total_aerial_duels > 0 else 0
                shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0

                # Calculate per 90 minutes statistics (following data_processor.py pattern)
                def per_90(value):
                    return (value / total_minutes * 90) if total_minutes > 0 else 0

                goals_per_90 = per_90(total_goals)
                assists_per_90 = per_90(total_assists)
                shots_per_90 = per_90(total_shots)
                shots_on_target_per_90 = per_90(total_shots_on_target)
                xg_per_90 = per_90(total_xg)
                passes_per_90 = per_90(total_passes)
                passes_accurate_per_90 = per_90(total_passes_accurate)
                long_passes_per_90 = per_90(total_long_passes)
                long_passes_accurate_per_90 = per_90(total_long_passes_accurate)
                crosses_per_90 = per_90(total_crosses)
                crosses_accurate_per_90 = per_90(total_crosses_accurate)
                dribbles_per_90 = per_90(total_dribbles)
                dribbles_successful_per_90 = per_90(total_dribbles_successful)
                duels_per_90 = per_90(total_duels)
                duels_won_per_90 = per_90(total_duels_won)
                aerial_duels_per_90 = per_90(total_aerial_duels)
                aerial_duels_won_per_90 = per_90(total_aerial_duels_won)
                interceptions_per_90 = per_90(total_interceptions)
                losses_per_90 = per_90(total_losses)
                losses_own_half_per_90 = per_90(total_losses_own_half)
                recoveries_per_90 = per_90(total_recoveries)
                recoveries_opp_half_per_90 = per_90(total_recoveries_opp_half)
                total_actions_per_90 = per_90(total_actions)
                total_actions_successful_per_90 = per_90(total_actions_successful)

                # Update player statistics - Basic info
                filtered_player["matches"] = total_matches
                filtered_player["minutes"] = total_minutes

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

                # Per 90 minutes stats
                filtered_player["goals_per_90"] = goals_per_90
                filtered_player["assists_per_90"] = assists_per_90
                filtered_player["shots_per_90"] = shots_per_90
                filtered_player["shots_on_target_per_90"] = shots_on_target_per_90
                filtered_player["xg_per_90"] = xg_per_90
                filtered_player["passes_per_90"] = passes_per_90
                filtered_player["passes_accurate_per_90"] = passes_accurate_per_90
                filtered_player["long_passes_per_90"] = long_passes_per_90
                filtered_player["long_passes_accurate_per_90"] = long_passes_accurate_per_90
                filtered_player["crosses_per_90"] = crosses_per_90
                filtered_player["crosses_accurate_per_90"] = crosses_accurate_per_90
                filtered_player["dribbles_per_90"] = dribbles_per_90
                filtered_player["dribbles_successful_per_90"] = dribbles_successful_per_90
                filtered_player["duels_per_90"] = duels_per_90
                filtered_player["duels_won_per_90"] = duels_won_per_90
                filtered_player["aerial_duels_per_90"] = aerial_duels_per_90
                filtered_player["aerial_duels_won_per_90"] = aerial_duels_won_per_90
                filtered_player["interceptions_per_90"] = interceptions_per_90
                filtered_player["losses_per_90"] = losses_per_90
                filtered_player["losses_own_half_per_90"] = losses_own_half_per_90
                filtered_player["recoveries_per_90"] = recoveries_per_90
                filtered_player["recoveries_opp_half_per_90"] = recoveries_opp_half_per_90
                filtered_player["total_actions_per_90"] = total_actions_per_90
                filtered_player["total_actions_successful_per_90"] = total_actions_successful_per_90

            filtered_data[player_name] = filtered_player

    return filtered_data

def render_player_search(data_provider, filtered_data=None):
    """
    Render the Player Search page.

    Args:
        data_provider: An object that provides access to player data
                      (either GoalkeeperRAG or SimpleGoalkeeperSearch)
        filtered_data: Optional pre-filtered player data
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

    st.header("Player Search")

    # Get all player data
    if filtered_data is None:
        if not data_provider.data_processor.player_data:
            data_provider.data_processor.process_data()
        player_data = data_provider.data_processor.player_data
    else:
        player_data = filtered_data

    players = list(player_data.keys())
    players.sort()

    if not players:
        st.warning("No players found with the current filters. Try adjusting the global filters in the sidebar.")
        return

    # Search filters
    col1, col2 = st.columns(2)

    with col1:
        search_name = st.text_input("Search by name:")

    with col2:
        team_filter = st.selectbox(
            "Filter by team:",
            ["All Teams"] + sorted(list({player_data[p]["team"] for p in players}))
        )

    # Filter players
    filtered_players = []
    for player in players:
        if search_name.lower() in player.lower() and (team_filter == "All Teams" or player_data[player]["team"] == team_filter):
            filtered_players.append(player)

    # Role-based search section
    st.subheader("Search Players by Role")

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

    # Role selection and top 10 filter
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_role = st.selectbox("Select goalkeeper role:", ["None"] + list(goalkeeper_role_weights.keys()))
    with col2:
        show_top_10_only = st.checkbox("Show Top 10 Only", value=True)

    if selected_role != "None":
        # Calculate role scores for all players
        role_data = []
        role_weights = goalkeeper_role_weights[selected_role]

        # Get all values for normalization
        all_values = {}
        for stat in role_weights.keys():
            all_values[stat] = [player_data[p].get(stat, 0) for p in filtered_players]

        for player in filtered_players:
            stats = player_data[player]

            # Calculate weighted score
            total_score = 0
            total_weight = 0
            stat_values = {}

            for stat, weight in role_weights.items():
                value = stats.get(stat, 0)
                stat_values[stat] = value

                # Normalize the value (0-100 scale)
                max_val = max(all_values[stat]) if all_values[stat] else 1
                min_val = min(all_values[stat]) if all_values[stat] else 0

                if max_val > min_val:
                    if weight < 0:  # Negative stats (lower is better)
                        normalized = 100 - ((value - min_val) / (max_val - min_val) * 100)
                        weight = abs(weight)  # Use absolute weight for calculation
                    else:
                        normalized = (value - min_val) / (max_val - min_val) * 100
                else:
                    normalized = 50  # Default if all values are the same

                total_score += normalized * weight
                total_weight += weight

            final_score = total_score / total_weight if total_weight > 0 else 0

            role_data.append({
                "Rank": 0,  # Will be set after sorting
                "Team": stats["team"],
                "Player": player,
                "Age": stats.get("age", "N/A"),
                "Position": "GK",
                "Minutes": stats["minutes"],
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

            # Display the dataframe with progress column and enhanced styling
            st.dataframe(
                df_role,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                height=min(600, len(df_role) * 35 + 50)  # Dynamic height based on rows
            )
        else:
            st.warning("No players found for role analysis.")

    # Display results
    st.subheader(f"Results: {len(filtered_players)} players found")

    if filtered_players:
        # Create a DataFrame for display with enhanced goalkeeper statistics
        data = []
        for player in filtered_players:
            stats = player_data[player]

            # Build the data row with comprehensive goalkeeper statistics
            row = {
                "Player": player,
                "Team": stats["team"],
                "Matches": stats["matches"],
                "Minutes": stats["minutes"],
                "Goals Conceded": stats["conceded_goals"],
                "Goals Conceded/90": f"{stats['goals_conceded_per_90']:.2f}",
                "Saves": stats["saves"],
                "Save %": f"{stats['save_percentage']:.1f}%",
                "Shots Against": stats.get("shots_against", 0),
                "Shots Against/90": f"{stats.get('shots_against_per_90', 0):.1f}",
            }

            # Add league-specific statistics if available
            if 'xg_against' in stats and stats['xg_against'] > 0:
                row["xG Against"] = f"{stats['xg_against']:.1f}"
                row["xG Against/90"] = f"{stats.get('xg_against_per_90', 0):.2f}"

            if 'prevented_goals' in stats:
                row["Prevented Goals"] = f"{stats['prevented_goals']:.1f}"
                row["Prevented Goals/90"] = f"{stats.get('prevented_goals_per_90', 0):.3f}"

            if 'clean_sheets' in stats:
                row["Clean Sheets"] = stats['clean_sheets']
                row["Clean Sheet %"] = f"{stats.get('clean_sheet_percentage', 0):.1f}%"

            if 'save_rate_percent' in stats and stats['save_rate_percent'] != stats.get('save_percentage', 0):
                row["Save Rate (League)"] = f"{stats['save_rate_percent']:.1f}%"

            if 'age' in stats and stats['age'] > 0:
                row["Age"] = stats['age']

            data.append(row)

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=min(600, len(df) * 35 + 50))

        # Player details
        selected_player = st.selectbox("Select a player for detailed stats:", filtered_players)

        if selected_player:
            st.subheader(f"Detailed Stats: {selected_player}")

            stats = player_data[selected_player]

            # Display key metrics in multiple rows for comprehensive view
            st.subheader("Key Performance Metrics")

            # First row - Core goalkeeping stats
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Save Percentage", f"{stats['save_percentage']:.1f}%")
            col2.metric("Goals Conceded/90", f"{stats['goals_conceded_per_90']:.2f}")
            col3.metric("Total Saves", stats['saves'])
            col4.metric("Matches Played", stats['matches'])

            # Second row - League statistics (if available)
            if any(key in stats for key in ['xg_against', 'prevented_goals', 'clean_sheets', 'age']):
                st.subheader("League Statistics")
                col1, col2, col3, col4 = st.columns(4)

                if 'xg_against' in stats and stats['xg_against'] > 0:
                    col1.metric("xG Against", f"{stats['xg_against']:.1f}")
                    col2.metric("xG Against/90", f"{stats.get('xg_against_per_90', 0):.2f}")
                else:
                    col1.metric("xG Against", "N/A")
                    col2.metric("xG Against/90", "N/A")

                if 'prevented_goals' in stats:
                    col3.metric("Prevented Goals", f"{stats['prevented_goals']:.2f}")
                    col4.metric("Prevented Goals/90", f"{stats.get('prevented_goals_per_90', 0):.3f}")
                else:
                    col3.metric("Prevented Goals", "N/A")
                    col4.metric("Prevented Goals/90", "N/A")

            # Third row - Additional league stats
            if any(key in stats for key in ['clean_sheets', 'save_rate_percent', 'aerial_duels_per_90', 'age']):
                col1, col2, col3, col4 = st.columns(4)

                if 'clean_sheets' in stats:
                    col1.metric("Clean Sheets", stats['clean_sheets'])
                    col2.metric("Clean Sheet %", f"{stats.get('clean_sheet_percentage', 0):.1f}%")
                else:
                    col1.metric("Clean Sheets", "N/A")
                    col2.metric("Clean Sheet %", "N/A")

                if 'save_rate_percent' in stats:
                    col3.metric("Save Rate (League)", f"{stats['save_rate_percent']:.1f}%")
                else:
                    col3.metric("Save Rate (League)", "N/A")

                if 'age' in stats and stats['age'] > 0:
                    col4.metric("Age", f"{stats['age']} years")
                else:
                    col4.metric("Age", "N/A")

            # Fourth row - Additional performance metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Shots Against", stats.get('shots_against', 0))
            col2.metric("Shots Against/90", f"{stats.get('shots_against_per_90', 0):.1f}")

            if 'aerial_duels_per_90' in stats and stats['aerial_duels_per_90'] > 0:
                col3.metric("Aerial Duels/90", f"{stats['aerial_duels_per_90']:.1f}")
            else:
                col3.metric("Aerial Duels/90", "N/A")

            if 'exits_per_90' in stats:
                col4.metric("Exits/90", f"{stats['exits_per_90']:.1f}")
            else:
                col4.metric("Exits/90", "N/A")

            # Display match history
            st.subheader("Match History")
            match_data = pd.DataFrame(stats["match_data"])

            # Select relevant columns with enhanced goalkeeper statistics
            display_columns = [
                "Match", "Competition", "Date", "Minutes played",
                "Conceded goals", "xCG", "Shots against", "Saves", "Saves with reflexes",
                "Exits", "Long passes", "Long passes accurate", "Short passes", "Short passes accurate",
                "Goal kicks", "Short goal kicks", "Long goal kicks"
            ]

            # Display only if these columns exist
            existing_columns = [col for col in display_columns if col in match_data.columns]
            if existing_columns:
                # Sort by date (most recent first) and display
                sorted_match_data = match_data[existing_columns].sort_values("Date", ascending=False)

                # Add calculated columns for better analysis
                if "Saves" in sorted_match_data.columns and "Shots against" in sorted_match_data.columns:
                    sorted_match_data["Save %"] = (sorted_match_data["Saves"] / sorted_match_data["Shots against"] * 100).round(1)
                    sorted_match_data["Save %"] = sorted_match_data["Save %"].fillna(0)

                if "Long passes accurate" in sorted_match_data.columns and "Long passes" in sorted_match_data.columns:
                    sorted_match_data["Long Pass %"] = (sorted_match_data["Long passes accurate"] / sorted_match_data["Long passes"] * 100).round(1)
                    sorted_match_data["Long Pass %"] = sorted_match_data["Long Pass %"].fillna(0)

                if "Short passes accurate" in sorted_match_data.columns and "Short passes" in sorted_match_data.columns:
                    sorted_match_data["Short Pass %"] = (sorted_match_data["Short passes accurate"] / sorted_match_data["Short passes"] * 100).round(1)
                    sorted_match_data["Short Pass %"] = sorted_match_data["Short Pass %"].fillna(0)

                st.dataframe(sorted_match_data, use_container_width=True)

                # Add summary statistics for the match history
                if len(sorted_match_data) > 1:
                    st.subheader("Match History Summary")
                    col1, col2, col3, col4 = st.columns(4)

                    avg_save_pct = sorted_match_data["Save %"].mean() if "Save %" in sorted_match_data.columns else 0
                    avg_conceded_per_90 = (sorted_match_data["Conceded goals"].sum() / sorted_match_data["Minutes played"].sum() * 90) if sorted_match_data["Minutes played"].sum() > 0 else 0
                    total_clean_sheets = len(sorted_match_data[sorted_match_data["Conceded goals"] == 0])
                    clean_sheet_pct = (total_clean_sheets / len(sorted_match_data) * 100) if len(sorted_match_data) > 0 else 0

                    col1.metric("Avg Save %", f"{avg_save_pct:.1f}%")
                    col2.metric("Avg Conceded/90", f"{avg_conceded_per_90:.2f}")
                    col3.metric("Clean Sheets", f"{total_clean_sheets}/{len(sorted_match_data)}")
                    col4.metric("Clean Sheet %", f"{clean_sheet_pct:.1f}%")
            else:
                st.write("Match data columns not found.")
    else:
        st.write("No players found matching your criteria.")

# Function to get color based on percentile
def get_percentile_color(percentile_rank):
    """
    Get color based on percentile rank using a color gradient.

    Args:
        percentile_rank (float): Percentile rank (0-100)

    Returns:
        str: Hex color code
    """
    # Ensure percentile is at least 1 for color coding
    percentile_rank = max(percentile_rank, 1)

    # Round the percentile to the nearest integer to avoid floating point issues
    percentile_rank = round(percentile_rank)

    # Color ranges - use exact boundaries to match the legend
    if percentile_rank >= 81:  # 81-100% range
        return '#1a9641'  # Dark green (81-100%)
    elif percentile_rank >= 61:  # 61-80% range
        return '#73c378'  # Medium green (61-80%)
    elif percentile_rank >= 41:  # 41-60% range
        return '#f9d057'  # Yellow (41-60%)
    elif percentile_rank >= 21:  # 21-40% range
        return '#fc8d59'  # Light orange (21-40%)
    else:  # 0-20% range
        return '#d73027'  # Red (0-20%)

# Function to generate bar chart for goalkeeper comparison using Plotly
def generate_goalkeeper_comparison_chart(player_name, player_stats, player_info, metrics_by_category, all_player_stats):
    """
    Generate an interactive bar chart visualization for goalkeeper comparison using Plotly.

    Args:
        player_name (str): Name of the player
        player_stats (dict): Dictionary containing player statistics
        player_info (dict): Dictionary containing player information
        metrics_by_category (dict): Dictionary of metrics organized by category
        all_player_stats (list): List of stats for all players being compared

    Returns:
        plotly.graph_objects.Figure: The generated interactive chart figure
    """
    # Category colors are defined by the bar colors based on percentile values

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

            # List of negative stats where lower values are better
            negative_stats = ["Goals Conceded", "Goals Conceded/90", "Conceded goals", "xCG"]

            # Calculate percentile based on comparison with other players (for color only)
            if all_values:
                # Handle stats with all zero values
                if sum(all_values) == 0:
                    percentile = 50  # Default to middle percentile
                else:
                    # For regular stats, calculate percentile using scipy's percentileofscore
                    if metric_info.get('invert', False) or metric_name in negative_stats:
                        # For negative stats, lower values are better
                        # percentileofscore returns the percentage of values at or below the given value
                        # So we invert it (100 - score) to get the correct ranking where lower is better
                        raw_percentile = stats.percentileofscore(all_values, actual_value)
                        percentile = 100 - raw_percentile
                    else:
                        # For positive stats, higher values are better
                        # percentileofscore returns the percentage of values at or below the given value
                        percentile = stats.percentileofscore(all_values, actual_value)

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
                if metric_info.get('invert', False) or metric_name in negative_stats:
                    percentile = max(0, min(100, 100 - (actual_value / metric_info.get('max_value', 1) * 100)))
                else:
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
                        'conceded_goals': 3.0,  # Max ~3 goals conceded per 90
                        'saves': 8.0,           # Max ~8 saves per 90
                        'shots_against': 10.0,  # Max ~10 shots against per 90
                        'xcg': 3.0,             # Max ~3 xCG per 90
                        'exits': 2.0,           # Max ~2 exits per 90
                        'saves_with_reflexes': 3.0,  # Max ~3 reflex saves per 90
                        'goal_kicks': 15.0,     # Max ~15 goal kicks per 90
                        'short_goal_kicks': 8.0, # Max ~8 short goal kicks per 90
                        'long_goal_kicks': 8.0,  # Max ~8 long goal kicks per 90
                        'short_passes': 25.0,   # Max ~25 short passes per 90
                        'short_passes_accurate': 22.0, # Max ~22 accurate short passes per 90
                        'long_passes': 20.0,    # Max ~20 long passes per 90
                        'long_passes_accurate': 12.0   # Max ~12 accurate long passes per 90
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
    df['CategoryOrder'] = df['Category'].map({'General': 0, 'Goalkeeping': 1, 'Distribution': 2})

    # Create a dictionary to store the original order of metrics in each category
    metric_order = {
        'General': ['Minutes played'],
        'Goalkeeping': ['Conceded goals', 'xCG', 'Shots against', 'Saves', 'Saves with reflexes', 'Exits'],
        'Distribution': ['Goal kicks', 'Short goal kicks', 'Long goal kicks', 'Short passes', 'Short passes accurate', 'Long passes', 'Long passes accurate']
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
    for category in ['General', 'Goalkeeping', 'Distribution']:
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

    # Remove percentile bands since we're now showing actual values
    # The grid lines will be handled by the x-axis grid

    # Add category dividers and labels
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

    # Add category annotations
    for category in ['General', 'Goalkeeping', 'Distribution']:
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
    age = player_info.get('age', 'Unknown')
    position = "GK"
    club = player_info.get('team', 'Unknown')
    total_matches = player_stats.get('matches', 0)
    total_minutes = player_stats.get('minutes', 0)
    total_conceded = player_stats.get('conceded_goals', 0)

    competitions = player_info.get('competitions', 'All competitions')
    per_90_mode = player_info.get('per_90_mode', False)
    stats_mode = " (Per 90 min)" if per_90_mode else ""

    player_info_text = f"<b>{player_name}</b>{stats_mode}<br>{age} | {position} | {club}<br>Competitions: {competitions}<br>Matches: {total_matches} | Minutes: {total_minutes} | Goals Conceded: {total_conceded}"

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

def render_player_comparison(data_provider, filtered_data=None):
    """
    Render the Player Comparison page.

    Args:
        data_provider: An object that provides access to player data
                      (either GoalkeeperRAG or SimpleGoalkeeperSearch)
        filtered_data: Optional pre-filtered player data
    """
    st.header("Player Comparison")

    # Get all player data
    if filtered_data is None:
        if not data_provider.data_processor.player_data:
            data_provider.data_processor.process_data()
        player_data = data_provider.data_processor.player_data
    else:
        player_data = filtered_data

    players = sorted(list(player_data.keys()))

    if len(players) < 2:
        st.warning("Not enough players found with the current filters. Try adjusting the global filters in the sidebar.")
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
        per_90_mode = st.toggle("Per 90 Minutes Stats", value=False, help="Calculate all statistics per 90 minutes of play instead of per match")

    # Number of players to compare (2 or 3)
    if from_find_similar and 'comparison_players' in st.session_state:
        # Pre-set based on Find Similar Player selection
        preselected_players = st.session_state['comparison_players']
        num_players = st.radio("Number of players to compare:", [2, 3],
                              index=0 if len(preselected_players) == 2 else 1,
                              horizontal=True)
    else:
        num_players = st.radio("Number of players to compare:", [2, 3], horizontal=True)

    # Select players
    selected_players = []

    if selection_mode:
        # Multiselect mode
        max_selections = 3 if num_players == 3 else 2

        # Pre-populate if coming from Find Similar Player
        default_selection = []
        if from_find_similar and 'comparison_players' in st.session_state:
            preselected = st.session_state['comparison_players']
            # Filter to only include players that exist in current filtered data
            default_selection = [p for p in preselected if p in players][:max_selections]

        selected_players = st.multiselect("Select players", players,
                                        default=default_selection,
                                        max_selections=max_selections)

        # Ensure we have the right number of players
        if len(selected_players) > num_players:
            selected_players = selected_players[:num_players]
    else:
        # Individual selection mode
        remaining_players = players.copy()

        # Pre-populate if coming from Find Similar Player
        preselected = []
        if from_find_similar and 'comparison_players' in st.session_state:
            preselected = [p for p in st.session_state['comparison_players'] if p in players]

        # First player
        default_idx_1 = 0
        if preselected and len(preselected) > 0 and preselected[0] in remaining_players:
            default_idx_1 = remaining_players.index(preselected[0])

        player1 = st.selectbox("Select first player:", remaining_players, index=default_idx_1, key="player1")
        selected_players.append(player1)
        remaining_players = [p for p in remaining_players if p != player1]

        # Second player
        default_idx_2 = 0
        if preselected and len(preselected) > 1 and preselected[1] in remaining_players:
            default_idx_2 = remaining_players.index(preselected[1])

        player2 = st.selectbox("Select second player:", remaining_players, index=default_idx_2, key="player2")
        selected_players.append(player2)
        remaining_players = [p for p in remaining_players if p != player2]

        # Third player (if selected)
        if num_players == 3:
            default_idx_3 = 0
            if preselected and len(preselected) > 2 and preselected[2] in remaining_players:
                default_idx_3 = remaining_players.index(preselected[2])

            player3 = st.selectbox("Select third player:", remaining_players, index=default_idx_3, key="player3")
            selected_players.append(player3)

    # Clear the session state after using it
    if from_find_similar and 'comparison_players' in st.session_state:
        # Keep it for one more page load, then clear
        if st.session_state.get('comparison_used', False):
            del st.session_state['comparison_players']
            if 'comparison_used' in st.session_state:
                del st.session_state['comparison_used']
        else:
            st.session_state['comparison_used'] = True

    # Competition selection for each player
    st.subheader("Select Competitions (Optional)")
    st.info("Select specific competitions to filter player data. Leave empty to include all competitions.")

    # Competition selection for each selected player
    player_competitions = {}
    if selected_players:
        cols = st.columns(len(selected_players))
        for i, (col, player) in enumerate(zip(cols, selected_players)):
            with col:
                st.write(f"**{player}**")

                # Get competitions only for this specific player
                player_stats = player_data.get(player, {})
                player_competition_dates = {}
                player_competitions_set = set()

                # Extract competitions from this player's match data with their dates
                for match in player_stats.get("match_data", []):
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

    # Get player stats with competition filtering
    player_stats = []
    for player in selected_players:
        raw_data = player_data.get(player)
        if raw_data:
            selected_comps = player_competitions.get(player, [])

            # Filter match data by selected competitions
            filtered_matches = []
            for match in raw_data.get("match_data", []):
                if match.get("Competition") in selected_comps or not selected_comps:
                    filtered_matches.append(match)

            if not filtered_matches:
                st.warning(f"No matches found for {player} in selected competitions.")
                continue

            # Recalculate statistics from filtered matches
            filtered_stats = {
                'name': player,
                'team': raw_data['team'],
                'position': raw_data.get('position', 'GK'),
                'matches': len(filtered_matches),
                'selected_competitions': selected_comps
            }

            # Helper function to safely sum columns from filtered matches
            def safe_sum_filtered(column_name):
                return sum(match.get(column_name, 0) for match in filtered_matches if match.get(column_name) is not None)

            # Calculate aggregate statistics from filtered matches
            filtered_stats['minutes'] = safe_sum_filtered('Minutes played')
            filtered_stats['conceded_goals'] = safe_sum_filtered('Conceded goals')
            filtered_stats['xcg'] = safe_sum_filtered('xCG')
            filtered_stats['shots_against'] = safe_sum_filtered('Shots against')
            filtered_stats['saves'] = safe_sum_filtered('Saves')
            filtered_stats['saves_with_reflexes'] = safe_sum_filtered('Saves with reflexes')
            filtered_stats['exits'] = safe_sum_filtered('Exits')
            filtered_stats['long_passes'] = safe_sum_filtered('Long passes')
            filtered_stats['long_passes_accurate'] = safe_sum_filtered('Long passes accurate')
            filtered_stats['short_passes'] = safe_sum_filtered('Short passes')
            filtered_stats['short_passes_accurate'] = safe_sum_filtered('Short passes accurate')
            filtered_stats['goal_kicks'] = safe_sum_filtered('Goal kicks')
            filtered_stats['short_goal_kicks'] = safe_sum_filtered('Short goal kicks')
            filtered_stats['long_goal_kicks'] = safe_sum_filtered('Long goal kicks')

            # Calculate derived metrics
            if filtered_stats['shots_against'] > 0:
                filtered_stats['save_percentage'] = (filtered_stats['saves'] / filtered_stats['shots_against'] * 100)
            else:
                filtered_stats['save_percentage'] = 0

            if filtered_stats['minutes'] > 0:
                filtered_stats['goals_conceded_per_90'] = (filtered_stats['conceded_goals'] / filtered_stats['minutes'] * 90)
                filtered_stats['xcg_per_90'] = (filtered_stats['xcg'] / filtered_stats['minutes'] * 90)
            else:
                filtered_stats['goals_conceded_per_90'] = 0
                filtered_stats['xcg_per_90'] = 0

            # Calculate accuracy percentages
            if filtered_stats['long_passes'] > 0:
                filtered_stats['long_pass_accuracy'] = (filtered_stats['long_passes_accurate'] / filtered_stats['long_passes'] * 100)
            else:
                filtered_stats['long_pass_accuracy'] = 0

            if filtered_stats['short_passes'] > 0:
                filtered_stats['short_pass_accuracy'] = (filtered_stats['short_passes_accurate'] / filtered_stats['short_passes'] * 100)
            else:
                filtered_stats['short_pass_accuracy'] = 0

            # Add league statistics if available (from original data)
            for league_stat in ['xg_against', 'xg_against_per_90', 'prevented_goals', 'prevented_goals_per_90',
                              'clean_sheets', 'save_rate_percent', 'aerial_duels_per_90', 'age']:
                if league_stat in raw_data:
                    filtered_stats[league_stat] = raw_data[league_stat]

            # Store filtered match data for reference
            filtered_stats['match_data'] = filtered_matches

            player_stats.append(filtered_stats)
        else:
            st.error(f"Player {player} not found")
            return

    # We don't need the comparison data anymore since we removed the radar chart

    # Display comparison title
    if len(selected_players) == 0:
        st.warning("Please select at least one player to compare.")
        return
    elif not player_stats:
        st.warning("No valid player data found for the selected competitions.")
        return
    elif len(player_stats) == 1:
        st.subheader(f"Player Analysis: {player_stats[0]['name']}")
    elif len(player_stats) == 2:
        st.subheader(f"Comparison: {player_stats[0]['name']} vs {player_stats[1]['name']}")
    else:
        player_names = [stats['name'] for stats in player_stats]
        st.subheader(f"Comparison: {' vs '.join(player_names)}")

    # Display selected competitions info
    if player_competitions:
        with st.expander("Selected Competitions", expanded=False):
            for stats in player_stats:
                player = stats['name']
                if player in player_competitions:
                    comps = player_competitions[player]
                    st.write(f"**{player}**: {', '.join(comps) if comps else 'All competitions'}")

    # Define metrics for goalkeeper comparison by category
    gk_metrics_by_category = {
        "General": {
            "Minutes played": {"key": "minutes", "max_value": 90*38}
        },
        "Goalkeeping": {
            "Conceded goals": {"key": "conceded_goals", "max_value": 50, "invert": True},
            "xCG": {"key": "xcg", "max_value": 40, "calculated": True, "invert": True},
            "Shots against": {"key": "shots_against", "max_value": 200},
            "Saves": {"key": "saves", "max_value": 150},
            "Saves with reflexes": {"key": "saves_with_reflexes", "max_value": 5, "calculated": True},
            "Exits": {"key": "exits", "max_value": 5, "calculated": True}
        },
        "Distribution": {
            "Goal kicks": {"key": "goal_kicks", "max_value": 10, "calculated": True},
            "Short goal kicks": {"key": "short_goal_kicks", "max_value": 10, "calculated": True},
            "Long goal kicks": {"key": "long_goal_kicks", "max_value": 10, "calculated": True},
            "Short passes": {"key": "short_passes", "max_value": 10, "calculated": True},
            "Short passes accurate": {"key": "short_passes_accurate", "max_value": 10, "calculated": True},
            "Long passes": {"key": "long_passes", "max_value": 10, "calculated": True},
            "Long passes accurate": {"key": "long_passes_accurate", "max_value": 10, "calculated": True}
        }
    }

    # Function to convert stats to per 90 minutes
    def convert_to_per_90(stats, per_90_enabled=False):
        if not per_90_enabled:
            return stats

        converted_stats = stats.copy()
        minutes = stats.get("minutes", 0)

        if minutes == 0:
            return converted_stats

        # Stats that should be converted to per 90 minutes
        per_90_stats = [
            "conceded_goals", "saves", "shots_against", "xcg",
            "saves_with_reflexes", "exits", "goal_kicks",
            "short_goal_kicks", "long_goal_kicks", "short_passes",
            "short_passes_accurate", "long_passes", "long_passes_accurate"
        ]

        # Convert each stat to per 90 minutes
        for stat in per_90_stats:
            if stat in converted_stats:
                converted_stats[stat] = (converted_stats[stat] * 90) / minutes

        # Recalculate derived stats that depend on per 90 values
        if per_90_enabled:
            # Save percentage remains the same as it's already a ratio
            # Goals conceded per 90 is now just the conceded_goals value
            converted_stats["goals_conceded_per_90"] = converted_stats.get("conceded_goals", 0)

        return converted_stats

    # Calculate additional metrics for each player (only for missing data)
    for i, stats in enumerate(player_stats):
        # Calculate derived metrics based on available data
        matches = stats["matches"]
        saves = stats["saves"]

        # Only calculate approximate values for missing metrics (use actual data when available)
        if stats.get("long_goal_kicks", 0) == 0:
            player_stats[i]["long_goal_kicks"] = int(matches * 3.5)  # Approx 3.5 long goal kicks per match
        if stats.get("short_goal_kicks", 0) == 0:
            player_stats[i]["short_goal_kicks"] = int(matches * 2.5)  # Approx 2.5 short goal kicks per match
        if stats.get("goal_kicks", 0) == 0:
            player_stats[i]["goal_kicks"] = player_stats[i]["long_goal_kicks"] + player_stats[i]["short_goal_kicks"]

        if stats.get("long_passes", 0) == 0:
            player_stats[i]["long_passes"] = int(matches * 15)  # Approx 15 long passes per match
        if stats.get("long_passes_accurate", 0) == 0:
            player_stats[i]["long_passes_accurate"] = int(player_stats[i]["long_passes"] * 0.6)  # 60% accuracy

        if stats.get("short_passes", 0) == 0:
            player_stats[i]["short_passes"] = int(matches * 20)  # Approx 20 short passes per match
        if stats.get("short_passes_accurate", 0) == 0:
            player_stats[i]["short_passes_accurate"] = int(player_stats[i]["short_passes"] * 0.85)  # 85% accuracy

        if stats.get("exits", 0) == 0:
            player_stats[i]["exits"] = int(matches * 1.2)  # Approx 1.2 exits per match
        if stats.get("saves_with_reflexes", 0) == 0:
            player_stats[i]["saves_with_reflexes"] = int(saves * 0.3)  # 30% of saves are with reflexes

        if stats.get("xcg", 0) == 0:
            player_stats[i]["xcg"] = stats["conceded_goals"] * 0.9  # xCG slightly lower than actual goals

        # Add missing general stats
        player_stats[i]["total_actions"] = int(saves * 2.5)  # Approx 2.5x saves as total actions
        player_stats[i]["total_actions_successful"] = int(player_stats[i]["total_actions"] * 0.8)  # 80% success rate

        # Apply per 90 minutes conversion if enabled
        player_stats[i] = convert_to_per_90(player_stats[i], per_90_mode)

    # Display bar charts for each player (only for players with valid data)
    if not player_stats:
        st.warning("No valid player data found for the selected competitions.")
        return

    actual_players = len(player_stats)
    cols = st.columns(actual_players)

    for i, (col, stats) in enumerate(zip(cols, player_stats)):
        with col:
            player = stats['name']
            # Create player info dictionary
            selected_comps = stats.get('selected_competitions', ['All competitions'])
            comp_text = ', '.join(selected_comps) if len(selected_comps) <= 2 else f"{selected_comps[0]} +{len(selected_comps)-1} more"

            # Get original stats for display (before per 90 conversion)
            original_stats = player_data.get(player)

            # Use filtered stats for display but show original total stats for context
            filtered_stats_display = stats

            player_info = {
                "age": filtered_stats_display.get("age", "N/A"),
                "team": filtered_stats_display["team"],
                "total_matches": filtered_stats_display["matches"],  # Use filtered matches
                "total_minutes": filtered_stats_display["minutes"],  # Use filtered minutes
                "total_conceded": filtered_stats_display["conceded_goals"],  # Use filtered goals
                "competitions": comp_text,
                "per_90_mode": per_90_mode,
                "original_matches": original_stats["matches"],  # Keep original for reference
                "original_minutes": original_stats["minutes"],  # Keep original for reference
            }

            # For consistency, use only the selected players for comparison
            selected_player_stats = player_stats.copy()

            # Generate and display the bar chart
            fig = generate_goalkeeper_comparison_chart(player, stats, player_info, gk_metrics_by_category, selected_player_stats)
            st.plotly_chart(fig, use_container_width=True)

    # Add a table comparison
    stats_mode_text = " (Per 90 Minutes)" if per_90_mode else ""
    st.subheader(f"Detailed Comparison{stats_mode_text}")

    # Define all metrics to include in the detailed comparison following your specification
    all_metrics = {
        "General": [
            {"name": "Matches", "key": "matches", "format": "int"},
            {"name": "Minutes played", "key": "minutes", "format": "int"},
            {"name": "Total actions", "key": "total_actions", "format": "int"},
            {"name": "Total actions successful", "key": "total_actions_successful", "format": "int"},
            {"name": "Team", "key": "team", "format": "str"}
        ],
        "Goalkeeping": [
            {"name": "Conceded goals", "key": "conceded_goals", "format": "int"},
            {"name": "xCG", "key": "xcg", "format": "float2"},
            {"name": "Shots against", "key": "shots_against", "format": "int"},
            {"name": "Saves", "key": "saves", "format": "int"},
            {"name": "Saves with reflexes", "key": "saves_with_reflexes", "format": "int"},
            {"name": "Exits", "key": "exits", "format": "int"}
        ],
        "Distribution": [
            {"name": "Long passes", "key": "long_passes", "format": "int"},
            {"name": "Long passes accurate", "key": "long_passes_accurate", "format": "int"},
            {"name": "Short passes", "key": "short_passes", "format": "int"},
            {"name": "Short passes accurate", "key": "short_passes_accurate", "format": "int"},
            {"name": "Goal kicks", "key": "goal_kicks", "format": "int"},
            {"name": "Short goal kicks", "key": "short_goal_kicks", "format": "int"},
            {"name": "Long goal kicks", "key": "long_goal_kicks", "format": "int"}
        ]
    }

    # Create a list of all metrics with category headers
    metrics_list = []
    for category, metrics in all_metrics.items():
        metrics_list.append({"name": f"--- {category} ---", "key": None, "format": "header"})
        metrics_list.extend(metrics)

    # Create a DataFrame for the comparison
    comparison_df = pd.DataFrame({
        "Metric": [m["name"] for m in metrics_list]
    })

    # Add data for each player (only for players with valid data)
    for i, stats in enumerate(player_stats):
        player = stats['name']
        player_data_list = []

        for metric in metrics_list:
            if metric["format"] == "header":
                # Add category header
                player_data_list.append("")
            else:
                # Get the value
                key = metric["key"]
                value = stats.get(key, 0)

                # Format the value
                if metric["format"] == "int":
                    player_data_list.append(int(value))
                elif metric["format"] == "float1":
                    player_data_list.append(f"{value:.1f}")
                elif metric["format"] == "float2":
                    player_data_list.append(f"{value:.2f}")
                elif metric["format"] == "percent":
                    player_data_list.append(f"{value:.1f}%")
                else:
                    player_data_list.append(value)

        comparison_df[player] = player_data_list

    # Apply percentile coloring to the comparison table
    def color_percentile(val, metric_name=None):
        """Apply color styling based on percentile value"""
        if isinstance(val, str) and val.startswith('---'):
            # Category header
            return 'background-color: #e6e6e6; font-weight: bold; color: #333333'

        if metric_name is None or val == '':
            return ''

        # List of negative stats where lower values are better
        negative_stats = ["Goals Conceded", "Goals Conceded/90", "Conceded goals", "xCG"]

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

    # Create a styled dataframe with percentile coloring
    styled_df = pd.DataFrame()

    # Apply styling to each column
    for col in comparison_df.columns:
        if col == 'Metric':
            styled_df[col] = comparison_df[col]
        else:
            # Apply coloring to each player's column
            for i, metric in enumerate(comparison_df['Metric']):
                if i < len(comparison_df):
                    val = comparison_df.loc[i, col]
                    if metric.startswith('---') or val == '':
                        # Skip headers and empty cells
                        continue

                    # Apply color based on percentile
                    comparison_df.loc[i, col] = f"{val}"

    # Display the styled comparison table
    st.dataframe(
        comparison_df.style.apply(
            lambda row: [color_percentile(val, row['Metric']) for val in row],
            axis=1
        ),
        use_container_width=True
    )

    # Radar Chart Comparison removed as requested

    # Add Player Role Analysis
    role_stats_mode_text = " (Per 90 Minutes)" if per_90_mode else ""
    st.subheader(f"Player Role Analysis{role_stats_mode_text}")

    if per_90_mode:
        st.info("📊 **Per 90 Minutes Mode**: All statistics have been normalized to per 90 minutes of play for fair comparison between players with different playing time.")

    # Define metrics and weights for goalkeeper roles
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

    # Normalize and score each player for each role
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

    # Compute scores for all players (assuming all are goalkeepers)
    role_scores = compute_role_scores(player_stats, goalkeeper_role_weights)

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
                st.markdown(f"<h3 style='text-align: center; margin-bottom: 10px; font-size: 16px;'>{player} (GK)</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; margin-bottom: 10px; font-size: 12px; color: #333;'>{player_team} | {player_matches} matches</p>", unsafe_allow_html=True)

                # Create separate figure for this player
                fig = go.Figure()

                # Sort role scores for this player from highest to lowest
                sorted_roles = sorted([(role, player_score[role]) for role in goalkeeper_role_weights.keys()], key=lambda x: x[1], reverse=True)
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
                    for role, role_weights in goalkeeper_role_weights.items():
                        st.markdown(f"**{role}** (Total Score: {player_score[role]:.3f})")

                        role_breakdown = []
                        total_weight = sum(abs(w) for w in role_weights.values())

                        for stat, weight in role_weights.items():
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
                                if stat == "conceded_goals":
                                    display_stat = "Goals Conceded"
                                elif stat == "xcg":
                                    display_stat = "xCG"
                                elif stat == "shots_against":
                                    display_stat = "Shots Against"
                                elif stat == "saves_with_reflexes":
                                    display_stat = "Saves with Reflexes"
                                elif stat == "long_passes_accurate":
                                    display_stat = "Long Passes Accurate"
                                elif stat == "short_passes_accurate":
                                    display_stat = "Short Passes Accurate"
                                elif stat == "goal_kicks":
                                    display_stat = "Goal Kicks"
                                elif stat == "short_goal_kicks":
                                    display_stat = "Short Goal Kicks"
                                elif stat == "long_goal_kicks":
                                    display_stat = "Long Goal Kicks"

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
            for role in goalkeeper_role_weights.keys():
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

    # Add info message for goalkeeper roles
    st.info(
        """
**Goalkeeper Role Analysis**: Each goalkeeper is scored for different playing styles based on their statistics:

- **Shot Stopper**: Excels at making saves and preventing goals through reflexes and positioning.
- **Sweeper Keeper**: Acts as an extra defender, good with distribution and reading the game.

**How to Read the Detailed Breakdown**:
- **Raw Value**: The actual statistic value for the player
- **Weight**: How important this statistic is for the role (negative means lower is better)
- **Normalized**: The statistic normalized to 0-1 scale compared to other players
- **Contribution**: How much this statistic contributes to the final role score
        """
    )

    # Add detailed weight information in a collapsible section
    with st.expander("📊 View Role Weight Details", expanded=False):
        st.markdown("""
        ### Goalkeeper Role Weight Details

        Each goalkeeper role is defined by a weighted combination of key statistics that determine the player's suitability for that role.
        The weights below show which statistics are most important for each role type.
        """)

        # Create a table for Shot Stopper weights
        st.markdown("#### Shot Stopper")
        ss_data = []
        for stat, weight in goalkeeper_role_weights["Shot Stopper"].items():
            # Convert stat key to display name
            display_name = stat.replace('_', ' ').title()
            if stat == "conceded_goals":
                display_name = "Goals Conceded"
            elif stat == "xcg":
                display_name = "xCG"
            elif stat == "shots_against":
                display_name = "Shots Against"
            elif stat == "saves_with_reflexes":
                display_name = "Saves with Reflexes"
            ss_data.append([display_name, weight])

        ss_df = pd.DataFrame(ss_data, columns=["Statistic", "Weight"])
        st.dataframe(ss_df.style.format({"Weight": "{:.2f}"}), use_container_width=True)

        st.markdown("#### Sweeper Keeper")
        sk_data = []
        for stat, weight in goalkeeper_role_weights["Sweeper Keeper"].items():
            # Convert stat key to display name
            display_name = stat.replace('_', ' ').title()
            if stat == "long_passes_accurate":
                display_name = "Long Passes Accurate"
            elif stat == "short_passes_accurate":
                display_name = "Short Passes Accurate"
            elif stat == "goal_kicks":
                display_name = "Goal Kicks"
            elif stat == "short_goal_kicks":
                display_name = "Short Goal Kicks"
            elif stat == "long_goal_kicks":
                display_name = "Long Goal Kicks"
            sk_data.append([display_name, weight])

        sk_df = pd.DataFrame(sk_data, columns=["Statistic", "Weight"])
        st.dataframe(sk_df.style.format({"Weight": "{:.2f}"}), use_container_width=True)

        st.markdown("""
        **Note**: Negative weights indicate that lower values are better for that role (e.g., fewer goals conceded is better for a Shot Stopper).
        """)

    st.markdown("---")

    # Add Scatter Plot Analysis Section
    st.subheader("Performance Scatter Plot")

    # Define goalkeeper-specific preset combinations
    gk_preset_combinations = {
        # Goalkeeper presets
        "Saves vs Conceded": ("saves", "conceded_goals"),
        "Distribution vs Exits": ("long_passes_accurate", "exits"),
        "Shot Stopping vs Sweeping": ("saves_with_reflexes", "xcg"),
        "Saves vs Shots Against": ("saves", "shots_against"),
        "Goal Kicks vs Passes": ("goal_kicks", "short_passes_accurate"),
        "Custom Selection": ("custom", "custom")
    }

    # Let user select a preset or custom
    selected_preset = st.selectbox(
        "Choose analysis perspective:",
        options=list(gk_preset_combinations.keys()),
        index=0
    )

    # Add explanation for the selected preset
    preset_explanations = {
        "Saves vs Conceded": "This perspective shows shot-stopping efficiency. "
                           "Elite Shot Stoppers make many saves with few goals conceded, "
                           "while Sweeper Keepers may concede more but contribute to build-up play.",

        "Distribution vs Exits": "This highlights goalkeeper's role in possession and defensive actions. "
                               "Traditional Keepers focus on safe distribution, "
                               "while Modern Sweeper Keepers excel at both distribution and defensive exits.",

        "Shot Stopping vs Sweeping": "This shows goalkeeper's defensive style specialization. "
                                    "Pure Shot Stoppers excel at reflex saves, "
                                    "while Sweeper Keepers contribute more to defensive actions and ball-playing.",

        "Saves vs Shots Against": "This reveals workload and save efficiency relationship. "
                                "Busy Keepers face many shots and make many saves, "
                                "while Protected Keepers face fewer shots but must maintain concentration.",

        "Goal Kicks vs Passes": "This shows distribution style and involvement in build-up play. "
                              "Traditional Keepers rely on goal kicks, "
                              "while Ball-Playing Keepers are more involved in short passing."
    }

    if selected_preset in preset_explanations:
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 10px 0; font-style: italic; color: #555;">
            {preset_explanations[selected_preset]}
        </div>
        """, unsafe_allow_html=True)

    # Get the preset values
    preset_x, preset_y = gk_preset_combinations[selected_preset]

    # Create columns for selecting stats for each axis
    scatter_cols = st.columns(2)

    # Define available stats for goalkeepers
    gk_available_stats = [
        "saves", "conceded_goals", "shots_against", "xcg", "saves_with_reflexes",
        "exits", "goal_kicks", "short_goal_kicks", "long_goal_kicks",
        "short_passes", "short_passes_accurate", "long_passes", "long_passes_accurate",
        "minutes", "matches"
    ]

    # Define stat categories for filtering
    gk_stat_categories = {
        "Shot Stopping": ["saves", "saves_with_reflexes", "conceded_goals", "shots_against", "xcg"],
        "Distribution": ["goal_kicks", "short_goal_kicks", "long_goal_kicks", "short_passes",
                        "short_passes_accurate", "long_passes", "long_passes_accurate"],
        "Defensive Actions": ["exits", "xcg"],
        "General": ["minutes", "matches"]
    }

    with scatter_cols[0]:
        if preset_x == "custom":
            # Add category filter for stats
            x_stat_category = st.radio(
                "Filter X-axis stats by category:",
                options=["All"] + list(gk_stat_categories.keys()),
                horizontal=True,
                key="x_stat_category"
            )

            # Filter stats based on selected category
            if x_stat_category == "All":
                x_filtered_stats = gk_available_stats
            else:
                x_filtered_stats = gk_stat_categories.get(x_stat_category, gk_available_stats)

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
            if preset_x == "conceded_goals":
                display_name = "Goals Conceded"
            elif preset_x == "xcg":
                display_name = "xCG"
            elif preset_x == "saves_with_reflexes":
                display_name = "Saves with Reflexes"
            elif preset_x == "long_passes_accurate":
                display_name = "Long Passes Accurate"
            st.markdown(f"**X-Axis**: {display_name}")

    with scatter_cols[1]:
        if preset_y == "custom":
            # Add category filter for stats
            y_stat_category = st.radio(
                "Filter Y-axis stats by category:",
                options=["All"] + list(gk_stat_categories.keys()),
                horizontal=True,
                key="y_stat_category"
            )

            # Filter stats based on selected category
            if y_stat_category == "All":
                y_filtered_stats = gk_available_stats
            else:
                y_filtered_stats = gk_stat_categories.get(y_stat_category, gk_available_stats)

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
            if preset_y == "conceded_goals":
                display_name = "Goals Conceded"
            elif preset_y == "xcg":
                display_name = "xCG"
            elif preset_y == "saves_with_reflexes":
                display_name = "Saves with Reflexes"
            elif preset_y == "long_passes_accurate":
                display_name = "Long Passes Accurate"
            st.markdown(f"**Y-Axis**: {display_name}")

    # Create function to generate goalkeeper scatter plot
    def create_gk_scatter_plot(players, player_stats_list, x_stat, y_stat, per_90_mode=False,
                              additional_players_data=None):
        # List of negative stats where lower values are better for goalkeepers
        negative_stats = ["conceded_goals", "xcg"]

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
        def calculate_percentile(value, all_values, is_negative=False):
            if len(all_values) <= 1:
                return 50

            # Calculate percentile rank
            rank = sum(1 for v in all_values if v < value)
            percentile = (rank / (len(all_values) - 1)) * 100

            # For negative stats, invert the percentile
            if is_negative:
                percentile = 100 - percentile

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

            x_percentile = calculate_percentile(x_val, x_values, x_stat in negative_stats)
            y_percentile = calculate_percentile(y_val, y_values, y_stat in negative_stats)

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

            if x_stat == "conceded_goals":
                x_display = "Goals Conceded"
            elif x_stat == "xcg":
                x_display = "xCG"
            elif x_stat == "saves_with_reflexes":
                x_display = "Saves with Reflexes"
            elif x_stat == "long_passes_accurate":
                x_display = "Long Passes Accurate"

            if y_stat == "conceded_goals":
                y_display = "Goals Conceded"
            elif y_stat == "xcg":
                y_display = "xCG"
            elif y_stat == "saves_with_reflexes":
                y_display = "Saves with Reflexes"
            elif y_stat == "long_passes_accurate":
                y_display = "Long Passes Accurate"

            # Add per 90 indicator if enabled
            x_label = f"{x_display}" + (" (per 90)" if per_90_mode and x_stat not in ["minutes", "matches"] else "")
            y_label = f"{y_display}" + (" (per 90)" if per_90_mode and y_stat not in ["minutes", "matches"] else "")

            if x_stat in negative_stats:
                hover_text += f"{x_label}: {x_val:.2f} ({x_percentile:.0f}% - lower is better)<br>"
            else:
                hover_text += f"{x_label}: {x_val:.2f} ({x_percentile:.0f}%)<br>"

            if y_stat in negative_stats:
                hover_text += f"{y_label}: {y_val:.2f} ({y_percentile:.0f}% - lower is better)<br>"
            else:
                hover_text += f"{y_label}: {y_val:.2f} ({y_percentile:.0f}%)<br>"

            # Add additional key stats
            additional_stats = ["saves", "conceded_goals", "shots_against", "exits"]
            for stat in additional_stats:
                if stat != x_stat and stat != y_stat and stat in stats:
                    stat_val = float(stats[stat])
                    stat_display = stat.replace('_', ' ').title()
                    if stat == "conceded_goals":
                        stat_display = "Goals Conceded"
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

        # Calculate axis ranges based on actual data values
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

        # Add quadrant lines
        fig.add_shape(
            type="line", x0=x_range[0], y0=y_mid, x1=x_range[1], y1=y_mid,
            line=dict(color="#666666", width=1)
        )
        fig.add_shape(
            type="line", x0=x_mid, y0=y_range[0], x1=x_mid, y1=y_range[1],
            line=dict(color="#666666", width=1)
        )

        # Generate quadrant descriptions for goalkeepers
        def get_gk_quadrant_descriptions(x_stat, y_stat):
            # Define goalkeeper role descriptions
            role_descriptions = {
                "saves": {
                    "high": "Active Shot Stopper",
                    "low": "Protected Keeper"
                },
                "conceded_goals": {
                    "high": "Vulnerable Defense",  # Note: this is inverted due to negative stat
                    "low": "Solid Defense"
                },
                "shots_against": {
                    "high": "Busy Keeper",
                    "low": "Protected Keeper"
                },
                "xcg": {
                    "high": "Under Pressure",  # Note: this is inverted due to negative stat
                    "low": "Well Protected"
                },
                "saves_with_reflexes": {
                    "high": "Reflex Specialist",
                    "low": "Positional Keeper"
                },
                "exits": {
                    "high": "Sweeper Keeper",
                    "low": "Line Keeper"
                },
                "goal_kicks": {
                    "high": "Long Ball Distributor",
                    "low": "Short Passing Keeper"
                },
                "long_passes_accurate": {
                    "high": "Ball Playing Keeper",
                    "low": "Traditional Keeper"
                },
                "short_passes_accurate": {
                    "high": "Build-up Specialist",
                    "low": "Direct Distributor"
                }
            }

            # Check if stats are negative
            x_is_negative = x_stat in negative_stats
            y_is_negative = y_stat in negative_stats

            # Get descriptions accounting for negative stats
            if x_is_negative:
                x_high = role_descriptions.get(x_stat, {}).get("low", f"Low {x_stat.replace('_', ' ').title()}")
                x_low = role_descriptions.get(x_stat, {}).get("high", f"High {x_stat.replace('_', ' ').title()}")
            else:
                x_high = role_descriptions.get(x_stat, {}).get("high", f"High {x_stat.replace('_', ' ').title()}")
                x_low = role_descriptions.get(x_stat, {}).get("low", f"Low {x_stat.replace('_', ' ').title()}")

            if y_is_negative:
                y_high = role_descriptions.get(y_stat, {}).get("low", f"Low {y_stat.replace('_', ' ').title()}")
                y_low = role_descriptions.get(y_stat, {}).get("high", f"High {y_stat.replace('_', ' ').title()}")
            else:
                y_high = role_descriptions.get(y_stat, {}).get("high", f"High {y_stat.replace('_', ' ').title()}")
                y_low = role_descriptions.get(y_stat, {}).get("low", f"Low {y_stat.replace('_', ' ').title()}")

            # Calculate quadrant positions based on actual data ranges
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

        # Add quadrant descriptions
        fig.update_layout(annotations=get_gk_quadrant_descriptions(x_stat, y_stat))

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

        if x_stat == "conceded_goals":
            x_display = "Goals Conceded"
        elif x_stat == "xcg":
            x_display = "xCG"
        elif x_stat == "saves_with_reflexes":
            x_display = "Saves with Reflexes"
        elif x_stat == "long_passes_accurate":
            x_display = "Long Passes Accurate"

        if y_stat == "conceded_goals":
            y_display = "Goals Conceded"
        elif y_stat == "xcg":
            y_display = "xCG"
        elif y_stat == "saves_with_reflexes":
            y_display = "Saves with Reflexes"
        elif y_stat == "long_passes_accurate":
            y_display = "Long Passes Accurate"

        # Add title with per90 indication if enabled
        title_text = "Goalkeeper Performance Classification"
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

    # Add configuration options for scatter plot
    include_additional_players = st.checkbox("Include Additional Goalkeepers from Competition", value=False,
                                            help="Add other goalkeepers from selected competition for better context (same position only)")

    # Additional competition selection if including other players
    additional_competition = None
    if include_additional_players:
        # Get available competitions from the original filtered data
        if hasattr(st.session_state, 'filtered_data') and st.session_state.filtered_data:
            all_competitions = set()
            for player_data in st.session_state.filtered_data.values():
                if 'competitions' in player_data:
                    all_competitions.add(player_data['competitions'])
            available_comps = sorted(list(all_competitions)) if all_competitions else ["Indonesia Liga 1"]
        else:
            available_comps = ["Indonesia Liga 1"]

        additional_competition = st.selectbox(
            "Select competition for additional goalkeepers:",
            options=available_comps,
            index=0,
            help="Choose which competition to include additional goalkeepers from (same position only)"
        )

    if selected_players:
        # Prepare additional players data if requested
        additional_players_data = None
        if include_additional_players and additional_competition:
            # Get additional players from the selected competition
            # This would need access to the full dataset filtered by global filters
            additional_players_data = {}

            # Try to get data from session state or data provider
            if hasattr(st.session_state, 'filtered_data') and st.session_state.filtered_data:
                for player_name, player_data in st.session_state.filtered_data.items():
                    # Check if player is a goalkeeper (assume all players in this dataset are goalkeepers)
                    # Also check for explicit position field if available
                    is_goalkeeper = True  # Default assumption for goalkeeper dataset
                    if 'position' in player_data:
                        position = player_data.get('position', '').lower()
                        is_goalkeeper = position in ['goalkeeper', 'gk', 'goalie', 'keeper', '']

                    if (player_name not in selected_players and
                        player_data.get('competitions') == additional_competition and
                        player_data.get('matches', 0) >= 3 and  # Minimum matches filter
                        is_goalkeeper):  # Same position filter

                        # Apply per 90 conversion if needed
                        processed_stats = player_data.copy()
                        if per_90_mode:
                            # Apply the same per 90 conversion logic
                            def convert_to_per_90_simple(stats):
                                converted = stats.copy()
                                minutes = stats.get("minutes", 0)
                                if minutes > 0:
                                    per_90_stats = [
                                        "conceded_goals", "saves", "shots_against", "xcg",
                                        "saves_with_reflexes", "exits", "goal_kicks",
                                        "short_goal_kicks", "long_goal_kicks", "short_passes",
                                        "short_passes_accurate", "long_passes", "long_passes_accurate"
                                    ]
                                    for stat in per_90_stats:
                                        if stat in converted:
                                            converted[stat] = (converted[stat] * 90) / minutes
                                return converted

                            processed_stats = convert_to_per_90_simple(processed_stats)

                        additional_players_data[player_name] = processed_stats

        # Generate and display interactive plotly version
        plotly_fig = create_gk_scatter_plot(
            selected_players,
            player_stats,
            x_stat,
            y_stat,
            per_90_mode=per_90_mode,
            additional_players_data=additional_players_data
        )

        if plotly_fig:
            st.plotly_chart(plotly_fig, use_container_width=True)

            # Add information about additional players if included
            if include_additional_players and additional_players_data:
                st.info(f"""
                **Additional Players Context**:

                The scatter plot includes {len(additional_players_data)} additional goalkeepers from {additional_competition}
                (shown in gray) to provide better context for comparison. Only goalkeepers with similar positions and
                at least 3 matches are included. Selected players are highlighted in color with larger markers and labels.

                - **Selected Players**: Colored markers with labels (comparison players)
                - **Additional Goalkeepers**: Gray markers without labels (context players from same position)
                """)

        # Add information about negative stats
        if x_stat in ["conceded_goals", "xcg"] or y_stat in ["conceded_goals", "xcg"]:
            st.info("""
            **Note about negative statistics:**

            For goalkeeper stats like Goals Conceded and xCG, lower values indicate better performance.
            These negative stats have been handled appropriately in the visualization:
            - **Red quadrants**: Higher frequency (poorer performance)
            - **Green quadrants**: Lower frequency (better performance)

            The percentiles for these stats have been inverted so that higher percentiles
            consistently represent better performance across all metrics.
            """)
    elif not selected_players:
        st.warning("Please select players to generate the scatter plot.")

    st.markdown("---")


