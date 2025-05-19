import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from basic_search import SimpleGoalkeeperSearch

# Set page configuration
st.set_page_config(
    page_title="Goalkeeper Scouting Hub",
    page_icon="⚽",
    layout="wide"
)

# Initialize the search system
@st.cache_resource
def get_search_system():
    search = SimpleGoalkeeperSearch()
    search.build_search_index()
    return search

search = get_search_system()

# Title and description
st.title("⚽ Goalkeeper Scouting Hub")
st.markdown("""
This application helps you analyze and compare goalkeepers based on their performance statistics.
Use the search functionality to find goalkeepers or explore the data directly.
""")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Search", "Player Search", "Player Comparison", "Performance Analysis"])

# Search page
if page == "Search":
    st.header("Goalkeeper Search")
    st.markdown("""
    Search for goalkeepers based on your criteria. The system will find the most relevant goalkeeper profiles.
    
    Example searches:
    - high save percentage
    - few goals conceded
    - good reflexes
    """)
    
    # Query input
    query = st.text_input("Enter your search:")
    
    if query:
        with st.spinner("Searching..."):
            results = search.search(query, top_k=5)
            
        st.subheader("Results")
        if results:
            for i, result in enumerate(results):
                with st.expander(f"{result['player']} (Relevance: {result['score']})"):
                    st.text(result['content'])
                    
                    # Add a button to view detailed stats
                    if st.button(f"View detailed stats for {result['player']}", key=f"view_{i}"):
                        stats = search.get_player_stats(result['player'])
                        
                        # Display key metrics
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Save Percentage", f"{stats['save_percentage']:.1f}%")
                        col2.metric("Goals Conceded/90", f"{stats['goals_conceded_per_90']:.2f}")
                        col3.metric("Total Saves", stats['saves'])
                        col4.metric("Matches Played", stats['matches'])
        else:
            st.write("No results found. Try a different search query.")

# Player Search page
elif page == "Player Search":
    st.header("Player Search")
    
    # Get all player data
    if not search.data_processor.player_data:
        search.data_processor.process_data()
        
    players = list(search.data_processor.player_data.keys())
    players.sort()
    
    # Search filters
    col1, col2 = st.columns(2)
    
    with col1:
        search_name = st.text_input("Search by name:")
        
    with col2:
        team_filter = st.selectbox(
            "Filter by team:",
            ["All Teams"] + sorted(list({search.data_processor.player_data[p]["team"] for p in players}))
        )
    
    # Filter players
    filtered_players = []
    for player in players:
        if search_name.lower() in player.lower() and (team_filter == "All Teams" or search.data_processor.player_data[player]["team"] == team_filter):
            filtered_players.append(player)
    
    # Display results
    st.subheader(f"Results: {len(filtered_players)} players found")
    
    if filtered_players:
        # Create a DataFrame for display
        data = []
        for player in filtered_players:
            stats = search.data_processor.player_data[player]
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
            
            stats = search.data_processor.player_data[selected_player]
            
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

