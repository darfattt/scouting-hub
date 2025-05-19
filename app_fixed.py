import streamlit as st
from basic_search import SimpleGoalkeeperSearch
from app_components import (
    render_player_search,
    render_player_comparison,
    render_performance_analysis,
    add_global_filters,
    filter_player_data
)

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

# Add global filters to the sidebar
filters = add_global_filters()

# Apply filters to get filtered player data
filtered_data = filter_player_data(search, filters)

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
    render_player_search(search, filtered_data)

# Player Comparison page
elif page == "Player Comparison":
    render_player_comparison(search, filtered_data)

# Performance Analysis page
elif page == "Performance Analysis":
    render_performance_analysis(search, filtered_data)

# Footer
st.markdown("---")
st.markdown("Goalkeeper Scouting Hub | Simple Search System")
