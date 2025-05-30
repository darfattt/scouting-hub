import streamlit as st
import pandas as pd
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
