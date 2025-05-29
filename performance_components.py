import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats

def render_player_performance(rag, filtered_data, position_type):
    """
    Render the Player Performance page with two tabs:
    1. Overall Player Performance
    2. Multi-Stat Comparison
    """
    st.header("Player Performance Analysis")
    st.markdown("Analyze player performances based on key performance metrics.")

    # Create tabs
    tab1, tab2 = st.tabs(["📊 Overall Player Performance", "📈 Multi-Stat Comparison"])

    with tab1:
        render_overall_performance(filtered_data, position_type)

    with tab2:
        render_multi_stat_comparison(filtered_data, position_type)

def render_overall_performance(filtered_data, position_type):
    """
    Render the Overall Player Performance tab
    """
    st.markdown("### Analyze player performances based on key performance metrics")

    # Get available stats based on position type
    available_stats, stats_by_category = get_available_stats_with_categories(filtered_data, position_type)

    if not available_stats:
        st.warning("No performance data available for analysis.")
        return

    # Metric selection with categories
    st.markdown("#### 📊 Select a Key Performance Metric")

    # Create organized options
    metric_options = []
    for category, metrics in stats_by_category.items():
        if metrics:  # Only add categories that have available metrics
            metric_options.append(f"--- {category} ---")
            metric_options.extend(metrics)

    selected_metric = st.selectbox(
        "Choose metric:",
        options=metric_options,
        help="Select the performance metric to analyze"
    )

    # Skip if a category header is selected
    if selected_metric.startswith("---"):
        st.info("Please select a specific metric from the dropdown.")
        return

    # Display options
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 How Many Players to Display?")
        num_players = st.slider(
            "Number of players:",
            min_value=3,
            max_value=min(50, len(filtered_data)),
            value=10,
            help="Select how many top players to display"
        )

    with col2:
        st.markdown("#### ⚽ Display Options")
        show_per_90 = st.checkbox(
            "Show Per 90 Minutes",
            value=False,
            help="Display statistics per 90 minutes played"
        )

    # Generate the chart
    generate_overall_performance_chart(
        filtered_data,
        selected_metric,
        available_stats[selected_metric],
        num_players,
        show_per_90,
        position_type
    )

def render_multi_stat_comparison(filtered_data, position_type):
    """
    Render the Multi-Stat Comparison tab
    """
    st.markdown("### Compare player performances across multiple statistics")

    # Get available stats with categories
    available_stats, stats_by_category = get_available_stats_with_categories(filtered_data, position_type)

    if not available_stats:
        st.warning("No performance data available for analysis.")
        return

    # Stats selection with categories
    st.markdown("#### 📊 Choose 2 or 3 Stats for Comparison")

    # Create organized options for multiselect
    all_stat_names = []
    for category, metrics in stats_by_category.items():
        if metrics:  # Only add categories that have available metrics
            all_stat_names.extend(metrics)

    selected_stats = st.multiselect(
        "Select statistics:",
        options=all_stat_names,
        default=all_stat_names[:2] if len(all_stat_names) >= 2 else [],
        help="Choose 2 or 3 statistics to compare",
        max_selections=3
    )

    # Show category breakdown for selected stats
    if selected_stats:
        st.markdown("**Selected Statistics by Category:**")
        for category, metrics in stats_by_category.items():
            category_selected = [stat for stat in selected_stats if stat in metrics]
            if category_selected:
                st.markdown(f"- **{category}**: {', '.join(category_selected)}")

    if len(selected_stats) < 2:
        st.warning("Please select at least 2 statistics for comparison.")
        return

    # Display options
    col1, col2 = st.columns(2)

    with col1:
        show_trendline = st.checkbox("Show Trendline", value=False)
        show_median = st.checkbox("Show Median Lines", value=False)

    with col2:
        show_player_names = st.checkbox("Show Player Names", value=True)

    # Player count slider
    st.markdown("#### 🎯 How Many Players to Display for Multi-Stat Analysis?")
    num_players_multi = st.slider(
        "Number of players for analysis:",
        min_value=3,
        max_value=min(100, len(filtered_data)),
        value=20,
        help="Select how many players to include in the analysis"
    )

    # Generate the scatter plot
    generate_multi_stat_comparison(
        filtered_data,
        selected_stats,
        available_stats,
        num_players_multi,
        show_trendline,
        show_median,
        show_player_names,
        position_type
    )

