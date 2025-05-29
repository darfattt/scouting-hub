import streamlit as st
from rag_system import GoalkeeperRAG, ForwardRAG, MidfielderRAG, DefenderRAG, OutfieldRAG
from app_components import (
    render_player_search,
    render_player_comparison,
    add_global_filters,
    filter_player_data
)
from outfield_components import render_outfield_player_comparison, render_outfield_player_search

# Set page configuration
st.set_page_config(
    page_title="Football Scouting Hub - Multi Position",
    page_icon="⚽",
    layout="wide"
)

# Initialize RAG systems for different positions
@st.cache_resource
def get_rag_systems():
    """Initialize and cache RAG systems for all positions."""
    systems = {}

    # Initialize goalkeeper RAG
    try:
        systems['Goalkeepers'] = GoalkeeperRAG()
        systems['Goalkeepers'].build_vector_store()
    except Exception as e:
        st.error(f"Failed to initialize Goalkeeper RAG: {e}")
        systems['Goalkeepers'] = None

    # Initialize outfield RAG systems (these may fail if no outfield data)
    outfield_systems = [
        ('All Outfield', OutfieldRAG),
        ('Forwards', ForwardRAG),
        ('Midfielders', MidfielderRAG),
        ('Defenders', DefenderRAG)
    ]

    for name, rag_class in outfield_systems:
        try:
            systems[name] = rag_class()
            systems[name].build_vector_store()
        except Exception as e:
            # This is expected if no outfield data is available
            print(f"Note: {name} RAG not available (no data): {e}")
            systems[name] = None

    return systems

# Get all RAG systems
rag_systems = get_rag_systems()

# Title and description
st.title("⚽ Football Scouting Hub - Multi Position")
st.markdown("""
This application helps you analyze and compare players across all positions based on their performance statistics.
Use the AI assistant to ask questions about players or explore the data directly.
""")

# Sidebar
st.sidebar.title("Navigation & Settings")

# Position selection - only show available systems
available_positions = [pos for pos, system in rag_systems.items() if system is not None]

if not available_positions:
    st.error("No RAG systems are available. Please check your data and Ollama setup.")
    st.stop()

position_type = st.sidebar.selectbox(
    "Select Player Position:",
    available_positions,
    index=0,
    help="Choose the type of players to analyze"
)

# Get the appropriate RAG system
rag = rag_systems[position_type]

if rag is None:
    st.error(f"The {position_type} RAG system is not available.")
    st.stop()

# Page selection
page = st.sidebar.radio("Select a page", ["AI Assistant", "Player Search", "Player Comparison", "Player Performance", "Player Search Profiler", "Attribute Analysis"])

# Add global filters to the sidebar
filters = add_global_filters()

# Apply filters to get filtered player data
filtered_data = filter_player_data(rag, filters)

# AI Assistant page
if page == "AI Assistant":
    st.header(f"AI Scout Assistant - {position_type}")

    # Position-specific example questions
    if position_type == "Goalkeepers":
        example_questions = [
            "Who is the best goalkeeper in terms of save percentage?",
            "Which goalkeeper concedes the fewest goals per 90 minutes?",
            "How does [Player Name] perform compared to other goalkeepers?"
        ]
        query_placeholder = "Ask a question about goalkeepers..."
    elif position_type == "Forwards":
        example_questions = [
            "Who is the top scorer among forwards?",
            "Which forward has the best shot accuracy?",
            "Who creates the most assists among forwards?"
        ]
        query_placeholder = "Ask a question about forwards..."
    elif position_type == "Midfielders":
        example_questions = [
            "Who has the highest pass accuracy among midfielders?",
            "Which midfielder creates the most assists?",
            "Who wins the most duels in midfield?"
        ]
        query_placeholder = "Ask a question about midfielders..."
    elif position_type == "Defenders":
        example_questions = [
            "Who makes the most interceptions among defenders?",
            "Which defender wins the most aerial duels?",
            "Who has the best defensive statistics?"
        ]
        query_placeholder = "Ask a question about defenders..."
    else:  # All Outfield
        example_questions = [
            "Who is the most versatile outfield player?",
            "Which player contributes most to both attack and defense?",
            "Who has the best overall statistics?"
        ]
        query_placeholder = "Ask a question about outfield players..."

    st.markdown(f"""
    Ask questions about {position_type.lower()} and get AI-powered insights based on the data.

    Example questions:
    """ + "\n".join([f"    - {q}" for q in example_questions]))

    # Query input
    query = st.text_input(f"Ask a question about {position_type.lower()}:", placeholder=query_placeholder)

    if query:
        with st.spinner("Analyzing data..."):
            result = rag.query(query)

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Sources")
        for i, doc in enumerate(result["source_documents"]):
            with st.expander(f"Source {i+1}: {doc.metadata.get('player', 'Unknown')}"):
                st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)

# Player Search page
elif page == "Player Search":
    if position_type == "Goalkeepers":
        render_player_search(rag, filtered_data)
    else:
        render_outfield_player_search(rag, filtered_data, position_type)

# Player Comparison page
elif page == "Player Comparison":
    if position_type == "Goalkeepers":
        render_player_comparison(rag, filtered_data)
    else:
        render_outfield_player_comparison(rag, filtered_data, position_type)

# Player Performance page
elif page == "Player Performance":
    from performance_components import render_player_performance
    render_player_performance(rag, filtered_data, position_type)

# Player Search Profiler page
elif page == "Player Search Profiler":
    from profiler_components import render_player_search_profiler
    render_player_search_profiler(rag, filtered_data, position_type)

elif page == "Attribute Analysis":
    from player_screen_components import render_player_screen
    render_player_screen(rag, filtered_data, position_type)

# Footer
st.markdown("---")
st.markdown(f"Football Scouting Hub - {position_type} Analysis | Powered by Ollama and LangChain")
