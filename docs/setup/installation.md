# Installation Guide

This guide will help you set up the Football Scouting RAG System on your local machine.

## Prerequisites

- Python 3.8 or higher
- Git
- At least 4GB of RAM
- 2GB of free disk space

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd rag_gk
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Install Ollama

1. Visit [https://ollama.ai](https://ollama.ai) and download Ollama for your operating system
2. Install Ollama following the platform-specific instructions
3. Start Ollama service
4. Pull the required model:

```bash
ollama pull deepseek-r1:8b
```

## Step 5: Prepare Data

1. Place your player statistics CSV files in the `data/stats/` directory
2. Ensure files follow the expected format (see Data Format Guide)

## Step 6: Build RAG System

```bash
python scripts/build_all_rag.py
```

This will:
- Process all player data
- Create vector embeddings
- Build search indices
- Set up the RAG system

## Step 7: Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama service is running
   - Check if the model is properly downloaded
   - Verify firewall settings

2. **Import Errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Data Processing Errors**
   - Check CSV file formats
   - Ensure data directory structure is correct
   - Verify file permissions

### Getting Help

- Check the troubleshooting guide in `docs/troubleshooting/`
- Review error logs in the terminal
- Ensure all prerequisites are met

## Next Steps

- Read the [Features Guide](../features/overview.md) to understand application capabilities
- Check the [Data Format Guide](data-format.md) for CSV file requirements
- Explore the [User Guide](../features/user-guide.md) for usage instructions