def get_available_stats(filtered_data, position_type):
    """
    Get available statistics based on position type with comprehensive metrics
    """
    if not filtered_data:
        return {}

    # Get a sample player to check available stats
    sample_player = next(iter(filtered_data.values()))

    # Define comprehensive stats based on position
    if position_type == "Goalkeepers":
        all_metrics = {
            "General": [
                {"name": "Matches", "key": "matches"},
                {"name": "Minutes played", "key": "minutes"},
                {"name": "Total actions", "key": "total_actions"},
                {"name": "Total actions successful", "key": "total_actions_successful"}
            ],
            "Goalkeeping": [
                {"name": "Conceded goals", "key": "conceded_goals"},
                {"name": "xCG", "key": "xcg"},
                {"name": "Shots against", "key": "shots_against"},
                {"name": "Saves", "key": "saves"},
                {"name": "Saves with reflexes", "key": "saves_with_reflexes"},
                {"name": "Exits", "key": "exits"},
                {"name": "Save Percentage", "key": "save_percentage"}
            ],
            "Distribution": [
                {"name": "Long passes", "key": "long_passes"},
                {"name": "Long passes accurate", "key": "long_passes_accurate"},
                {"name": "Short passes", "key": "short_passes"},
                {"name": "Short passes accurate", "key": "short_passes_accurate"},
                {"name": "Goal kicks", "key": "goal_kicks"},
                {"name": "Short goal kicks", "key": "short_goal_kicks"},
                {"name": "Long goal kicks", "key": "long_goal_kicks"},
                {"name": "Long Pass Accuracy", "key": "long_pass_accuracy"},
                {"name": "Short Pass Accuracy", "key": "short_pass_accuracy"}
            ]
        }
    else:
        all_metrics = {
            "General": [
                {"name": "Minutes", "key": "minutes"},
                {"name": "Total actions", "key": "total_actions"},
                {"name": "Total actions successful", "key": "total_actions_successful"}
            ],
            "Defensive": [
                {"name": "Duels", "key": "duels"},
                {"name": "Duels won", "key": "duels_won"},
                {"name": "Aerial duels", "key": "aerial_duels"},
                {"name": "Aerial duels won", "key": "aerial_duels_won"},
                {"name": "Interceptions", "key": "interceptions"},
                {"name": "Losses", "key": "losses"},
                {"name": "Losses own half", "key": "losses_own_half"},
                {"name": "Recoveries", "key": "recoveries"},
                {"name": "Recoveries opp half", "key": "recoveries_opp_half"}
            ],
            "Progressive": [
                {"name": "Passes", "key": "passes"},
                {"name": "Passes accurate", "key": "passes_accurate"},
                {"name": "Long passes", "key": "long_passes"},
                {"name": "Long passes accurate", "key": "long_passes_accurate"},
                {"name": "Crosses", "key": "crosses"},
                {"name": "Crosses accurate", "key": "crosses_accurate"},
                {"name": "Dribbles", "key": "dribbles"},
                {"name": "Dribbles successful", "key": "dribbles_successful"}
            ],
            "Offensive": [
                {"name": "Goals", "key": "goals"},
                {"name": "Assists", "key": "assists"},
                {"name": "Shots", "key": "shots"},
                {"name": "Shots on target", "key": "shots_on_target"},
                {"name": "xG", "key": "xg"}
            ]
        }

    # Flatten all metrics and filter only available stats
    available_stats = {}
    for category, metrics in all_metrics.items():
        for metric in metrics:
            display_name = metric["name"]
            key = metric["key"]
            if key in sample_player and sample_player[key] is not None:
                available_stats[display_name] = key

    return available_stats

