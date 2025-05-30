# Football Scouting RAG System

A comprehensive football scouting application using RAG (Retrieval-Augmented Generation) with Ollama for intelligent player analysis and comparison.

## 🚀 Features

- **Player Search**: Search and filter players by various criteria
- **Player Comparison**: Compare up to 3 players with detailed statistics  
- **Performance Analysis**: Analyze player performance with AI insights
- **Attribute Analysis**: Filter players by statistical ranges with percentile ranking
- **Player Search Profiler**: Advanced player profiling with custom metrics
- **RAG Integration**: Uses Ollama with deepseek-r1:8b model for intelligent responses

## 📁 Project Structure

```
rag_gk/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # Project documentation
│
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── components/                # UI components
│   │   ├── __init__.py
│   │   ├── app_components.py      # Main app components (GK)
│   │   ├── outfield_components.py # Outfield player components
│   │   ├── performance_components.py # Performance analysis
│   │   ├── player_screen_components.py # Attribute analysis
│   │   └── profiler_components.py # Player profiler
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── data_processor.py      # Data processing logic
│   │   ├── rag_system.py         # RAG implementation
│   │   └── search/               # Search modules
│   │       ├── __init__.py
│   │       ├── basic_search.py
│   │       └── simple_search.py
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── data/                          # Data directory
│   ├── stats/                     # Player statistics CSV files
│   └── stats_league/             # League statistics
│
├── tests/                         # Test files
│   ├── __init__.py
│   ├── test_data_processor.py
│   ├── test_rag_system.py
│   └── test_components.py
│
├── scripts/                       # Build and utility scripts
│   ├── build_all_rag.py
│   ├── build_gk_only.py
│   ├── build_goalkeeper_rag.py
│   ├── build_smart_rag.py
│   ├── rebuild_all_rag.py
│   ├── setup_models.py
│   └── check_setup.py
│
├── docs/                          # Documentation
│   ├── setup/
│   ├── features/
│   └── troubleshooting/
│
└── storage/                       # Generated files and models
    ├── vector_store/
    ├── vector_store_outfield/
    ├── vector_store_defenders/
    ├── vector_store_midfielders/
    ├── vector_store_forwards/
    ├── player_data.pkl
    └── tfidf_model.pkl
```

## 🛠️ Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install and setup Ollama:**
```bash
# Install Ollama (visit https://ollama.ai for installation instructions)
ollama pull deepseek-r1:8b
```

3. **Build the RAG system:**
```bash
python scripts/build_all_rag.py
```

4. **Run the application:**
```bash
streamlit run app.py
```

## 📊 Data Structure

Place your player statistics CSV files in the `data/stats/` directory. The system supports both goalkeeper and outfield player data with automatic position detection.

## 🎯 Usage

1. **Global Filters**: Set date range and competition filters in the sidebar
2. **Player Search**: Find players based on position and statistics
3. **Player Comparison**: Compare multiple players side-by-side with role analysis
4. **Performance Analysis**: Get AI-powered insights on player performance
5. **Attribute Analysis**: Filter players by statistical ranges with color-coded percentiles
6. **Player Search Profiler**: Advanced profiling with preset categories and custom metrics

## 🧪 Testing

Run tests using pytest:
```bash
pytest tests/
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory covering setup, features, and troubleshooting.
