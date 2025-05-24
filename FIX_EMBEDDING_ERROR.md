# Fix for Embedding Model Error

## Problem
The error you encountered happens because `deepseek-r1:8b` is a reasoning model, not an embedding model. The RAG system needs two different types of models:

1. **Reasoning Model**: `deepseek-r1:8b` - for generating answers
2. **Embedding Model**: `nomic-embed-text` - for creating vector embeddings

## Solution Applied

I've updated the RAG system to use the correct embedding model:

### Changes Made:
- ✅ Updated `GoalkeeperRAG` to use `nomic-embed-text` for embeddings
- ✅ Updated `OutfieldRAG` to use `nomic-embed-text` for embeddings  
- ✅ Updated all position-specific RAG classes
- ✅ Created model setup script
- ✅ Updated verification scripts

## Quick Fix Steps

### Step 1: Download the Embedding Model
```bash
# Option A: Manual download
ollama pull nomic-embed-text

# Option B: Automated script
python setup_models.py
```

### Step 2: Verify Models are Available
```bash
ollama list
```

You should see both:
- `deepseek-r1:8b` (reasoning model)
- `nomic-embed-text` (embedding model)

### Step 3: Build RAG System
```bash
# Check everything is ready
python check_setup.py

# Build goalkeeper RAG
python build_goalkeeper_rag.py
```

## Model Details

### DeepSeek R1 8B
- **Purpose**: Text generation and reasoning
- **Size**: ~4.7GB
- **Used for**: Answering questions about players

### Nomic Embed Text
- **Purpose**: Text embeddings
- **Size**: ~274MB  
- **Used for**: Converting player data to vectors for similarity search

## Why This Error Occurred

The original configuration tried to use `deepseek-r1:8b` for both:
1. ❌ Text generation (✅ correct usage)
2. ❌ Text embeddings (✗ incorrect - this model doesn't support embeddings)

The fix separates these concerns:
1. ✅ `deepseek-r1:8b` for text generation
2. ✅ `nomic-embed-text` for text embeddings

## Verification

After downloading the embedding model, you can test:

```python
# Test script
from rag_system import GoalkeeperRAG

# This should now work without errors
rag = GoalkeeperRAG()
rag.build_vector_store(force_rebuild=True)
print("✅ RAG system built successfully!")
```

## Alternative Embedding Models

If `nomic-embed-text` doesn't work, you can try these alternatives:

```bash
# Option 1: All-MiniLM (smaller, faster)
ollama pull all-minilm

# Option 2: BGE Large (larger, more accurate)  
ollama pull bge-large

# Option 3: E5 Large
ollama pull e5-large
```

Then update the RAG system initialization:
```python
# In rag_system.py, change embeddings_model_name to:
embeddings_model_name: str = "all-minilm"  # or other model
```

## Complete Setup Workflow

### 1. Setup Models
```bash
python setup_models.py
```

### 2. Verify Setup
```bash
python check_setup.py
```

### 3. Build RAG Systems
```bash
# Just goalkeeper
python build_goalkeeper_rag.py

# Or all systems
python build_all_rag.py
```

### 4. Run Application
```bash
streamlit run app.py
```

## Expected Output

After the fix, you should see:
```
Building vector store from goalkeeper data...
Processing goalkeeper data...
Creating text representations for players...
Created text representations for 33 players
Converting to documents for vector store...
Creating vector store with FAISS...
This may take some time as it needs to generate embeddings for all documents...
Vector store created successfully!
Vector store built with 33 documents and saved to vector_store
✅ Goalkeeper RAG system is ready!
```

## Troubleshooting

### If nomic-embed-text fails to download:
```bash
# Try pulling with specific tag
ollama pull nomic-embed-text:latest

# Or check available versions
ollama search nomic-embed-text
```

### If embedding generation is slow:
- This is normal for the first run
- Subsequent runs will be much faster
- Consider using a smaller embedding model like `all-minilm`

### If you get memory errors:
- Close other applications
- Try processing fewer players at once
- Use a smaller embedding model

## Performance Notes

- **First build**: 5-15 minutes (generating embeddings)
- **Subsequent builds**: 1-2 minutes (loading cached embeddings)
- **Memory usage**: ~500MB-1GB during build
- **Disk space**: ~50MB per vector store

The fix ensures your RAG system will work correctly with proper model separation!