def get_available_stats_with_categories(filtered_data, position_type):
    """
    Get available statistics organized by categories
    """
    if not filtered_data:
        return {}, {}

    # Get a sample player to check available stats
    sample_player = next(iter(filtered_data.values()))

    # Define comprehensive stats based on position
    if position_type == "Goalkeepers":
        all_metrics = {
            "General": [
                {"name": "Matches", "key": "matches"},
                {"name": "Minutes played", "key": "minutes"},
                {"name": "Total actions", "key": "total_actions"},
                {"name": "Total actions successful", "key": "total_actions_successful"}
            ],
            "Goalkeeping": [
                {"name": "Conceded goals", "key": "conceded_goals"},
                {"name": "xCG", "key": "xcg"},
                {"name": "Shots against", "key": "shots_against"},
                {"name": "Saves", "key": "saves"},
                {"name": "Saves with reflexes", "key": "saves_with_reflexes"},
                {"name": "Exits", "key": "exits"},
                {"name": "Save Percentage", "key": "save_percentage"}
            ],
            "Distribution": [
                {"name": "Long passes", "key": "long_passes"},
                {"name": "Long passes accurate", "key": "long_passes_accurate"},
                {"name": "Short passes", "key": "short_passes"},
                {"name": "Short passes accurate", "key": "short_passes_accurate"},
                {"name": "Goal kicks", "key": "goal_kicks"},
                {"name": "Short goal kicks", "key": "short_goal_kicks"},
                {"name": "Long goal kicks", "key": "long_goal_kicks"},
                {"name": "Long Pass Accuracy", "key": "long_pass_accuracy"},
                {"name": "Short Pass Accuracy", "key": "short_pass_accuracy"}
            ]
        }
    else:
        all_metrics = {
            "General": [
                {"name": "Minutes", "key": "minutes"},
                {"name": "Total actions", "key": "total_actions"},
                {"name": "Total actions successful", "key": "total_actions_successful"}
            ],
            "Defensive": [
                {"name": "Duels", "key": "duels"},
                {"name": "Duels won", "key": "duels_won"},
                {"name": "Aerial duels", "key": "aerial_duels"},
                {"name": "Aerial duels won", "key": "aerial_duels_won"},
                {"name": "Interceptions", "key": "interceptions"},
                {"name": "Losses", "key": "losses"},
                {"name": "Losses own half", "key": "losses_own_half"},
                {"name": "Recoveries", "key": "recoveries"},
                {"name": "Recoveries opp half", "key": "recoveries_opp_half"}
            ],
            "Progressive": [
                {"name": "Passes", "key": "passes"},
                {"name": "Passes accurate", "key": "passes_accurate"},
                {"name": "Long passes", "key": "long_passes"},
                {"name": "Long passes accurate", "key": "long_passes_accurate"},
                {"name": "Crosses", "key": "crosses"},
                {"name": "Crosses accurate", "key": "crosses_accurate"},
                {"name": "Dribbles", "key": "dribbles"},
                {"name": "Dribbles successful", "key": "dribbles_successful"}
            ],
            "Offensive": [
                {"name": "Goals", "key": "goals"},
                {"name": "Assists", "key": "assists"},
                {"name": "Shots", "key": "shots"},
                {"name": "Shots on target", "key": "shots_on_target"},
                {"name": "xG", "key": "xg"}
            ]
        }

    # Filter available stats and organize by category
    available_stats = {}
    stats_by_category = {}

    for category, metrics in all_metrics.items():
        category_stats = []
        for metric in metrics:
            display_name = metric["name"]
            key = metric["key"]
            if key in sample_player and sample_player[key] is not None:
                available_stats[display_name] = key
                category_stats.append(display_name)
        stats_by_category[category] = category_stats

    return available_stats, stats_by_category

