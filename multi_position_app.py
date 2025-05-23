import streamlit as st
from rag_system import GoalkeeperRAG, ForwardRAG, MidfielderRAG, DefenderRAG, OutfieldRAG
from app_components import add_global_filters, filter_player_data, render_player_comparison
from outfield_components import render_outfield_player_comparison

def main():
    """
    Main application for multi-position football scouting hub.
    """
    st.set_page_config(
        page_title="Football Scouting Hub - Multi Position",
        page_icon="⚽",
        layout="wide"
    )
    
    st.title("⚽ Football Scouting Hub - Multi Position Analysis")
    st.markdown("Advanced player analysis and comparison across all positions")
    
    # Sidebar for position selection and global filters
    st.sidebar.title("Navigation & Filters")
    
    # Position selection
    position_type = st.sidebar.selectbox(
        "Select Player Position:",
        ["Goalkeepers", "All Outfield", "Forwards", "Midfielders", "Defenders"],
        index=0
    )
    
    # Global filters
    filters = add_global_filters()
    
    # Initialize RAG system based on position selection
    rag_system = None
    
    try:
        if position_type == "Goalkeepers":
            st.sidebar.info("🥅 Analyzing Goalkeeper Data")
            rag_system = GoalkeeperRAG()
            
        elif position_type == "All Outfield":
            st.sidebar.info("🏃 Analyzing All Outfield Players")
            rag_system = OutfieldRAG()
            
        elif position_type == "Forwards":
            st.sidebar.info("⚽ Analyzing Forward Players")
            rag_system = ForwardRAG()
            
        elif position_type == "Midfielders":
            st.sidebar.info("🎯 Analyzing Midfielder Players")
            rag_system = MidfielderRAG()
            
        elif position_type == "Defenders":
            st.sidebar.info("🛡️ Analyzing Defender Players")
            rag_system = DefenderRAG()
        
        # Build vector store
        with st.spinner(f"Loading {position_type} data..."):
            rag_system.build_vector_store()
        
        # Get and filter player data
        if position_type == "Goalkeepers":
            all_player_data = rag_system.data_processor.player_data
        else:
            all_player_data = rag_system.data_processor.player_data
        
        if not all_player_data:
            st.error(f"No {position_type.lower()} data found. Please check your data directory.")
            return
        
        # Apply global filters
        filtered_data = filter_player_data(all_player_data, filters)
        
        # Store filtered data in session state for use in components
        st.session_state.filtered_data = filtered_data
        
        # Display main content based on position type
        if position_type == "Goalkeepers":
            render_goalkeeper_analysis(rag_system, filtered_data)
        else:
            render_outfield_analysis(rag_system, filtered_data, position_type)
            
    except Exception as e:
        st.error(f"Error initializing {position_type} analysis: {str(e)}")
        st.info("Please ensure you have the correct data files in the data/stats directory.")


def render_goalkeeper_analysis(rag, filtered_data):
    """
    Render goalkeeper-specific analysis.
    """
    # Navigation tabs for goalkeeper analysis
    tab1, tab2, tab3 = st.tabs(["🔍 Player Search", "⚖️ Player Comparison", "🤖 AI Analysis"])
    
    with tab1:
        st.header("Goalkeeper Search")
        render_goalkeeper_search(rag, filtered_data)
    
    with tab2:
        render_player_comparison(rag, filtered_data)
    
    with tab3:
        st.header("AI-Powered Goalkeeper Analysis")
        render_ai_analysis(rag)


def render_outfield_analysis(rag, filtered_data, position_type):
    """
    Render outfield player analysis.
    """
    # Navigation tabs for outfield analysis
    tab1, tab2, tab3 = st.tabs(["🔍 Player Search", "⚖️ Player Comparison", "🤖 AI Analysis"])
    
    with tab1:
        st.header(f"{position_type} Search")
        render_outfield_search(rag, filtered_data, position_type)
    
    with tab2:
        render_outfield_player_comparison(rag, filtered_data, position_type)
    
    with tab3:
        st.header(f"AI-Powered {position_type} Analysis")
        render_ai_analysis(rag)


