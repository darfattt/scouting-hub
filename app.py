import streamlit as st
from rag_system import GoalkeeperRAG
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

# Initialize the RAG system
@st.cache_resource
def get_rag_system():
    rag = GoalkeeperRAG()
    rag.build_vector_store()
    return rag

rag = get_rag_system()

# Title and description
st.title("⚽ Goalkeeper Scouting Hub")
st.markdown("""
This application helps you analyze and compare goalkeepers based on their performance statistics.
Use the AI assistant to ask questions about goalkeepers or explore the data directly.
""")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["AI Assistant", "Player Search", "Player Comparison", "Performance Analysis"])

# Add global filters to the sidebar
filters = add_global_filters()

# Apply filters to get filtered player data
filtered_data = filter_player_data(rag, filters)

# AI Assistant page
if page == "AI Assistant":
    st.header("AI Goalkeeper Scout Assistant")
    st.markdown("""
    Ask questions about goalkeepers and get AI-powered insights based on the data.

    Example questions:
    - Who is the best goalkeeper in terms of save percentage?
    - Which goalkeeper concedes the fewest goals per 90 minutes?
    - How does Teja Paku Alam perform compared to other goalkeepers?
    """)

    # Query input
    query = st.text_input("Ask a question about goalkeepers:")

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
    render_player_search(rag, filtered_data)

# Player Comparison page
elif page == "Player Comparison":
    render_player_comparison(rag, filtered_data)

# Performance Analysis page
elif page == "Performance Analysis":
    render_performance_analysis(rag, filtered_data)

# Footer
st.markdown("---")
st.markdown("Goalkeeper Scouting Hub | Powered by Ollama and LangChain")
