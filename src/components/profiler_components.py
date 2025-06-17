import streamlit as st
import pandas as pd
import datetime

def render_player_search_profiler(data_provider, filtered_data=None, position_type="Goalkeepers"):
    """
    Render the Player Search Profiler page with configurable performance categories.

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

    st.header("🎯 Player Search Profiler")
    st.markdown("Configure custom performance categories with adjustable weights and filters")

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

    # Define performance categories based on position type
    if position_type == "Goalkeepers":
        performance_categories = {
            "Shot Stopper Score": {
                "saves": {"name": "Saves", "weight": 0.3, "negative": False},
                "saves_with_reflexes": {"name": "Saves with Reflexes", "weight": 0.25, "negative": False},
                "conceded_goals": {"name": "Goals Conceded", "weight": 0.2, "negative": True},
                "xcg": {"name": "xCG", "weight": 0.15, "negative": True},
                "shots_against": {"name": "Shots Against", "weight": 0.1, "negative": False}
            },
            "Distribution Score": {
                "long_passes_accurate": {"name": "Long Passes Accurate", "weight": 0.3, "negative": False},
                "short_passes_accurate": {"name": "Short Passes Accurate", "weight": 0.25, "negative": False},
                "goal_kicks": {"name": "Goal Kicks", "weight": 0.2, "negative": False},
                "long_goal_kicks": {"name": "Long Goal Kicks", "weight": 0.15, "negative": False},
                "short_goal_kicks": {"name": "Short Goal Kicks", "weight": 0.1, "negative": False}
            },
            "Sweeper Score": {
                "exits": {"name": "Exits", "weight": 0.4, "negative": False},
                "long_passes_accurate": {"name": "Long Passes Accurate", "weight": 0.25, "negative": False},
                "short_passes_accurate": {"name": "Short Passes Accurate", "weight": 0.2, "negative": False},
                "goal_kicks": {"name": "Goal Kicks", "weight": 0.15, "negative": False}
            }
        }
    else:  # Outfield players
        performance_categories = {
            "Attacking Score": {
                "goals": {"name": "Goals", "weight": 0.3, "negative": False},
                "assists": {"name": "Assists", "weight": 0.25, "negative": False},
                "shots": {"name": "Shots", "weight": 0.2, "negative": False},
                "shots_on_target": {"name": "Shots on Target", "weight": 0.15, "negative": False},
                "dribbles_successful": {"name": "Dribbles Successful", "weight": 0.1, "negative": False}
            },
            "Counter Attack Threat Score": {
                "dribbles_successful": {"name": "Dribbles Successful", "weight": 0.3, "negative": False},
                "recoveries": {"name": "Recoveries", "weight": 0.25, "negative": False},
                "passes": {"name": "Passes", "weight": 0.2, "negative": False},
                "shots": {"name": "Shots", "weight": 0.15, "negative": False},
                "goals": {"name": "Goals", "weight": 0.1, "negative": False}
            },
            "Playmaking Score": {
                "assists": {"name": "Assists", "weight": 0.3, "negative": False},
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.25, "negative": False},
                "pass_accuracy": {"name": "Pass Accuracy", "weight": 0.2, "negative": False},
                "crosses_accurate": {"name": "Crosses Accurate", "weight": 0.15, "negative": False},
                "long_passes_accurate": {"name": "Long Passes Accurate", "weight": 0.1, "negative": False}
            },
            "Build Up": {
                "passes": {"name": "Passes", "weight": 0.3, "negative": False},
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.25, "negative": False},
                "pass_accuracy": {"name": "Pass Accuracy", "weight": 0.2, "negative": False},
                "long_passes": {"name": "Long Passes", "weight": 0.15, "negative": False},
                "long_passes_accurate": {"name": "Long Passes Accurate", "weight": 0.1, "negative": False}
            },
            "Ball Retention": {
                "pass_accuracy": {"name": "Pass Accuracy", "weight": 0.3, "negative": False},
                "dribble_success_rate": {"name": "Dribble Success Rate", "weight": 0.25, "negative": False},
                "losses": {"name": "Losses", "weight": 0.2, "negative": True},
                "losses_own_half": {"name": "Losses Own Half", "weight": 0.15, "negative": True},
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.1, "negative": False}
            },
            "Defensive Score": {
                "duels_won": {"name": "Duels Won", "weight": 0.25, "negative": False},
                "interceptions": {"name": "Interceptions", "weight": 0.2, "negative": False},
                "recoveries": {"name": "Recoveries", "weight": 0.2, "negative": False},
                "duel_success_rate": {"name": "Duel Success Rate", "weight": 0.15, "negative": False},
                "duels": {"name": "Duels", "weight": 0.1, "negative": False},
                "losses": {"name": "Losses", "weight": 0.1, "negative": True}
            },
            "Versatile Score": {
                "goals": {"name": "Goals", "weight": 0.2, "negative": False},
                "assists": {"name": "Assists", "weight": 0.2, "negative": False},
                "duels_won": {"name": "Duels Won", "weight": 0.15, "negative": False},
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.15, "negative": False},
                "interceptions": {"name": "Interceptions", "weight": 0.15, "negative": False},
                "recoveries": {"name": "Recoveries", "weight": 0.15, "negative": False}
            },
            # Role-based performance categories for Center Forwards
            "Advance Forward": {
                "goals": {"name": "Goals", "weight": 0.3, "negative": False},
                "shots": {"name": "Shots", "weight": 0.2, "negative": False},
                "shots_on_target": {"name": "Shots on Target", "weight": 0.15, "negative": False},
                "dribbles_successful": {"name": "Dribbles Successful", "weight": 0.15, "negative": False},
                "passes": {"name": "Passes", "weight": 0.1, "negative": False},
                "minutes": {"name": "Minutes", "weight": 0.1, "negative": False}
            },
            "Pressing Forward": {
                "duels_won": {"name": "Duels Won", "weight": 0.25, "negative": False},
                "recoveries": {"name": "Recoveries", "weight": 0.2, "negative": False},
                "interceptions": {"name": "Interceptions", "weight": 0.2, "negative": False},
                "goals": {"name": "Goals", "weight": 0.15, "negative": False},
                "shots": {"name": "Shots", "weight": 0.1, "negative": False},
                "duel_success_rate": {"name": "Duel Success Rate", "weight": 0.1, "negative": False}
            },
            "Deep-lying Forward": {
                "assists": {"name": "Assists", "weight": 0.25, "negative": False},
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.25, "negative": False},
                "pass_accuracy": {"name": "Pass Accuracy", "weight": 0.15, "negative": False},
                "passes": {"name": "Passes", "weight": 0.15, "negative": False},
                "dribbles": {"name": "Dribbles", "weight": 0.1, "negative": False},
                "goals": {"name": "Goals", "weight": 0.1, "negative": False}
            },
            "Poacher": {
                "goals": {"name": "Goals", "weight": 0.5, "negative": False},
                "shots": {"name": "Shots", "weight": 0.3, "negative": False},
                "shots_on_target": {"name": "Shots on Target", "weight": 0.2, "negative": False}
            },
            # Role-based performance categories for Center Backs
            "No-Nonsense Centre-Back": {
                "duels_won": {"name": "Duels Won", "weight": 0.25, "negative": False},
                "duel_success_rate": {"name": "Duel Success Rate", "weight": 0.2, "negative": False},
                "recoveries": {"name": "Recoveries", "weight": 0.2, "negative": False},
                "interceptions": {"name": "Interceptions", "weight": 0.15, "negative": False},
                "duels": {"name": "Duels", "weight": 0.1, "negative": False},
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.1, "negative": False}
            },
            "Central Defender": {
                "duels_won": {"name": "Duels Won", "weight": 0.2, "negative": False},
                "duel_success_rate": {"name": "Duel Success Rate", "weight": 0.2, "negative": False},
                "interceptions": {"name": "Interceptions", "weight": 0.15, "negative": False},
                "recoveries": {"name": "Recoveries", "weight": 0.15, "negative": False},
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.15, "negative": False},
                "duels": {"name": "Duels", "weight": 0.1, "negative": False},
                "pass_accuracy": {"name": "Pass Accuracy", "weight": 0.05, "negative": False}
            },
            "Ball Playing Defender": {
                "passes_accurate": {"name": "Passes Accurate", "weight": 0.25, "negative": False},
                "pass_accuracy": {"name": "Pass Accuracy", "weight": 0.2, "negative": False},
                "passes": {"name": "Passes", "weight": 0.15, "negative": False},
                "duels_won": {"name": "Duels Won", "weight": 0.15, "negative": False},
                "duel_success_rate": {"name": "Duel Success Rate", "weight": 0.1, "negative": False},
                "interceptions": {"name": "Interceptions", "weight": 0.1, "negative": False},
                "recoveries": {"name": "Recoveries", "weight": 0.05, "negative": False}
            }
        }

    # Performance category selection
    st.subheader("📊 Choose Performance Category")
    selected_category = st.selectbox(
        "Select a performance category:",
        list(performance_categories.keys()),
        help="Choose a preset performance category to analyze players"
    )

    # Configuration options
    st.subheader("⚙️ Configuration")
    col1, col2, col3 = st.columns(3)

    with col1:
        per_90_mode = st.checkbox("Per 90 Minutes", value=False, help="Calculate statistics per 90 minutes of play")

    with col2:
        show_top_10_only = st.checkbox("Show Top 10 Only", value=True, help="Display only the top 10 players")

    with col3:
        min_minutes = st.slider("Minimum Minutes Played", min_value=0, max_value=3000, value=90, step=90,
                               help="Filter players by minimum minutes played")

    # Date filter section
    st.subheader("📅 Date Filter")
    use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range")

    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.date(2025, 5, 1),
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
            original_player_count = len(player_data)
            player_data = apply_date_filter(player_data, start_date, end_date)

            # Update players list after filtering
            players = list(player_data.keys())
            players.sort()

            # Show filtering results
            filtered_player_count = len(players)
            st.success(f"✅ Date filter applied: {filtered_player_count} players found (was {original_player_count})")

            # Debug information
            if st.checkbox("🔍 Show Date Filter Debug Info", value=False):
                st.markdown("### 🔍 Date Filter Debug Information")

                # Show overall filtering results
                st.markdown(f"**Original player count**: {original_player_count}")
                st.markdown(f"**Filtered player count**: {filtered_player_count}")
                st.markdown(f"**Date range**: {start_date} to {end_date}")

                # Check if David da Silva is in the data
                if "David da Silva" in player_data:
                    david_stats = player_data["David da Silva"]
                    st.markdown("**🎯 David da Silva Debug Info (After Date Filter):**")
                    st.markdown(f"**Filtered Minutes**: {david_stats.get('minutes', 'N/A')}")
                    st.markdown(f"**Filtered Matches**: {david_stats.get('matches', 'N/A')}")

                    # Show match data details
                    match_data = david_stats.get('match_data', [])
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
                        if david_stats.get('minutes', 0) == total_minutes_from_matches:
                            st.success("✅ Minutes calculation is consistent!")
                        else:
                            st.error(f"❌ Minutes mismatch! Stored: {david_stats.get('minutes', 0)}, Calculated: {total_minutes_from_matches}")
                else:
                    st.warning("David da Silva not found in filtered data")

                    # Show available players for debugging
                    available_players = list(player_data.keys())[:10]  # Show first 10
                    st.markdown(f"**Available players (first 10)**: {', '.join(available_players)}")

            if not players:
                st.warning("No players found with matches in the selected date range.")
                return

    # Custom metric selection section
    st.subheader("📊 Select Metrics")
    st.markdown("**Choose which metrics to include in your custom analysis:**")

    category_weights = performance_categories[selected_category].copy()

    # Define additional metrics not in preset categories
    additional_metrics = {}
    if position_type == "Goalkeepers":
        additional_metrics = {
            "exits": {"name": "Exits", "weight": 0.1, "negative": False},
            "goal_kicks": {"name": "Goal Kicks", "weight": 0.1, "negative": False},
            "short_goal_kicks": {"name": "Short Goal Kicks", "weight": 0.1, "negative": False},
            "long_goal_kicks": {"name": "Long Goal Kicks", "weight": 0.1, "negative": False},
            "prevented_goals": {"name": "Prevented Goals", "weight": 0.15, "negative": False},
            "clean_sheets": {"name": "Clean Sheets", "weight": 0.15, "negative": False},
            "save_rate": {"name": "Save Rate %", "weight": 0.15, "negative": False},
            "xg_against": {"name": "xG Against", "weight": 0.1, "negative": True},
            "aerial_duels": {"name": "Aerial Duels", "weight": 0.1, "negative": False},
            "aerial_duels_won": {"name": "Aerial Duels Won", "weight": 0.1, "negative": False}
        }
    else:  # Outfield players
        additional_metrics = {
            "total_actions": {"name": "Total Actions", "weight": 0.1, "negative": False},
            "total_actions_successful": {"name": "Total Actions Successful", "weight": 0.1, "negative": False},
            "long_passes": {"name": "Long Passes", "weight": 0.1, "negative": False},
            "long_passes_accurate": {"name": "Long Passes Accurate", "weight": 0.1, "negative": False},
            "crosses": {"name": "Crosses", "weight": 0.1, "negative": False},
            "crosses_accurate": {"name": "Crosses Accurate", "weight": 0.1, "negative": False},
            "dribbles": {"name": "Dribbles", "weight": 0.1, "negative": False},
            "aerial_duels": {"name": "Aerial Duels", "weight": 0.1, "negative": False},
            "aerial_duels_won": {"name": "Aerial Duels Won", "weight": 0.1, "negative": False},
            "losses_own_half": {"name": "Losses Own Half", "weight": 0.1, "negative": True},
            "recoveries_opp_half": {"name": "Recoveries Opp. Half", "weight": 0.1, "negative": False},
            "yellow_cards": {"name": "Yellow Cards", "weight": 0.05, "negative": True},
            "red_cards": {"name": "Red Cards", "weight": 0.05, "negative": True},
            "shot_accuracy": {"name": "Shot Accuracy %", "weight": 0.1, "negative": False},
            "long_pass_accuracy": {"name": "Long Pass Accuracy %", "weight": 0.1, "negative": False},
            "cross_accuracy": {"name": "Cross Accuracy %", "weight": 0.1, "negative": False},
            "aerial_duel_success_rate": {"name": "Aerial Duel Success Rate %", "weight": 0.1, "negative": False}
        }

    # Get all available metrics for the selected category
    available_metrics = list(category_weights.keys())
    available_metric_names = [category_weights[key]['name'] for key in available_metrics]

    # Get additional metrics
    additional_metric_keys = list(additional_metrics.keys())
    additional_metric_names = [additional_metrics[key]['name'] for key in additional_metric_keys]

    # Create a mapping from display names back to keys
    display_name_to_key = {category_weights[key]['name']: key for key in available_metrics}
    display_name_to_key.update({additional_metrics[key]['name']: key for key in additional_metric_keys})

    # Create two columns for metric selection
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**📋 {selected_category} Metrics:**")
        selected_preset_metrics = st.multiselect(
            "Preset Category Metrics:",
            options=available_metric_names,
            default=available_metric_names,  # Default to all preset metrics
            help=f"Metrics from the {selected_category} category",
            key="preset_metrics"
        )

    with col2:
        st.markdown("**🔧 Additional Metrics:**")
        selected_additional_metrics = st.multiselect(
            "Other Available Metrics:",
            options=additional_metric_names,
            default=[],  # Default to none
            help="Additional metrics not included in the preset category",
            key="additional_metrics"
        )

    # Combine selected metrics
    selected_metric_names = selected_preset_metrics + selected_additional_metrics

    # Convert selected display names back to keys
    selected_metric_keys = [display_name_to_key[name] for name in selected_metric_names]

    if not selected_metric_keys:
        st.warning("⚠️ Please select at least one metric to continue.")
        return

    # Create combined weights dictionary from both preset and additional metrics
    all_available_weights = {**category_weights, **additional_metrics}
    filtered_category_weights = {key: all_available_weights[key] for key in selected_metric_keys if key in all_available_weights}

    # Weight adjustment section
    st.subheader("⚖️ Customize Weights for Selected Metrics")
    st.markdown("**Adjust the importance of each selected metric (0.0 = not important, 1.0 = very important):**")

    # Create weight adjustment interface
    weight_cols = st.columns(2)
    col_idx = 0

    for stat_key, stat_info in filtered_category_weights.items():
        with weight_cols[col_idx % 2]:
            new_weight = st.slider(
                f"⚖️ {stat_info['name']}",
                min_value=0.0,
                max_value=1.0,
                value=stat_info['weight'],
                step=0.05,
                key=f"weight_{stat_key}_{selected_category}",
                help=f"Weight for {stat_info['name']} ({'negative' if stat_info['negative'] else 'positive'} stat)"
            )
            filtered_category_weights[stat_key]['weight'] = new_weight
        col_idx += 1

    # Calculate and display results
    st.markdown("---")
    if st.button("🚀 Calculate Performance Scores", type="primary", use_container_width=True):
        calculate_and_display_scores(
            player_data,
            players,
            filtered_category_weights,
            selected_category,
            per_90_mode,
            min_minutes,
            show_top_10_only
        )

def get_stat_value(stats, stat_key, per_90_mode=False):
    """Safely get stat value with fallback handling"""
    # Direct stat lookup
    value = stats.get(stat_key, 0)

    # If stat is missing, try to calculate from available data
    if value == 0 and stat_key not in stats:
        # Handle missing stats with reasonable defaults or calculations
        if stat_key == "crosses_accurate":
            value = stats.get("crosses", 0) * 0.3  # Assume 30% accuracy
        elif stat_key == "losses":
            value = stats.get("matches", 0) * 8  # Assume 8 losses per match
        elif stat_key == "losses_own_half":
            value = stats.get("losses", 0) * 0.4  # Assume 40% in own half
        elif stat_key == "duel_success_rate":
            duels = stats.get("duels", 0)
            duels_won = stats.get("duels_won", 0)
            value = (duels_won / duels * 100) if duels > 0 else 0
        elif stat_key == "pass_accuracy":
            passes = stats.get("passes", 0)
            passes_accurate = stats.get("passes_accurate", 0)
            value = (passes_accurate / passes * 100) if passes > 0 else 0
        elif stat_key == "dribble_success_rate":
            dribbles = stats.get("dribbles", 0)
            dribbles_successful = stats.get("dribbles_successful", 0)
            value = (dribbles_successful / dribbles * 100) if dribbles > 0 else 0
        elif stat_key == "shot_accuracy":
            shots = stats.get("shots", 0)
            shots_on_target = stats.get("shots_on_target", 0)
            value = (shots_on_target / shots * 100) if shots > 0 else 0
        elif stat_key == "long_pass_accuracy":
            long_passes = stats.get("long_passes", 0)
            long_passes_accurate = stats.get("long_passes_accurate", 0)
            value = (long_passes_accurate / long_passes * 100) if long_passes > 0 else 0
        elif stat_key == "cross_accuracy":
            crosses = stats.get("crosses", 0)
            crosses_accurate = stats.get("crosses_accurate", 0)
            value = (crosses_accurate / crosses * 100) if crosses > 0 else 0
        elif stat_key == "aerial_duel_success_rate":
            aerial_duels = stats.get("aerial_duels", 0)
            aerial_duels_won = stats.get("aerial_duels_won", 0)
            value = (aerial_duels_won / aerial_duels * 100) if aerial_duels > 0 else 0
        elif stat_key == "save_rate":
            shots_against = stats.get("shots_against", 0)
            saves = stats.get("saves", 0)
            value = (saves / shots_against * 100) if shots_against > 0 else 0
        elif stat_key == "total_actions":
            # Calculate total actions from available stats
            passes = stats.get("passes", 0)
            duels = stats.get("duels", 0)
            shots = stats.get("shots", 0)
            value = passes + duels + shots
        elif stat_key == "total_actions_successful":
            # Calculate successful actions
            passes_accurate = stats.get("passes_accurate", 0)
            duels_won = stats.get("duels_won", 0)
            shots_on_target = stats.get("shots_on_target", 0)
            value = passes_accurate + duels_won + shots_on_target
        elif stat_key == "aerial_duels":
            # Estimate aerial duels as 30% of total duels
            value = stats.get("duels", 0) * 0.3
        elif stat_key == "aerial_duels_won":
            # Estimate aerial duels won as 60% of aerial duels
            aerial_duels = stats.get("aerial_duels", stats.get("duels", 0) * 0.3)
            value = aerial_duels * 0.6
        elif stat_key == "recoveries_opp_half":
            # Estimate as 30% of total recoveries
            value = stats.get("recoveries", 0) * 0.3

    # Apply per 90 calculation if enabled (exclude certain stats)
    if per_90_mode and stat_key not in ["minutes", "save_rate", "pass_accuracy", "shot_accuracy",
                                       "long_pass_accuracy", "cross_accuracy", "duel_success_rate",
                                       "dribble_success_rate", "aerial_duel_success_rate"]:
        minutes = stats.get("minutes", 1)
        if minutes > 0:
            value = (value / minutes) * 90

    return value

def calculate_and_display_scores(player_data, players, category_weights, category_name,
                               per_90_mode, min_minutes, show_top_10_only):
    """Calculate performance scores and display results"""

    # Filter players by minimum minutes
    filtered_players = [p for p in players if player_data[p].get("minutes", 0) >= min_minutes]

    if not filtered_players:
        st.warning(f"No players found with at least {min_minutes} minutes played.")
        return

    # Calculate scores
    score_data = []

    # Get all values for normalization
    all_values = {}
    for stat_key in category_weights.keys():
        all_values[stat_key] = []
        for player in filtered_players:
            stats = player_data[player]
            value = get_stat_value(stats, stat_key, per_90_mode)
            all_values[stat_key].append(value)

    # Calculate scores for each player
    for player in filtered_players:
        stats = player_data[player]

        total_score = 0
        total_weight = 0
        stat_values = {}
        percentile_rank = 0

        for stat_key, stat_info in category_weights.items():
            value = get_stat_value(stats, stat_key, per_90_mode)
            stat_values[stat_key] = value
            weight = stat_info['weight']

            # Normalize the value (0-100 scale)
            max_val = max(all_values[stat_key]) if all_values[stat_key] else 1
            min_val = min(all_values[stat_key]) if all_values[stat_key] else 0

            if max_val > min_val:
                if stat_info['negative']:  # Negative stats (lower is better)
                    normalized = 100 - ((value - min_val) / (max_val - min_val) * 100)
                else:
                    normalized = (value - min_val) / (max_val - min_val) * 100
            else:
                normalized = 50  # Default if all values are the same

            total_score += normalized * weight
            total_weight += weight

        final_score = total_score / total_weight if total_weight > 0 else 0

        # Calculate percentile rank
        all_scores = []
        for other_player in filtered_players:
            other_stats = player_data[other_player]
            other_total = 0
            other_weight = 0

            for stat_key, stat_info in category_weights.items():
                other_value = get_stat_value(other_stats, stat_key, per_90_mode)

                other_weight_val = stat_info['weight']
                max_val = max(all_values[stat_key]) if all_values[stat_key] else 1
                min_val = min(all_values[stat_key]) if all_values[stat_key] else 0

                if max_val > min_val:
                    if stat_info['negative']:
                        other_normalized = 100 - ((other_value - min_val) / (max_val - min_val) * 100)
                    else:
                        other_normalized = (other_value - min_val) / (max_val - min_val) * 100
                else:
                    other_normalized = 50

                other_total += other_normalized * other_weight_val
                other_weight += other_weight_val

            other_final = other_total / other_weight if other_weight > 0 else 0
            all_scores.append(other_final)

        # Calculate percentile
        percentile_rank = (sum(1 for score in all_scores if score < final_score) / len(all_scores)) * 100

        score_data.append({
            "Rank": 0,  # Will be set after sorting
            "Player": player,
            "Team": stats.get("team", "Unknown"),
            "Position": stats.get("position", "Unknown"),
            "Minutes": stats.get("minutes", 0),
            "Weighted Score": final_score,
            "Percentile Rank": percentile_rank,
            **{category_weights[stat]['name']: stat_values[stat] for stat in category_weights.keys()}
        })

    # Sort by score and assign ranks
    score_data.sort(key=lambda x: x["Weighted Score"], reverse=True)
    for i, player_data_item in enumerate(score_data):
        player_data_item["Rank"] = i + 1

    # Apply top 10 filter if enabled
    display_data = score_data[:10] if show_top_10_only else score_data

    # Display results
    st.markdown("---")
    st.subheader(f"🏆 Performance Index Results - {category_name}")
    st.markdown(f"Showing {'top 10' if show_top_10_only else 'all'} players {'(per 90 minutes)' if per_90_mode else '(total stats)'}")

    if display_data:
        df = pd.DataFrame(display_data)

        # Configure columns
        column_config = {}

        # Function to get percentile color
        def get_percentile_color(percentile_rank):
            """Get color based on percentile rank"""
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

        # Apply styling to the dataframe
        def style_weighted_score(val, percentile_rank):
            """Style function for weighted score column"""
            color = get_percentile_color(percentile_rank)
            return f'background-color: {color}; color: white; font-weight: bold'

        # Create styled dataframe
        styled_df = df.style.apply(
            lambda row: [
                style_weighted_score(row['Weighted Score'], row['Percentile Rank'])
                if col == 'Weighted Score' else ''
                for col in df.columns
            ],
            axis=1
        )

        # Configure Weighted Score as number column
        column_config["Weighted Score"] = st.column_config.NumberColumn(
            "Weighted Score",
            help="Performance score based on weighted metrics (colored by percentile rank)",
            format="%.1f"
        )

        # Configure Percentile Rank as progress column
        column_config["Percentile Rank"] = st.column_config.ProgressColumn(
            "Percentile Rank",
            help="Percentile ranking among all players",
            min_value=0,
            max_value=100,
            format="%.0f%%"
        )

        # Configure other numeric columns
        for col in df.columns:
            if col not in ["Player", "Team", "Position", "Weighted Score", "Percentile Rank"]:
                if col == "Rank":
                    column_config[col] = st.column_config.NumberColumn(col, format="%d")
                elif col == "Minutes":
                    column_config[col] = st.column_config.NumberColumn(col, format="%d")
                else:
                    column_config[col] = st.column_config.NumberColumn(col, format="%.1f")

        # Display the styled dataframe with full width and no spacing
        st.dataframe(
            styled_df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            #height=min(600, len(df) * 35 + 50)  # Dynamic height based on rows
        )

        # Add performance index metrics explanation
        st.info(f"""
        **Performance Index Metrics**:
        - **Weighted Score**: A combined score based on selected metrics, adjusted by their assigned weights. Higher values indicate stronger overall performance.
        - **Percentile Rank**: Compares a player's score to others, placing them on a 0-100 scale. A higher percentile means better relative performance.

        **{category_name}**: {get_category_description(category_name)}
        """)
    else:
        st.warning("No players found matching the criteria.")

def get_category_description(category_name):
    """Get description for performance categories"""
    descriptions = {
        "Shot Stopper Score": "Measures goalkeeper's ability to make saves and prevent goals through shot-stopping skills.",
        "Distribution Score": "Evaluates goalkeeper's passing and distribution abilities from goal kicks and throws.",
        "Sweeper Score": "Assesses goalkeeper's ability to act as a sweeper, coming off the line and distributing effectively.",
        "Attacking Score": "Measures player's goal-scoring threat and offensive contribution.",
        "Counter Attack Threat Score": "Evaluates player's ability to create and finish counter-attacking opportunities.",
        "Playmaking Score": "Assesses player's creative abilities and chance creation for teammates.",
        "Build Up": "Measures player's contribution to team's build-up play and possession retention.",
        "Ball Retention": "Evaluates player's ability to keep possession and avoid losing the ball.",
        "Defensive Score": "Assesses player's defensive contributions including duels, interceptions, and recoveries.",
        "Versatile Score": "Measures player's all-around contribution across multiple aspects of the game.",
        # Role-based descriptions for Center Forwards
        "Advance Forward": "Evaluates a forward's ability to score goals and create chances through direct attacking play, dribbling, and shooting.",
        "Pressing Forward": "Measures a forward's defensive contribution through pressing, winning duels, and recovering possession in the final third.",
        "Deep-lying Forward": "Assesses a forward's playmaking abilities, focusing on assists, passing accuracy, and creative distribution.",
        "Poacher": "Focuses purely on goal-scoring efficiency and clinical finishing ability in the penalty area.",
        # Role-based descriptions for Center Backs
        "No-Nonsense Centre-Back": "Evaluates a defender's ability to win duels, make recoveries, and provide solid defensive fundamentals.",
        "Central Defender": "Measures a balanced defensive approach combining dueling, interceptions, and basic passing distribution.",
        "Ball Playing Defender": "Assesses a defender's ability to contribute to build-up play through accurate passing while maintaining defensive duties."
    }
    return descriptions.get(category_name, "Custom performance category")

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
        # Create a deep copy of the player data to avoid reference issues
        import copy
        filtered_player = copy.deepcopy(player_stats)

        # Filter match data
        filtered_matches = []
        for match in player_stats.get("match_data", []):
            include_match = True

            # Apply date filter
            if "Date" in match:
                try:
                    # Try multiple date formats
                    date_str = str(match["Date"]).strip()
                    match_date = None

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
                            match_date = datetime.datetime.strptime(date_str, date_format).date()
                            break
                        except (ValueError, TypeError):
                            continue

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

            # Check if this is goalkeeper or outfield player data
            if "saves" in player_stats:  # Goalkeeper data
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

                # Calculate success rates
                total_actions_success_rate = (total_actions_successful / total_actions * 100) if total_actions > 0 else 0
                pass_accuracy = (total_passes_accurate / total_passes * 100) if total_passes > 0 else 0
                long_pass_accuracy = (total_long_passes_accurate / total_long_passes * 100) if total_long_passes > 0 else 0
                cross_accuracy = (total_crosses_accurate / total_crosses * 100) if total_crosses > 0 else 0
                dribble_success_rate = (total_dribbles_successful / total_dribbles * 100) if total_dribbles > 0 else 0
                duel_success_rate = (total_duels_won / total_duels * 100) if total_duels > 0 else 0
                aerial_duel_success_rate = (total_aerial_duels_won / total_aerial_duels * 100) if total_aerial_duels > 0 else 0
                shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0

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

            filtered_data[player_name] = filtered_player
            #print(player_name, filtered_player["minutes"])

    return filtered_data
