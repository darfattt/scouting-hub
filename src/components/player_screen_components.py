import streamlit as st
import pandas as pd
import datetime
import copy
from typing import Dict, Optional


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
        return '#d73027'  # Red, Optional


def render_player_screen(data_provider, filtered_data: Optional[pd.DataFrame] = None, position_type: str = "Goalkeepers"):
    """
    Render the Player Screen interface for filtering players by statistics with percentile ranking.

    Args:
        data_provider: An object that provides access to player data
        filtered_data: Optional pre-filtered player data
        position_type: Type of position (Goalkeepers, Forwards, Defenders, etc.)
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

    st.header("📊 Attribute Analysis")
    st.markdown("Filter players by statistics with customizable ranges and percentile ranking")

    # Get all player data
    if filtered_data is None:
        if not data_provider.data_processor.player_data:
            data_provider.data_processor.process_data()
        player_data_dict = data_provider.data_processor.player_data

        if not player_data_dict:
            st.error("No player data available. Please check your data files.")
            return
    else:
        # filtered_data is a dictionary from filter_player_data function
        player_data_dict = filtered_data

        if not player_data_dict:
            st.warning("No players found with the current filters.")
            return

    # Configuration section (moved up before data processing)
    st.subheader("⚙️ Configuration")
    col1, col2 = st.columns(2)

    with col1:
        per_90_mode = st.checkbox("Per 90 Minutes", value=False, help="Calculate statistics per 90 minutes of play")

    with col2:
        use_percentile_ranks = st.checkbox("Use Percentile Rank", value=True, help="Show percentile ranks with color coding")

    # Date filter section (first filter)
    st.subheader("📅 Date Filter")
    use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range")

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

        # Apply date filter to player data
        if start_date and end_date:
            st.info(f"📊 Filtering data from {start_date} to {end_date}")
            original_player_count = len(player_data_dict)
            player_data_dict = apply_date_filter(player_data_dict, start_date, end_date)

            # Show filtering results
            filtered_player_count = len(player_data_dict)
            st.success(f"✅ Date filter applied: {filtered_player_count} players found (was {original_player_count})")

            # Debug information
            if st.checkbox("🔍 Show Date Filter Debug Info", value=False):
                render_debug_interface(player_data_dict, original_player_count, filtered_player_count, start_date, end_date)

            if not player_data_dict:
                st.warning("No players found with matches in the selected date range.")
                return

    # Minutes filter
    min_minutes = st.slider("Minimum Minutes Played", min_value=0, max_value=3000, value=90, step=90,
                           help="Filter players by minimum minutes played")

    # Convert dictionary to DataFrame
    all_data = pd.DataFrame.from_dict(player_data_dict, orient='index')
    # Add player name as a column
    all_data['player'] = all_data.index
    all_data.reset_index(drop=True, inplace=True)

    if all_data.empty:
        st.warning("No players found with the current filters.")
        return

    # Apply minutes filter early
    if 'minutes' in all_data.columns:
        all_data = all_data[all_data['minutes'] >= min_minutes]
        if all_data.empty:
            st.warning(f"No players found with at least {min_minutes} minutes played.")
            return

    # Define metrics based on position type (removed General category)
    if position_type == "Goalkeepers":
        all_metrics = {
            "Goalkeeping": [
                {"name": "Conceded goals", "key": "conceded_goals", "format": "int"},
                {"name": "xCG", "key": "xcg", "format": "float2"},
                {"name": "Shots against", "key": "shots_against", "format": "int"},
                {"name": "Saves", "key": "saves", "format": "int"},
                {"name": "Saves with reflexes", "key": "saves_with_reflexes", "format": "int"},
                {"name": "Exits", "key": "exits", "format": "int"},
                {"name": "xG Against", "key": "xg_against", "format": "float2"},
                {"name": "Prevented Goals", "key": "prevented_goals", "format": "float2"},
                {"name": "Clean Sheets", "key": "clean_sheets", "format": "int"},
                {"name": "Save Rate %", "key": "save_rate", "format": "float1"}
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
    else:
        all_metrics = {
            'Defensive': [
                {"name": "Duels", "key": "duels", "format": "int"},
                {"name": "Duels won", "key": "duels_won", "format": "int"},
                {"name": "Aerial duels", "key": "aerial_duels", "format": "int"},
                {"name": "Aerial duels won", "key": "aerial_duels_won", "format": "int"},
                {"name": "Interceptions", "key": "interceptions", "format": "int"},
                {"name": "Losses", "key": "losses", "format": "int"},
                {"name": "Losses own half", "key": "losses_own_half", "format": "int"},
                {"name": "Recoveries", "key": "recoveries", "format": "int"},
                {"name": "Recoveries opp half", "key": "recoveries_opp_half", "format": "int"}
            ],
            'Progressive': [
                {"name": "Passes", "key": "passes", "format": "int"},
                {"name": "Passes accurate", "key": "passes_accurate", "format": "int"},
                {"name": "Long passes", "key": "long_passes", "format": "int"},
                {"name": "Long passes accurate", "key": "long_passes_accurate", "format": "int"},
                {"name": "Crosses", "key": "crosses", "format": "int"},
                {"name": "Crosses accurate", "key": "crosses_accurate", "format": "int"},
                {"name": "Dribbles", "key": "dribbles", "format": "int"},
                {"name": "Dribbles successful", "key": "dribbles_successful", "format": "int"}
            ],
            'Offensive': [
                {"name": "Goals", "key": "goals", "format": "int"},
                {"name": "Assists", "key": "assists", "format": "int"},
                {"name": "Shots", "key": "shots", "format": "int"},
                {"name": "Shots on target", "key": "shots_on_target", "format": "int"},
                {"name": "xG", "key": "xg", "format": "float2"}
            ]
        }



    # Stat selection and filtering
    st.subheader("📈 Select Statistics to Filter")

    # Create tabs for different metric categories
    tabs = st.tabs(list(all_metrics.keys()))

    selected_filters = {}

    for i, (category, metrics) in enumerate(all_metrics.items()):
        with tabs[i]:
            st.markdown(f"**{category} Statistics**")

            for metric in metrics:
                if metric["format"] == "str":  # Skip string columns for filtering
                    continue

                metric_key = metric["key"]
                metric_name = metric["name"]

                # Check if column exists in data
                if metric_key not in all_data.columns:
                    continue

                # Get data for this metric
                metric_data = all_data[metric_key].dropna()
                if metric_data.empty:
                    continue

                # Apply per 90 calculation if enabled
                if per_90_mode and metric_key != "minutes":
                    if "minutes" in all_data.columns:
                        metric_data = (metric_data / all_data["minutes"] * 90).dropna()
                        display_name = f"{metric_name} (per 90)"
                    else:
                        display_name = metric_name
                else:
                    display_name = metric_name

                # Create filter controls
                col_check, col_min, col_max = st.columns([1, 1, 1])

                with col_check:
                    use_filter = st.checkbox(f"{display_name}", key=f"filter_{metric_key}")

                if use_filter:
                    min_val = float(metric_data.min())
                    max_val = float(metric_data.max())

                    with col_min:
                        min_filter = st.number_input(
                            f"Min {display_name}",
                            min_value=min_val,
                            max_value=max_val,
                            value=min_val,
                            key=f"min_{metric_key}"
                        )

                    with col_max:
                        max_filter = st.number_input(
                            f"Max {display_name}",
                            min_value=min_val,
                            max_value=max_val,
                            value=max_val,
                            key=f"max_{metric_key}"
                        )

                    selected_filters[metric_key] = {
                        "min": min_filter,
                        "max": max_filter,
                        "name": display_name,
                        "format": metric["format"]
                    }

    # Apply filters and display results
    if selected_filters:
        st.markdown("---")
        st.subheader("🎯 Filtered Results")

        # Apply filters to data
        filtered_players = apply_stat_filters(all_data, selected_filters, per_90_mode)

        if filtered_players.empty:
            st.warning("No players match the selected criteria.")
        else:
            # Show filtering summary
            st.markdown(f"**Found {len(filtered_players)} players** out of {len(all_data)} total players matching the criteria:")

            # Display filter summary
            filter_summary = []
            for metric_key, filter_config in selected_filters.items():
                filter_summary.append(f"• **{filter_config['name']}**: {filter_config['min']:.1f} - {filter_config['max']:.1f}")

            with st.expander("📋 Applied Filters", expanded=False):
                for summary in filter_summary:
                    st.markdown(summary)

            # Calculate percentiles if enabled
            if use_percentile_ranks:
                display_data = calculate_percentiles_for_display(filtered_players, selected_filters, per_90_mode, all_data)
            else:
                display_data = prepare_display_data(filtered_players, selected_filters, per_90_mode)

            # Display results table
            display_results_table(display_data, selected_filters, use_percentile_ranks)
    else:
        st.info("Select at least one statistic to filter players.")


def apply_stat_filters(data: pd.DataFrame, filters: Dict, per_90_mode: bool) -> pd.DataFrame:
    """Apply statistical filters to the player data."""
    filtered_data = data.copy()

    for metric_key, filter_config in filters.items():
        if metric_key not in data.columns:
            continue

        metric_data = data[metric_key]

        # Apply per 90 calculation if enabled
        if per_90_mode and metric_key != "minutes":
            if "minutes" in data.columns:
                metric_data = metric_data / data["minutes"] * 90

        # Apply min/max filters
        mask = (metric_data >= filter_config["min"]) & (metric_data <= filter_config["max"])
        filtered_data = filtered_data[mask]

    return filtered_data


def calculate_percentiles_for_display(filtered_data: pd.DataFrame, filters: Dict, per_90_mode: bool, all_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate percentiles for the filtered data."""
    display_data = filtered_data.copy()

    # Calculate percentiles for each filtered metric
    for metric_key in filters.keys():
        if metric_key not in all_data.columns:
            continue

        # Get reference data for percentile calculation (use all data)
        reference_data = all_data[metric_key].dropna()

        if per_90_mode and metric_key != "minutes":
            if "minutes" in all_data.columns:
                # Calculate per 90 for reference data
                minutes_ref = all_data.loc[reference_data.index, "minutes"]
                reference_data = reference_data / minutes_ref * 90
                reference_data = reference_data.dropna()

                # Calculate per 90 for filtered data
                filtered_metric_data = display_data[metric_key] / display_data["minutes"] * 90
            else:
                filtered_metric_data = display_data[metric_key]
        else:
            filtered_metric_data = display_data[metric_key]

        # Calculate percentiles
        percentiles = []
        for value in filtered_metric_data:
            if pd.isna(value):
                percentiles.append(0)
            else:
                # Handle negative stats (lower is better)
                if metric_key in ["conceded_goals", "losses", "losses_own_half"]:
                    percentile = 100 - (reference_data <= value).mean() * 100
                else:
                    percentile = (reference_data <= value).mean() * 100
                percentiles.append(percentile)

        display_data[f"{metric_key}_percentile"] = percentiles

    return display_data


