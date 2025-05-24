#!/usr/bin/env python3
"""
Simple RAG test - just build goalkeeper RAG system.
"""

import os
import sys

def main():
    print("Simple RAG Test - Goalkeeper Only")
    print("=" * 50)
    
    try:
        # Import the RAG system
        print("1. Importing RAG system...")
        from rag_system import GoalkeeperRAG
        print("   ✓ Import successful")
        
        # Initialize
        print("2. Initializing GoalkeeperRAG...")
        rag = GoalkeeperRAG()
        print("   ✓ Initialization successful")
        
        # Check if vector store exists
        if os.path.exists("vector_store"):
            print("3. Vector store already exists, loading...")
            rag.build_vector_store(force_rebuild=False)
        else:
            print("3. Building new vector store...")
            rag.build_vector_store(force_rebuild=True)
        
        print("   ✓ Vector store ready")
        
        # Check data
        player_count = len(rag.data_processor.player_data)
        print(f"4. Players loaded: {player_count}")
        
        if player_count > 0:
            # List some players
            players = list(rag.data_processor.player_data.keys())[:5]
            print("   Sample players:")
            for player in players:
                print(f"     - {player}")
        
        print("\n✓ Goalkeeper RAG system is ready!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nYou can now run: streamlit run app.py")
    else:
        print("\nPlease check the error messages above.")