def generate_overall_performance_chart(filtered_data, metric_name, metric_key, num_players, show_per_90, position_type):
    """
    Generate bar chart for overall player performance
    """
    # Prepare data
    player_data = []

    for player_name, stats in filtered_data.items():
        value = stats.get(metric_key, 0)
        minutes = stats.get("minutes", 1)

        # Calculate per 90 if requested (skip for percentages and accuracy metrics)
        percentage_metrics = ["save_percentage", "pass_accuracy", "long_pass_accuracy", "short_pass_accuracy"]
        if show_per_90 and metric_key not in percentage_metrics and not metric_key.endswith("_accuracy"):
            if minutes > 0:
                value = (value / minutes) * 90

        player_data.append({
            "Player": player_name,
            "Value": value,
            "Team": stats.get("team", "Unknown"),
            "Minutes": minutes
        })

    # Sort by value and take top N players
    player_data.sort(key=lambda x: x["Value"], reverse=True)
    top_players = player_data[:num_players]

    if not top_players:
        st.warning("No data available for the selected metric.")
        return

    # Create DataFrame
    df = pd.DataFrame(top_players)

    # Create bar chart
    fig = px.bar(
        df,
        x="Value",
        y="Player",
        orientation="h",
        title=f"Top {num_players} Players: {metric_name}" + (" (Per 90 Minutes)" if show_per_90 else ""),
        labels={"Value": metric_name + (" (Per 90)" if show_per_90 else ""), "Player": "Players"},
        color="Value",
        color_continuous_scale="viridis",
        hover_data=["Team", "Minutes"]
    )

    # Update layout
    fig.update_layout(
        height=max(400, num_players * 30),
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    # Add value labels on bars
    fig.update_traces(
        texttemplate='%{x:.1f}',
        textposition='auto'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display data table
    st.markdown("#### 📋 Detailed Data")
    display_df = df.copy()
    display_df["Value"] = display_df["Value"].round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def generate_multi_stat_comparison(filtered_data, selected_stats, available_stats, num_players, show_trendline, show_median, show_player_names, position_type):
    """
    Generate scatter plot for multi-stat comparison
    """
    if len(selected_stats) < 2:
        return

    # Prepare data
    player_data = []

    for player_name, stats in filtered_data.items():
        row = {"Player": player_name, "Team": stats.get("team", "Unknown")}

        # Get values for selected stats
        valid_data = True
        for stat_name in selected_stats:
            stat_key = available_stats[stat_name]
            value = stats.get(stat_key, 0)
            if value is None:
                valid_data = False
                break
            row[stat_name] = value

        if valid_data:
            player_data.append(row)

    if not player_data:
        st.warning("No valid data available for the selected statistics.")
        return

    # Create DataFrame and sort by first stat
    df = pd.DataFrame(player_data)
    df = df.sort_values(by=selected_stats[0], ascending=False).head(num_players)

    # Create scatter plot
    if len(selected_stats) == 2:
        # 2D scatter plot
        fig = px.scatter(
            df,
            x=selected_stats[0],
            y=selected_stats[1],
            hover_name="Player" if show_player_names else None,
            hover_data=["Team"],
            title=f"Top {num_players} Players: {selected_stats[0]} vs {selected_stats[1]}",
            color_discrete_sequence=["#1f77b4"]
        )

        # Add player names as text if requested
        if show_player_names:
            fig.add_trace(
                go.Scatter(
                    x=df[selected_stats[0]],
                    y=df[selected_stats[1]],
                    mode="text",
                    text=df["Player"],
                    textposition="top center",
                    showlegend=False,
                    textfont=dict(size=10, color="white")
                )
            )

        # Add trendline if requested
        if show_trendline:
            z = np.polyfit(df[selected_stats[0]], df[selected_stats[1]], 1)
            p = np.poly1d(z)
            fig.add_trace(
                go.Scatter(
                    x=df[selected_stats[0]],
                    y=p(df[selected_stats[0]]),
                    mode="lines",
                    name="Trendline",
                    line=dict(color="red", dash="dash")
                )
            )

        # Add median lines if requested
        if show_median:
            median_x = df[selected_stats[0]].median()
            median_y = df[selected_stats[1]].median()

            fig.add_hline(y=median_y, line_dash="dot", line_color="orange", annotation_text="Median Y")
            fig.add_vline(x=median_x, line_dash="dot", line_color="orange", annotation_text="Median X")

    else:
        # 3D scatter plot for 3 stats
        fig = px.scatter_3d(
            df,
            x=selected_stats[0],
            y=selected_stats[1],
            z=selected_stats[2],
            hover_name="Player" if show_player_names else None,
            hover_data=["Team"],
            title=f"Top {num_players} Players: {' vs '.join(selected_stats)}",
            color_discrete_sequence=["#1f77b4"]
        )

    # Update layout
    fig.update_layout(
        height=600,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display data table
    st.markdown("#### 📋 Detailed Data")
    display_df = df[["Player", "Team"] + selected_stats].copy()
    for stat in selected_stats:
        display_df[stat] = display_df[stat].round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