def render_goalkeeper_search(rag, filtered_data):
    """
    Render goalkeeper search interface.
    """
    st.subheader("Search Goalkeepers")
    
    if not filtered_data:
        st.warning("No goalkeeper data available.")
        return
    
    # Display basic stats
    st.metric("Total Goalkeepers", len(filtered_data))
    
    # Search and filter options
    search_term = st.text_input("Search by name:", placeholder="Enter goalkeeper name...")
    
    # Display results
    if search_term:
        matching_players = [name for name in filtered_data.keys() 
                          if search_term.lower() in name.lower()]
        
        if matching_players:
            for player in matching_players:
                with st.expander(f"🥅 {player}"):
                    stats = filtered_data[player]
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Matches", stats.get('matches', 0))
                        st.metric("Minutes", stats.get('minutes', 0))
                    
                    with col2:
                        st.metric("Goals Conceded", stats.get('conceded_goals', 0))
                        st.metric("Saves", stats.get('saves', 0))
                    
                    with col3:
                        st.metric("Save %", f"{stats.get('save_percentage', 0):.1f}%")
                        st.metric("Goals/90", f"{stats.get('goals_conceded_per_90', 0):.2f}")
        else:
            st.info("No goalkeepers found matching your search.")
    else:
        # Show all players
        st.write("**All Goalkeepers:**")
        for player in sorted(filtered_data.keys()):
            st.write(f"• {player}")


def render_outfield_search(rag, filtered_data, position_type):
    """
    Render outfield player search interface.
    """
    st.subheader(f"Search {position_type}")
    
    if not filtered_data:
        st.warning(f"No {position_type.lower()} data available.")
        return
    
    # Display basic stats
    st.metric(f"Total {position_type}", len(filtered_data))
    
    # Search and filter options
    search_term = st.text_input("Search by name:", placeholder=f"Enter {position_type.lower()} name...")
    
    # Display results
    if search_term:
        matching_players = [name for name in filtered_data.keys() 
                          if search_term.lower() in name.lower()]
        
        if matching_players:
            for player in matching_players:
                with st.expander(f"⚽ {player}"):
                    stats = filtered_data[player]
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Matches", stats.get('matches', 0))
                        st.metric("Minutes", stats.get('minutes', 0))
                    
                    with col2:
                        st.metric("Goals", stats.get('goals', 0))
                        st.metric("Assists", stats.get('assists', 0))
                    
                    with col3:
                        st.metric("Pass Accuracy", f"{stats.get('pass_accuracy', 0):.1f}%")
                        st.metric("Position", stats.get('position', 'Unknown'))
        else:
            st.info(f"No {position_type.lower()} found matching your search.")
    else:
        # Show all players
        st.write(f"**All {position_type}:**")
        for player in sorted(filtered_data.keys()):
            st.write(f"• {player}")


def render_ai_analysis(rag):
    """
    Render AI-powered analysis interface.
    """
    st.subheader("Ask AI About Players")
    
    # Query input
    question = st.text_area(
        "Ask a question about the players:",
        placeholder="e.g., Who is the best goalkeeper in terms of save percentage?",
        height=100
    )
    
    if st.button("🤖 Get AI Analysis", type="primary"):
        if question.strip():
            with st.spinner("Analyzing..."):
                try:
                    result = rag.query(question)
                    
                    st.subheader("AI Response:")
                    st.write(result["answer"])
                    
                    if result.get("source_documents"):
                        with st.expander("📚 Source Information"):
                            for i, doc in enumerate(result["source_documents"]):
                                st.write(f"**Source {i+1}:**")
                                st.write(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
                                st.write("---")
                                
                except Exception as e:
                    st.error(f"Error getting AI response: {str(e)}")
        else:
            st.warning("Please enter a question.")


if __name__ == "__main__":
    main()
