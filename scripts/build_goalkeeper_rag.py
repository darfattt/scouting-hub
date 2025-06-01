#!/usr/bin/env python3
"""
Build Goalkeeper RAG System
Simple script to build just the goalkeeper RAG system.
"""

import os
import sys
from datetime import datetime

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def main():
    print("=" * 60)
    print("BUILDING GOALKEEPER RAG SYSTEM")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Step 1: Import
        print("Step 1: Importing RAG system...")
        from core.rag_system import GoalkeeperRAG
        print("✓ Import successful")
        
        # Step 2: Initialize
        print("\nStep 2: Initializing GoalkeeperRAG...")
        rag = GoalkeeperRAG()
        print("✓ Initialization successful")
        
        # Step 3: Check existing vector store
        print("\nStep 3: Checking for existing vector store...")
        if os.path.exists("storage/vector_store"):
            print("✓ Found existing vector store")
            rebuild = input("Rebuild vector store? (y/N): ").lower().startswith('y')
        else:
            print("✗ No existing vector store found")
            rebuild = True
        
        # Step 4: Build vector store
        print(f"\nStep 4: {'Rebuilding' if rebuild else 'Loading'} vector store...")
        print("Note: This may take 5-15 minutes on first build...")
        
        rag.build_vector_store(force_rebuild=rebuild)
        print("✓ Vector store ready")
        
        # Step 5: Verify data
        print("\nStep 5: Verifying data...")
        player_count = len(rag.data_processor.player_data)
        print(f"✓ Loaded {player_count} goalkeepers")
        
        if player_count > 0:
            # Show sample players
            players = list(rag.data_processor.player_data.keys())[:5]
            print("\nSample players:")
            for i, player in enumerate(players, 1):
                print(f"  {i}. {player}")
            
            if len(players) < player_count:
                print(f"  ... and {player_count - len(players)} more")
        
        # Step 6: Test query
        print("\nStep 6: Testing RAG system...")
        test_query = "How many goalkeepers are in the dataset?"
        result = rag.query(test_query)
        print(f"Query: {test_query}")
        print(f"Answer: {result['answer'][:200]}...")
        print("✓ Query test successful")
        
        # Step 7: Summary
        print("\n" + "=" * 60)
        print("GOALKEEPER RAG SYSTEM BUILD COMPLETE")
        print("=" * 60)
        print(f"✓ Vector store: {'vector_store'}")
        print(f"✓ Players loaded: {player_count}")
        print(f"✓ System ready for use")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Select 'Goalkeepers' in the position dropdown")
        print("3. Use the AI Assistant or Player Comparison features")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama list")
        print("2. Check deepseek-r1:8b model: ollama pull deepseek-r1:8b")
        print("3. Verify data files in data/stats/ directory")
        print("4. Check Python environment and dependencies")
        
        import traceback
        print("\nDetailed error:")
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Goalkeeper RAG system is ready to use.")
    else:
        print("\n❌ FAILED! Please check the error messages above.")
    
    input("\nPress Enter to exit...")
