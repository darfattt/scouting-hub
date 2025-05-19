# Goalkeeper Scouting Hub with RAG

This project is a Retrieval-Augmented Generation (RAG) system for goalkeeper scouting and analysis. It uses Ollama for local LLM inference, LangChain for the RAG pipeline, and Streamlit for the user interface.

## Features

- **AI Assistant**: Ask questions about goalkeepers and get AI-powered insights
- **Player Search**: Search and filter goalkeepers by name and team
- **Player Comparison**: Compare two goalkeepers side by side with visual charts
- **Performance Analysis**: Analyze goalkeeper performance metrics with visualizations

## Data

The system uses goalkeeper statistics data from Wyscout, stored in CSV files in the `data/stats` directory. Each file contains match-by-match statistics for a goalkeeper, including:

- Match details (opponent, competition, date)
- Minutes played
- Conceded goals
- Expected Conceded Goals (xCG)
- Shots against
- Saves
- Saves with reflexes
- Exits
- Passing statistics (long/short passes, accuracy)
- Goal kick statistics

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have Ollama installed and running locally. You can download it from [https://ollama.ai/](https://ollama.ai/).

3. Make sure you have the required model:

```bash
# This project uses the deepseek-r1:8b model
# If you don't have it, you can pull it with:
# ollama pull deepseek-r1:8b
```

4. Run the Streamlit app:

```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Streamlit application for the user interface
- `data_processor.py`: Module for processing goalkeeper data from CSV files
- `rag_system.py`: Implementation of the RAG system using LangChain and Ollama
- `requirements.txt`: List of required Python packages
- `data/stats/`: Directory containing goalkeeper statistics CSV files
- `vector_store/`: Directory where the FAISS vector store is saved (created on first run)

## How It Works

1. The system processes goalkeeper statistics from CSV files
2. It creates text representations of each goalkeeper's profile
3. These text representations are embedded and stored in a FAISS vector database
4. When a user asks a question, the system:
   - Retrieves the most relevant goalkeeper profiles
   - Passes these profiles as context to the LLM
   - Generates an answer based on the retrieved context

## Customization

You can customize the system by:

- Changing the Ollama model in `rag_system.py` (default is "llama3")
- Adjusting the embedding model (default is "nomic-embed-text")
- Modifying the prompt template in `rag_system.py`
- Adding more data to the `data/stats` directory

## Future Improvements

- Add more advanced statistical analysis
- Implement player recommendation based on specific criteria
- Add support for other player positions
- Integrate with live data sources
- Implement user authentication for team-specific access