def prepare_display_data(filtered_data: pd.DataFrame, filters: Dict, per_90_mode: bool) -> pd.DataFrame:
    """Prepare display data without percentiles."""
    display_data = filtered_data.copy()

    # Apply per 90 calculations to display columns
    if per_90_mode:
        for metric_key in filters.keys():
            if metric_key != "minutes" and metric_key in display_data.columns:
                if "minutes" in display_data.columns:
                    display_data[f"{metric_key}_per90"] = display_data[metric_key] / display_data["minutes"] * 90

    return display_data


def display_results_table(data: pd.DataFrame, filters: Dict, use_percentile_ranks: bool):
    """Display the results table with proper formatting and percentile cell coloring."""
    # Prepare columns for display
    basic_columns = []
    column_config = {}

    # Add basic info columns (check what's actually available)
    possible_basic_cols = ["player", "team", "position", "Player", "Team", "Position"]
    for col in possible_basic_cols:
        if col in data.columns and col not in basic_columns:
            basic_columns.append(col)
            column_config[col] = st.column_config.TextColumn(col.title())

    # Add minutes played if available and not already in basic columns
    if "minutes" in data.columns and "minutes" not in basic_columns:
        basic_columns.append("minutes")
        column_config["minutes"] = st.column_config.NumberColumn("Minutes", format="%d")

    display_columns = basic_columns.copy()

    # Add filtered metrics
    for metric_key, filter_config in filters.items():
        if metric_key in data.columns:
            col_name = metric_key

            if use_percentile_ranks and f"{metric_key}_percentile" in data.columns:
                # Show both raw value and percentile with cell coloring
                # First add raw value (only if not already in display_columns)
                if col_name not in display_columns:
                    if filter_config["format"] == "int":
                        column_config[col_name] = st.column_config.NumberColumn(
                            filter_config["name"],
                            format="%d"
                        )
                    else:
                        column_config[col_name] = st.column_config.NumberColumn(
                            filter_config["name"],
                            format="%.2f"
                        )
                    display_columns.append(col_name)

                # Add percentile column (will be styled with colors)
                percentile_col = f"{metric_key}_percentile"
                column_config[percentile_col] = st.column_config.NumberColumn(
                    filter_config["name"] + " %",
                    format="%.1f%%"
                )
                display_columns.append(percentile_col)
            else:
                # Show raw values only (only if not already in display_columns)
                if col_name not in display_columns:
                    if filter_config["format"] == "int":
                        column_config[col_name] = st.column_config.NumberColumn(
                            filter_config["name"],
                            format="%d"
                        )
                    else:
                        column_config[col_name] = st.column_config.NumberColumn(
                            filter_config["name"],
                            format="%.2f"
                        )
                    display_columns.append(col_name)

    # Filter data to only show relevant columns
    available_columns = [col for col in display_columns if col in data.columns]
    display_data = data[available_columns]

    if use_percentile_ranks:
        # Apply cell coloring for percentile columns using pandas styler
        def color_percentile_cells(val, col_name):
            """Apply color styling to percentile cells"""
            if pd.isna(val) or not col_name.endswith('_percentile'):
                return ''
            return f'background-color: {get_percentile_color(val)}; color: white'

        # Create styler and apply coloring to percentile columns
        styler = display_data.style

        # Apply styling to each percentile column
        for metric_key in filters.keys():
            percentile_col = f"{metric_key}_percentile"
            if percentile_col in display_data.columns:
                styler = styler.applymap(
                    lambda val: f'background-color: {get_percentile_color(val)}; color: white' if pd.notna(val) else '',
                    subset=[percentile_col]
                )

        # Display the styled table
        st.dataframe(
            styler,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            height=min(600, len(display_data) * 35 + 50)
        )
    else:
        # Display without styling
        st.dataframe(
            display_data,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            height=min(600, len(display_data) * 35 + 50)
        )


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
