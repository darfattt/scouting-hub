#!/usr/bin/env python3
"""
Simple script to run the RAG test with proper path setup.
This script ensures the imports work correctly for the restructured project.
"""

import os
import sys

# Add the project root and src directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

def main():
    """
    Run the simple RAG test with proper imports.
    """
    print("Simple RAG Test - Goalkeeper Only")
    print("=" * 50)
    print(f"Project root: {project_root}")
    print(f"Source path: {src_path}")
    print()
    
    try:
        # Import the RAG system from new structure
        print("1. Importing RAG system...")
        from core.rag_system import GoalkeeperRAG
        print("   ✓ Import successful")
        
        # Initialize
        print("2. Initializing GoalkeeperRAG...")
        rag = GoalkeeperRAG()
        print("   ✓ Initialization successful")
        
        # Check if vector store exists in storage directory
        vector_store_path = os.path.join(project_root, "storage", "vector_store")
        if os.path.exists(vector_store_path):
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
        
        # Test data processing
        print("\n5. Testing data processing...")
        from core.data_processor import GoalkeeperDataProcessor
        
        processor = GoalkeeperDataProcessor()
        processor.load_data()
        processor.process_data()
        
        print(f"   ✓ Data processing successful: {len(processor.player_data)} players")
        
        # Test text representation
        print("6. Testing text representation...")
        if processor.player_data:
            player_name = list(processor.player_data.keys())[0]
            text_repr = processor.get_player_text_representation(player_name)
            
            if text_repr and player_name in text_repr:
                print(f"   ✓ Text representation successful for {player_name}")
            else:
                print(f"   ✗ Text representation failed for {player_name}")
                return False
        
        print("\n✓ All tests passed!")
        print("✓ Goalkeeper RAG system is ready!")
        print("\nYou can now run: streamlit run app.py")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Change to project root directory
    os.chdir(project_root)
    
    success = main()
    if not success:
        print("\nPlease check the error messages above.")
        sys.exit(1)
    else:
        print("\nRAG system test completed successfully!")
