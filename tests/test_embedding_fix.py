#!/usr/bin/env python3
"""
Test Embedding Fix
Quick test to verify the embedding model fix works.
"""

import os
import sys

def test_ollama_connection():
    """Test if we can connect to Ollama."""
    print("Testing Ollama connection...")
    
    try:
        from langchain_ollama import OllamaLLM, OllamaEmbeddings
        
        # Test reasoning model
        print("  Testing deepseek-r1:8b (reasoning model)...")
        llm = OllamaLLM(model="deepseek-r1:8b")
        response = llm.invoke("Hello, respond with just 'OK'")
        print(f"    Response: {response[:50]}...")
        print("    ✓ Reasoning model working")
        
        # Test embedding model
        print("  Testing nomic-embed-text (embedding model)...")
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        test_embedding = embeddings.embed_query("test text")
        print(f"    Embedding dimension: {len(test_embedding)}")
        print("    ✓ Embedding model working")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def test_rag_initialization():
    """Test if RAG system can be initialized."""
    print("\nTesting RAG system initialization...")
    
    try:
        from rag_system import GoalkeeperRAG
        
        print("  Initializing GoalkeeperRAG...")
        rag = GoalkeeperRAG()
        print("    ✓ RAG system initialized successfully")
        
        # Check if it has the correct models
        print(f"    Reasoning model: {rag.model_name}")
        print(f"    Embedding model: {rag.embeddings_model_name}")
        
        if rag.embeddings_model_name == "nomic-embed-text":
            print("    ✓ Using correct embedding model")
            return True
        else:
            print(f"    ✗ Wrong embedding model: {rag.embeddings_model_name}")
            return False
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def test_small_vector_store():
    """Test building a small vector store."""
    print("\nTesting small vector store creation...")
    
    try:
        from langchain_ollama import OllamaEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.schema import Document
        
        print("  Creating test documents...")
        documents = [
            Document(page_content="Test goalkeeper data", metadata={"player": "Test Player 1"}),
            Document(page_content="Another goalkeeper stats", metadata={"player": "Test Player 2"})
        ]
        
        print("  Initializing embeddings...")
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        print("  Creating vector store...")
        vector_store = FAISS.from_documents(documents, embeddings)
        print("    ✓ Vector store created successfully")
        
        # Test similarity search
        print("  Testing similarity search...")
        results = vector_store.similarity_search("goalkeeper", k=1)
        print(f"    Found {len(results)} results")
        print("    ✓ Similarity search working")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTING EMBEDDING FIX")
    print("=" * 60)
    print("This will test if the embedding model fix resolves the issue.\n")
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("RAG Initialization", test_rag_initialization),
        ("Vector Store Creation", test_small_vector_store)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
        print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe embedding fix is working correctly.")
        print("\nNext steps:")
        print("1. Run: python build_goalkeeper_rag.py")
        print("2. Run: streamlit run app.py")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPossible issues:")
        print("1. Ollama not running: ollama serve")
        print("2. Models not downloaded:")
        print("   - ollama pull deepseek-r1:8b")
        print("   - ollama pull nomic-embed-text")
        print("3. Network connectivity issues")
        
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    input("\nPress Enter to exit...")