# Player Comparison page
elif page == "Player Comparison":
    st.header("Player Comparison")
    
    # Get all player data
    if not search.data_processor.player_data:
        search.data_processor.process_data()
        
    players = sorted(list(search.data_processor.player_data.keys()))
    
    # Select players to compare
    col1, col2 = st.columns(2)
    
    with col1:
        player1 = st.selectbox("Select first player:", players, index=0)
        
    with col2:
        # Filter out the first player from the second dropdown
        player2_options = [p for p in players if p != player1]
        player2 = st.selectbox("Select second player:", player2_options, index=0)
    
    if player1 and player2:
        # Get comparison data
        comparison = search.compare_players(player1, player2)
        
        if "error" in comparison:
            st.error(comparison["error"])
        else:
            st.subheader(f"Comparison: {player1} vs {player2}")
            
            # Display metrics side by side
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(player1)
                st.metric("Matches", comparison["metrics"]["matches"][0])
                st.metric("Minutes", comparison["metrics"]["minutes"][0])
                st.metric("Goals Conceded", comparison["metrics"]["conceded_goals"][0])
                st.metric("Saves", comparison["metrics"]["saves"][0])
                st.metric("Save Percentage", f"{comparison['metrics']['save_percentage'][0]:.1f}%")
                st.metric("Goals Conceded/90", f"{comparison['metrics']['goals_conceded_per_90'][0]:.2f}")
                
            with col2:
                st.subheader(player2)
                st.metric("Matches", comparison["metrics"]["matches"][1])
                st.metric("Minutes", comparison["metrics"]["minutes"][1])
                st.metric("Goals Conceded", comparison["metrics"]["conceded_goals"][1])
                st.metric("Saves", comparison["metrics"]["saves"][1])
                st.metric("Save Percentage", f"{comparison['metrics']['save_percentage'][1]:.1f}%")
                st.metric("Goals Conceded/90", f"{comparison['metrics']['goals_conceded_per_90'][1]:.2f}")
            
            # Create radar chart for comparison
            st.subheader("Performance Comparison")
            
            # Prepare data for radar chart
            metrics = ["Save %", "Goals Conceded/90", "Saves/Match", "Minutes/Match"]
            
            # Calculate normalized values (0-1 scale)
            p1_save_pct = comparison["metrics"]["save_percentage"][0] / 100
            p2_save_pct = comparison["metrics"]["save_percentage"][1] / 100
            
            # For goals conceded, lower is better, so invert the scale
            max_gc90 = max(comparison["metrics"]["goals_conceded_per_90"])
            p1_gc90 = 1 - (comparison["metrics"]["goals_conceded_per_90"][0] / max_gc90 if max_gc90 > 0 else 0)
            p2_gc90 = 1 - (comparison["metrics"]["goals_conceded_per_90"][1] / max_gc90 if max_gc90 > 0 else 0)
            
            p1_saves_per_match = comparison["metrics"]["saves"][0] / comparison["metrics"]["matches"][0] if comparison["metrics"]["matches"][0] > 0 else 0
            p2_saves_per_match = comparison["metrics"]["saves"][1] / comparison["metrics"]["matches"][1] if comparison["metrics"]["matches"][1] > 0 else 0
            max_saves_per_match = max(p1_saves_per_match, p2_saves_per_match)
            p1_saves_per_match = p1_saves_per_match / max_saves_per_match if max_saves_per_match > 0 else 0
            p2_saves_per_match = p2_saves_per_match / max_saves_per_match if max_saves_per_match > 0 else 0
            
            p1_mins_per_match = comparison["metrics"]["minutes"][0] / comparison["metrics"]["matches"][0] if comparison["metrics"]["matches"][0] > 0 else 0
            p2_mins_per_match = comparison["metrics"]["minutes"][1] / comparison["metrics"]["matches"][1] if comparison["metrics"]["matches"][1] > 0 else 0
            max_mins_per_match = max(p1_mins_per_match, p2_mins_per_match)
            p1_mins_per_match = p1_mins_per_match / max_mins_per_match if max_mins_per_match > 0 else 0
            p2_mins_per_match = p2_mins_per_match / max_mins_per_match if max_mins_per_match > 0 else 0
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            
            # Number of variables
            N = len(metrics)
            
            # Angle of each axis
            angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Player 1 data
            values1 = [p1_save_pct, p1_gc90, p1_saves_per_match, p1_mins_per_match]
            values1 += values1[:1]  # Close the loop
            
            # Player 2 data
            values2 = [p2_save_pct, p2_gc90, p2_saves_per_match, p2_mins_per_match]
            values2 += values2[:1]  # Close the loop
            
            # Draw the chart
            ax.plot(angles, values1, linewidth=1, linestyle='solid', label=player1)
            ax.fill(angles, values1, alpha=0.1)
            
            ax.plot(angles, values2, linewidth=1, linestyle='solid', label=player2)
            ax.fill(angles, values2, alpha=0.1)
            
            # Add labels
            plt.xticks(angles[:-1], metrics)
            
            # Add legend
            plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            
            st.pyplot(fig)

# Performance Analysis page
elif page == "Performance Analysis":
    st.header("Performance Analysis")
    
    # Get all player data
    if not search.data_processor.player_data:
        search.data_processor.process_data()
        
    players = list(search.data_processor.player_data.keys())
    
    # Create a DataFrame for analysis
    data = []
    for player in players:
        stats = search.data_processor.player_data[player]
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

# Footer
st.markdown("---")
st.markdown("Goalkeeper Scouting Hub | Simple Search System")
