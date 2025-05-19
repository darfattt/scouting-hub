import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from typing import Any, Dict, List, Tuple, Optional

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

    # Number of players to compare (2 or 3)
    num_players = st.radio("Number of players to compare:", [2, 3], horizontal=True)

    # Select players
    selected_players = []
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
    player3 = None
    if num_players == 3:
        player3 = st.selectbox("Select third player:", remaining_players, index=0, key="player3")
        selected_players.append(player3)

    # Get player stats
    player_stats = []
    for player in selected_players:
        stats = player_data.get(player)
        if stats:
            player_stats.append(stats)
        else:
            st.error(f"Player {player} not found")
            return

    # Create comparison data
    comparison = {
        "players": selected_players,
        "metrics": {
            "matches": [stats["matches"] for stats in player_stats],
            "minutes": [stats["minutes"] for stats in player_stats],
            "conceded_goals": [stats["conceded_goals"] for stats in player_stats],
            "saves": [stats["saves"] for stats in player_stats],
            "shots_against": [stats["shots_against"] for stats in player_stats],
            "save_percentage": [stats["save_percentage"] for stats in player_stats],
            "goals_conceded_per_90": [stats["goals_conceded_per_90"] for stats in player_stats]
        }
    }

    # Display comparison title
    if num_players == 2:
        st.subheader(f"Comparison: {player1} vs {player2}")
    else:
        st.subheader(f"Comparison: {player1} vs {player2} vs {player3}")

    # Display metrics side by side
    cols = st.columns(num_players)

    for i, (col, player) in enumerate(zip(cols, selected_players)):
        with col:
            st.subheader(player)
            st.metric("Matches", comparison["metrics"]["matches"][i])
            st.metric("Minutes", comparison["metrics"]["minutes"][i])
            st.metric("Goals Conceded", comparison["metrics"]["conceded_goals"][i])
            st.metric("Saves", comparison["metrics"]["saves"][i])
            st.metric("Save Percentage", f"{comparison['metrics']['save_percentage'][i]:.1f}%")
            st.metric("Goals Conceded/90", f"{comparison['metrics']['goals_conceded_per_90'][i]:.2f}")

    # Create radar chart for comparison
    st.subheader("Performance Comparison")

    # Prepare data for radar chart
    metrics = ["Save %", "Goals Conceded/90", "Saves/Match", "Minutes/Match"]

    # Number of variables
    N = len(metrics)

    # Angle of each axis
    angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
    angles += angles[:1]  # Close the loop

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # Colors for different players
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    # Process each player's data
    for i, player in enumerate(selected_players):
        # Calculate normalized values (0-1 scale)
        save_pct = comparison["metrics"]["save_percentage"][i] / 100

        # For goals conceded, lower is better, so invert the scale
        max_gc90 = max(comparison["metrics"]["goals_conceded_per_90"])
        gc90 = 1 - (comparison["metrics"]["goals_conceded_per_90"][i] / max_gc90 if max_gc90 > 0 else 0)

        # Saves per match
        saves_per_match = comparison["metrics"]["saves"][i] / comparison["metrics"]["matches"][i] if comparison["metrics"]["matches"][i] > 0 else 0

        # Minutes per match
        mins_per_match = comparison["metrics"]["minutes"][i] / comparison["metrics"]["matches"][i] if comparison["metrics"]["matches"][i] > 0 else 0

        # Normalize saves per match and minutes per match across all players
        max_saves_per_match = max([comparison["metrics"]["saves"][j] / comparison["metrics"]["matches"][j]
                                  if comparison["metrics"]["matches"][j] > 0 else 0
                                  for j in range(len(selected_players))])

        max_mins_per_match = max([comparison["metrics"]["minutes"][j] / comparison["metrics"]["matches"][j]
                                 if comparison["metrics"]["matches"][j] > 0 else 0
                                 for j in range(len(selected_players))])

        saves_per_match_norm = saves_per_match / max_saves_per_match if max_saves_per_match > 0 else 0
        mins_per_match_norm = mins_per_match / max_mins_per_match if max_mins_per_match > 0 else 0

        # Create values array
        values = [save_pct, gc90, saves_per_match_norm, mins_per_match_norm]
        values += values[:1]  # Close the loop

        # Draw the chart
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=player, color=colors[i])
        ax.fill(angles, values, alpha=0.1, color=colors[i])

    # Add labels
    plt.xticks(angles[:-1], metrics, size=12)

    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

    # Add grid
    ax.grid(True)

    st.pyplot(fig)

    # Add a table comparison
    st.subheader("Detailed Comparison")

    # Create a DataFrame for the comparison
    comparison_df = pd.DataFrame({
        "Metric": ["Matches", "Minutes", "Goals Conceded", "Saves", "Shots Against",
                  "Save Percentage", "Goals Conceded/90"]
    })

    # Add data for each player
    for i, player in enumerate(selected_players):
        comparison_df[player] = [
            comparison["metrics"]["matches"][i],
            comparison["metrics"]["minutes"][i],
            comparison["metrics"]["conceded_goals"][i],
            comparison["metrics"]["saves"][i],
            comparison["metrics"]["shots_against"][i],
            f"{comparison['metrics']['save_percentage'][i]:.1f}%",
            f"{comparison['metrics']['goals_conceded_per_90'][i]:.2f}"
        ]

    # Display the comparison table
    st.dataframe(comparison_df, use_container_width=True)

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

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df["Save %"], bins=20, kde=True, ax=ax)
        ax.set_xlabel("Save Percentage (%)")
        ax.set_ylabel("Number of Goalkeepers")
        ax.set_title("Distribution of Goalkeeper Save Percentages")

        st.pyplot(fig)

        # Show top performers
        st.subheader("Top 5 Goalkeepers by Save Percentage")
        top_save_pct = df.sort_values("Save %", ascending=False).head(5)
        st.dataframe(top_save_pct[["Player", "Team", "Save %", "Matches", "Saves", "Shots Against"]])

    elif analysis_type == "Goals Conceded per 90 Distribution":
        st.subheader("Goals Conceded per 90 Minutes Distribution")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df["Goals Conceded/90"], bins=20, kde=True, ax=ax)
        ax.set_xlabel("Goals Conceded per 90 Minutes")
        ax.set_ylabel("Number of Goalkeepers")
        ax.set_title("Distribution of Goals Conceded per 90 Minutes")

        st.pyplot(fig)

        # Show top performers (lowest goals conceded)
        st.subheader("Top 5 Goalkeepers by Lowest Goals Conceded per 90")
        top_gc90 = df.sort_values("Goals Conceded/90").head(5)
        st.dataframe(top_gc90[["Player", "Team", "Goals Conceded/90", "Matches", "Goals Conceded", "Minutes"]])

    elif analysis_type == "Saves vs. Goals Conceded":
        st.subheader("Saves vs. Goals Conceded")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df, x="Saves", y="Goals Conceded", size="Matches", hue="Save %", palette="viridis", ax=ax)
        ax.set_xlabel("Total Saves")
        ax.set_ylabel("Total Goals Conceded")
        ax.set_title("Relationship Between Saves and Goals Conceded")

        st.pyplot(fig)

        # Show the data
        st.dataframe(df.sort_values("Save %", ascending=False)[["Player", "Team", "Saves", "Goals Conceded", "Save %", "Matches"]])

    elif analysis_type == "Top Performers":
        st.subheader("Top Performers Analysis")

        # Create a composite score (higher save %, lower goals conceded/90)
        df["Composite Score"] = df["Save %"] / 100 - df["Goals Conceded/90"] / 3

        # Show top performers by composite score
        st.subheader("Top 10 Goalkeepers (Overall Performance)")
        top_overall = df.sort_values("Composite Score", ascending=False).head(10)
        st.dataframe(top_overall[["Player", "Team", "Save %", "Goals Conceded/90", "Matches", "Composite Score"]])

        # Visualize top performers
        fig, ax = plt.subplots(figsize=(10, 6))
        top_10_players = top_overall["Player"].tolist()
        top_10_df = df[df["Player"].isin(top_10_players)]

        sns.scatterplot(
            data=top_10_df,
            x="Goals Conceded/90",
            y="Save %",
            size="Matches",
            hue="Player",
            ax=ax
        )
        ax.set_xlabel("Goals Conceded per 90 Minutes")
        ax.set_ylabel("Save Percentage (%)")
        ax.set_title("Top 10 Goalkeepers: Save % vs. Goals Conceded/90")

        # Invert x-axis (lower goals conceded is better)
        ax.invert_xaxis()

        st.pyplot(fig)
