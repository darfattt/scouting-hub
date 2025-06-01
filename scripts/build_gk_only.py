#!/usr/bin/env python3
import sys
"""
Build Goalkeeper RAG Only
Simple script to build just the goalkeeper RAG system without trying outfield systems.
"""

import os
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
    print("BUILDING GOALKEEPER RAG ONLY")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("This script builds only the goalkeeper RAG system.")
    print("It will not attempt to build outfield systems that might cause errors.")
    print()
    
    try:
        # Import and build goalkeeper RAG
        print("Step 1: Importing GoalkeeperRAG...")
        from core.rag_system import GoalkeeperRAG
        print("✓ Import successful")
        
        print("\nStep 2: Initializing GoalkeeperRAG...")
        rag = GoalkeeperRAG()
        print("✓ Initialization successful")
        
        print("\nStep 3: Building vector store...")
        print("Note: This may take 5-15 minutes on first build...")
        rag.build_vector_store(force_rebuild=False)
        print("✓ Vector store built successfully")
        
        print("\nStep 4: Verifying data...")
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
        
        print("\nStep 5: Testing query...")
        result = rag.query("How many goalkeepers are in the dataset?")
        print(f"Query: How many goalkeepers are in the dataset?")
        print(f"Answer: {result['answer'][:200]}...")
        print("✓ Query test successful")
        
        # Check vector store file
        print("\nStep 6: Checking vector store file...")
        if os.path.exists("storage/vector_store"):
            print("✓ Vector store file exists: vector_store/")
        else:
            print("✗ Vector store file not found")
        
        print("\n" + "=" * 60)
        print("GOALKEEPER RAG BUILD COMPLETE")
        print("=" * 60)
        print(f"✓ Players loaded: {player_count}")
        print(f"✓ Vector store: vector_store/")
        print(f"✓ System ready for use")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n🎉 SUCCESS! Goalkeeper RAG system is ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Select 'Goalkeepers' in the position dropdown")
        print("3. Use AI Assistant, Player Search, or Player Comparison")
        
        print("\n📝 Note about other positions:")
        print("- Other position types will show 'No data available'")
        print("- This is normal since you only have goalkeeper data")
        print("- Add outfield player CSV files to enable those features")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Check models are available:")
        print("   - ollama pull deepseek-r1:8b")
        print("   - ollama pull nomic-embed-text")
        print("3. Verify data files in data/stats/ directory")
        print("4. Check Python environment and dependencies")
        
        import traceback
        print("\nDetailed error:")
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Build failed. Please check the error messages above.")
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
