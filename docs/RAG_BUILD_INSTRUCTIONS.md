# RAG System Build Instructions

## Overview
This guide will help you build and generate the RAG (Retrieval-Augmented Generation) systems for your football scouting hub.

## Prerequisites

### 1. Ensure Ollama is Running
Make sure Ollama is installed and running with the required models:

```bash
# Check if Ollama is running
ollama list

# Pull required models (if not available)
ollama pull phi3:mini           # Main reasoning model (~2.3GB)
ollama pull nomic-embed-text    # Embedding model (~274MB)
```

**Or use the automated setup script:**
```bash
python setup_models.py
```

### 2. Verify Python Environment
Make sure you're in the correct directory and virtual environment:

```bash
# Navigate to your project directory
cd "E:\darfat\persib\scouting hub\workspace\rag_gk"

# Activate virtual environment (if using one)
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Verify required packages
pip list | findstr "streamlit pandas faiss langchain"
```

## Step-by-Step RAG Building

### Step 1: Test Basic Imports
First, test if all imports work correctly:

```python
# Run this in Python console or create test_imports.py
python -c "
from rag_system import GoalkeeperRAG
from data_processor import GoalkeeperDataProcessor
print('✓ All imports successful')
"
```

### Step 2: Build Goalkeeper RAG (Primary)
Start with the goalkeeper RAG system since you have goalkeeper data:

```python
# Create and run build_gk_rag.py
python -c "
from rag_system import GoalkeeperRAG
print('Building Goalkeeper RAG...')
rag = GoalkeeperRAG()
rag.build_vector_store(force_rebuild=True)
print('✓ Goalkeeper RAG built successfully')
"
```

### Step 3: Test Goalkeeper RAG
Test the goalkeeper RAG system:

```python
# Create and run test_gk_rag.py
python -c "
from rag_system import GoalkeeperRAG
rag = GoalkeeperRAG()
rag.build_vector_store()
result = rag.query('How many goalkeepers are in the dataset?')
print('Query result:', result['answer'])
print('✓ Goalkeeper RAG test successful')
"
```

### Step 4: Build Outfield RAG (If Data Available)
If you have outfield player data:

```python
# Create and run build_outfield_rag.py
python -c "
from rag_system import OutfieldRAG, ForwardRAG, MidfielderRAG, DefenderRAG
print('Building Outfield RAG systems...')

# Build general outfield RAG
outfield_rag = OutfieldRAG()
outfield_rag.build_vector_store(force_rebuild=True)
print('✓ Outfield RAG built')

# Build position-specific RAGs
forward_rag = ForwardRAG()
forward_rag.build_vector_store(force_rebuild=True)
print('✓ Forward RAG built')

midfielder_rag = MidfielderRAG()
midfielder_rag.build_vector_store(force_rebuild=True)
print('✓ Midfielder RAG built')

defender_rag = DefenderRAG()
defender_rag.build_vector_store(force_rebuild=True)
print('✓ Defender RAG built')

print('All RAG systems built successfully!')
"
```

## Alternative: Manual Script Execution

### Option 1: Create Individual Build Scripts

**build_goalkeeper_rag.py:**
```python
#!/usr/bin/env python3
from rag_system import GoalkeeperRAG
import os

def main():
    print("Building Goalkeeper RAG System...")

    # Initialize
    rag = GoalkeeperRAG()

    # Build vector store
    rag.build_vector_store(force_rebuild=True)

    # Verify
    player_count = len(rag.data_processor.player_data)
    print(f"✓ Built RAG for {player_count} goalkeepers")

    # Test query
    result = rag.query("List the goalkeepers in the dataset")
    print("✓ RAG system working correctly")

    print("Goalkeeper RAG system ready!")

if __name__ == "__main__":
    main()
```

**build_outfield_rag.py:**
```python
#!/usr/bin/env python3
from rag_system import OutfieldRAG, ForwardRAG, MidfielderRAG, DefenderRAG

def main():
    print("Building Outfield RAG Systems...")

    systems = [
        ("Outfield", OutfieldRAG),
        ("Forward", ForwardRAG),
        ("Midfielder", MidfielderRAG),
        ("Defender", DefenderRAG)
    ]

    for name, rag_class in systems:
        try:
            print(f"Building {name} RAG...")
            rag = rag_class()
            rag.build_vector_store(force_rebuild=True)
            player_count = len(rag.data_processor.player_data)
            print(f"✓ {name} RAG built for {player_count} players")
        except Exception as e:
            print(f"✗ {name} RAG failed: {e}")

    print("Outfield RAG systems ready!")

if __name__ == "__main__":
    main()
```

### Option 2: Run the Original Script
Try running the original rag_system.py:

```bash
python rag_system.py
```

**Note:** This may take 5-15 minutes on first run as it generates embeddings.

## Expected Output

### Successful Build Output:
```
Testing GoalkeeperRAG...
Building vector store from goalkeeper data...
Processing goalkeeper data...
Creating text representations for players...
Created text representations for 33 players
Converting to documents for vector store...
Creating vector store with FAISS...
This may take some time as it needs to generate embeddings for all documents...
Vector store created successfully!
Vector store built with 33 documents and saved to vector_store
GK Answer: [AI response about goalkeepers]

Testing ForwardRAG...
Building vector store from outfield player data (Forward)...
Processing outfield player data...
Creating text representations for players...
Created text representations for X players
...
```

### Generated Files:
After successful build, you should see these directories:
```
├── vector_store/           # Goalkeeper embeddings
├── vector_store_outfield/  # All outfield players
├── vector_store_forwards/  # Forward players only
├── vector_store_midfielders/ # Midfielder players only
└── vector_store_defenders/ # Defender players only
```

## Troubleshooting

### Common Issues:

**1. Ollama Connection Error:**
```
Error: Could not connect to Ollama
Solution: Ensure Ollama is running and deepseek-r1:8b model is available
```

**2. No Data Found:**
```
Error: No player data found
Solution: Check that CSV files are in data/stats/ directory
```

**3. Memory Issues:**
```
Error: Out of memory during embedding generation
Solution: Process fewer players at once or increase system memory
```

**4. Import Errors:**
```
Error: ModuleNotFoundError
Solution: Install missing packages with pip install
```

### Performance Tips:

1. **First Run**: Takes 5-15 minutes to generate embeddings
2. **Subsequent Runs**: Much faster as embeddings are cached
3. **Memory Usage**: Each RAG system uses ~100-500MB RAM
4. **Disk Space**: Vector stores require ~10-50MB each

## Verification

### Test the Built RAG Systems:
```python
# Test all systems
from rag_system import GoalkeeperRAG, ForwardRAG, MidfielderRAG, DefenderRAG

# Test goalkeeper
gk_rag = GoalkeeperRAG()
gk_result = gk_rag.query("Who is the best goalkeeper?")
print("GK Test:", gk_result['answer'][:100])

# Test forward (if data available)
fw_rag = ForwardRAG()
fw_result = fw_rag.query("Who scores the most goals?")
print("Forward Test:", fw_result['answer'][:100])
```

### Run the App:
```bash
streamlit run app.py
```

The app should now work with all position types available in the sidebar dropdown.

## Next Steps

1. **Build RAG Systems**: Follow the steps above
2. **Test Each System**: Verify they work correctly
3. **Run the App**: Use `streamlit run app.py`
4. **Add More Data**: Add outfield player CSV files as needed
5. **Customize**: Modify role weights and analysis as desired

## Support

If you encounter issues:
1. Check Ollama is running
2. Verify data files are present
3. Ensure all dependencies are installed
4. Check Python environment is correct
5. Review error messages for specific issues
