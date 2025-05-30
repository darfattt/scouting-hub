import streamlit as st
import pandas as pd

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

    # Weight adjustment section
    st.subheader("⚖️ Customize Metrics & Weights")
    st.markdown("**Adjust the weights for each metric in the selected category:**")

    category_weights = performance_categories[selected_category].copy()

    # Create weight adjustment interface
    weight_cols = st.columns(2)
    col_idx = 0

    for stat_key, stat_info in category_weights.items():
        with weight_cols[col_idx % 2]:
            new_weight = st.slider(
                f"{stat_info['name']} Weight",
                min_value=0.0,
                max_value=1.0,
                value=stat_info['weight'],
                step=0.05,
                key=f"weight_{stat_key}",
                help=f"Weight for {stat_info['name']} ({'negative' if stat_info['negative'] else 'positive'} stat)"
            )
            category_weights[stat_key]['weight'] = new_weight
        col_idx += 1

    # Calculate and display results
    st.markdown("---")
    if st.button("🚀 Calculate Performance Scores", type="primary", use_container_width=True):
        calculate_and_display_scores(
            player_data,
            players,
            category_weights,
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

    # Apply per 90 calculation if enabled
    if per_90_mode and stat_key != "minutes":
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

        # Configure Weighted Score as progress column
        max_score = df["Weighted Score"].max()
        column_config["Weighted Score"] = st.column_config.ProgressColumn(
            "Weighted Score",
            help="Performance score based on weighted metrics",
            min_value=0,
            max_value=max_score,
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

        # Display the dataframe with full width and no spacing
        st.dataframe(
            df,
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
        "Versatile Score": "Measures player's all-around contribution across multiple aspects of the game."
    }
    return descriptions.get(category_name, "Custom performance category")
