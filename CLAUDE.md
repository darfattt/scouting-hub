# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Setup and Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Check system setup and verify all dependencies
python scripts/check_setup.py

# Setup Ollama models (requires Ollama installed)
python scripts/setup_models.py
```

### Building RAG Systems
```bash
# Build all RAG systems (goalkeeper and outfield)
python scripts/build_all_rag.py

# Build only goalkeeper RAG system
python scripts/build_gk_only.py

# Build specific position RAG systems
python scripts/build_goalkeeper_rag.py
python scripts/build_smart_rag.py
```

### Running the Application
```bash
# Start the Streamlit application
streamlit run app.py

# Clear Streamlit cache if needed
python scripts/clear_streamlit_cache.py
```

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m rag          # RAG system tests only
pytest -m "not slow"   # Exclude slow tests

# Run tests with coverage
pytest --cov=src tests/
```

### Development Tools
```bash
# Format code (if black is installed)
black src/ tests/ scripts/

# Lint code (if flake8 is installed)
flake8 src/ tests/ scripts/

# Type checking (if mypy is installed)
mypy src/
```

## Architecture Overview

### Core System Design
This is a football scouting application using RAG (Retrieval-Augmented Generation) with position-specific data processing:

- **Multi-Position RAG**: Separate vector stores for goalkeepers, defenders, midfielders, forwards, and combined outfield players
- **Data Processing**: Unified data processor handling different CSV filename formats and position detection
- **Modular Components**: Streamlit UI components separated by functionality (goalkeeper vs outfield)
- **Optional RAG**: System gracefully degrades if RAG dependencies (FAISS, LangChain, Ollama) are unavailable

### Key Components

#### Data Flow
1. **CSV Data Loading** (`data/stats/`): Supports multiple filename formats
   - Team-based: `"Team - Player Name (Stats).csv"`
   - Player-based: `"Player stats PlayerName.csv"`
   - League data: `data/stats_league/` for additional statistics

2. **Position Detection**: Automatic detection based on statistics columns
   - Goalkeepers: Have goalkeeper-specific metrics (saves, goals against, etc.)
   - Outfield: Classified into defenders, midfielders, forwards based on role

3. **Vector Store Building**: Position-specific FAISS indexes stored in:
   - `vector_store/` (goalkeepers)
   - `vector_store_outfield/` (all outfield)
   - `vector_store_defenders/`, `vector_store_midfielders/`, `vector_store_forwards/`

#### Core Classes
- **DataProcessor** (`src/core/data_processor.py`): Handles all data loading, cleaning, and position classification
- **RAG Systems** (`src/core/rag_system.py`): Position-specific RAG implementations with Ollama integration
- **UI Components** (`src/components/`): Modular Streamlit components for different player types

### Data Requirements
- Player statistics must be in CSV format in `data/stats/`
- League-wide statistics go in `data/stats_league/`
- System automatically detects player positions from statistical columns
- Supports both individual team exports and league-wide data

### External Dependencies
- **Ollama**: Required for RAG functionality with deepseek-r1:8b model
- **FAISS**: Vector similarity search (optional, graceful degradation)
- **LangChain**: RAG pipeline orchestration (optional)

### Testing Strategy
- **Unit tests**: Core data processing and component logic
- **Integration tests**: RAG system building and querying
- **Position-specific tests**: Ensure proper classification and filtering
- **RAG tests**: Vector store building and similarity search

### Development Notes
- All scripts include proper path management for imports
- System handles missing RAG dependencies gracefully
- Separate build scripts allow incremental RAG system updates
- Vector stores can be rebuilt selectively per position