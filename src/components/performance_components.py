import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
import copy
from scipy import stats

def render_player_performance(rag, filtered_data, position_type):
    """
    Render the Player Performance page with enhanced analysis and AI insights:
    1. Overall Player Performance
    2. Multi-Stat Comparison
    3. AI Performance Insights
    """
    st.header("Player Performance Analysis")
    st.markdown("Analyze player performances with advanced visualizations and AI-powered insights.")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overall Player Performance", "📈 Multi-Stat Comparison", "🤖 AI Performance Insights"])

    with tab1:
        render_overall_performance(rag, filtered_data, position_type)

    with tab2:
        render_multi_stat_comparison(rag, filtered_data, position_type)

    with tab3:
        if filtered_data:
            render_ai_performance_insights(rag, filtered_data, position_type)
        else:
            st.info("Please select data from the global filters to use AI Performance Insights.")

def render_overall_performance(rag, filtered_data, position_type):
    """
    Render the Overall Player Performance tab with enhanced visualizations
    """
    st.markdown("### Analyze player performances based on key performance metrics")

    # Date filter section (first filter)
    st.subheader("📅 Date Filter")
    use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range", key="overall_date_filter")

    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.date(2024, 8, 1),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="Start date for filtering matches",
                key="overall_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.date(2025, 6, 30),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="End date for filtering matches",
                key="overall_end_date"
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
            if st.checkbox("🔍 Show Date Filter Debug Info", value=False, key="overall_debug"):
                render_debug_interface(filtered_data, original_player_count, filtered_player_count, start_date, end_date)

            if not filtered_data:
                st.warning("No players found with matches in the selected date range.")
                return

    # Configuration section
    st.markdown("#### ⚙️ Configuration")
    col1, col2 = st.columns(2)

    with col1:
        show_per_90 = st.checkbox(
            "Show Per 90 Minutes",
            value=False,
            help="Display statistics per 90 minutes played",
            key="overall_show_per_90"
        )

    with col2:
        num_players = st.slider(
            "Number of players:",
            min_value=3,
            max_value=min(50, len(filtered_data)),
            value=10,
            help="Select how many top players to display",
            key="overall_num_players"
        )

    # Minutes filter
    min_minutes = st.slider(
        "Minimum Minutes Played",
        min_value=0,
        max_value=3000,
        value=90,
        step=90,
        help="Filter players by minimum minutes played",
        key="overall_min_minutes"
    )

    # Apply minutes filter
    if 'minutes' in next(iter(filtered_data.values()), {}):
        filtered_data = {
            player: stats for player, stats in filtered_data.items()
            if stats.get('minutes', 0) >= min_minutes
        }

    if not filtered_data:
        st.warning(f"No players found with at least {min_minutes} minutes played.")
        return

    # Get available stats based on position type (excluding minutes)
    available_stats, stats_by_category = get_available_stats_with_categories(filtered_data, position_type)

    if not available_stats:
        st.warning("No performance data available for analysis.")
        return

    # Metric selection with categories
    st.markdown("#### 📊 Select a Key Performance Metric")

    # Create flat list of all available metrics (no category headers, excluding minutes)
    all_metrics = []
    for category, metrics in stats_by_category.items():
        if metrics:  # Only add metrics that are available
            # Filter out minutes-related metrics
            filtered_metrics = [m for m in metrics if 'minutes' not in m.lower()]
            all_metrics.extend(filtered_metrics)

    if not all_metrics:
        st.warning("No performance metrics available for analysis.")
        return

    selected_metric = st.selectbox(
        "Choose metric:",
        options=all_metrics,
        help="Select the performance metric to analyze"
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

def render_multi_stat_comparison(rag, filtered_data, position_type):
    """
    Render the Multi-Stat Comparison tab with enhanced scatter plots
    """
    st.markdown("### Compare player performances across multiple statistics")

    # Date filter section (first filter)
    st.subheader("📅 Date Filter")
    use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range", key="multi_date_filter")

    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.date(2024, 8, 1),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="Start date for filtering matches",
                key="multi_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.date(2025, 6, 30),
                min_value=datetime.date(2020, 1, 1),
                max_value=datetime.date(2030, 12, 31),
                help="End date for filtering matches",
                key="multi_end_date"
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
            if st.checkbox("🔍 Show Date Filter Debug Info", value=False, key="multi_debug"):
                render_debug_interface(filtered_data, original_player_count, filtered_player_count, start_date, end_date)

            if not filtered_data:
                st.warning("No players found with matches in the selected date range.")
                return

    # Configuration section
    st.markdown("#### ⚙️ Configuration")
    col1, col2 = st.columns(2)

    with col1:
        show_trendline = st.checkbox("Show Trendline", value=False, key="multi_show_trendline")
        show_median = st.checkbox("Show Median Lines", value=False, key="multi_show_median")

    with col2:
        show_player_names = st.checkbox("Show Player Names", value=True, key="multi_show_player_names")

    # Player count and minutes filter
    num_players_multi = st.slider(
        "Number of players for analysis:",
        min_value=3,
        max_value=min(100, len(filtered_data)),
        value=20,
        help="Select how many players to include in the analysis",
        key="multi_num_players"
    )

    min_minutes = st.slider(
        "Minimum Minutes Played",
        min_value=0,
        max_value=3000,
        value=90,
        step=90,
        help="Filter players by minimum minutes played",
        key="multi_min_minutes"
    )

    # Apply minutes filter
    if 'minutes' in next(iter(filtered_data.values()), {}):
        filtered_data = {
            player: stats for player, stats in filtered_data.items()
            if stats.get('minutes', 0) >= min_minutes
        }

    if not filtered_data:
        st.warning(f"No players found with at least {min_minutes} minutes played.")
        return

    # Get available stats with categories (excluding minutes)
    available_stats, stats_by_category = get_available_stats_with_categories(filtered_data, position_type)

    if not available_stats:
        st.warning("No performance data available for analysis.")
        return

    # Stats selection with categories
    st.markdown("#### 📊 Choose 2 or 3 Stats for Comparison")

    # Create organized options for multiselect (excluding minutes)
    all_stat_names = []
    for category, metrics in stats_by_category.items():
        if metrics:  # Only add categories that have available metrics
            # Filter out minutes-related metrics
            filtered_metrics = [m for m in metrics if 'minutes' not in m.lower()]
            all_stat_names.extend(filtered_metrics)

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

    # Define comprehensive stats based on position (excluding minutes from selection)
    if position_type == "Goalkeepers":
        all_metrics = {
            "General": [
                {"name": "Matches", "key": "matches"},
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
        # 2D scatter plot with different colors for each player
        fig = px.scatter(
            df,
            x=selected_stats[0],
            y=selected_stats[1],
            hover_name="Player" if show_player_names else None,
            hover_data=["Team"],
            title=f"Top {num_players} Players: {selected_stats[0]} vs {selected_stats[1]}",
            color="Player",  # Different color for each player
            color_discrete_sequence=px.colors.qualitative.Set3
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
                    textfont=dict(size=11, color="white")  # Increased font size from 10 to 11
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
        # 3D scatter plot for 3 stats with different colors for each player
        fig = px.scatter_3d(
            df,
            x=selected_stats[0],
            y=selected_stats[1],
            z=selected_stats[2],
            hover_name="Player" if show_player_names else None,
            hover_data=["Team"],
            title=f"Top {num_players} Players: {' vs '.join(selected_stats)}",
            color="Player",  # Different color for each player
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        # Add player names as text if requested
        if show_player_names:
            fig.add_trace(
                go.Scatter3d(
                    x=df[selected_stats[0]],
                    y=df[selected_stats[1]],
                    z=df[selected_stats[2]],
                    mode="text",
                    text=df["Player"],
                    textposition="top center",
                    showlegend=False,
                    textfont=dict(size=11, color="white")  # Increased font size from 10 to 11
                )
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

def render_ai_performance_insights(rag, filtered_data, position_type):
    """
    Render AI-powered performance insights and analysis
    """
    st.markdown("### 🤖 AI-Powered Performance Analysis")
    st.markdown("Get intelligent insights about player performances using AI analysis.")

    if not filtered_data:
        st.warning("No player data available for AI analysis.")
        return

    # Initialize session state for AI insights
    if 'ai_insights_results' not in st.session_state:
        st.session_state.ai_insights_results = {}
    if 'current_analysis_type' not in st.session_state:
        st.session_state.current_analysis_type = None

    # Performance analysis options
    analysis_options = [
        "Top Performers Analysis",
        "Performance Trends Analysis",
        "Player Comparison Insights",
        "Tactical Analysis",
        "Performance Prediction"
    ]

    selected_analysis = st.selectbox(
        "Choose AI Analysis Type:",
        analysis_options,
        help="Select the type of AI analysis you want to perform"
    )

    # Check if analysis type changed, clear previous results
    if st.session_state.current_analysis_type != selected_analysis:
        st.session_state.ai_insights_results = {}
        st.session_state.current_analysis_type = selected_analysis

    # Player selection for focused analysis
    players = list(filtered_data.keys())

    # Add a button to start analysis
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        with st.spinner(f"Running {selected_analysis}..."):
            if selected_analysis == "Top Performers Analysis":
                result = render_top_performers_ai_analysis(rag, filtered_data, position_type)
                st.session_state.ai_insights_results[selected_analysis] = result
            elif selected_analysis == "Performance Trends Analysis":
                result = render_performance_trends_ai_analysis(rag, filtered_data, position_type)
                st.session_state.ai_insights_results[selected_analysis] = result
            elif selected_analysis == "Player Comparison Insights":
                result = render_player_comparison_ai_insights(rag, filtered_data, position_type, players)
                st.session_state.ai_insights_results[selected_analysis] = result
            elif selected_analysis == "Tactical Analysis":
                result = render_tactical_ai_analysis(rag, filtered_data, position_type)
                st.session_state.ai_insights_results[selected_analysis] = result
            elif selected_analysis == "Performance Prediction":
                result = render_performance_prediction_ai_analysis(rag, filtered_data, position_type, players)
                st.session_state.ai_insights_results[selected_analysis] = result

    # Display results if available
    if selected_analysis in st.session_state.ai_insights_results:
        result = st.session_state.ai_insights_results[selected_analysis]
        if result:
            st.markdown("---")
            st.markdown("#### 📊 Analysis Results")
            # The result is already displayed by the individual analysis functions
    else:
        st.info(f"Click 'Start Analysis' to begin {selected_analysis}.")

def render_top_performers_ai_analysis(rag, filtered_data, position_type):
    """
    AI analysis of top performers with insights
    """
    st.markdown("#### 🏆 Top Performers AI Analysis")

    # Get top performers data
    top_performers_data = get_top_performers_summary(filtered_data, position_type)

    if top_performers_data is None or top_performers_data.empty:
        st.warning("Insufficient data for top performers analysis.")
        return None

    # Display top performers table
    st.markdown("##### 📊 Top Performers Summary")
    st.dataframe(top_performers_data, use_container_width=True, hide_index=True)

    # Generate AI insights automatically
    with st.spinner("Analyzing top performers..."):
        # Create analysis prompt
        analysis_prompt = create_top_performers_analysis_prompt(top_performers_data, position_type)

        # Get AI insights
        ai_response = rag.query(analysis_prompt)

        st.markdown("##### 🧠 AI Performance Insights")
        st.markdown(ai_response["answer"])

        # Show data sources used
        with st.expander("📚 Analysis Sources"):
            for i, doc in enumerate(ai_response.get("source_documents", [])):
                st.markdown(f"**Source {i+1}:** {doc.metadata.get('player', 'Unknown')}")
                st.text(doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content)

    return {"data": top_performers_data, "insights": ai_response["answer"]}

def render_performance_trends_ai_analysis(rag, filtered_data, position_type):
    """
    AI analysis of performance trends
    """
    st.markdown("#### 📈 Performance Trends AI Analysis")

    # Performance metrics selection
    available_stats, _ = get_available_stats_with_categories(filtered_data, position_type)

    if not available_stats:
        st.warning("No performance metrics available for analysis.")
        return None

    selected_metric = st.selectbox(
        "Select metric for trend analysis:",
        list(available_stats.keys()),
        help="Choose a performance metric to analyze trends"
    )

    # Generate trend visualization
    trend_data = generate_performance_trend_data(filtered_data, available_stats[selected_metric], selected_metric)

    if trend_data is not None and not trend_data.empty:
        # Create trend chart
        fig = px.histogram(
            trend_data,
            x="Value",
            nbins=20,
            title=f"{selected_metric} Distribution Analysis",
            labels={"Value": selected_metric, "count": "Number of Players"}
        )

        fig.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, use_container_width=True)

        # AI trend analysis automatically
        with st.spinner("Analyzing performance trends..."):
            # Create trend analysis prompt
            trend_prompt = create_trend_analysis_prompt(trend_data, selected_metric, position_type)

            # Get AI insights
            ai_response = rag.query(trend_prompt)

            st.markdown("##### 🧠 AI Trend Analysis")
            st.markdown(ai_response["answer"])

        return {"metric": selected_metric, "data": trend_data, "insights": ai_response["answer"]}

    return None

def render_player_comparison_ai_insights(rag, filtered_data, position_type, players):
    """
    AI-powered player comparison insights
    """
    st.markdown("#### ⚖️ Player Comparison AI Insights")

    # Player selection
    selected_players = st.multiselect(
        "Select players to compare (2-4 players):",
        players,
        default=players[:2] if len(players) >= 2 else [],
        max_selections=4,
        help="Choose 2-4 players for AI comparison analysis"
    )

    if len(selected_players) < 2:
        st.info("Please select at least 2 players for comparison.")
        return None

    # Display comparison data
    comparison_data = create_player_comparison_data(filtered_data, selected_players, position_type)

    if comparison_data is not None and not comparison_data.empty:
        st.markdown("##### 📊 Player Comparison Data")
        st.dataframe(comparison_data, use_container_width=True, hide_index=True)

        # AI comparison analysis automatically
        with st.spinner("Analyzing player comparisons..."):
            # Create comparison prompt
            comparison_prompt = create_player_comparison_prompt(comparison_data, selected_players, position_type)

            # Get AI insights
            ai_response = rag.query(comparison_prompt)

            st.markdown("##### 🧠 AI Comparison Analysis")
            st.markdown(ai_response["answer"])

        return {"players": selected_players, "data": comparison_data, "insights": ai_response["answer"]}

    return None

def render_tactical_ai_analysis(rag, filtered_data, position_type):
    """
    AI tactical analysis based on player performance data
    """
    st.markdown("#### ⚽ Tactical AI Analysis")

    # Tactical analysis options
    tactical_options = [
        "Formation Suitability Analysis",
        "Playing Style Analysis",
        "Team Balance Analysis",
        "Positional Strengths & Weaknesses"
    ]

    selected_tactical = st.selectbox(
        "Choose tactical analysis:",
        tactical_options,
        help="Select the type of tactical analysis"
    )

    # Generate tactical insights automatically
    with st.spinner("Analyzing tactical aspects..."):
        # Create tactical analysis prompt
        tactical_prompt = create_tactical_analysis_prompt(filtered_data, selected_tactical, position_type)

        # Get AI insights
        ai_response = rag.query(tactical_prompt)

        st.markdown("##### 🧠 AI Tactical Analysis")
        st.markdown(ai_response["answer"])

    return {"analysis_type": selected_tactical, "insights": ai_response["answer"]}

def render_performance_prediction_ai_analysis(rag, filtered_data, position_type, players):
    """
    AI-powered performance prediction analysis
    """
    st.markdown("#### 🔮 Performance Prediction AI Analysis")

    # Player selection for prediction
    selected_player = st.selectbox(
        "Select player for performance prediction:",
        players,
        help="Choose a player for AI performance prediction analysis"
    )

    if not selected_player:
        return None

    # Display player current stats
    player_stats = filtered_data[selected_player]

    # Create current performance summary
    st.markdown("##### 📊 Current Performance Summary")
    current_stats_df = create_player_stats_summary(player_stats, position_type)
    st.dataframe(current_stats_df, use_container_width=True, hide_index=True)

    # AI prediction analysis automatically
    with st.spinner("Analyzing performance predictions..."):
        # Create prediction prompt
        prediction_prompt = create_performance_prediction_prompt(player_stats, selected_player, position_type)

        # Get AI insights
        ai_response = rag.query(prediction_prompt)

        st.markdown("##### 🧠 AI Performance Prediction")
        st.markdown(ai_response["answer"])

    return {"player": selected_player, "stats": current_stats_df, "insights": ai_response["answer"]}

# Helper functions for AI analysis

def get_top_performers_summary(filtered_data, position_type):
    """
    Create a summary of top performers for AI analysis
    """
    if not filtered_data:
        return None

    # Get key metrics based on position
    if position_type == "Goalkeepers":
        key_metrics = ["save_percentage", "saves", "conceded_goals", "minutes"]
        metric_names = ["Save %", "Saves", "Goals Conceded", "Minutes"]
    else:
        key_metrics = ["goals", "assists", "passes_accurate", "duels_won", "minutes"]
        metric_names = ["Goals", "Assists", "Accurate Passes", "Duels Won", "Minutes"]

    # Create summary data
    summary_data = []
    for player_name, stats in filtered_data.items():
        row = {"Player": player_name, "Team": stats.get("team", "Unknown")}

        for i, metric in enumerate(key_metrics):
            value = stats.get(metric, 0)
            if value is not None:
                row[metric_names[i]] = value

        summary_data.append(row)

    # Convert to DataFrame and sort by first metric
    if summary_data:
        df = pd.DataFrame(summary_data)
        if len(metric_names) > 0:
            df = df.sort_values(by=metric_names[0], ascending=False).head(10)
        return df

    return None

def create_top_performers_analysis_prompt(top_performers_data, position_type):
    """
    Create AI prompt for top performers analysis
    """
    if top_performers_data is None or top_performers_data.empty:
        return f"Analyze the top {position_type.lower()} based on their performance metrics."

    # Convert DataFrame to text summary
    data_summary = top_performers_data.to_string(index=False)

    prompt = f"""
    Analyze the top performing {position_type.lower()} based on the following performance data:

    {data_summary}

    Please provide insights on:
    1. Who are the standout performers and why?
    2. What patterns do you see in the top performers' statistics?
    3. Are there any surprising results or outliers?
    4. What recommendations would you make for team selection based on this data?
    5. How do these players compare in terms of consistency vs peak performance?

    Focus on actionable insights for scouts and coaches.
    """

    return prompt

def generate_performance_trend_data(filtered_data, metric_key, metric_name):
    """
    Generate trend data for performance analysis
    """
    if not filtered_data:
        return None

    trend_data = []
    for player_name, stats in filtered_data.items():
        value = stats.get(metric_key, 0)
        if value is not None and value > 0:
            trend_data.append({
                "Player": player_name,
                "Value": value,
                "Team": stats.get("team", "Unknown")
            })

    if trend_data:
        return pd.DataFrame(trend_data)

    return None

def create_trend_analysis_prompt(trend_data, metric_name, position_type):
    """
    Create AI prompt for trend analysis
    """
    if trend_data is None or trend_data.empty:
        return f"Analyze the {metric_name} trends for {position_type.lower()}."

    # Calculate basic statistics
    mean_val = trend_data["Value"].mean()
    median_val = trend_data["Value"].median()
    std_val = trend_data["Value"].std()
    min_val = trend_data["Value"].min()
    max_val = trend_data["Value"].max()

    prompt = f"""
    Analyze the {metric_name} performance trends for {position_type.lower()} with the following statistics:

    - Mean: {mean_val:.2f}
    - Median: {median_val:.2f}
    - Standard Deviation: {std_val:.2f}
    - Range: {min_val:.2f} to {max_val:.2f}
    - Number of players: {len(trend_data)}

    Top 5 performers:
    {trend_data.nlargest(5, 'Value')[['Player', 'Value', 'Team']].to_string(index=False)}

    Please provide insights on:
    1. What does this distribution tell us about {metric_name} performance?
    2. Are there clear performance tiers or is it more evenly distributed?
    3. What would be considered excellent, good, average, and poor performance levels?
    4. Are there any outliers that deserve special attention?
    5. What factors might explain the performance variations?

    Provide actionable insights for player evaluation and development.
    """

    return prompt

def create_player_comparison_data(filtered_data, selected_players, position_type):
    """
    Create comparison data for selected players
    """
    if not selected_players or not filtered_data:
        return None

    # Get key metrics for comparison
    if position_type == "Goalkeepers":
        metrics = ["save_percentage", "saves", "conceded_goals", "shots_against", "minutes"]
        metric_names = ["Save %", "Saves", "Goals Conceded", "Shots Against", "Minutes"]
    else:
        metrics = ["goals", "assists", "shots", "passes_accurate", "duels_won", "minutes"]
        metric_names = ["Goals", "Assists", "Shots", "Accurate Passes", "Duels Won", "Minutes"]

    comparison_data = []
    for player in selected_players:
        if player in filtered_data:
            stats = filtered_data[player]
            row = {"Player": player, "Team": stats.get("team", "Unknown")}

            for i, metric in enumerate(metrics):
                value = stats.get(metric, 0)
                row[metric_names[i]] = value if value is not None else 0

            comparison_data.append(row)

    if comparison_data:
        return pd.DataFrame(comparison_data)

    return None

def create_player_comparison_prompt(comparison_data, selected_players, position_type):
    """
    Create AI prompt for player comparison
    """
    if comparison_data is None or comparison_data.empty:
        return f"Compare the selected {position_type.lower()} players."

    data_summary = comparison_data.to_string(index=False)

    prompt = f"""
    Compare the following {position_type.lower()} players based on their performance data:

    {data_summary}

    Please provide a detailed comparison including:
    1. Who is the strongest performer overall and in which areas?
    2. What are each player's key strengths and weaknesses?
    3. How do they complement each other if used together?
    4. Which player would you recommend for different tactical situations?
    5. Are there areas where any player significantly outperforms the others?
    6. What development areas would you suggest for each player?

    Provide specific, actionable insights for team selection and player development.
    """

    return prompt

def create_tactical_analysis_prompt(filtered_data, selected_tactical, position_type):
    """
    Create AI prompt for tactical analysis
    """
    # Get sample of player data for context
    sample_players = list(filtered_data.keys())[:5]
    context_data = []

    for player in sample_players:
        stats = filtered_data[player]
        context_data.append(f"{player} ({stats.get('team', 'Unknown')})")

    prompt = f"""
    Perform a {selected_tactical} for {position_type.lower()} based on the available player data.

    Available players include: {', '.join(context_data)}

    For {selected_tactical}, please analyze:
    1. What tactical patterns emerge from the player performance data?
    2. How should these players be utilized tactically?
    3. What formations or playing styles would best suit these players?
    4. Are there tactical weaknesses that need to be addressed?
    5. What recommendations would you make for tactical setup?

    Focus on practical tactical insights that can be implemented by coaches.
    """

    return prompt

def create_player_stats_summary(player_stats, position_type):
    """
    Create a summary of player statistics for display
    """
    if position_type == "Goalkeepers":
        key_stats = {
            "Matches": player_stats.get("matches", 0),
            "Minutes": player_stats.get("minutes", 0),
            "Save %": player_stats.get("save_percentage", 0),
            "Saves": player_stats.get("saves", 0),
            "Goals Conceded": player_stats.get("conceded_goals", 0),
            "Shots Against": player_stats.get("shots_against", 0)
        }
    else:
        key_stats = {
            "Minutes": player_stats.get("minutes", 0),
            "Goals": player_stats.get("goals", 0),
            "Assists": player_stats.get("assists", 0),
            "Shots": player_stats.get("shots", 0),
            "Passes": player_stats.get("passes", 0),
            "Duels Won": player_stats.get("duels_won", 0)
        }

    # Convert to DataFrame
    stats_df = pd.DataFrame([
        {"Statistic": stat, "Value": value}
        for stat, value in key_stats.items()
    ])

    return stats_df

def create_performance_prediction_prompt(player_stats, player_name, position_type):
    """
    Create AI prompt for performance prediction
    """
    # Get key stats for context
    if position_type == "Goalkeepers":
        key_metrics = {
            "Save Percentage": player_stats.get("save_percentage", 0),
            "Saves": player_stats.get("saves", 0),
            "Goals Conceded": player_stats.get("conceded_goals", 0),
            "Minutes": player_stats.get("minutes", 0)
        }
    else:
        key_metrics = {
            "Goals": player_stats.get("goals", 0),
            "Assists": player_stats.get("assists", 0),
            "Minutes": player_stats.get("minutes", 0),
            "Duels Won": player_stats.get("duels_won", 0)
        }

    stats_summary = ", ".join([f"{k}: {v}" for k, v in key_metrics.items()])

    prompt = f"""
    Analyze and predict the future performance of {player_name} ({position_type.lower()}) based on current statistics:

    Current Performance: {stats_summary}

    Please provide predictions and analysis on:
    1. How is this player likely to perform in the next 6 months?
    2. What are the key performance indicators to watch?
    3. Are there signs of improvement or decline in their current form?
    4. What factors could positively or negatively impact their future performance?
    5. What specific areas should the player focus on for development?
    6. How does their current trajectory compare to typical player development patterns?

    Provide specific, actionable insights for player development and performance optimization.
    """

    return prompt


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
