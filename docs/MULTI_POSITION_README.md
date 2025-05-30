# Multi-Position Football Scouting Hub

## Overview

This enhanced football scouting hub now supports analysis across all player positions with specialized RAG (Retrieval-Augmented Generation) systems for different player types.

## New RAG Classes

### 1. GoalkeeperRAG (Existing)
- **Purpose**: Specialized for goalkeeper analysis
- **Data**: Goalkeeper-specific statistics (saves, goals conceded, etc.)
- **Vector Store**: `vector_store` (existing)

### 2. OutfieldRAG (New Base Class)
- **Purpose**: Base class for all outfield players
- **Data**: Outfield player statistics (goals, assists, passes, etc.)
- **Vector Store**: `vector_store_outfield`
- **Features**: Can filter by position or analyze all outfield players

### 3. ForwardRAG (New Specialized Class)
- **Purpose**: Specialized for forward/striker analysis
- **Data**: Forward-specific statistics and analysis
- **Vector Store**: `vector_store_forwards`
- **Focus**: Goals, shots, finishing, attacking play

### 4. MidfielderRAG (New Specialized Class)
- **Purpose**: Specialized for midfielder analysis
- **Data**: Midfielder-specific statistics and analysis
- **Vector Store**: `vector_store_midfielders`
- **Focus**: Passing, assists, ball control, transitions

### 5. DefenderRAG (New Specialized Class)
- **Purpose**: Specialized for defender analysis
- **Data**: Defender-specific statistics and analysis
- **Vector Store**: `vector_store_defenders`
- **Focus**: Interceptions, duels, recoveries, defensive actions

## Data Structure

### Outfield Player Statistics
The new system handles these statistics for outfield players:

```
- Match, Competition, Date, Position
- Minutes played, Total actions, Total actions successful
- Goals, Assists, Shots, Shots on target, xG
- Passes, Passes accurate, Long passes, Long passes accurate
- Crosses, Crosses accurate
- Dribbles, Dribbles successful
- Duels, Duels won, Aerial duels, Aerial duels won
- Interceptions, Losses, Losses own half
- Recoveries, Recoveries opp. half
- Yellow card, Red card (minutes when received)
```

### Special Handling
- **Yellow/Red Cards**: Stored as minutes when received, converted to counts
- **Per 90 Statistics**: All counting stats can be normalized per 90 minutes
- **Position Filtering**: Automatic filtering by position type

## File Structure

```
├── rag_system.py              # All RAG classes (GK + Outfield)
├── data_processor.py          # Data processors for both GK and outfield
├── app_components.py          # Goalkeeper comparison components (existing)
├── outfield_components.py     # Outfield player comparison components (new)
├── multi_position_app.py      # Main multi-position application
├── app.py                     # Original goalkeeper-only app (existing)
└── data/
    └── stats/                 # CSV files for all player types
```

## Usage Examples

### 1. Initialize Different RAG Systems

```python
from rag_system import GoalkeeperRAG, ForwardRAG, MidfielderRAG, DefenderRAG, OutfieldRAG

# Goalkeeper analysis
gk_rag = GoalkeeperRAG()

# Forward analysis
forward_rag = ForwardRAG()

# Midfielder analysis
midfielder_rag = MidfielderRAG()

# Defender analysis
defender_rag = DefenderRAG()

# All outfield players
outfield_rag = OutfieldRAG()
```

### 2. Query Examples

```python
# Goalkeeper queries
gk_result = gk_rag.query("Who has the highest save percentage?")

# Forward queries
forward_result = forward_rag.query("Which forward scores the most goals per 90 minutes?")

# Midfielder queries
mid_result = midfielder_rag.query("Who is the best playmaker in terms of assists?")

# Defender queries
def_result = defender_rag.query("Which defender wins the most duels?")
```

### 3. Player Comparison

```python
# Compare forwards
comparison = forward_rag.compare_players("Player A", "Player B")

# Compare midfielders
comparison = midfielder_rag.compare_players("Player C", "Player D")
```

## Running the Applications

### Multi-Position App (New)
```bash
streamlit run multi_position_app.py
```

### Goalkeeper-Only App (Existing)
```bash
streamlit run app.py
```

## Features

### Position-Specific Analysis
- **Goalkeepers**: Save percentage, goals conceded, distribution
- **Forwards**: Goals, shots, finishing, attacking metrics
- **Midfielders**: Passing, assists, ball control, creativity
- **Defenders**: Interceptions, duels, defensive actions

### Reusable Components
- Player comparison logic can be reused across positions
- Shared filtering and data processing
- Consistent UI patterns across position types

### Advanced Analytics
- Per 90 minute statistics
- Position-specific role analysis
- Scatter plot comparisons with position context
- AI-powered insights for each position

## Data Requirements

### File Naming Convention
```
Team - Player Name (Stats).csv
```

### CSV Structure for Outfield Players
Must include columns for outfield statistics as listed above, with Position column to identify player type.

### CSV Structure for Goalkeepers
Existing goalkeeper CSV structure (saves, goals conceded, etc.)

## Benefits

1. **Specialized Analysis**: Each position gets tailored analysis
2. **Code Reusability**: Shared components and logic
3. **Scalability**: Easy to add new positions or modify existing ones
4. **Consistency**: Uniform interface across all position types
5. **Flexibility**: Can analyze individual positions or all outfield players together

## Future Enhancements

1. **Sub-Position Analysis**: Left-back vs Right-back, CAM vs CDM
2. **Formation Analysis**: How players perform in different formations
3. **Cross-Position Comparisons**: Compare players across different positions
4. **Team Analysis**: Analyze entire team compositions
5. **Advanced Metrics**: xG, xA, progressive passes, etc.
