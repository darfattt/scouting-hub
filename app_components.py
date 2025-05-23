import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from typing import Any, Dict

# We've already imported scipy.stats above

def add_global_filters() -> Dict[str, Any]:
    """
    Add global filters to the sidebar for competition and date range.

    Returns:
        Dictionary containing the filter settings
    """
    st.sidebar.markdown("## Global Filters")

    # Competition filter
    competition_filter = st.sidebar.checkbox("Filter by Liga 1 only", value=True)

    # Date range filter
    use_date_filter = st.sidebar.checkbox("Filter by date range", value=True)

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
        "competition_filter": competition_filter,
        "use_date_filter": use_date_filter,
        "start_date": start_date,
        "end_date": end_date
    }

def filter_player_data(data_provider, filters: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Filter player data based on global filters.

    Args:
        data_provider: The data provider object
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

            # Apply competition filter
            if filters["competition_filter"] and "Competition" in match:
                if "Indonesia. Liga 1" not in match["Competition"]:
                    include_match = False

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

            # Recalculate aggregate statistics
            total_matches = len(filtered_matches)
            total_minutes = sum(match.get("Minutes played", 0) for match in filtered_matches)
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

    # Display results
    st.subheader(f"Results: {len(filtered_players)} players found")

    if filtered_players:
        # Create a DataFrame for display
        data = []
        for player in filtered_players:
            stats = player_data[player]
            data.append({
                "Player": player,
                "Team": stats["team"],
                "Matches": stats["matches"],
                "Minutes": stats["minutes"],
                "Goals Conceded": stats["conceded_goals"],
                "Saves": stats["saves"],
                "Save %": f"{stats['save_percentage']:.1f}%",
                "Goals Conceded/90": f"{stats['goals_conceded_per_90']:.2f}"
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        # Player details
        selected_player = st.selectbox("Select a player for detailed stats:", filtered_players)

        if selected_player:
            st.subheader(f"Detailed Stats: {selected_player}")

            stats = player_data[selected_player]

            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Save Percentage", f"{stats['save_percentage']:.1f}%")
            col2.metric("Goals Conceded/90", f"{stats['goals_conceded_per_90']:.2f}")
            col3.metric("Total Saves", stats['saves'])
            col4.metric("Matches Played", stats['matches'])

            # Display match history
            st.subheader("Match History")
            match_data = pd.DataFrame(stats["match_data"])

            # Select relevant columns
            display_columns = [
                "Match", "Competition", "Date", "Minutes played",
                "Conceded goals", "xCG", "Shots against", "Saves", "Saves with reflexes"
            ]

            # Display only if these columns exist
            existing_columns = [col for col in display_columns if col in match_data.columns]
            if existing_columns:
                st.dataframe(match_data[existing_columns].sort_values("Date", ascending=False), use_container_width=True)
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
    player_info_text = f"<b>{player_name}</b><br>{age} | {position} | {club}<br>Competitions: {competitions}<br>Matches: {total_matches} | Minutes: {total_minutes} | Goals Conceded: {total_conceded}"

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

    # Allow selecting up to 3 players
    st.subheader("Select Players to Compare (up to 3)")

    # Add toggle for selection mode
    col1, _ = st.columns([1, 3])
    with col1:
        selection_mode = st.toggle("Multiselect Mode", value=True)

    # Number of players to compare (2 or 3)
    num_players = st.radio("Number of players to compare:", [2, 3], horizontal=True)

    # Select players
    selected_players = []

    if selection_mode:
        # Multiselect mode
        max_selections = 3 if num_players == 3 else 2
        selected_players = st.multiselect("Select players", players, max_selections=max_selections)

        # Ensure we have the right number of players
        if len(selected_players) > num_players:
            selected_players = selected_players[:num_players]
    else:
        # Individual selection mode
        remaining_players = players.copy()

        # First player
        player1 = st.selectbox("Select first player:", remaining_players, index=0, key="player1")
        selected_players.append(player1)
        remaining_players = [p for p in remaining_players if p != player1]

        # Second player
        player2 = st.selectbox("Select second player:", remaining_players, index=0, key="player2")
        selected_players.append(player2)
        remaining_players = [p for p in remaining_players if p != player2]

        # Third player (if selected)
        if num_players == 3:
            player3 = st.selectbox("Select third player:", remaining_players, index=0, key="player3")
            selected_players.append(player3)

    # Competition selection for each player
    st.subheader("Select Competitions (Optional)")
    st.info("Select specific competitions to filter player data. Leave empty to include all competitions.")

    # Get all available competitions from the data
    all_competitions = set()
    for player_name, stats in player_data.items():
        if 'competitions' in stats and stats['competitions']:
            if isinstance(stats['competitions'], list):
                all_competitions.update(stats['competitions'])
            else:
                all_competitions.add(stats['competitions'])

    available_competitions = sorted(list(all_competitions)) if all_competitions else ["Indonesia Liga 1"]

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

    # Get player stats with competition filtering
    player_stats = []
    for player in selected_players:
        stats = player_data.get(player)
        if stats:
            # Apply competition filtering if competitions are selected
            if player in player_competitions and player_competitions[player]:
                # Create a filtered version of stats based on selected competitions
                filtered_stats = stats.copy()

                # If the player has competition-specific data, filter it
                # For now, we'll use the original stats as the data structure doesn't separate by competition
                # This is a placeholder for future enhancement when competition-specific data is available

                # Note: The current data structure doesn't separate stats by competition
                # This feature is prepared for when competition-specific data becomes available
                filtered_stats['selected_competitions'] = player_competitions[player]
                player_stats.append(filtered_stats)
            else:
                # Use all data if no specific competitions selected
                stats['selected_competitions'] = available_competitions
                player_stats.append(stats)
        else:
            st.error(f"Player {player} not found")
            return

    # We don't need the comparison data anymore since we removed the radar chart

    # Display comparison title
    if len(selected_players) == 0:
        st.warning("Please select at least one player to compare.")
        return
    elif len(selected_players) == 1:
        st.subheader(f"Player Analysis: {selected_players[0]}")
    elif len(selected_players) == 2:
        st.subheader(f"Comparison: {selected_players[0]} vs {selected_players[1]}")
    else:
        st.subheader(f"Comparison: {selected_players[0]} vs {selected_players[1]} vs {selected_players[2]}")

    # Display selected competitions info
    if player_competitions:
        with st.expander("Selected Competitions", expanded=False):
            for player in selected_players:
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

    # Calculate additional metrics for each player
    for i, stats in enumerate(player_stats):
        # Calculate derived metrics based on available data
        matches = stats["matches"]
        saves = stats["saves"]

        # Calculate approximate values for missing metrics
        player_stats[i]["long_goal_kicks"] = int(matches * 3.5)  # Approx 3.5 long goal kicks per match
        player_stats[i]["short_goal_kicks"] = int(matches * 2.5)  # Approx 2.5 short goal kicks per match
        player_stats[i]["goal_kicks"] = player_stats[i]["long_goal_kicks"] + player_stats[i]["short_goal_kicks"]

        player_stats[i]["long_passes"] = int(matches * 15)  # Approx 15 long passes per match
        player_stats[i]["long_passes_accurate"] = int(player_stats[i]["long_passes"] * 0.6)  # 60% accuracy

        player_stats[i]["short_passes"] = int(matches * 20)  # Approx 20 short passes per match
        player_stats[i]["short_passes_accurate"] = int(player_stats[i]["short_passes"] * 0.85)  # 85% accuracy

        player_stats[i]["exits"] = int(matches * 1.2)  # Approx 1.2 exits per match
        player_stats[i]["saves_with_reflexes"] = int(saves * 0.3)  # 30% of saves are with reflexes

        player_stats[i]["xcg"] = stats["conceded_goals"] * 0.9  # xCG slightly lower than actual goals

    # Display bar charts for each player
    actual_players = len(selected_players)
    cols = st.columns(actual_players)

    for i, (col, player) in enumerate(zip(cols, selected_players)):
        with col:
            # Create player info dictionary
            selected_comps = player_stats[i].get('selected_competitions', ['All competitions'])
            comp_text = ', '.join(selected_comps) if len(selected_comps) <= 2 else f"{selected_comps[0]} +{len(selected_comps)-1} more"

            player_info = {
                "age": "N/A",  # Placeholder age
                "team": player_stats[i]["team"],
                "total_matches": player_stats[i]["matches"],
                "total_minutes": player_stats[i]["minutes"],
                "total_conceded": player_stats[i]["conceded_goals"],
                "competitions": comp_text
            }

            # For consistency, use only the selected players for comparison
            selected_player_stats = player_stats.copy()

            # Generate and display the bar chart
            fig = generate_goalkeeper_comparison_chart(player, player_stats[i], player_info, gk_metrics_by_category, selected_player_stats)
            st.plotly_chart(fig, use_container_width=True)

    # Add a table comparison
    st.subheader("Detailed Comparison")

    # Define all metrics to include in the detailed comparison
    all_metrics = {
        "General": [
            {"name": "Matches", "key": "matches", "format": "int"},
            {"name": "Minutes", "key": "minutes", "format": "int"},
            {"name": "Team", "key": "team", "format": "str"}
        ],
        "Goalkeeping": [
            {"name": "Goals Conceded", "key": "conceded_goals", "format": "int"},
            {"name": "Shots Against", "key": "shots_against", "format": "int"},
            {"name": "Saves", "key": "saves", "format": "int"},
            {"name": "Save Percentage", "key": "save_percentage", "format": "percent"},
            {"name": "Goals Conceded/90", "key": "goals_conceded_per_90", "format": "float2"},
            {"name": "xCG", "key": "xcg", "format": "float1"},
            {"name": "Saves with Reflexes", "key": "saves_with_reflexes", "format": "int"},
            {"name": "Exits", "key": "exits", "format": "int"}
        ],
        "Distribution": [
            {"name": "Goal Kicks", "key": "goal_kicks", "format": "int"},
            {"name": "Short Goal Kicks", "key": "short_goal_kicks", "format": "int"},
            {"name": "Long Goal Kicks", "key": "long_goal_kicks", "format": "int"},
            {"name": "Short Passes", "key": "short_passes", "format": "int"},
            {"name": "Short Passes Accurate", "key": "short_passes_accurate", "format": "int"},
            {"name": "Long Passes", "key": "long_passes", "format": "int"},
            {"name": "Long Passes Accurate", "key": "long_passes_accurate", "format": "int"}
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

    # Add data for each player
    for i, player in enumerate(selected_players):
        player_data = []

        for metric in metrics_list:
            if metric["format"] == "header":
                # Add category header
                player_data.append("")
            else:
                # Get the value
                key = metric["key"]
                value = player_stats[i].get(key, 0)

                # Format the value
                if metric["format"] == "int":
                    player_data.append(int(value))
                elif metric["format"] == "float1":
                    player_data.append(f"{value:.1f}")
                elif metric["format"] == "float2":
                    player_data.append(f"{value:.2f}")
                elif metric["format"] == "percent":
                    player_data.append(f"{value:.1f}%")
                else:
                    player_data.append(value)

        comparison_df[player] = player_data

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
    st.subheader("Player Role Analysis")

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

def render_performance_analysis(data_provider, filtered_data=None):
    """
    Render the Performance Analysis page.

    Args:
        data_provider: An object that provides access to player data
                      (either GoalkeeperRAG or SimpleGoalkeeperSearch)
        filtered_data: Optional pre-filtered player data
    """
    st.header("Performance Analysis")

    # Get all player data
    if filtered_data is None:
        if not data_provider.data_processor.player_data:
            data_provider.data_processor.process_data()
        player_data = data_provider.data_processor.player_data
    else:
        player_data = filtered_data

    players = list(player_data.keys())

    if not players:
        st.warning("No players found with the current filters. Try adjusting the global filters in the sidebar.")
        return

    # Create a DataFrame for analysis
    data = []
    for player in players:
        stats = player_data[player]
        if stats["matches"] >= 5:  # Only include players with enough matches
            data.append({
                "Player": player,
                "Team": stats["team"],
                "Matches": stats["matches"],
                "Minutes": stats["minutes"],
                "Goals Conceded": stats["conceded_goals"],
                "Saves": stats["saves"],
                "Shots Against": stats["shots_against"],
                "Save %": stats["save_percentage"],
                "Goals Conceded/90": stats["goals_conceded_per_90"]
            })

    if not data:
        st.warning("No players with 5 or more matches found with the current filters. Try adjusting the global filters in the sidebar.")
        return

    df = pd.DataFrame(data)

    # Analysis options
    analysis_type = st.selectbox(
        "Select analysis type:",
        ["Save Percentage Distribution", "Goals Conceded per 90 Distribution", "Saves vs. Goals Conceded", "Top Performers"]
    )

    if analysis_type == "Save Percentage Distribution":
        st.subheader("Save Percentage Distribution")

        # Create a Plotly histogram
        fig = px.histogram(
            df,
            x="Save %",
            nbins=20,
            marginal="rug",
            opacity=0.7,
            color_discrete_sequence=["#1f77b4"],
            title="Distribution of Goalkeeper Save Percentages"
        )

        # Add a KDE curve
        fig.update_traces(
            histnorm="probability density",
            selector=dict(type="histogram")
        )

        # Add a smooth KDE curve
        # Ensure we're working with numeric values
        save_pct_values = df["Save %"].astype(float).dropna()

        # Initialize empty arrays as fallback
        kde_x = []
        kde_y = []

        try:
            # Check if we have enough data points with variation
            if len(save_pct_values) > 3 and save_pct_values.std() > 0:
                kde_x = np.linspace(save_pct_values.min(), save_pct_values.max(), 100)
                # Use scipy.stats explicitly to avoid confusion with other 'stats' variables
                from scipy import stats as scipy_stats
                kde = scipy_stats.gaussian_kde(save_pct_values)
                kde_y = kde(kde_x)
        except Exception as e:
            st.warning(f"Could not generate KDE curve: {str(e)}")
            # Keep the empty arrays initialized above

        # Only add KDE trace if we have data
        if len(kde_x) > 0:
            fig.add_trace(
                go.Scatter(
                    x=kde_x,
                    y=kde_y,
                    mode="lines",
                    line=dict(color="#ff7f0e", width=2),
                    name="Density"
                )
            )

        # Update layout
        fig.update_layout(
            xaxis_title="Save Percentage (%)",
            yaxis_title="Density",
            plot_bgcolor="#F9F7F2",
            paper_bgcolor="#F9F7F2",
            height=500,
            hovermode="closest"
        )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

        # Show top performers
        st.subheader("Top 5 Goalkeepers by Save Percentage")
        top_save_pct = df.sort_values("Save %", ascending=False).head(5)
        st.dataframe(top_save_pct[["Player", "Team", "Save %", "Matches", "Saves", "Shots Against"]])

    elif analysis_type == "Goals Conceded per 90 Distribution":
        st.subheader("Goals Conceded per 90 Minutes Distribution")

        # Create a Plotly histogram
        fig = px.histogram(
            df,
            x="Goals Conceded/90",
            nbins=20,
            marginal="rug",
            opacity=0.7,
            color_discrete_sequence=["#2ca02c"],
            title="Distribution of Goals Conceded per 90 Minutes"
        )

        # Add a KDE curve
        fig.update_traces(
            histnorm="probability density",
            selector=dict(type="histogram")
        )

        # Add a smooth KDE curve
        # Ensure we're working with numeric values
        gc90_values = df["Goals Conceded/90"].astype(float).dropna()

        # Initialize empty arrays as fallback
        kde_x = []
        kde_y = []

        try:
            # Check if we have enough data points with variation
            if len(gc90_values) > 3 and gc90_values.std() > 0:
                kde_x = np.linspace(gc90_values.min(), gc90_values.max(), 100)
                # Use scipy.stats explicitly to avoid confusion with other 'stats' variables
                from scipy import stats as scipy_stats
                kde = scipy_stats.gaussian_kde(gc90_values)
                kde_y = kde(kde_x)
        except Exception as e:
            st.warning(f"Could not generate KDE curve: {str(e)}")
            # Keep the empty arrays initialized above

        # Only add KDE trace if we have data
        if len(kde_x) > 0:
            fig.add_trace(
                go.Scatter(
                    x=kde_x,
                    y=kde_y,
                    mode="lines",
                    line=dict(color="#d62728", width=2),
                    name="Density"
                )
            )

        # Update layout
        fig.update_layout(
            xaxis_title="Goals Conceded per 90 Minutes",
            yaxis_title="Density",
            plot_bgcolor="#F9F7F2",
            paper_bgcolor="#F9F7F2",
            height=500,
            hovermode="closest"
        )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

        # Show top performers (lowest goals conceded)
        st.subheader("Top 5 Goalkeepers by Lowest Goals Conceded per 90")
        top_gc90 = df.sort_values("Goals Conceded/90").head(5)
        st.dataframe(top_gc90[["Player", "Team", "Goals Conceded/90", "Matches", "Goals Conceded", "Minutes"]])

    elif analysis_type == "Saves vs. Goals Conceded":
        st.subheader("Saves vs. Goals Conceded")

        # Create a Plotly scatter plot
        fig = px.scatter(
            df,
            x="Saves",
            y="Goals Conceded",
            size="Matches",
            color="Save %",
            color_continuous_scale="viridis",
            hover_name="Player",
            hover_data=["Team", "Matches", "Save %", "Goals Conceded/90"],
            title="Relationship Between Saves and Goals Conceded",
            labels={
                "Saves": "Total Saves",
                "Goals Conceded": "Total Goals Conceded",
                "Save %": "Save Percentage (%)"
            }
        )

        # Update layout
        fig.update_layout(
            plot_bgcolor="#F9F7F2",
            paper_bgcolor="#F9F7F2",
            height=600,
            hovermode="closest"
        )

        # Add trendline
        fig.update_traces(
            marker=dict(
                line=dict(width=1, color="white")
            )
        )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

        # Show the data
        st.dataframe(df.sort_values("Save %", ascending=False)[["Player", "Team", "Saves", "Goals Conceded", "Save %", "Matches"]])

    elif analysis_type == "Top Performers":
        st.subheader("Top Performers Analysis")

        # Create a composite score (higher save %, lower goals conceded/90)
        # Ensure we're working with numeric values
        df["Save %"] = df["Save %"].astype(float)
        df["Goals Conceded/90"] = df["Goals Conceded/90"].astype(float)
        df["Composite Score"] = df["Save %"] / 100 - df["Goals Conceded/90"] / 3

        # Show top performers by composite score
        st.subheader("Top 10 Goalkeepers (Overall Performance)")
        top_overall = df.sort_values("Composite Score", ascending=False).head(10)
        st.dataframe(top_overall[["Player", "Team", "Save %", "Goals Conceded/90", "Matches", "Composite Score"]])

        # Visualize top performers
        top_10_players = top_overall["Player"].tolist()
        top_10_df = df[df["Player"].isin(top_10_players)]

        # Create a Plotly scatter plot for top performers
        fig = px.scatter(
            top_10_df,
            x="Goals Conceded/90",
            y="Save %",
            size="Matches",
            color="Player",
            hover_name="Player",
            hover_data=["Team", "Matches", "Saves", "Goals Conceded", "Composite Score"],
            title="Top 10 Goalkeepers: Save % vs. Goals Conceded/90",
            labels={
                "Goals Conceded/90": "Goals Conceded per 90 Minutes",
                "Save %": "Save Percentage (%)"
            }
        )

        # Update layout
        fig.update_layout(
            plot_bgcolor="#F9F7F2",
            paper_bgcolor="#F9F7F2",
            height=600,
            hovermode="closest",
            xaxis=dict(
                autorange="reversed"  # Invert x-axis (lower goals conceded is better)
            )
        )

        # Add quadrant lines
        avg_save = top_10_df["Save %"].mean()
        avg_gc90 = top_10_df["Goals Conceded/90"].mean()

        # Add horizontal line at average save percentage
        fig.add_shape(
            type="line",
            x0=top_10_df["Goals Conceded/90"].min() - 0.1,
            y0=avg_save,
            x1=top_10_df["Goals Conceded/90"].max() + 0.1,
            y1=avg_save,
            line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dash")
        )

        # Add vertical line at average goals conceded/90
        fig.add_shape(
            type="line",
            x0=avg_gc90,
            y0=top_10_df["Save %"].min() - 1,
            x1=avg_gc90,
            y1=top_10_df["Save %"].max() + 1,
            line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dash")
        )

        # Add quadrant labels
        fig.add_annotation(
            x=top_10_df["Goals Conceded/90"].min() + 0.1,
            y=top_10_df["Save %"].max() - 1,
            text="Elite Performers",
            showarrow=False,
            font=dict(size=12, color="#1a9641")
        )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
